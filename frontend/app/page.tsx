"use client";
// =============================================================================
// Upload Page — home screen with upload zone + processing timeline
// =============================================================================
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Brain, FileDown, Shield } from "lucide-react";
import Header from "@/components/layout/Header";
import UploadZone from "@/components/upload/UploadZone";
import ProcessingTimeline from "@/components/upload/ProcessingTimeline";
import { useUpload } from "@/hooks/useUpload";

const FEATURES = [
  {
    icon: Brain,
    title: "Vision AI Extraction",
    desc: "Gemini 2.5 Flash analyzes every symbol, annotation, and dimension on the drawing",
    color: "indigo",
  },
  {
    icon: Shield,
    title: "Engineering Rule Engine",
    desc: "Deterministic post-processing derives bolt sets, gaskets, and normalizes all data",
    color: "violet",
  },
  {
    icon: FileDown,
    title: "CSV Export",
    desc: "Download a complete MTO with metadata header ready for import into any ERP system",
    color: "cyan",
  },
];

const ICON_COLORS: Record<string, string> = {
  indigo: "bg-indigo-50 text-indigo-600",
  violet: "bg-violet-50 text-violet-600",
  cyan: "bg-cyan-50 text-cyan-600",
};

export default function HomePage() {
  const router = useRouter();
  const { state, upload } = useUpload();
  const [provider, setProvider] = useState<"gemini" | "mock">("mock");

  const isProcessing = state.phase === "polling" || state.phase === "uploading";

  // Navigate to results when done (in a useEffect side effect to avoid rendering warning)
  useEffect(() => {
    if (state.phase === "done") {
      router.push(`/results/${state.jobId}`);
    }
  }, [state, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50/30">
      <Header />

      <main className="max-w-3xl mx-auto px-6 py-16">
        {/* Hero */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-100 text-indigo-700 text-xs font-semibold mb-4 border border-indigo-200">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
            AI-Powered Pipeline
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-3 tracking-tight">
            Piping Isometric
            <span className="text-indigo-600"> MTO Generator</span>
          </h1>
          <p className="text-lg text-slate-500 max-w-xl mx-auto">
            Upload a piping isometric drawing and let AI extract a complete,
            engineer-validated Material Take-Off in seconds.
          </p>
        </div>

        {/* Upload zone or processing state */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 mb-8">
          {isProcessing ? (
            <div className="max-w-sm mx-auto">
              <h2 className="text-base font-semibold text-slate-700 text-center mb-6">
                {state.phase === "uploading"
                  ? `Uploading... ${state.uploadPct}%`
                  : "Analyzing Drawing..."}
              </h2>
              <ProcessingTimeline
                progress={state.phase === "uploading" ? state.uploadPct * 0.1 : state.progress}
                currentStep={state.phase === "uploading" ? "Uploading file" : state.currentStep}
                mock={state.phase === "polling" && state.mock}
              />
            </div>
          ) : (
            <>
              {/* Provider Selection Radio Cards */}
              <div className="mb-6">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
                  AI Pipeline Engine
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setProvider("gemini")}
                    className={[
                      "flex items-start gap-3 p-4 rounded-xl border text-left transition-all cursor-pointer",
                      provider === "gemini"
                        ? "border-indigo-500 bg-indigo-50/50 ring-2 ring-indigo-500/20"
                        : "border-slate-200 hover:border-slate-300 hover:bg-slate-50",
                    ].join(" ")}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <span className={[
                        "w-4 h-4 rounded-full border flex items-center justify-center",
                        provider === "gemini" ? "border-indigo-500 text-indigo-500" : "border-slate-300"
                      ].join(" ")}>
                        {provider === "gemini" && <span className="w-2 h-2 rounded-full bg-indigo-500" />}
                      </span>
                    </div>
                    <div>
                      <span className="block text-sm font-semibold text-slate-800">Gemini 2.5 Flash</span>
                      <span className="block text-xs text-slate-500 mt-0.5">Live Vision AI extraction from drawing</span>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setProvider("mock")}
                    className={[
                      "flex items-start gap-3 p-4 rounded-xl border text-left transition-all cursor-pointer",
                      provider === "mock"
                        ? "border-amber-500 bg-amber-50/40 ring-2 ring-amber-500/20"
                        : "border-slate-200 hover:border-slate-300 hover:bg-slate-50",
                    ].join(" ")}
                  >
                    <div className="flex-shrink-0 mt-0.5">
                      <span className={[
                        "w-4 h-4 rounded-full border flex items-center justify-center",
                        provider === "mock" ? "border-amber-500 text-amber-500" : "border-slate-300"
                      ].join(" ")}>
                        {provider === "mock" && <span className="w-2 h-2 rounded-full bg-amber-500" />}
                      </span>
                    </div>
                    <div>
                      <span className="block text-sm font-semibold text-slate-800">Mock Provider</span>
                      <span className="block text-xs text-slate-500 mt-0.5">Offline interactive demo mode</span>
                    </div>
                  </button>
                </div>
              </div>

              <UploadZone onFile={(file) => upload(file, provider)} disabled={isProcessing} />
              {state.phase === "error" && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
                  <strong>Error:</strong> {state.message}
                  <button
                    onClick={() => window.location.reload()}
                    className="ml-3 underline hover:no-underline"
                  >
                    Try again
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        {/* Feature cards */}
        <div className="grid grid-cols-3 gap-4">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-3 ${ICON_COLORS[f.color]}`}>
                <f.icon size={18} />
              </div>
              <h3 className="text-sm font-semibold text-slate-800 mb-1">{f.title}</h3>
              <p className="text-xs text-slate-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>

        {/* Mock mode notice */}
        <p className="text-center text-xs text-slate-400 mt-8">
          No API key? The app runs with a realistic mock MTO. Add{" "}
          <code className="bg-slate-100 px-1 rounded">GOOGLE_API_KEY</code> to{" "}
          <code className="bg-slate-100 px-1 rounded">backend/.env</code> for live AI extraction.
        </p>
      </main>
    </div>
  );
}
