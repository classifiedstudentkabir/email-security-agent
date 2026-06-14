"""Email parser module — converts raw RFC 2822 bytes into an EmailMessage.

Handles:
- RFC 2047 encoded-word subjects
- Multipart emails (prefers text/plain over text/html)
- Basic HTML stripping for html-only emails
- Graceful date parsing with None fallback
"""

import email
import email.header
import email.message
import email.utils
import logging
import re
from datetime import datetime
from email.message import Message

from .models import EmailMessage

logger = logging.getLogger(__name__)

# Regex to strip HTML tags when no plain-text alternative is available
_HTML_TAG_RE = re.compile(r"<[^>]+>")
# Collapse three or more consecutive newlines into two
_EXCESS_BLANK_LINES_RE = re.compile(r"\n{3,}")


def _decode_header_value(raw_value: str | None) -> str:
    """Decode an RFC 2047 encoded email header value to a plain string.

    Args:
        raw_value: The raw header string, possibly containing encoded-words.

    Returns:
        Decoded string, or empty string if raw_value is None.
    """
    if not raw_value:
        return ""

    parts = email.header.decode_header(raw_value)
    decoded_parts: list[str] = []
    for part, charset in parts:
        if isinstance(part, bytes):
            try:
                decoded_parts.append(part.decode(charset or "utf-8", errors="replace"))
            except (LookupError, UnicodeDecodeError):
                decoded_parts.append(part.decode("utf-8", errors="replace"))
        else:
            decoded_parts.append(part)
    return "".join(decoded_parts)


def _extract_sender(msg: Message) -> str:
    """Extract a human-readable sender string from the From header.

    Args:
        msg: Parsed email message object.

    Returns:
        Sender in "Display Name <address>" format, or just the address.
    """
    raw_from = msg.get("From", "")
    display_name, address = email.utils.parseaddr(raw_from)
    display_name = _decode_header_value(display_name)
    if display_name:
        return f"{display_name} <{address}>"
    return address


def _strip_html(html_content: str) -> str:
    """Strip HTML tags from a string and normalise whitespace.

    Args:
        html_content: Raw HTML string.

    Returns:
        Plain text with tags removed and whitespace collapsed.
    """
    text = _HTML_TAG_RE.sub(" ", html_content)
    return re.sub(r" {2,}", " ", text).strip()


def _extract_body(msg: Message) -> str:
    """Recursively extract body text from an email message.

    Priority order:
    1. text/plain parts
    2. text/html parts (tags stripped)

    Args:
        msg: Email message or sub-part.

    Returns:
        Decoded body string.
    """
    if msg.is_multipart():
        return _extract_body_multipart(msg)
    return _extract_body_single(msg)


def _extract_body_multipart(msg: Message) -> str:
    """Extract body from a multipart message, preferring text/plain.

    Args:
        msg: A multipart email.Message object.

    Returns:
        Best available body text.
    """
    plain_parts: list[str] = []
    html_parts: list[str] = []

    for part in msg.walk():
        content_type = part.get_content_type()
        if content_type == "text/plain":
            plain_parts.append(_decode_payload(part))
        elif content_type == "text/html":
            html_parts.append(_strip_html(_decode_payload(part)))

    if plain_parts:
        return "\n".join(plain_parts)
    return "\n".join(html_parts)


def _extract_body_single(msg: Message) -> str:
    """Extract body from a non-multipart message.

    Args:
        msg: A single-part email.Message object.

    Returns:
        Decoded body string.
    """
    content_type = msg.get_content_type()
    payload = _decode_payload(msg)
    if content_type == "text/html":
        return _strip_html(payload)
    return payload


def _decode_payload(part: Message) -> str:
    """Decode a message part's payload to a string.

    Args:
        part: An email.message.Message part.

    Returns:
        Decoded string content.
    """
    payload = part.get_payload(decode=True)
    if not isinstance(payload, bytes):
        return str(payload or "")
    charset = part.get_content_charset() or "utf-8"
    try:
        return payload.decode(charset, errors="replace")
    except (LookupError, UnicodeDecodeError):
        return payload.decode("utf-8", errors="replace")


def _normalise_body(body: str) -> str:
    """Collapse excessive blank lines and strip leading/trailing whitespace.

    Args:
        body: Raw body string.

    Returns:
        Normalised body string.
    """
    return _EXCESS_BLANK_LINES_RE.sub("\n\n", body).strip()


def _parse_date(msg: Message) -> datetime | None:
    """Parse the Date header into a datetime object.

    Args:
        msg: Parsed email message.

    Returns:
        Datetime object if parsing succeeds, None otherwise.
    """
    raw_date = msg.get("Date")
    if not raw_date:
        return None
    try:
        parsed = email.utils.parsedate_to_datetime(raw_date)
        return parsed
    except (ValueError, TypeError) as exc:
        logger.warning("Could not parse date header %r: %s", raw_date, exc)
        return None


class EmailParser:
    """Parses raw RFC 2822 email bytes into an EmailMessage model."""

    def parse(self, uid: str, raw: bytes) -> EmailMessage:
        """Parse raw email bytes into a structured EmailMessage.

        Args:
            uid: IMAP UID string uniquely identifying this email.
            raw: Raw RFC 2822 email bytes.

        Returns:
            Populated EmailMessage instance.
        """
        msg = email.message_from_bytes(raw)

        sender = _extract_sender(msg)
        subject = _decode_header_value(msg.get("Subject", ""))
        body = _normalise_body(_extract_body(msg))
        date = _parse_date(msg)

        logger.debug("Parsed email UID=%s from=%s subject=%r", uid, sender, subject[:60])

        return EmailMessage(
            uid=uid,
            sender=sender,
            subject=subject,
            body=body,
            date=date,
            raw=raw,
        )
