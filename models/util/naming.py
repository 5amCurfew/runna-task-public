import re
from typing import Dict, Any

# Utility function to convert camelCase to snake_case
def camel_to_snake(name: str) -> str:
    # Convert from camelCase to snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# Function to convert a JSON dict's keys to snake_case
def convert_keys_to_snake_case(data: Dict[str, Any]) -> Dict[str, Any]:
    return {camel_to_snake(k): v for k, v in data.items()}