"""Entry point for the Local AI Email Security Agent.

Usage:
    python main.py --scan           Scan inbox once
    python main.py --scan --watch   Scan continuously
    python main.py --test           Run against test fixtures (no IMAP needed)
    python main.py --check          Check Ollama connection and model availability
"""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

# Make sure src/ is on the path when running directly from project root
sys.path.insert(0, str(Path(__file__).parent / "src"))

from email_agent import display as display_module
from email_agent.classifier import Classifier
from email_agent.config import settings
from email_agent.imap_reader import IMAPReader
from email_agent.parser import EmailParser
from email_agent.pipeline import Pipeline

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

FIXTURES_DIR = Path(__file__).parent / "tests" / "fixtures"


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="email-security-agent",
        description="Local AI Email Security Agent — powered by Ollama",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--scan", action="store_true", help="Scan inbox (use with --watch for continuous)")
    mode.add_argument("--test", action="store_true", help="Run against fixture emails (no IMAP needed)")
    mode.add_argument("--check", action="store_true", help="Check Ollama connection and model availability")
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Continuously scan on an interval (only valid with --scan)",
    )
    return parser


def _validate_imap_settings() -> bool:
    """Check that IMAP credentials are configured.

    Returns:
        True if credentials are present, False otherwise.
    """
    if not settings.imap_username or not settings.imap_password:
        display_module.print_error(
            "IMAP credentials are not configured.\n\n"
            "Please create a .env file (copy from .env.example) and set:\n"
            "  IMAP_USERNAME=your_email@gmail.com\n"
            "  IMAP_PASSWORD=your_gmail_app_password\n\n"
            "Gmail requires an App Password (not your real password).\n"
            "See README.md → 'Gmail App Password Setup' for step-by-step instructions."
        )
        return False
    return True


def _log_startup_info() -> None:
    """Log model and Ollama URL to confirm the active configuration."""
    logger.info(
        "Starting agent — model=%s  ollama=%s",
        settings.ollama_model,
        settings.ollama_base_url,
    )


def _build_pipeline() -> Pipeline:
    """Construct and return the fully wired Pipeline instance.

    Returns:
        A ready-to-use Pipeline object.
    """
    reader = IMAPReader(settings)
    parser = EmailParser()
    classifier = Classifier(settings)
    return Pipeline(settings, reader, parser, classifier, display_module)


# ---------------------------------------------------------------------------
# Mode handlers
# ---------------------------------------------------------------------------


def handle_check() -> None:
    """Run the Ollama health-check script and relay its exit code."""
    check_script = Path(__file__).parent / "scripts" / "check_ollama.py"
    result = subprocess.run(
        [sys.executable, str(check_script)],
        check=False,
    )
    sys.exit(result.returncode)


def handle_test() -> None:
    """Run the pipeline in test mode against fixture .eml files."""
    _log_startup_info()
    pipeline = _build_pipeline()
    pipeline.run_test_mode(FIXTURES_DIR)


def handle_scan(watch: bool) -> None:
    """Run the pipeline in live IMAP scan mode.

    Args:
        watch: If True, loop continuously until Ctrl+C.
    """
    if not _validate_imap_settings():
        sys.exit(1)

    _log_startup_info()
    pipeline = _build_pipeline()

    if watch:
        pipeline.run_watch(settings.scan_interval_seconds)
    else:
        pipeline.run_once()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Parse CLI arguments and dispatch to the appropriate handler."""
    parser = _build_parser()
    args = parser.parse_args()

    if args.check:
        handle_check()
    elif args.test:
        handle_test()
    elif args.scan:
        handle_scan(watch=args.watch)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
