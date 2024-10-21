import re
from typing import Dict, Any, Union, List


def to_snake_case(s: str) -> str:
    """Helper function to convert camelCase or PascalCase to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()


def convert_keys_to_snake_case(
    data: Union[Dict[str, Any], List[Any]],
) -> Union[Dict[str, Any], List[Any]]:
    """Recursively convert all dictionary keys to snake_case."""
    if isinstance(data, dict):
        new_data = {}
        for key, value in data.items():
            new_key = to_snake_case(key)
            new_data[new_key] = convert_keys_to_snake_case(value)
        return new_data
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data]
    else:
        return data
