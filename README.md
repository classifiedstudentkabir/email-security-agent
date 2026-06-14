<<<<<<< HEAD
# Local AI Email Security Agent

A fully local, privacy-first email security pipeline that reads your inbox,
classifies each email using a small language model running on your own machine
via [Ollama](https://ollama.com/), and displays results in a rich terminal UI —
**no cloud services, no API keys, no data ever leaving your machine.**

Designed for low-end hardware: runs comfortably on a laptop with 8 GB RAM and
an NVIDIA 940MX (or CPU-only). Default model: **qwen2.5:1.5b**.

---

## What It Does

- Connects to any IMAP mailbox (Gmail, Outlook, Yahoo, self-hosted)
- Fetches unread emails and parses sender, subject, and body
- Sends each email to a local Ollama model for classification
- Returns: **category**, **priority**, **summary**, **recommended action**, and **confidence**
- Displays results in a colour-coded terminal table via Rich
- Supports continuous watch mode, one-shot scan, offline fixture testing, and health checks

---

## Requirements

- Python 3.11 or later
- [Ollama](https://ollama.com/) installed and running locally
- A local model pulled (default: `qwen2.5:1.5b`)
- For live email scanning: IMAP access to your mailbox

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourorg/email-security-agent.git
cd email-security-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Copy the example environment file

```bash
cp .env.example .env
```

### 5. Edit `.env` with your settings

Open `.env` in any editor and set your IMAP credentials and model preferences.
See the [Configuration](#configuration) section below for details.

---

## Gmail App Password Setup

Gmail requires an **App Password** — your real Gmail password will not work
for IMAP access when 2FA is enabled (which is required).

1. Go to your Google Account: [myaccount.google.com](https://myaccount.google.com)
2. Navigate to **Security** → **2-Step Verification** and ensure it is enabled
3. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Under "Select app", choose **Mail**
5. Under "Select device", choose **Windows Computer** (or your OS)
6. Click **Generate**
7. Copy the 16-character password (spaces are optional)
8. In your `.env` file, set:
   ```
   IMAP_USERNAME=your_email@gmail.com
   IMAP_PASSWORD=abcd efgh ijkl mnop
   ```

> ⚠️ **Never use your real Gmail password here.** App Passwords are separate
> credentials that can be revoked at any time from your Google Account.

---

## Verify Ollama Is Running

Before running the agent, confirm Ollama is running and your model is available:

```bash
python scripts/check_ollama.py
```

Expected output when everything is ready:

```
Ollama Health Check
========================================
  URL:   http://localhost:11434
  Model: qwen2.5:1.5b
========================================
✅  Ollama is running at http://localhost:11434
✅  Model 'qwen2.5:1.5b' is available
========================================
✅  All checks passed — ready to run.
```

If the model is not pulled yet:

```bash
ollama pull qwen2.5:1.5b
```

---

## Usage

### Test without IMAP (recommended first run)

Runs the full pipeline against 5 built-in fixture emails — no inbox connection needed.

```bash
python main.py --test
```

### Scan inbox once

```bash
python main.py --scan
```

### Scan continuously

Scans every `SCAN_INTERVAL_SECONDS` (default: 60 seconds). Press `Ctrl+C` to stop.

```bash
python main.py --scan --watch
```

### Check Ollama health

```bash
python main.py --check
```

---

## Running Tests

Install development dependencies first:

```bash
pip install -r requirements-dev.txt
```

Run all tests with coverage:

```bash
pytest tests/ -v --cov=src/email_agent --cov-report=term-missing
```

All tests run fully offline — no Ollama instance or live inbox is required.

---

## Configuration

All configuration lives in `.env`. Copy `.env.example` to get started.

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | Model to use for classification |
| `OLLAMA_TIMEOUT` | `30` | Seconds per request |
| `OLLAMA_MAX_RETRIES` | `3` | Retry attempts on failure |
| `IMAP_HOST` | `imap.gmail.com` | IMAP server hostname |
| `IMAP_PORT` | `993` | IMAP SSL port |
| `IMAP_USERNAME` | *(required)* | Your email address |
| `IMAP_PASSWORD` | *(required)* | App password / email password |
| `IMAP_MAILBOX` | `INBOX` | Mailbox folder to monitor |
| `IMAP_MARK_AS_READ` | `false` | Mark fetched emails as read |
| `EMAIL_BODY_MAX_CHARS` | `1200` | Body chars sent to model |
| `SCAN_INTERVAL_SECONDS` | `60` | Seconds between watch-mode scans |
| `MAX_EMAILS_PER_SCAN` | `10` | Max emails per scan cycle |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### Changing the Model

Edit `.env`:

```
OLLAMA_MODEL=qwen2.5:3b
```

No code changes required. Pull the model first with `ollama pull qwen2.5:3b`.

---

## Project Structure

```
email-security-agent/
├── src/
│   └── email_agent/
│       ├── __init__.py
│       ├── config.py          # All settings via pydantic-settings + .env
│       ├── models.py          # Pydantic models: EmailMessage, ClassificationResult
│       ├── imap_reader.py     # IMAP connection, fetch unread emails
│       ├── parser.py          # Parse raw RFC 2822 → EmailMessage
│       ├── classifier.py      # Ollama API call + JSON parsing + retry
│       ├── display.py         # Rich terminal output
│       └── pipeline.py        # Orchestrates all steps
├── tests/
│   ├── conftest.py
│   ├── test_parser.py
│   ├── test_classifier.py
│   ├── test_pipeline.py
│   └── fixtures/              # 5 sample .eml files for offline testing
├── scripts/
│   └── check_ollama.py        # Verify Ollama is running + model is available
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── main.py
```

---

## Roadmap

| Phase | Description |
|-------|-------------|
| **Phase 1** *(current)* | Core pipeline — fetch, parse, classify, display |
| **Phase 2** | SQLite storage — persist classifications, deduplication, `--history` CLI |
| **Phase 3** | FastAPI backend — REST API for scan, status, and results |
| **Phase 4** | Docker — containerised agent + Ollama service via docker-compose |
| **Phase 5** | Web Dashboard — React or HTML/JS frontend served by FastAPI |
| **Phase 6** | Multi-Agent — async task runners per pipeline stage |
| **Phase 7** | Advanced Analysis — PDF attachment scanning, URL + VirusTotal checks |

---

## Security Notes

- **No credentials are hardcoded.** All secrets live in `.env` (git-ignored).
- **No data leaves your machine.** Ollama runs entirely locally.
- **App Passwords can be revoked** at any time from your Google Account without changing your real password.
- The classifier always returns a result — it never crashes on a bad model response.

---

## License

MIT
=======
# email-security-agent
>>>>>>> 63f2cc8304c7aed06594731bb3e87e3c59558a27
