import datetime
from dataclasses import dataclass
from typing import Optional
from .BaseDataClass import BaseDataClass

@dataclass
class Lap(BaseDataClass):
    index: int
    averageCadence: Optional[float] = None
    averageHeartRate: Optional[float] = None
    averageSpeed: Optional[float] = None
    distance: Optional[float] = None
    elevationGain: Optional[float] = None
    maxCadence: Optional[float] = None
    maxElevation: Optional[float] = None
    maxHeartRate: Optional[int] = None
    maxSpeed: Optional[float] = None
    minElevation: Optional[float] = None
    minHeartRate: Optional[float] = None
    movingTime: Optional[float] = None
    startTimestamp: Optional[int] = None
    totalTime: Optional[float] = None
    wktStepIndex: Optional[int] = None

    def __post_init__(self):
        # If startTimestamp is provided, divide it by 1000
        if self.startTimestamp is not None:
            self.startTimestamp /= 1000
        # Set ETL metadata
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
