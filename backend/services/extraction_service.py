# =============================================================================
# ExtractionService — orchestrates the full pipeline lifecycle
# =============================================================================
from __future__ import annotations

import time
import asyncio
from typing import Optional

from schemas.mto import (
    DrawingMeta, ExtractionMetrics, JobStatus,
    MTOItem, MTOResponse, MTOSummary,
)
from services.job_store import Job, job_store
from pipeline.preprocessor import preprocess
from pipeline.extractor import extract_mto_async
from providers.factory import create_provider


class ExtractionService:
    """Manages the full extraction lifecycle for a job.

    API routes call this service rather than the pipeline directly,
    keeping HTTP concerns separate from business logic.
    """

    async def process_job(self, job: Job, file_bytes: bytes, content_type: str) -> None:
        """Run the full extraction pipeline, updating job state at each step."""
        start_time = time.time()

        try:
            # --- Step 1: Mark as processing ---
            job_store.update(
                job.job_id,
                status=JobStatus.PROCESSING,
                progress=10,
                current_step="Validating file",
            )
            await asyncio.sleep(0)  # yield to event loop

            # --- Step 2: Preprocess ---
            job_store.update(job.job_id, progress=25, current_step="Rendering & enhancing image")
            await asyncio.sleep(0)
            image = preprocess(file_bytes, content_type)

            # --- Step 3: Create provider ---
            job_store.update(job.job_id, progress=40, current_step="Selecting AI provider")
            provider, is_mock = create_provider()

            # --- Step 4: AI Extraction ---
            job_store.update(
                job.job_id,
                progress=55,
                current_step=f"Running AI extraction ({provider.name})",
                mock=is_mock,
            )
            raw = await extract_mto_async(image, provider)

            # --- Step 5: Pydantic Validation ---
            job_store.update(job.job_id, progress=75, current_step="Validating & normalizing MTO")
            mto_response = self._build_response(job.job_id, raw, provider.name, is_mock, start_time)

            # --- Step 6: Complete ---
            elapsed_ms = int((time.time() - start_time) * 1000)
            job_store.update(
                job.job_id,
                status=JobStatus.COMPLETED,
                progress=100,
                current_step="MTO Generated",
                mock=is_mock,
                processing_time_ms=elapsed_ms,
                result=mto_response,
            )

        except Exception as exc:
            elapsed_ms = int((time.time() - start_time) * 1000)
            job_store.update(
                job.job_id,
                status=JobStatus.FAILED,
                progress=0,
                current_step="Failed",
                processing_time_ms=elapsed_ms,
                error=str(exc),
            )

    def _build_response(
        self,
        job_id: str,
        raw: dict,
        provider_name: str,
        is_mock: bool,
        start_time: float,
    ) -> MTOResponse:
        """Validate raw dict against Pydantic models and build MTOResponse."""

        # Drawing metadata
        meta_raw = raw.get("drawing_meta", {})
        drawing_meta = DrawingMeta(**{k: str(v) for k, v in meta_raw.items() if v is not None})

        # Items — validate each one individually so a bad item doesn't fail the whole job
        items: list[MTOItem] = []
        warnings: list[str] = []
        for i, item_raw in enumerate(raw.get("items", []), start=1):
            try:
                item_raw.setdefault("item_no", i)
                items.append(MTOItem(**item_raw))
            except Exception as e:
                warnings.append(f"Item {i} skipped: {e}")

        # Summary
        summary_raw = raw.get("summary", {})
        summary = MTOSummary(**{k: v for k, v in summary_raw.items() if v is not None})

        # Metrics
        avg_conf = (
            sum(item.confidence for item in items) / len(items) if items else 0.0
        )
        elapsed_ms = int((time.time() - start_time) * 1000)
        metrics = ExtractionMetrics(
            provider=provider_name,
            processing_time_ms=elapsed_ms,
            items_extracted=len(items),
            average_confidence=round(avg_conf, 3),
            warnings=warnings,
            mock=is_mock,
        )

        return MTOResponse(
            job_id=job_id,
            status=JobStatus.COMPLETED,
            drawing_meta=drawing_meta,
            items=items,
            summary=summary,
            metrics=metrics,
        )


extraction_service = ExtractionService()
