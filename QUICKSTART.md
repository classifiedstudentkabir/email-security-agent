# ⚡ Quick Start Guide (5-Minute Setup)

Get the Local AI Email Security Agent up and running in less than 5 minutes.

---

## 📋 Prerequisites Checklist

Before you begin, ensure you have these installed and active:
- [ ] **Docker Desktop:** Installed and running in the background ([Download](https://www.docker.com/products/docker-desktop/))
- [ ] **Ollama:** Installed and running ([Download](https://ollama.com/))
- [ ] **Email App Password:** A 16-character login password generated for your email ([Gmail App Passwords Link](https://myaccount.google.com/apppasswords))
- [ ] **IMAP Enabled:** Active IMAP access in your email provider's settings tab

---

## 🚀 Step-by-Step Instructions

### 1. Download the AI Model
Open a command prompt (press `Win+R`, type `cmd`, hit Enter) and download the default classification model:
```bash
ollama pull qwen2.5:1.5b
```

### 2. Configure Your Environment
1. In the project directory, make a copy of `.env.example` and name it `.env`.
2. Open the `.env` file in Notepad.
3. Fill in your email account credentials:
   ```env
   IMAP_USERNAME=your_name@gmail.com
   IMAP_PASSWORD=abcd efgh ijkl mnop
   ```
4. Save and close the file.

### 3. Start the Agent
Double-click the **`Run.bat`** file in the project root.
- The startup script will verify Docker, Ollama, your `.env` file, and your model automatically.
- Once verified, the container will build and immediately begin scanning your inbox for threats.

### 4. Stop the Agent
Double-click the **`Stop.bat`** file to shut down the container and clean up Docker resources cleanly.

---

## 🛠️ Instant Troubleshooting

* **IMAP/Login Error:** Verify you are using a 16-character Google App Password (not your primary password) and that IMAP is enabled in your Gmail settings under *Settings → Forwarding and POP/IMAP*.
* **Docker/Ollama Connection Issues:** Make sure both applications are actively running in your system tray before running `Run.bat`.
* **Health Checks:** Double-click **`Check.bat`** to run a comprehensive system health report and diagnostic verification.
