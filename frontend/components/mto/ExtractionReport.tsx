"use client";
// =============================================================================
// ExtractionReport — panel showing AI pipeline metrics
// =============================================================================
import {
  Cpu, Clock, List, BarChart2, AlertTriangle, CheckCircle2,
} from "lucide-react";
import type { ExtractionMetrics } from "@/types/mto";

interface Props {
  metrics: ExtractionMetrics;
}

function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 90 ? "bg-emerald-100 text-emerald-700 border-emerald-200" :
    pct >= 70 ? "bg-amber-100 text-amber-700 border-amber-200" :
    "bg-red-100 text-red-700 border-red-200";
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-bold border ${color}`}>
      {pct}%
    </span>
  );
}

interface RowProps {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}

function Row({ icon, label, value }: RowProps) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-slate-50 last:border-0">
      <div className="flex items-center gap-2 text-slate-500">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <div className="text-sm font-medium text-slate-800">{value}</div>
    </div>
  );
}

export default function ExtractionReport({ metrics }: Props) {
  const executionSec = (metrics.processing_time_ms / 1000).toFixed(1);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-slate-700">Extraction Report</h3>
        {metrics.mock && (
          <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-700 border border-amber-200">
            MOCK
          </span>
        )}
      </div>

      <div className="space-y-0">
        <Row
          icon={<Cpu size={13} />}
          label="Provider"
          value={<span className="text-xs">{metrics.provider}</span>}
        />
        <Row
          icon={<Clock size={13} />}
          label="Execution"
          value={`${executionSec} s`}
        />
        <Row
          icon={<List size={13} />}
          label="Components"
          value={metrics.items_extracted}
        />
        <Row
          icon={<BarChart2 size={13} />}
          label="Confidence"
          value={<ConfidenceBadge value={metrics.average_confidence} />}
        />
        <Row
          icon={<AlertTriangle size={13} />}
          label="Warnings"
          value={
            metrics.warnings.length > 0 ? (
              <span className="text-amber-600 font-semibold">
                {metrics.warnings.length}
              </span>
            ) : (
              <CheckCircle2 size={14} className="text-emerald-500" />
            )
          }
        />
      </div>

      {metrics.warnings.length > 0 && (
        <details className="mt-3">
          <summary className="text-xs text-amber-600 cursor-pointer hover:underline">
            {metrics.warnings.length} warning{metrics.warnings.length > 1 ? "s" : ""}
          </summary>
          <ul className="mt-2 space-y-1">
            {metrics.warnings.map((w, i) => (
              <li key={i} className="text-xs text-slate-500 bg-amber-50 rounded px-2 py-1">
                {w}
              </li>
            ))}
          </ul>
        </details>
      )}
    </div>
  );
}
