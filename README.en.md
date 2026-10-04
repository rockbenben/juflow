# JuFlow 聚流

> A feed reader for Chinese-platform bloggers

**English** · [简体中文](README.md)

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![365 Open Source Plan #007](https://img.shields.io/badge/365%20Open%20Source%20Plan-%23007-1f6feb)](https://github.com/rockbenben/365opensource)

**▶ Self-host it**: `git clone` → `docker compose up -d` → open `http://localhost` ([full steps](#quick-start))

Follow bloggers across 14 Chinese platforms — Xueqiu, Jisilu, Taoguba, WeChat Official Accounts, Zhihu, Weibo, Xiaohongshu and more — and get their new posts pushed to you in real time, in one place.

## Why this exists

RSS readers like Folo have thin support for bloggers on Chinese platforms. Many of those platforms publish no RSS at all, so reaching the content takes a scraper. JuFlow uses a layered adapter architecture (**RSS → RSSHub → custom scraper**) that picks the best available method per source, so everything you follow lands in a single inbox.

## Features

### Aggregation

- **14 platforms** — Xueqiu, Jisilu, Taoguba, EastMoney, THS, Jiuquaner, YouzhiYouxing, WeChat Official Accounts, Zhihu, Weibo, Xiaohongshu, Juejin, CSDN, V2EX
- **Subscribe by pasting a link** — paste a blogger's profile URL and the platform is detected automatically
- **Onboarding** — new accounts get a curated list of sources to subscribe to in one click
- **OPML import / export** — migrate from another reader
- **Per-source fetch interval** — anywhere from 1 minute to 1 day
- **Plugin marketplace** — community adapters, installable at runtime (admin only; the worker needs a restart to pick them up)

### Reading

- **Three-pane layout** — sidebar + article list + reading pane on desktop
- **Mobile layout** — responsive single column with bottom navigation
- **Safe rendering** — article HTML is sanitized through DOMPurify
- **Folders and tags** — colored labels to organize subscriptions
- **Favorites and read-later**
- **Title search** — fuzzy keyword matching
- **Keyboard shortcuts** — `j`/`k` to navigate, `s` to favorite, `m` to mark read, `?` for help
- **Dark / light theme** — can follow the system setting

### Real-time delivery

- **WebSocket** — live updates inside the app
- **Web Push** — browser system notifications
- **WeChat** — WeCom group bot webhook
- **Telegram** — Bot API
- **Email** — instant, hourly, or daily digest
- **Quiet hours** — configurable, with an exemption list for bloggers you don't want to miss
- **Cookie expiry alerts** — you get told when a platform credential goes stale

### Also

- **PWA** — installable, with Service Worker caching
- **Cookie management** — platform credentials stored with AES-256-GCM
- **Open API** — API-key auth via the `X-API-Key` header, for third-party clients
- **Health monitoring** — per-adapter success rate, latency, and error tracking
- **Internationalized** — English / 简体中文

## Quick start

### Prerequisites

- Docker + Docker Compose
- Git

### Deploy

```bash
# 1. Clone
git clone https://github.com/rockbenben/juflow.git
cd juflow

# 2. Configure
cp .env.example .env
# Edit .env — you MUST change:
#   - SECRET_KEY       (any random string; startup warns if left at the default)
#   - POSTGRES_PASSWORD (use a strong one)

# 3. Start everything (health checks wait for dependencies; migrations run automatically)
docker compose up -d

# 4. Open
# http://localhost
# After registering you'll get the recommended-sources page — subscribe in one click and you're reading.
```

### Services

| Service       | Port | What it does                                                              |
| ------------- | ---- | ------------------------------------------------------------------------- |
| frontend      | 80   | Nginx serving the SPA; reverse-proxies `/api`, `/ws`, `/docs`, `/openapi.json`, `/health`  |
| backend       | 8000 | FastAPI API + WebSocket (runs DB migrations on startup)                    |
| celery-worker | —    | Fetch and notification jobs                                               |
| celery-beat   | —    | Scheduler                                                                 |
| postgres      | —    | Database (container-internal; dev exposes 5432 via the override file)     |
| redis         | —    | Task queue + cache (container-internal; dev exposes 6379)                 |
| rsshub        | —    | RSS proxy (dev exposes 1200)                                              |

> Dev ports come from `docker-compose.override.yml`, which Compose loads automatically. For production, delete that file or run `docker compose -f docker-compose.yml up -d`.

## Using it

### Adding a subscription

1. Sign in, then click **+ Add subscription** at the bottom of the sidebar
2. Paste the blogger's profile URL, for example:
   - `https://xueqiu.com/u/1234567890` (Xueqiu)
   - `https://blog.csdn.net/username` (CSDN)
   - `https://www.zhihu.com/people/someone` (Zhihu)
   - `半佛仙人` (WeChat Official Account — type the name directly)
3. Pick a fetch interval and add it

### Setting up notifications

Under **Settings → Notifications**:

- Choose the default channel
- WeChat: paste a WeCom group-bot webhook URL
- Telegram: paste the bot token and chat ID
- Email: enter the destination address
- Configure quiet hours

### Managing cookies

Some platforms (Jisilu, Taoguba, THS, Jiuquaner, YouzhiYouxing) only serve content to a signed-in session:

1. Sign in to the platform in your browser
2. Open DevTools (F12) → Application → Cookies
3. Copy the cookies
4. Go to **Settings → Cookies**, paste and save

Cookies are stored encrypted with AES-256-GCM. When one expires you get a WebSocket push telling you to refresh it.

> **Worth knowing**: cookies are encrypted at rest, but the server administrator holds the key and can decrypt them. Only deploy this on a server you control or fully trust.

### Installing plugins

Community adapter plugins install under **Settings → Plugins** (admin only — that's whoever registered first):

- Paste the plugin's Git repository URL and click install
- Or upload a zip
- The API picks it up immediately; the background fetcher needs a worker restart (`docker compose restart celery-worker`)

> **Worth knowing**: plugins execute Python on your server, with no sandbox. Install only plugins you've read or trust.

### Using the API

Third-party clients authenticate with an API key:

1. Go to **Settings → API** and generate a key
2. Send it in the `X-API-Key` header (URL parameters are deliberately not accepted, so keys don't leak into logs)
3. API docs live at `http://localhost/docs`

## Development

### Running locally

```bash
# Start the backing services (the override file exposes their ports on localhost)
docker compose up postgres redis rsshub -d

# Backend (no .env needed — config.py defaults point at localhost)
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Celery worker (new terminal, inside backend/)
celery -A app.tasks.celery_app worker --loglevel=info

# Celery beat (new terminal, inside backend/)
celery -A app.tasks.celery_app beat --loglevel=info

# Frontend (vite.config.ts already proxies /api and /ws to localhost:8000)
cd frontend
npm install
npm run dev
```

> **Note**: the hostnames in `.env.example` (`postgres`, `redis`) are for container-to-container traffic. Don't copy `.env` for local development — the defaults in `config.py` (`localhost`) are what you want.

### More

Writing adapter plugins — the three base classes, selector syntax and manifest format — is in **[CONTRIBUTING.en.md](CONTRIBUTING.en.md)**.

## Environment variables

| Variable                      | What it is                          | Required                                  |
| ----------------------------- | ----------------------------------- | ----------------------------------------- |
| `SECRET_KEY`                  | JWT signing key (startup warns if unset) | Yes                                   |
| `POSTGRES_PASSWORD`           | Database password                   | Yes                                       |
| `DATABASE_URL`                | Database connection string          | Yes                                       |
| `REDIS_URL`                   | Redis connection string             | Yes                                       |
| `RSSHUB_URL`                  | RSSHub instance address             | Yes                                       |
| `CORS_ORIGINS`                | Allowed frontend origins (comma-separated) | No (defaults to localhost)         |
| `VAPID_PRIVATE_KEY`           | Web Push private key                | No (needed for Web Push)                  |
| `VAPID_PUBLIC_KEY`            | Web Push public key                 | No (needed for Web Push)                  |
| `SMTP_HOST`                   | Mail server                         | No (needed for email notifications)       |
| `SMTP_PORT`                   | Mail port                           | No                                        |
| `SMTP_USER`                   | Mail account                        | No                                        |
| `SMTP_PASSWORD`               | Mail password                       | No                                        |
| `SMTP_FROM`                   | From address                        | No (defaults to `noreply@juflow.app`)     |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime in minutes             | No (defaults to 1440 — 24 hours)          |
| `VAPID_CLAIM_EMAIL`           | Web Push contact address            | No (defaults to `admin@example.com`)      |

The full template is in `.env.example`.

## Security

- **XSS** — article HTML sanitized with DOMPurify; email and Telegram notification content is HTML-escaped
- **XXE** — OPML import goes through defusedxml
- **SSRF** — subscription URLs pointing at private ranges or cloud metadata endpoints are rejected
- **Input validation** — registration requires a valid email, a password of 6+ characters, and a 2–100 character username; search terms escape LIKE wildcards
- **Auth rate limiting** — 10 logins/min, 5 registrations/min (slowapi)
- **Plugin isolation** — admin-only installation, alphanumeric plugin names, zip path-traversal guarded
- **API keys** — header only, never accepted as a URL parameter
- **Cookie encryption** — AES-256-GCM, isolated per user

Two things worth deciding on before you deploy:

- **Platform cookies are decryptable by whoever runs the server.** Some sources (Jisilu, Taoguba, THS, Jiuquaner, YouzhiYouxing) can only be fetched while logged in, so you paste that platform's cookies into JuFlow. They're encrypted at rest, but the server administrator holds the key. **Only deploy this on a server you control or fully trust.**
- **Plugins run Python on your server.** The adapter marketplace installs and executes third-party code in the worker process — there is no sandbox. Install only plugins you've read or trust.

## About the 365 Open Source Plan

Project **#007** of the [365 Open Source Plan](https://github.com/rockbenben/365opensource) — one person + AI, 300+ open-source projects in a year. [Submit your idea →](https://365.aishort.top/) · [Discord](https://discord.gg/PZTQfJ4GjX) · [Telegram](https://t.me/aishort_top)
