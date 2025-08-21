use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use std::collections::BTreeMap;




#[derive(Serialize, Deserialize, ToSchema, Clone, Debug)]
pub struct NodalSupport {
    pub id: u32,
    pub classification: Option<String>,
    pub displacement_conditions: BTreeMap<String, String>,
    pub rotation_conditions: BTreeMap<String, String>,
}
