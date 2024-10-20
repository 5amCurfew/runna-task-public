from google.cloud import bigquery
from typing import Sequence

def load(table_id: str, data: list[dict]) -> Sequence[dict]:
    """
    Args:
        table_id (str): The full table ID in the format `project.dataset.table`.
        data (dict): The data object to write to BigQuery.
        sourcePath (str): parse sourcePath for reference for logging
    
    Returns BigQuery load errors if applicable
    """
    client = bigquery.Client(project="runna-task-public")
    errors = client.insert_rows_json(f"runna-task-public.activities.raw__{table_id}", data)
    if errors != []:
        return errors
    return None