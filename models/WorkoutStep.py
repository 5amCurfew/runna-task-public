import datetime
import json
from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkoutStep():
    index: int
    durationType: Optional[str] = None
    durationValue: Optional[float] = None
    durationValueType: Optional[str] = None
    intensity: Optional[str] = None
    paces: Optional[dict] = None
    repeatValue: Optional[int] = None
    stepOrder: Optional[int] = None
    steps: Optional[int] = None
    targetType: Optional[str] = None
    type: Optional[str] = None

    def __post_init__(self):
        if self.paces is not None:
            self.paces = json.dumps(self.paces)
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")