import json
import os
from openai import OpenAI

from config import OPENAI_MODEL, POST_MIN_WORDS, POST_MAX_WORDS

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


def generate_post(research, previous_posts):
    api_key = os.environ["OPENAI_API_KEY"]
    client = OpenAI(api_key=api_key)

    prompt = f"""
Today's research:

{json.dumps(research, ensure_ascii=False, indent=2)}

Recent posts from this account. Avoid repeating their topic, structure,
opening sentence, and wording:

{json.dumps(previous_posts[-12:], ensure_ascii=False, indent=2)}

Choose the strongest legitimate topic available and write today's post.
"""

    response = client.responses.create(
        model=OPENAI_MODEL,
        instructions=SYSTEM_PROMPT,
        input=prompt,
    )

    return response.output_text.strip()
