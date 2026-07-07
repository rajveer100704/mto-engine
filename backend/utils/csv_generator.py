# =============================================================================
# CSV Generator — pandas-based MTO CSV export
# =============================================================================
from __future__ import annotations

import io

import pandas as pd

from schemas.mto import MTOResponse


COLUMNS = [
    "item_no", "category", "description", "size_nps",
    "schedule_rating", "material_spec", "end_type",
    "quantity", "unit", "length_m", "confidence", "remarks",
]

DISPLAY_HEADERS = [
    "Item No.", "Category", "Description", "Size (NPS)",
    "Schedule / Rating", "Material Spec", "End Type",
    "Quantity", "Unit", "Length (m)", "Confidence", "Remarks",
]


def generate_csv(mto: MTOResponse) -> bytes:
    """Generate UTF-8 encoded CSV bytes from an MTOResponse.

    Includes a metadata header block and the full items table.
    """
    buf = io.StringIO()

    # --- Header block ---
    meta = mto.drawing_meta
    buf.write(f"# IsometricMTO Export\n")
    buf.write(f"# Drawing No.,{meta.drawing_no}\n")
    buf.write(f"# Revision,{meta.revision}\n")
    buf.write(f"# Line Number,{meta.line_number}\n")
    buf.write(f"# NPS,{meta.nps}\n")
    buf.write(f"# Material Class,{meta.material_class}\n")
    buf.write(f"# Service,{meta.service}\n")
    buf.write(f"# Provider,{mto.metrics.provider}\n")
    buf.write(f"# Mock,{mto.metrics.mock}\n")
    buf.write(f"# Processing Time (ms),{mto.metrics.processing_time_ms}\n")
    buf.write(f"# Average Confidence,{mto.metrics.average_confidence:.0%}\n")
    buf.write("#\n")

    # --- Summary block ---
    s = mto.summary
    buf.write(f"# SUMMARY\n")
    buf.write(f"# Total Pipe Length (m),{s.total_pipe_length_m}\n")
    buf.write(f"# Fittings,{s.fittings}\n")
    buf.write(f"# Flanges,{s.flanges}\n")
    buf.write(f"# Valves,{s.valves}\n")
    buf.write(f"# Gaskets,{s.gaskets}\n")
    buf.write(f"# Bolt Sets,{s.bolt_sets}\n")
    buf.write(f"# Supports,{s.supports}\n")
    buf.write(f"# Field Welds,{s.field_welds}\n")
    buf.write("#\n")

    # --- Items table ---
    rows = []
    for item in mto.items:
        rows.append({
            "item_no": item.item_no,
            "category": item.category,
            "description": item.description,
            "size_nps": item.size_nps,
            "schedule_rating": item.schedule_rating,
            "material_spec": item.material_spec,
            "end_type": item.end_type,
            "quantity": item.quantity,
            "unit": item.unit,
            "length_m": item.length_m if item.length_m is not None else "",
            "confidence": f"{item.confidence:.0%}",
            "remarks": item.remarks,
        })

    df = pd.DataFrame(rows, columns=COLUMNS)
    df.columns = DISPLAY_HEADERS
    df.to_csv(buf, index=False)

    return buf.getvalue().encode("utf-8")
