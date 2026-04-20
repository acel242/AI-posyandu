"""Railway entry point — starts the FastAPI server."""
import uvicorn, os

PORT = int(os.environ.get("PORT", 8000))
uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=False)
