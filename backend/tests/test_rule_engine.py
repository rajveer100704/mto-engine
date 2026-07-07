"""Tests for the Engineering Rule Engine — deterministic post-processing."""
from __future__ import annotations

import pytest
from pipeline.rule_engine import apply_rules, _clamp_confidence, _normalize_nps, _derive_consumables


# ---------------------------------------------------------------------------
# Confidence clamping
# ---------------------------------------------------------------------------

class TestConfidenceClamping:
    def test_valid_confidence_unchanged(self):
        item = {"confidence": 0.85, "category": "PIPE", "size_nps": "6\"",
                 "quantity": 1, "unit": "M"}
        result = _clamp_confidence(item)
        assert result["confidence"] == 0.85

    def test_confidence_above_1_clamped(self):
        item = {"confidence": 1.5, "category": "PIPE", "size_nps": "6\"",
                 "quantity": 1, "unit": "M"}
        result = _clamp_confidence(item)
        assert result["confidence"] == 1.0

    def test_confidence_below_0_clamped(self):
        item = {"confidence": -0.3, "category": "PIPE", "size_nps": "6\"",
                 "quantity": 1, "unit": "M"}
        result = _clamp_confidence(item)
        assert result["confidence"] == 0.0

    def test_confidence_string_converted(self):
        item = {"confidence": "0.9", "category": "PIPE", "size_nps": "6\"",
                 "quantity": 1, "unit": "M"}
        result = _clamp_confidence(item)
        assert result["confidence"] == 0.9

    def test_confidence_invalid_defaults_to_0_85(self):
        item = {"confidence": "bad_value", "category": "PIPE", "size_nps": "6\"",
                 "quantity": 1, "unit": "M"}
        result = _clamp_confidence(item)
        assert result["confidence"] == 0.85


# ---------------------------------------------------------------------------
# NPS normalization
# ---------------------------------------------------------------------------

class TestNPSNormalization:
    def test_quoted_nps_unchanged(self):
        item = {"size_nps": '6"', "category": "PIPE", "quantity": 1, "unit": "M", "confidence": 0.9}
        result = _normalize_nps(item)
        assert result["size_nps"] == '6"'

    def test_numeric_nps_gets_quotes(self):
        item = {"size_nps": "6", "category": "PIPE", "quantity": 1, "unit": "M", "confidence": 0.9}
        result = _normalize_nps(item)
        assert result["size_nps"] == '6"'

    def test_text_nps_normalized(self):
        item = {"size_nps": "6 inch", "category": "PIPE", "quantity": 1, "unit": "M", "confidence": 0.9}
        result = _normalize_nps(item)
        assert result["size_nps"] == '6"'

    def test_decimal_nps_normalized(self):
        item = {"size_nps": "1.5\"", "category": "PIPE", "quantity": 1, "unit": "M", "confidence": 0.9}
        result = _normalize_nps(item)
        assert '"' in result["size_nps"]


# ---------------------------------------------------------------------------
# Bolt set and gasket derivation
# ---------------------------------------------------------------------------

class TestConsumableDerivation:
    def _make_raw(self, flange_qty: int, valve_qty: int = 0) -> dict:
        items = []
        items.append({
            "item_no": 1, "category": "PIPE", "description": "Pipe",
            "size_nps": '6"', "schedule_rating": "SCH 40",
            "material_spec": "ASTM A106 Gr.B", "end_type": "BW",
            "quantity": 1, "unit": "M", "length_m": 10.0, "confidence": 0.9, "remarks": "",
        })
        if flange_qty > 0:
            items.append({
                "item_no": 2, "category": "FLANGE", "description": "WN Flange",
                "size_nps": '6"', "schedule_rating": "CL150",
                "material_spec": "ASTM A105", "end_type": "BW",
                "quantity": flange_qty, "unit": "EA", "confidence": 0.9, "remarks": "",
            })
        if valve_qty > 0:
            items.append({
                "item_no": 3, "category": "VALVE", "description": "Gate Valve",
                "size_nps": '6"', "schedule_rating": "CL150",
                "material_spec": "ASTM A216 WCB", "end_type": "FLGD",
                "quantity": valve_qty, "unit": "EA", "confidence": 0.9, "remarks": "",
            })
        return {"drawing_meta": {}, "items": items, "summary": {}}

    def test_bolt_sets_derived_from_flanges(self):
        raw = self._make_raw(flange_qty=4)
        result = apply_rules(raw)
        bolt_items = [i for i in result["items"] if i["category"] == "BOLT"]
        assert len(bolt_items) == 1
        assert bolt_items[0]["quantity"] == 2  # 4 flanges / 2 = 2 joints

    def test_gaskets_derived_from_flanges(self):
        raw = self._make_raw(flange_qty=6)
        result = apply_rules(raw)
        gasket_items = [i for i in result["items"] if i["category"] == "GASKET"]
        assert len(gasket_items) == 1
        assert gasket_items[0]["quantity"] == 3  # 6 flanges / 2 = 3 joints

    def test_no_consumables_when_no_flanges(self):
        raw = self._make_raw(flange_qty=0)
        result = apply_rules(raw)
        bolt_items = [i for i in result["items"] if i["category"] == "BOLT"]
        gasket_items = [i for i in result["items"] if i["category"] == "GASKET"]
        assert len(bolt_items) == 0
        assert len(gasket_items) == 0

    def test_summary_recomputed(self):
        raw = self._make_raw(flange_qty=4)
        result = apply_rules(raw)
        assert result["summary"]["flanges"] == 4
        assert result["summary"]["bolt_sets"] == 2
        assert result["summary"]["gaskets"] == 2
        assert result["summary"]["total_pipe_length_m"] == 10.0

    def test_item_nos_resequenced(self):
        raw = self._make_raw(flange_qty=4)
        result = apply_rules(raw)
        item_nos = [i["item_no"] for i in result["items"]]
        assert item_nos == list(range(1, len(item_nos) + 1))
