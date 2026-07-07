"use client";
// =============================================================================
// UploadZone — drag-and-drop file picker with validation
// =============================================================================
import { useCallback, useState } from "react";
import { Upload, FileImage, FileType2, AlertCircle } from "lucide-react";

const ACCEPTED = ["image/png", "image/jpeg", "image/jpg", "application/pdf"];
const MAX_MB = 20;

interface Props {
  onFile: (file: File) => void;
  disabled?: boolean;
}

export default function UploadZone({ onFile, disabled }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = (file: File): string | null => {
    if (!ACCEPTED.includes(file.type))
      return `Unsupported file type: ${file.type}. Upload PNG, JPG, or PDF.`;
    if (file.size > MAX_MB * 1024 * 1024)
      return `File too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Maximum is ${MAX_MB} MB.`;
    return null;
  };

  const handleFile = useCallback(
    (file: File) => {
      const err = validate(file);
      if (err) { setError(err); return; }
      setError(null);
      onFile(file);
    },
    [onFile]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const onInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div className="w-full">
      <label
        htmlFor="file-upload"
        className={[
          "flex flex-col items-center justify-center w-full h-64 rounded-2xl",
          "border-2 border-dashed transition-all duration-200 cursor-pointer",
          "bg-slate-50 hover:bg-indigo-50",
          dragOver
            ? "border-indigo-500 bg-indigo-50 scale-[1.01]"
            : "border-slate-300 hover:border-indigo-400",
          disabled ? "opacity-50 cursor-not-allowed" : "",
        ].join(" ")}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <div className="flex flex-col items-center gap-3 text-center px-6">
          <div className={[
            "w-16 h-16 rounded-2xl flex items-center justify-center transition-colors",
            dragOver ? "bg-indigo-100" : "bg-slate-100",
          ].join(" ")}>
            <Upload
              className={dragOver ? "text-indigo-600" : "text-slate-400"}
              size={28}
            />
          </div>
          <div>
            <p className="text-lg font-semibold text-slate-700">
              {dragOver ? "Drop to upload" : "Drag & drop your isometric drawing"}
            </p>
            <p className="text-sm text-slate-500 mt-1">or</p>
          </div>
          <span className="px-5 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 transition-colors">
            Browse Files
          </span>
          <div className="flex items-center gap-3 mt-2">
            {[
              { icon: FileImage, label: "PNG" },
              { icon: FileImage, label: "JPG" },
              { icon: FileType2, label: "PDF" },
            ].map(({ icon: Icon, label }) => (
              <span
                key={label}
                className="flex items-center gap-1 px-2 py-1 rounded-md bg-slate-200 text-slate-600 text-xs font-medium"
              >
                <Icon size={12} /> {label}
              </span>
            ))}
            <span className="text-xs text-slate-400">· Max {MAX_MB} MB</span>
          </div>
        </div>
        <input
          id="file-upload"
          type="file"
          className="hidden"
          accept=".png,.jpg,.jpeg,.pdf"
          onChange={onInputChange}
          disabled={disabled}
        />
      </label>

      {error && (
        <div className="mt-3 flex items-center gap-2 text-red-600 text-sm bg-red-50 border border-red-200 rounded-lg px-4 py-3">
          <AlertCircle size={16} className="flex-shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
}
