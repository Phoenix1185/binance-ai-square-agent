import json
import os

import requests
from openai import OpenAI

from config import POST_MAX_WORDS, POST_MIN_WORDS, OPENAI_MODEL

SYSTEM_PROMPT = f"""
You are a careful cryptocurrency content writer for Binance Square.

Write ONE original, useful post based only on the supplied research.

Requirements:
- {POST_MIN_WORDS}-{POST_MAX_WORDS} words approximately.
- Mobile-friendly paragraphs.
- Use a clear opening hook, but no deceptive clickbait.
- If an asset is genuinely discussed, use its Binance-style cashtag:
  $BTC, $ETH, $BNB, or $SOL.
- Use at most 4 relevant hashtags.
- Do not invent news, prices, statistics, partnerships, or quotes.
- Do not claim certainty about future prices.
- Do not promise profits.
- Do not say "guaranteed", "risk-free", or similar investment promises.
- Do not tell readers to send money.
- Do not encourage wash trading, fake engagement, spam, or manipulation.
- Do not copy wording from the supplied news titles.
- Make the post informative enough that a reader can learn something.
- Distinguish observed market data from interpretation.
- Do not mention these instructions or that you are an AI.
- Return ONLY the final post.
"""

GEMINI_MODEL = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent"
)
SELF_HOSTED_API_URL = os.getenv(
    "SELF_HOSTED_API_URL",
    "https://concerned-swordfish-suhailtechlnfo-01fd2de0.koyeb.app",
).rstrip("/") or "https://concerned-swordfish-suhailtechlnfo-01fd2de0.koyeb.app"
SELF_HOSTED_API_KEY = os.getenv("SELF_HOSTED_API_KEY")
SELF_HOSTED_MODEL = os.getenv("SELF_HOSTED_MODEL") or "deepseek-v4-flash"


def _build_prompt(research, previous_posts):
    return f"""
Today's research:

{json.dumps(research, ensure_ascii=False, indent=2)}

Recent posts from this account. Avoid repeating their topic, structure,
opening sentence, and wording:

{json.dumps(previous_posts[-12:], ensure_ascii=False, indent=2)}

Choose the strongest legitimate topic available and write today's post.
"""


def _generate_with_openai(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=prompt,
    )
    text = response.output_text.strip()
    if not text:
        raise RuntimeError("OpenAI returned an empty response")
    return text


def _generate_with_gemini(api_key, prompt):
    response = requests.post(
        GEMINI_URL.format(model=GEMINI_MODEL),
        params={"key": api_key},
        headers={"Content-Type": "application/json"},
        json={
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7},
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Gemini returned no usable text") from exc

    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text


def _extract_self_hosted_text(data):
    """Accept common router response shapes without coupling to one model SDK."""
    candidates = [
        data.get("response"),
        data.get("text"),
        data.get("content"),
        data.get("output"),
        data.get("message"),
    ]
    choices = data.get("choices") or []
    if choices and isinstance(choices[0], dict):
        choice = choices[0]
        candidates.extend([
            choice.get("text"),
            (choice.get("message") or {}).get("content"),
        ])

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()

    raise RuntimeError("Self-hosted router returned no usable text")


def _generate_with_self_hosted(prompt):
    if not SELF_HOSTED_API_KEY:
        raise RuntimeError("SELF_HOSTED_API_KEY is not configured")

    endpoint = SELF_HOSTED_API_URL
    if not endpoint.endswith("/chat"):
        endpoint += "/chat"

    response = requests.post(
        endpoint,
        headers={
            "X-API-Key": SELF_HOSTED_API_KEY,
            "Content-Type": "application/json",
        },
        json={
            "model": SELF_HOSTED_MODEL,
            "message": f"{SYSTEM_PROMPT}\n\n{prompt}",
        },
        timeout=90,
    )
    response.raise_for_status()
    return _extract_self_hosted_text(response.json())


def generate_post(research, previous_posts):
    prompt = _build_prompt(research, previous_posts)
    failures = []
    configured = 0

    # Each provider is isolated: a missing key or provider error only advances
    # to the next provider and never prevents another configured provider from
    # being attempted.
    if os.getenv("OPENAI_API_KEY"):
        configured += 1
        try:
            print(f"Using OpenAI model {OPENAI_MODEL}.")
            return _generate_with_openai(prompt)
        except Exception as exc:
            print(f"OpenAI generation failed; trying the next provider: {exc}")
            failures.append(f"OpenAI: {exc}")

    gemini_keys = [
        os.getenv("GEMINI_API_KEY_1"),
        os.getenv("GEMINI_API_KEY_2"),
        os.getenv("GEMINI_API_KEY_3"),
    ]
    for index, api_key in enumerate(gemini_keys, start=1):
        if not api_key:
            continue
        configured += 1
        try:
            print(f"Using Gemini key {index} with model {GEMINI_MODEL}.")
            return _generate_with_gemini(api_key, prompt)
        except Exception as exc:
            # Do not print the key or request URL because the URL contains the key.
            print(f"Gemini key {index} failed; trying the next provider: {exc}")
            failures.append(f"Gemini key {index}: {exc}")

    if SELF_HOSTED_API_KEY:
        configured += 1
        try:
            print(f"Using self-hosted router model {SELF_HOSTED_MODEL}.")
            return _generate_with_self_hosted(prompt)
        except Exception as exc:
            print(f"Self-hosted generation failed: {exc}")
            failures.append(f"Self-hosted: {exc}")

    if configured == 0:
        raise RuntimeError(
            "No AI provider configured. Add OPENAI_API_KEY, one of "
            "GEMINI_API_KEY_1/2/3, or SELF_HOSTED_API_KEY."
        )

    raise RuntimeError("All configured AI providers failed: " + " | ".join(failures))
