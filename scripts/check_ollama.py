#!/usr/bin/env python3
"""Health-check script for Ollama availability and model readiness.

Usage:
    python scripts/check_ollama.py

Reads OLLAMA_BASE_URL and OLLAMA_MODEL from the environment (with defaults).
Exits with code 0 if all checks pass, code 1 if any check fails.
"""

import os
import sys

import httpx


def get_env_defaults() -> tuple[str, str]:
    """Read Ollama settings from environment variables with fallback defaults.

    Returns:
        Tuple of (base_url, model_name).
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
    return base_url, model


def check_ollama_running(base_url: str) -> list[str] | None:
    """Check if Ollama is running by hitting the /api/tags endpoint.

    Args:
        base_url: Base URL of the Ollama server.

    Returns:
        List of available model names on success, None on failure.
    """
    tags_url = f"{base_url}/api/tags"
    try:
        with httpx.Client(timeout=10) as client:
            response = client.get(tags_url)
            response.raise_for_status()
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            return models
    except httpx.ConnectError:
        return None
    except httpx.TimeoutException:
        return None
    except httpx.HTTPStatusError as exc:
        print(f"  HTTP error from Ollama: {exc.response.status_code}")
        return None


def check_model_available(available_models: list[str], target_model: str) -> bool:
    """Check whether the target model is in the available models list.

    Matching is prefix-based: 'qwen2.5:1.5b' matches 'qwen2.5:1.5b'
    or 'qwen2.5:1.5b-instruct-q4_0'.

    Args:
        available_models: List of model names returned by Ollama.
        target_model: The model name from settings.

    Returns:
        True if the model is available, False otherwise.
    """
    for name in available_models:
        if name == target_model or name.startswith(target_model.split(":")[0]):
            return True
    return False


def main() -> int:
    """Run all health checks and print their status.

    Returns:
        Exit code: 0 if all checks pass, 1 if any check fails.
    """
    base_url, model = get_env_defaults()
    all_passed = True

    print(f"\nOllama Health Check")
    print(f"{'=' * 40}")
    print(f"  URL:   {base_url}")
    print(f"  Model: {model}")
    print(f"{'=' * 40}")

    # Check 1: Is Ollama running?
    available_models = check_ollama_running(base_url)
    if available_models is None:
        print(f"❌  Ollama is NOT running at {base_url}")
        print(f"\n    To start Ollama: run 'ollama serve' in a terminal")
        return 1

    print(f"✅  Ollama is running at {base_url}")

    # Check 2: Is the required model available?
    model_found = check_model_available(available_models, model)
    if model_found:
        print(f"✅  Model '{model}' is available")
    else:
        print(f"❌  Model '{model}' is NOT available")
        all_passed = False

        if available_models:
            print(f"\n    Available models:")
            for name in available_models:
                print(f"      • {name}")
        else:
            print(f"\n    No models are currently pulled.")

        print(f"\n    To download the required model, run:")
        print(f"      ollama pull {model}")

    print(f"{'=' * 40}")
    if all_passed:
        print("✅  All checks passed — ready to run.\n")
        return 0

    print("❌  Some checks failed. See above for details.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
