# Local AI Email Security Agent

> **Privacy-first email security powered by local AI — no cloud, no API keys, no data ever leaves your machine.**

A fully local email security pipeline that connects to your inbox, classifies each email using a small language model running on your own hardware via [Ollama](https://ollama.com/), and displays results in a rich terminal UI.

Designed to run on everyday hardware: a laptop with **8 GB RAM** and a basic GPU (or CPU-only) is enough. Default model: **qwen2.5:1.5b**.

---

## Project Overview

The Local AI Email Security Agent monitors your Gmail (or any IMAP mailbox) for suspicious emails and classifies them in real time using a locally running AI model. Every email is analysed and assigned a **category**, **priority**, **summary**, **recommended action**, and **confidence score** — all computed on your machine without sending data to any external service.

It is built for security-conscious users, developers, and researchers who want AI-assisted inbox monitoring without trusting a third-party cloud provider with their email content.

---

## Features

- 📬 **IMAP email fetching** — connects to Gmail, Outlook, Yahoo, or any IMAP provider
- 🤖 **Local AI classification** — uses Ollama to run models like qwen2.5:1.5b entirely on your machine
- 🔒 **100% private** — no data ever leaves your machine; no internet required after setup
- 🏷️ **8 security categories** — Phishing, SQL Injection, XSS, Vulnerability Disclosure, Bug Report, Critical Security Alert, Spam, General Inquiry
- 🎯 **Priority scoring** — LOW / MEDIUM / HIGH / CRITICAL per email
- 📊 **Rich terminal UI** — colour-coded table with summaries and recommended actions
- ⏱️ **Watch mode** — continuous scanning at a configurable interval
- 🧪 **Offline test mode** — run against built-in fixture emails without any inbox connection
- 🩺 **Health check** — verify Ollama is running and the model is available
- 🐳 **Docker support** — run the entire agent in a container with `docker compose up`
- ⚙️ **Zero-code configuration** — everything is controlled via `.env` file

---

## Requirements

### Running with Docker (recommended)

| Requirement | Notes |
|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Windows / macOS / Linux |
| [Ollama](https://ollama.com/) | Running on your host machine |
| A pulled Ollama model | e.g. `ollama pull qwen2.5:1.5b` |
| Gmail App Password | Required for live inbox scanning |

> **No Python installation required.** Docker handles everything.

### Running without Docker (Python directly)

| Requirement | Notes |
|---|---|
| Python 3.11+ | 3.13 recommended |
| [Ollama](https://ollama.com/) | Running locally |
| A pulled Ollama model | e.g. `ollama pull qwen2.5:1.5b` |
| Gmail App Password | Required for live inbox scanning |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourorg/email-security-agent.git
cd email-security-agent
```

### 2. Copy the environment file

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**
```bash
cp .env.example .env
```

### 3. Edit `.env`

Open `.env` in any text editor and set your credentials:

```env
IMAP_USERNAME=your_email@gmail.com
IMAP_PASSWORD=your_16_char_app_password
OLLAMA_MODEL=qwen2.5:1.5b
```

See [Gmail Setup](#gmail-setup) and [Ollama Setup](#ollama-setup) below for details.

---

## Ollama Setup

Ollama runs AI models locally on your machine. It must be installed and running **before** starting the agent.

### Install Ollama

Download from [ollama.com](https://ollama.com/) and install for your OS. Ollama starts automatically on most systems.

### Pull a Model

```bash
# Fast, CPU-friendly (recommended for most users)
ollama pull qwen2.5:1.5b

# Better accuracy, still CPU-friendly (~3 GB RAM)
ollama pull qwen2.5:3b

# High accuracy (needs ~5 GB RAM or GPU)
ollama pull qwen2.5:7b

# Very high accuracy (needs ~8 GB VRAM or powerful CPU)
ollama pull mistral:7b

# Good general-purpose alternative
ollama pull llama3.2:3b
```

### Verify Ollama is Running

```bash
# Check Ollama and confirm your model is available
python main.py --check

# Or call the Ollama API directly
curl http://localhost:11434/api/tags
```

### How to Change Models

1. Pull the new model: `ollama pull qwen2.5:3b`
2. Edit `.env`:
   ```env
   OLLAMA_MODEL=qwen2.5:3b
   ```
3. Restart the agent:
   - Without Docker: re-run `python main.py --scan --watch`
   - With Docker: `docker compose restart`

No code changes required.

---

## Gmail Setup

Gmail requires an **App Password** for IMAP access. Your real Gmail password will not work.

### Step 1 — Enable 2-Factor Authentication

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left sidebar
3. Under **"How you sign in to Google"**, enable **2-Step Verification**
4. Follow the on-screen prompts to complete setup

### Step 2 — Generate an App Password

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Under **"Select app"**, choose **Mail**
3. Under **"Select device"**, choose **Windows Computer** (or your OS)
4. Click **Generate**
5. Copy the 16-character password (spaces are optional)

### Step 3 — Enable IMAP in Gmail

1. Open **Gmail** → **Settings** (gear icon) → **See all settings**
2. Click the **"Forwarding and POP/IMAP"** tab
3. Under **"IMAP access"**, select **Enable IMAP**
4. Click **Save Changes**

### Step 4 — Add Credentials to `.env`

```env
IMAP_USERNAME=your_email@gmail.com
IMAP_PASSWORD=abcd efgh ijkl mnop
```

> ⚠️ **Never use your real Gmail password here.** App Passwords are separate credentials that can be revoked at any time from your Google Account without affecting your main password.

---

## Running Without Docker

### Create a virtual environment

```bash
python -m venv .venv
```

**Windows PowerShell:**
```powershell
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Usage

```bash
# Check Ollama health and model availability
python main.py --check

# Test with built-in fixture emails (no inbox needed)
python main.py --test

# Scan inbox once
python main.py --scan

# Scan continuously (every SCAN_INTERVAL_SECONDS, default 60s)
python main.py --scan --watch
```

Press `Ctrl+C` to stop watch mode.

---

## Running With Docker

No Python installation required on your host machine. Docker handles everything.

### Prerequisites

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
2. [Ollama](https://ollama.com/) installed and running on your host machine
3. A model pulled: `ollama pull qwen2.5:1.5b`
4. `.env` file configured (see [Installation](#installation))

### Build the Image

```bash
docker compose build
```

### Start the Agent (foreground)

```bash
docker compose up
```

### Start in Background (detached mode)

```bash
docker compose up -d
```

### Follow Logs

```bash
docker compose logs -f
```

### Stop the Agent

```bash
docker compose down
```

### Run a One-Shot Scan (instead of watch mode)

```bash
docker compose run --rm email-agent python main.py --scan
```

### Run the Fixture Test (no inbox required)

```bash
docker compose run --rm email-agent python main.py --test
```

### Check Ollama Health from Inside the Container

```bash
docker compose run --rm email-agent python main.py --check
```

### Open a Shell Inside the Container

```bash
docker exec -it email-security-agent /bin/bash
```

### View Container Logs

```bash
docker logs email-security-agent
docker logs -f email-security-agent        # follow / tail
docker logs --tail 50 email-security-agent # last 50 lines
```

---

## Updating the Model

To switch to a different Ollama model:

1. Pull the new model on your host machine:
   ```bash
   ollama pull qwen2.5:3b
   ```

2. Edit `.env`:
   ```env
   OLLAMA_MODEL=qwen2.5:3b
   ```

3. Restart the agent:
   ```bash
   # Without Docker
   python main.py --scan --watch

   # With Docker
   docker compose restart
   ```

No code changes or rebuilds required.

---

## Common Errors

### ❌ Invalid credentials / Authentication failed

```
IMAP authentication failed. Check IMAP_USERNAME and IMAP_PASSWORD in .env
```

**Cause:** Wrong email address or App Password.

**Fix:**
- Confirm `IMAP_USERNAME` is your full Gmail address (e.g. `yourname@gmail.com`)
- Regenerate the App Password at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- Ensure **IMAP is enabled** in Gmail settings (Forwarding and POP/IMAP tab)
- Remove all spaces from the App Password if present, or include them — both work

---

### ❌ Ollama not reachable

```
Ollama is NOT running at http://localhost:11434
```

**Cause:** Ollama is not installed, not started, or on a different port.

**Fix:**
- Start Ollama: run `ollama serve` in a terminal (or launch the Ollama app)
- Confirm it's running: `curl http://localhost:11434/api/tags`
- If using a custom port, update `OLLAMA_BASE_URL` in `.env`

---

### ❌ Ollama not reachable from Docker

```
Ollama is NOT running at http://host.docker.internal:11434
```

**Cause:** The container cannot reach Ollama on the host machine.

**Fix (Windows / macOS):** `host.docker.internal` should work automatically with Docker Desktop. Confirm Ollama is running.

**Fix (Linux — native Docker):** Uncomment the `extra_hosts` section in `docker-compose.yml`:
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```
Then run `docker compose up`.

---

### ❌ Model not found

```
❌  Model 'qwen2.5:1.5b' is NOT available
```

**Cause:** The model has not been pulled yet.

**Fix:**
```bash
ollama pull qwen2.5:1.5b
```

---

### ❌ IMAP connection failure / SSL error

```
[SSL: CERTIFICATE_VERIFY_FAILED]
```

**Cause:** Corporate VPN, firewall, or proxy is intercepting SSL traffic.

**Fix:**
- Disconnect from VPN and retry
- Check if port 993 is accessible: `Test-NetConnection imap.gmail.com -Port 993` (Windows)
- Contact your network administrator if on a corporate network

---

### ❌ Docker build fails / pip errors

**Cause:** Network issue during `pip install` inside the container.

**Fix:**
```bash
docker compose build --no-cache
```

---

## Configuration Reference

All configuration is in `.env`. Copy `.env.example` to get started.

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL (auto-overridden for Docker) |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | Model for email classification |
| `OLLAMA_TIMEOUT` | `30` | Seconds per Ollama request |
| `OLLAMA_MAX_RETRIES` | `3` | Retry attempts on Ollama failure |
| `IMAP_HOST` | `imap.gmail.com` | IMAP server hostname |
| `IMAP_PORT` | `993` | IMAP SSL port |
| `IMAP_USERNAME` | *(required)* | Your email address |
| `IMAP_PASSWORD` | *(required)* | App Password or email password |
| `IMAP_MAILBOX` | `INBOX` | Mailbox folder to monitor |
| `IMAP_MARK_AS_READ` | `false` | Mark emails as read after scanning |
| `EMAIL_BODY_MAX_CHARS` | `1200` | Body characters sent to the model |
| `SCAN_INTERVAL_SECONDS` | `60` | Seconds between watch-mode scans |
| `MAX_EMAILS_PER_SCAN` | `10` | Max emails processed per scan cycle |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG/INFO/WARNING/ERROR) |

---

## Project Structure

```
email-security-agent/
├── src/
│   └── email_agent/
│       ├── __init__.py          # Package init and public exports
│       ├── config.py            # All settings via pydantic-settings + .env
│       ├── models.py            # Pydantic models: EmailMessage, ClassificationResult
│       ├── imap_reader.py       # IMAP connection and unread email fetching
│       ├── parser.py            # Parse raw RFC 2822 bytes → EmailMessage
│       ├── classifier.py        # Ollama API call + JSON parsing + retry logic
│       ├── display.py           # Rich terminal output (tables, colours, panels)
│       └── pipeline.py          # Orchestrates: fetch → parse → classify → display
├── tests/
│   ├── conftest.py              # Shared pytest fixtures
│   ├── test_parser.py           # Parser unit tests
│   ├── test_classifier.py       # Classifier unit tests
│   ├── test_pipeline.py         # Pipeline integration tests
│   └── fixtures/                # 5 sample .eml files for offline testing
├── scripts/
│   └── check_ollama.py          # Verify Ollama is running and model is available
├── Dockerfile                   # Docker image definition (Python 3.13 slim)
├── docker-compose.yml           # Docker Compose for one-command deployment
├── .dockerignore                # Files excluded from Docker build context
├── .env.example                 # Template for environment configuration
├── .env                         # Your local config (git-ignored, never committed)
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Production Python dependencies
├── requirements-dev.txt         # Development dependencies (pytest, etc.)
└── main.py                      # CLI entry point
```

---

## Running Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run all tests with coverage:

```bash
pytest tests/ -v --cov=src/email_agent --cov-report=term-missing
```

All tests run fully offline — no Ollama instance or live inbox connection required.

---

## Security Notes

- **No credentials are hardcoded.** All secrets live in `.env` (git-ignored).
- **No data leaves your machine.** Ollama runs entirely locally.
- **App Passwords can be revoked** at any time from your Google Account without changing your real password.
- **The classifier never crashes** on a bad model response — it always returns a safe fallback result.
- **Docker does not bake secrets into the image** — the `.env` file is excluded by `.dockerignore`.

---

## Future Roadmap

| Phase | Feature | Description |
|-------|---------|-------------|
| **Phase 1** *(current)* | Core Pipeline | Fetch → Parse → Classify → Display via terminal UI |
| **Phase 2** | SQLite Storage | Persist classifications, deduplication, `--history` CLI flag |
| **Phase 3** | FastAPI Backend | REST API for triggering scans and retrieving results |
| **Phase 4** | Web Dashboard | Browser-based UI served by FastAPI showing classification history |
| **Phase 5** | Agent Actions | Auto-label, auto-reply, or auto-archive emails based on classification |
| **Phase 6** | Notifications | Desktop / webhook / email alerts for CRITICAL priority emails |
| **Phase 7** | Multi-Agent System | Async task runners per pipeline stage for higher throughput |
| **Phase 8** | Advanced Analysis | PDF attachment scanning, URL extraction, VirusTotal integration |

---

## License

MIT
