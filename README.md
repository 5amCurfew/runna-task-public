```bash
python3 main.py 2024-10-01
python3 main.py 2024-10-02
```

*How much did a user beat/miss their pace targets by on average?*
```SQL
select
  fct.userID,
  fct.activityID,
  bdg_to_laps.index as lapIndex,
  bdg_to_laps.averageSpeed,
  JSON_EXTRACT(bdg_to_steps.paces, "$.slow.mps"),
  JSON_EXTRACT(bdg_to_steps.paces, "$.fast.mps"),
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