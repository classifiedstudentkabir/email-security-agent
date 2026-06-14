# 📧 Local AI Email Security Agent

> **Privacy-first email security powered by local AI — 100% private, runs entirely on your own computer, with no API keys or cloud service required.**

Welcome! The **Local AI Email Security Agent** is a tool that monitors your email inbox (like Gmail) for suspicious messages, security threats, phishing attempts, and junk emails. It uses a small, smart artificial intelligence (AI) model running locally on your hardware to read and classify each email. Because it is completely local, **none of your email content or password data ever leaves your computer.**

This project is optimized to run on normal everyday computers (even standard laptops with 8 GB of RAM and standard CPUs).

---

## 🌟 Features

- 🔒 **100% Private & Secure:** Your email messages and login credentials are saved only on your local machine. No data is sent to OpenAI, Google, or any other cloud provider.
- 🤖 **Local AI Classification:** Uses [Ollama](https://ollama.com/) to run lightweight models (such as `qwen2.5:1.5b`) directly on your machine.
- 📬 **Real-time Monitoring:** Works with Gmail, Outlook, Yahoo, or any standard email provider that supports IMAP.
- 🏷️ **Intelligent Categorization:** Automatically classifies every incoming email into one of 8 distinct security categories:
  - **Phishing:** Fake emails designed to steal passwords, links to malicious sites, or social engineering.
  - **SQL Injection:** Emails containing code snippets aimed at attacking databases.
  - **XSS (Cross-Site Scripting):** Emails containing malicious scripts designed to execute in a browser.
  - **Vulnerability Disclosure:** Security researchers or automated tools reporting security flaws.
  - **Bug Report:** General software bug reports.
  - **Critical Security Alert:** Account alerts, password reset requests, or login notifications.
  - **Spam:** Commercial advertisements and unsolicited junk mail.
  - **General Inquiry:** Regular business, personal, or administrative communications.
- 🎯 **Priority & Actions:** Assigns a clear priority (**LOW**, **MEDIUM**, **HIGH**, or **CRITICAL**) to each email, generates a quick summary, and recommends a specific action (e.g. "Ignore", "Review immediately", "Delete").
- 📊 **Beautiful Terminal UI:** Displays results in a clean, color-coded dashboard directly in your command line window.
- 🐳 **One-Click Container Setup:** Fully dockerized so you don't have to deal with installing Python, packages, or setting up complex software environments.

---

## 🛠️ Prerequisites

Before starting, you will need:
1. **Windows 10 or 11** (though it also runs on macOS/Linux).
2. **An email account** (Gmail, Outlook, Yahoo, etc.) with **IMAP enabled** and an **App Password** created.

---

## 🚀 Quick Start (Recommended & Easiest)

Follow these 5 simple steps to get the agent running on your computer.

### Step 1: Install Docker Desktop
Docker is a software that lets you run applications in isolated virtual "containers" without messing up your computer's regular settings. If you've never used Docker before, don't worry!
1. Download **Docker Desktop** from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
2. Run the installer and follow the instructions. If prompted, choose the default options and restart your computer if requested.
3. Open Docker Desktop once it's installed. Keep it open in the background.

### Step 2: Install Ollama
Ollama is a tool that runs artificial intelligence models directly on your computer.
1. Download **Ollama** from [ollama.com/download](https://ollama.com/download).
2. Install it like any regular program.
3. Once installed, Ollama runs in your system tray (the small icons near your clock in the bottom-right corner of Windows).

### Step 3: Pull the AI Model
We need to download the lightweight brain (AI model) that will analyze the emails.
1. Open your Windows **Terminal**, **Command Prompt**, or **PowerShell** (press the `Windows Key`, type `cmd`, and press Enter).
2. Copy and paste the following command, then press Enter:
   ```bash
   ollama pull qwen2.5:1.5b
   ```
3. Wait for the download to finish. It is about 1 GB and will download to your local machine.

### Step 4: Configure Your Environment (`.env`)
You need to tell the agent which email address to monitor and how to log in.
1. In the project folder, locate the file named `.env.example`.
2. Duplicate or copy this file, and rename the copy to exactly `.env`.
3. Open `.env` in Notepad or any other text editor.
4. Replace the following values with your own:
   - `IMAP_USERNAME=your_email@gmail.com`
   - `IMAP_PASSWORD=your_16_character_app_password`
5. Save and close the file.
> ⚠️ **IMPORTANT for Gmail users:** Do NOT use your regular email login password. Google blocks regular passwords for security. You **MUST** create a 16-character **App Password** (see the [Gmail App Password Setup](#-gmail-app-password-setup) section below).

### Step 5: Start the Agent
1. Double-click the file named `Run.bat` inside the project folder.
2. The script will automatically verify your Docker and Ollama settings.
3. Once the checks pass, it will download dependencies inside Docker and launch the agent.
4. The agent will begin monitoring your inbox!

---

## 📸 Screenshots

*Placeholder sections for visual representation of the application:*

### Docker Container Running
*(Placeholder for screenshot showing Docker Desktop dashboard with the active `email-security-agent` container)*

### Startup Verification
*(Placeholder for screenshot showing the `Run.bat` console output showing all green checkmarks for Docker, Ollama, and Configuration checks)*

### Live Classification Dashboard
*(Placeholder for screenshot showing the Rich Terminal UI with color-coded classification table and details)*

---

## 🔒 Gmail App Password Setup

If you are using Gmail, you cannot log in with your primary Google account password. You must generate an App Password.

1. Go to your Google Account Settings: [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left-hand menu.
3. Under the **"How you sign in to Google"** section, look for **2-Step Verification**.
   - If it is Off, click on it, follow the steps to turn it On, then return to the Security tab.
4. Search for or go directly to the **App Passwords** page: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
5. Enter a name for the app (e.g. "Email Security Agent") and click **Create**.
6. Google will display a **16-character password** (e.g., `abcd efgh ijkl mnop`). Copy this password.
7. Paste this exact 16-character password into your `.env` file for the `IMAP_PASSWORD` value.
8. **Enable IMAP in Gmail Settings:**
   - Open your Gmail inbox in your web browser.
   - Click the gear icon (Settings) in the top right and select **See all settings**.
   - Click on the **Forwarding and POP/IMAP** tab.
   - Scroll down to the **IMAP Access** section and select **Enable IMAP**.
   - Click **Save Changes** at the bottom of the page.

---

## ⚙️ How-To Guides

### How to Change Your Email Account
If you want to use a different email account, or switch email providers (e.g. from Gmail to Outlook):
1. Open your `.env` file in a text editor.
2. Update the `IMAP_USERNAME` and `IMAP_PASSWORD` with your new account credentials.
3. Update `IMAP_HOST` if you are using a non-Gmail provider:
   - **Outlook / Hotmail:** `imap-mail.outlook.com`
   - **Yahoo Mail:** `imap.mail.yahoo.com`
   - **Custom IMAP Server:** Enter your provider's IMAP host address.
4. Save the file and restart the agent by running `Run.bat` again.

### How to Change the AI Model
If your computer is powerful (has a GPU or 16+ GB RAM) and you want higher classification accuracy, you can use a larger AI model:
1. Open your terminal and pull the larger model, for example:
   ```bash
   ollama pull qwen2.5:3b
   ```
2. Open your `.env` file.
3. Change the line `OLLAMA_MODEL=qwen2.5:1.5b` to `OLLAMA_MODEL=qwen2.5:3b`.
4. Save the file and restart the agent. The agent will automatically load the new model on the next startup.

### How to Stop the Agent
If you want to shut down the monitoring agent:
- **If running in a command window:** Simply select the window and press `Ctrl+C` on your keyboard, or close the window.
- **To clean up Docker resources:** Double-click the file named `Stop.bat` in the project folder. This will safely stop and remove the active Docker container.

---

## 🛠️ Running Without Docker (Python Directly)

If you prefer to run the application natively in Python:
1. Ensure you have **Python 3.11 or newer** installed.
2. Open your terminal in the project folder and create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - **Windows PowerShell:** `.venv\Scripts\activate`
   - **Linux / macOS:** `source .venv/bin/activate`
4. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the offline test suite to verify:
   ```bash
   python main.py --test
   ```
6. Run the agent in scan-and-watch mode:
   ```bash
   python main.py --scan --watch
   ```

---

## 🚨 Common Issues & Troubleshooting

### ❌ Error: "IMAP authentication failed"
- **Cause:** Incorrect username or password configuration.
- **Fix:** Double-check your `.env` file. Make sure `IMAP_USERNAME` is your full email address. If using Gmail, make sure you generated an **App Password** as described above, and that **IMAP is enabled** in your Gmail settings.

### ❌ Error: "Ollama is NOT running"
- **Cause:** Ollama application is not open or configured incorrectly.
- **Fix:** Launch Ollama from your desktop or start menu. Verify that the Ollama icon is visible in your Windows taskbar. If you are using Docker and get connection issues, ensure Docker can access the host machine (on Windows/Mac this is handled automatically via `host.docker.internal`).

### ❌ Error: "Model not found" or "Model 'qwen2.5:1.5b' is NOT available"
- **Cause:** The model specified in your `.env` has not been downloaded yet.
- **Fix:** Open your terminal and run `ollama pull qwen2.5:1.5b` (or whatever model name is in your `.env` file).

### ❌ Error: "SSL: CERTIFICATE_VERIFY_FAILED"
- **Cause:** A corporate VPN, firewall, or security software is blocking the SSL connection to your email server.
- **Fix:** Try disconnecting your VPN or checking if your firewall permits outbound traffic on port 993.

---

## 📝 License

This project is licensed under the MIT License.
