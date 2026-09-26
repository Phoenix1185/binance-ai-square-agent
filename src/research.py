import requests
import feedparser
from datetime import datetime, timezone

BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/24hr"

# Public Binance announcements RSS. If Binance changes this feed,
# the market data still provides a useful fallback.
BINANCE_NEWS_RSS = "https://www.binance.com/en/support/announcement/rss"

SYMBOLS = ("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT")


def get_market_data():
    result = {}

    for symbol in SYMBOLS:
        try:
            response = requests.get(
                BINANCE_TICKER_URL,
                params={"symbol": symbol},
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            result[symbol] = {
                "price": data.get("lastPrice"),
                "change_24h": data.get("priceChangePercent"),
                "volume_24h": data.get("volume"),
                "high_24h": data.get("highPrice"),
                "low_24h": data.get("lowPrice"),
            }
        except Exception as exc:
            print(f"Market data warning for {symbol}: {exc}")

    return result


def get_news(limit=8):
    try:
        feed = feedparser.parse(BINANCE_NEWS_RSS)
        items = []

        for item in feed.entries[:limit]:
            items.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "published": item.get("published", ""),
            })

        return items
    except Exception as exc:
        print(f"News warning: {exc}")
        return []


def collect_research():
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "market": get_market_data(),
        "news": get_news(),
    }
