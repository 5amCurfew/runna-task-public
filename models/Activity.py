import datetime
from models.ActivityRecord import ActivityRecord
from models.Workout import Workout
from models.WorkoutStep import WorkoutStep
from models.Plan import Plan
from models.ActivityLap import ActivityLap
from dataclasses import dataclass
from typing import Optional
from models.util.BaseDataClasses import BaseDataClass


@dataclass
class Activity(BaseDataClass):
    activity_id: str
    laps: list[dict]
    plan_details: dict
    planned_workout_metadata: dict
    source_path: str
    unit_of_measure: str
    user_id: str
    waypoints: list[dict]
    workout_id: str
    created_on: Optional[int] = None
    extracted_at: str = None
    record_type: Optional[str] = None
    surrogate_key: str = None
    week_of_plan: Optional[int] = None

    def __post_init__(self):
        self.extracted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogate_key = self.activity_id
        if self.created_on is None:
            self.created_on = min(self.laps, key=lambda x: x["startTimestamp"]).get(
                "startTimestamp"
            )

    # ########################
    # Transform: fct__activities
    # ########################
    def transform__fct__activities_record(self) -> list[dict]:
        record = ActivityRecord(
            activity_id=self.activity_id,
            created_on=self.created_on,
            current_est5k_time_in_secs=self.planned_workout_metadata.get(
                "current_est5k_time_in_secs", None
            ),
            plan_id=self.plan_details["id"],
            record_type=self.record_type,
            source_path=self.source_path,
            surrogate_key=self.surrogate_key,
            user_id=self.user_id,
            week_of_plan=self.week_of_plan,
            workout_id=self.workout_id,
        )

        return [record.__dict__]

    # ########################
    # Transform: bdg__activity_to_laps
    # ########################
    def transform__bdg__activity_to_laps_record(self) -> list[dict]:
        """
        Transforms laps data into a format suitable for bridge table (activity -> laps)
        """
        return [
            {
                "workout_step_surrogate_key": f"{self.workout_id}::{index}",
                **ActivityLap(
                    activity_id=self.activity_id, index=index, **lap
                ).__dict__,
            }
            for index, lap in enumerate(self.laps)
        ]

    # ########################
    # Transform: dim__plans
    # ########################
    def transform__dim__plans_record(self) -> list[dict]:
        """
        Extract plan details for dimension table
        """
        record = Plan(
            plan_id=self.plan_details["id"],
            plan_length=self.plan_details.get("plan_length", -1),
        )

        return [record.__dict__]

    # ########################
    # Transform: dim__workouts
    # ########################
    def transform__dim__workouts_record(self) -> list[dict]:
        """
        Transform workout data into a summary for summary dimension table
        """
        workout = Workout(
            workout_id=self.workout_id, metadata=self.planned_workout_metadata
        )
        record = workout.transform__dim__workouts_record()

        return [record.__dict__]

    # ########################
    # Transform: bdg__workout_to_steps
    # ########################
    def transform__bdg__workout_to_steps_record(self) -> list[dict]:
        """
        Transforms workout steps into a format suitable for for bridge table (workout -> steps)
        """
        workout = Workout(
            workout_id=self.workout_id, metadata=self.planned_workout_metadata
        )
        records = workout.transform__bdg__workout_to_steps()

        return [
            {**WorkoutStep(workout_id=self.workout_id, index=index, **step).__dict__}
            for index, step in enumerate(records)
        ]
