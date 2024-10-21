import json

def extract(path: str) -> tuple[dict, str]:
    """
    Extracts activity data from a given JSON file
    """
    try:
        with open(path, "r") as file:
            data = json.load(file)
            data['sourcePath'] = path
            return data, None
    except FileNotFoundError as e:
        return None, str(f"FileNotFoundError: {e}")
    except json.JSONDecodeError as e:
        return None, str(f"JSONDecodeError: {e}")