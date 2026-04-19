"""
Vercel API Proxy — routes all /api/* requests to VM backend.
Uses Flask for @vercel/python compatibility.
"""

import os
from flask import Flask, request, Response
import urllib.request
import urllib.parse
import urllib.error

app = Flask(__name__)

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5001")

ALLOWED_PREFIXES = [
    "/api/health",
    "/api/stats",
    "/api/children",
    "/api/schedules",
    "/api/kaders",
    "/api/alerts",
    "/api/posyandu",
    "/api/agent",
]


def proxy_request(method, path, query_string=None):
    """Forward request to backend VM and return response."""
    if not any(path.startswith(p) for p in ALLOWED_PREFIXES):
        return Response(f"Forbidden: {path}", status=403)

    backend_url = f"{BACKEND_URL}{path}"
    if query_string:
        backend_url = f"{backend_url}?{query_string}"

    try:
        headers = {k: v for k, v in request.headers if k.lower() not in ("host", "x-forwarded-host")}

        req = urllib.request.Request(backend_url, method=method, headers=headers)
        if method in ("POST", "PATCH", "PUT") and request.data:
            req.data = request.data

        with urllib.request.urlopen(req, timeout=30) as resp:
            return Response(
                resp.read(),
                status=resp.status,
                headers=dict(resp.headers)
            )

    except urllib.error.URLError as e:
        return Response(f"Backend error: {e}", status=502)
    except Exception as e:
        return Response(f"Server error: {e}", status=500)


@app.route("/api/health")
def health():
    return proxy_request("GET", "/api/health")


@app.route("/api/stats")
def stats():
    return proxy_request("GET", "/api/stats")


@app.route("/api/children")
def children():
    return proxy_request("GET", "/api/children")


@app.route("/api/children", methods=["POST"])
def children_post():
    return proxy_request("POST", "/api/children")


@app.route("/api/children/<int:child_id>", methods=["GET", "DELETE"])
def child_detail(child_id):
    return proxy_request(request.method, f"/api/children/{child_id}")


@app.route("/api/children/<int:child_id>/health-record", methods=["POST"])
def child_health_record(child_id):
    return proxy_request("POST", f"/api/children/{child_id}/health-record")


@app.route("/api/children/by-nik/<nik>", methods=["GET"])
def child_by_nik(nik):
    return proxy_request("GET", f"/api/children/by-nik/{nik}")


@app.route("/api/children/risk/<risk_status>", methods=["GET"])
def children_by_risk(risk_status):
    return proxy_request("GET", f"/api/children/risk/{risk_status}")


@app.route("/api/schedules", methods=["GET", "POST"])
def schedules():
    return proxy_request(request.method, "/api/schedules")


@app.route("/api/schedules/<int:schedule_id>", methods=["DELETE"])
def schedule_detail(schedule_id):
    return proxy_request("DELETE", f"/api/schedules/{schedule_id}")


@app.route("/api/kaders", methods=["GET", "POST"])
def kaders():
    return proxy_request(request.method, "/api/kaders")


@app.route("/api/kaders/<int:kader_id>", methods=["GET", "DELETE"])
def kader_detail(kader_id):
    return proxy_request(request.method, f"/api/kaders/{kader_id}")


@app.route("/api/kaders/<int:kader_id>/link", methods=["POST"])
def kader_link(kader_id):
    return proxy_request("POST", f"/api/kaders/{kader_id}/link")


@app.route("/api/kaders/<int:kader_id>/unlink", methods=["POST"])
def kader_unlink(kader_id):
    return proxy_request("POST", f"/api/kaders/{kader_id}/unlink")


@app.route("/api/alerts/stats", methods=["GET"])
def alerts_stats():
    return proxy_request("GET", "/api/alerts/stats")


@app.route("/api/alerts/logs", methods=["GET"])
def alerts_logs():
    qs = request.query_string.decode()
    path = "/api/alerts/logs"
    if qs:
        path += f"?{qs}"
    return proxy_request("GET", path)


@app.route("/api/alerts/pending", methods=["GET"])
def alerts_pending():
    return proxy_request("GET", "/api/alerts/pending")


@app.route("/api/alerts/send", methods=["POST"])
def alerts_send():
    return proxy_request("POST", "/api/alerts/send")


@app.route("/api/alerts/retry/<int:alert_id>", methods=["POST"])
def alerts_retry(alert_id):
    return proxy_request("POST", f"/api/alerts/retry/{alert_id}")


@app.route("/api/posyandu", methods=["GET", "POST"])
def posyandu():
    return proxy_request(request.method, "/api/posyandu")


@app.route("/api/agent/classify", methods=["GET"])
def classify():
    qs = request.query_string.decode()
    return proxy_request("GET", "/api/agent/classify", qs)


@app.route("/api/agent/chat", methods=["POST"])
def chat():
    return proxy_request("POST", "/api/agent/chat")


@app.route("/api/agent/lessons", methods=["GET"])
def lessons():
    return proxy_request("GET", "/api/agent/lessons")


@app.route("/api/agent/errors", methods=["GET"])
def errors():
    return proxy_request("GET", "/api/agent/errors")


@app.route("/<path:path>", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
def catch_all(path):
    return proxy_request(request.method, f"/{path}", request.query_string.decode())
