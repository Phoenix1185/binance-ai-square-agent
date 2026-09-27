import argparse
import json
import os
import base64

import requests
from datetime import datetime, timezone

from config import POST_MIN_WORDS, POST_MAX_WORDS
from research import collect_research
from writer import generate_post
from quality import validate_post
from binance_square import publish_to_square, BinanceSquareError
from network_diagnostics import print_network_diagnostics

HISTORY_FILE = "data/history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as handle:
            value = json.load(handle)
            return value if isinstance(value, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_history(history):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)

    with open(HISTORY_FILE, "w", encoding="utf-8") as handle:
        json.dump(history[-100:], handle, ensure_ascii=False, indent=2)


def persist_history_to_github():
    """Optionally persist history to the GitHub repository via Contents API."""
    token = os.getenv("GITHUB_AGENT_TOKEN")
    repo = os.getenv("GITHUB_AGENT_REPO")
    if not token or not repo:
        return {"saved": False, "reason": "GitHub persistence not configured"}

    path = "data/history.json"
    try:
        with open(HISTORY_FILE, "rb") as handle:
            content = base64.b64encode(handle.read()).decode("ascii")

        api = f"https://api.github.com/repos/{repo}/contents/{path}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        current = requests.get(api, headers=headers, timeout=20)
        sha = current.json().get("sha") if current.status_code == 200 else None

        payload = {
            "message": "Update Binance Square posting history",
            "content": content,
        }
        if sha:
            payload["sha"] = sha

        response = requests.put(api, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        print("GitHub history persistence: saved")
        return {"saved": True}
    except Exception as exc:
        print(f"GitHub history persistence skipped: {exc}")
        return {"saved": False, "reason": str(exc)}


def run_agent(dry_run=False):
    print("=== Binance AI Square Agent ===")
    print_network_diagnostics()

    history = load_history()

    print("[1/4] Collecting research...")
    research = collect_research()

    print("[2/4] Generating original post...")
    post = generate_post(research, history)

    print("\n--- GENERATED POST ---")
    print(post)
    print("--- END POST ---\n")

    print("[3/4] Validating...")
    valid, reason = validate_post(
        post,
        history,
        min_words=POST_MIN_WORDS,
        max_words=POST_MAX_WORDS + 50,
    )

    if not valid:
        raise RuntimeError(f"Post rejected: {reason}")

    print("Validation passed.")

    if dry_run:
        return {
            "success": True,
            "dry_run": True,
            "post": post,
        }

    print("[4/4] Publishing to Binance Square...")
    result = publish_to_square(post)

    entry = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "post": post,
        "id": result.get("id"),
        "url": result.get("url"),
        "success": result.get("success", False),
        "message": result.get("message"),
    }

    history.append(entry)
    save_history(history)
    persistence = persist_history_to_github()

    print("\n=== PUBLISH RESULT ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    result["history_persistence"] = persistence
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate and validate a post without publishing.",
    )
    args = parser.parse_args()
    run_agent(dry_run=args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except BinanceSquareError as exc:
        print(f"ERROR: {exc}")
        raise
