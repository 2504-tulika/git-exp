# Zombie Survival DAG

An Apache Airflow DAG built for the "Zombie Apocalypse Survival" assignment. The idea was to automate a survivor camp's dawn/dusk routine — check the perimeter, decide whether to fight or hide, ration supplies, take a headcount, and radio in a report — instead of someone doing all of that manually every shift.

## What the DAG actually does

```
dawn_patrol_scan --> decide_fight_or_hide --> engage_threat     ---\
                                          \--> fortify_barricade ---> survivor_headcount --> radio_checkin
ration_supplies ------------------------------------------------------^
```

`dawn_patrol_scan` runs first and estimates a threat level between 0 and 10, based on how many zombies the (simulated) perimeter scan picks up. That number decides everything downstream, so it gets pushed to XCom right away instead of being recalculated later.

`ration_supplies` runs alongside it — I kept this separate from the threat check on purpose, because in a real camp, "how many zombies are outside" and "how much food is left" are two completely different problems that happen to get reported together at the end, not one thing.

`decide_fight_or_hide` is where the branching happens. If the threat level is 5 or above, it routes to `engage_threat`. If it's below 5, it routes to `fortify_barricade` instead. Only one of these two ever actually runs — the other shows up as skipped in the graph view, which is the "deliberately skipped task" requirement for this assignment.

Both branches lead back into `survivor_headcount`, which needed a `none_failed_min_one_success` trigger rule since one of its upstream tasks is always going to be skipped by design — the default trigger rule would've made this task skip too, which isn't what I wanted.

Last task is `radio_checkin`, a BashOperator that pulls the threat level, supply count, and headcount straight out of XCom using Jinja templating and logs a final situation report.

## Why I passed threat_level through XCom

I picked `threat_level` as the main thing to move between tasks because it's the one value the entire rest of the run depends on — the branch decision, what `engage_threat` logs about itself, and what ends up in the final radio report all trace back to that single number from the patrol scan. Recomputing it in every task that needed it would've meant the "scan" logic living in three different places, which felt messy, so XCom made more sense than repeating it.

`supply_count` and `headcount` also get pushed and pulled later on so the final report has real numbers instead of placeholders.

## Why engage_threat gets skipped sometimes

The skip condition is simple: if the patrol doesn't find enough zombies to justify a fight (threat level under 5), there's no reason to send anyone out to engage — better to just reinforce the barricade and move on. I used a `BranchPythonOperator` for this instead of a `ShortCircuitOperator` because I wanted an actual alternate path to run (`fortify_barricade`), not just a task getting skipped with nothing replacing it.

## Why this schedule

`0 6,18 * * *` — 6 AM and 6 PM, every day. A survivor camp isn't going to reassess the situation once at midnight like a generic `@daily` schedule would suggest. Dawn makes sense because that's before anyone heads out to scavenge, and dusk makes sense because that's the last check before the camp locks down for the night.

## Screenshots

**Graph view of a completed run**, with the skipped task visible:

![Graph view showing completed run](screenshots/graph_view.png)

In this run the threat level came out low, so `engage_threat` shows up skipped and `fortify_barricade` ran instead.

**Triggering the DAG through the Airflow REST API** (not the UI button):

![API trigger request and response](screenshots/api_trigger.png)

The response comes back with a `dag_run_id` and a `state`, confirming the run was actually kicked off through the API rather than clicked through the UI.

## Running it yourself

1. Clone this repo and drop `dags/zombie_survival_dag.py` into an Airflow `dags/` folder.
2. Start Airflow (I used the standard Docker Compose setup).
3. Unpause `zombie_survival_dag` from the UI.
4. Trigger a run through the API:
   ```
   curl -X POST 'http://localhost:8080/api/v1/dags/zombie_survival_dag/dagRuns' \
     -H 'Content-Type: application/json' \
     -u airflow:airflow \
     -d '{}'
   ```
5. Check the Graph view once it finishes to see the branch outcome.
