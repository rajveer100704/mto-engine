// =============================================================================
// TypeScript types — mirrors backend Pydantic schemas exactly
// =============================================================================

export type JobStatus = "pending" | "processing" | "completed" | "failed";

export interface DrawingMeta {
  drawing_no: string;
  revision: string;
  line_number: string;
  nps: string;
  material_class: string;
  service: string;
  design_pressure: string;
  design_temperature: string;
  sheet_number: string;
}

export interface MTOItem {
  item_no: number;
  category: "PIPE" | "FITTING" | "FLANGE" | "VALVE" | "GASKET" | "BOLT" | "SUPPORT";
  description: string;
  size_nps: string;
  schedule_rating: string;
  material_spec: string;
  end_type: string;
  quantity: number;
  unit: string;
  length_m: number | null;
  confidence: number;
  remarks: string;
}

export interface MTOSummary {
  total_pipe_length_m: number;
  fittings: number;
  flanges: number;
  valves: number;
  gaskets: number;
  bolt_sets: number;
  supports: number;
  field_welds: number;
}

export interface ExtractionMetrics {
  provider: string;
  processing_time_ms: number;
  items_extracted: number;
  average_confidence: number;
  warnings: string[];
  mock: boolean;
}

export interface MTOResponse {
  job_id: string;
  status: JobStatus;
  drawing_meta: DrawingMeta;
  items: MTOItem[];
  summary: MTOSummary;
  metrics: ExtractionMetrics;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  current_step: string;
  mock: boolean;
  processing_time_ms: number | null;
  result: MTOResponse | null;
  error: string | null;
}

export interface UploadResponse {
  job_id: string;
  status: JobStatus;
  message: string;
}
