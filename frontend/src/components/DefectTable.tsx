import React from 'react';
import { Table, ShieldCheck } from '@phosphor-icons/react';
import type { DetectedDefect } from '../api/types';
import { useInspectionStore } from '../store/useInspectionStore';

interface DefectTableProps {
  defects: DetectedDefect[];
}

export const DefectTable: React.FC<DefectTableProps> = ({ defects }) => {
  const { hoveredDefectId, setHoveredDefectId } = useInspectionStore();

  return (
    <div className="rounded-2xl border border-[#E5EBF5] bg-white overflow-hidden shadow-xs">
      <div className="flex items-center justify-between border-b border-gray-100 px-5 py-3">
        <h3 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-gray-800">
          <Table size={16} className="text-blue-600" weight="bold" />
          Defect Spatial Quantification Breakdown
        </h3>
        <span className="font-mono text-xs text-gray-500 font-medium">
          {defects.length} {defects.length === 1 ? 'flaw' : 'flaws'} detected
        </span>
      </div>

      {defects.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="border-b border-[#E5EBF5] bg-[#F8FAFD] text-[10px] uppercase font-semibold text-gray-400">
              <tr>
                <th className="px-4 py-2.5">ID</th>
                <th className="px-4 py-2.5">Defect Type</th>
                <th className="px-4 py-2.5">Classification</th>
                <th className="px-4 py-2.5">Confidence</th>
                <th className="px-4 py-2.5">Area (px)</th>
                <th className="px-4 py-2.5">Bounding Box (Norm)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F1F5F9] bg-white">
              {defects.map((defect) => {
                const isHovered = hoveredDefectId === defect.defect_id;
                const isRot = defect.defect_type.toLowerCase().includes('rot');

                return (
                  <tr
                    key={defect.defect_id}
                    onMouseEnter={() => setHoveredDefectId(defect.defect_id)}
                    onMouseLeave={() => setHoveredDefectId(null)}
                    className={`cursor-pointer transition-colors ${
                      isHovered
                        ? 'bg-blue-50/80 text-blue-900'
                        : 'hover:bg-gray-50/70 text-gray-700'
                    }`}
                  >
                    <td className="px-4 py-2.5 font-bold text-blue-600">
                      #{defect.defect_id}
                    </td>
                    <td className="px-4 py-2.5 font-semibold text-gray-900">
                      {defect.defect_type.toUpperCase()}
                    </td>
                    <td className="px-4 py-2.5">
                      <span
                        className={`inline-block rounded-md px-2 py-0.5 text-[10px] font-bold ${
                          isRot
                            ? 'bg-rose-50 text-rose-700 border border-rose-200'
                            : 'bg-amber-50 text-amber-800 border border-amber-200'
                        }`}
                      >
                        {isRot ? 'CRITICAL (ROT)' : 'COSMETIC BLEMISH'}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 font-medium">
                      {(defect.confidence * 100).toFixed(1)}%
                    </td>
                    <td className="px-4 py-2.5 font-bold text-gray-900">
                      {defect.pixel_area.toLocaleString()} px
                    </td>
                    <td className="px-4 py-2.5 text-[11px] text-gray-500">
                      ({defect.bbox.x_min.toFixed(2)}, {defect.bbox.y_min.toFixed(2)}) → (
                      {defect.bbox.x_max.toFixed(2)}, {defect.bbox.y_max.toFixed(2)})
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="flex items-center justify-center gap-2 p-6 text-xs text-gray-500 font-sans">
          <ShieldCheck size={18} className="text-emerald-500" weight="fill" />
          <span>Surface clean. No defect polygons identified above confidence threshold.</span>
        </div>
      )}
    </div>
  );
};
