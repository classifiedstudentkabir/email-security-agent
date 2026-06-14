"""Tests for the email classifier module.

Uses respx to intercept httpx calls so no real Ollama instance is needed.
All tests verify the JSON parsing strategy and retry logic.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
import respx

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from email_agent.classifier import Classifier
from email_agent.models import Category, EmailMessage, Priority

OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"


def _make_ollama_response(payload: dict) -> dict:
    """Build a minimal /api/chat response body wrapping the given payload.

    Args:
        payload: Dict to serialise as the model's message content.

    Returns:
        Dict matching the Ollama /api/chat response schema.
    """
    return {
        "message": {
            "role": "assistant",
            "content": json.dumps(payload),
        }
    }


def _sample_email() -> EmailMessage:
    """Return a minimal EmailMessage for use across tests.

    Returns:
        EmailMessage with uid, sender, subject, and body set.
    """
    return EmailMessage(
        uid="test-001",
        sender="researcher@protonmail.com",
        subject="SQL Injection in Login",
        body="Found ' OR '1'='1 in the login form",
        date=datetime.now(tz=timezone.utc),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@respx.mock
def test_classify_sql_injection(settings_fixture):
    """Classify an email and assert SQL_INJECTION category with HIGH priority.

    Mocks Ollama to return valid JSON with the expected fields.
    """
    mock_body = {
        "category": "SQL Injection Report",
        "priority": "HIGH",
        "summary": "SQL injection vulnerability found in login endpoint",
        "recommended_action": "Patch immediately using parameterised queries",
        "confidence": 92,
    }
    respx.post(OLLAMA_ENDPOINT).mock(return_value=httpx.Response(200, json=_make_ollama_response(mock_body)))

    classifier = Classifier(settings_fixture)
    result = classifier.classify(_sample_email())

    assert result.category == Category.SQL_INJECTION
    assert result.priority == Priority.HIGH
    assert result.confidence == 92
    assert result.model_used == settings_fixture.ollama_model


@respx.mock
def test_classify_spam(settings_fixture):
    """Classify a spam email and assert SPAM category with LOW priority.

    Mocks Ollama to return valid JSON.
    """
    mock_body = {
        "category": "Spam",
        "priority": "LOW",
        "summary": "Prize-winning spam message",
        "recommended_action": "Delete immediately",
        "confidence": 98,
    }
    respx.post(OLLAMA_ENDPOINT).mock(return_value=httpx.Response(200, json=_make_ollama_response(mock_body)))

    classifier = Classifier(settings_fixture)
    email = EmailMessage(
        uid="spam-001",
        sender="promo@deals.xyz",
        subject="You've won!!!",
        body="Click here for your prize",
    )
    result = classifier.classify(email)

    assert result.category == Category.SPAM
    assert result.priority == Priority.LOW
    assert result.confidence == 98


@respx.mock
def test_classify_fallback_on_invalid_json(settings_fixture):
    """Return a safe fallback result when the model outputs non-JSON prose.

    Asserts that confidence is 0, category is GENERAL_INQUIRY, and the
    summary mentions 'failed'.
    """
    respx.post(OLLAMA_ENDPOINT).mock(
        return_value=httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": "I cannot classify this email right now."}},
        )
    )

    classifier = Classifier(settings_fixture)
    result = classifier.classify(_sample_email())

    assert result.category == Category.GENERAL_INQUIRY
    assert result.confidence == 0
    assert "failed" in result.summary.lower()
    assert result.raw_response is not None


@respx.mock
def test_classify_fallback_on_json_inside_prose(settings_fixture):
    """Extract JSON embedded inside prose using regex fallback.

    The model response contains a JSON object surrounded by natural language
    text. The classifier must extract it and return the correct category.
    """
    embedded_json = json.dumps({
        "category": "Spam",
        "priority": "LOW",
        "summary": "Classic prize spam email",
        "recommended_action": "Delete without clicking links",
        "confidence": 85,
    })
    prose_response = f'Sure, here is my classification answer: {embedded_json} Hope that helps!'
    respx.post(OLLAMA_ENDPOINT).mock(
        return_value=httpx.Response(
            200,
            json={"message": {"role": "assistant", "content": prose_response}},
        )
    )

    classifier = Classifier(settings_fixture)
    result = classifier.classify(_sample_email())

    assert result.category == Category.SPAM
    assert result.confidence == 85


@respx.mock
def test_classify_retry_on_timeout(settings_fixture):
    """Retry Ollama call on timeout and succeed on the third attempt.

    The mock raises TimeoutException twice then returns a valid response.
    Asserts the result is valid and that the endpoint was called 3 times.
    """
    valid_body = {
        "category": "General Inquiry",
        "priority": "LOW",
        "summary": "General email about security policy",
        "recommended_action": "Reply with policy document link",
        "confidence": 75,
    }

    route = respx.post(OLLAMA_ENDPOINT)
    route.side_effect = [
        httpx.TimeoutException("timeout 1"),
        httpx.TimeoutException("timeout 2"),
        httpx.Response(200, json=_make_ollama_response(valid_body)),
    ]

    classifier = Classifier(settings_fixture)
    result = classifier.classify(_sample_email())

    assert result.category == Category.GENERAL_INQUIRY
    assert result.confidence == 75
    assert route.call_count == 3
