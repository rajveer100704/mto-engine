// =============================================================================
// API Client — typed fetch functions for all backend endpoints
// =============================================================================
import type { JobStatusResponse, UploadResponse } from "@/types/mto";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {}
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

/**
 * Upload a drawing file and get a job_id back.
 */
export async function uploadDrawing(
  file: File,
  onProgress?: (pct: number) => void,
  provider?: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (provider) {
    formData.append("provider", provider);
  }

  // Use XMLHttpRequest for upload progress
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}/api/upload`);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText) as UploadResponse);
      } else {
        let detail = `HTTP ${xhr.status}`;
        try {
          detail = JSON.parse(xhr.responseText).detail ?? detail;
        } catch {}
        reject(new ApiError(xhr.status, detail));
      }
    };

    xhr.onerror = () => reject(new ApiError(0, "Network error"));
    xhr.send(formData);
  });
}

/**
 * Poll job status. Returns full result when status=completed.
 */
export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const res = await fetch(`${API_BASE}/api/mto/${jobId}`, { cache: "no-store" });
  return handleResponse<JobStatusResponse>(res);
}

/**
 * Get CSV download URL for a completed job.
 */
export function getCsvUrl(jobId: string): string {
  return `${API_BASE}/api/mto/${jobId}/csv`;
}

/**
 * Download CSV directly.
 */
export async function downloadCsv(jobId: string, drawingNo: string): Promise<void> {
  const res = await fetch(getCsvUrl(jobId));
  if (!res.ok) throw new ApiError(res.status, "CSV download failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `MTO_${drawingNo || jobId.slice(0, 8)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}
