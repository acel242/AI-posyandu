"""
sync.py — Local pending-registration queue with automatic API sync.

When a registration fails to save to the backend (network error, server down, etc.),
the data is written to a local JSON queue (pending_registrations.json).

Sync happens:
  1. Automatically at bot startup — all pending records are retried
  2. On /sync command — user can manually trigger a retry
  3. After every registration attempt — immediate retry on next step

Pending records are removed from the queue only when the API confirms success.
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

PENDING_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "pending_registrations.json"
)


def _load_pending() -> dict:
    """Load pending queue from disk. Returns {telegram_id: [reg1, reg2, ...]}."""
    if not os.path.exists(PENDING_FILE):
        return {}
    try:
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_pending(queue: dict) -> None:
    """Atomically write pending queue to disk."""
    tmp = PENDING_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(queue, f, indent=2)
    os.replace(tmp, PENDING_FILE)


def add_pending(telegram_id: str, reg_data: dict) -> None:
    """Add a registration record to the pending queue."""
    queue = _load_pending()
    queue[telegram_id] = queue.get(telegram_id, [])
    queue[telegram_id].append({**reg_data, "pending_since": datetime.now().isoformat()})
    _save_pending(queue)
    logger.info(f"[Sync] Pending registration added for {telegram_id}. Queue size: {len(queue)}")


async def _try_push(reg_data: dict) -> bool:
    """Try to POST a registration to the backend API. Returns True on success."""
    import database as db

    # Ensure required fields have defaults to satisfy NOT NULL constraints
    reg_data = {
        **reg_data,
        "rt_rw": reg_data.get("rt_rw") or "-",
        # Fix field name mismatch: bot saves telegram_id, db expects parent_telegram_id
        "parent_telegram_id": reg_data.get("parent_telegram_id") or reg_data.get("telegram_id"),
    }

    try:
        child_id = await db.add_child(reg_data)
        logger.info(f"[Sync] Successfully synced: {reg_data.get('name')} (ID: {child_id})")
        return True
    except Exception as e:
        err = str(e).lower()
        # Duplicate NIK = already registered, treat as success
        if "unique" in err or "duplicate" in err or "constraint" in err:
            logger.info(f"[Sync] Child already registered (NIK exists): {reg_data.get('name')}")
            return True
        logger.warning(f"[Sync] Sync failed: {e}")
        return False


async def _push_all() -> tuple[int, int]:
    """
    Attempt to push ALL pending registrations to the backend.
    Returns (succeeded_count, failed_count).
    """
    queue = _load_pending()
    if not queue:
        return 0, 0

    succeeded = 0
    failed = 0
    still_pending = {}

    for telegram_id, regs in list(queue.items()):
        still_pending[telegram_id] = []
        for reg in regs:
            ok = await _try_push(reg)
            if ok:
                succeeded += 1
            else:
                still_pending[telegram_id].append(reg)
                failed += 1

        if not still_pending[telegram_id]:
            del still_pending[telegram_id]

    _save_pending(still_pending)
    return succeeded, failed


async def sync_all(bot_context: ContextTypes.DEFAULT_TYPE = None) -> str:
    """Run full sync and return a human-readable status message."""
    if not os.path.exists(PENDING_FILE):
        return "✅ Tidak ada data yang tertunda."

    succeeded, failed = await _push_all()
    if succeeded == 0 and failed == 0:
        return "✅ Tidak ada data yang tertunda."
    msg = f"🔄 *Sinkronisasi Selesai*\n\n"
    msg += f"✅ Berhasil: {succeeded}\n"
    msg += f"❌ Gagal: {failed}"
    if failed > 0:
        msg += "\n\nData yang gagal akan dicoba lagi otomatis."
    return msg


async def cmd_sync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /sync — manually trigger sync of pending registrations."""
    msg = await sync_all(context)
    await update.message.reply_text(msg, parse_mode="Markdown")


async def on_startup(bot_context: ContextTypes.DEFAULT_TYPE = None) -> str:
    """Called by main.py on bot startup. Returns status message for log."""
    succeeded, failed = await _push_all()
    msg = f"[Sync] Startup sync done — {succeeded} synced, {failed} failed"
    logger.info(msg)
    return msg
