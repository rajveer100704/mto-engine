# =============================================================================
# MTO Extractor — orchestrates provider call + Pydantic validation
# =============================================================================
from __future__ import annotations

from PIL import Image

from providers.base import VisionExtractionProvider
from pipeline.rule_engine import apply_rules
from schemas.mto import MTOResponse, JobStatus


def extract_mto(image: Image.Image, provider: VisionExtractionProvider) -> dict:
    """Synchronous extraction wrapper.

    This is called from the async extraction service via run_in_executor.
    Returns raw dict (pre-Pydantic) for easier rule engine application.
    """
    import asyncio

    loop = asyncio.new_event_loop()
    try:
        raw = loop.run_until_complete(provider.extract(image))
    finally:
        loop.close()

    # Apply deterministic engineering rules
    raw = apply_rules(raw)
    return raw


async def extract_mto_async(image: Image.Image, provider: VisionExtractionProvider) -> dict:
    """Async version — awaits provider directly."""
    raw = await provider.extract(image)
    raw = apply_rules(raw)
    return raw
