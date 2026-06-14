"""Configuration module for the Email Security Agent.

All settings are loaded from environment variables or a .env file via pydantic-settings.
Never hardcode credentials or model names anywhere else in the codebase.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file.

    All fields have defaults except IMAP_USERNAME and IMAP_PASSWORD,
    which must be provided via .env or environment variables for --scan mode.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # -------------------------------------------------------------------------
    # Ollama settings
    # -------------------------------------------------------------------------
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:1.5b"
    ollama_timeout: int = 30
    ollama_max_retries: int = 3

    # -------------------------------------------------------------------------
    # IMAP settings
    # -------------------------------------------------------------------------
    imap_host: str = "imap.gmail.com"
    imap_port: int = 993
    imap_username: str = ""
    imap_password: str = ""
    imap_mailbox: str = "INBOX"
    imap_mark_as_read: bool = False

    # -------------------------------------------------------------------------
    # Pipeline settings
    # -------------------------------------------------------------------------
    email_body_max_chars: int = 1200
    scan_interval_seconds: int = 60
    max_emails_per_scan: int = 10

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------
    log_level: str = "INFO"


# Singleton — import this throughout the project
settings = Settings()
