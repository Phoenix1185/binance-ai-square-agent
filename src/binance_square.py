import os
import requests

from config import BINANCE_SQUARE_URL

SUCCESS_CODE = "000000"


class BinanceSquareError(RuntimeError):
    pass


def publish_to_square(text):
    api_key = os.environ.get("BINANCE_SQUARE_OPENAPI_KEY")

    if not api_key:
        raise BinanceSquareError(
            "BINANCE_SQUARE_OPENAPI_KEY is not configured."
        )

    headers = {
        "X-Square-OpenAPI-Key": api_key,
        "Content-Type": "application/json",
        "clienttype": "binanceSkill",
    }

    payload = {"bodyTextOnly": text}

    try:
        response = requests.post(
            BINANCE_SQUARE_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise BinanceSquareError(
            f"Network error while publishing: {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError:
        raise BinanceSquareError(
            f"Binance returned HTTP {response.status_code} with "
            "a non-JSON response."
        )

    code = str(data.get("code", ""))

    if code != SUCCESS_CODE:
        message = data.get("message") or "Unknown Binance Square error"
        raise BinanceSquareError(
            f"Binance Square error {code}: {message}"
        )

    post_id = ((data.get("data") or {}).get("id"))

    # Binance's current skill notes that a successful submission can
    # occasionally return without an ID. Do not falsely claim failure.
    if not post_id:
        return {
            "id": None,
            "url": None,
            "success": True,
            "message": (
                "Submission accepted but Binance did not return a post ID."
            ),
        }

    return {
        "id": str(post_id),
        "url": f"https://www.binance.com/square/post/{post_id}",
        "success": True,
        "message": "Published successfully.",
    }
