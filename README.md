# IsometricMTO — AI-Powered Material Take-Off Generator

> **Pathnovo Full-Stack AI Engineer Internship Assessment**

Upload a piping isometric drawing (PNG, JPG, or PDF) and receive a complete, engineer-validated **Material Take-Off (MTO)** in seconds. The AI pipeline is powered by **Google Gemini 2.5 Flash Vision**, with a deterministic **Engineering Rule Engine** for post-processing. No API key? The app runs with a clearly-labelled mock MTO.

---

## Screenshots

| Upload Page | Processing Timeline | Results Dashboard |
|---|---|---|
| Drag & drop zone + feature cards | Step-by-step pipeline progress | Two-column: drawing + MTO table |

---

## Architecture

```
User → Upload PNG/JPG/PDF
         ↓
   Next.js 15 (App Router, TypeScript, Tailwind CSS)
         ↓  POST /api/upload → { job_id, status: PENDING }
   FastAPI Backend
         ↓
   ExtractionService (job lifecycle manager)
         ↓
   Pipeline:
     1.  Validate file (type, size, content)
     2.  PDF Render (pdf2image → PIL Image)
     3.  Image Enhancement (contrast ×1.3, sharpness ×1.4)
     4.  VisionExtractionProvider (factory-selected)
           ├── GeminiVisionProvider  (GOOGLE_API_KEY set)
           └── MockVisionProvider    (graceful fallback)
     5.  Pydantic Validation (strict schema enforcement)
     6.  Engineering Rule Engine (deterministic post-processing)
           ├── Derive gasket count from flanged joints
           ├── Derive bolt sets from flanged joints
           ├── Normalize NPS (6" not "6 inch")
           ├── Normalize schedule/rating strings
           ├── Clamp confidence → [0.0, 1.0]
           ├── Infer missing material specs from defaults
           └── Validate / coerce quantities
     7.  Summary Generator (recompute totals from items)
         ↓
   REST API (polling GET /api/mto/{job_id})
         ↓
   Two-column Results Dashboard:
     Left:  Sticky drawing preview + metadata chips + extraction report
     Right: Summary cards + MTO table + CSV export
```

---

## Folder Structure

```
isometric-mto/
├── backend/
│   ├── api/
│   │   └── routes.py            # FastAPI routes (upload, poll, CSV, health)
│   ├── pipeline/
│   │   ├── preprocessor.py      # PDF render + image enhancement
│   │   ├── extractor.py         # Calls provider + rule engine
│   │   └── rule_engine.py       # ← Engineering Rule Engine (deterministic)
│   ├── providers/
│   │   ├── base.py              # VisionExtractionProvider ABC
│   │   ├── gemini_provider.py   # GeminiVisionProvider (Gemini 2.5 Flash)
│   │   ├── mock_provider.py     # MockVisionProvider (no key needed)
│   │   └── factory.py           # Provider selection logic
│   ├── prompts/
│   │   ├── system_prompt.py     # Piping engineer persona + instructions
│   │   └── response_schema.py   # JSON schema (shared: Gemini + Pydantic)
│   ├── schemas/
│   │   └── mto.py               # Pydantic models + JobStatus enum
│   ├── services/
│   │   ├── job_store.py         # In-memory UUID job store
│   │   └── extraction_service.py # ExtractionService (orchestrates pipeline)
│   ├── tests/
│   │   ├── test_upload.py       # API endpoint tests
│   │   ├── test_schema.py       # Pydantic validation tests
│   │   ├── test_mock.py         # Mock provider tests
│   │   ├── test_csv.py          # CSV generation tests
│   │   └── test_rule_engine.py  # ← Rule engine determinism tests
│   ├── utils/
│   │   └── csv_generator.py     # pandas CSV with metadata header
│   ├── main.py                  # FastAPI app + CORS
│   ├── pytest.ini
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Upload home page
│   │   ├── layout.tsx           # Root layout, Inter font, SEO metadata
│   │   └── results/[jobId]/
│   │       └── page.tsx         # Two-column results dashboard
│   ├── components/
│   │   ├── layout/Header.tsx    # Sticky app header
│   │   ├── upload/
│   │   │   ├── UploadZone.tsx          # Drag-drop + validation
│   │   │   └── ProcessingTimeline.tsx   # Step timeline
│   │   └── mto/
│   │       ├── MTOTable.tsx            # Searchable/sortable table
│   │       ├── SummaryCards.tsx        # KPI summary cards
│   │       ├── MetadataChips.tsx       # Drawing metadata badges
│   │       ├── ExtractionReport.tsx    # AI pipeline metrics panel
│   │       └── ExportButton.tsx        # CSV download
│   ├── hooks/useUpload.ts       # Upload state machine (idle→done)
│   ├── lib/api.ts               # Typed API client
│   ├── types/mto.ts             # TypeScript interfaces
│   └── Dockerfile
│
├── samples/                     # Sample isometric drawings for testing
├── docker-compose.yml
├── .env.example
└── README.md                    # ← This file
```

---

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Clone / unzip the project
cd isometric-mto

# 2. Configure environment
cp .env.example .env
# Optional: add your GOOGLE_API_KEY to .env for live AI extraction

# 3. Start both services
docker compose up

# Frontend → http://localhost:3000
# Backend API → http://localhost:8000
# Swagger UI → http://localhost:8000/docs
```

### Option 2: Local Development

**Backend**
```bash
cd backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Configure
cp ../.env.example .env
# Edit .env: add GOOGLE_API_KEY (optional)

uvicorn main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev   # → http://localhost:3000
```

---

## Mock Mode

The app **always works** without an API key.

| Condition | Behaviour |
|-----------|-----------|
| `GOOGLE_API_KEY` not set | MockVisionProvider used automatically |
| `AI_PROVIDER=mock` in `.env` | MockVisionProvider forced |
| Mock active | All responses include `"mock": true`, UI shows **MOCK** badge |

The mock MTO is based on the XTechs Testings Pvt Ltd CDU-II Loop-3 sample isometric and includes realistic pipe lengths, fittings, flanges, valves, gaskets, and bolt sets.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload drawing → returns `{ job_id, status }` |
| `GET` | `/api/mto/{job_id}` | Poll status → returns progress + full result when complete |
| `GET` | `/api/mto/{job_id}/csv` | Download MTO as CSV file |
| `GET` | `/api/health` | Liveness check |
| `GET` | `/docs` | Swagger UI |

**Example poll response (completed):**
```json
{
  "job_id": "550e8400-...",
  "status": "completed",
  "progress": 100,
  "current_step": "MTO Generated",
  "mock": false,
  "processing_time_ms": 2412,
  "result": {
    "drawing_meta": { "drawing_no": "ISO-001", "revision": "A", ... },
    "items": [ ... ],
    "summary": { "total_pipe_length_m": 24.8, "fittings": 17, ... },
    "metrics": { "provider": "Gemini gemini-2.5-flash", "average_confidence": 0.91, ... }
  }
}
```

---

## Pipeline Design Decisions

### ExtractionService Layer
API routes delegate to `ExtractionService`, not the pipeline directly. This separates HTTP concerns from business logic and keeps routes thin.

### Provider Abstraction
```python
class VisionExtractionProvider(ABC):
    async def extract(self, image: PIL.Image) -> dict: ...
```
The factory reads `GOOGLE_API_KEY` and `AI_PROVIDER` env vars and returns the correct concrete implementation. New providers (e.g., Azure Vision, Claude) are added by implementing this interface alone.

### Engineering Rule Engine (Key Design Decision)
All business rules live in `pipeline/rule_engine.py`, **not in the LLM prompt**. This is the most important architectural choice:

The pipeline intentionally separates probabilistic AI extraction from deterministic engineering rules. Gemini is responsible only for understanding the drawing, while all engineering calculations (bolt sets, gasket derivation, unit normalization, summary generation) are implemented in deterministic Python services for reproducibility and easier testing.

- **Deterministic**: bolt sets are always `flanges // 2`, regardless of what the LLM outputs
- **Testable**: `test_rule_engine.py` verifies business rules independently of the AI
- **Maintainable**: rules change without touching the prompt
- **Interview answer**: "We don't trust the LLM for arithmetic — we derive consumables from the flange count"

### Prompt Strategy
The prompt is split into two files:
- `system_prompt.py`: piping engineer persona, recognition guide, material defaults
- `response_schema.py`: JSON schema used as both Gemini `response_schema` param and Pydantic model

Gemini is called with `response_mime_type="application/json"` — no regex parsing required.

### Confidence Visualization
- **Green** `≥90%`: clear symbol with readable annotation
- **Yellow** `70–89%`: visible but partially legible
- **Red** `<70%`: inferred or uncertain — review required

---

## Testing

```bash
cd backend
pytest tests/ -v
```

| Test File | Coverage |
|-----------|----------|
| `test_upload.py` | Upload endpoint, validation, 404 |
| `test_schema.py` | Pydantic model validation |
| `test_mock.py` | Mock provider + rule engine integration |
| `test_csv.py` | CSV bytes, headers, item data |
| `test_rule_engine.py` | Confidence clamping, NPS normalization, bolt/gasket derivation |

---

## Accuracy Expectations

### Current Strengths
- **Digital isometric drawings**: High legibility results in near-perfect extraction rates.
- **Standard engineering symbols**: Recognizes ASME/ANSI symbols (valves, elbows, flanges) consistently.
- **Printed title blocks**: Text block extraction is highly reliable.

### Known Limitations
- **Low-resolution scans**: Small text annotation or dimension markings can be misread.
- **Handwritten annotations**: Inconsistent writing styles may result in lower confidence scores.
- **Highly rotated drawings**: Orientation skew can degrade OCR results.

### Future Work
- **OCR Fusion**: Combine localized text OCR with overall layout parsing.
- **Symbol Detection Model**: Train a fine-tuned CNN/YOLO model solely for drawing components, feeding coordinate boundaries to Gemini.
- **Multi-page PDFs**: Support drawings split across multiple sheets.
- **Human-in-the-loop Validation**: An interactive UI diff editor for engineers to adjust anomalies before ERP import.

---

## Performance & Scale

- **Typical Processing Time**:
  - **Mock Mode**: ~1.8 seconds (simulated network latency for optimal UI visualization).
  - **Gemini Vision Mode**: ~3–8 seconds depending on image resolution, network latency, and Google API response times.
- **Resource Usage**:
  - **Memory**: < 250 MB total RAM for both containers in Docker.
  - **CPU**: Minimal CPU usage; image processing (Pillow/pdf2image) runs in O(1) time per request.
- **Limits**:
  - **Supported File Sizes**: Configured up to 20 MB max file size.
  - **Single Page Only**: Currently accepts single-page files (PNG, JPG, PDF).

---

## Tradeoffs & Future Work

| Decision | Tradeoff | Future |
|----------|----------|--------|
| In-memory job store | No persistence; jobs lost on restart | Redis + persistent store |
| Single-page PDF only | Multi-sheet drawings not supported | Process all pages, merge MTOs |
| Synchronous rule engine | Runs in request thread | Move to background worker |
| No auth | Fine for demo | JWT + project-scoped access |
| No image storage | Drawing not re-viewable after upload | S3 / object storage |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.12, Pydantic v2 |
| AI | Google Gemini 2.5 Flash (Vision) |
| PDF Rendering | pdf2image + Poppler |
| Image Processing | Pillow |
| CSV Export | pandas |
| Testing | pytest, pytest-asyncio, httpx |
| Containerisation | Docker, Docker Compose |

---

## AI Assistance Disclaimer

AI coding assistants (Gemini, Claude, ChatGPT, Cursor) were utilized during the development of this project to accelerate implementation, UI generation, and unit testing. Every design pattern (such as the provider abstraction and the decoupled engineering rule engine), component, and line of code has been thoroughly reviewed, understood, and validated to ensure reliability and engineering correctness.

---

*Submitted for the Pathnovo Full-Stack AI Engineer Internship Assessment.*
