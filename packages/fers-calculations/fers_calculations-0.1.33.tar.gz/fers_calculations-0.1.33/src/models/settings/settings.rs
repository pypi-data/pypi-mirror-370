use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use crate::models::settings::generalinfo::GeneralInfo;
use crate::models::settings::analysissettings::AnalysisOption;

#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct Settings {
    pub id: u32,
    pub analysis_option: AnalysisOption,
    pub general_info: GeneralInfo,
}
