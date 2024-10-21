import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class WorkoutRecord:
    workout_id: str
    distance: Optional[float] = None
    extracted_at: Optional[str] = None
    extracted_at: str = None
    run_type: Optional[str] = None
    surrogate_key: Optional[str] = None
    surrogate_key: str = None
    workout_type: Optional[str] = None

    def __post_init__(self):
        self.extracted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogate_key = self.workout_id
