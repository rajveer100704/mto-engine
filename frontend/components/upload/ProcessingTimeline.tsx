"use client";
// =============================================================================
// ProcessingTimeline — animated pipeline step tracker
// =============================================================================
import { Check, Loader2, Circle } from "lucide-react";

export interface TimelineStep {
  label: string;
  description?: string;
}

const PIPELINE_STEPS: TimelineStep[] = [
  { label: "Upload Complete", description: "Drawing received" },
  { label: "Image Enhancement", description: "Contrast & clarity optimized" },
  { label: "AI Extraction", description: "Gemini Vision analyzing" },
  { label: "Rule Engine Validation", description: "Engineering rules applied" },
  { label: "MTO Generated", description: "Ready to review" },
];

type StepStatus = "done" | "active" | "pending";

function getStepStatus(stepIndex: number, progress: number): StepStatus {
  const thresholds = [10, 40, 65, 85, 100];
  const pct = thresholds[stepIndex] ?? 100;
  if (progress >= pct) return "done";
  if (progress >= (thresholds[stepIndex - 1] ?? 0)) return "active";
  return "pending";
}

interface Props {
  progress: number;
  currentStep: string;
  mock?: boolean;
}

export default function ProcessingTimeline({ progress, currentStep, mock }: Props) {
  return (
    <div className="w-full">
      {mock && (
        <div className="mb-4 px-3 py-2 bg-amber-50 border border-amber-200 rounded-lg text-amber-700 text-xs font-medium">
          ⚠ Running in Mock Mode — no API key configured
        </div>
      )}

      {/* Progress bar */}
      <div className="w-full bg-slate-100 rounded-full h-2 mb-6">
        <div
          className="bg-indigo-600 h-2 rounded-full transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Steps */}
      <div className="space-y-4">
        {PIPELINE_STEPS.map((step, i) => {
          const status = getStepStatus(i, progress);
          return (
            <div key={step.label} className="flex items-start gap-3">
              {/* Icon */}
              <div className={[
                "flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center mt-0.5",
                status === "done" ? "bg-emerald-100" :
                status === "active" ? "bg-indigo-100" : "bg-slate-100",
              ].join(" ")}>
                {status === "done" ? (
                  <Check size={14} className="text-emerald-600" />
                ) : status === "active" ? (
                  <Loader2 size={14} className="text-indigo-600 animate-spin" />
                ) : (
                  <Circle size={10} className="text-slate-300" />
                )}
              </div>

              {/* Text */}
              <div>
                <p className={[
                  "text-sm font-medium",
                  status === "done" ? "text-emerald-700" :
                  status === "active" ? "text-indigo-700" : "text-slate-400",
                ].join(" ")}>
                  {step.label}
                </p>
                {step.description && (
                  <p className="text-xs text-slate-400 mt-0.5">{step.description}</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <p className="text-xs text-slate-500 mt-5 text-center italic">
        {currentStep}
      </p>
    </div>
  );
}
