# =============================================================================
# FastAPI Application Entry Point
# =============================================================================
from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # Load .env before anything else

from api.routes import router

app = FastAPI(
    title="Isometric MTO Generator API",
    description=(
        "AI-powered piping isometric drawing to Material Take-Off extraction. "
        "Upload a PNG/JPG/PDF isometric drawing and receive a structured MTO "
        "with pipe lengths, fittings, flanges, valves, gaskets, and bolt sets."
    ),
    version="1.0.0",
    contact={
        "name": "Pathnovo Assessment Submission",
    },
    license_info={"name": "MIT"},
)

# ---------------------------------------------------------------------------
# CORS — allow Next.js dev server and production frontend
# ---------------------------------------------------------------------------
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(router)


@app.get("/", tags=["Root"])
async def root() -> dict:
    return {
        "service": "Isometric MTO Generator",
        "docs": "/docs",
        "health": "/api/health",
    }
