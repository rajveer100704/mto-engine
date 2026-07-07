"use client";
// =============================================================================
// Results Dashboard — two-column layout: drawing panel + MTO panel
// =============================================================================
import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ChevronRight, AlertCircle } from "lucide-react";
import Header from "@/components/layout/Header";
import MetadataChips from "@/components/mto/MetadataChips";
import ExtractionReport from "@/components/mto/ExtractionReport";
import SummaryCards from "@/components/mto/SummaryCards";
import MTOTable from "@/components/mto/MTOTable";
import ExportButton from "@/components/mto/ExportButton";
import ProcessingTimeline from "@/components/upload/ProcessingTimeline";
import { getJobStatus } from "@/lib/api";
import type { JobStatusResponse, MTOResponse } from "@/types/mto";

interface Props {
  params: Promise<{ jobId: string }>;
}

export default function ResultsPage({ params }: Props) {
  const { jobId } = use(params);
  const router = useRouter();
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const poll = async (delay = 800) => {
      if (cancelled) return;
      try {
        const s = await getJobStatus(jobId);
        if (!cancelled) {
          setStatus(s);
          if (s.status === "pending" || s.status === "processing") {
            const next = Math.min(delay * 1.3, 3000);
            setTimeout(() => poll(next), delay);
          }
        }
      } catch (e: unknown) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load results");
      }
    };

    poll();
    return () => { cancelled = true; };
  }, [jobId]);

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header />
        <main className="max-w-2xl mx-auto px-6 py-20 text-center">
          <AlertCircle size={40} className="text-red-400 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-slate-800 mb-2">Something went wrong</h1>
          <p className="text-slate-500 mb-6">{error}</p>
          <Link href="/" className="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
            Back to Upload
          </Link>
        </main>
      </div>
    );
  }

  // Loading / processing state
  if (!status || status.status === "pending" || status.status === "processing") {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header />
        <main className="max-w-lg mx-auto px-6 py-20">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
            <h1 className="text-lg font-bold text-slate-800 text-center mb-6">
              Analyzing Drawing...
            </h1>
            <ProcessingTimeline
              progress={status?.progress ?? 0}
              currentStep={status?.current_step ?? "Initializing..."}
              mock={status?.mock}
            />
          </div>
        </main>
      </div>
    );
  }

  // Failed state
  if (status.status === "failed") {
    return (
      <div className="min-h-screen bg-slate-50">
        <Header />
        <main className="max-w-2xl mx-auto px-6 py-20 text-center">
          <AlertCircle size={40} className="text-red-400 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-slate-800 mb-2">Extraction Failed</h1>
          <p className="text-slate-500 mb-6">{status.error ?? "Unknown error"}</p>
          <Link href="/" className="px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700">
            Try Another Drawing
          </Link>
        </main>
      </div>
    );
  }

  // Completed — full dashboard
  const result = status.result as MTOResponse;
  const meta = result.drawing_meta;

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />

      {/* Breadcrumb */}
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center gap-2 text-sm text-slate-500">
        <Link href="/" className="hover:text-indigo-600 transition-colors">Home</Link>
        <ChevronRight size={14} />
        <span>Results</span>
        <ChevronRight size={14} />
        <span className="text-slate-800 font-medium">
          {meta.drawing_no || jobId.slice(0, 8)}
        </span>
        {status.mock && (
          <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-amber-100 text-amber-700 border border-amber-200 font-medium">
            MOCK
          </span>
        )}
      </div>

      {/* Two-column layout */}
      <main className="max-w-7xl mx-auto px-6 pb-12 flex gap-6 items-start">

        {/* LEFT COLUMN — sticky drawing panel */}
        <aside className="w-80 flex-shrink-0 sticky top-20 space-y-4">
          {/* Drawing Preview */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-100">
              <h2 className="text-sm font-semibold text-slate-700">Isometric Drawing</h2>
            </div>
            <div className="p-3 bg-slate-50 flex items-center justify-center min-h-48">
              <div className="text-center text-slate-400">
                <div className="w-16 h-16 mx-auto bg-slate-200 rounded-xl flex items-center justify-center mb-2">
                  <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
                <p className="text-xs">
                  {meta.drawing_no || "Drawing"}
                </p>
              </div>
            </div>
          </div>

          {/* Metadata Chips */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Drawing Metadata</h3>
            <MetadataChips meta={meta} />
          </div>

          {/* Extraction Report */}
          <ExtractionReport metrics={result.metrics} />

          {/* Back link */}
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-slate-500 hover:text-indigo-600 transition-colors"
          >
            <ArrowLeft size={14} />
            Upload another drawing
          </Link>
        </aside>

        {/* RIGHT COLUMN — MTO content */}
        <div className="flex-1 min-w-0 space-y-5">
          {/* Title + Export */}
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-xl font-bold text-slate-900">Material Take-Off</h1>
              <p className="text-sm text-slate-500 mt-0.5">
                {result.items.length} line items extracted
                {status.processing_time_ms && (
                  <span className="ml-2 text-slate-400">
                    in {(status.processing_time_ms / 1000).toFixed(1)}s
                  </span>
                )}
              </p>
            </div>
            <ExportButton
              jobId={jobId}
              drawingNo={meta.drawing_no}
            />
          </div>

          {/* Summary Cards */}
          <SummaryCards summary={result.summary} />

          {/* MTO Table */}
          <MTOTable items={result.items} />
        </div>
      </main>
    </div>
  );
}
