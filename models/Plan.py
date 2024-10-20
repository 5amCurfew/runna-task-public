import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Plan():
    planId: str
    planLength: Optional[int] = None
    extractedAt: Optional[str] = None
    surrogateKey: Optional[str] = None
    
    def __post_init__(self):
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.surrogateKey = self.planId