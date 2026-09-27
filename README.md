# Binance AI Square Agent

A free-hosting architecture for an automated Binance Square content agent.

## Current architecture

```text
GitHub Actions (free scheduler)
        |
        | HTTPS trigger only
        v
Render Free Web Service
        |
        +--> public crypto research
        +--> AI fallback chain
        |      1. OpenAI
        |      2. Gemini key 1
        |      3. Gemini key 2
        |      4. Gemini key 3
        |      5. Self-hosted Phoenix AI Router
        |
        +--> quality/duplicate checks
        |
        +--> Binance Square OpenAPI
```

**Important:** GitHub Actions does not call Binance. It only wakes/triggers the Render service. The Binance Square request therefore originates from Render.

This is specifically intended to test whether the HTTP 451 received from GitHub Actions is caused by the GitHub runner network/location.

## Free deployment

Render is configured as a **Free Web Service**, not a Render Cron Job. The daily scheduler remains GitHub Actions, which only sends an authenticated HTTPS request to Render.

Render free services can spin down when idle. The GitHub trigger first calls `/health`, which wakes the service, waits for HTTP 200, and then calls `/run`.

### Render setup

1. Push this repository to GitHub.
2. Render → **New → Blueprint** → select the repository.
3. Render reads `render.yaml` and creates a **Free Web Service**.
4. In Render Environment, configure:

Required:

- `AGENT_TRIGGER_TOKEN` — random long secret used only to authorize `/run`
- `BINANCE_SQUARE_OPENAPI_KEY` — your Binance Square OpenAPI posting key

AI fallback keys (keep all you have; none were removed):

- `OPENAI_API_KEY`
- `GEMINI_API_KEY_1`
- `GEMINI_API_KEY_2`
- `GEMINI_API_KEY_3`
- `SELF_HOSTED_API_KEY`

Optional models/configuration:

- `OPENAI_MODEL` — `gpt-5-mini`
- `GEMINI_MODEL` — `gemini-2.5-flash`
- `SELF_HOSTED_API_URL` — Phoenix AI Router URL
- `SELF_HOSTED_MODEL` — `deepseek-v4-flash`
- `POST_MIN_WORDS` — `90`
- `POST_MAX_WORDS` — `230`

### GitHub scheduler secrets

In GitHub → Settings → Secrets and variables → Actions, add:

- `RENDER_AGENT_URL` — for example `https://your-service.onrender.com`
- `AGENT_TRIGGER_TOKEN` — exactly the same value as the Render secret

The scheduler is configured for **07:00 UTC / 08:00 Nigeria time (WAT)**.

### First test

After Render finishes deploying:

1. Open `https://your-service.onrender.com/health`.
2. It should return `{"status":"ok"}`.
3. In GitHub Actions run **Trigger Render Binance Agent** manually.
4. Watch the Render logs.

The Render log begins with network diagnostics such as:

```text
=== NETWORK DIAGNOSTICS ===
Outbound public IP: ...
api.binance.com: HTTP ...
www.binance.com: HTTP ...
=== END NETWORK DIAGNOSTICS ===
```

If GitHub gets HTTP 451 but Render successfully reaches/publishes to Square, the runner network was a likely factor.

If Render also receives HTTP 451, do not immediately buy a dedicated IP. That points toward a Binance geographic/network/API eligibility issue and should be investigated from the actual response.

## AI fallback chain

The existing multi-provider system is preserved:

1. OpenAI
2. Gemini API key 1
3. Gemini API key 2
4. Gemini API key 3
5. Self-hosted Phoenix AI Router

A provider failure, quota error, timeout, or invalid response moves to the next configured provider.

You can therefore use only Gemini, only self-hosted, OpenAI + Gemini, or all providers together.

## Binance Square OpenAPI

The agent continues using the Binance Square OpenAPI publisher. The Square key is separate from normal Binance trading/withdrawal credentials.

Never put Binance trading keys, wallet private keys, or API secrets in source code.

## History persistence

Render free services have ephemeral local storage. The agent therefore supports optional GitHub Contents API persistence:

- `GITHUB_AGENT_TOKEN`
- `GITHUB_AGENT_REPO` (default in `render.yaml`: `Phoenix1185/binance-ai-square-agent`)

If configured, the latest `data/history.json` is committed back to the repository after a successful post. This keeps duplicate detection and the GitHub Pages dashboard history available across Render restarts.

For the GitHub token, use a narrowly scoped fine-grained token that can write only the repository contents needed by this agent. Do not use an account password or Binance credential.

## Endpoints

- `GET /` — service information
- `GET /health` — health check
- `POST /run` — authenticated agent execution

Authentication for `/run` uses the `X-Agent-Trigger-Token` header.

## Local test

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export BINANCE_SQUARE_OPENAPI_KEY="YOUR_SQUARE_KEY"
export AGENT_TRIGGER_TOKEN="YOUR_RANDOM_TRIGGER_SECRET"
export SELF_HOSTED_API_KEY="YOUR_ROUTER_KEY"

python src/agent.py --dry-run
python server.py
```

## Safety/content behavior

The agent is designed for original informational content. It does not automate likes, follows, comments, views, multiple accounts, or artificial engagement. It also rejects basic scam/guaranteed-profit language and checks recent posts for excessive similarity.
