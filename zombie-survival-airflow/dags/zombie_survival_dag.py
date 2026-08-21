from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator

THREAT_THRESHOLD = 5          
CRITICAL_SUPPLY_LEVEL = 10    # supply_count below this => critical warning

DEFAULT_ARGS = {
    "owner": "bunker_survivors",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "depends_on_past": False,
}

logger = logging.getLogger("airflow.task")

def dawn_patrol_scan(**context) -> None:
    """Scan the perimeter and estimate a threat level (0-10).

    Pushes `threat_level` and `zombie_count` to XCom so downstream tasks
    (branching, engagement, the final report) don't have to re-derive them.
    """
    zombie_count = random.randint(0, 12)
    threat_level = min(zombie_count, 10)

    logger.debug("Raw perimeter sensor reading: %s zombies spotted", zombie_count)
    logger.info("Calculated threat_level=%s (from zombie_count=%s)", threat_level, zombie_count)

    if threat_level >= THREAT_THRESHOLD:
        logger.warning(
            "Threat level %s meets/exceeds fight threshold of %s", threat_level, THREAT_THRESHOLD
        )
    else:
        logger.info(
            "Threat level %s is below fight threshold of %s — perimeter looks safe",
            threat_level, THREAT_THRESHOLD,
        )

    context["ti"].xcom_push(key="threat_level", value=threat_level)
    context["ti"].xcom_push(key="zombie_count", value=zombie_count)


def decide_fight_or_hide(**context) -> str:
    """Branch the DAG based on the threat_level recorded during patrol.

    Returns the task_id that should run next. Airflow automatically marks
    the *other* branch as skipped, which satisfies the "deliberately skip
    a task" requirement — the skip condition here is "threat_level below
    THREAT_THRESHOLD".
    """
    threat_level = context["ti"].xcom_pull(task_ids="dawn_patrol_scan", key="threat_level")
    logger.info("Pulled threat_level=%s from dawn_patrol_scan for branch decision", threat_level)

    if threat_level is None:
        logger.error("threat_level missing from XCom — defaulting to fortify_barricade for safety")
        return "fortify_barricade"

    if threat_level >= THREAT_THRESHOLD:
        logger.warning("Decision: FIGHT — threat_level %s requires engagement", threat_level)
        return "engage_threat"

    logger.info(
        "Decision: HIDE — threat_level %s is manageable, engage_threat will be skipped", threat_level
    )
    return "fortify_barricade"


def engage_threat(**context) -> None:
    """Fight-day task. Only reached when decide_fight_or_hide routes here."""
    ti = context["ti"]
    threat_level = ti.xcom_pull(task_ids="dawn_patrol_scan", key="threat_level")
    zombie_count = ti.xcom_pull(task_ids="dawn_patrol_scan", key="zombie_count")

    logger.critical(
        "Engaging %s zombies at threat_level=%s — all hands to the perimeter", zombie_count, threat_level
    )
    logger.info("Engagement complete. Perimeter secured, no casualties reported.")


def ration_supplies(**context) -> None:
    """Count remaining supplies independently of the threat assessment.

    Runs in parallel with the patrol/branch chain and pushes `supply_count`
    to XCom for the final situation report.
    """
    supply_count = random.randint(0, 30)
    logger.debug("Inventory scan returned raw supply_count=%s", supply_count)

    if supply_count < CRITICAL_SUPPLY_LEVEL:
        logger.warning(
            "Supplies CRITICAL: %s units remain (below threshold of %s)",
            supply_count, CRITICAL_SUPPLY_LEVEL,
        )
    else:
        logger.info("Supplies sufficient: %s units remain", supply_count)

    context["ti"].xcom_push(key="supply_count", value=supply_count)


def survivor_headcount(**context) -> None:
    """Take a headcount and compile the end-of-shift situation report.

    Uses trigger_rule='none_failed_min_one_success' at the DAG level so it
    still runs even though exactly one of engage_threat / fortify_barricade
    was skipped upstream.
    """
    ti = context["ti"]
    threat_level = ti.xcom_pull(task_ids="dawn_patrol_scan", key="threat_level")
    supply_count = ti.xcom_pull(task_ids="ration_supplies", key="supply_count")
    headcount = random.randint(3, 8)

    logger.info("Headcount complete: %s survivors accounted for", headcount)
    logger.info(
        "Situation report — threat_level=%s, supply_count=%s, survivors=%s",
        threat_level, supply_count, headcount,
    )

    if supply_count is not None and supply_count < CRITICAL_SUPPLY_LEVEL:
        logger.warning("Report flags a supply run as urgent before the next shift")

    ti.xcom_push(key="headcount", value=headcount)


with DAG(
    dag_id="zombie_survival_dag",
    description="Recurring dawn/dusk survivor routine: scan, decide, ration, report.",
    default_args=DEFAULT_ARGS,
    # Twice a day: 06:00 (dawn patrol) and 18:00 (dusk lockdown) — matches
    # the two moments a survivor camp actually needs to reassess the
    # situation, rather than an arbitrary @daily run.
    schedule_interval="0 6,18 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["zombie-survival", "training"],
) as dag:

    dawn_patrol_scan_task = PythonOperator(
        task_id="dawn_patrol_scan",
        python_callable=dawn_patrol_scan,
    )

    ration_supplies_task = PythonOperator(
        task_id="ration_supplies",
        python_callable=ration_supplies,
    )

    decide_fight_or_hide_task = BranchPythonOperator(
        task_id="decide_fight_or_hide",
        python_callable=decide_fight_or_hide,
    )

    engage_threat_task = PythonOperator(
        task_id="engage_threat",
        python_callable=engage_threat,
    )

    fortify_barricade_task = BashOperator(
        task_id="fortify_barricade",
        bash_command=(
            "echo '[INFO] Barricade check starting for threat_level="
            "{{ ti.xcom_pull(task_ids=\"dawn_patrol_scan\", key=\"threat_level\") }}' && "
            "echo '[INFO] Reinforcing weak points on the east and west gates' && "
            "echo '[INFO] Barricade secured — no engagement required this shift'"
        ),
    )

    survivor_headcount_task = PythonOperator(
        task_id="survivor_headcount",
        python_callable=survivor_headcount,
        trigger_rule="none_failed_min_one_success",
    )

    radio_checkin_task = BashOperator(
        task_id="radio_checkin",
        bash_command=(
            "echo '[INFO] Broadcasting situation report to nearby camps' && "
            "echo '[INFO] threat_level={{ ti.xcom_pull(task_ids=\"dawn_patrol_scan\", key=\"threat_level\") }} "
            "supply_count={{ ti.xcom_pull(task_ids=\"ration_supplies\", key=\"supply_count\") }} "
            "headcount={{ ti.xcom_pull(task_ids=\"survivor_headcount\", key=\"headcount\") }}' && "
            "echo '[INFO] Radio check-in complete — signing off until next shift'"
        ),
    )

    dawn_patrol_scan_task >> decide_fight_or_hide_task
    decide_fight_or_hide_task >> [engage_threat_task, fortify_barricade_task]
    [engage_threat_task, fortify_barricade_task, ration_supplies_task] >> survivor_headcount_task
    survivor_headcount_task >> radio_checkin_task
