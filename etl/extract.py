import datetime
import json

def extract(path: str) -> tuple[dict, str]:
    """
    Extracts activity data from a given JSON file (demonstration here is for local file storage)

    Returns:
        tuple[dict, str]: A tuple containing:
            - dict: The extracted data from the JSON file with additional metadata if successful, or None if an error occurs.
            - str: An error message if an exception is raised, or None if no error occurs.
    
    Raises:
        FileNotFoundError: If the file is not found.
        JSONDecodeError: If the file contains invalid JSON data.
    """
    print(f"{path} extraction at {datetime.datetime.now()}...")

    try:
        with open(path, "r") as file:
            data = json.load(file)
            data['sourcePath'] = path
            return data, None
    except FileNotFoundError as e:
        print(f"Warning: file not found {path} - skipping...")
        return None, str(e)
    except json.JSONDecodeError as e:
        print(f"Warning: invalid json at {path} - skipping...")
        return None, str(e)