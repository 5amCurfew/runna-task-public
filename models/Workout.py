import datetime
from .WorkoutRecord import WorkoutRecord
from dataclasses import dataclass
from typing import Optional

@dataclass
class Workout():
    workoutId: int
    metadata: dict
    extractedAt: Optional[str] = None
    surrogateKey: Optional[str] = None

    def transform__dim_workouts_record(self) -> dict:
        return WorkoutRecord(**{
            "workoutId": self.workoutId,
            "workoutType": self.metadata.get("workoutType", None),
            "runType": self.metadata.get("runType", None),
            "distance": self.metadata.get("distance", None),
        })

    def transform__bdg__workout_to_steps(self):
        flattened_workout_steps = []

        for step in self.metadata["stepsV2"]:
            if step["type"] == "WorkoutRepeatStep":
                for _ in range(step["repeatValue"]):
                    for repeated_step in step["steps"]:
                        flattened_workout_steps.append(repeated_step)
            else:
                flattened_workout_steps.append(step)

        return flattened_workout_steps
    
    def __post_init__(self):
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogateKey = self.workoutId