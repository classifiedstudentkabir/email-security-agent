# 📦 Project Release Checklist

This checklist is for maintainers to verify system stability, documentation accuracy, and configuration consistency before releasing a new version of the Local AI Email Security Agent.

---

## 🧪 1. Tests & Code Quality Check
- [ ] Run the complete offline test suite and ensure 100% of tests pass:
  ```bash
  .venv\Scripts\python -m pytest tests/ -v --cov=src/email_agent
  ```
- [ ] Ensure that code style and formatting adhere to standards by running Ruff:
  ```bash
  .venv\Scripts\ruff check src/
  .venv\Scripts\ruff format --check src/
  ```

---

## 🐳 2. Docker & Multi-Platform Validation
- [ ] Build the Docker container from clean state to verify no dependency build errors:
  ```bash
  docker compose build --no-cache
  ```
- [ ] Verify test mode runs cleanly inside Docker:
  ```bash
  docker compose run --rm email-agent python main.py --test
  ```
- [ ] Run the agent check utility inside the Docker context to verify internal connectivity:
  ```bash
  docker compose run --rm email-agent python main.py --check
  ```
- [ ] Verify that logs are successfully created and mounted to the host `./logs/` directory.

---

## 🤖 3. Ollama & Model Compatibility Check
- [ ] Confirm the default model (`qwen2.5:1.5b`) runs as expected and outputs clean JSON.
- [ ] Verify support for alternative recommended models:
  - [ ] `qwen2.5:3b`
  - [ ] `llama3.2:3b`
- [ ] Verify the JSON repair mechanisms successfully catch and repair minor output formatting discrepancies.

---

## 📝 4. Documentation & Configuration Audit
- [ ] **`.env.example` Check:** Ensure no default production secrets or credentials are present and comments remain clean, up-to-date, and helpful.
- [ ] **`README.md` Check:** Check that installation URLs are active and Windows quick start commands are accurate.
- [ ] **`docs/CONFIGURATION.md` Check:** Make sure any new variables added in the release are fully documented.
- [ ] **Startup Files Check:** Confirm `Run.bat`, `Stop.bat`, and `Check.bat` contain no broken syntax, path references, or typos.

---

## 🚀 5. GitHub Release Process
- [ ] Increment the project version in configuration files (if applicable).
- [ ] Create a git tag corresponding to the release version:
  ```bash
  git tag -a v1.0.0 -m "Release version 1.0.0"
  ```
- [ ] Push the tag to GitHub:
  ```bash
  git push origin v1.0.0
  ```
- [ ] Write clear GitHub Release Notes summarizing:
  - New features
  - Bug fixes
  - Configuration changes
  - Upgrade guidelines
