"use client";
// =============================================================================
// SummaryCards — key MTO metrics in card grid
// =============================================================================
import { Pipette, Wrench, Disc, Gauge, Circle, Bolt, HardHat } from "lucide-react";
import type { MTOSummary } from "@/types/mto";

interface Props {
  summary: MTOSummary;
}

interface CardData {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ReactNode;
  color: string;
}

export default function SummaryCards({ summary }: Props) {
  const cards: CardData[] = [
    {
      label: "Pipe Length",
      value: `${summary.total_pipe_length_m.toFixed(1)} m`,
      icon: <Pipette size={20} />,
      color: "indigo",
    },
    {
      label: "Fittings",
      value: summary.fittings,
      sub: "EA",
      icon: <Wrench size={20} />,
      color: "blue",
    },
    {
      label: "Flanges",
      value: summary.flanges,
      sub: "EA",
      icon: <Disc size={20} />,
      color: "violet",
    },
    {
      label: "Valves",
      value: summary.valves,
      sub: "EA",
      icon: <Gauge size={20} />,
      color: "cyan",
    },
    {
      label: "Gaskets",
      value: summary.gaskets,
      sub: "EA",
      icon: <Circle size={20} />,
      color: "teal",
    },
    {
      label: "Bolt Sets",
      value: summary.bolt_sets,
      sub: "SET",
      icon: <Bolt size={20} />,
      color: "orange",
    },
    {
      label: "Supports",
      value: summary.supports,
      sub: "EA",
      icon: <HardHat size={20} />,
      color: "slate",
    },
  ];

  const COLOR_STYLES: Record<string, string> = {
    indigo: "bg-indigo-50 text-indigo-600",
    blue: "bg-blue-50 text-blue-600",
    violet: "bg-violet-50 text-violet-600",
    cyan: "bg-cyan-50 text-cyan-600",
    teal: "bg-teal-50 text-teal-600",
    orange: "bg-orange-50 text-orange-600",
    slate: "bg-slate-100 text-slate-500",
  };

  return (
    <div className="grid grid-cols-4 gap-3">
      {cards.map((card) => (
        <div
          key={card.label}
          className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center mb-3 ${COLOR_STYLES[card.color]}`}>
            {card.icon}
          </div>
          <div className="text-2xl font-bold text-slate-800">{card.value}</div>
          <div className="text-xs text-slate-500 mt-1">
            {card.label} {card.sub && <span className="opacity-60">· {card.sub}</span>}
          </div>
        </div>
      ))}
    </div>
  );
}
