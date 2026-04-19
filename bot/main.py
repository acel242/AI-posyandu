"""
main.py — Posyandu AI Telegram Bot entry point.

Usage:
    python -m AI-posyandu.bot.main

Or from project root:
    PYTHONPATH=. python AI-posyandu/bot/main.py
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

# ---------------------------------------------------------------------------
# Path setup — make backend importable
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # workspace/
BOT_DIR = Path(__file__).resolve().parent  # AI-posyandu/bot/

sys.path.insert(0, str(PROJECT_ROOT / "AI-posyandu" / "backend"))

# ---------------------------------------------------------------------------
# Load .env from bot directory
# ---------------------------------------------------------------------------
load_dotenv(BOT_DIR / ".env")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip().isdigit()]
API_BASE = os.getenv("API_BASE", "http://localhost:5001")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("posyandu.bot")


# ---------------------------------------------------------------------------
# Basic command handlers
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: CallbackContext):
    welcome = (
        "🏥 *Posyandu AI — Patakbanteng*\n\n"
        "Selamat datang! Saya adalah asisten Posyandu AI yang akan "
        "membantu Anda dalam:\n\n"
        "👶 Mendaftarkan anak Anda\n"
        "📋 Mengecek status kesehatan anak\n"
        "📅 Mengetahui jadwal Posyandu\n"
        "⚠️ Mendapatkan informasi stunting\n\n"
        "*Commands:*\n"
        "/daftar — Daftarkan anak baru\n"
        "/bantuan — Tampilkan semua perintah\n"
        "/stats — Statistik Posyandu (admin)\n\n"
        "Silakan ketik /daftar untuk memulai! 🙏"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")


async def cmd_bantuan(update: Update, context: CallbackContext):
    text = (
        "📖 *Daftar Perintah*\n\n"
        "/start — Memulai bot\n"
        "/daftar — Mendaftarkan anak baru\n"
        "/bantuan — Menampilkan bantuan\n"
        "/batal — Membatalkan pendaftaran\n"
        "/stats — Statistik (admin only)\n\n"
        "💬 Anda juga bisa bertanya tentang:\n"
        "- Jadwal Posyandu\n"
        "- Tips nutricióni anak\n"
        "- Tanda-tanda stunting\n"
        "- Pertanyaan kesehatan anak"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_stats(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if ADMIN_IDS and user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ Anda tidak memiliki akses ke perintah ini.")
        return

    try:
        import database as db
        await db.init_db()
        stats = await db.get_statistics()
        text = (
            "📊 *Statistik Posyandu*\n\n"
            f"👶 Total Anak : {stats['total']}\n"
            f"🟢 Sehat       : {stats['green']}\n"
            f"🟡 Waspada     : {stats['yellow']}\n"
            f"🔴 Risiko Tinggi: {stats['red']}"
        )
    except Exception as e:
        log.error("Failed to fetch stats: %s", e)
        text = "⚠️ Gagal mengambil statistik. Coba lagi nanti."

    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_batal(update: Update, context: CallbackContext):
    reg = context.user_data.pop("registration", None)
    if reg:
        await update.message.reply_text("✅ Pendaftaran telah dibatalkan.")
    else:
        await update.message.reply_text(
            "Tidak ada pendaftaran yang sedang berjalan.\n"
            "Ketik /daftar untuk memulai."
        )


async def cmd_setrole(update: Update, context: CallbackContext):
    """Forward to handlers.cmd_setrole — imported here to avoid circular imports."""
    from handlers import cmd_setrole as setrole_handler
    await setrole_handler(update, context)
    from sync import sync_all
    await update.message.reply_text("🔄 Menyinkronkan data...")
    result = await sync_all()
    await update.message.reply_text(result, parse_mode="Markdown")


async def echo_handler(update: Update, context: CallbackContext):
    """Route free-text to Aidi agent — the AI that understands Indonesian."""
    user_text = update.message.text.strip()
    if not user_text:
        return
    # Skip empty / accidental messages
    user_id = str(update.effective_user.id)
    try:
        import requests
        resp = requests.post(
            f"{API_BASE}/api/agent/chat",
            json={"telegram_id": user_id, "message": user_text},
            timeout=25,
        )
        if resp.status_code == 200:
            data = resp.json()
            reply = data.get("response", "").strip()
            if reply:
                await update.message.reply_text(reply[:4096])
                return
        # Fallback if API is down
        await update.message.reply_text(
            "Ayo istirahat dulu sebentar, ya! "
            "Nanti coba lagi ya!"
        )
    except Exception as e:
        log.error("Aidi agent error: %s", e)
        await update.message.reply_text(
            "Ayo istirahat dulu sebentar, ya! "
            "Silakan coba lagi nanti."
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not TOKEN or TOKEN == "YOUR_BOT_TOKEN_HERE":
        log.error("TELEGRAM_BOT_TOKEN is not set in bot/.env")
        log.error("Get a token from @BotFather and add it to AI-posyandu/bot/.env")
        sys.exit(1)

    # Build application
    app = Application.builder().token(TOKEN).build()

    # Import handlers here so the bot module doesn't crash on bad imports
    # before the ConversationHandler is wired in
    from handlers import build_registration_conv_handler

    registration_conv = build_registration_conv_handler()

    # Register handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("bantuan", cmd_bantuan))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("batal", cmd_batal))
    app.add_handler(CommandHandler("setrole", cmd_setrole))
    app.add_handler(registration_conv)

    # Fallback — must be added LAST so it doesn't intercept handled messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))

    # Startup sync — runs once when the bot connects
    async def on_bot_startup(app: Application):
        import sync as sync_mod
        await sync_mod.on_startup()

    app.post_init = on_bot_startup

    log.info("Posyandu AI Bot starting...")
    log.info("API_BASE: %s", API_BASE)
    log.info("Admin IDs: %s", ADMIN_IDS or "none")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
