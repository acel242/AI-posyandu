import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from contextlib import asynccontextmanager
import database as db
import classifier as clf
import agent as ag
import scheduler as sc
import chart_generator as cg
import who_anthro as who
import os
from dotenv import load_dotenv

# Load .env from project root or backend directory
_env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env_file):
    load_dotenv(_env_file)
else:
    load_dotenv()  # fallback to default


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_db()
    scheduler = sc.build_scheduler()
    sc.start_scheduler(scheduler)
    app.state.scheduler = scheduler
    yield
    scheduler.shutdown(wait=True)

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


@app.get("/api/trends")
async def get_trends(months: int = 6):
    """
    Get Z-score distribution trends over the last N months.
    
    Query params:
        months: number of months to include (default 6, max 24)
    
    Returns:
        - trends: list of monthly breakdowns
        - current: latest month summary
        - changes: difference from previous month
    """
    months = min(max(1, months), 24)
    return await db.get_zscore_trends(months)


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
    """Add a health record with automatic WHO z-score classification."""
    data = await request.json()

    # Get child's DOB and gender from DB
    child = await db.get_child_by_id(child_id)
    if not child:
        return {"success": False, "error": "Child not found"}, 404

    dob = child["date_of_birth"]
    gender = child["gender"]

    # Calculate age in months from DOB + measurement date
    from datetime import datetime
    mdate = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    dob_dt = datetime.strptime(dob, "%Y-%m-%d")
    mdate_dt = datetime.strptime(mdate[:10], "%Y-%m-%d")
    age_months = (mdate_dt - dob_dt).days / 30.436875

    weight_kg = float(data["weight_kg"])
    height_cm = float(data["height_cm"])

    # WHO z-score calculation
    z_wfa = who.calc_zscore_weight_for_age(weight_kg, age_months, gender)
    z_hfa = who.calc_zscore_height_for_age(height_cm, age_months, gender)
    z_wfh = who.calc_zscore_weight_for_height(weight_kg, height_cm, gender)
    overall = who.classify_overall(weight_kg, height_cm, age_months, gender)

    # Also run old classifier for bb_tb_status
    classification = clf.classify_bb_tb(
        age_months=age_months,
        gender=gender,
        weight_kg=weight_kg,
        height_cm=height_cm,
    )

    record_data = {
        "child_id": child_id,
        "date": mdate[:10],
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "bb_tb_status": classification["status"],  # keep old classifier for compatibility
        "vitamin_a": data.get("vitamin_a", False),
        "immunization_status": data.get("immunization_status", "complete"),
        "notes": data.get("notes", ""),
        "recorded_by": data.get("recorded_by"),
        "z_score_wfa": z_wfa,
        "z_score_hfa": z_hfa,
        "z_score_wfh": z_wfh,
        "age_months": round(age_months, 1),
        "overall_status": overall,
    }

    try:
        record_id = await db.add_health_record(record_data)
        await db.update_child_risk(child_id, overall)

        # Trigger risk alert if child is high-risk
        if overall in ("yellow", "red"):
            asyncio.create_task(sc.trigger_risiko_tinggi_alert(child_id))

        return {
            "success": True,
            "id": record_id,
            "z_score_wfa": z_wfa,
            "z_score_hfa": z_hfa,
            "z_score_wfh": z_wfh,
            "overall_status": overall,
            "bb_tb_status": classification["status"],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


# ─── Growth Chart ──────────────────────────────────────────────

@app.get("/api/children/{child_id}/measurements")
async def get_measurements(child_id: int):
    """Get all measurements for a child with WHO z-scores."""
    child = await db.get_child_by_id(child_id)
    if not child:
        return {"error": "Child not found"}, 404
    measurements = await db.get_child_measurements(child_id)
    return {
        "child": child,
        "measurements": measurements,
    }


@app.get("/api/children/{child_id}/growth-chart.png")
async def get_growth_chart_png(child_id: int, chart_type: str = "wfa"):
    """Generate and return a growth chart PNG."""
    child = await db.get_child_by_id(child_id)
    if not child:
        return {"error": "Child not found"}, 404
    
    measurements = await db.get_child_measurements(child_id)
    if not measurements:
        return {"error": "No measurements yet"}, 404
    
    try:
        png_data = cg.generate_growth_chart_png(
            child_name=child["name"],
            gender=child["gender"],
            measurements=measurements,
            chart_type=chart_type,
        )
        from fastapi.responses import Response
        return Response(content=png_data, media_type="image/png")
    except Exception as e:
        return {"error": str(e)}, 500


@app.get("/api/children/{child_id}/growth-summary")
async def get_growth_summary(child_id: int):
    """Get a text summary of growth for Telegram display."""
    child = await db.get_child_by_id(child_id)
    if not child:
        return {"error": "Child not found"}, 404
    
    measurements = await db.get_child_measurements(child_id)
    if not measurements:
        return {"summary": f"{child["name"]}: Belum ada data pengukuran."}
    
    summary = cg.generate_measurement_summary(measurements, child["name"], child["gender"])
    return {"summary": summary, "child": child, "measurements": measurements}


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


# ─── Kader / Bidan ──────────────────────────────────────────────────

@app.get("/api/kaders")
async def list_kaders():
    """List all kader and bidan accounts."""
    return await db.get_all_kaders()


@app.get("/api/kaders/{kader_id}")
async def get_kader(kader_id: int):
    kader = await db.get_kader_by_id(kader_id)
    if not kader:
        return {"error": "Not found"}, 404
    return kader


@app.post("/api/kaders")
async def create_kader(request: Request):
    """Register a new kader or bidan. Body: {name, role, telegram_id?}"""
    data = await request.json()
    if not data.get("name"):
        return {"error": "name is required"}, 400
    try:
        kid = await db.add_kader(data)
        return {"success": True, "id": kid, "name": data["name"]}
    except Exception as e:
        return {"success": False, "error": str(e)}, 500


@app.post("/api/kaders/{kader_id}/link")
async def link_kader_telegram(kader_id: int, request: Request):
    """Link a Telegram ID to a kader. Body: {telegram_id}"""
    data = await request.json()
    tid = data.get("telegram_id")
    if not tid:
        return {"error": "telegram_id required"}, 400
    kader = await db.get_kader_by_id(kader_id)
    if not kader:
        return {"error": "Kader not found"}, 404
    ok = await db.link_kader_telegram(kader_id, tid)
    return {"success": ok, "kader_id": kader_id}


@app.post("/api/kaders/{kader_id}/unlink")
async def unlink_kader_telegram(kader_id: int):
    """Unlink a Telegram ID from a kader."""
    ok = await db.unlink_kader_telegram(kader_id)
    return {"success": ok}


@app.delete("/api/kaders/{kader_id}")
async def remove_kader(kader_id: int):
    ok = await db.delete_kader(kader_id)
    return {"success": ok}


# ─── Alerts ─────────────────────────────────────────────────────

@app.get("/api/alerts/logs")
async def get_alert_logs(
    child_id: int = None,
    alert_type: str = None,
    status: str = None,
    limit: int = 100,
    offset: int = 0,
):
    """Get alert log entries with optional filters."""
    return await db.get_alert_logs(
        child_id=child_id,
        alert_type=alert_type,
        status=status,
        limit=limit,
        offset=offset,
    )


@app.get("/api/alerts/pending")
async def get_pending_alerts(limit: int = 100):
    """Get pending alerts that haven't been sent yet."""
    return await db.get_pending_alerts(limit=limit)


@app.post("/api/alerts/retry/{alert_id}")
async def retry_alert(alert_id: int):
    """Reset a failed alert back to pending for retry."""
    ok = await db.retry_alert(alert_id)
    return {"success": ok, "alert_id": alert_id}


@app.get("/api/alerts/stats")
async def get_alert_stats():
    """Get alert statistics."""
    return await db.get_alert_stats()


@app.post("/api/alerts/send")
async def send_test_alert(request: Request):
    """Manually trigger an alert for testing. Supply child_id + alert_type."""
    data = await request.json()
    child_id = data.get("child_id")
    alert_type = data.get("alert_type")  # posyandu_reminder | belum_timbang | risiko_tinggi

    if not child_id or not alert_type:
        return {"success": False, "error": "child_id and alert_type required"}, 400

    if alert_type == "risiko_tinggi":
        await sc.trigger_risiko_tinggi_alert(child_id)
        return {"success": True, "alert_type": alert_type, "child_id": child_id}
    else:
        return {"success": False, "error": "Manual send for this alert_type not yet implemented"}, 501


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
    if not path:
        return RedirectResponse("/")
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return RedirectResponse("/")

# SPA catch-all — serve index.html for any non-API frontend route
@app.get('/{path:path}')
async def serve_spa(path: str):
    """Serve the SPA for any path not matched above."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"error": "not found"}, 404

@app.get("/static/{path:path}")
async def serve_static(path: str):
    file_path = os.path.join(STATIC_DIR, path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Not found"}, 404

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
