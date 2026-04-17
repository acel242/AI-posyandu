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

BACKEND_URL = os.environ.get("BACKEND_URL", "http://43.157.235.76:5001")

ALLOWED_PATHS = [
    "/api/health",
    "/api/stats",
    "/api/children",
    "/api/schedules",
    "/api/posyandu",
    "/api/agent/classify",
    "/api/agent/chat",
]


def proxy_request(method, path, query_string=None):
    """Forward request to backend VM and return response."""
    if not any(path.startswith(p) for p in ALLOWED_PATHS):
        return Response("Forbidden", status=403)

    backend_url = f"{BACKEND_URL}{path}"
    if query_string:
        backend_url = f"{backend_url}?{query_string}"

    try:
        headers = {k: v for k, v in request.headers if k.lower() not in ("host", "x-forwarded-host")}
        
        req = urllib.request.Request(backend_url, method=method, headers=headers)
        if method in ("POST", "PATCH") and request.data:
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


@app.route("/api/children/<path:child_id>")
def child_detail(child_id):
    return proxy_request("GET", f"/api/children/{child_id}")


@app.route("/api/schedules")
def schedules():
    return proxy_request("GET", "/api/schedules")


@app.route("/api/posyandu")
def posyandu():
    return proxy_request("GET", "/api/posyandu")


@app.route("/api/agent/classify")
def classify():
    return proxy_request("GET", "/api/agent/classify", request.query_string.decode())


@app.route("/api/agent/chat", methods=["POST"])
def chat():
    return proxy_request("POST", "/api/agent/chat")


@app.route("/<path:path>", methods=["GET", "POST", "PATCH", "DELETE"])
def catch_all(path):
    return proxy_request(request.method, f"/{path}", request.query_string.decode())
