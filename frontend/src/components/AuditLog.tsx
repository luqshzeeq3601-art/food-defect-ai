import React from 'react';
import { ClockCountdown, DownloadSimple, Trash } from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';

export const AuditLog: React.FC = () => {
  const { history, clearHistory } = useInspectionStore();

  const handleExportCSV = () => {
    if (history.length === 0) return;

    const headers = [
      'Timestamp',
      'Sample Name',
      'Grade',
      'Defect Ratio (%)',
      'Defect Count',
      'Latency (ms)',
      'Precision',
      'Reject Reason',
    ];

    const rows = history.map((h) => [
      h.timestamp,
      `"${h.sampleName.replace(/"/g, '""')}"`,
      h.grade,
      h.defectRatio.toFixed(2),
      h.defectCount,
      h.latencyMs.toFixed(1),
      h.precision.toUpperCase(),
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

  // Yield calculations
  const total = history.length;
  const gradeACount = history.filter((h) => h.grade === 'GRADE_A').length;
  const gradeBCount = history.filter((h) => h.grade === 'GRADE_B').length;
  const rejectCount = history.filter((h) => h.grade === 'REJECT').length;

  const gradeAYield = total > 0 ? (gradeACount / total) * 100 : 0;
  const gradeBYield = total > 0 ? (gradeBCount / total) * 100 : 0;
  const rejectYield = total > 0 ? (rejectCount / total) * 100 : 0;

  return (
    <div className="rounded-lg border border-[#1F2937] bg-[#111827] overflow-hidden">
      <div className="flex items-center justify-between border-b border-[#1F2937] px-4 py-2.5">
        <div className="flex items-center gap-2">
          <ClockCountdown size={16} className="text-cyan-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-gray-300">
            Session Inspection Audit Log
          </h3>
          <span className="rounded bg-gray-800 px-1.5 py-0.5 font-mono text-[10px] text-gray-400">
            {total} records
          </span>
        </div>

        <div className="flex items-center gap-2">
          {total > 0 && (
            <>
              <button
                type="button"
                onClick={handleExportCSV}
                className="flex items-center gap-1 rounded border border-gray-700 bg-gray-800/80 px-2 py-1 text-[11px] font-mono text-gray-300 hover:border-gray-500 hover:text-white transition-colors"
              >
                <DownloadSimple size={12} />
                Export CSV
              </button>
              <button
                type="button"
                onClick={clearHistory}
                className="flex items-center gap-1 rounded border border-gray-700 bg-gray-800/80 px-2 py-1 text-[11px] font-mono text-rose-400 hover:border-rose-500 transition-colors"
                title="Clear History"
              >
                <Trash size={12} />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Yield Summary Bar */}
      {total > 0 && (
        <div className="grid grid-cols-4 border-b border-[#1F2937] bg-[#0B0F19] px-4 py-2 text-center text-xs font-mono">
          <div>
            <span className="text-[10px] text-gray-500 uppercase block">Total Inspected</span>
            <span className="font-bold text-white">{total} units</span>
          </div>
          <div>
            <span className="text-[10px] text-emerald-500 uppercase block">Grade A Yield</span>
            <span className="font-bold text-emerald-400">{gradeAYield.toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-[10px] text-amber-500 uppercase block">Grade B Yield</span>
            <span className="font-bold text-amber-400">{gradeBYield.toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-[10px] text-rose-500 uppercase block">Scrap / Reject</span>
            <span className="font-bold text-rose-400">{rejectYield.toFixed(1)}%</span>
          </div>
        </div>
      )}

      {/* Audit Table */}
      {total > 0 ? (
        <div className="max-h-52 overflow-y-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="sticky top-0 bg-[#0B0F19] text-[10px] uppercase text-gray-400 border-b border-[#1F2937]">
              <tr>
                <th className="px-3 py-1.5">Time (UTC)</th>
                <th className="px-3 py-1.5">Sample</th>
                <th className="px-3 py-1.5">Precision</th>
                <th className="px-3 py-1.5">Grade</th>
                <th className="px-3 py-1.5">Defect %</th>
                <th className="px-3 py-1.5">Latency</th>
                <th className="px-3 py-1.5">Diagnostic</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1F2937]">
              {history.map((h) => {
                let badgeClass = 'text-gray-400';
                if (h.grade === 'GRADE_A') badgeClass = 'text-emerald-400 font-bold';
                else if (h.grade === 'GRADE_B') badgeClass = 'text-amber-400 font-bold';
                else if (h.grade === 'REJECT') badgeClass = 'text-rose-400 font-bold';

                return (
                  <tr key={h.id} className="hover:bg-gray-800/40 text-gray-300">
                    <td className="px-3 py-1.5 text-gray-400">{h.timestamp}</td>
                    <td className="px-3 py-1.5 font-medium truncate max-w-[140px]">{h.sampleName}</td>
                    <td className="px-3 py-1.5 text-gray-400">{h.precision.toUpperCase()}</td>
                    <td className={`px-3 py-1.5 ${badgeClass}`}>{h.grade}</td>
                    <td className="px-3 py-1.5">{h.defectRatio.toFixed(2)}%</td>
                    <td className="px-3 py-1.5">{h.latencyMs.toFixed(1)} ms</td>
                    <td className="px-3 py-1.5 text-gray-400 truncate max-w-[180px]">
                      {h.rejectReason || 'PASS'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="p-4 text-center text-xs text-gray-500 font-mono">
          Session history is empty. Inspected produce items will be logged here.
        </div>
      )}
    </div>
  );
};
