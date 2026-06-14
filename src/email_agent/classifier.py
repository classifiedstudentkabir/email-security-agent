"""Classifier module — sends emails to Ollama and parses the JSON response.

Uses httpx (not the ollama SDK) for maximum testability and future async compatibility.
All errors are handled internally; callers always receive a ClassificationResult.
"""

import json
import logging
import re
import time
from datetime import datetime, timezone

import httpx

from .config import Settings
from .models import Category, ClassificationResult, EmailMessage, Priority

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt — strict JSON schema enforced via prompt engineering
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a security email classifier. You must respond ONLY with valid JSON.
No preamble. No explanation. No markdown fences. No text before or after.
Only a single JSON object matching this exact schema:

{
  "category": "<category>",
  "priority": "<priority>",
  "summary": "<one sentence summary, max 20 words>",
  "recommended_action": "<one sentence, max 20 words>",
  "confidence": <integer between 0 and 100>
}

Valid categories (use EXACTLY one of these strings):
SQL Injection Report, XSS Report, Vulnerability Disclosure, Bug Report,
Critical Security Alert, Phishing, General Inquiry, Spam

Valid priorities: LOW, MEDIUM, HIGH, CRITICAL"""


def _build_user_message(email: EmailMessage, max_chars: int) -> str:
    """Build the user-facing message from an EmailMessage.

    Args:
        email: The parsed email to describe.
        max_chars: Maximum characters to include from the body.

    Returns:
        Formatted string for the Ollama user message.
    """
    body_truncated = email.body[:max_chars]
    return f"From: {email.sender}\nSubject: {email.subject}\nBody:\n{body_truncated}"


def _parse_json_response(response_text: str) -> dict | None:
    """Attempt to extract a JSON object from the model's response text.

    Tries direct parsing first, then regex extraction as fallback.

    Args:
        response_text: Raw string returned by the model.

    Returns:
        Parsed dict if successful, None otherwise.
    """
    # Attempt 1: direct JSON parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Attempt 2: regex extraction of first {...} block
    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def _build_fallback_result(email_uid: str, model_used: str, raw_response: str | None) -> ClassificationResult:
    """Build a safe fallback ClassificationResult when classification fails.

    Args:
        email_uid: UID of the email that could not be classified.
        model_used: Name of the model that was queried.
        raw_response: Raw text returned by the model (for debugging).

    Returns:
        A ClassificationResult indicating classification failure.
    """
    return ClassificationResult(
        email_uid=email_uid,
        category=Category.GENERAL_INQUIRY,
        priority=Priority.LOW,
        summary="Classification failed - model returned invalid JSON",
        recommended_action="Review email manually",
        confidence=0,
        model_used=model_used,
        classified_at=datetime.now(tz=timezone.utc),
        raw_response=raw_response,
    )


def _dict_to_result(data: dict, email_uid: str, model_used: str) -> ClassificationResult | None:
    """Convert a parsed JSON dict to a ClassificationResult.

    Args:
        data: Parsed JSON dict from the model response.
        email_uid: UID of the classified email.
        model_used: Name of the model that produced the response.

    Returns:
        ClassificationResult on success, None if fields are invalid.
    """
    try:
        return ClassificationResult(
            email_uid=email_uid,
            category=Category(data["category"]),
            priority=Priority(data["priority"]),
            summary=data.get("summary", ""),
            recommended_action=data.get("recommended_action", ""),
            confidence=int(data.get("confidence", 0)),
            model_used=model_used,
            classified_at=datetime.now(tz=timezone.utc),
        )
    except (KeyError, ValueError) as exc:
        logger.warning("JSON parsed but fields invalid: %s", exc)
        return None


class Classifier:
    """Classifies email messages using a local Ollama model via HTTP.

    Implements retry with exponential backoff and a multi-level JSON fallback
    chain so the pipeline never crashes on a single bad model response.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialise the classifier with application settings.

        Args:
            settings: Application settings including Ollama URL, model, and timeouts.
        """
        self._settings = settings
        self._api_url = f"{settings.ollama_base_url}/api/chat"

    def classify(self, email: EmailMessage) -> ClassificationResult:
        """Classify a single email message via Ollama.

        Never raises. All errors result in a fallback ClassificationResult.

        Args:
            email: Parsed email message to classify.

        Returns:
            ClassificationResult with category, priority, summary, and confidence.
        """
        user_message = _build_user_message(email, self._settings.email_body_max_chars)
        payload = {
            "model": self._settings.ollama_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
        }

        raw_response: str | None = None
        last_exception: Exception | None = None

        for attempt in range(1, self._settings.ollama_max_retries + 1):
            try:
                raw_response = self._call_ollama(payload)
                break
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                last_exception = exc
                backoff = 2 ** attempt  # 2s, 4s, 8s
                logger.warning(
                    "Ollama call failed (attempt %d/%d): %s — retrying in %ds",
                    attempt,
                    self._settings.ollama_max_retries,
                    exc,
                    backoff,
                )
                if attempt < self._settings.ollama_max_retries:
                    time.sleep(backoff)

        if raw_response is None:
            logger.error("All Ollama retries exhausted: %s", last_exception)
            return _build_fallback_result(email.uid, self._settings.ollama_model, None)

        parsed = _parse_json_response(raw_response)
        if parsed is None:
            logger.warning("Could not parse JSON from model response: %r", raw_response[:200])
            return _build_fallback_result(email.uid, self._settings.ollama_model, raw_response)

        result = _dict_to_result(parsed, email.uid, self._settings.ollama_model)
        if result is None:
            return _build_fallback_result(email.uid, self._settings.ollama_model, raw_response)

        logger.debug(
            "Classified email %s → %s (%s) confidence=%d%%",
            email.uid,
            result.category.value,
            result.priority.value,
            result.confidence,
        )
        return result

    def _call_ollama(self, payload: dict) -> str:
        """Send a chat request to the Ollama API and return the message content.

        Args:
            payload: JSON payload for the /api/chat endpoint.

        Returns:
            The text content from the model's response message.

        Raises:
            httpx.TimeoutException: If the request exceeds the configured timeout.
            httpx.NetworkError: If the network connection fails.
            httpx.HTTPStatusError: If the server returns a 4xx/5xx status.
        """
        with httpx.Client(timeout=self._settings.ollama_timeout) as client:
            response = client.post(self._api_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
