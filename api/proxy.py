"""
Vercel API Proxy — routes all /api/* requests to backend.
"""

import os
from flask import Flask, request, Response
import urllib.request
import urllib.parse
import urllib.error
import json

app = Flask(__name__)

# Backend URL — can be overridden via env var
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:5001")

@app.after_request
def add_cors_headers(response):
    """Add CORS headers for cross-origin requests."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def api_proxy(path):
    """Forward request to backend."""
    if request.method == 'OPTIONS':
        return Response('', status=204)
    
    backend_url = f"{BACKEND_URL}/api/{path}"
    query_string = request.query_string.decode()
    if query_string:
        backend_url += f"?{query_string}"
    
    try:
        headers = {k: v for k, v in request.headers if k.lower() not in ("host", "connection")}
        
        req = urllib.request.Request(backend_url, method=request.method, headers=headers)
        if request.method in ('POST', 'PUT', 'PATCH') and request.data:
            req.data = request.data
        
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            result = Response(data, status=resp.status)
            for key, value in resp.headers.items():
                if key.lower() not in ('transfer-encoding', 'content-encoding', 'content-length'):
                    result.headers[key] = value
            return result
    
    except urllib.error.HTTPError as e:
        return Response(e.read(), status=e.code, content_type=e.headers.get('Content-Type', 'application/json'))
    except Exception as e:
        return Response(json.dumps({"error": str(e), "backend_url": backend_url}), status=502, content_type='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
