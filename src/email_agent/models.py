"""Data models for the Email Security Agent.

These Pydantic v2 models define the contracts between every layer of the pipeline.
Field names are frozen — future phases may only add new optional fields.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    """Classification category for an incoming email.

    Each value is the exact string the Ollama model is asked to return.
    """

    SQL_INJECTION = "SQL Injection Report"
    XSS = "XSS Report"
    VULNERABILITY = "Vulnerability Disclosure"
    BUG_REPORT = "Bug Report"
    CRITICAL_ALERT = "Critical Security Alert"
    PHISHING = "Phishing"
    GENERAL_INQUIRY = "General Inquiry"
    SPAM = "Spam"


class Priority(str, Enum):
    """Priority level assigned to a classified email."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EmailMessage(BaseModel):
    """Parsed representation of an RFC 2822 email message.

    Produced by EmailParser and consumed by Classifier and Display.
    """

    uid: str
    sender: str
    subject: str
    body: str
    date: datetime | None = None
    raw: bytes | None = None  # Reserved for Phase 2 storage


class ClassificationResult(BaseModel):
    """Result of classifying a single email via Ollama.

    Produced by Classifier and consumed by Display and (Phase 2) Storage.
    """

    email_uid: str
    category: Category
    priority: Priority
    summary: str = Field(description="One-sentence summary, max 20 words")
    recommended_action: str = Field(description="One-sentence action, max 20 words")
    confidence: int = Field(ge=0, le=100, description="Self-reported model confidence 0–100")
    model_used: str
    classified_at: datetime
    raw_response: str | None = None  # For debugging malformed model output
