import re

FORBIDDEN_PATTERNS = [
    r"\bguaranteed\s+(?:profit|return|gains?)\b",
    r"\b100%\s+guaranteed\b",
    r"\brisk[- ]free\b",
    r"\bdouble\s+your\s+money\b",
    r"\bsend\s+(?:me|us)\s+money\b",
    r"\bdeposit\s+(?:now|today)\b",
]


def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def word_count(text):
    return len(re.findall(r"\b[\w$#'-]+\b", text))


def similarity(a, b):
    a_words = set(normalize(a).split())
    b_words = set(normalize(b).split())

    if not a_words or not b_words:
        return 0.0

    return len(a_words & b_words) / len(a_words | b_words)


def validate_post(post, history, min_words=90, max_words=280):
    if not post:
        return False, "empty post"

    count = word_count(post)

    if count < min_words:
        return False, f"too short ({count} words)"

    if count > max_words:
        return False, f"too long ({count} words)"

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, post, re.IGNORECASE):
            return False, "contains prohibited promotional/scam language"

    for old in history[-30:]:
        old_text = old.get("post", "") if isinstance(old, dict) else old
        if similarity(post, old_text) >= 0.68:
            return False, "too similar to a recent post"

    return True, "OK"
