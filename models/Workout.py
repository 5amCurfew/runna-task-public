import datetime
from models.WorkoutRecord import WorkoutRecord
from dataclasses import dataclass


@dataclass
class Workout:
    workout_id: int
    metadata: dict
    extracted_at: str = None
    surrogate_key: str = None

    def transform__dim__workouts_record(self) -> dict:
        return WorkoutRecord(
            workout_id=self.workout_id,
            workout_type=self.metadata.get("workout_type", None),
            run_type=self.metadata.get("run_type", None),
            distance=self.metadata.get("distance", None),
        )

    def transform__bdg__workout_to_steps(self):
        flattened_workout_steps = []

        for step in self.metadata["steps_v2"]:
            if step["type"] == "WorkoutRepeatStep":
                for _ in range(step["repeat_value"]):
                    for repeated_step in step["steps"]:
                        flattened_workout_steps.append(repeated_step)
            else:
                flattened_workout_steps.append(step)

        return flattened_workout_steps

    def __post_init__(self):
        self.extracted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogate_key = self.workout_id
