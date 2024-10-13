## Runna Task Home Task, October 2024

*We currently have ~30,000 activities landing in s3 per day. The representations of these activities are JSON files with data pertaining to activity performance, plan adherence (e.g. which week of their plan they are on) and user data (e.g. their current estimated 5k time).*

*The objective of this task is to create a robust data pipeline that processes workout data from a JSON structure, stores it in an optimal format, and makes it available for querying and analysis.*

### Introduction

Cloud infrastructure for this task is provided in the `infra` directory. This includes creation of data sinks (BigQuery tables) and the presentation views presented for analytics. For more information, see the `README.md` in the `infra` directory. Terraform is used to manage the infrastructure. *Note that GCP & BigQuery was chosen for ease due to my existing personal accounts. The principles can also be applied to AWS & Redshift.*

The `etl` directory contains the *extract* and *load* functions used for the pipeline. It is assumed throughout that **daily batches** meets requirements for this data. `extract` reads from JSON file, and `load` writes to BigQuery.

The data provided, in addition to replicated JSON files, can be found in the `data` directory, where each subdirectory reflects a **batch date** (this is to mirror a cloud storage system, such as S3, for demonstration purposes).

**Data transformation** is handled by the `Activity` class within the `models` directory. This class is responsible for parsing and storing the data in the appropriate format. This includes transforming *Workout Steps* (bridge table), *Activity Laps* (bridge table) and the fact/dimensional models.

Mock-batches are processed in the `main.py` file.

```bash
python3 main.py 2024-10-01
python3 main.py 2024-10-02
```

### Data Model


### Example Queries

*How much did a user beat/miss their pace targets by on average?*

```SQL
select
  fct.userID,
  fct.activityID,
  bdg_to_laps.index as lapIndex,
  bdg_to_laps.averageSpeed,
  JSON_EXTRACT(bdg_to_steps.paces, "$.slow.mps") as slowPace,
  JSON_EXTRACT(bdg_to_steps.paces, "$.fast.mps") as fastPace,
from
  `activities.fct__activities` as fct
  inner join `activities.bdg__activity_to_laps` as bdg_to_laps
    on bdg_to_laps.activityID = fct.activityID
  left join `activities.bdg__workout_to_steps` as bdg_to_steps
    on bdg_to_steps.surrogateKey = bdg_to_laps.workoutStepSurrogateKey
order by
  userID, activityID, lapIndex
```

*How does this workout distance compare to their workouts in the previous week of their plan?*

```SQL
select
  fct.userID,
  fct.planID,
  fct.activityID,
  fct.weekOfPlan,
  workouts.distance,
  AVG(prev_workouts.distance) OVER (PARTITION BY fct.userID, fct.planID ORDER BY fct.weekOfPlan) AS avg_distance_prior_week
from
  `activities.fct__activities` AS fct
  left join `activities.dim__workouts` workouts
    on workouts.workoutID = fct.workoutID
  -- Join the previous week's activities to get the average distance
  left join `activities.fct__activities` AS prev_fct
    on fct.userID = prev_fct.userID
    and fct.planID = prev_fct.planID
    and fct.weekOfPlan = prev_fct.weekOfPlan + 1
  left join `activities.dim__workouts` prev_workouts
    on prev_workouts.workoutID = prev_fct.workoutID
ORDER BY
  fct.userID, fct.planID, fct.weekOfPlan;
```

*How did this user perform compared with other users in this same workout?*

```SQL
select 
  workouts.workoutID,
  steps.index as workoutStep,
  laps.surrogateKey,
  laps.averageSpeed,
  fct.userID,
  RANK() OVER (PARTITION BY steps.surrogateKey ORDER BY laps.averageSpeed DESC)
from  
  `activities.fct__activities` AS fct
  inner join `activities.dim__workouts` workouts
    ON workouts.workoutID = fct.workoutID
  inner join `activities.bdg__workout_to_steps` steps
    on steps.workoutID = fct.workoutID
  left join `activities.bdg__activity_to_laps` laps
    on laps.workoutStepSurrogateKey = steps.surrogateKey
    and laps.activityID = fct.activityID
order by
  workoutID, workoutStep, averageSpeed desc
```

*In the last 6 months, how many TEMPO sessions have been completed?*

```SQL
with activity_steps_completed as (
  select 
    fct.activityID,
    workouts.runType,
    count(laps.surrogateKey) as total,
  from
    `activities.fct__activities` AS fct
    inner join `activities.dim__workouts` workouts
      on workouts.workoutID = fct.workoutID
      and workouts.runType = 'TEMPO'
    left join `activities.bdg__activity_to_laps` laps
      on laps.activityID = fct.activityID
  where date(fct.createdAt) >= current_date() - interval 6 month
  group by 
    1,2
)

,activity_steps as (
  select 
    fct.activityID,
    workouts.runType,
    count(steps.surrogateKey) as total,
  from
    `activities.fct__activities` AS fct
    inner join `activities.dim__workouts` workouts
      on workouts.workoutID = fct.workoutID
    left join `activities.bdg__workout_to_steps` steps
      on steps.workoutID = fct.workoutID
  group by 
    1,2
)

select
  activity_steps_completed.activityID,
  activity_steps_completed.runType,
  activity_steps_completed.total as steps_completed,
  activity_steps.total as steps,
  case when activity_steps_completed.total = activity_steps.total then true else false end as isCompleted
from 
  activity_steps_completed
  inner join activity_steps
    on activity_steps.activityID = activity_steps_completed.activityID
```


### File Structure
```bash
runna-task-public/
┣ data/
┃ ┣ 2024-10-01/
┃ ┗ 2024-10-02/
┣ etl/
┃ ┣ __init__.py
┃ ┣ extract.py
┃ ┗ load.py
┣ infra/
┃ ┣ schema/
┃ ┣ README.md
┃ ┣ backend.hcl
┃ ┣ bigquery__presentation.tf
┃ ┣ bigquery__raw.tf
┃ ┗ main.tf
┣ models/
┃ ┣ Activity.py
┃ ┣ ActivityLap.py
┃ ┣ ActivitySummary.py
┃ ┣ BaseDataClass.py
┃ ┣ Plan.py
┃ ┣ Workout.py
┃ ┣ WorkoutStep.py
┃ ┣ WorkoutSummary.py
┃ ┗ __init__.py
┣ .gitignore
┣ .python-version
┣ Makefile
┣ README.md
┣ main.py
┗ requirements.txt
```


#### Notes

A PLAN is a collection of scheduled WORKOUTs
- ID: unique identifier of the plan
- planLength: the total duration of the plan

An ACTIVITY is a record of performance during a WORKOUT
- ID: unique identifier of the activity
- userID: identifier of the user
- workoutID: unique identifier of the workout
- weekOfPlan: the week of the plan at the time of the activity
- ...

A WORKOUT is a collection of STEPS
- ID: unique identifier of the workout
- workoutType: classifier of the workout
- runType: classifier of the run
- plannedWorkoutDate: scheduled date of the workout
- ...

A STEP is an component of a workout (completion reflected in an activity LAP)
- type: classifier of the step
- duration: duration of the step
- ...

fct__activities

* -> dim__workouts
* -> dim__plans
* -> bdg__activity_to_laps

dim__plans

* <- fct__activities

dim__workouts

* <- fct__activities
* -> bdg__workout_to_steps

bdg__activity_to_laps

* <- fct__activities
* -> bdg__workout_to_steps

bdg__workout_to_steps

* <- dim__workouts
* <- bdg__activity_to_lap 