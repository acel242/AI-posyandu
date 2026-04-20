"""
scheduler.py — APScheduler job definitions for AI-Posyandu alert system.

Jobs:
  1. check_posyandu_reminders  — send H-1 reminders to warga
  2. check_belum_timbang       — alert parents of children not weighed in 30+ days
  3. check_risiko_tinggi       — alert kader/bidan of high-risk children
"""

import logging
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

import database as db
import bot_notification as bn

logger = logging.getLogger(__name__)

TZ = ZoneInfo("Asia/Shanghai")  # WIB

# Alert repeat intervals
BELUM_TIMBANG_DAYS = 30
BELUM_TIMBANG_REPEAT_DAYS = 7  # re-alert if still not weighed after 7 days

# Alert types
ALERT_POSYANDU = "posyandu_reminder"
ALERT_BELUM_TIMBANG = "belum_timbang"
ALERT_RISIKO = "risiko_tinggi"


# ── Helpers ───────────────────────────────────────────────────────────────────

def today_str() -> str:
    return date.today().isoformat()


def days_between(d1_str: str, d2_str: str) -> int:
    d1 = date.fromisoformat(d1_str)
    d2 = date.fromisoformat(d2_str)
    return (d2 - d1).days


async def age_in_days(dob_str: str) -> int:
    dob = date.fromisoformat(dob_str)
    return (date.today() - dob).days


# ── Job 1: Posyandu Reminder (H-N, configurable) ─────────────────────────────

async def check_posyandu_reminders():
    """
    Send reminders to warga/kader N days before scheduled Posyandu.
    Reads reminder_days_before from each schedule row.
    target_role: 'warga' → parents, 'kader'/'bidan' → kader/bidan.
    Runs daily at 08:00 WIB.
    """
    logger.info("[Scheduler] Running: check_posyandu_reminders")

    today = date.today()
    all_schedules = await db.get_schedules()

    # Filter schedules where reminder_date == today
    todays_reminders = [
        s for s in all_schedules
        if s.get("reminder_days_before", 1) is not None
        and _reminder_is_today(s, today)
    ]

    if not todays_reminders:
        logger.info(f"[Scheduler] No reminders due today ({today}), skipping.")
        return

    # Collect recipients by role
    warga_ids = await db.get_parent_telegram_ids()
    kader_ids = await db.get_kader_telegram_ids(role="kader")
    bidan_ids = await db.get_kader_telegram_ids(role="bidan")

    for schedule in todays_reminders:
        posyandu_name = schedule.get("title", "Posyandu")
        posyandu_location = schedule.get("description", "Lokasi tidak diketahui")
        event_date = schedule["scheduled_date"]
        event_time = schedule.get("scheduled_time", "08:00")
        target_role = schedule.get("target_role", "warga")
        days_before = schedule.get("reminder_days_before", 1)
        schedule_id = schedule.get("id")

        # Determine recipients
        if target_role == "warga":
            recipients = [(tid, "warga") for tid in warga_ids]
        elif target_role == "kader":
            recipients = [(tid, "kader") for tid in kader_ids]
        elif target_role == "bidan":
            recipients = [(tid, "bidan") for tid in bidan_ids]
        else:  # 'all' or unknown
            recipients = [(tid, "warga") for tid in warga_ids] + \
                         [(tid, "kader") for tid in kader_ids] + \
                         [(tid, "bidan") for tid in bidan_ids]

        logger.info(
            f"[Scheduler] Reminder for '{posyandu_name}' (H-{days_before}): "
            f"{len(recipients)} {target_role} recipients"
        )

        for tid, role in recipients:
            # Check duplicate per schedule_id (not child_id, since broadcast)
            is_dup = await db.check_alert_already_sent(
                child_id=schedule_id,   # use schedule_id to dedup broadcast
                alert_type=ALERT_POSYANDU,
                recipient_telegram_id=tid,
                same_day=True,
            )
            if is_dup:
                continue

            alert_id = await db.add_alert_log({
                "child_id": schedule_id,  # schedule as pseudo-child for broadcast
                "alert_type": ALERT_POSYANDU,
                "recipient_telegram_id": tid,
                "message_text": f"Reminder Posyandu {posyandu_name} {days_before} hari lagi",
                "scheduled_time": schedule.get("scheduled_time"),
                "status": "pending",
            })

            ok = await bn.send_posyandu_reminder(
                telegram_id=tid,
                child_name=None,        # broadcast = no specific child
                parent_name=role.title(),
                posyandu_name=posyandu_name,
                location=posyandu_location,
                date=event_date,
                time=event_time,
            )

            if ok:
                await db.mark_alert_sent(alert_id, datetime.now(TZ).isoformat())
            else:
                await db.mark_alert_failed(alert_id, "Telegram send failed")

    logger.info(f"[Scheduler] Finished: check_posyandu_reminders ({len(todays_reminders)} reminders sent)")


def _reminder_is_today(schedule: dict, today: date) -> bool:
    """Return True if today is exactly N days before scheduled_date."""
    try:
        scheduled = date.fromisoformat(schedule["scheduled_date"])
        days_before = schedule.get("reminder_days_before", 1) or 1
        reminder_date = scheduled - timedelta(days=days_before)
        return reminder_date == today
    except (ValueError, TypeError):
        return False


# ── Job 2: Belum Ditimbang (>30 days) ───────────────────────────────────────

async def check_belum_timbang():
    """
    Alert parents whose children haven't been weighed in 30+ days.
    Runs every 6 hours. Repeats every 7 days if still not weighed.
    """
    logger.info("[Scheduler] Running: check_belum_timbang")

    all_children = await db.get_all_children()
    today = date.today()
    alerted_count = 0

    for child in all_children:
        parent_tid = child.get("parent_telegram_id")
        if not parent_tid:
            continue

        last_date = child.get("last_posyandu_date")
        if not last_date:
            continue

        last = date.fromisoformat(last_date)
        days_ago = (today - last).days

        if days_ago <= BELUM_TIMBANG_DAYS:
            continue

        # Check if we already alerted recently (within 7 days)
        is_dup = await db.check_alert_already_sent(
            child_id=child["id"],
            alert_type=ALERT_BELUM_TIMBANG,
            recipient_telegram_id=parent_tid,
            same_day=False,
        )
        if is_dup:
            continue

        child_age = await age_in_days(child["date_of_birth"])

        # Log pending
        alert_id = await db.add_alert_log({
            "child_id": child["id"],
            "alert_type": ALERT_BELUM_TIMBANG,
            "recipient_telegram_id": parent_tid,
            "message_text": f"Anak {child['name']} belum ditimbang",
            "scheduled_time": today.isoformat(),
            "status": "pending",
        })

        # Send
        ok = await bn.send_belum_timbang(
            telegram_id=parent_tid,
            child_name=child["name"],
            parent_name=child["parent_name"],
            last_date=last_date,
            days_ago=days_ago,
            age_days=child_age,
        )

        if ok:
            await db.mark_alert_sent(alert_id, datetime.now(TZ).isoformat())
            alerted_count += 1
        else:
            await db.mark_alert_failed(alert_id, "Telegram send failed")

    logger.info(f"[Scheduler] Finished: check_belum_timbang ({alerted_count} alerts sent)")


# ── Job 3: Anak Risiko Tinggi ─────────────────────────────────────────────────

async def check_risiko_tinggi():
    """
    Alert kader and bidan when children are classified high-risk (yellow/red).
    Triggered when a health record is added — not a scheduled job.
    This function is called manually after add_health_record updates risk_status.
    """
    # This is called directly from the health record flow, not scheduled.
    pass


async def trigger_risiko_tinggi_alert(child_id: int):
    """
    Manually trigger risk alert after a health record is saved.
    Call this from wherever risk_status is updated.
    """
    logger.info(f"[Scheduler] Triggering risk alert for child_id={child_id}")

    child = await db.get_child_by_id(child_id)
    if not child:
        logger.error(f"Child {child_id} not found for risk alert")
        return

    if child["risk_status"] not in ("yellow", "red"):
        return

    risk_level = child["risk_status"]
    risk_label = "risiko" if risk_level == "yellow" else "rujuk"

    # Get latest health record for z-score and notes
    records = await db.get_health_records(child_id)
    latest = records[0] if records else {}
    zscore = latest.get("bb_tb_status", "?")
    notes = latest.get("notes", "")

    # Get kader/bidan Telegram IDs
    kader_ids = await db.get_kader_telegram_ids(role="kader")
    bidan_ids = await db.get_kader_telegram_ids(role="bidan")
    all_recipients = list(set(kader_ids + bidan_ids))

    for tid in all_recipients:
        # Check duplicate
        is_dup = await db.check_alert_already_sent(
            child_id=child_id,
            alert_type=ALERT_RISIKO,
            recipient_telegram_id=tid,
            same_day=False,
        )
        if is_dup:
            continue

        alert_id = await db.add_alert_log({
            "child_id": child_id,
            "alert_type": ALERT_RISIKO,
            "recipient_telegram_id": tid,
            "message_text": f"Alert {risk_label} untuk {child['name']}",
            "scheduled_time": date.today().isoformat(),
            "status": "pending",
        })

        ok = await bn.send_risiko_tinggi(
            telegram_id=tid,
            child_name=child["name"],
            parent_name=child["parent_name"],
            zscore=zscore,
            last_date=child.get("last_posyandu_date", "—"),
            risk_level=risk_level,
            notes=notes,
        )

        if ok:
            await db.mark_alert_sent(alert_id, datetime.now(TZ).isoformat())
        else:
            await db.mark_alert_failed(alert_id, "Telegram send failed")

    logger.info(f"[Scheduler] Risk alert triggered for child_id={child_id}")


# ── Scheduler Setup ───────────────────────────────────────────────────────────

def build_scheduler() -> AsyncIOScheduler:
    """Build and return a configured AsyncIOScheduler."""
    scheduler = AsyncIOScheduler(timezone=str(TZ))

    # Job 1: Posyandu reminder — daily at 08:00 WIB
    scheduler.add_job(
        check_posyandu_reminders,
        trigger="cron",
        hour=8,
        minute=0,
        id="posyandu_reminder",
        name="Posyandu H-1 Reminder",
        replace_existing=True,
    )

    # Job 2: Belum ditimbang — every 6 hours
    scheduler.add_job(
        check_belum_timbang,
        trigger=IntervalTrigger(hours=6),
        id="belum_timbang",
        name="Belum Ditimbang 30+ Days",
        replace_existing=True,
    )

    return scheduler


def start_scheduler(scheduler: AsyncIOScheduler):
    """Start the scheduler. Call this on app startup."""
    scheduler.start()
    logger.info("[Scheduler] Started — jobs: posyandu_reminder (daily 08:00), belum_timbang (every 6h)")
