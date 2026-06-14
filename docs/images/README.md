# 📸 Project Screenshot Placeholders & Capture Instructions

This folder is a placeholder for screenshots used in the project documentation. Please capture and save the following screenshots in this directory.

---

## 1. Docker Desktop Screenshot
* **Filename:** `docker_desktop.png` (or `.jpg`)
* **What to capture:** Open the **Docker Desktop** application on your host machine. Locate the Containers tab. Find the container named `email-security-agent` (which is started when running `Run.bat` or `docker compose up`). Ensure the status is green and showing `Running`.
* **How to capture:**
  - Press `Alt + Print Screen` (or `Windows + Shift + S`) while focusing on the Docker Desktop window.
  - Save the captured screenshot in this folder as `docker_desktop.png`.

---

## 2. Startup Verification Screenshot
* **Filename:** `startup_checks.png` (or `.jpg`)
* **What to capture:** Double-click `Run.bat` or run `Check.bat` in a Windows Terminal. Wait for the system verification checks (Configuration, Docker CLI, Docker Desktop, Ollama service, and Model download state) to complete successfully. Capture the terminal window showing the list of green checkmarks `[✓]`.
* **How to capture:**
  - Press `Alt + Print Screen` while focusing on the terminal.
  - Save the captured screenshot in this folder as `startup_checks.png`.

---

## 3. Email Classification Screenshot
* **Filename:** `classification_dashboard.png` (or `.jpg`)
* **What to capture:** With the agent running, send a test email or run the pipeline in test mode (`docker compose run --rm email-agent python main.py --test` or `.venv\Scripts\python main.py --test`). Capture the terminal output displaying the beautifully formatted Rich panels and color-coded table showing category classifications, priorities, summaries, and confidence bars.
* **How to capture:**
  - Crop the terminal window focusing on the tabular classification panel output.
  - Save the captured screenshot in this folder as `classification_dashboard.png`.
