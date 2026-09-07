import React from 'react';
import {
  CheckCircle,
  WarningCircle,
  XCircle,
  MinusCircle,
  ArrowsSplit,
  WarningOctagon,
} from '@phosphor-icons/react';
import type { InspectionResponse } from '../api/types';
import { useInspectionStore } from '../store/useInspectionStore';

interface DecisionDeckProps {
  result: InspectionResponse | null;
}

export const DecisionDeck: React.FC<DecisionDeckProps> = ({ result }) => {
  const { gradeAThreshold, gradeBThreshold } = useInspectionStore();

  if (!result) return null;

  const { grade, defect_ratio_percent, reject_reason, fruit, defects } = result;

  // Grade configuration
  let verdictStyle = {
    bg: 'bg-gray-50 border-gray-200',
    badge: 'bg-gray-200/80 text-gray-700 border-gray-300',
    title: 'NO OBJECT',
    subtitle: 'Conveyor belt empty. Awaiting produce feed.',
    action: 'STATUS: CONVEYOR CLEAR',
    icon: <MinusCircle size={24} weight="bold" className="text-gray-400" />,
  };

  if (grade === 'GRADE_A') {
    verdictStyle = {
      bg: 'bg-emerald-50/70 border-emerald-200 shadow-xs',
      badge: 'bg-emerald-100 text-emerald-800 border-emerald-300 font-bold',
      title: 'PASS (GRADE A)',
      subtitle: `Optimal surface quality. Defect area (${defect_ratio_percent.toFixed(2)}%) within ${gradeAThreshold.toFixed(1)}% export tolerance.`,
      action: 'ROUTE: PACKAGING CONVEYOR #1 (EXPORT)',
      icon: <CheckCircle size={24} weight="fill" className="text-emerald-500" />,
    };
  } else if (grade === 'GRADE_B') {
    verdictStyle = {
      bg: 'bg-amber-50/70 border-amber-200 shadow-xs',
      badge: 'bg-amber-100 text-amber-800 border-amber-300 font-bold',
      title: 'PASS (GRADE B)',
      subtitle: `Minor surface blemish detected. Approved for domestic distribution or processing.`,
      action: 'ROUTE: SECONDARY SORT #2 (COMMERCIAL)',
      icon: <WarningCircle size={24} weight="fill" className="text-amber-500" />,
    };
  } else if (grade === 'REJECT') {
    verdictStyle = {
      bg: 'bg-rose-50/70 border-rose-200 shadow-xs',
      badge: 'bg-rose-100 text-rose-800 border-rose-300 font-bold',
      title: 'REJECTED',
      subtitle: reject_reason || `Surface defect exceeds tolerance (${defect_ratio_percent.toFixed(2)}% > ${gradeBThreshold.toFixed(1)}%).`,
      action: 'ROUTE: REJECT CHUTE #3 (SCRAP)',
      icon: <XCircle size={24} weight="fill" className="text-rose-500" />,
    };
  }

  // Tolerance spectrum gauge calculations
  const needlePercent = Math.min(100, Math.max(0, (defect_ratio_percent / 7.0) * 100));

  return (
    <div className="space-y-3.5">
      {/* Hero Decision Banner */}
      <div className={`rounded-2xl border p-5 transition-all ${verdictStyle.bg}`}>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3.5">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white shadow-2xs border border-gray-100">
              {verdictStyle.icon}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className={`rounded-lg border px-2.5 py-0.5 text-xs font-mono font-bold tracking-wide ${verdictStyle.badge}`}>
                  {verdictStyle.title}
                </span>
              </div>
              <p className="mt-1 text-xs font-medium text-gray-700">
                {verdictStyle.subtitle}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-xl border border-gray-200/80 bg-white px-3.5 py-2 font-mono text-xs font-bold text-gray-800 shadow-xs">
            <ArrowsSplit size={16} className="text-blue-600" weight="bold" />
            <span>{verdictStyle.action}</span>
          </div>
        </div>

        {/* Defect Safety Spectrum Gauge */}
        <div className="mt-4 border-t border-gray-200/60 pt-3">
          <div className="flex justify-between text-[11px] font-mono text-gray-600 mb-1.5 font-medium">
            <span>Defect Ratio: <strong className="text-gray-900">{defect_ratio_percent.toFixed(2)}%</strong></span>
            <span>Grade A ≤ {gradeAThreshold.toFixed(1)}% | Grade B ≤ {gradeBThreshold.toFixed(1)}%</span>
          </div>

          <div className="relative h-2.5 w-full rounded-full bg-gray-200/80 overflow-visible flex shadow-inner">
            <div className="w-[18%] bg-emerald-500 rounded-l-full" title="Grade A (0-1%)" />
            <div className="w-[45%] bg-amber-500" title="Grade B (1-5%)" />
            <div className="w-[37%] bg-rose-500 rounded-r-full" title="Reject (>5%)" />
            {/* Position needle indicator */}
            <div
              style={{ left: `${needlePercent}%` }}
              className="absolute -top-1 h-4.5 w-1.5 -translate-x-1/2 rounded-full bg-gray-900 border-2 border-white shadow-md transition-all duration-300"
              title={`Current: ${defect_ratio_percent.toFixed(2)}%`}
            />
          </div>
        </div>
      </div>

      {/* Diagnostic Rejection Alert */}
      {reject_reason && (
        <div className="flex items-center gap-2 rounded-xl border border-rose-200 bg-rose-50 p-3.5 text-xs text-rose-800 shadow-2xs font-medium">
          <WarningOctagon size={18} className="shrink-0 text-rose-500" weight="bold" />
          <div>
            <strong>Rejection Reason:</strong> {reject_reason}
          </div>
        </div>
      )}

      {/* 4-Metric Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3.5">
        <div className="rounded-xl border border-[#E5EBF5] bg-white p-4 shadow-xs">
          <span className="text-[10px] font-mono uppercase tracking-wider text-gray-400 block font-semibold">
            Defect Area Ratio
          </span>
          <span className="text-xl font-mono font-bold text-gray-900 block mt-1">
            {defect_ratio_percent.toFixed(2)}%
          </span>
          <span className="text-[10px] text-gray-500 block font-medium">
            {defect_ratio_percent > gradeBThreshold ? 'Over Limit' : 'Within Limits'}
          </span>
        </div>

        <div className="rounded-xl border border-[#E5EBF5] bg-white p-4 shadow-xs">
          <span className="text-[10px] font-mono uppercase tracking-wider text-gray-400 block font-semibold">
            Pipeline Latency
          </span>
          <span className="text-xl font-mono font-bold text-gray-900 block mt-1">
            {result.timing.total_ms.toFixed(1)} ms
          </span>
          <span className="text-[10px] text-emerald-600 block font-semibold">
            {(1000.0 / Math.max(0.1, result.timing.total_ms)).toFixed(0)} FPS
          </span>
        </div>

        <div className="rounded-xl border border-[#E5EBF5] bg-white p-4 shadow-xs">
          <span className="text-[10px] font-mono uppercase tracking-wider text-gray-400 block font-semibold">
            Fruit Surface Pixels
          </span>
          <span className="text-xl font-mono font-bold text-gray-900 block mt-1">
            {fruit?.pixel_area ? fruit.pixel_area.toLocaleString() : '0'} px
          </span>
          <span className="text-[10px] text-gray-500 block font-medium">
            Confidence: {fruit ? `${(fruit.confidence * 100).toFixed(0)}%` : 'N/A'}
          </span>
        </div>

        <div className="rounded-xl border border-[#E5EBF5] bg-white p-4 shadow-xs">
          <span className="text-[10px] font-mono uppercase tracking-wider text-gray-400 block font-semibold">
            Active Defect Flaws
          </span>
          <span className="text-xl font-mono font-bold text-gray-900 block mt-1">
            {defects.length}
          </span>
          <span className="text-[10px] text-rose-600 block font-semibold">
            {defects.filter((d) => d.defect_type.toLowerCase().includes('rot')).length} Critical Rot
          </span>
        </div>
      </div>
    </div>
  );
};
