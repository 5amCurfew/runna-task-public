import datetime
from .WorkoutSummary import WorkoutSummary
from dataclasses import dataclass
from .BaseDataClass import BaseDataClass

@dataclass
class Workout(BaseDataClass):
    workoutId: int
    metadata: dict

    def transform__summary(self) -> dict:
        self.summary = WorkoutSummary(**{
            "workoutId": self.workoutId,
            "workoutType": self.metadata.get("workoutType", None),
            "runType": self.metadata.get("runType", None),
            "distance": self.metadata.get("distance", None),
        })

    def transform__flatten_steps(self):
        flattened_steps = []

        for step in self.metadata["stepsV2"]:
            if step["type"] == "WorkoutRepeatStep":
                for _ in range(step["repeatValue"]):
                    for repeated_step in step["steps"]:
                        flattened_steps.append(repeated_step)
            else:
                flattened_steps.append(step)

        self.flattened_steps = flattened_steps
    
    def __post_init__(self):
        # Set ETL metadata
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogateKey = self.workoutId