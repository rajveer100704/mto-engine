# =============================================================================
# Isometric MTO Generator — Backend Pydantic Schemas
# =============================================================================
from __future__ import annotations

import enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DrawingMeta(BaseModel):
    drawing_no: str = Field(default="", description="Drawing number from title block")
    revision: str = Field(default="", description="Revision letter/number")
    line_number: str = Field(default="", description="Full pipe line number e.g. 6\"-P-1501-A1A-IH")
    nps: str = Field(default="", description="Nominal Pipe Size e.g. 6\"")
    material_class: str = Field(default="", description="Piping material class e.g. A1A")
    service: str = Field(default="", description="Service code e.g. Process")
    design_pressure: str = Field(default="", description="Design pressure")
    design_temperature: str = Field(default="", description="Design temperature")
    sheet_number: str = Field(default="", description="Sheet number e.g. 1 of 3")


class MTOItem(BaseModel):
    item_no: int = Field(description="Sequential item number")
    category: str = Field(description="PIPE | FITTING | FLANGE | VALVE | GASKET | BOLT | SUPPORT")
    description: str = Field(description="Full engineering description")
    size_nps: str = Field(description="Nominal pipe size in inches e.g. 6\"")
    schedule_rating: str = Field(default="", description="SCH 40 / CL150 etc.")
    material_spec: str = Field(default="", description="ASTM material grade")
    end_type: str = Field(default="BW", description="BW | SW | THD | FLGD")
    quantity: float = Field(ge=0, description="Count or quantity")
    unit: str = Field(description="EA | M | SET")
    length_m: Optional[float] = Field(default=None, description="Total length in metres, pipes only")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="AI confidence 0-1")
    remarks: str = Field(default="", description="Additional notes")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = {"PIPE", "FITTING", "FLANGE", "VALVE", "GASKET", "BOLT", "SUPPORT"}
        up = v.upper()
        return up if up in valid else v.upper()

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: str) -> str:
        valid = {"EA", "M", "SET", "NO"}
        up = v.upper()
        return "EA" if up not in valid else up


class MTOSummary(BaseModel):
    total_pipe_length_m: float = Field(default=0.0, description="Total pipe length in metres")
    fittings: int = Field(default=0, description="Total fitting count")
    flanges: int = Field(default=0, description="Total flange count")
    valves: int = Field(default=0, description="Total valve count")
    gaskets: int = Field(default=0, description="Total gasket count")
    bolt_sets: int = Field(default=0, description="Total bolt set count")
    supports: int = Field(default=0, description="Total support count")
    field_welds: int = Field(default=0, description="Field weld count")


class ExtractionMetrics(BaseModel):
    provider: str = Field(description="AI provider name e.g. Gemini 2.5 Flash")
    processing_time_ms: int = Field(description="Total processing time in milliseconds")
    items_extracted: int = Field(description="Number of MTO items extracted")
    average_confidence: float = Field(description="Mean confidence score 0-1")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings")
    mock: bool = Field(default=False, description="True if mock data was returned")


class MTOResponse(BaseModel):
    job_id: str = Field(description="Job UUID")
    status: JobStatus = Field(description="Job status")
    drawing_meta: DrawingMeta = Field(description="Drawing metadata")
    items: list[MTOItem] = Field(description="MTO line items")
    summary: MTOSummary = Field(description="Aggregate summary")
    metrics: ExtractionMetrics = Field(description="Extraction performance metrics")


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    progress: int = Field(ge=0, le=100, description="Progress percentage 0-100")
    current_step: str = Field(default="", description="Human-readable current pipeline step")
    mock: bool = Field(default=False)
    processing_time_ms: Optional[int] = Field(default=None)
    result: Optional[MTOResponse] = Field(default=None, description="Set when status=completed")
    error: Optional[str] = Field(default=None, description="Set when status=failed")


class UploadResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


class ErrorResponse(BaseModel):
    detail: str
    code: str
