# Binance AI Square Agent

Automatically researches crypto topics, generates an original Binance Square post, validates it, and publishes it once per day using the official Binance Square OpenAPI posting interface.

## Live dashboard

The repository includes a responsive GitHub Pages dashboard that displays the agent's recorded publishing history. It is deployed automatically whenever the site or history changes:

`https://phoenix1185.github.io/binance-ai-square-agent/`

GitHub Pages is a static site, so it does not hold API keys or execute the Python agent in the browser. The agent runs securely in GitHub Actions; the Pages dashboard only displays the history committed by the workflow.

## Self-hosted AI Router

The companion Phoenix AI Router API is running at:

- [API base URL](https://concerned-swordfish-suhailtechlnfo-01fd2de0.koyeb.app/)
- [Interactive API documentation](https://concerned-swordfish-suhailtechlnfo-01fd2de0.koyeb.app/docs)

The agent can use this router as its final AI fallback. Configure `SELF_HOSTED_API_KEY` in GitHub Actions and optionally override `SELF_HOSTED_API_URL` and `SELF_HOSTED_MODEL`.

## Independent AI fallback chain

The agent tries providers independently in this order:

1. OpenAI using `OPENAI_API_KEY`
2. Gemini using `GEMINI_API_KEY_1`
3. Gemini using `GEMINI_API_KEY_2`
4. Gemini using `GEMINI_API_KEY_3`
5. Self-hosted Phoenix AI Router using `SELF_HOSTED_API_KEY`

Missing credentials are skipped. A failure, timeout, quota error, or invalid response from one provider is caught and the next configured provider is tried. Therefore, a self-hosted-only setup works when OpenAI and Gemini secrets are absent, and a failure in one provider cannot prevent another configured provider from running.

## Important

This repository is designed for legitimate, original content. It does not automate likes, follows, comments, views, multiple accounts, or artificial engagement.

The repository uses the Binance Square posting API key only for Square publishing. Never put a Binance trading/withdrawal API key in this project.

## Architecture

GitHub Actions cron
→ research Binance market/news data
→ generate original post with AI fallback chain
→ duplicate/spam/safety checks
→ publish to Binance Square
→ save posting history
→ deploy the GitHub Pages dashboard

## Requirements

- GitHub account
- Binance Square Creator account eligible to publish
- Binance Square OpenAPI key
- At least one AI provider: OpenAI, Gemini, or the self-hosted Phoenix AI Router

The Binance Square key is separate from normal Binance trading/asset API credentials.

## Setup

### 1. Add GitHub Actions secrets

Repository → Settings and variables → Actions → New repository secret

Add the Binance key:

- `BINANCE_SQUARE_OPENAPI_KEY`

Add one or more AI providers:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY_1`
- `GEMINI_API_KEY_2`
- `GEMINI_API_KEY_3`
- `SELF_HOSTED_API_KEY`

For self-hosted-only mode, you need only:

- `BINANCE_SQUARE_OPENAPI_KEY`
- `SELF_HOSTED_API_KEY`

Optional repository variables:

- `OPENAI_MODEL` — default `gpt-5-mini`
- `GEMINI_MODEL` — default `gemini-2.5-flash`
- `SELF_HOSTED_API_URL` — default `https://concerned-swordfish-suhailtechlnfo-01fd2de0.koyeb.app`
- `SELF_HOSTED_MODEL` — default `deepseek-v4-flash`

Never put keys into source files. Keys are never printed to logs.

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
export SELF_HOSTED_API_KEY="YOUR_ROUTER_API_KEY"

python src/agent.py
```

Dry run:

```bash
python src/agent.py --dry-run
```

## Configuration

Environment variables:

- `OPENAI_API_KEY` — optional primary provider
- `GEMINI_API_KEY_1` — optional first Gemini fallback key
- `GEMINI_API_KEY_2` — optional second Gemini fallback key
- `GEMINI_API_KEY_3` — optional third Gemini fallback key
- `SELF_HOSTED_API_KEY` — optional final fallback router key
- `SELF_HOSTED_API_URL` — optional router base URL; defaults to the Koyeb service
- `SELF_HOSTED_MODEL` — optional router model; default `deepseek-v4-flash`
- `BINANCE_SQUARE_OPENAPI_KEY` — required unless using `--dry-run`
- `OPENAI_MODEL` — optional; default `gpt-5-mini`
- `GEMINI_MODEL` — optional; default `gemini-2.5-flash`
- `POST_MIN_WORDS` — optional; default 90
- `POST_MAX_WORDS` — optional; default 230

## Security

Do not commit API keys, `.env`, wallet/private keys, or Binance trading credentials. The `.gitignore` excludes common secret files. Provider keys are sent only to their configured provider and are never included in logs.

## License

MIT
