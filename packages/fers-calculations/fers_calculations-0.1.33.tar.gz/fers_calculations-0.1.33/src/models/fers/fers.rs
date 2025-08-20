
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use std::collections::{BTreeMap, HashMap};
use nalgebra::{DMatrix};
use std::collections::HashSet;
use crate::functions::results::{ compute_member_results_from_displacement, extract_displacements};
// use csv::Writer;
// use std::error::Error;
use crate::models::members::{material::Material, section::Section, memberhinge::MemberHinge, shapepath::ShapePath};
use crate::models::members::memberset::MemberSet;
use crate::models::loads::loadcase::LoadCase;
use crate::models::loads::loadcombination::LoadCombination;
use crate::models::imperfections::imperfectioncase::ImperfectionCase;
use crate::models::results::resultbundle::ResultsBundle;
use crate::models::results::results::{ResultType, Results};
use crate::models::results::resultssummary::ResultsSummary;
use crate::models::settings::settings::Settings;
use crate::models::supports::nodalsupport::NodalSupport;

use crate::functions::load_assembler::{assemble_nodal_loads, assemble_nodal_moments, assemble_distributed_loads};
use crate::functions::reactions::extract_reaction_nodes;


#[derive(Serialize, Deserialize, ToSchema, Debug)]
pub struct FERS {
    pub member_sets: Vec<MemberSet>,
    pub load_cases: Vec<LoadCase>,
    pub load_combinations: Vec<LoadCombination>,
    pub imperfection_cases: Vec<ImperfectionCase>,
    pub settings: Settings, 
    pub results: Option<ResultsBundle>,  
    pub memberhinges: Option<Vec<MemberHinge>>,
    pub materials: Vec<Material>,
    pub sections: Vec<Section>,
    pub nodal_supports: Vec<NodalSupport>, 
    pub shape_paths: Option<Vec<ShapePath>>,
}

impl FERS {
    // Function to build lookup maps from Vec<Material>, Vec<Section>, and Vec<MemberHinge>
    pub fn build_lookup_maps(
        &self
    ) -> (
        HashMap<u32, &Material>,
        HashMap<u32, &Section>,
        HashMap<u32, &MemberHinge>,
        HashMap<u32, &NodalSupport>
    ) {
        let material_map: HashMap<u32, &Material> = self.materials.iter().map(|m| (m.id, m)).collect();
        let section_map: HashMap<u32, &Section> = self.sections.iter().map(|s| (s.id, s)).collect();
        let memberhinge_map: HashMap<u32, &MemberHinge> = self.memberhinges.iter().flatten().map(|mh| (mh.id, mh)).collect();
        let support_map: HashMap<u32, &NodalSupport> = self.nodal_supports.iter().map(|s| (s.id, s)).collect();
        
        (material_map, section_map, memberhinge_map, support_map)
    }

    pub fn get_member_count(&self) -> usize {
        self.member_sets
            .iter()
            .map(|ms| ms.members.len())
            .sum()
    }

    pub fn assemble_global_stiffness_matrix(&self) -> Result<DMatrix<f64>, String> {
        self.validate_node_ids()?;
        let (material_map, section_map, _memberhinge_map, _support_map) = self.build_lookup_maps();
        let num_dofs: usize = self.member_sets.iter()
            .flat_map(|ms| ms.members.iter())
            .flat_map(|m| vec![m.start_node.id, m.end_node.id])
            .max()
            .unwrap_or(0) as usize * 6; // 6 DOFs per node in 3D
        let mut k_global = DMatrix::<f64>::zeros(num_dofs, num_dofs);

        for member_set in &self.member_sets {
            for member in &member_set.members {
                if let Some(k_local) = member.calculate_stiffness_matrix_3d(&material_map, &section_map) {
                    let t_matrix = member.calculate_transformation_matrix_3d();
                    let k_global_transformed = t_matrix.transpose() * k_local * t_matrix;

                    let si = (member.start_node.id as usize - 1) * 6;
                    let ei = (member.end_node.id   as usize - 1) * 6;
                    for i in 0..6 {
                        for j in 0..6 {
                            k_global[(si + i, si + j)] += k_global_transformed[(i,     j    )];
                            k_global[(si + i, ei + j)] += k_global_transformed[(i,     j + 6)];
                            k_global[(ei + i, si + j)] += k_global_transformed[(i + 6, j    )];
                            k_global[(ei + i, ei + j)] += k_global_transformed[(i + 6, j + 6)];
                        }
                    }
                }
            }
        }

        Ok(k_global)
    }


    pub fn assemble_geometric_stiffness_matrix(
        &self,
        displacement: &DMatrix<f64>,
    ) -> Result<DMatrix<f64>, String> {
        let (material_map, section_map, _hinge_map, _support_map) = self.build_lookup_maps();
        let n = self.compute_num_dofs();
        let mut k_geo = DMatrix::<f64>::zeros(n, n);

        for ms in &self.member_sets {
            for member in &ms.members {
                // 1) axial force in member from current u
                let n_axial = member.calculate_axial_force_3d(
                    displacement, &material_map, &section_map
                );
                // 2) local geometric stiffness
                let k_g_local = member.calculate_geometric_stiffness_matrix_3d(n_axial);
                // 3) transform to global
                let t = member.calculate_transformation_matrix_3d();
                let k_g_global = t.transpose() * k_g_local * t;
                // 4) scatter into k_geo
                let i0 = (member.start_node.id as usize - 1) * 6;
                let j0 = (member.end_node.id   as usize - 1) * 6;
                for i in 0..6 {
                    for j in 0..6 {
                        k_geo[(i0 + i, i0 + j)] += k_g_global[(i,     j    )];
                        k_geo[(i0 + i, j0 + j)] += k_g_global[(i,     j + 6)];
                        k_geo[(j0 + i, i0 + j)] += k_g_global[(i + 6, j    )];
                        k_geo[(j0 + i, j0 + j)] += k_g_global[(i + 6, j + 6)];
                    }
                }
            }
        }

        Ok(k_geo)
    }

    pub fn validate_node_ids(&self) -> Result<(), String> {
        // Collect all node IDs in a HashSet for quick lookup
        let mut node_ids: HashSet<u32> = HashSet::new();

        // Populate node IDs from all members
        for member_set in &self.member_sets {
            for member in &member_set.members {
                node_ids.insert(member.start_node.id);
                node_ids.insert(member.end_node.id);
            }
        }

        // Ensure IDs start at 1 and are consecutive
        let max_id = *node_ids.iter().max().unwrap_or(&0);
        for id in 1..=max_id {
            if !node_ids.contains(&id) {
                return Err(format!("Node ID {} is missing. Node IDs must be consecutive starting from 1.", id));
            }
        }

        Ok(())
    }

    fn compute_num_dofs(&self) -> usize {
        let max_node = self.member_sets.iter()
            .flat_map(|ms| ms.members.iter())
            .flat_map(|m| vec![m.start_node.id, m.end_node.id])
            .max()
            .unwrap_or(0) as usize;
        max_node * 6
    }

   pub fn assemble_load_vector_for_combination(
        &self,
        combination_id: u32,
    ) -> Result<DMatrix<f64>, String> {
        let num_dofs = self.compute_num_dofs();
        let mut f_comb = DMatrix::<f64>::zeros(num_dofs, 1);

        // Find the combination by its load_combination_id field
        let combo = self
            .load_combinations
            .iter()
            .find(|lc| lc.load_combination_id == combination_id)
            .ok_or_else(|| format!("LoadCombination {} not found.", combination_id))?;

        // Now iterate the HashMap<u32, f64>
        for (&case_id, &factor) in &combo.load_cases_factors {
            let f_case = self.assemble_load_vector_for_case(case_id);
            f_comb += f_case * factor;
        }

        Ok(f_comb)
    }


    pub fn apply_boundary_conditions(&self, k_global: &mut DMatrix<f64>) {
        // Build the support mapping from support id to &NodalSupport.
        // This maps the nodal support definitions provided in FERS.
        let support_map: HashMap<u32, &NodalSupport> = self
            .nodal_supports
            .iter()
            .map(|support| (support.id, support))
            .collect();

        // Create a set to keep track of node IDs that have already had their boundary conditions applied.
        let mut applied_nodes: HashSet<u32> = HashSet::new();

        // Loop over each memberset and each member within
        for member_set in &self.member_sets {
            for member in &member_set.members {
                // Process both the start and end nodes of the member.
                for node in [&member.start_node, &member.end_node] {
                    // Check if we've already applied the BC for this node.
                    if applied_nodes.contains(&node.id) {
                        continue;
                    }

                    // Only apply a BC if the node has a nodal support assigned.
                    if let Some(support_id) = node.nodal_support {
                        // Attempt to retrieve the corresponding nodal support from the support_map.
                        if let Some(support) = support_map.get(&support_id) {
                            self.constrain_dof(k_global, node.id, support);
                            applied_nodes.insert(node.id);
                        }
                    }
                }
            }
        }
    }


    // Helper function to apply constraints based on support
    fn constrain_dof(&self, k_global: &mut DMatrix<f64>, node_id: u32, support: &NodalSupport) {
        let dof_start = (node_id as usize - 1) * 6;

        // Constrain translational DOFs based on displacement conditions
        for (axis, condition) in &support.displacement_conditions {
            let dof = match axis.as_str() {
                "X" => 0,  // X translation
                "Y" => 1,  // Y translation
                "Z" => 2,  // Z translation
                _ => continue,
            };
            match condition.as_str() {
                "Fixed" => self.constrain_single_dof(k_global, dof_start + dof),
                "Free"  => {
                    // DOF is free, so do nothing
                },
                // Optionally handle other conditions (e.g., "Pinned") here
                _ => continue,
            }
        }

        // Constrain rotational DOFs based on rotation conditions
        for (axis, condition) in &support.rotation_conditions {
            let dof = match axis.as_str() {
                "X" => 3,  // X rotation
                "Y" => 4,  // Y rotation
                "Z" => 5,  // Z rotation
                _ => continue,
            };
            match condition.as_str() {
                "Fixed" => self.constrain_single_dof(k_global, dof_start + dof),
                "Free"  => {
                    // Rotation is free, so leave it unmodified.
                },
                _ => continue,
            }
        }
    }

    // Helper function to apply constraints to a single DOF by modifying k_global
    fn constrain_single_dof(&self, k_global: &mut DMatrix<f64>, dof_index: usize) {
        // Zero out the row and column for this constrained DOF
        for j in 0..k_global.ncols() {
            k_global[(dof_index, j)] = 0.0;
        }
        for i in 0..k_global.nrows() {
            k_global[(i, dof_index)] = 0.0;
        }
        k_global[(dof_index, dof_index)] = 1e20;  // Large value to simulate constraint
    }

    pub fn assemble_load_vector_for_case(&self, load_case_id: u32) -> DMatrix<f64> {
        let num_dofs = self.member_sets.iter()
            .flat_map(|ms| ms.members.iter())
            .flat_map(|m| vec![m.start_node.id, m.end_node.id])
            .max()
            .unwrap_or(0) as usize * 6;
        let mut f = DMatrix::<f64>::zeros(num_dofs, 1);
    
        if let Some(load_case) = self.load_cases.iter().find(|lc| lc.id == load_case_id) {
            assemble_nodal_loads(load_case, &mut f);
            assemble_nodal_moments(load_case, &mut f);
            assemble_distributed_loads(load_case, &self.member_sets, &mut f, load_case_id);
        }
        f
    }

    pub fn solve_for_load_case(&mut self, load_case_id: u32) -> Result<Results, String> {
        // a) validate & build stiffness
        self.validate_node_ids()?;
        let original_k = self.assemble_global_stiffness_matrix()?;
        let mut k_global = original_k.clone();

        // b) apply supports
        self.apply_boundary_conditions(&mut k_global);

        // c) build load vector
        let f = self.assemble_load_vector_for_case(load_case_id);

        // d) solve K u = f
        let u = k_global.clone()
            .lu()
            .solve(&f)
            .ok_or_else(|| String::from("Global stiffness matrix is singular or near-singular"))?;

        // e) reaction = K₀·u – f
        let reaction = &original_k * &u - &f;

        let load_case = self
            .load_cases
            .iter()
            .find(|lc| lc.id == load_case_id)
            .ok_or_else(|| format!("LoadCase {} not found.", load_case_id))?;
        let name: String = load_case.name.clone();

        // f) build & store results with the real name
        let results = self.build_and_store_results(
            name,
            ResultType::Loadcase(load_case_id),
            &u,
            &reaction,
        )?;
        Ok(results.clone())
    }

    pub fn solve_for_load_case_second_order(
        &mut self,
        load_case_id: u32,
        max_iterations: usize,
        tolerance: f64,
    ) -> Result<Results, String> {
        self.validate_node_ids()?;
        // assemble linear stiffness & load
        let k_linear = self.assemble_global_stiffness_matrix()?;
        let f = self.assemble_load_vector_for_case(load_case_id);

        let load_case = self
            .load_cases
            .iter()
            .find(|lc| lc.id == load_case_id)
            .ok_or_else(|| format!("LoadCase {} not found.", load_case_id))?;
        let name: String = load_case.name.clone();

        // initial guess
        let mut u = DMatrix::<f64>::zeros(k_linear.nrows(), 1);
        for iter in 0..max_iterations {
            let k_geo = self.assemble_geometric_stiffness_matrix(&u)?;
            let mut k_tangent = &k_linear + &k_geo;
            self.apply_boundary_conditions(&mut k_tangent);

            let r = &k_linear * &u + &k_geo * &u - &f;
            let delta_u = k_tangent
                .clone()
                .lu()
                .solve(&(-&r))
                .ok_or_else(|| "Tangent stiffness singular.".to_string())?;

            u += &delta_u;
            if delta_u.norm() < tolerance {
                break;
            }
            if iter + 1 == max_iterations {
                return Err(format!(
                    "Newton–Raphson failed to converge in {} iterations",
                    max_iterations
                ));
            }
        }

        let reaction = &k_linear * &u - &f;
        // g) build & store results with the real name
        let results = self.build_and_store_results(
            name,
            ResultType::Loadcase(load_case_id),
            &u,
            &reaction,
        )?;
        Ok(results.clone())
    }

    pub fn solve_for_load_combination(
        &mut self,
        combination_id: u32,
    ) -> Result<Results, String> {
        self.validate_node_ids()?;
        let original_k = self.assemble_global_stiffness_matrix()?;
        let mut k_global = original_k.clone();

        self.apply_boundary_conditions(&mut k_global);
        let f_comb = self.assemble_load_vector_for_combination(combination_id)?;

        let u = k_global
            .clone()
            .lu()
            .solve(&f_comb)
            .ok_or_else(|| "Global stiffness matrix singular or near‐singular.".to_string())?;

        let reaction = &original_k * &u - &f_comb;

        // ** lookup the LoadCombination and pull its real name **
        let combo = self
            .load_combinations
            .iter()
            .find(|lc| lc.load_combination_id == combination_id)
            .ok_or_else(|| format!("LoadCombination {} not found.", combination_id))?;
        let name = combo.name.clone();

        // build & store results with the real name
        let results = self.build_and_store_results(
            name,
            ResultType::Loadcombination(combination_id),
            &u,
            &reaction,
        )?;
        Ok(results.clone())
    }

    pub fn solve_for_load_combination_second_order(
            &mut self,
            combination_id: u32,
            max_iterations: usize,
            tolerance: f64,
        ) -> Result<Results, String> {
            // 1) Validate & build linear stiffness and combined load
            self.validate_node_ids()?;
            let k_linear = self.assemble_global_stiffness_matrix()?;
            let f_comb = self.assemble_load_vector_for_combination(combination_id)?;

            // 2) Initialize displacement vector
            let mut u = DMatrix::<f64>::zeros(k_linear.nrows(), 1);

            // 3) Newton–Raphson loop
            for iter in 0..max_iterations {
                // a) geometric stiffness at current u
                let k_geo = self.assemble_geometric_stiffness_matrix(&u)?;
                // b) form tangent stiffness = K_L + K_G
                let mut k_tangent = &k_linear + &k_geo;
                self.apply_boundary_conditions(&mut k_tangent);

                // c) residual R = (K_L + K_G)·u – F
                let r = &k_linear * &u + &k_geo * &u - &f_comb;

                // d) solve for Δu:  K_tangent · Δu = –R
                let delta_u = k_tangent
                    .clone()
                    .lu()
                    .solve(&(-&r))
                    .ok_or_else(|| "Tangent stiffness singular.".to_string())?;

                // e) update
                u += &delta_u;

                // f) check convergence
                if delta_u.norm() < tolerance {
                    break;
                }
                if iter + 1 == max_iterations {
                    return Err(format!(
                        "Newton–Raphson did not converge in {} iterations.",
                        max_iterations
                    ));
                }
            }

            // 4) Compute reactions
            let reaction = &k_linear * &u - &f_comb;

            // 5) Lookup combo for its name
            let combo = self
                .load_combinations
                .iter()
                .find(|lc| lc.load_combination_id == combination_id)
                .ok_or_else(|| format!("LoadCombination {} not found.", combination_id))?;

            // 6) Build and store Results
            let results = self.build_and_store_results(
                combo.name.clone(),
                ResultType::Loadcombination(combination_id),
                &u,
                &reaction,
            )?;
            Ok(results.clone())
        }



    pub fn build_and_store_results(
        &mut self,
        name: String,
        result_type: ResultType,
        displacement_vector: &DMatrix<f64>,
        global_reaction_vector: &DMatrix<f64>,
    ) -> Result<&Results, String> {
        // Build the three main maps
        let member_results = compute_member_results_from_displacement(self, displacement_vector);
        let displacement_nodes = extract_displacements(self, displacement_vector);
        let reaction_nodes = extract_reaction_nodes(self, global_reaction_vector);

        // Summaries
        let total_members: usize = self.member_sets.iter().map(|set| set.members.len()).sum();
        let total_supports: usize = self.nodal_supports.len();

        let results = Results {
            name: name.clone(),
            result_type: result_type.clone(),
            displacement_nodes,
            reaction_nodes,
            member_results,
            summary: ResultsSummary {
                total_displacements: total_members,      
                total_reaction_forces: total_supports,
                total_member_forces: total_members,
            },
            unity_checks: None,
        };

        // Insert into bundle
        let bundle = self.results.get_or_insert_with(|| ResultsBundle {
            loadcases: BTreeMap::new(),
            loadcombinations: BTreeMap::new(),
            unity_checks_overview: None,
        });

        match result_type {
            ResultType::Loadcase(_) => {
                if bundle.loadcases.insert(name.clone(), results).is_some() {
                    return Err(format!("Duplicate load case name `{}`", name));
                }
                Ok(bundle.loadcases.get(&name).unwrap())
            }
            ResultType::Loadcombination(_) => {
                if bundle.loadcombinations.insert(name.clone(), results).is_some() {
                    return Err(format!("Duplicate load combination name `{}`", name));
                }
                Ok(bundle.loadcombinations.get(&name).unwrap())
            }
        }
    }

    pub fn save_results_to_json(fers_data: &FERS, file_path: &str) -> Result<(), std::io::Error> {
        let json = serde_json::to_string_pretty(fers_data)?; 
        std::fs::write(file_path, json) 
    }
}