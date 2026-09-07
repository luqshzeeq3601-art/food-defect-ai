import React from 'react';
import {
  FileText,
  DownloadSimple,
  Trash,
  ArrowBendDownRight,
} from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';
import { normalizeGrade } from '../api/types';
import { PRESET_SAMPLES } from '../constants/presets';

export const AuditLogCard: React.FC = () => {
  const { history, clearHistory, deleteHistoryItem } = useInspectionStore();

  const handleExportCSV = () => {
    if (history.length === 0) return;

    const headers = [
      'Time (UTC)',
      'Sample',
      'Precision',
      'Grade',
      'Defect %',
      'Route',
      'Latency (ms)',
      'Diagnostic',
    ];

    const rows = history.map((h) => {
      const norm = normalizeGrade(h.grade);
      const routeStr =
        h.route ||
        (norm === 'GRADE_A'
          ? 'Chute #1'
          : norm === 'GRADE_B'
          ? 'Sort #2'
          : norm === 'REJECT'
          ? 'Reject #3'
          : 'Standby');

      return [
        h.timestamp,
        `"${h.sampleName.replace(/"/g, '""')}"`,
        h.precision.toUpperCase(),
        h.grade,
        h.defectRatio.toFixed(2),
        `"${routeStr}"`,
        h.latencyMs.toFixed(1),
        `"${(h.rejectReason || 'PASS').replace(/"/g, '""')}"`,
      ];
    });

    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `AOI_Inspection_Audit_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const total = history.length;
  const gradeACount = history.filter((h) => normalizeGrade(h.grade) === 'GRADE_A').length;
  const gradeBCount = history.filter((h) => normalizeGrade(h.grade) === 'GRADE_B').length;
  const rejectCount = history.filter((h) => normalizeGrade(h.grade) === 'REJECT').length;

  // Helper to find image thumbnail for historical row
  const getThumbnailSrc = (sampleName: string, explicitUrl?: string) => {
    if (explicitUrl) return explicitUrl;
    const preset = PRESET_SAMPLES.find((p) => p.name === sampleName);
    if (preset) return preset.path;

    const lower = sampleName.toLowerCase();
    if (lower.includes('orange')) return '/samples/real_orange.jpg';
    if (lower.includes('banana')) return '/samples/real_banana.jpg';
    if (lower.includes('bruise') || lower.includes('grade b')) return '/samples/real_orange.jpg';
    if (lower.includes('rot') || lower.includes('decay')) return '/samples/defective_apple_rot.jpg';
    if (lower.includes('apple')) return '/samples/sample_fruit_grade_a.jpg';
    return '/samples/sample_fruit_grade_b.jpg';
  };

  return (
    <div
      id="audit-log-card"
      className="rounded-3xl border border-slate-200/80 dark:border-[#262B33] bg-white dark:bg-[#16191E] p-5 sm:p-6 shadow-sm space-y-5 transition-colors"
    >
      {/* Header: Title + Filter Counts + CSV / Clear actions */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Left: Icon Squircle + Title & Subtitle + Status Badges */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex h-10 w-10 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-2xl bg-blue-50 dark:bg-blue-950/50 text-[#2563EB] dark:text-sky-400 shadow-2xs">
            <FileText size={22} weight="bold" />
          </div>

          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white leading-tight tracking-tight">
                Audit Log
              </h2>
              <div className="flex items-center gap-1.5 text-xs font-mono">
                <span className="px-2.5 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/50 text-[#2563EB] dark:text-sky-400 font-bold border border-blue-100/60 dark:border-blue-900/30">
                  {total} runs
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 font-bold border border-emerald-100 dark:border-emerald-900/30">
                  {gradeACount} A
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-amber-50 dark:bg-amber-950/50 text-amber-600 dark:text-amber-400 font-bold border border-amber-100 dark:border-amber-900/30">
                  {gradeBCount} B
                </span>
                <span className="px-2.5 py-0.5 rounded-full bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 font-bold border border-rose-100 dark:border-rose-900/30">
                  {rejectCount} Reject
                </span>
              </div>
            </div>
            <p className="text-xs text-slate-400 dark:text-slate-500 font-medium mt-0.5">
              Traceable Session History & Conveyor Records
            </p>
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2">
          {total > 0 && (
            <button
              type="button"
              onClick={clearHistory}
              className="h-9 w-9 flex items-center justify-center text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl border border-slate-200/80 dark:border-slate-800 transition-colors cursor-pointer"
              title="Clear all records"
            >
              <Trash size={15} />
            </button>
          )}

          <button
            type="button"
            onClick={handleExportCSV}
            disabled={total === 0}
            className="flex items-center gap-2 rounded-xl bg-[#2563EB] hover:bg-blue-700 text-white px-4 py-2 text-xs font-bold transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-xs"
          >
            <DownloadSimple size={15} weight="bold" />
            <span>Download CSV</span>
          </button>
        </div>
      </div>

      {/* Modern Data Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-200/80 dark:border-slate-800/80">
        <table className="w-full text-left text-xs font-sans">
          <thead className="bg-slate-50/70 dark:bg-[#1A1F26] border-b border-slate-200/80 dark:border-slate-800/80 text-[10px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-500">
            <tr>
              <th className="px-4 py-3 font-semibold">TIME</th>
              <th className="px-4 py-3 font-semibold">SAMPLE</th>
              <th className="px-4 py-3 font-semibold">GRADE</th>
              <th className="px-4 py-3 font-semibold">DEFECT</th>
              <th className="px-4 py-3 font-semibold">ROUTE</th>
              <th className="px-3 py-3 font-semibold text-center w-10">ACTIONS</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80 bg-white dark:bg-[#16191E]">
            {total > 0 ? (
              history.map((h) => {
                const norm = normalizeGrade(h.grade);

                let gradeBadge = (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-bold font-mono text-xs border border-slate-200 dark:border-slate-700">
                    <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
                    Standby
                  </span>
                );
                let defaultRoute = 'Standby';

                if (norm === 'GRADE_A') {
                  gradeBadge = (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#F0FDF4] dark:bg-emerald-950/40 text-[#15803D] dark:text-emerald-400 font-bold font-mono text-xs border border-[#DCFCE7] dark:border-emerald-800/40">
                      <span className="h-1.5 w-1.5 rounded-full bg-[#10B981]" />
                      Grade A
                    </span>
                  );
                  defaultRoute = 'Sort #1';
                } else if (norm === 'GRADE_B') {
                  gradeBadge = (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#FFFBEB] dark:bg-amber-950/40 text-[#D97706] dark:text-amber-400 font-bold font-mono text-xs border border-[#FEF3C7] dark:border-amber-800/40">
                      <span className="h-1.5 w-1.5 rounded-full bg-[#F59E0B]" />
                      Grade B
                    </span>
                  );
                  defaultRoute = 'Sort #2';
                } else if (norm === 'REJECT') {
                  gradeBadge = (
                    <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#FFF1F2] dark:bg-rose-950/40 text-[#E11D48] dark:text-rose-400 font-bold font-mono text-xs border border-[#FFE4E6] dark:border-rose-800/40">
                      <span className="h-1.5 w-1.5 rounded-full bg-[#F43F5E]" />
                      Reject
                    </span>
                  );
                  defaultRoute = 'Reject #3';
                }

                const thumbSrc = getThumbnailSrc(h.sampleName, h.thumbnailUrl);

                return (
                  <tr
                    key={h.id}
                    className="hover:bg-slate-50/70 dark:hover:bg-[#1A1F26] transition-colors group"
                    title={h.rejectReason || 'Passed quality parameters'}
                  >
                    {/* Time */}
                    <td className="px-4 py-3 font-mono text-xs text-slate-500 dark:text-slate-400 whitespace-nowrap">
                      {h.timestamp}
                    </td>

                    {/* Sample: Thumbnail Image + Label */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <img
                          src={thumbSrc}
                          alt={h.sampleName}
                          className="h-9 w-9 rounded-lg object-cover bg-slate-100 dark:bg-slate-800 border border-slate-200/80 dark:border-slate-700/80 shrink-0 shadow-2xs"
                          onError={(e) => {
                            // Fallback if image fails
                            (e.currentTarget as HTMLImageElement).src = '/samples/sample_fruit_grade_b.jpg';
                          }}
                        />
                        <span className="font-semibold text-xs text-slate-800 dark:text-slate-200 truncate max-w-[260px]">
                          {h.sampleName}
                        </span>
                      </div>
                    </td>

                    {/* Grade */}
                    <td className="px-4 py-3">
                      {gradeBadge}
                    </td>

                    {/* Defect % */}
                    <td className="px-4 py-3 font-mono font-bold text-xs text-slate-800 dark:text-slate-200 tabular-nums">
                      {h.defectRatio.toFixed(1)}%
                    </td>

                    {/* Route */}
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                      <span className="flex items-center gap-1.5 text-xs font-mono">
                        <ArrowBendDownRight size={13} className="text-slate-400 shrink-0" />
                        {h.route || defaultRoute}
                      </span>
                    </td>

                    {/* Actions */}
                    <td className="px-3 py-3 text-center">
                      <button
                        type="button"
                        onClick={() => deleteHistoryItem(h.id)}
                        className="p-1.5 text-slate-300 dark:text-slate-600 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition-colors cursor-pointer opacity-70 group-hover:opacity-100"
                        title="Delete this record"
                      >
                        <Trash size={14} />
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-xs font-mono text-slate-400 dark:text-slate-500">
                  No inspection logs recorded yet. Ingest a conveyor frame to begin.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

