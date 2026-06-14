# Local AI Email Security Agent — Technical Architecture

This document provides a deep dive into the system architecture, component layout, and data flow of the Local AI Email Security Agent. It is written for developers, contributors, and administrators.

---

## 📂 Folder Structure

```
email-security-agent/
├── src/
│   └── email_agent/
│       ├── __init__.py          # Package initialization & public API exports
│       ├── config.py            # Configuration management (Pydantic Settings & env loading)
│       ├── models.py            # Core Pydantic data models (contracts between components)
│       ├── imap_reader.py       # IMAP network client for fetching unread messages
│       ├── parser.py            # Email parser converting raw RFC 2822 bytes to data objects
│       ├── classifier.py        # Ollama REST client, prompt engineering, and JSON repair
│       ├── display.py           # Terminal interface renderer using the Rich library
│       └── pipeline.py          # Pipeline orchestrator wiring components together
├── tests/
│   ├── conftest.py              # Pytest setup and mock fixtures
│   ├── test_parser.py           # Unit tests for the parser module
│   ├── test_classifier.py       # Unit/mock tests for the Ollama integration
│   ├── test_pipeline.py         # End-to-end pipeline integration tests
│   └── fixtures/                # Raw email test files (.eml)
├── scripts/
│   └── check_ollama.py          # Standalone python script for checking local Ollama health
├── Run.bat                      # Windows verification and startup script
├── Stop.bat                     # Windows Docker Compose teardown script
├── Check.bat                    # Windows detailed environment health check script
├── Dockerfile                   # Docker image definition (Python 3.13-slim based)
├── docker-compose.yml           # Multi-container and networking layout
├── requirements.txt             # Production dependencies
└── main.py                      # Application command-line entrypoint
```

---

## 🔌 Component Overview

The application is structured into decoupled, single-responsibility components to allow scaling and database/web dashboard integrations:

1. **Config (`config.py`)**: Loads environment variables from the `.env` file or host shell using Pydantic Settings. Includes default configurations for timeouts, scan intervals, limits, and logging.
2. **Models (`models.py`)**: Defines Pydantic data structures. The key structures are `EmailMessage` (sender, subject, body, date) and `ClassificationResult` (category, priority, summary, recommended action, confidence, model info).
3. **IMAP Reader (`imap_reader.py`)**: Establishes secure SSL connection to the IMAP mail server, searches the specified folder (usually `INBOX`) for unread emails, and fetches their raw body bytes.
4. **Parser (`parser.py`)**: Parses standard RFC 2822 email headers and body using the Python standard library `email` package. Extracts plaintext, decodes headers, and handles multipart encodings.
5. **Classifier (`classifier.py`)**: Formulates the prompt with strict output instructions, contacts the local Ollama API via HTTP request, extracts the classification JSON, and falls back to a safe result on parser failure.
6. **Display (`display.py`)**: A presentation helper using the `rich` library. Draws tables, panels, custom progress/confidence bars, and logs output.
7. **Pipeline (`pipeline.py`)**: The conductor of the system. Runs loops for continuous monitoring, fetches emails, runs them through the parser and classifier, and pushes them to display.

---

## 📊 Data Flow Diagram

```
 [IMAP Server]
       │  (Fetch raw RFC 2822 bytes)
       ▼
 [IMAP Reader] ─────► returns: raw bytes
       │
       ▼
 [Email Parser] ────► returns: EmailMessage (Pydantic model)
       │
       ▼
 [Classifier]   ─────► constructs: system + user prompt with truncated body
       │               Sends HTTP POST /api/generate
       ▼
 [Ollama Engine] ───► returns: JSON string response
       │
       ▼
 [JSON Repair]  ─────► parses / extracts JSON block or applies fallback defaults
       │
       ▼
 [Display UI]   ─────► renders: Rich terminal panels & logs to console
```

---

## 🐋 Docker Integration Flow

Running inside a container introduces isolated network boundaries. The system manages this with the following architecture:

```
┌──────────────────────────────────────┐     ┌────────────────────────────────┐
│           DOCKER CONTAINER           │     │          HOST MACHINE          │
│                                      │     │                                │
│   ┌──────────────┐                   │     │   ┌────────────────────────┐   │
│   │ Email Agent  │                   │     │   │     Ollama Server      │   │
│   │              │                   │     │   │                        │   │
│   │ Configures:  │                   │     │   │ listens:               │   │
│   │ OLLAMA_BASE_ │                   │     │   │ http://127.0.0.1:11434 │   │
│   │ URL to       │                   │     │   └───────────▲────────────┘   │
│   │ http://host. │                   │     │               │                │
│   │ docker.      │────────────────────────►│  (Routes via loopback bridge)  │
│   │ internal     │                   │     │                                │
│   └──────────────┘                   │     └────────────────────────────────┘
└──────────────────────────────────────┘
```

- **Linux vs Windows/macOS:** On Windows and macOS, Docker Desktop automatically configures routing for `host.docker.internal` back to the host machine. On Linux, host routing requires appending `extra_hosts` mappings in the Compose configuration.
- **Data Persistence:** Logs are written to `/app/logs` inside the container, which is mounted to `./logs` on the host machine using a Docker bind mount to persist information across runs.

---

## 📬 IMAP Retrieval Flow

```
1. Connect securely via IMAP over SSL (port 993) to the configured IMAP Host.
2. Log in using the Username (email) and Password/App Password.
3. Select the target mailbox (default: 'INBOX').
4. Search for UNREAD messages.
5. Retrieve up to MAX_EMAILS_PER_SCAN (ordered from newest to oldest).
6. Fetch the raw RFC 2822 body of selected messages.
7. Parse the headers (From, Subject, Date) and extract the plain-text body.
8. If IMAP_MARK_AS_READ is set to true, mark processed emails as read.
9. Close connection and logout cleanly.
```

---

## 🤖 Ollama Classification Flow

To work reliably with small, locally run LLMs (e.g., `qwen2.5:1.5b`), the classification engine utilizes a highly defensive structure:

```
1. Prompt Construction
   - System Prompt: Explains the classification task, sets the 8 valid categories, 
     the 4 priorities, and outlines the target JSON structure.
   - User Prompt: Injects the Sender, Subject, and a truncated Email Body 
     (limited to EMAIL_BODY_MAX_CHARS to fit token context windows).

2. HTTP Request
   - Send an HTTP POST request to `{OLLAMA_BASE_URL}/api/generate`.
   - Set request options with raw JSON payload and format output parameter.

3. Failure Mitigation & Retries
   - If a connection error occurs, retry the request up to OLLAMA_MAX_RETRIES 
     with exponential backoff (2s, 4s, 8s).
   - If the request times out or exhausts retries, capture the error.

4. Parsing & JSON Repair
   - If the response is valid JSON, validate it against the Pydantic schema.
   - If the response is wrapped in text or has slight formatting issues, 
     use regex parsing to extract the JSON block.
   - If parsing completely fails, log the anomaly and return a fallback model response:
     { Category: "General Inquiry", Priority: "LOW", Confidence: 0 }
```

---

## 🗺️ Future Roadmap

- **Phase 2 — Persistence:** Store email details, categories, priorities, and confidence metrics in a local SQLite database (`aiosqlite`) to avoid re-classifying emails.
- **Phase 3 — REST API:** Build a FastAPI web server exposing endpoints to fetch classification logs, trigger manually, and view analytics.
- **Phase 4 — Web Dashboard:** Render a modern, beautiful React or HTML5 browser dashboard reading from the FastAPI backend.
- **Phase 5 — Automated Actions:** Add configurable actions (e.g. automatically archive spam, move phishing to junk label, send notifications via Telegram Webhook).
