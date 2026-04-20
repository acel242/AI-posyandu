import aiosqlite
import os
from datetime import date, datetime
from typing import Optional

# Absolute path so backend and bot both write to the same file
# Use /data volume on Railway, local fallback elsewhere
DATA_DIR = os.environ.get("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(DATA_DIR, "posyandu.db")


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS children (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nik TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                gender TEXT NOT NULL,
                parent_name TEXT NOT NULL,
                parent_phone TEXT NOT NULL,
                parent_telegram_id TEXT,
                address TEXT NOT NULL,
                rt_rw TEXT NOT NULL,
                risk_status TEXT DEFAULT 'unmeasured',
                last_posyandu_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS health_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                weight_kg REAL NOT NULL,
                height_cm REAL NOT NULL,
                bb_tb_status TEXT NOT NULL,
                vitamin_a INTEGER DEFAULT 0,
                immunization_status TEXT DEFAULT 'complete',
                notes TEXT,
                recorded_by INTEGER,
                FOREIGN KEY (child_id) REFERENCES children(id)
            )
        """)
        # Migration: add WHO z-score columns to health_records
        for col, coltype in [
            ('z_score_wfa', 'REAL'),
            ('z_score_hfa', 'REAL'),
            ('z_score_wfh', 'REAL'),
            ('age_months', 'REAL'),
            ('overall_status', 'TEXT'),
        ]:
            try:
                await db.execute(f'ALTER TABLE health_records ADD COLUMN {col} {coltype}')
            except Exception:
                pass
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posyandu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                schedule_day INTEGER NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                posyandu_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                scheduled_date TEXT NOT NULL,
                scheduled_time TEXT NOT NULL,
                reminder_days_before INTEGER DEFAULT 1,
                target_role TEXT DEFAULT 'warga',
                created_by_telegram_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (posyandu_id) REFERENCES posyandu(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS kaders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                telegram_id TEXT UNIQUE,
                role TEXT DEFAULT 'kader'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT NOT NULL,
                child_id INTEGER,
                role TEXT DEFAULT 'user',
                message TEXT NOT NULL,
                response TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS error_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id TEXT NOT NULL,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                context TEXT,
                resolution_attempted TEXT,
                resolved BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS agent_lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                trigger_keywords TEXT NOT NULL,
                lesson_text TEXT NOT NULL,
                action TEXT,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                last_tested_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS alert_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER,
                schedule_id INTEGER,
                alert_type TEXT NOT NULL,
                recipient_telegram_id TEXT NOT NULL,
                message_text TEXT,
                scheduled_time TEXT,
                sent_time TEXT,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children(id)
            )
        """)
        await db.commit()


async def add_child(data: dict) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO children (nik, name, date_of_birth, gender, parent_name,
                parent_phone, parent_telegram_id, address, rt_rw)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['nik'], data['name'], data['date_of_birth'], data['gender'],
            data['parent_name'], data['parent_phone'], data.get('parent_telegram_id'),
            data['address'], data['rt_rw']
        ))
        await db.commit()
        return cursor.lastrowid


async def get_child_by_nik(nik: str) -> Optional[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM children WHERE nik = ?", (nik,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_child_by_id(child_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM children WHERE id = ?", (child_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_all_children() -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM children ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def update_child_risk(child_id: int, risk_status: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE children SET risk_status = ? WHERE id = ?",
            (risk_status, child_id)
        )
        await db.commit()


async def add_health_record(data: dict) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO health_records
            (child_id, date, weight_kg, height_cm, bb_tb_status, vitamin_a,
             immunization_status, notes, recorded_by, z_score_wfa, z_score_hfa,
             z_score_wfh, age_months, overall_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['child_id'], data['date'], data['weight_kg'], data['height_cm'],
            data['bb_tb_status'], int(data.get('vitamin_a', False)),
            data.get('immunization_status', 'complete'), data.get('notes', ''),
            data.get('recorded_by'),
            data.get('z_score_wfa'), data.get('z_score_hfa'), data.get('z_score_wfh'),
            data.get('age_months'), data.get('overall_status')
        ))
        await db.commit()
        await db.execute(
            "UPDATE children SET last_posyandu_date = ?, risk_status = ? WHERE id = ?",
            (data['date'], data['bb_tb_status'], data['child_id'])
        )
        await db.commit()
        return cursor.lastrowid


async def get_health_records(child_id: int) -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM health_records WHERE child_id = ? ORDER BY date DESC",
            (child_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_child_measurements(child_id: int) -> list:
    """Get measurements for a child with WHO z-scores and age_months calculated."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        # Get child's DOB and gender
        cur = await db.execute("SELECT date_of_birth, gender FROM children WHERE id = ?", (child_id,))
        child_row = await cur.fetchone()
        if not child_row:
            return []
        dob = child_row['date_of_birth']
        gender = child_row['gender']
        
        cursor = await db.execute(
            "SELECT * FROM health_records WHERE child_id = ? ORDER BY date ASC",
            (child_id,)
        )
        rows = await cursor.fetchall()
        measurements = []
        for row in rows:
            m = dict(row)
            # Calculate age_months from DOB
            from datetime import datetime
            dob_dt = datetime.strptime(dob, '%Y-%m-%d')
            if m.get('date') and m['date'].strip():
                mdate = datetime.strptime(m['date'], '%Y-%m-%d')
                age_months = (mdate - dob_dt).days / 30.436875
                m['age_months'] = round(age_months, 1)
            else:
                m['age_months'] = None
            
            # Import WHO functions inline to avoid circular deps
            from who_anthro import (
                calc_zscore_weight_for_age, calc_zscore_height_for_age,
                calc_zscore_weight_for_height, classify_overall
            )
            w = m.get('weight_kg')
            h = m.get('height_cm')
            am = m.get('age_months')
            m['z_score_wfa'] = calc_zscore_weight_for_age(w, am, gender) if w and am else None
            m['z_score_hfa'] = calc_zscore_height_for_age(h, am, gender) if h and am else None
            m['z_score_wfh'] = calc_zscore_weight_for_height(w, h, gender) if w and h else None
            m['overall_status'] = classify_overall(w, h, am, gender)
            measurements.append(m)
        return measurements


async def save_conversation(telegram_id: str, child_id: Optional[int],
                            role: str, message: str, response: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO conversations (telegram_id, child_id, role, message, response)
            VALUES (?, ?, ?, ?, ?)
        """, (telegram_id, child_id, role, message, response))
        await db.commit()


async def get_conversation_history(telegram_id: str, limit: int = 10) -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM conversations
            WHERE telegram_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (telegram_id, limit))
        rows = await cursor.fetchall()
        return [dict(row) for row in reversed(rows)]


async def get_children_by_risk(risk_status: str) -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM children WHERE risk_status = ? ORDER BY last_posyandu_date",
            (risk_status,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_statistics() -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        total_cur = await db.execute("SELECT COUNT(*) as count FROM children")
        green_cur = await db.execute("SELECT COUNT(*) as count FROM children WHERE risk_status = 'green'")
        yellow_cur = await db.execute("SELECT COUNT(*) as count FROM children WHERE risk_status = 'yellow'")
        red_cur = await db.execute("SELECT COUNT(*) as count FROM children WHERE risk_status = 'red'")

        total_r = await total_cur.fetchone()
        green_r = await green_cur.fetchone()
        yellow_r = await yellow_cur.fetchone()
        red_r = await red_cur.fetchone()
        unmeasured_cur = await db.execute("SELECT COUNT(*) as count FROM children WHERE risk_status = 'unmeasured'")
        unmeasured_r = await unmeasured_cur.fetchone()

        return {
            "total": total_r[0] if total_r else 0,
            "green": green_r[0] if green_r else 0,
            "yellow": yellow_r[0] if yellow_r else 0,
            "red": red_r[0] if red_r else 0,
            "unmeasured": unmeasured_r[0] if unmeasured_r else 0
        }


# ── Error Log & Lesson Memory ─────────────────────────────────────────────────

async def log_error(telegram_id: str, error_type: str, error_message: str,
                    context: str = None, resolution: str = None) -> int:
    """Record a failure so the agent can learn from it."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO error_log
            (telegram_id, error_type, error_message, context, resolution_attempted)
            VALUES (?, ?, ?, ?, ?)
        """, (telegram_id, error_type, error_message, context, resolution))
        await db.commit()
        return cursor.lastrowid


async def mark_error_resolved(error_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE error_log SET resolved = 1 WHERE id = ?", (error_id,)
        )
        await db.commit()


async def get_unresolved_errors(limit: int = 20) -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM error_log
            WHERE resolved = 0
            ORDER BY created_at DESC LIMIT ?
        """, (limit,))
        return [dict(r) for r in await cursor.fetchall()]


async def add_lesson(error_type: str, keywords: str, lesson: str,
                     action: str = None) -> int:
    """Store a learned lesson for future reference."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO agent_lessons
            (error_type, trigger_keywords, lesson_text, action)
            VALUES (?, ?, ?, ?)
        """, (error_type, keywords, lesson, action))
        await db.commit()
        return cursor.lastrowid


async def increment_lesson_success(lesson_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE agent_lessons
            SET success_count = success_count + 1,
                last_tested_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (lesson_id,))
        await db.commit()


async def increment_lesson_failure(lesson_id: int) -> None:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE agent_lessons
            SET failure_count = failure_count + 1,
                last_tested_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (lesson_id,))
        await db.commit()


async def get_lessons_by_keywords(keywords: str) -> list:
    """Find lessons whose trigger keywords match the given text."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM agent_lessons
            WHERE trigger_keywords LIKE ?
            ORDER BY success_count DESC, failure_count ASC
            LIMIT 5
        """, (f"%{keywords}%",))
        return [dict(r) for r in await cursor.fetchall()]


async def get_all_lessons() -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM agent_lessons
            ORDER BY success_count DESC, failure_count ASC
        """)
        return [dict(r) for r in await cursor.fetchall()]


async def get_lesson_stats() -> dict:
    """Summary of lessons and error patterns."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        r1 = await db.execute("SELECT COUNT(*) as c FROM agent_lessons").__aenter__()
        total_lessons = (await (await db.execute("SELECT COUNT(*) as c FROM agent_lessons")).fetchone())[0]
        total_errors = (await (await db.execute("SELECT COUNT(*) as c FROM error_log WHERE resolved=0")).fetchone())[0]
        high_success = (await (await db.execute("SELECT COUNT(*) as c FROM agent_lessons WHERE success_count > failure_count")).fetchone())[0]
        return {
            "total_lessons": total_lessons,
            "unresolved_errors": total_errors,
            "lessons_working": high_success
        }


# ── Schedules ─────────────────────────────────────────────────────────────────

async def add_schedule(data: dict) -> int:
    """Create a new schedule/reminder entry. Returns schedule id."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO schedules
            (posyandu_id, title, description, scheduled_date, scheduled_time,
             reminder_days_before, target_role, created_by_telegram_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("posyandu_id"),
            data["title"],
            data.get("description", ""),
            data["scheduled_date"],
            data["scheduled_time"],
            data.get("reminder_days_before", 1),
            data.get("target_role", "warga"),
            data.get("created_by_telegram_id"),
        ))
        await db.commit()
        return cursor.lastrowid


async def get_schedules(posyandu_id: int = None, target_role: str = None,
                        from_date: str = None) -> list:
    """List schedules, optionally filtered."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM schedules WHERE 1=1"
        params = []
        if posyandu_id:
            query += " AND posyandu_id = ?"
            params.append(posyandu_id)
        if target_role:
            query += " AND target_role = ?"
            params.append(target_role)
        if from_date:
            query += " AND scheduled_date >= ?"
            params.append(from_date)
        query += " ORDER BY scheduled_date ASC, scheduled_time ASC"
        cursor = await db.execute(query, params)
        return [dict(r) for r in await cursor.fetchall()]


async def get_schedule(id: int) -> Optional[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM schedules WHERE id = ?", (id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def delete_schedule(id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("DELETE FROM schedules WHERE id = ?", (id,))
        await db.commit()
        return cursor.rowcount > 0


async def get_all_posyandus() -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM posyandu ORDER BY name ASC")
        return [dict(r) for r in await cursor.fetchall()]


async def get_posyandu(id: int) -> Optional[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM posyandu WHERE id = ?", (id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_posyandu(data: dict) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO posyandu (name, location, schedule_day)
            VALUES (?, ?, ?)
        """, (data["name"], data["location"], data["schedule_day"]))
        await db.commit()
        return cursor.lastrowid


# ── Kader / Bidan ─────────────────────────────────────────────────────────────

async def add_kader(data: dict) -> int:
    """Register a new kader or bidan. Returns kader id."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO kaders (name, telegram_id, role)
            VALUES (?, ?, ?)
        """, (
            data["name"],
            data.get("telegram_id"),
            data.get("role", "kader"),
        ))
        await db.commit()
        return cursor.lastrowid


async def get_all_kaders() -> list:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM kaders ORDER BY role, name ASC")
        return [dict(r) for r in await cursor.fetchall()]


async def get_kader_by_id(kader_id: int) -> Optional[dict]:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM kaders WHERE id = ?", (kader_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_kader_by_name(name: str) -> Optional[dict]:
    """Find a kader by name (for /setrole verification). Case-insensitive partial match."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM kaders WHERE LOWER(name) = LOWER(?)",
            (name,),
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def link_kader_telegram(kader_id: int, telegram_id: str) -> bool:
    """Link a Telegram ID to an existing kader. Returns True if updated."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "UPDATE kaders SET telegram_id = ? WHERE id = ?",
            (telegram_id, kader_id),
        )
        await db.commit()
        return cursor.rowcount > 0


async def unlink_kader_telegram(kader_id: int) -> bool:
    """Unlink a Telegram ID from a kader (set to NULL)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "UPDATE kaders SET telegram_id = NULL WHERE id = ?",
            (kader_id,),
        )
        await db.commit()
        return cursor.rowcount > 0


async def delete_kader(kader_id: int) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("DELETE FROM kaders WHERE id = ?", (kader_id,))
        await db.commit()
        return cursor.rowcount > 0


# ── Alert Log ─────────────────────────────────────────────────────────────────

async def add_alert_log(data: dict) -> int:
    """Insert a new alert into the log. Returns the new alert id."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO alert_log
            (child_id, schedule_id, alert_type, recipient_telegram_id, message_text,
             scheduled_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("child_id"),
            data.get("schedule_id"),
            data["alert_type"],
            data["recipient_telegram_id"],
            data.get("message_text", ""),
            data.get("scheduled_time"),
            data.get("status", "pending"),
        ))
        await db.commit()
        return cursor.lastrowid


async def get_alert_logs(
    child_id: int = None,
    alert_type: str = None,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
) -> list:
    """Fetch alert log entries with optional filters."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM alert_log WHERE 1=1"
        params = []
        if child_id is not None:
            query += " AND child_id = ?"
            params.append(child_id)
        if alert_type:
            query += " AND alert_type = ?"
            params.append(alert_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cursor = await db.execute(query, params)
        return [dict(r) for r in await cursor.fetchall()]


async def get_pending_alerts(limit: int = 100) -> list:
    """Get all pending alerts that haven't been sent yet."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM alert_log WHERE status = 'pending' ORDER BY created_at ASC LIMIT ?",
            (limit,),
        )
        return [dict(r) for r in await cursor.fetchall()]


async def mark_alert_sent(alert_id: int, sent_time: str = None) -> None:
    """Mark an alert as successfully sent."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE alert_log SET status = 'sent', sent_time = ? WHERE id = ?",
            (sent_time, alert_id),
        )
        await db.commit()


async def mark_alert_failed(alert_id: int, error_message: str) -> None:
    """Mark an alert as failed with an error message."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE alert_log SET status = 'failed', error_message = ? WHERE id = ?",
            (error_message, alert_id),
        )
        await db.commit()


async def check_alert_already_sent(
    child_id: int = None,
    schedule_id: int = None,
    alert_type: str = None,
    recipient_telegram_id: str = None,
    same_day: bool = True,
) -> bool:
    """Check if an alert of the same type was already sent to this recipient today.
    For broadcast alerts use schedule_id; for child alerts use child_id.
    Returns True if a duplicate alert exists."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Build WHERE clause
        if schedule_id is not None:
            id_clause = "schedule_id = ?"
            id_val = schedule_id
        else:
            id_clause = "child_id = ?"
            id_val = child_id

        if same_day:
            cursor = await db.execute(
                f"""SELECT id FROM alert_log
                WHERE {id_clause} AND alert_type = ? AND recipient_telegram_id = ?
                AND status = 'sent'
                AND date(sent_time) = date('now')
                LIMIT 1""",
                (id_val, alert_type, recipient_telegram_id),
            )
        else:
            cursor = await db.execute(
                f"""SELECT id FROM alert_log
                WHERE {id_clause} AND alert_type = ? AND recipient_telegram_id = ?
                AND status = 'sent'
                LIMIT 1""",
                (id_val, alert_type, recipient_telegram_id),
            )
        row = await cursor.fetchone()
        return row is not None


async def get_alert_stats() -> dict:
    """Return counts of sent, failed, and pending alerts."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        total = (await (await db.execute("SELECT COUNT(*) as c FROM alert_log")).fetchone())[0]
        sent = (await (await db.execute("SELECT COUNT(*) as c FROM alert_log WHERE status='sent'")).fetchone())[0]
        failed = (await (await db.execute("SELECT COUNT(*) as c FROM alert_log WHERE status='failed'")).fetchone())[0]
        pending = (await (await db.execute("SELECT COUNT(*) as c FROM alert_log WHERE status='pending'")).fetchone())[0]
        return {"total": total, "sent": sent, "failed": failed, "pending": pending}


async def retry_alert(alert_id: int) -> bool:
    """Reset a failed alert back to pending for retry."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "UPDATE alert_log SET status = 'pending', error_message = NULL WHERE id = ? AND status = 'failed'",
            (alert_id,),
        )
        await db.commit()
        return cursor.rowcount > 0


# ── Telegram ID helpers ───────────────────────────────────────────────────────

async def get_parent_telegram_ids() -> list:
    """Get all parent telegram IDs from children table."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT DISTINCT parent_telegram_id FROM children WHERE parent_telegram_id IS NOT NULL"
        )
        rows = await cursor.fetchall()
        return [r["parent_telegram_id"] for r in rows if r["parent_telegram_id"]]


async def get_kader_telegram_ids(role: str = None) -> list:
    """Get telegram_ids for all kader/bidan. Optionally filter by role."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        if role:
            cursor = await db.execute(
                "SELECT telegram_id FROM kaders WHERE telegram_id IS NOT NULL AND role = ?",
                (role,),
            )
        else:
            cursor = await db.execute(
                "SELECT telegram_id FROM kaders WHERE telegram_id IS NOT NULL"
            )
        rows = await cursor.fetchall()
        return [r["telegram_id"] for r in rows if r["telegram_id"]]


async def update_kader_telegram_id(kader_id: int, telegram_id: str) -> None:
    """Update a kader's Telegram ID (for notification targeting)."""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE kaders SET telegram_id = ? WHERE id = ?",
            (telegram_id, kader_id),
        )
        await db.commit()
