import datetime
from dataclasses import dataclass

@dataclass
class BaseDataClass:
    def to_dict(self) -> dict:
        """Convert the dataclass instance to a dictionary."""
        return {**self.__dict__}

    def __post__init__(self):
        """
        Post-initialization hook to perform any necessary transformations.
        """
        self.extractedAt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
