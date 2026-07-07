"use client";
// =============================================================================
// useUpload — upload state machine hook
// States: idle → uploading → polling → done → error
// =============================================================================
import { useState, useCallback, useRef } from "react";
import { uploadDrawing, getJobStatus, ApiError } from "@/lib/api";
import type { MTOResponse } from "@/types/mto";

export type UploadState =
  | { phase: "idle" }
  | { phase: "uploading"; uploadPct: number }
  | { phase: "polling"; jobId: string; progress: number; currentStep: string; mock: boolean }
  | { phase: "done"; jobId: string; result: MTOResponse; mock: boolean; processingMs: number }
  | { phase: "error"; message: string };

export function useUpload() {
  const [state, setState] = useState<UploadState>({ phase: "idle" });
  const pollRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const stopPolling = () => {
    if (pollRef.current) {
      clearTimeout(pollRef.current);
      pollRef.current = null;
    }
  };

  const reset = useCallback(() => {
    stopPolling();
    setState({ phase: "idle" });
  }, []);

  const upload = useCallback(async (file: File, provider?: string) => {
    stopPolling();
    setState({ phase: "uploading", uploadPct: 0 });

    try {
      const { job_id } = await uploadDrawing(file, (pct) => {
        setState({ phase: "uploading", uploadPct: pct });
      }, provider);

      // Start polling
      setState({ phase: "polling", jobId: job_id, progress: 5, currentStep: "Queued", mock: false });

      const poll = async (delay = 1000) => {
        try {
          const status = await getJobStatus(job_id);

          if (status.status === "completed" && status.result) {
            setState({
              phase: "done",
              jobId: job_id,
              result: status.result,
              mock: status.mock,
              processingMs: status.processing_time_ms ?? 0,
            });
            return;
          }

          if (status.status === "failed") {
            setState({ phase: "error", message: status.error ?? "Extraction failed" });
            return;
          }

          setState({
            phase: "polling",
            jobId: job_id,
            progress: status.progress,
            currentStep: status.current_step,
            mock: status.mock,
          });

          // Exponential backoff: 1s → 1.5s → 2s → ... max 4s
          const nextDelay = Math.min(delay * 1.3, 4000);
          pollRef.current = setTimeout(() => poll(nextDelay), delay);
        } catch (err) {
          if (err instanceof ApiError && err.status === 404) {
            setState({ phase: "error", message: "Job not found on server" });
          } else {
            // Retry on network error
            pollRef.current = setTimeout(() => poll(delay), 2000);
          }
        }
      };

      pollRef.current = setTimeout(() => poll(), 800);
    } catch (err) {
      const msg = err instanceof ApiError ? err.detail : "Upload failed";
      setState({ phase: "error", message: msg });
    }
  }, []);

  return { state, upload, reset };
}
