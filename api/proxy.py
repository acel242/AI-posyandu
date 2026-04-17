"""
Vercel API Proxy — routes all /api/* requests to VM backend.
"""

import os
import urllib.request
import urllib.parse

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


def handler(req, context):
    path = req.path

    # Only allow specific API paths
    if not any(path.startswith(p) for p in ALLOWED_PATHS):
        return {"statusCode": 403, "body": "Forbidden"}

    # Build backend URL
    backend_url = f"{BACKEND_URL}{path}"
    query = req.query
    if query:
        backend_url = f"{backend_url}?{query}"

    try:
        headers = dict(req.headers)
        headers.pop("host", None)
        headers.pop("x-forwarded-host", None)

        # Prepare urllib request
        req_obj = urllib.request.Request(backend_url, method=req.method, headers=headers)
        if req.method in ("POST", "PATCH") and req.body:
            req_obj.data = req.body

        with urllib.request.urlopen(req_obj, timeout=30) as response:
            body = response.read().decode("utf-8")
            return {
                "statusCode": response.status,
                "headers": dict(response.headers),
                "body": body,
            }

    except urllib.error.URLError as e:
        return {"statusCode": 502, "body": f"Backend error: {str(e)}"}
    except Exception as e:
        return {"statusCode": 500, "body": f"Server error: {str(e)}"}
