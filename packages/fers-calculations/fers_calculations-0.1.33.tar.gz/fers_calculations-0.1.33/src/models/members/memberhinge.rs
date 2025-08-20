use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct MemberHinge {
    pub id: u32,
    pub hinge_type: String,
    pub translational_release_vx: Option<f64>,
    pub translational_release_vy: Option<f64>,
    pub translational_release_vz: Option<f64>,
    pub rotational_release_mx: Option<f64>,
    pub rotational_release_my: Option<f64>,
    pub rotational_release_mz: Option<f64>,
    pub max_tension_vx: Option<f64>,
    pub max_tension_vy: Option<f64>,
    pub max_tension_vz: Option<f64>,
    pub max_moment_mx: Option<f64>,
    pub max_moment_my: Option<f64>,
    pub max_moment_mz: Option<f64>,
}
