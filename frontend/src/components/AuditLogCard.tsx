import React from 'react';
import {
  FileText,
  DownloadSimple,
  Trash,
  ArrowBendDownRight,
} from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';
import { normalizeGrade } from '../api/types';

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
      'Latency (ms)',
      'Diagnostic',
    ];

    const rows = history.map((h) => [
      h.timestamp,
      `"${h.sampleName.replace(/"/g, '""')}"`,
      h.precision.toUpperCase(),
      h.grade,
      h.defectRatio.toFixed(2),
      h.latencyMs.toFixed(1),
      `"${(h.rejectReason || 'PASS').replace(/"/g, '""')}"`,
    ]);

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

  return (
    <div
      id="audit-log-card"
      className="rounded-2xl border border-slate-200/80 dark:border-[#262B33] bg-white dark:bg-[#16191E] p-4 shadow-sm space-y-3 transition-colors"
    >
      {/* Header with Title + Filter Counts + CSV / Clear actions */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-sky-400">
            <FileText size={16} weight="bold" />
          </div>
          <h2 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight shrink-0">
            Audit Log
          </h2>

          {total > 0 && (
            <div className="flex items-center gap-1.5 text-[11px] font-mono">
              <span className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium">
                {total} runs
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold border border-emerald-500/20">
                {gradeACount} A
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-600 dark:text-amber-400 font-bold border border-amber-500/20">
                {gradeBCount} B
              </span>
              <span className="hidden sm:inline-block px-2 py-0.5 rounded-md bg-rose-500/10 text-rose-600 dark:text-rose-400 font-bold border border-rose-500/20">
                {rejectCount} Reject
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-1.5">
          {total > 0 && (
            <button
              type="button"
              onClick={clearHistory}
              className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition-colors cursor-pointer"
              title="Clear all records"
            >
              <Trash size={15} />
            </button>
          )}

          <button
            type="button"
            onClick={handleExportCSV}
            disabled={total === 0}
            className="flex items-center gap-1.5 rounded-lg bg-[#2563EB] hover:bg-blue-700 text-white px-3 py-1.5 text-xs font-bold transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-2xs"
          >
            <DownloadSimple size={14} weight="bold" />
            <span>CSV</span>
          </button>
        </div>
      </div>

      {/* Modern Data Table */}
      <div className="overflow-x-auto rounded-xl border border-slate-200/80 dark:border-slate-800/80">
        <table className="w-full text-left text-xs font-sans">
          <thead className="bg-slate-50 dark:bg-[#1A1F26] border-b border-slate-200/80 dark:border-slate-800/80 text-[11px] font-mono uppercase tracking-wider text-slate-400 dark:text-slate-500">
            <tr>
              <th className="px-3.5 py-2.5 font-medium">Time</th>
              <th className="px-3.5 py-2.5 font-medium">Sample</th>
              <th className="px-3.5 py-2.5 font-medium">Grade</th>
              <th className="px-3.5 py-2.5 font-medium text-right">Defect</th>
              <th className="px-3.5 py-2.5 font-medium">Route</th>
              <th className="px-2 py-2.5 font-medium text-center w-8">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80 bg-white dark:bg-[#16191E]">
            {total > 0 ? (
              history.slice(0, 10).map((h) => {
                const norm = normalizeGrade(h.grade);

                let gradePill = 'bg-slate-500/10 text-slate-500 border-slate-500/20';
                let gradeText = 'STANDBY';
                let routeName = 'Standby';

                if (norm === 'GRADE_A') {
                  gradePill = 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/25';
                  gradeText = 'Grade A';
                  routeName = 'Packer #1';
                } else if (norm === 'GRADE_B') {
                  gradePill = 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/25';
                  gradeText = 'Grade B';
                  routeName = 'Sort #2';
                } else if (norm === 'REJECT') {
                  gradePill = 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/25';
                  gradeText = 'Reject';
                  routeName = 'Reject #3';
                }

                return (
                  <tr
                    key={h.id}
                    className="hover:bg-slate-50/80 dark:hover:bg-[#1A1F26] transition-colors group"
                    title={h.rejectReason || 'Passed quality parameters'}
                  >
                    <td className="px-3.5 py-2.5 font-mono text-[11px] text-slate-500 dark:text-slate-400 whitespace-nowrap">
                      {h.timestamp}
                    </td>
                    <td className="px-3.5 py-2.5 font-medium text-slate-800 dark:text-slate-200 truncate max-w-[180px]">
                      {h.sampleName}
                    </td>
                    <td className="px-3.5 py-2.5">
                      <span className={`inline-block px-2 py-0.5 rounded-md border text-[11px] font-bold font-mono ${gradePill}`}>
                        {gradeText}
                      </span>
                    </td>
                    <td className="px-3.5 py-2.5 text-right font-mono font-bold text-slate-800 dark:text-slate-200 tabular-nums">
                      {h.defectRatio.toFixed(1)}%
                    </td>
                    <td className="px-3.5 py-2.5 text-slate-600 dark:text-slate-400">
                      <span className="flex items-center gap-1 text-[11px] font-mono">
                        <ArrowBendDownRight size={12} className="text-slate-400" />
                        {routeName}
                      </span>
                    </td>
                    <td className="px-2 py-2.5 text-center">
                      <button
                        type="button"
                        onClick={() => deleteHistoryItem(h.id)}
                        className="p-1 text-slate-300 dark:text-slate-600 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded transition-colors cursor-pointer opacity-80 group-hover:opacity-100"
                        title="Delete this record"
                      >
                        <Trash size={13} />
                      </button>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={6} className="px-3.5 py-8 text-center text-xs font-mono text-slate-400 dark:text-slate-500">
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
