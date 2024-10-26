from dataclasses import dataclass
from typing import Optional
import datetime


@dataclass
class Plan:
    plan_id: str
    extracted_at: str = None
    plan_length: Optional[int] = None
    surrogate_key: str = None

    def __post_init__(self):
        self.extracted_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogate_key = self.plan_id
