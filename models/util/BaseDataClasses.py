from models.util import naming
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class BaseDataClass():

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]):
        snake_case_data = naming.convert_keys_to_snake_case(json_data)
        return cls(**snake_case_data)