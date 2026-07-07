import os
import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport
from PIL import Image

from main import app
from providers.factory import create_provider
from providers.mock_provider import MockVisionProvider
from providers.gemini_provider import GeminiVisionProvider
from schemas.mto import ProviderType, JobStatus


def test_factory_mock_choice():
    """Mock choice always returns MockVisionProvider."""
    provider, is_mock = create_provider(ProviderType.MOCK)
    assert isinstance(provider, MockVisionProvider)
    assert is_mock is True


def test_factory_gemini_choice_without_key_falls_back():
    """Gemini choice falls back to MockVisionProvider if key is missing."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}):
        provider, is_mock = create_provider(ProviderType.GEMINI)
        assert isinstance(provider, MockVisionProvider)
        assert is_mock is True


def test_factory_gemini_choice_with_key():
    """Gemini choice returns GeminiVisionProvider if key is present."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "AIzaSyDummyKey"}):
        provider, is_mock = create_provider(ProviderType.GEMINI)
        assert isinstance(provider, GeminiVisionProvider)
        assert is_mock is False


@pytest.mark.asyncio
async def test_upload_api_with_provider_mock():
    """Upload endpoint correctly parses and handles provider='mock'."""
    from PIL import Image as PILImage
    import io

    # Create a 10x10 white PNG in memory
    img = PILImage.new("RGB", (10, 10), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/upload",
            files={"file": ("test.png", buf, "image/png")},
            data={"provider": "mock"},
        )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"
