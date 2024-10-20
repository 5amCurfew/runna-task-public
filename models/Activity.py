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
    record_type: Optional[str] = None
    week_of_plan: Optional[int] = None
    extract_at: Optional[str] = None
    surrogate_key: Optional[str] = None

    def __post_init__(self):
        self.extracted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogate_key = self.activity_id
        if self.created_on is None:
            self.created_on = min(self.laps, key=lambda x: x["startTimestamp"]).get("startTimestamp")

    # ########################
    # Transform: fct__activities
    # ########################
    def transform__fct__activities_record(self) -> list[dict]:
        record = ActivityRecord(**{
                "activity_id": self.activity_id,
                "created_on": self.created_on,
                "plan_id": self.plan_details["id"],
                "source_path": self.source_path,
                "surrogate_key": self.surrogate_key,
                "user_id": self.user_id,
                "workout_id": self.workout_id,
                "record_type": self.record_type,
                "week_of_plan": self.week_of_plan,
                "current_est5k_time_in_secs": self.planned_workout_metadata.get("currentEst5kTimeInSecs", None),
        })
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
                "surrogate_key": f"{self.activity_id}::{index}",
                "activity_id": self.activity_id,
                "workout_step_surrogate_key": f"{self.workout_id}::{index}",
                **ActivityLap(index=index, **lap).__dict__
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
        record = Plan(planId = self.plan_details["id"], planLength = self.plan_details.get("planLength", None))
        return [record.__dict__]

    # ########################
    # Transform: dim__workouts
    # ########################
    def transform__dim__workouts_record(self) -> list[dict]:
        """
        Transform workout data into a summary for summary dimension table
        """
        record = Workout(workoutId = self.workout_id, metadata = self.planned_workout_metadata).transform__dim_workouts_record()
        return [record.__dict__]

    # ########################
    # Transform: bdg__workout_to_steps
    # ########################
    def transform__bdg__workout_to_steps_record(self) -> list[dict]:
        """
        Transforms workout steps into a format suitable for for bridge table (workout -> steps)
        """
        records = Workout(workoutId=self.workout_id, metadata=self.planned_workout_metadata).transform__bdg__workout_to_steps()
        return [
            {
                "surrogateKey": f"{self.workoutId}::{index}",
                "workoutID": self.workoutId,
                **WorkoutStep(index=index, **step).__dict__
            }
            for index, step in enumerate(records)
        ]