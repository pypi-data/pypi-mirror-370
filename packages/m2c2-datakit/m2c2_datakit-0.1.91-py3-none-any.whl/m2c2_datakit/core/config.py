import os
import re
from typing import List
from pydantic import BaseModel, Field
from importlib.metadata import version
from pathlib import Path



class Settings(BaseModel):
    PACKAGE_VERSION: str = Field(default_factory=lambda: version("m2c2-datakit"))

    # ABSTRACT ALL IDS BY PROVIDER
    DEDUP_IDS_METRICWIRE: List[str] = [
        "userId",
        "submissionSessionId",
        "activityId",
    ]
    DEDUP_IDS_UAS: List[str] = [
        "userId",
        "submissionSessionId",
        "activityId",
    ]
    
    DEDUP_IDS_MONGODB: List[str] = []
    DEDUP_IDS_QUALTRICS: List[str] = ["index", "ResponseId", 'M2C2_ASSESSMENT_ORDER', 'M2C2_AUTO_ADVANCE', 'M2C2_LANGUAGE']
    
    # def unnest_trial_level_data(df: pd.DataFrame, drop_duplicates=True, column_order: List[str] = None) -> pd.DataFrame:
#     column_order = column_order or ["participant_id", "session_id", "group", "wave", "activity_id", "study_id", "document_uuid"]
#     trial_df = trial_df.drop_duplicates(subset=["activity_uuid", "session_uuid", "trial_begin_iso8601_timestamp"])

    STANDARD_GROUPING_FOR_AGGREGATION: List[str] = [
        "study_uid",
        "user_uid",
        "uuid",
        "activity_name",
    ]
    STANDARD_GROUPING_FOR_AGGREGATION_QUALTRICS: List[str] = ['ResponseId']
    
    STANDARD_GROUPING_FOR_AGGREGATION_METRICWIRE: List[str] = [
        "userId",
        "submissionSessionId",
        "activityId",
    ]
    STANDARD_GROUPING_FOR_AGGREGATION_UAS: List[str] = [
        "userId",
        "submissionSessionId",
        "activityId",
    ]
    
    @property
    def QUALTRICS_TRIAL_DATA_REGEX(self):
        return re.compile(r"(M2C2_ASSESSMENT_\d+)_TRIAL_DATA_(\d+)")
    
    @property
    def DEFAULT_FUNC_MAP_SCORING(self):
        from .map import DEFAULT_FUNC_MAP_SCORING
        return DEFAULT_FUNC_MAP_SCORING
    
    # DEFAULTS FOR UI
    DEFAULT_PLOT_COLOR: str = "steelblue"
    DEFAULT_PLOT_DPI: int = 150


settings = Settings()

# === Environment Safeguards ===
os.environ["LOGFIRE_DISABLE_CLOUD"] = "1"
os.environ["LOGFIRE_IGNORE_NO_CONFIG"] = "1"

# === Local JSONL Logging Setup ===
LOG_DIR = Path.cwd() / "logs"
LOG_FILE = LOG_DIR / "events.jsonl"
LOG_DIR.mkdir(exist_ok=True)