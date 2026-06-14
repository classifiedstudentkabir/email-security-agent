"""Pipeline module — orchestrates fetch → parse → classify → display.

The Pipeline class is the single integration point that knows about all
other modules. main.py creates a Pipeline and calls one of its three run
methods depending on the CLI flag used.
"""

import logging
import time
import types
from pathlib import Path

from .classifier import Classifier
from .config import Settings
from .display import (
    print_classification_result,
    print_error,
    print_scan_complete,
    print_scan_header,
    print_test_mode_banner,
)
from .imap_reader import IMAPReader
from .models import ClassificationResult
from .parser import EmailParser

logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrates the full email security analysis pipeline.

    Each run method corresponds to a CLI mode:

    - ``run_once()``  — scan the real inbox once.
    - ``run_test_mode()`` — scan fixture .eml files (no IMAP needed).
    - ``run_watch()`` — loop ``run_once()`` on a fixed interval.
    """

    def __init__(
        self,
        settings: Settings,
        imap_reader: IMAPReader,
        parser: EmailParser,
        classifier: Classifier,
        display: types.ModuleType,
    ) -> None:
        """Initialise the pipeline with all required dependencies.

        Args:
            settings: Application settings.
            imap_reader: IMAP reader for fetching real emails.
            parser: Email parser for converting raw bytes to EmailMessage.
            classifier: Classifier that calls Ollama and returns ClassificationResult.
            display: The display module (passed as a module object for testability).
        """
        self._settings = settings
        self._imap_reader = imap_reader
        self._parser = parser
        self._classifier = classifier
        self._display = display

    # ------------------------------------------------------------------
    # Public run methods
    # ------------------------------------------------------------------

    def run_once(self) -> list[ClassificationResult]:
        """Fetch and classify all unread emails from the configured inbox.

        Returns:
            List of ClassificationResult objects, one per successfully processed email.
        """
        with self._imap_reader as reader:
            raw_emails = reader.fetch_unread()

        print_scan_header(len(raw_emails))
        results = self._process_raw_emails(raw_emails)
        return results

    def run_test_mode(self, fixture_dir: Path) -> list[ClassificationResult]:
        """Classify all .eml fixture files without making an IMAP connection.

        Args:
            fixture_dir: Path to the directory containing .eml fixture files.

        Returns:
            List of ClassificationResult objects for each fixture.
        """
        print_test_mode_banner()

        try:
            eml_files = sorted(fixture_dir.glob("*.eml"))
        except FileNotFoundError:
            print_error(f"Fixture directory not found: {fixture_dir}")
            return []

        raw_emails: list[tuple[str, bytes]] = []
        for eml_path in eml_files:
            try:
                raw_bytes = eml_path.read_bytes()
                raw_emails.append((eml_path.stem, raw_bytes))
            except FileNotFoundError as exc:
                logger.error("Could not read fixture file %s: %s", eml_path, exc)

        print_scan_header(len(raw_emails))
        results = self._process_raw_emails(raw_emails)
        return results

    def run_watch(self, interval_seconds: int) -> None:
        """Continuously scan the inbox at a fixed interval.

        Runs until interrupted by Ctrl+C.

        Args:
            interval_seconds: Seconds to wait between scans.
        """
        logger.info("Starting watcher — scanning every %ds", interval_seconds)
        try:
            while True:
                self.run_once()
                logger.info("Next scan in %ds — press Ctrl+C to stop", interval_seconds)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("👋 Stopping watcher...")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _process_raw_emails(
        self, raw_emails: list[tuple[str, bytes]]
    ) -> list[ClassificationResult]:
        """Parse, classify, and display each raw email.

        Args:
            raw_emails: List of ``(uid, raw_bytes)`` pairs.

        Returns:
            List of ClassificationResult for successfully processed emails.
        """
        results: list[ClassificationResult] = []
        errors = 0

        for uid, raw_bytes in raw_emails:
            result = self._process_single(uid, raw_bytes)
            if result is not None:
                results.append(result)
            else:
                errors += 1

        print_scan_complete(len(results), errors)
        return results

    def _process_single(self, uid: str, raw_bytes: bytes) -> ClassificationResult | None:
        """Parse and classify a single raw email, displaying the result.

        Args:
            uid: IMAP UID or fixture name for this email.
            raw_bytes: Raw RFC 2822 bytes.

        Returns:
            ClassificationResult on success, None on unrecoverable error.
        """
        try:
            email_msg = self._parser.parse(uid, raw_bytes)
            result = self._classifier.classify(email_msg)
            print_classification_result(email_msg, result)
            return result
        except Exception as exc:  # noqa: BLE001 — pipeline must not stop
            logger.error("Unexpected error processing email UID=%s: %s", uid, exc, exc_info=True)
            print_error(f"Failed to process email UID={uid}: {exc}")
            return None
