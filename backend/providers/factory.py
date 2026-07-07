# =============================================================================
# Provider Factory — selects provider based on environment configuration
# =============================================================================
from __future__ import annotations

import os

import logging
from providers.base import VisionExtractionProvider
from schemas.mto import ProviderType

logger = logging.getLogger(__name__)


def create_provider(override: ProviderType | None = None) -> tuple[VisionExtractionProvider, bool]:
    """Create and return the appropriate provider.

    Selection logic:
    1. If override is specified, try to use it.
       If override is gemini but GOOGLE_API_KEY is missing, log warning and fallback to mock.
    2. Otherwise, check AI_PROVIDER env var.
    3. If neither is specified/valid, fallback to gemini if GOOGLE_API_KEY is present, else mock.

    Returns:
        Tuple of (provider, is_mock)
    """
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    # Determine desired provider choice
    choice = override
    if not choice:
        env_val = os.getenv("AI_PROVIDER", "").lower()
        if env_val == "mock":
            choice = ProviderType.MOCK
        elif env_val == "gemini":
            choice = ProviderType.GEMINI

    # Apply choice logic
    if choice == ProviderType.MOCK:
        from providers.mock_provider import MockVisionProvider
        return MockVisionProvider(), True

    if choice == ProviderType.GEMINI:
        if not api_key:
            logger.warning("Gemini provider requested but GOOGLE_API_KEY is not set. Falling back to Mock.")
            from providers.mock_provider import MockVisionProvider
            return MockVisionProvider(), True
        try:
            from providers.gemini_provider import GeminiVisionProvider
            return GeminiVisionProvider(), False
        except Exception as e:
            logger.error(f"Failed to initialize GeminiVisionProvider: {e}. Falling back to Mock.")
            from providers.mock_provider import MockVisionProvider
            return MockVisionProvider(), True

    # Default fallback when no specific choice is requested
    if api_key:
        try:
            from providers.gemini_provider import GeminiVisionProvider
            return GeminiVisionProvider(), False
        except Exception:
            pass

    from providers.mock_provider import MockVisionProvider
    return MockVisionProvider(), True
