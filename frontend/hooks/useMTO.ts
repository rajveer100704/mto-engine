"use client";
// =============================================================================
// useMTO — polling hook for MTO job results
// Note: This hook is available for reuse. The results page uses it inline.
// =============================================================================
import { useState, useEffect } from "react";
import { getJobStatus } from "@/lib/api";
import type { JobStatusResponse } from "@/types/mto";

interface Options {
  enabled?: boolean;
  onComplete?: (status: JobStatusResponse) => void;
}

export function useMTO(jobId: string | null, options: Options = {}) {
  const { enabled = true, onComplete } = options;
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId || !enabled) return;
    let cancelled = false;

    const poll = async (delay = 800) => {
      if (cancelled) return;
      try {
        const s = await getJobStatus(jobId);
        if (!cancelled) {
          setStatus(s);
          if (s.status === "completed") {
            onComplete?.(s);
            return;
          }
          if (s.status === "failed") {
            setError(s.error ?? "Extraction failed");
            return;
          }
          const next = Math.min(delay * 1.3, 3000);
          setTimeout(() => poll(next), delay);
        }
      } catch (e: unknown) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Poll failed");
      }
    };

    poll();
    return () => { cancelled = true; };
  }, [jobId, enabled]);

  return { status, error };
}
