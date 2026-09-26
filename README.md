# Binance AI Square Agent

Automatically researches crypto topics, generates an original Binance Square post, validates it, and publishes it once per day using the official Binance Square OpenAPI posting interface.

## Live dashboard

The repository includes a responsive GitHub Pages dashboard that displays the agent's recorded publishing history. It is deployed automatically whenever the site or history changes:

`https://phoenix1185.github.io/binance-ai-square-agent/`

GitHub Pages is a static site, so it does not hold API keys or execute the Python agent in the browser. The agent runs securely in GitHub Actions; the Pages dashboard only displays the history committed by the workflow.

## Important

This repository is designed for legitimate, original content. It does not automate likes, follows, comments, views, multiple accounts, or artificial engagement.

The repository uses the Binance Square posting API key only for Square publishing. Never put a Binance trading/withdrawal API key in this project.

## Architecture

GitHub Actions cron
→ research Binance market/news data
→ generate original post with AI
→ duplicate/spam/safety checks
→ publish to Binance Square
→ save posting history
→ deploy the GitHub Pages dashboard

## Requirements

- GitHub account
- Binance Square Creator account eligible to publish
- Binance Square OpenAPI key
- OpenAI API key

The Binance Square key is separate from normal Binance trading/asset API credentials.

## Setup

### 1. Add GitHub Actions secrets

Repository → Settings → Secrets and variables → Actions → New repository secret

Add:

- `BINANCE_SQUARE_OPENAPI_KEY`
- `OPENAI_API_KEY`

Never put either key into source files.

### 2. Test manually

GitHub → Actions → **Binance AI Daily Post** → **Run workflow**. Select `dry_run` to generate and validate a post without publishing.

### 3. Automatic schedule

The included workflow is configured for **08:00 Nigeria time (WAT)**, which is 07:00 UTC. GitHub Actions schedules can occasionally be delayed during high load. If a precise posting minute is critical, use an external scheduler instead.

## Local test

Python 3.11+ is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export BINANCE_SQUARE_OPENAPI_KEY="YOUR_SQUARE_KEY"
export OPENAI_API_KEY="YOUR_OPENAI_KEY"

python src/agent.py
```

Dry run:

```bash
python src/agent.py --dry-run
```

## Configuration

Environment variables:

- `OPENAI_API_KEY` — required
- `BINANCE_SQUARE_OPENAPI_KEY` — required unless using `--dry-run`
- `OPENAI_MODEL` — optional; default `gpt-5-mini`
- `POST_MIN_WORDS` — optional; default 90
- `POST_MAX_WORDS` — optional; default 230

## Security

Do not commit API keys, `.env`, wallet/private keys, or Binance trading credentials. The `.gitignore` excludes common secret files.

## License

MIT
