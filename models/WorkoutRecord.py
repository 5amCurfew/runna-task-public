import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class WorkoutRecord():
    workoutId: str
    workoutType: Optional[str] = None
    runType: Optional[str] = None
    distance: Optional[float] = None
    extractedAt: Optional[str] = None
    surrogateKey: Optional[str] = None
    
    def __post_init__(self):
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogateKey = self.workoutId