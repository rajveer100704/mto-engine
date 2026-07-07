# =============================================================================
# Provider Factory — selects provider based on environment configuration
# =============================================================================
from __future__ import annotations

import os

from providers.base import VisionExtractionProvider


def create_provider() -> tuple[VisionExtractionProvider, bool]:
    """Create and return the appropriate provider.

    Selection logic:
    1. If AI_PROVIDER=mock → MockVisionProvider (explicit override)
    2. If GOOGLE_API_KEY is set → GeminiVisionProvider
    3. Otherwise → MockVisionProvider (graceful degradation)

    Returns:
        Tuple of (provider, is_mock)
    """
    explicit_provider = os.getenv("AI_PROVIDER", "").lower()
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()

    if explicit_provider == "mock" or not api_key:
        from providers.mock_provider import MockVisionProvider
        return MockVisionProvider(), True

    try:
        from providers.gemini_provider import GeminiVisionProvider
        return GeminiVisionProvider(), False
    except Exception:
        # Fallback to mock if Gemini init fails
        from providers.mock_provider import MockVisionProvider
        return MockVisionProvider(), True
