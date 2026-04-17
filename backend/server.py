import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from contextlib import asynccontextmanager
import database as db
import classifier as clf
import agent as ag
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    yield

app = FastAPI(title="Patyandu AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health / Info ────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Patyandu AI API"}


# ─── Statistics ───────────────────────────────────────────────────

@app.get("/api/stats")
async def stats():
    return await db.get_statistics()


# ─── Children ───────────────────────────────────────────────────

@app.get("/api/children")
async def list_children():
    return await db.get_all_children()


@app.get("/api/children/{child_id}")
async def get_child(child_id: int):
    child = await db.get_child_by_id(child_id)
    if not child:
        return {"error": "Not found"}, 404
    records = await db.get_health_records(child_id)
    return {"child": child, "records": records}


@app.get("/api/children/by-nik/{nik}")
async def get_child_by_nik(nik: str):
    child = await db.get_child_by_nik(nik)
    if not child:
        return {"error": "Not found"}, 404
    records = await db.get_health_records(child["id"])
    return {"child": child, "records": records}


@app.get("/api/children/risk/{risk_status}")
async def list_by_risk(risk_status: str):
    return await db.get_children_by_risk(risk_status)


@app.post("/api/children")
async def create_child(request: Request):
    data = await request.json()
    try:
        child_id = await db.add_child(data)
        return {"success": True, "id": child_id, "name": data["name"]}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


# ─── Health Records ─────────────────────────────────────────────

@app.post("/api/children/{child_id}/health-record")
async def create_health_record(child_id: int, request: Request):
    """Add a health record with automatic BB/TB risk classification."""
    data = await request.json()

    # Calculate age from date_of_birth if provided
    age_months = data.get("age_months", 24)  # default 24 months

    # Classify risk
    classification = clf.classify_bb_tb(
        age_months=age_months,
        gender=data.get("gender", "L"),
        weight_kg=data["weight_kg"],
        height_cm=data["height_cm"],
    )

    # Add classification result to record
    record_data = {
        "child_id": child_id,
        "date": data.get("date", ""),
        "weight_kg": data["weight_kg"],
        "height_cm": data["height_cm"],
        "bb_tb_status": classification["status"],
        "vitamin_a": data.get("vitamin_a", False),
        "immunization_status": data.get("immunization_status", "complete"),
        "notes": data.get("notes", ""),
        "recorded_by": data.get("recorded_by"),
    }

    try:
        record_id = await db.add_health_record(record_data)
        await db.update_child_risk(child_id, classification["status"])
        return {
            "success": True,
            "id": record_id,
            "classification": classification,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


# ─── AI Agent ───────────────────────────────────────────────────

@app.post("/api/agent/chat")
async def agent_chat(request: Request):
    """AI Agent chat endpoint."""
    data = await request.json()
    telegram_id = data.get("telegram_id", "anonymous")
    message = data.get("message", "")

    if not message:
        return {"response": "Maaf, pesan kosong."}

    response = await ag.process_message(message, telegram_id)
    return {"response": response}


@app.get("/api/agent/classify")
async def classify_child(
    age_months: int = 24,
    gender: str = "L",
    weight_kg: float = 12.0,
    height_cm: float = 85.0,
):
    """Standalone BB/TB classification endpoint."""
    return clf.classify_bb_tb(age_months, gender, weight_kg, height_cm)


@app.get("/api/agent/lessons")
async def get_lessons():
    """List all learned lessons and their success rates."""
    lessons = await db.get_all_lessons()
    stats = await db.get_lesson_stats()
    return {"lessons": lessons, "stats": stats}


@app.get("/api/agent/errors")
async def get_errors():
    """List unresolved errors for review."""
    return {"errors": await db.get_unresolved_errors()}


# ─── Schedules ───────────────────────────────────────────────────

@app.get("/api/schedules")
async def list_schedules(posyandu_id: int = None, target_role: str = None):
    return await db.get_schedules(posyandu_id=posyandu_id, target_role=target_role)


@app.post("/api/schedules")
async def create_schedule(request: Request):
    data = await request.json()
    try:
        sid = await db.add_schedule(data)
        return {"success": True, "id": sid}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@app.delete("/api/schedules/{schedule_id}")
async def delete_schedule(schedule_id: int):
    ok = await db.delete_schedule(schedule_id)
    return {"success": ok}


# ─── Posyandu ───────────────────────────────────────────────────

@app.get("/api/posyandu")
async def list_posyandu():
    return await db.get_all_posyandus()


@app.post("/api/posyandu")
async def create_posyandu(request: Request):
    data = await request.json()
    try:
        pid = await db.add_posyandu(data)
        return {"success": True, "id": pid}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


# ─── Static Files (Frontend) ────────────────────────────────────────
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@app.get("/")
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Patyandu AI API - frontend not built"}

@app.get("/dashboard/{path:path}")
async def serve_dashboard(path: str):
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return RedirectResponse("/")

@app.get("/static/{path:path}")
async def serve_static(path: str):
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Not found"}, 404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=5001, reload=False)
