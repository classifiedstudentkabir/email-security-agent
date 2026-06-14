# ⚙️ Configuration Reference Guide

The Local AI Email Security Agent is configured entirely using environment variables. When starting, the application reads these settings from a `.env` file in the project root folder.

Below is a detailed breakdown of every configuration variable available.

---

## 🤖 Ollama Settings

These variables control how the agent communicates with your local Ollama AI model engine.

### `OLLAMA_BASE_URL`
* **Description:** The URL of the running Ollama API service on your machine.
* **Default Value:** `http://localhost:11434`
* **Docker Behavior:** When running inside Docker via `Run.bat` or `docker compose up`, the container overrides this variable automatically to `http://host.docker.internal:11434` to communicate with the host system. You do not need to modify this manually for Docker.
* **Example:** `OLLAMA_BASE_URL=http://127.0.0.1:11434`
* **Recommended Value:** `http://localhost:11434` (standard local installations)

### `OLLAMA_MODEL`
* **Description:** The name of the LLM pulled in Ollama that will classify emails.
* **Default Value:** `qwen2.5:1.5b`
* **Examples:** `qwen2.5:3b`, `llama3.2:3b`, `mistral:7b`
* **Recommended Values:**
  - `qwen2.5:1.5b` (Recommended for low-end CPUs and machines with 8 GB RAM. Fast and uses ~1 GB RAM.)
  - `qwen2.5:3b` / `llama3.2:3b` (Best trade-off of speed and accuracy. Runs fine on mid-range machines. Uses ~3 GB RAM.)
  - `qwen2.5:7b` (High accuracy. Recommended if you have an external GPU and 16 GB+ RAM.)

### `OLLAMA_TIMEOUT`
* **Description:** The maximum time in seconds the agent waits for Ollama to return a classification before timing out.
* **Default Value:** `30`
* **Examples:** `60`, `90`
* **Recommended Values:**
  - `30` seconds if running a lightweight model (1.5b/3b) or using GPU acceleration.
  - `60`–`120` seconds if running a larger model (7b) on a slow CPU or older laptop.

### `OLLAMA_MAX_RETRIES`
* **Description:** The number of times to retry a failed HTTP request to Ollama before returning a safe fallback classification. Uses exponential backoff (2s, 4s, 8s).
* **Default Value:** `3`
* **Examples:** `1` (for fast debugging), `5` (highly robust)
* **Recommended Value:** `3` (balance between reliability and quick response)

---

## 📬 IMAP / Email Settings

These variables configure the secure connection to your email inbox.

### `IMAP_HOST`
* **Description:** The server hostname of your email provider's IMAP service.
* **Default Value:** `imap.gmail.com`
* **Common Examples:**
  - **Gmail:** `imap.gmail.com`
  - **Outlook / Hotmail:** `imap-mail.outlook.com`
  - **Yahoo Mail:** `imap.mail.yahoo.com`
  - **Proton Mail (Bridge):** `127.0.0.1` (requires Proton Mail Bridge desktop app running)
* **Recommended Value:** Match this to your email provider.

### `IMAP_PORT`
* **Description:** The network port used to connect securely to the IMAP server.
* **Default Value:** `993` (standard IMAP over SSL/TLS)
* **Common Ports:**
  - `993` (Secure SSL/TLS - required by Gmail and almost all modern providers)
  - `143` (Non-secure plain IMAP - not recommended or supported by Gmail)
* **Recommended Value:** `993`

### `IMAP_USERNAME`
* **Description:** The email address of the account you want the agent to scan and monitor.
* **Default Value:** *(None - must be filled out)*
* **Example:** `john.doe@gmail.com`
* **Recommended Value:** Your active email address.

### `IMAP_PASSWORD`
* **Description:** The login credential for the email account.
* **Default Value:** *(None - must be filled out)*
* **Gmail Requirement:** Google blocks regular account passwords for IMAP clients. You **must** enable 2-Factor Authentication and generate a 16-character **App Password** (see the README for instructions).
* **Example:** `abcd efgh ijkl mnop` (spaces are optional)
* **Recommended Value:** Your generated 16-character App Password (Gmail) or your regular secure password (for other providers).

### `IMAP_MAILBOX`
* **Description:** The mailbox directory/label folder to scan for unread messages.
* **Default Value:** `INBOX`
* **Examples:** `INBOX`, `[Gmail]/Spam` (to scan spam folders in Gmail), `Archive`
* **Recommended Value:** `INBOX` (scans your primary inbox)

### `IMAP_MARK_AS_READ`
* **Description:** If set to `true`, the agent will mark emails as read after fetching and classifying them.
* **Default Value:** `false`
* **Recommended Value:**
  - `false` (for initial testing - so emails remain unread in your inbox for you to see)
  - `true` (once you trust the agent, to prevent processing the same emails repeatedly if they remain in your inbox)

---

## ⚙️ Pipeline Settings

These variables adjust the performance and thresholds of the processing pipeline.

### `EMAIL_BODY_MAX_CHARS`
* **Description:** The maximum number of characters from the email body sent to the AI model. Truncation prevents token overflow and maintains fast inference.
* **Default Value:** `1200`
* **Recommended Values:**
  - `800`–`1200` characters (for small 1.5b models. 1200 characters is about 300 words, enough context for security analysis).
  - `2000`–`3000` characters (if using `qwen2.5:3b` or `qwen2.5:7b` models which support larger context windows).

### `SCAN_INTERVAL_SECONDS`
* **Description:** The time in seconds the agent waits between consecutive inbox checks when running in continuous watch mode (`--watch`).
* **Default Value:** `60`
* **Recommended Values:**
  - `30`–`60` seconds (for active, real-time alert systems)
  - `300` (5 minutes - light monitoring, prevents hitting email provider rate limits)

### `MAX_EMAILS_PER_SCAN`
* **Description:** The maximum number of unread emails the agent fetches in a single scan cycle. The agent processes the most recent emails first.
* **Default Value:** `10`
* **Recommended Value:** `10`–`20` (prevents API throttling or long processing delays if your inbox suddenly receives a storm of unread messages)

---

## 📝 Logging Settings

### `LOG_LEVEL`
* **Description:** The verbosity of logs printed in the console and written to the `logs/` directory.
* **Default Value:** `INFO`
* **Available Options:**
  - `DEBUG` (Prints everything, including raw API responses and prompt structures. Use for troubleshooting.)
  - `INFO` (Standard operation logs. Shows inbox scan starts, classified email titles, and summaries.)
  - `WARNING` (Only alerts, retry attempts, and minor network anomalies.)
  - `ERROR` (Only database, IMAP, or Ollama server connection failures.)
  - `CRITICAL` (System crashes.)
* **Recommended Value:** `INFO`
