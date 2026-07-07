# =============================================================================
# Engineering Rule Engine — deterministic post-processing
# =============================================================================
"""All piping engineering business rules live here, NOT in the LLM prompt.

This separation ensures:
- Bolt sets are always correctly derived from flanged joints
- Confidence values are always valid floats in [0.0, 1.0]
- NPS strings are always normalized (6" not "6 inch" or "DN150")
- Quantities are always positive
- Material specs are inferred from category when Gemini omits them
- Gaskets are always 1 per flanged joint

The rule engine operates on raw dicts (post-provider, pre-Pydantic final validation)
and returns a clean, normalized dict.
"""
from __future__ import annotations

import re


# ---------------------------------------------------------------------------
# Default material specs by category
# ---------------------------------------------------------------------------
DEFAULT_MATERIALS: dict[str, str] = {
    "PIPE": "ASTM A106 Gr.B",
    "FITTING": "ASTM A234 WPB",
    "FLANGE": "ASTM A105",
    "VALVE": "ASTM A216 WCB",
    "GASKET": "SS316/Graphite, ASME B16.20",
    "BOLT": "ASTM A193 B7 / A194 2H",
    "SUPPORT": "ASTM A36",
}

DEFAULT_SCHEDULES: dict[str, str] = {
    "PIPE": "SCH 40",
    "FITTING": "SCH 40",
}

# NPS normalization: map common variants to canonical form
NPS_NORMALIZATION: dict[str, str] = {
    "1/2 inch": '1/2"', "1/2in": '1/2"', '0.5"': '1/2"',
    "3/4 inch": '3/4"', "3/4in": '3/4"', '0.75"': '3/4"',
    "1 inch": '1"', "1in": '1"',
    "1.5 inch": '1-1/2"', "1.5in": '1-1/2"', '1.5"': '1-1/2"',
    "2 inch": '2"', "2in": '2"',
    "3 inch": '3"', "3in": '3"',
    "4 inch": '4"', "4in": '4"',
    "6 inch": '6"', "6in": '6"',
    "8 inch": '8"', "8in": '8"',
    "10 inch": '10"', "10in": '10"',
    "12 inch": '12"', "12in": '12"',
}


def apply_rules(raw: dict) -> dict:
    """Apply all engineering rules to raw provider output.

    Args:
        raw: Dict matching RESPONSE_SCHEMA from provider.

    Returns:
        Cleaned and enriched dict ready for Pydantic MTOResponse validation.
    """
    raw = _normalize_items(raw)
    raw = _derive_consumables(raw)
    raw = _resequence_item_nos(raw)
    raw = _recompute_summary(raw)
    return raw


# ---------------------------------------------------------------------------
# Internal rule functions
# ---------------------------------------------------------------------------

def _normalize_items(raw: dict) -> dict:
    items = raw.get("items", [])
    normalized: list[dict] = []
    for item in items:
        item = _normalize_category(item)
        item = _normalize_nps(item)
        item = _normalize_schedule(item)
        item = _normalize_unit(item)
        item = _clamp_confidence(item)
        item = _infer_material(item)
        item = _normalize_quantity(item)
        item = _normalize_end_type(item)
        normalized.append(item)
    raw["items"] = normalized
    return raw


def _normalize_category(item: dict) -> dict:
    cat = str(item.get("category", "")).upper().strip()
    valid = {"PIPE", "FITTING", "FLANGE", "VALVE", "GASKET", "BOLT", "SUPPORT"}
    if cat not in valid:
        # Try common aliases
        aliases = {
            "ELBOW": "FITTING", "TEE": "FITTING", "REDUCER": "FITTING",
            "CAP": "FITTING", "COUPLING": "FITTING",
            "GATE": "VALVE", "GLOBE": "VALVE", "CHECK": "VALVE",
            "BALL": "VALVE", "BUTTERFLY": "VALVE",
            "WN FLANGE": "FLANGE", "WNF": "FLANGE",
            "STUD": "BOLT", "BOLT SET": "BOLT",
            "GASKET SET": "GASKET", "SPIRAL": "GASKET",
            "SHOE": "SUPPORT", "HANGER": "SUPPORT", "ANCHOR": "SUPPORT",
        }
        for alias, mapped in aliases.items():
            if alias in cat:
                cat = mapped
                break
        else:
            cat = "FITTING"  # safe default
    item["category"] = cat
    return item


def _normalize_nps(item: dict) -> dict:
    nps = str(item.get("size_nps", "")).strip()
    # Apply lookup table
    nps_lower = nps.lower()
    for variant, canonical in NPS_NORMALIZATION.items():
        if nps_lower == variant.lower():
            nps = canonical
            break
    # Ensure quotes present for numeric values
    if re.match(r"^\d+(\.\d+)?$", nps) or re.match(r"^\d+/\d+$", nps):
        nps = f'{nps}"'
    item["size_nps"] = nps or '?'
    return item


def _normalize_schedule(item: dict) -> dict:
    sched = str(item.get("schedule_rating", "")).strip().upper()
    if not sched:
        cat = item.get("category", "")
        sched = DEFAULT_SCHEDULES.get(cat, "")
    # Normalize common formats
    sched = sched.replace("SCHEDULE", "SCH").replace("SCH.", "SCH")
    # Normalize class rating
    sched = re.sub(r"CLASS\s*(\d+)", r"CL\1", sched)
    item["schedule_rating"] = sched
    return item


def _normalize_unit(item: dict) -> dict:
    unit = str(item.get("unit", "")).upper().strip()
    cat = item.get("category", "")
    if cat == "PIPE":
        item["unit"] = "M"
    elif cat == "BOLT":
        item["unit"] = "SET"
    elif unit not in ("EA", "M", "SET", "NO"):
        item["unit"] = "EA"
    else:
        item["unit"] = unit
    return item


def _clamp_confidence(item: dict) -> dict:
    """Clamp confidence to [0.0, 1.0] and round to 2 dp."""
    try:
        conf = float(item.get("confidence", 0.85))
    except (TypeError, ValueError):
        conf = 0.85
    item["confidence"] = round(max(0.0, min(1.0, conf)), 2)
    return item


def _infer_material(item: dict) -> dict:
    mat = str(item.get("material_spec", "")).strip()
    if not mat:
        cat = item.get("category", "")
        item["material_spec"] = DEFAULT_MATERIALS.get(cat, "")
    return item


def _normalize_quantity(item: dict) -> dict:
    try:
        qty = float(item.get("quantity", 1))
    except (TypeError, ValueError):
        qty = 1.0
    # Quantities must be > 0
    item["quantity"] = max(qty, 0.001)
    return item


def _normalize_end_type(item: dict) -> dict:
    et = str(item.get("end_type", "")).upper().strip()
    valid = {"BW", "SW", "THD", "FLGD", ""}
    if et not in valid:
        aliases = {
            "BUTT WELD": "BW", "BUTTWELD": "BW",
            "SOCKET WELD": "SW", "SOCKETWELD": "SW",
            "THREADED": "THD", "SCREWED": "THD",
            "FLANGED": "FLGD", "FLANGE": "FLGD",
        }
        et = aliases.get(et, "BW")
    item["end_type"] = et
    return item


def _derive_consumables(raw: dict) -> dict:
    """Derive gaskets and bolt sets from flanged joints if not present.

    A flanged joint = any FLANGE item (each flange is one face of a joint).
    Joints = flanges / 2 (pairs).
    Valves with FLGD end type also require flanges, but they come with their
    own flanges — we count them separately.
    """
    items: list[dict] = raw.get("items", [])

    # Count existing gaskets and bolt sets
    existing_gaskets = sum(
        int(i.get("quantity", 0)) for i in items if i.get("category") == "GASKET"
    )
    existing_bolts = sum(
        int(i.get("quantity", 0)) for i in items if i.get("category") == "BOLT"
    )

    # Count flanged joints
    flange_count = sum(
        int(i.get("quantity", 0)) for i in items if i.get("category") == "FLANGE"
    )
    flanged_valves = sum(
        int(i.get("quantity", 0))
        for i in items
        if i.get("category") == "VALVE" and i.get("end_type") == "FLGD"
    )
    # Each flanged valve has 2 flanged faces = 2 joints
    joint_count = (flange_count // 2) + flanged_valves * 2

    if joint_count <= 0:
        return raw

    next_item_no = max((i.get("item_no", 0) for i in items), default=0) + 1

    # Add gaskets if missing
    if existing_gaskets == 0 and joint_count > 0:
        nps = _dominant_nps(items)
        sched = _dominant_schedule(items)
        items.append({
            "item_no": next_item_no,
            "category": "GASKET",
            "description": "Spiral Wound Gasket, SS316/Graphite, ASME B16.20",
            "size_nps": nps,
            "schedule_rating": sched,
            "material_spec": "SS316/Graphite, ASME B16.20",
            "end_type": "FLGD",
            "quantity": joint_count,
            "unit": "EA",
            "confidence": 0.95,
            "remarks": "Derived — 1 per flanged joint",
        })
        next_item_no += 1

    # Add bolt sets if missing
    if existing_bolts == 0 and joint_count > 0:
        nps = _dominant_nps(items)
        sched = _dominant_schedule(items)
        items.append({
            "item_no": next_item_no,
            "category": "BOLT",
            "description": "Stud Bolt with 2 Hex Nuts, ASME B18.2.1",
            "size_nps": nps,
            "schedule_rating": sched,
            "material_spec": "ASTM A193 B7 / A194 2H",
            "end_type": "FLGD",
            "quantity": joint_count,
            "unit": "SET",
            "confidence": 0.95,
            "remarks": "Derived — 1 set per flanged joint",
        })

    raw["items"] = items
    return raw


def _dominant_nps(items: list[dict]) -> str:
    """Return the most common NPS among pipe items."""
    pipe_nps = [i.get("size_nps", '?') for i in items if i.get("category") == "PIPE"]
    if not pipe_nps:
        return '?'
    return max(set(pipe_nps), key=pipe_nps.count)


def _dominant_schedule(items: list[dict]) -> str:
    """Return CL150 default for flanges (most common in process piping)."""
    flange_scheds = [
        i.get("schedule_rating", "CL150")
        for i in items
        if i.get("category") in ("FLANGE", "VALVE")
    ]
    if not flange_scheds:
        return "CL150"
    return max(set(flange_scheds), key=flange_scheds.count)


def _resequence_item_nos(raw: dict) -> dict:
    for idx, item in enumerate(raw.get("items", []), start=1):
        item["item_no"] = idx
    return raw


def _recompute_summary(raw: dict) -> dict:
    """Recompute summary totals from the validated items list."""
    items = raw.get("items", [])

    total_pipe_m = sum(
        float(i.get("length_m") or 0) for i in items if i.get("category") == "PIPE"
    )
    fittings = sum(int(i.get("quantity", 0)) for i in items if i.get("category") == "FITTING")
    flanges = sum(int(i.get("quantity", 0)) for i in items if i.get("category") == "FLANGE")
    valves = sum(int(i.get("quantity", 0)) for i in items if i.get("category") == "VALVE")
    gaskets = sum(int(i.get("quantity", 0)) for i in items if i.get("category") == "GASKET")
    bolt_sets = sum(int(i.get("quantity", 0)) for i in items if i.get("category") == "BOLT")
    supports = sum(int(i.get("quantity", 0)) for i in items if i.get("category") == "SUPPORT")
    field_welds = raw.get("summary", {}).get("field_welds", 0)

    raw["summary"] = {
        "total_pipe_length_m": round(total_pipe_m, 3),
        "fittings": fittings,
        "flanges": flanges,
        "valves": valves,
        "gaskets": gaskets,
        "bolt_sets": bolt_sets,
        "supports": supports,
        "field_welds": field_welds,
    }
    return raw
