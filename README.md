- [Runna Task Home Task, October 2024](#runna-task-home-task-october-2024)
   * [Introduction](#introduction)
   * [Data Model (Transformation)](#data-model-transformation)
      + [`fct__activities`](#fct__activities)
      + [`dim__plans`](#dim__plans)
      + [`dim__workouts`](#dim__workouts)
      + [`bdg__activity_to_laps`](#bdg__activity_to_laps)
      + [`bdg__workout_to_steps`](#bdg__workout_to_steps)
   * [Example Output](#example-output)
   * [Example Queries](#example-queries)

## Runna Take Home Task, October 2024

*We currently have ~30,000 activities landing in s3 per day. The representations of these activities are JSON files with data pertaining to activity performance, plan adherence (e.g. which week of their plan they are on) and user data (e.g. their current estimated 5k time).*

*The objective of this task is to create a robust data pipeline that processes workout data from a JSON structure, stores it in an optimal format, and makes it available for querying and analysis.*

### Introduction

The `etl` package contains [ParDo](https://beam.apache.org/documentation/transforms/python/elementwise/pardo/) functions used to extract, transform and load data in the [Apache Beam](https://beam.apache.org/) pipeline. It is assumed throughout that *daily batches* meets requirements for Runna.

Data transformation is handled by the `Activity` class within the `models` package (this is called in the `TransformFn`). This class is responsible for parsing and storing the data in the appropriate format to then *load* to the data warehouse. This includes transforming *Workout Steps* (bridge table), *Activity Laps* (bridge table) and the fact/dimensional models.

The data provided, in addition to replicated JSON files, can be found in the `data` directory, where each subdirectory reflects a **batch date** (this is to mirror a cloud storage system bucket, such as S3, for demonstration purposes).

The `pipeline.py` defines an [Apache Beam](https://beam.apache.org/) pipeline. This is the orchestrator for the ETL process.

### Data Model (Transformation)

![ERD](/assets/ERD.png)

*Note that presentation models are views on top of `raw__<TABLE_TYPE>__<ATOMIC_VALUE>` where the raw table creates a new row for each etl run. Please refer to `infra/bigquery__presentation.tf` for the definition of the presentation models.*

A `@dataclass` for each of the models is created in the `models` directory to validate the expected schema.

#### `fct__activities`

A fact table, where each row represents an activity. This is partitioned on `createdAt` (assumption for analysis) and clustered on `userID` (assumption for frequent joins) for performance.

```hcl
    time_partitioning {
        type = "DAY"
        field = "created_at"
    }

    clustering = [
        "user_id"
    ]
```

#### `dim__plans`

A dimension table, normalising plan metadata, namely `planLength`.

#### `dim__workouts`

A dimension table, normalising workout metadata, including `workoutType`, `runType` and `workoutType`.

#### `bdg__activity_to_laps`

A bridge table, mapping an activity (one) to laps (many). Lap metadata is stored here. This table is partitioned on `startTimestamp` and clustered on `activityID`.

```hcl
    time_partitioning {
        type = "DAY"
        field = "start_timestamp"
    }

    clustering = [
        "activity_id"
    ]
```

#### `bdg__workout_to_steps`

A bridge table, mapping a workout (one) to steps (many). Step metadata is stored here. This table is clustered on `workoutID`.

```hcl
    clustering = [
        "workout_id"
    ]
```

### Example Output

`python3 pipeline.py --batch_date 2024-10-01`

```bash
2024-10-26 12:12:07.308 - INFO - extracting data/2024-10-01/error-not-json.json
2024-10-26 12:12:07.311 - INFO - extracting data/2024-10-01/take-home-example-activity-6.json
2024-10-26 12:12:07.311 - WARNING - data/2024-10-01/error-not-json.json: JSONDecodeError: Expecting value: line 1 column 1 (char 0): data/2024-10-01/error-not-json.json skipping...
2024-10-26 12:12:07.311 - INFO - extracting data/2024-10-01/take-home-example-activity-5.json
2024-10-26 12:12:07.315 - INFO - extracting data/2024-10-01/take-home-example-activity-1.json
2024-10-26 12:12:07.321 - INFO - extracted data/2024-10-01/take-home-example-activity-6.json
2024-10-26 12:12:07.322 - INFO - transforming data/2024-10-01/take-home-example-activity-6.json
2024-10-26 12:12:07.338 - INFO - extracted data/2024-10-01/take-home-example-activity-1.json
2024-10-26 12:12:07.340 - INFO - transforming data/2024-10-01/take-home-example-activity-1.json
2024-10-26 12:12:07.359 - INFO - extracted data/2024-10-01/take-home-example-activity-5.json
2024-10-26 12:12:07.361 - INFO - transforming data/2024-10-01/take-home-example-activity-5.json
2024-10-26 12:12:07.393 - INFO - transformed data/2024-10-01/take-home-example-activity-6.json
2024-10-26 12:12:07.394 - INFO - extracting data/2024-10-01/take-home-example-activity-7-with-no-steps.json
2024-10-26 12:12:07.423 - INFO - transformed data/2024-10-01/take-home-example-activity-1.json
2024-10-26 12:12:07.424 - INFO - extracting data/2024-10-01/take-home-example-activity-1-with-no-activity-id.json
2024-10-26 12:12:07.429 - INFO - extracted data/2024-10-01/take-home-example-activity-7-with-no-steps.json
2024-10-26 12:12:07.431 - INFO - transforming data/2024-10-01/take-home-example-activity-7-with-no-steps.json
2024-10-26 12:12:07.451 - INFO - transformed data/2024-10-01/take-home-example-activity-5.json
2024-10-26 12:12:07.469 - INFO - extracted data/2024-10-01/take-home-example-activity-1-with-no-activity-id.json
2024-10-26 12:12:07.471 - INFO - transforming data/2024-10-01/take-home-example-activity-1-with-no-activity-id.json
2024-10-26 12:12:07.500 - WARNING - data/2024-10-01/take-home-example-activity-7-with-no-steps.json:bdg__workout_to_steps: failed transform 'steps_v2' skipping...
2024-10-26 12:12:07.500 - INFO - transformed data/2024-10-01/take-home-example-activity-7-with-no-steps.json
2024-10-26 12:12:07.511 - WARNING - data/2024-10-01/take-home-example-activity-1-with-no-activity-id.json: __init__() missing 2 required positional arguments: 'activity_id' and 'plan_details' skipping...
```