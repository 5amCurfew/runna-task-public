import datetime
from dataclasses import dataclass
from typing import Optional
from .BaseDataClass import BaseDataClass

@dataclass
class Plan(BaseDataClass):
    planId: str
    planLength: Optional[int] = None

    def __post_init__(self):
        # Set ETL metadata
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogateKey = self.planId