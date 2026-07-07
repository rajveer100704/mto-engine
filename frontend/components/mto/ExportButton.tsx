"use client";
// =============================================================================
// ExportButton — CSV download trigger
// =============================================================================
import { useState } from "react";
import { Download, Loader2, Check } from "lucide-react";
import { downloadCsv } from "@/lib/api";

interface Props {
  jobId: string;
  drawingNo: string;
}

export default function ExportButton({ jobId, drawingNo }: Props) {
  const [state, setState] = useState<"idle" | "loading" | "done" | "error">("idle");

  const handleClick = async () => {
    setState("loading");
    try {
      await downloadCsv(jobId, drawingNo);
      setState("done");
      setTimeout(() => setState("idle"), 3000);
    } catch {
      setState("error");
      setTimeout(() => setState("idle"), 3000);
    }
  };

  const label =
    state === "loading" ? "Generating..." :
    state === "done" ? "Downloaded!" :
    state === "error" ? "Download failed" :
    "Export CSV";

  const Icon =
    state === "loading" ? Loader2 :
    state === "done" ? Check :
    Download;

  return (
    <button
      onClick={handleClick}
      disabled={state === "loading"}
      className={[
        "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all",
        state === "done"
          ? "bg-emerald-100 text-emerald-700 border border-emerald-200"
          : state === "error"
          ? "bg-red-100 text-red-700 border border-red-200"
          : "bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm hover:shadow-md",
        state === "loading" ? "opacity-75 cursor-not-allowed" : "",
      ].join(" ")}
    >
      <Icon size={16} className={state === "loading" ? "animate-spin" : ""} />
      {label}
    </button>
  );
}
