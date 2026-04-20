# Railway entry point — just proxy to backend
import subprocess, sys, os

os.chdir(os.path.join(os.path.dirname(__file__), "backend"))
os.environ.setdefault("DATA_DIR", os.environ.get("DATA_DIR", "/data"))
sys.exit(subprocess.call([
    sys.executable, "-m", "uvicorn", "server:app",
    "--host", "0.0.0.0", "--port", os.environ.get("PORT", "8000")
]))
