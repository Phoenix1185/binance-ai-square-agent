import os
import secrets
import sys
import threading
from flask import Flask, jsonify, request

# The agent modules use repository-local top-level imports such as `config`.
# Render starts Gunicorn from the repository root, so expose `src` explicitly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.agent import run_agent

app = Flask(__name__)
run_lock = threading.Lock()

TRIGGER_TOKEN = os.getenv("AGENT_TRIGGER_TOKEN", "").strip()


def authorized(req):
    if not TRIGGER_TOKEN:
        return False
    supplied = req.headers.get("X-Agent-Trigger-Token", "")
    if not supplied:
        supplied = req.args.get("token", "")
    return secrets.compare_digest(supplied, TRIGGER_TOKEN)


@app.get("/")
def home():
    return jsonify({
        "service": "Binance AI Square Agent",
        "status": "online",
        "endpoints": ["/health", "/run"],
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/run")
def run():
    if not authorized(request):
        return jsonify({"ok": False, "error": "unauthorized"}), 401

    if not run_lock.acquire(blocking=False):
        return jsonify({"ok": False, "error": "agent already running"}), 409

    try:
        result = run_agent()
        return jsonify({"ok": True, "result": result})
    except Exception as exc:
        app.logger.exception("Agent run failed")
        return jsonify({"ok": False, "error": str(exc)}), 500
    finally:
        run_lock.release()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
