use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub enum SupportConditionType {
    Fixed,
    Free,
    Spring,
    PositiveOnly,
    NegativeOnly,
}

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct SupportCondition {
    pub condition: Option<SupportConditionType>,
    pub stiffness: Option<f64>,
}
