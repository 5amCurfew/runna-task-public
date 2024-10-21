import datetime
import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkoutStep():
    workout_id: int
    index: int
    duration_type: Optional[str] = None
    duration_value: Optional[float] = None
    duration_value_type: Optional[str] = None
    extracted_at: str = None
    intensity: Optional[str] = None
    paces: Optional[dict] = None
    repeat_value: Optional[int] = None
    step_order: Optional[int] = None
    steps: Optional[int] = None
    surrogate_key: str = None
    target_type: Optional[str] = None
    type: Optional[str] = None
    
    def __post_init__(self):
        if self.paces is not None:
            self.paces = json.dumps(self.paces)
        self.extracted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogate_key = f"{self.workout_id}:{self.index}"