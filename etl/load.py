from google.cloud import bigquery

def load(table_id: str, data: list[dict], sourcePath: str) -> None:
    """
    Args:
        table_id (str): The full table ID in the format `project.dataset.table`.
        data (dict): The data object to write to BigQuery.
        sourcePath (str): parse sourcePath for reference for logging
    
    Returns:
        None
    """
    client = bigquery.Client(project="runna-task-public")
    try:
        errors = client.insert_rows_json(table_id, data)
        if errors != []:
            print(f"Warning: {sourcePath}: errors while inserting rows: {errors}")
    except Exception as e:
        print(f"Failed to load: {e}")