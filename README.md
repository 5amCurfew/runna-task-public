```bash
python3 main.py 2024-10-01
python3 main.py 2024-10-02
```

-- How much did a user beat/miss their pace targets by on average?
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
  left join `activities.bdg__activity_to_laps` as bdg_to_laps
    on bdg_to_laps.activityID = fct.activityID
  left join `activities.bdg__workout_to_steps` as bdg_to_steps
    on bdg_to_steps.surrogateKey = bdg_to_laps.workoutStepSurrogateKey
order by
  userID, activityID, lapIndex
```

--TODO How does this workout distance compare to their workouts in the previous week of their plan?
select
  fct.userID,
  fct.planID,
  fct.weekOfPlan,
  workouts.distance
from
  `activities.fct__activities` as fct
  left join `activities.dim__workouts` workouts
    on workouts.workoutID = fct.workoutID
order by
  userID, planID, weekOfPlan;


--TODO How did this user perform compared with other users in this same workout?
--TODO In the last 6 months, how many TEMPO sessions have been completed?



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