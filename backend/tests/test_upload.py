"""Tests for FastAPI upload endpoint and health check."""
from __future__ import annotations

import io
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_upload_png_returns_job_id():
    """Happy path: upload a minimal PNG, expect a job_id back."""
    # Create a 10x10 white PNG in memory
    from PIL import Image as PILImage
    img = PILImage.new("RGB", (10, 10), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/upload",
            files={"file": ("test.png", buf, "image/png")},
        )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_upload_invalid_type_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/upload",
            files={"file": ("test.txt", b"hello", "text/plain")},
        )
    assert response.status_code == 415


@pytest.mark.asyncio
async def test_upload_empty_file_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/upload",
            files={"file": ("empty.png", b"", "image/png")},
        )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_mto_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/mto/nonexistent-id")
    assert response.status_code == 404
