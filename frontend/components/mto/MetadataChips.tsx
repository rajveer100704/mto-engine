"use client";
// =============================================================================
// MetadataChips — compact badge display for drawing metadata
// =============================================================================
import type { DrawingMeta } from "@/types/mto";

interface Props {
  meta: DrawingMeta;
}

interface Chip {
  label: string;
  value: string;
  color: string;
}

function getChips(meta: DrawingMeta): Chip[] {
  const chips: Chip[] = [];

  if (meta.drawing_no) chips.push({ label: "Drawing", value: meta.drawing_no, color: "slate" });
  if (meta.revision) chips.push({ label: "Rev", value: meta.revision, color: "blue" });
  if (meta.nps) chips.push({ label: "NPS", value: meta.nps, color: "indigo" });
  if (meta.material_class) chips.push({ label: "Class", value: meta.material_class, color: "violet" });
  if (meta.service) chips.push({ label: "Service", value: meta.service, color: "cyan" });
  if (meta.design_pressure) chips.push({ label: "Press.", value: meta.design_pressure, color: "orange" });
  if (meta.design_temperature) chips.push({ label: "Temp.", value: meta.design_temperature, color: "red" });
  if (meta.sheet_number) chips.push({ label: "Sheet", value: meta.sheet_number, color: "slate" });

  return chips;
}

const COLOR_MAP: Record<string, string> = {
  slate: "bg-slate-100 text-slate-700 border-slate-200",
  blue: "bg-blue-50 text-blue-700 border-blue-200",
  indigo: "bg-indigo-50 text-indigo-700 border-indigo-200",
  violet: "bg-violet-50 text-violet-700 border-violet-200",
  cyan: "bg-cyan-50 text-cyan-700 border-cyan-200",
  orange: "bg-orange-50 text-orange-700 border-orange-200",
  red: "bg-red-50 text-red-700 border-red-200",
};

export default function MetadataChips({ meta }: Props) {
  const chips = getChips(meta);

  if (chips.length === 0) {
    return (
      <p className="text-sm text-slate-400 italic">
        No metadata extracted from title block
      </p>
    );
  }

  return (
    <div>
      {meta.line_number && (
        <p className="text-xs text-slate-500 font-mono mb-2 tracking-wide">
          {meta.line_number}
        </p>
      )}
      <div className="flex flex-wrap gap-2">
        {chips.map((chip) => (
          <span
            key={chip.label}
            className={[
              "inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium border",
              COLOR_MAP[chip.color] ?? COLOR_MAP.slate,
            ].join(" ")}
          >
            <span className="opacity-60">{chip.label}:</span>
            <span className="font-semibold">{chip.value}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
