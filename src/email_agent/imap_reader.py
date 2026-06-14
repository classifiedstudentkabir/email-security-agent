"""IMAP reader module — connects to a mail server and fetches unread emails.

Uses Python stdlib imaplib with SSL. Implemented as a context manager so
the connection is always properly closed, even if an error occurs mid-fetch.
Never raises to the caller — errors are logged and an empty list is returned.
"""

import imaplib
import logging
from types import TracebackType
from typing import Self

from .config import Settings

logger = logging.getLogger(__name__)


class IMAPReader:
    """Fetches unread emails from an IMAP mailbox via SSL.

    Usage::

        with IMAPReader(settings) as reader:
            pairs = reader.fetch_unread()

    Each item in the returned list is a ``(uid, raw_bytes)`` tuple.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialise with application settings.

        Args:
            settings: Settings containing IMAP host, credentials, and limits.
        """
        self._settings = settings
        self._conn: imaplib.IMAP4_SSL | None = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> Self:
        """Open the IMAP SSL connection and log in.

        Returns:
            This reader instance, ready to fetch emails.
        """
        self._connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the IMAP connection regardless of whether an error occurred.

        Args:
            exc_type: Exception type, if any.
            exc_val: Exception value, if any.
            exc_tb: Exception traceback, if any.
        """
        self._disconnect()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_unread(self) -> list[tuple[str, bytes]]:
        """Fetch unread emails from the configured mailbox.

        Returns:
            List of ``(uid_string, raw_rfc2822_bytes)`` tuples.
            Returns an empty list on any error.
        """
        if self._conn is None:
            logger.error("Cannot fetch — IMAP connection is not open.")
            return []

        try:
            return self._fetch_emails()
        except (imaplib.IMAP4.error, OSError) as exc:
            logger.error("Error fetching emails: %s", exc)
            return []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _connect(self) -> None:
        """Establish SSL IMAP connection and authenticate.

        Logs an error and leaves ``self._conn`` as None if connection fails.
        """
        try:
            self._conn = imaplib.IMAP4_SSL(self._settings.imap_host, self._settings.imap_port)
            self._conn.login(self._settings.imap_username, self._settings.imap_password)
            logger.info(
                "Connected to IMAP server %s:%d as %s",
                self._settings.imap_host,
                self._settings.imap_port,
                self._settings.imap_username,
            )
        except (imaplib.IMAP4.error, OSError) as exc:
            logger.error("IMAP connection failed: %s", exc)
            self._conn = None

    def _disconnect(self) -> None:
        """Gracefully log out and close the IMAP connection."""
        if self._conn is None:
            return
        try:
            self._conn.logout()
        except (imaplib.IMAP4.error, OSError) as exc:
            logger.warning("Error during IMAP logout: %s", exc)
        finally:
            self._conn = None

    def _fetch_emails(self) -> list[tuple[str, bytes]]:
        """Select mailbox, search for UNSEEN messages, and fetch raw bytes.

        Returns:
            List of ``(uid_string, raw_bytes)`` tuples for unread emails.
        """
        assert self._conn is not None  # guarded by caller

        status, _ = self._conn.select(self._settings.imap_mailbox)
        if status != "OK":
            logger.error("Could not select mailbox: %s", self._settings.imap_mailbox)
            return []

        status, uid_list_raw = self._conn.uid("search", None, "UNSEEN")
        if status != "OK" or not uid_list_raw or not uid_list_raw[0]:
            return []

        uids = uid_list_raw[0].split()
        # Respect the per-scan limit — take the most recent N
        uids = uids[-self._settings.max_emails_per_scan :]

        results: list[tuple[str, bytes]] = []
        for uid_bytes in uids:
            uid_str = uid_bytes.decode()
            raw = self._fetch_single(uid_str)
            if raw is not None:
                if self._settings.imap_mark_as_read:
                    self._mark_seen(uid_str)
                results.append((uid_str, raw))

        logger.info("Fetched %d unread email(s)", len(results))
        return results

    def _fetch_single(self, uid: str) -> bytes | None:
        """Fetch raw RFC 2822 bytes for a single email UID.

        Args:
            uid: IMAP UID string.

        Returns:
            Raw email bytes, or None if fetch failed.
        """
        assert self._conn is not None

        status, data = self._conn.uid("fetch", uid, "(RFC822)")
        if status != "OK" or not data or data[0] is None:
            logger.warning("Failed to fetch UID %s", uid)
            return None

        raw = data[0][1]
        if not isinstance(raw, bytes):
            logger.warning("Unexpected data type for UID %s: %s", uid, type(raw))
            return None

        return raw

    def _mark_seen(self, uid: str) -> None:
        """Mark a single email as \\Seen on the server.

        Args:
            uid: IMAP UID string of the email to mark.
        """
        assert self._conn is not None

        try:
            self._conn.uid("store", uid, "+FLAGS", "\\Seen")
            logger.debug("Marked UID %s as seen", uid)
        except imaplib.IMAP4.error as exc:
            logger.warning("Could not mark UID %s as seen: %s", uid, exc)
