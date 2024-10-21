import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class ActivityLap():
    activity_id: str
    index: int
    average_cadence: Optional[float] = None
    average_heart_rate: Optional[float] = None
    average_speed: Optional[float] = None
    distance: Optional[float] = None
    elevation_gain: Optional[float] = None
    extracted_at: str = None
    max_cadence: Optional[float] = None
    max_elevation: Optional[float] = None
    max_heart_rate: Optional[int] = None
    max_speed: Optional[float] = None
    min_elevation: Optional[float] = None
    min_heart_rate: Optional[float] = None
    moving_time: Optional[float] = None
    start_timestamp: Optional[int] = None
    surrogate_key: str = None
    total_time: Optional[float] = None
    wkt_step_index: Optional[int] = None
    
    def __post_init__(self):
        # If startTimestamp is provided, divide it by 1000
        if self.start_timestamp is not None:
            self.start_timestamp /= 1000
        self.extracted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogate_key = f"{self.activity_id}::{self.index}"
