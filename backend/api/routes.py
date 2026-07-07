# =============================================================================
# FastAPI Routes
# =============================================================================
from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from schemas.mto import ErrorResponse, JobStatus, JobStatusResponse, UploadResponse, ProviderType
from services.job_store import job_store
from services.extraction_service import extraction_service
from utils.csv_generator import generate_csv

router = APIRouter(prefix="/api")

# Allowed content types
ALLOWED_TYPES = {"image/png", "image/jpeg", "image/jpg", "application/pdf"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Liveness check."""
    return {"status": "ok", "service": "isometric-mto-backend"}


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=202,
    tags=["Extraction"],
    summary="Upload an isometric drawing for MTO extraction",
)
async def upload_drawing(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File(description="PNG, JPG, or PDF isometric drawing (max 20 MB)")],
    provider: Annotated[ProviderType | None, Form(description="AI provider override: 'gemini' or 'mock'")] = None,
) -> UploadResponse:
    """Accept a drawing upload, create a job, and start background extraction."""

    # --- Server-side validation ---
    content_type = file.content_type or ""
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {content_type}. Accepted: PNG, JPG, PDF",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({len(file_bytes) // 1024 // 1024} MB). Maximum is 20 MB.",
        )

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Create job and kick off background task
    job = job_store.create()
    background_tasks.add_task(
        extraction_service.process_job,
        job,
        file_bytes,
        content_type,
        provider.value if provider else None,
    )

    return UploadResponse(
        job_id=job.job_id,
        status=JobStatus.PENDING,
        message="Job created. Poll /api/mto/{job_id} for status.",
    )


@router.get(
    "/mto/{job_id}",
    response_model=JobStatusResponse,
    tags=["Extraction"],
    summary="Get job status and MTO result",
)
async def get_mto(job_id: str) -> JobStatusResponse:
    """Poll for job status. Returns MTO result when status=completed."""
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        current_step=job.current_step,
        mock=job.mock,
        provider_requested=job.provider_requested,
        fallback=job.fallback,
        processing_time_ms=job.processing_time_ms,
        result=job.result,
        error=job.error,
    )


@router.get(
    "/mto/{job_id}/csv",
    tags=["Export"],
    summary="Download MTO as CSV",
)
async def get_mto_csv(job_id: str) -> Response:
    """Download the extracted MTO as a CSV file."""
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

    if job.status != JobStatus.COMPLETED or job.result is None:
        raise HTTPException(
            status_code=400,
            detail=f"Job {job_id} is not completed yet (status: {job.status}).",
        )

    csv_bytes = generate_csv(job.result)
    drawing_no = job.result.drawing_meta.drawing_no or job_id[:8]

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="MTO_{drawing_no}.csv"',
            "Content-Type": "text/csv; charset=utf-8",
        },
    )
