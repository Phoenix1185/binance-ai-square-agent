import os

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")

POST_MIN_WORDS = int(os.getenv("POST_MIN_WORDS", "90"))
POST_MAX_WORDS = int(os.getenv("POST_MAX_WORDS", "230"))

BINANCE_SQUARE_URL = (
    "https://www.binance.com/bapi/composite/v1/public/"
    "pgc/openApi/content/add"
)
