"""
handlers.py — Registration state machine for Posyandu AI Telegram bot.

Flow: nama_anak → tanggal_lahir → jenis_kelamin → nik → alamat → nama_ortu → telepon
"""

import re
import sys
import os
from datetime import datetime
from typing import Optional

# Ensure backend is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from telegram import Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    CommandHandler,
    filters,
)

# ---------------------------------------------------------------------------
# State constants
# ---------------------------------------------------------------------------
(
    STATE_NAMA_ANAK,
    STATE_TANGGAL_LAHIR,
    STATE_JENIS_KELAMIN,
    STATE_NIK,
    STATE_ALAMAT,
    STATE_NAMA_ORTU,
    STATE_TELEPON,
) = range(7)

# Conversation timeout (seconds)
REGISTRATION_TIMEOUT = 600

# ---------------------------------------------------------------------------
# User data shape
# ---------------------------------------------------------------------------


def new_registration(telegram_id: int) -> dict:
    return {
        "telegram_id": str(telegram_id),
        "name": None,
        "date_of_birth": None,
        "gender": None,
        "nik": None,
        "address": None,
        "rt_rw": None,
        "parent_name": None,
        "parent_phone": None,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

GENDER_LABELS = {"L": "Laki-laki", "P": "Perempuan"}


def format_registration_summary(data: dict) -> str:
    return (
        "✅ *Pendaftaran Selesai!*\n\n"
        f"📛 Nama Anak  : {data['name']}\n"
        f"📅 Lahir      : {data['date_of_birth']}\n"
        f"⚧ Jenis Kel. : {GENDER_LABELS.get(data['gender'], data['gender'])}\n"
        f"🪪 NIK        : {data['nik']}\n"
        f"🏠 Alamat     : {data['address']}\n"
        f"👤 Nama Ortu. : {data['parent_name']}\n"
        f"📞 Telepon    : {data['parent_phone']}\n\n"
        "Silakan datang ke Posyandu terdekat untuk pemeriksaan rutin. "
        "Terima kasih! 🙏"
    )


async def cancel_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data.pop("registration", None)
    await update.message.reply_text(
        "❌ Pendaftaran dibatalkan.\n"
        "Ketik /daftar untuk mulai lagi kapan saja."
    )
    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def cmd_daftar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the registration conversation."""
    user_id = update.effective_user.id
    context.user_data["registration"] = new_registration(user_id)

    welcome = (
        "🏥 *Selamat Datang di Posyandu AI!*\n\n"
        "Kami akan membantu mendaftarkan anak Anda.\n"
        "Silakan jawab beberapa pertanyaan berikut:\n\n"
        "📛 *Pertanyaan 1 dari 7*\n"
        "Siapa nama lengkap anak Anda?"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")
    return STATE_NAMA_ANAK


# ---------------------------------------------------------------------------
# Step 1 — Nama Anak
# ---------------------------------------------------------------------------


async def receive_nama_anak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if len(text) < 2:
        await update.message.reply_text(
            "⚠️ Nama terlalu pendek. Silakan masukkan nama lengkap anak Anda."
        )
        return STATE_NAMA_ANAK

    context.user_data["registration"]["name"] = text
    await update.message.reply_text(
        "📅 *Pertanyaan 2 dari 7*\n"
        "Tanggal lahir anak Anda? (format: `YYYY-MM-DD`, contoh: 2019-03-15)",
        parse_mode="Markdown",
    )
    return STATE_TANGGAL_LAHIR


# ---------------------------------------------------------------------------
# Step 2 — Tanggal Lahir
# ---------------------------------------------------------------------------


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


async def receive_tanggal_lahir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not DATE_RE.match(text):
        await update.message.reply_text(
            "⚠️ Format salah. Gunakan format `YYYY-MM-DD` (contoh: 2019-03-15).",
            parse_mode="Markdown",
        )
        return STATE_TANGGAL_LAHIR

    try:
        dob = datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text(
            "⚠️ Tanggal tidak valid. Masukkan tanggal lahir yang benar."
        )
        return STATE_TANGGAL_LAHIR

    if dob > datetime.now().date():
        await update.message.reply_text(
            "⚠️ Tanggal lahir tidak boleh di masa depan."
        )
        return STATE_TANGGAL_LAHIR

    context.user_data["registration"]["date_of_birth"] = text
    await update.message.reply_text(
        "⚧ *Pertanyaan 3 dari 7*\n" "Jenis kelamin anak Anda?\n" "L = Laki-laki\n" "P = Perempuan",
        parse_mode="Markdown",
    )
    return STATE_JENIS_KELAMIN


# ---------------------------------------------------------------------------
# Step 3 — Jenis Kelamin
# ---------------------------------------------------------------------------


async def receive_jenis_kelamin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    if text not in ("L", "P"):
        await update.message.reply_text(
            "⚠️ Pilihan tidak valid. Balas dengan `L` (Laki-laki) atau `P` (Perempuan).",
            parse_mode="Markdown",
        )
        return STATE_JENIS_KELAMIN

    context.user_data["registration"]["gender"] = text
    await update.message.reply_text(
        "🪪 *Pertanyaan 4 dari 7*\n" "Masukkan NIK (Nomor Induk Kependudukan) anak Anda.\n"
        "NIK terdiri dari 16 digit angka.",
        parse_mode="Markdown",
    )
    return STATE_NIK


# ---------------------------------------------------------------------------
# Step 4 — NIK
# ---------------------------------------------------------------------------


NIK_RE = re.compile(r"^\d{16}$")


async def receive_nik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not NIK_RE.match(text):
        await update.message.reply_text(
            "⚠️ NIK harus 16 digit angka. Silakan ulangi."
        )
        return STATE_NIK

    context.user_data["registration"]["nik"] = text
    await update.message.reply_text(
        "🏠 *Pertanyaan 5 dari 7*\n"
        "Masukkan alamat lengkap (termasuk RT/RW, desa, kecamatan).\n"
        "Contoh: `Dusun Desa Patakbanteng RT 003 RW 001, Kec. Susut, Bangli`",
        parse_mode="Markdown",
    )
    return STATE_ALAMAT


# ---------------------------------------------------------------------------
# Step 5 — Alamat
# ---------------------------------------------------------------------------


async def receive_alamat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if len(text) < 10:
        await update.message.reply_text(
            "⚠️ Alamat terlalu pendek. Silakan masukkan alamat yang lebih lengkap."
        )
        return STATE_ALAMAT

    # Split off RT/RW suffix if provided in separate format
    context.user_data["registration"]["address"] = text
    await update.message.reply_text(
        "👤 *Pertanyaan 6 dari 7*\n" "Siapa nama lengkap orang tua/wali?\n"
        "(Ibu atau Ayah yang bertanggung jawab)",
        parse_mode="Markdown",
    )
    return STATE_NAMA_ORTU


# ---------------------------------------------------------------------------
# Step 6 — Nama Orang Tua
# ---------------------------------------------------------------------------


async def receive_nama_ortu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if len(text) < 2:
        await update.message.reply_text(
            "⚠️ Nama terlalu pendek. Silakan masukkan nama lengkap orang tua/wali."
        )
        return STATE_NAMA_ORTU

    context.user_data["registration"]["parent_name"] = text
    await update.message.reply_text(
        "📞 *Pertanyaan 7 dari 7*\n"
        "Masukkan nomor telepon/WhatsApp yang aktif (dimulai dengan +62 atau 08).\n"
        "Contoh: `+6281234567890` atau `081234567890`",
        parse_mode="Markdown",
    )
    return STATE_TELEPON


# ---------------------------------------------------------------------------
# Step 7 — Telepon → Save
# ---------------------------------------------------------------------------


PHONE_RE = re.compile(r"^(\+?62|0)\d{8,14}$")


async def receive_telepon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().replace(" ", "")

    if not PHONE_RE.match(text):
        await update.message.reply_text(
            "⚠️ Nomor telepon tidak valid.\n"
            "Gunakan format: `+6281234567890` atau `081234567890`"
        )
        return STATE_TELEPON

    reg = context.user_data.pop("registration")
    reg["parent_phone"] = text

    # Try to save to database
    import database as db
    await db.init_db()

    saved = False
    error_msg = None
    try:
        child_id = await db.add_child(reg)
        saved = True
    except Exception as e:
        error_msg = str(e)
        saved = False

    if saved:
        await update.message.reply_text(
            format_registration_summary(reg),
            parse_mode="Markdown",
        )
        # Immediate sync attempt for any other pending records
        from sync import sync_all
        await sync_all()
    else:
        # Save to local pending queue for later retry
        from sync import add_pending
        add_pending(str(update.effective_user.id), reg)
        await update.message.reply_text(
            format_registration_summary(reg),
            parse_mode="Markdown",
        )
        await update.message.reply_text(
            "⚠️ Gagal menyimpan ke server karena masalah jaringan. "
            "Data Anda sudah tersimpan secara lokal dan akan dikirim "
            "otomatis saat koneksi pulih.不用担心! 🙏\n\n"
            "Ketik /sync untuk mencoba mengirim ulang sekarang."
        )

    return ConversationHandler.END


# ---------------------------------------------------------------------------
# Fallback handler — unexpected message during registration
# ---------------------------------------------------------------------------


async def unexpected_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Saya tidak mengerti pesan tersebut.\n"
        "Ketik /batal untuk membatalkan pendaftaran,\n"
        "atau lanjutkan menjawab pertanyaan yang asked."
    )
    # Return current state to stay in conversation
    return -1  # -1 keeps the conversation going without changing state


# ---------------------------------------------------------------------------
# Conversation handler factory
# ---------------------------------------------------------------------------


def build_registration_conv_handler() -> ConversationHandler:
    """Return a fully wired ConversationHandler for /daftar."""

    # We use a MessageHandler with the state as first positional arg.
    # python-telegram-bot v21 uses the `states` dict style.
    conv = ConversationHandler(
        entry_points=[CommandHandler("daftar", cmd_daftar)],
        states={
            STATE_NAMA_ANAK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_nama_anak)
            ],
            STATE_TANGGAL_LAHIR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_tanggal_lahir)
            ],
            STATE_JENIS_KELAMIN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_jenis_kelamin)
            ],
            STATE_NIK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_nik)
            ],
            STATE_ALAMAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_alamat)
            ],
            STATE_NAMA_ORTU: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_nama_ortu)
            ],
            STATE_TELEPON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_telepon)
            ],
        },
        fallbacks=[
            CommandHandler("batal", cancel_registration),
            CommandHandler("cancel", cancel_registration),
        ],
        conversation_timeout=REGISTRATION_TIMEOUT,
    )
    return conv
