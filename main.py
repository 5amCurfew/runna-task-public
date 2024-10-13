import argparse
import concurrent.futures
import datetime
import etl
import os
from models import Activity

def process_activity(path: str) -> str:
    # ########################
    # EXTRACT
    # ########################
    data, extract_error = etl.extract(f"{path}")
    if data is None:
        raise Exception(f"Warning: {path}: {extract_error}. skipping...")
    
    # ########################
    # TRANSFORM
    # ########################    
    try:
        activity = Activity(**data)
    except TypeError as e:
        print(f"Warning: {path}: {e}. skipping...")
        return
    
    # ########################
    # LOAD
    # ########################
    etl.load("runna-task-public.activities.raw__fct__activities", [activity.transform__fct__activities()], activity.sourcePath)
    etl.load("runna-task-public.activities.raw__dim__plans", [activity.transform__dim__plans()], activity.sourcePath)
    etl.load("runna-task-public.activities.raw__dim__workouts", [activity.transform__dim__workouts()], activity.sourcePath)
    etl.load("runna-task-public.activities.raw__bdg__activity_to_laps", activity.transform__bdg__activity_to_laps(), activity.sourcePath)
    etl.load("runna-task-public.activities.raw__bdg__workout_to_steps", activity.transform__bdg__workout_to_steps(), activity.sourcePath)
    print(f"{path} loaded successfully at {datetime.datetime.now()}")


# ########################
# Process files in parallel
# (for demonstration purposes, a concurrency of 2 is used)
# ########################
def process_batch(batch_date: str):
    data_dir = f"data/{batch_date}"
    file_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f))]
   
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_path = {executor.submit(process_activity, path): path for path in file_paths}
        for future in concurrent.futures.as_completed(future_to_path):
            path = future_to_path[future]
            try:
                future.result()
            except Exception as exc:
                print(f"Error: {path}: {exc}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process activity files for a specific batch date')
    parser.add_argument('batch_date', type=str, help='Batch date in YYYY-MM-DD format')
    args = parser.parse_args()

    batch_date = args.batch_date
    process_batch(batch_date)

