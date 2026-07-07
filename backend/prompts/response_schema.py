# =============================================================================
# JSON Response Schema — shared by Gemini structured output and Pydantic
# =============================================================================

RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["drawing_meta", "items"],
    "properties": {
        "drawing_meta": {
            "type": "object",
            "properties": {
                "drawing_no": {"type": "string"},
                "revision": {"type": "string"},
                "line_number": {"type": "string"},
                "nps": {"type": "string"},
                "material_class": {"type": "string"},
                "service": {"type": "string"},
                "design_pressure": {"type": "string"},
                "design_temperature": {"type": "string"},
                "sheet_number": {"type": "string"},
            },
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["item_no", "category", "description", "size_nps", "quantity", "unit"],
                "properties": {
                    "item_no": {"type": "integer"},
                    "category": {
                        "type": "string",
                        "enum": ["PIPE", "FITTING", "FLANGE", "VALVE", "GASKET", "BOLT", "SUPPORT"],
                    },
                    "description": {"type": "string"},
                    "size_nps": {"type": "string"},
                    "schedule_rating": {"type": "string"},
                    "material_spec": {"type": "string"},
                    "end_type": {
                        "type": "string",
                        "enum": ["BW", "SW", "THD", "FLGD", "UNKNOWN"],
                    },
                    "quantity": {"type": "number"},
                    "unit": {"type": "string", "enum": ["EA", "M", "SET", "NO"]},
                    "length_m": {"type": "number"},
                    "confidence": {"type": "number"},
                    "remarks": {"type": "string"},
                },
            },
        },
    },
}

# User-turn prompt appended after the system instruction
EXTRACTION_USER_PROMPT = (
    "You are an expert piping engineering AI. Analyze this piping isometric drawing step-by-step to extract a complete MTO:\n\n"
    "Step 1: Read the drawing's title block and metadata. Look for the drawing number (e.g. 'ISO-1501-01' or 'XPRF-17'), "
    "revision (e.g. '0', '1', 'A'), line number (e.g. '6\"-P-1501-A1A-IH' or '2\"-P-LOOP3-A1A'), nominal pipe size (NPS), piping material class "
    "(e.g. 'A1A'), and service code.\n\n"
    "Step 2: Identify every pipe segment on the isometric spool. Look for size markings (e.g. 6\", 2\") and dimension line lengths (e.g. 18.6m, 12.45m).\n\n"
    "Step 3: Scan the drawing for all piping components. Identify:\n"
    "- FITTINGS: Elbows (90 deg, 45 deg), Tees, Reducers (concentric, eccentric), Caps, Couplings.\n"
    "- FLANGES: Weld neck flanges, Slip-on flanges, Blind flanges.\n"
    "- VALVES: Gate, Globe, Check, Ball, Butterfly valves (note if they are flanged or butt-welded).\n"
    "- SUPPORTS: Support tags or symbols (e.g. S-NO-xxx, shoes, hangers).\n\n"
    "Step 4: Do NOT count or derive gaskets and bolt sets (the backend rule engine will derive them). Focus solely on extracting explicit drawing items.\n\n"
    "Step 5: For each extracted item, specify:\n"
    "- item_no: sequential index\n"
    "- category: PIPE | FITTING | FLANGE | VALVE | GASKET | BOLT | SUPPORT\n"
    "- description: full description (e.g. 'Elbow 90 Deg LR, BW, ASME B16.9')\n"
    "- size_nps: size in inches (e.g. '6\"', '2\"')\n"
    "- schedule_rating: schedule or rating (e.g. 'SCH 40', 'CL150')\n"
    "- material_spec: ASTM grade if visible or leave empty\n"
    "- end_type: BW | SW | THD | FLGD | UNKNOWN\n"
    "- quantity: count or length\n"
    "- unit: EA | M | SET | NO\n"
    "- length_m: pipe segment length in meters (for PIPE items only)\n"
    "- confidence: confidence score from 0.0 to 1.0\n"
    "- remarks: any extra label or symbol information seen (e.g. 'CDU-II' or 'Tag V-101')\n\n"
    "Step 6: Return ONLY a valid JSON object matching the requested schema. No markdown fences. No commentary."
)
