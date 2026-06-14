"""Integration tests for the Pipeline class.

Uses respx to mock Ollama responses so no real network or IMAP
connection is required. Loads all 5 .eml fixture files and asserts
that the pipeline produces one valid ClassificationResult per file.
"""

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest
import respx

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from email_agent import display as real_display_module
from email_agent.classifier import Classifier
from email_agent.imap_reader import IMAPReader
from email_agent.models import Category
from email_agent.parser import EmailParser
from email_agent.pipeline import Pipeline

OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _make_ollama_response(category: str = "General Inquiry") -> dict:
    """Build a mock Ollama /api/chat response for the given category.

    Args:
        category: Category string the model should return.

    Returns:
        Dict matching the Ollama /api/chat response schema.
    """
    payload = {
        "category": category,
        "priority": "LOW",
        "summary": "Integration test email summary placeholder",
        "recommended_action": "Review as part of integration test",
        "confidence": 80,
    }
    return {"message": {"role": "assistant", "content": json.dumps(payload)}}


def _build_silent_display() -> types.ModuleType:
    """Return a module-like object that silences all display output during tests.

    Returns:
        A mock module with all display functions replaced by no-ops.
    """
    mock_display = types.SimpleNamespace(
        print_classification_result=MagicMock(),
        print_scan_header=MagicMock(),
        print_scan_complete=MagicMock(),
        print_error=MagicMock(),
        print_test_mode_banner=MagicMock(),
    )
    return mock_display  # type: ignore[return-value]


@respx.mock
def test_pipeline_test_mode(settings_fixture, sample_eml_dir):
    """Run pipeline.run_test_mode() against all 5 fixture .eml files.

    Asserts:
    - Exactly 5 results are returned (one per fixture).
    - All results have a valid (non-None) category.
    - All results have confidence > 0 (model responded, not fallback).
    """
    # Mock Ollama to return valid JSON for every call
    respx.post(OLLAMA_ENDPOINT).mock(
        return_value=httpx.Response(200, json=_make_ollama_response("General Inquiry"))
    )

    reader = IMAPReader(settings_fixture)
    parser = EmailParser()
    classifier = Classifier(settings_fixture)
    silent_display = _build_silent_display()

    pipeline = Pipeline(settings_fixture, reader, parser, classifier, silent_display)

    results = pipeline.run_test_mode(sample_eml_dir)

    assert len(results) == 5, f"Expected 5 results, got {len(results)}"

    for result in results:
        assert result.category is not None, "Category should be set"
        assert isinstance(result.category, Category), "Category must be a Category enum member"
        assert result.confidence > 0, "Confidence should be > 0 when model responds"
