import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class ActivityRecord:
    activity_id: str
    created_on: str
    plan_id: str
    source_path: str
    surrogate_key: str
    user_id: str
    workout_id: str
    created_at: Optional[str] = None
    current_est5k_time_in_secs: Optional[int] = None
    extracted_at: Optional[str] = None
    record_type: Optional[str] = None
    week_of_plan: Optional[int] = None

    def __post_init__(self):
        """
        Post-initialization hook to perform any necessary transformations.
        """
        self.extracted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = datetime.datetime.fromtimestamp(
            self.created_on / 1000
        ).strftime("%Y-%m-%d %H:%M:%S")
        self.surrogate_key = self.activity_id
