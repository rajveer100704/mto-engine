# =============================================================================
# JSON Response Schema — shared by Gemini structured output and Pydantic
# =============================================================================

RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["drawing_meta", "items", "summary"],
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
                        "enum": ["BW", "SW", "THD", "FLGD", ""],
                    },
                    "quantity": {"type": "number"},
                    "unit": {"type": "string", "enum": ["EA", "M", "SET", "NO"]},
                    "length_m": {"type": "number"},
                    "confidence": {"type": "number"},
                    "remarks": {"type": "string"},
                },
            },
        },
        "summary": {
            "type": "object",
            "properties": {
                "total_pipe_length_m": {"type": "number"},
                "fittings": {"type": "integer"},
                "flanges": {"type": "integer"},
                "valves": {"type": "integer"},
                "gaskets": {"type": "integer"},
                "bolt_sets": {"type": "integer"},
                "supports": {"type": "integer"},
                "field_welds": {"type": "integer"},
            },
        },
    },
}

# User-turn prompt appended after the system instruction
EXTRACTION_USER_PROMPT = (
    "Analyze this piping isometric drawing. "
    "Extract ALL components visible and return the complete MTO JSON. "
    "Include every pipe segment, fitting, flange, valve, gasket set, bolt set, and support. "
    "Do NOT omit items due to low confidence — include them with a low confidence score and a remark. "
    "Return ONLY the JSON object. No markdown fences. No commentary."
)
