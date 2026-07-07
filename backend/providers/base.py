# =============================================================================
# VisionExtractionProvider — Abstract Base Class
# =============================================================================
from __future__ import annotations

from abc import ABC, abstractmethod
from PIL import Image


class VisionExtractionProvider(ABC):
    """Abstract interface for all vision AI extraction providers.

    Concrete implementations:
    - GeminiVisionProvider   : Google Gemini 2.5 Flash
    - MockVisionProvider     : Returns deterministic test data (no API key needed)
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider name e.g. 'Gemini 2.5 Flash'."""
        ...

    @abstractmethod
    async def extract(self, image: Image.Image) -> dict:
        """Extract raw MTO JSON from an image.

        Args:
            image: PIL Image (preprocessed, RGB, ≤ 4096 px on longest side)

        Returns:
            Raw dict matching RESPONSE_SCHEMA structure.
            Raises ProviderError on failure.
        """
        ...


class ProviderError(Exception):
    """Raised when a provider fails to return usable data."""

    def __init__(self, provider: str, detail: str) -> None:
        self.provider = provider
        self.detail = detail
        super().__init__(f"[{provider}] {detail}")
