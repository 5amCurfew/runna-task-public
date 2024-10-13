import datetime
from dataclasses import dataclass
from typing import Optional
from .BaseDataClass import BaseDataClass

@dataclass
class ActivitySummary(BaseDataClass):
    activityId: str
    createdOn: str
    planId: str
    sourcePath: str
    surrogateKey: str
    userId: str
    workoutId: str
    recordType: Optional[str] = None
    weekOfPlan: Optional[int] = None

    def __post_init__(self):
        """
        Post-initialization hook to perform any necessary transformations.
        """
        # Set ETL metadata
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.createdAt = datetime.datetime.fromtimestamp(self.createdOn / 1000).strftime("%Y-%m-%d %H:%M:%S")
        self.surrogateKey = self.activityId
