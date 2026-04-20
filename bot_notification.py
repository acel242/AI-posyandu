"""
bot_notification.py — Telegram notification sender for AI-Posyandu alerts.

Uses python-telegram-bot to send notification messages to warga, kader, and bidan.
"""

import os
from dotenv import load_dotenv

# Load Telegram bot token from bot/.env (relative to backend/)
_env_path = os.path.join(os.path.dirname(__file__), "..", "bot", ".env")
load_dotenv(_env_path)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

import os
import logging
from datetime import datetime
from typing import Optional

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
# Bot token from environment — lazily initialized
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def _get_bot():
    """Lazily create and return a Bot instance."""
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")
    return telegram.Bot(token=BOT_TOKEN)

logger = logging.getLogger(__name__)

# Rate limit delay (seconds) between batch sends
BATCH_DELAY_SECONDS = 0.1


# ── Alert Templates ────────────────────────────────────────────────────────────

TEMPLATES = {
    "posyandu_reminder": (
        "🔔 *Reminder Posyandu*\n\n"
        "Besok, {date} pukul {time}, akan diadakan Posyandu *{posyandu_name}* "
        "di {location}.\n\n"
        "Silakan datang untuk menimbangkan dan mengukur tinggi anak Anda. "
        "Jangan lupa bawa KMS! 📋"
    ),
    "belum_timbang": (
        "⚠️ *Anak Belum Ditimbang*\n\n"
        "Halo {parent_name}! Anak Anda *{child_name}* ({age_days} hari) "
        "belum ditimbang sejak *{last_date}*.\n\n"
        "Terakhir ditimbang: {last_date} ({days_ago} hari lalu)\n"
        "Silakan kunjungi Posyandu terdekat untuk pemeriksaan rutin. 🙏"
    ),
    "risiko_tinggi_yellow": (
        "🟡 *Alert Risiko — {child_name}*\n\n"
        "Anak *{child_name}* (orang tua: {parent_name}) "
        "masuk kategori *risiko* (Z-score: {zscore}).\n\n"
        "📅 Pengukuran terakhir: {last_date}\n"
        "📍 Kunjungan rumah dalam 7 hari disarankan.\n\n"
        "Keterangan: {notes}"
    ),
    "risiko_tinggi_red": (
        "🔴 *Alert Rujuk — {child_name}*\n\n"
        "🚨 Anak *{child_name}* (orang tua: {parent_name}) "
        "masuk kategori *buruk* (Z-score: {zscore}).\n\n"
        "📅 Pengukuran terakhir: {last_date}\n"
        "⚠️ *Segera rujuk ke Puskesmas.*\n\n"
        "Keterangan: {notes}"
    ),
}


# ── Core Send Function ─────────────────────────────────────────────────────────

async def send_telegram_message(
    telegram_id: str,
    text: str,
    parse_mode: str = "Markdown",
    keyboard: Optional[InlineKeyboardMarkup] = None,
) -> bool:
    """
    Send a Telegram message to the given telegram_id.
    Returns True on success, False on failure.
    """
    if not telegram_id:
        logger.warning("Cannot send message: telegram_id is empty")
        return False

    try:
        bot = _get_bot()
        await bot.send_message(
            chat_id=int(telegram_id),
            text=text,
            parse_mode=parse_mode,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
        logger.info(f"Message sent to {telegram_id}: {text[:80]}")
        return True
    except telegram.error.TelegramError as e:
        logger.error(f"Failed to send message to {telegram_id}: {e}")
        return False


# ── Alert Senders ─────────────────────────────────────────────────────────────

async def send_posyandu_reminder(
    telegram_id: str,
    child_name: str,
    parent_name: str,
    posyandu_name: str,
    location: str,
    date: str,
    time: str,
) -> bool:
    """Send H-1 Posyandu reminder to a parent."""
    text = TEMPLATES["posyandu_reminder"].format(
        date=date,
        time=time,
        posyandu_name=posyandu_name,
        location=location,
    )
    return await send_telegram_message(telegram_id, text)


async def send_belum_timbang(
    telegram_id: str,
    child_name: str,
    parent_name: str,
    last_date: str,
    days_ago: int,
    age_days: int,
) -> bool:
    """Send 'child not weighed in 30+ days' alert to parent."""
    text = TEMPLATES["belum_timbang"].format(
        parent_name=parent_name,
        child_name=child_name,
        age_days=age_days,
        last_date=last_date,
        days_ago=days_ago,
    )
    return await send_telegram_message(telegram_id, text)


async def send_risiko_tinggi(
    telegram_id: str,
    child_name: str,
    parent_name: str,
    zscore: str,
    last_date: str,
    risk_level: str,  # 'yellow' or 'red'
    notes: str = "",
) -> bool:
    """Send high-risk child alert to kader/bidan."""
    if risk_level == "red":
        template_key = "risiko_tinggi_red"
    else:
        template_key = "risiko_tinggi_yellow"

    text = TEMPLATES[template_key].format(
        child_name=child_name,
        parent_name=parent_name,
        zscore=zscore,
        last_date=last_date,
        notes=notes or "—",
    )

    # Add action button
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("👁 Lihat Detail", callback_data=f"child:{child_name}"),
        InlineKeyboardButton(
            "✅ Tandai Ditangani", callback_data=f"handled:{child_name}"
        ),
    ]])

    return await send_telegram_message(telegram_id, text, keyboard=keyboard)


async def send_batch(
    telegram_ids: list[str],
    message_factory,  # callable that returns message text
    delay: float = BATCH_DELAY_SECONDS,
) -> tuple[int, int]:
    """
    Send the same message to multiple recipients.
    message_factory: callable(telegram_id) -> str  (generates per-recipient text)
    Returns (success_count, failure_count).
    """
    import asyncio

    success = 0
    failed = 0

    for tid in telegram_ids:
        try:
            text = message_factory(tid)
            ok = await send_telegram_message(tid, text)
            if ok:
                success += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"Batch send failed for {tid}: {e}")
            failed += 1

        await asyncio.sleep(delay)

    return success, failed
