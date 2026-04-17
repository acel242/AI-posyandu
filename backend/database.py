import aiosqlite
import os
from datetime import date, datetime
from typing import Optional

# Absolute path so backend and bot both write to the same file
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posyandu.db")


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
                telegram_id TEXT UNIQUE NOT NULL,
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
             immunization_status, notes, recorded_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['child_id'], data['date'], data['weight_kg'], data['height_cm'],
            data['bb_tb_status'], int(data.get('vitamin_a', False)),
            data.get('immunization_status', 'complete'), data.get('notes', ''),
            data.get('recorded_by')
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
