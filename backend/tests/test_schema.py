"""Tests for Pydantic schema validation."""
from __future__ import annotations

import pytest
from schemas.mto import MTOItem, MTOSummary, DrawingMeta, JobStatus


def test_mto_item_category_uppercased():
    item = MTOItem(
        item_no=1, category="pipe", description="Pipe",
        size_nps='6"', quantity=1, unit="M"
    )
    assert item.category == "PIPE"


def test_mto_item_unit_uppercased():
    item = MTOItem(
        item_no=1, category="FITTING", description="Elbow",
        size_nps='6"', quantity=4, unit="ea"
    )
    assert item.unit == "EA"


def test_mto_item_confidence_default():
    item = MTOItem(
        item_no=1, category="PIPE", description="Pipe",
        size_nps='6"', quantity=1, unit="M"
    )
    assert 0.0 <= item.confidence <= 1.0


def test_job_status_enum():
    assert JobStatus.PENDING == "pending"
    assert JobStatus.COMPLETED == "completed"
    assert JobStatus.FAILED == "failed"
    assert JobStatus.PROCESSING == "processing"


def test_drawing_meta_defaults():
    meta = DrawingMeta()
    assert meta.drawing_no == ""
    assert meta.revision == ""
