use std::collections::{BTreeMap, HashSet};
use nalgebra::{DMatrix, DVector};
use crate::models::fers::fers::FERS;
use crate::models::results::displacement::NodeDisplacement;
use crate::models::results::forces::{ComponentForces, NodeForces};
use crate::models::results::memberresult::MemberResult; 

pub fn compute_component_extrema(start_forces: &NodeForces, end_forces: &NodeForces) -> (ComponentForces, ComponentForces) {
    let maximums = ComponentForces {
        fx: start_forces.fx.max(end_forces.fx),
        fy: start_forces.fy.max(end_forces.fy),
        fz: start_forces.fz.max(end_forces.fz),
        mx: start_forces.mx.max(end_forces.mx),
        my: start_forces.my.max(end_forces.my),
        mz: start_forces.mz.max(end_forces.mz),
    };
    let minimums = ComponentForces {
        fx: start_forces.fx.min(end_forces.fx),
        fy: start_forces.fy.min(end_forces.fy),
        fz: start_forces.fz.min(end_forces.fz),
        mx: start_forces.mx.min(end_forces.mx),
        my: start_forces.my.min(end_forces.my),
        mz: start_forces.mz.min(end_forces.mz),
    };
    (maximums, minimums)
}

pub fn extract_displacements(
    fers: &FERS,
    global_displacement_vector: &DMatrix<f64>,
) -> BTreeMap<u32, NodeDisplacement> {
    let mut unique_node_identifiers: HashSet<u32> = HashSet::new();

    for member_set in &fers.member_sets {
        for member in &member_set.members {
            unique_node_identifiers.insert(member.start_node.id);
            unique_node_identifiers.insert(member.end_node.id);
        }
    }

    unique_node_identifiers
        .into_iter()
        .map(|node_identifier| {
            let degree_of_freedom_start = (node_identifier as usize - 1) * 6;
            (
                node_identifier,
                NodeDisplacement {
                    dx: global_displacement_vector[(degree_of_freedom_start + 0, 0)],
                    dy: global_displacement_vector[(degree_of_freedom_start + 1, 0)],
                    dz: global_displacement_vector[(degree_of_freedom_start + 2, 0)],
                    rx: global_displacement_vector[(degree_of_freedom_start + 3, 0)],
                    ry: global_displacement_vector[(degree_of_freedom_start + 4, 0)],
                    rz: global_displacement_vector[(degree_of_freedom_start + 5, 0)],
                },
            )
        })
        .collect()
}

pub fn compute_member_results_from_displacement(
    fers: &FERS,
    global_displacement_vector: &DMatrix<f64>,
) -> BTreeMap<u32, MemberResult> {
    let (material_map, section_map, _hinge_map, _support_map) = fers.build_lookup_maps();
    let mut results_by_member_identifier: BTreeMap<u32, MemberResult> = BTreeMap::new();

    for member_set in &fers.member_sets {
        for member in &member_set.members {
            let start_node_dof_index = (member.start_node.id as usize - 1) * 6;
            let end_node_dof_index = (member.end_node.id as usize - 1) * 6;

            let mut member_displacement_vector = DVector::<f64>::zeros(12);
            for degree_of_freedom_offset in 0..6 {
                member_displacement_vector[degree_of_freedom_offset] =
                    global_displacement_vector[(start_node_dof_index + degree_of_freedom_offset, 0)];
                member_displacement_vector[degree_of_freedom_offset + 6] =
                    global_displacement_vector[(end_node_dof_index + degree_of_freedom_offset, 0)];
            }

            let local_stiffness_matrix = member
                .calculate_stiffness_matrix_3d(&material_map, &section_map)
                .expect("Failed to compute local stiffness matrix");
            let transformation_matrix = member.calculate_transformation_matrix_3d();

            let local_displacement_vector = &transformation_matrix * &member_displacement_vector;
            let local_force_vector = &local_stiffness_matrix * &local_displacement_vector;
            let global_force_vector = transformation_matrix.transpose() * local_force_vector;

            let start_node_forces = NodeForces {
                fx: global_force_vector[0],
                fy: global_force_vector[1],
                fz: global_force_vector[2],
                mx: global_force_vector[3],
                my: global_force_vector[4],
                mz: global_force_vector[5],
            };
            let end_node_forces = NodeForces {
                fx: global_force_vector[6],
                fy: global_force_vector[7],
                fz: global_force_vector[8],
                mx: global_force_vector[9],
                my: global_force_vector[10],
                mz: global_force_vector[11],
            };

            let (maximums, minimums) =
                compute_component_extrema(&start_node_forces, &end_node_forces);

            results_by_member_identifier.insert(
                member.id,
                MemberResult {
                    start_node_forces,
                    end_node_forces,
                    maximums,
                    minimums,
                },
            );
        }
    }

    results_by_member_identifier
}

