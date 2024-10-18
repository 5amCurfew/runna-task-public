import datetime
from .ActivitySummary import ActivitySummary
from .Workout import Workout
from .WorkoutStep import WorkoutStep
from .Plan import Plan
from .ActivityLap import ActivityLap
from dataclasses import dataclass
from typing import Optional
from .BaseDataClass import BaseDataClass

@dataclass
class Activity(BaseDataClass):
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
        """
        Warning on data type conflict example
        """
        if not isinstance(self.userId, str):
            print(f"Warning: {self.sourcePath}: 'userId' type str, but got {type(self.userId).__name__}")
        if not isinstance(self.workoutId, str):
            print(f"Warning: {self.sourcePath}: 'workoutId' type str, but got {type(self.workoutId).__name__}")
        # Set ETL metadata
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogateKey = self.activityId
        if self.createdOn is None:
            self.createdOn = min(self.laps, key=lambda x: x["startTimestamp"]).get("startTimestamp")

    def transform__summary(self) -> dict:
        self.summary = ActivitySummary(**{
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

    # ########################
    # Transform: fct__activities
    # ########################
    def transform__fct__activities(self):
        """
        Transforms activity data into a summary format suitable for data warehouse insertion
        """
        self.transform__summary()
        return [self.summary.to_dict()]

    # ########################
    # Transform: dim__workouts
    # ########################
    def transform__dim__workouts(self):
        """
        Transform workout data into a summary for summary dimension table
        """
        workout = Workout(workoutId = self.workoutId, metadata = self.plannedWorkoutMetadata)
        workout.transform__summary()
        return [workout.summary.to_dict()]

    # ########################
    # Transform: dim__plans
    # ########################
    def transform__dim__plans(self):
        """
        Extract plan details for dimension table
        """
        return [Plan(planId = self.planDetails["id"], planLength = self.planDetails["planLength"]).to_dict()]

    # ########################
    # Transform: bdg__activity_to_laps
    # ########################
    def transform__bdg__activity_to_laps(self) -> list[dict]:
        """
        Transforms laps data into a format suitable for bridge table (activity -> laps)
        """
        return [
            {
                "surrogateKey": f"{self.activityId}::{index}",
                "activityID": self.activityId,
                "workoutStepSurrogateKey": f"{self.workoutId}::{index}",
                **ActivityLap(index=index, **lap).to_dict()
            }
            for index, lap in enumerate(self.laps)
        ]

    # ########################
    # Transform: bdg__workout_to_steps
    # ########################
    def transform__bdg__workout_to_steps(self) -> list[dict]:
        """
        Transforms workout steps into a format suitable for for bridge table (workout -> steps)
        """
        workout = Workout(
            workoutId=self.workoutId, 
            metadata=self.plannedWorkoutMetadata
        )
        workout.transform__flatten_steps()
        return [
            {
                "surrogateKey": f"{self.workoutId}::{index}",
                "workoutID": self.workoutId,
                **WorkoutStep(index=index, **step).to_dict()
            }
            for index, step in enumerate(workout.flattened_steps)
        ]