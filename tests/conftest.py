"""Shared pytest fixtures for the email security agent test suite."""

import sys
from pathlib import Path

import pytest

# Ensure src/ is importable from tests/
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from email_agent.config import Settings

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def settings_fixture() -> Settings:
    """Return a Settings object pre-configured with safe test values.

    IMAP credentials are set to dummy values so Settings validates without
    a real .env file. The Ollama model matches the project default.

    Returns:
        Settings instance suitable for unit tests.
    """
    return Settings(
        imap_username="test@test.com",
        imap_password="test",
        ollama_model="qwen2.5:1.5b",
        ollama_base_url="http://localhost:11434",
        ollama_timeout=10,
        ollama_max_retries=3,
        email_body_max_chars=1200,
    )


@pytest.fixture()
def sample_eml_dir() -> Path:
    """Return the Path to the tests/fixtures/ directory.

    Returns:
        Absolute Path to the fixtures directory.
    """
    return FIXTURES_DIR


@pytest.fixture()
def sample_raw_eml():
    """Return a callable that loads a named fixture .eml file as bytes.

    Usage::

        def test_something(sample_raw_eml):
            raw = sample_raw_eml("sql_injection")
            ...

    Returns:
        Callable[[str], bytes] that takes a fixture name (without .eml) and
        returns the file's raw bytes.
    """

    def _loader(name: str) -> bytes:
        """Load a fixture file by stem name.

        Args:
            name: Fixture filename without the .eml extension.

        Returns:
            Raw bytes of the fixture file.

        Raises:
            FileNotFoundError: If the fixture does not exist.
        """
        path = FIXTURES_DIR / f"{name}.eml"
        if not path.exists():
            raise FileNotFoundError(f"Fixture not found: {path}")
        return path.read_bytes()

    return _loader
