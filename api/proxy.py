"""
Vercel API Proxy — routes all /api/* requests to backend via tunnel.
Uses Flask for @vercel/python compatibility.
"""

import os
from flask import Flask, request, Response
import urllib.request
import urllib.error

app = Flask(__name__)

# Backend URL — override with env var BACKEND_URL for production
# Auto-detect: if running locally (has backend on port 5001), use localhost
# Otherwise use provided tunnel URL
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5001")


def proxy_request(method, path, query_string=None):
    """Forward request to backend and return response."""
    url = f"{BACKEND_URL}{path}"
    if query_string:
        url += f"?{query_string}"

    try:
        headers = {k: v for k, v in request.headers 
                   if k.lower() not in ("host", "connection", "transfer-encoding")}
        
        req = urllib.request.Request(url, method=method, headers=headers)
        if method in ("POST", "PATCH", "PUT") and request.data:
            req.data = request.data

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            result = Response(data, status=resp.status)
            for key in ('Content-Type', 'Content-Length', 'Cache-Control'):
                if key in resp.headers:
                    result.headers[key] = resp.headers[key]
            return result

    except urllib.error.HTTPError as e:
        return Response(
            str({"error": str(e.code), "message": e.read().decode()}).replace("'", '"'),
            status=e.code,
            content_type='application/json'
        )
    except Exception as e:
        return Response(
            str({"error": "Backend unreachable", "url": url, "detail": str(e)}).replace("'", '"'),
            status=502,
            content_type='application/json'
        )


@app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def catch_all(path):
    return proxy_request(request.method, f"/{path}", request.query_string.decode())


@app.route("/api/health")
def health():
    return proxy_request("GET", "/api/health")
