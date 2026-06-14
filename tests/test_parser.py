"""Tests for the email parser module.

All tests are fully offline — they load .eml fixture files from disk
and assert that the parser extracts the correct fields.
No network calls are made.
"""

import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from email_agent.parser import EmailParser

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def parser() -> EmailParser:
    """Return an EmailParser instance.

    Returns:
        Ready-to-use EmailParser.
    """
    return EmailParser()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_parse_sql_injection_eml(parser: EmailParser, sample_raw_eml):
    """Parse sql_injection.eml and assert key fields are correctly extracted.

    Sender must contain the expected address, subject must mention SQL,
    and the body must be at least 50 characters long.
    """
    raw = sample_raw_eml("sql_injection")
    email_msg = parser.parse("sql-001", raw)

    assert "security_researcher@protonmail.com" in email_msg.sender
    assert "SQL" in email_msg.subject
    assert len(email_msg.body) > 50


def test_parse_phishing_eml(parser: EmailParser, sample_raw_eml):
    """Parse phishing.eml and assert the subject conveys urgency or suspension."""
    raw = sample_raw_eml("phishing")
    email_msg = parser.parse("phish-001", raw)

    subject_lower = email_msg.subject.lower()
    assert "suspended" in subject_lower or "urgent" in subject_lower


def test_parse_general_inquiry_eml(parser: EmailParser, sample_raw_eml):
    """Parse general_inquiry.eml and assert sender and body are populated."""
    raw = sample_raw_eml("general_inquiry")
    email_msg = parser.parse("general-001", raw)

    assert email_msg.sender != ""
    assert len(email_msg.body) > 0


def test_parse_subject_with_encoded_words(parser: EmailParser):
    """Parse a raw email with an RFC 2047 Base64-encoded subject.

    The encoded subject ``=?UTF-8?B?VGVzdCBTdWJqZWN0?=`` decodes to
    'Test Subject'. The parser must return the decoded plain string.
    """
    raw_email = (
        "From: sender@example.com\r\n"
        "To: recipient@example.com\r\n"
        "Subject: =?UTF-8?B?VGVzdCBTdWJqZWN0?=\r\n"
        "MIME-Version: 1.0\r\n"
        "Content-Type: text/plain; charset=UTF-8\r\n"
        "\r\n"
        "Body content here."
    ).encode("utf-8")

    email_msg = parser.parse("encoded-001", raw_email)
    assert email_msg.subject == "Test Subject"


def test_parse_multipart_extracts_text_plain(parser: EmailParser):
    """Parse a multipart email and confirm text/plain is preferred over text/html.

    The plain text part contains a unique marker string that should appear
    in the parsed body. The HTML part should not be selected.
    """
    msg = MIMEMultipart("alternative")
    msg["From"] = "sender@example.com"
    msg["To"] = "recipient@example.com"
    msg["Subject"] = "Multipart Test"

    plain_text = "This is the PLAIN TEXT version of the email."
    html_text = "<html><body><p>This is the <b>HTML</b> version.</p></body></html>"

    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_text, "html", "utf-8"))

    raw_bytes = msg.as_bytes()
    email_msg = parser.parse("multipart-001", raw_bytes)

    assert "PLAIN TEXT" in email_msg.body
    assert "<html>" not in email_msg.body
