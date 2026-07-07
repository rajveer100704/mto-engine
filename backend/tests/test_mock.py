"""Tests for MockVisionProvider."""
from __future__ import annotations

import asyncio
import pytest
from PIL import Image
from providers.mock_provider import MockVisionProvider
from pipeline.rule_engine import apply_rules


def test_mock_provider_name():
    p = MockVisionProvider()
    assert "Mock" in p.name


@pytest.mark.asyncio
async def test_mock_provider_returns_valid_structure():
    p = MockVisionProvider()
    img = Image.new("RGB", (100, 100))
    result = await p.extract(img)

    assert "drawing_meta" in result
    assert "items" in result
    assert "summary" in result
    assert len(result["items"]) > 0


@pytest.mark.asyncio
async def test_mock_provider_after_rule_engine():
    p = MockVisionProvider()
    img = Image.new("RGB", (100, 100))
    raw = await p.extract(img)
    normalized = apply_rules(raw)

    # All item_nos should be sequential
    item_nos = [i["item_no"] for i in normalized["items"]]
    assert item_nos == list(range(1, len(item_nos) + 1))

    # All confidences in range
    for item in normalized["items"]:
        assert 0.0 <= item["confidence"] <= 1.0

    # Summary should be populated
    assert normalized["summary"]["total_pipe_length_m"] > 0

