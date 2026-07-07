"use client";
// =============================================================================
// MTOTable — full-featured table: search, sort, pagination, confidence badges
// =============================================================================
import { useState, useMemo } from "react";
import { Search, ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react";
import type { MTOItem } from "@/types/mto";

interface Props {
  items: MTOItem[];
}

type SortKey = keyof MTOItem;
type SortDir = "asc" | "desc" | null;

function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const cls =
    pct >= 90 ? "bg-emerald-100 text-emerald-700 border border-emerald-200" :
    pct >= 70 ? "bg-amber-100 text-amber-700 border border-amber-200" :
    "bg-red-100 text-red-700 border border-red-200";
  return (
    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-bold ${cls}`}>
      {pct}%
    </span>
  );
}

function CategoryBadge({ value }: { value: string }) {
  const colors: Record<string, string> = {
    PIPE: "bg-slate-100 text-slate-700",
    FITTING: "bg-blue-50 text-blue-700",
    FLANGE: "bg-violet-50 text-violet-700",
    VALVE: "bg-cyan-50 text-cyan-700",
    GASKET: "bg-teal-50 text-teal-700",
    BOLT: "bg-orange-50 text-orange-700",
    SUPPORT: "bg-stone-100 text-stone-600",
  };
  return (
    <span className={`px-2 py-0.5 rounded-md text-xs font-semibold ${colors[value] ?? "bg-gray-100 text-gray-600"}`}>
      {value}
    </span>
  );
}

const PAGE_SIZE = 15;

const COLUMNS: { key: SortKey; label: string; width?: string }[] = [
  { key: "item_no", label: "#", width: "w-10" },
  { key: "category", label: "Category", width: "w-24" },
  { key: "description", label: "Description" },
  { key: "size_nps", label: "Size", width: "w-16" },
  { key: "schedule_rating", label: "Sched./Rating", width: "w-28" },
  { key: "material_spec", label: "Material Spec" },
  { key: "quantity", label: "Qty", width: "w-14" },
  { key: "unit", label: "Unit", width: "w-14" },
  { key: "length_m", label: "L (m)", width: "w-16" },
  { key: "confidence", label: "Conf.", width: "w-20" },
];

export default function MTOTable({ items }: Props) {
  const [search, setSearch] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("item_no");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [page, setPage] = useState(1);

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : sortDir === "desc" ? null : "asc");
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
    setPage(1);
  };

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return items.filter(
      (item) =>
        !q ||
        item.description.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q) ||
        item.size_nps.toLowerCase().includes(q) ||
        item.material_spec.toLowerCase().includes(q)
    );
  }, [items, search]);

  const sorted = useMemo(() => {
    if (!sortDir) return filtered;
    return [...filtered].sort((a, b) => {
      const av = a[sortKey] ?? 0;
      const bv = b[sortKey] ?? 0;
      const cmp = av < bv ? -1 : av > bv ? 1 : 0;
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [filtered, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE));
  const pageItems = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const SortIcon = ({ k }: { k: SortKey }) =>
    sortKey === k ? (
      sortDir === "asc" ? <ChevronUp size={12} /> : <ChevronDown size={12} />
    ) : (
      <ChevronsUpDown size={12} className="opacity-30" />
    );

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      {/* Search bar */}
      <div className="p-4 border-b border-slate-100 flex items-center gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search by description, category, material..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-300 bg-slate-50"
          />
        </div>
        <span className="text-xs text-slate-500 whitespace-nowrap">
          {filtered.length} / {items.length} items
        </span>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-100">
            <tr>
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key)}
                  className={[
                    "px-3 py-3 text-left text-xs font-semibold text-slate-500 cursor-pointer",
                    "hover:bg-slate-100 select-none transition-colors",
                    col.width ?? "",
                  ].join(" ")}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    <SortIcon k={col.key} />
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageItems.map((item, i) => (
              <tr
                key={item.item_no}
                className={[
                  "border-b border-slate-50 hover:bg-slate-50 transition-colors",
                  i % 2 === 0 ? "" : "bg-slate-50/50",
                ].join(" ")}
              >
                <td className="px-3 py-2.5 text-slate-400 text-xs">{item.item_no}</td>
                <td className="px-3 py-2.5">
                  <CategoryBadge value={item.category} />
                </td>
                <td className="px-3 py-2.5 text-slate-700 max-w-xs">
                  <div className="truncate">{item.description}</div>
                  {item.remarks && (
                    <div className="text-xs text-slate-400 truncate">{item.remarks}</div>
                  )}
                </td>
                <td className="px-3 py-2.5 text-slate-600 font-mono text-xs">{item.size_nps}</td>
                <td className="px-3 py-2.5 text-slate-500 text-xs">{item.schedule_rating}</td>
                <td className="px-3 py-2.5 text-slate-500 text-xs max-w-xs">
                  <div className="truncate">{item.material_spec}</div>
                </td>
                <td className="px-3 py-2.5 text-slate-700 font-semibold text-center">{item.quantity}</td>
                <td className="px-3 py-2.5 text-slate-500 text-xs text-center">{item.unit}</td>
                <td className="px-3 py-2.5 text-slate-500 text-xs text-center">
                  {item.length_m != null ? item.length_m.toFixed(2) : "—"}
                </td>
                <td className="px-3 py-2.5">
                  <ConfidenceBadge value={item.confidence} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-4 py-3 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Page {page} of {totalPages}
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 text-xs rounded-md border border-slate-200 disabled:opacity-40 hover:bg-slate-50"
            >
              Prev
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 text-xs rounded-md border border-slate-200 disabled:opacity-40 hover:bg-slate-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
