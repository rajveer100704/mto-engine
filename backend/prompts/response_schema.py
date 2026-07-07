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
EXTRACTION_USER_PROMPT = """Analyze this piping isometric drawing and extract a complete Material Take-Off.

Carefully inspect the ENTIRE drawing before generating output.
Do not stop after identifying the first few components.
Zoom mentally into every region of the drawing.

Read all callouts.
Read all leader annotations.
Read all dimensions.
Read all symbols.
Read all balloons.
Read all pipe labels.
Read all valve tags.
Read all fitting symbols.
Read all flange symbols.
Read all reducers.
Read all branch connections.
Read all support symbols.
Read all weld symbols.
Read all continuation arrows.
Read all elevation markers.
Read every pipeline segment individually.

Every visible engineering object should become one MTO item.

Extract at minimum:

PIPE
- straight pipe
- spool pieces
- pipe segments

FITTING
- elbows
- tees
- crosses
- reducers
- concentric reducers
- eccentric reducers
- caps
- couplings
- unions

FLANGE
- weld neck
- slip-on
- socket weld
- blind
- threaded

VALVE
- gate
- globe
- check
- ball
- butterfly
- plug
- control

SUPPORT
- shoes
- guides
- hangers
- spring supports
- clamps

GASKET

BOLT SET

For each item extract whenever visible:
- item_no
- category (PIPE | FITTING | FLANGE | VALVE | GASKET | BOLT | SUPPORT)
- description
- size_nps
- schedule_rating
- material_spec
- end_type
- quantity
- unit
- length_m
- confidence
- remarks

If length cannot be determined:
set length_m = 0

If schedule cannot be read:
return ""

If material specification cannot be read:
return ""

If end type cannot be read:
return ""

If quantity is uncertain:
estimate conservatively and reduce confidence.

Confidence Guidelines:
1.00 - Clearly visible and explicitly labeled.
0.90 - Clearly identifiable with readable annotation.
0.80 - Recognizable engineering symbol.
0.70 - Likely present but partially obscured.
0.50 - Visible but uncertain.

Never omit an item because confidence is low.
Unknown values should be empty strings instead of invented values.

Return ONLY one JSON object.
The JSON must strictly contain:
{
    "drawing_meta": {...},
    "items": [...]
}

Do NOT include:
- summary
- metrics
- warnings
- provider
- execution_time
- analysis
- thoughts
- markdown
- comments

Only return valid JSON."""
