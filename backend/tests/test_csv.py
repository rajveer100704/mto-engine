"""Tests for CSV generator."""
from __future__ import annotations

import pytest
from schemas.mto import (
    DrawingMeta, ExtractionMetrics, JobStatus,
    MTOItem, MTOResponse, MTOSummary,
)
from utils.csv_generator import generate_csv


def _make_mto() -> MTOResponse:
    return MTOResponse(
        job_id="test-123",
        status=JobStatus.COMPLETED,
        drawing_meta=DrawingMeta(drawing_no="ISO-001", revision="A", line_number='6"-P-1501-A1A'),
        items=[
            MTOItem(
                item_no=1, category="PIPE", description="Pipe, Seamless",
                size_nps='6"', schedule_rating="SCH 40",
                material_spec="ASTM A106 Gr.B", end_type="BW",
                quantity=1, unit="M", length_m=12.5, confidence=0.92,
            ),
            MTOItem(
                item_no=2, category="FITTING", description="Elbow 90° LR",
                size_nps='6"', schedule_rating="SCH 40",
                material_spec="ASTM A234 WPB", end_type="BW",
                quantity=3, unit="EA", confidence=0.88,
            ),
        ],
        summary=MTOSummary(total_pipe_length_m=12.5, fittings=3),
        metrics=ExtractionMetrics(
            provider="MockProvider", processing_time_ms=500,
            items_extracted=2, average_confidence=0.90, mock=True,
        ),
    )


def test_csv_is_bytes():
    mto = _make_mto()
    result = generate_csv(mto)
    assert isinstance(result, bytes)


def test_csv_contains_headers():
    mto = _make_mto()
    csv_str = generate_csv(mto).decode("utf-8")
    assert "Item No." in csv_str
    assert "Category" in csv_str
    assert "Description" in csv_str


def test_csv_contains_drawing_meta():
    mto = _make_mto()
    csv_str = generate_csv(mto).decode("utf-8")
    assert "ISO-001" in csv_str


def test_csv_contains_item_data():
    mto = _make_mto()
    csv_str = generate_csv(mto).decode("utf-8")
    assert "PIPE" in csv_str
    assert "FITTING" in csv_str
    assert "12.5" in csv_str
