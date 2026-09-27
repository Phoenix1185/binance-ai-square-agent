# Binance AI Square Agent

Automatically researches public crypto data, generates an original Binance Square post, validates it, and publishes it once per day through the Binance Square OpenAPI.

## Architecture

```text
GitHub Actions (daily scheduler and history sync)
          |
          | authenticated HTTPS only
          v
Render Free Web Service (Frankfurt)
          |
          +--> Binance market/news research
          +--> OpenAI -> Gemini 1 -> Gemini 2 -> Gemini 3 -> self-hosted AI fallback
          +--> quality and duplicate checks
          +--> Binance Square publishing
```

The Binance request is made by Render, not by the GitHub-hosted runner. This provides a useful comparison when GitHub Actions receives Binance HTTP 451 responses.

## Live dashboard and AI router

- GitHub Pages dashboard: <https://phoenix1185.github.io/binance-ai-square-agent/>
- Phoenix AI Router API: <https://concerned-swordfish-suhailtechlnfo-01fd2de0.koyeb.app/>
- Phoenix AI Router docs: <https://concerned-swordfish-suhailtechlnfo-01fd2de0.koyeb.app/docs>

GitHub Pages is static. It does not contain secrets or execute the agent.

## AI fallback chain

Providers are attempted independently in this order:

1. OpenAI — `OPENAI_API_KEY`
2. Gemini key 1 — `GEMINI_API_KEY_1`
3. Gemini key 2 — `GEMINI_API_KEY_2`
4. Gemini key 3 — `GEMINI_API_KEY_3`
5. Self-hosted Phoenix AI Router — `SELF_HOSTED_API_KEY`

Missing credentials are skipped. Provider errors, timeouts, quota failures, and invalid responses advance to the next configured provider. A self-hosted-only setup therefore works without OpenAI or Gemini credentials.

## Render Free Web Service

The included `render.yaml` creates a **Free Web Service**, not a paid Render Cron Job. The service runs `python src/web.py`, binds to Render's `$PORT`, and exposes:

- `GET /health` — public health check
- `POST /run` — authenticated agent execution
- `GET /history` — authenticated history read
- `POST /sync-history` — authenticated history sync from GitHub Actions

### Create the service

1. Push this repository to GitHub.
2. In Render choose **New → Web Service**.
3. Choose **Public Git Repository**.
4. Enter: <https://github.com/Phoenix1185/binance-ai-square-agent>
5. Use the `main` branch and let Render read `render.yaml`.
6. The service should use the Frankfurt region and Free plan.

The Render start command is:

```text
python src/web.py
```

### Render environment variables

Required:

- `AGENT_TRIGGER_TOKEN` — generate a long random value, for example with `openssl rand -hex 32`
- `BINANCE_SQUARE_OPENAPI_KEY` — the Binance Square posting key

At least one AI provider is required:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY_1`
- `GEMINI_API_KEY_2`
- `GEMINI_API_KEY_3`
- `SELF_HOSTED_API_KEY`

Optional defaults are already included in `render.yaml`:

- `OPENAI_MODEL` — `gpt-5-mini`
- `GEMINI_MODEL` — `gemini-2.5-flash`
- `SELF_HOSTED_API_URL` — Phoenix AI Router URL
- `SELF_HOSTED_MODEL` — `deepseek-v4-flash`
- `POST_MIN_WORDS` — `90`
- `POST_MAX_WORDS` — `230`

Never commit secret values to source control.

## GitHub Actions secrets

After the Render service is deployed, copy its public URL, such as:

```text
https://binance-ai-square-agent.onrender.com
```

Add these repository secrets under **Settings → Secrets and variables → Actions**:

- `RENDER_AGENT_URL` — the Render URL without a trailing slash
- `AGENT_TRIGGER_TOKEN` — exactly the same value configured in Render

The daily workflow at `07:00 UTC` first synchronizes the GitHub history to Render, calls the authenticated `/run` endpoint, then retrieves the updated history and commits it back to GitHub. The workflow does not call Binance directly.

Run **Trigger Binance AI Agent** manually with `dry_run=true` before enabling the first live post.

## HTTP 451 diagnostics

Every agent run prints:

```text
=== NETWORK DIAGNOSTICS ===
Outbound public IP: ...
api.binance.com: HTTP ...
www.binance.com: HTTP ...
=== END NETWORK DIAGNOSTICS ===
```

If GitHub Actions receives HTTP 451 but Render reaches Binance normally, the GitHub runner network/location is likely the factor. If Render also receives HTTP 451, investigate Binance geographic, network, or API eligibility restrictions; changing hosting region is not guaranteed to resolve it.

## Local test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export BINANCE_SQUARE_OPENAPI_KEY="YOUR_SQUARE_KEY"
export AGENT_TRIGGER_TOKEN="YOUR_RANDOM_TRIGGER_SECRET"
export SELF_HOSTED_API_KEY="YOUR_ROUTER_KEY"

python src/agent.py --dry-run
python src/web.py
```

Then check `http://localhost:10000/health`.

## Safety

The agent creates original informational content. It does not automate likes, follows, comments, views, multiple accounts, or artificial engagement. It rejects basic scam and guaranteed-profit language and checks recent posts for excessive similarity.

The Binance Square key is separate from normal Binance trading, withdrawal, or wallet credentials.
