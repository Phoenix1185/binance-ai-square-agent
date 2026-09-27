import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from agent import run_agent, load_history, save_history

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "10000"))
TRIGGER_TOKEN = os.getenv("AGENT_TRIGGER_TOKEN", "")


def authorized(handler):
    if not TRIGGER_TOKEN:
        return False
    header = handler.headers.get("Authorization", "")
    supplied = header[7:] if header.startswith("Bearer ") else ""
    return secrets.compare_digest(supplied, TRIGGER_TOKEN)


def send_json(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            send_json(self, 200, {"ok": True, "service": "binance-ai-square-agent"})
            return
        if path == "/history":
            if not authorized(self):
                send_json(self, 401, {"error": "unauthorized"})
                return
            send_json(self, 200, {"history": load_history()})
            return
        send_json(self, 404, {"error": "not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if not authorized(self):
            send_json(self, 401, {"error": "unauthorized"})
            return

        if path == "/sync-history":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw or b"{}")
                history = payload.get("history", [])
                if not isinstance(history, list):
                    raise ValueError("history must be a list")
                save_history(history)
                send_json(self, 200, {"ok": True, "count": len(history)})
            except Exception as exc:
                send_json(self, 400, {"error": str(exc)})
            return

        if path == "/run":
            dry_run = parse_qs(parsed.query).get("dry_run", ["0"])[0] == "1"
            try:
                result = run_agent(dry_run=dry_run)
                send_json(self, 200, result)
            except Exception as exc:
                print(f"Agent run failed: {exc}")
                send_json(self, 500, {"success": False, "error": str(exc)})
            return

        send_json(self, 404, {"error": "not found"})


if __name__ == "__main__":
    print(f"Starting Render web service on {HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
