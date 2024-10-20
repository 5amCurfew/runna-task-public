import datetime
from .ActivityRecord import ActivityRecord
from .Workout import Workout
from .WorkoutStep import WorkoutStep
from .Plan import Plan
from .ActivityLap import ActivityLap
from dataclasses import dataclass
from typing import Optional

@dataclass
class Activity():
    activityId: str
    laps: list[dict]
    planDetails: dict
    plannedWorkoutMetadata: dict
    sourcePath: str
    unitOfMeasure: str
    userId: str
    waypoints: list[dict]
    workoutId: str
    createdOn: Optional[int] = None
    recordType: Optional[str] = None
    weekOfPlan: Optional[int] = None

    def __post_init__(self):
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogateKey = self.activityId
        if self.createdOn is None:
            self.createdOn = min(self.laps, key=lambda x: x["startTimestamp"]).get("startTimestamp")

    # ########################
    # Transform: fct__activities
    # ########################
    def transform__fct__activities_record(self) -> list[dict]:
        record = ActivityRecord(**{
                "activityId": self.activityId,
                "createdOn": self.createdOn,
                "planId": self.planDetails["id"],
                "sourcePath": self.sourcePath,
                "surrogateKey": self.surrogateKey,
                "userId": self.userId,
                "workoutId": self.workoutId,
                "recordType": self.recordType,
                "weekOfPlan": self.weekOfPlan,
                "currentEst5kTimeInSecs": self.plannedWorkoutMetadata.get("currentEst5kTimeInSecs", None),
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
                "surrogateKey": f"{self.activityId}::{index}",
                "activityID": self.activityId,
                "workoutStepSurrogateKey": f"{self.workoutId}::{index}",
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
        record = Plan(planId = self.planDetails["id"], planLength = self.planDetails["planLength"])
        return [record.__dict__]

    # ########################
    # Transform: dim__workouts
    # ########################
    def transform__dim__workouts_record(self) -> list[dict]:
        """
        Transform workout data into a summary for summary dimension table
        """
        record = Workout(workoutId = self.workoutId, metadata = self.plannedWorkoutMetadata).transform__dim_workouts_record()
        return [record.__dict__]

    # ########################
    # Transform: bdg__workout_to_steps
    # ########################
    def transform__bdg__workout_to_steps_record(self) -> list[dict]:
        """
        Transforms workout steps into a format suitable for for bridge table (workout -> steps)
        """
        records = Workout(workoutId=self.workoutId, metadata=self.plannedWorkoutMetadata).transform__bdg__workout_to_steps()
        return [
            {
                "surrogateKey": f"{self.workoutId}::{index}",
                "workoutID": self.workoutId,
                **WorkoutStep(index=index, **step).__dict__
            }
            for index, step in enumerate(records)
        ]