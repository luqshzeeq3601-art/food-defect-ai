import React from 'react';
import {
  CheckCircle,
  XCircle,
  MinusCircle,
  ArrowBendDownRight,
  Sparkle,
  CornersOut,
  SlidersHorizontal,
} from '@phosphor-icons/react';
import { type InspectionResponse, normalizeGrade } from '../api/types';
import { useInspectionStore } from '../store/useInspectionStore';

interface InspectionHUDProps {
  result: InspectionResponse | null;
}

export const InspectionHUD: React.FC<InspectionHUDProps> = ({ result }) => {
  const {
    gradeAThreshold,
    gradeBThreshold,
    hoveredDefectId,
    setHoveredDefectId,
  } = useInspectionStore();

  if (!result) return null;

  const { defect_ratio_percent, reject_reason, defects, timing } = result;
  const gradeKey = normalizeGrade(result.grade);

  // Status configurations - clean Swiss minimalism with clear semantic colors
  const statusConfig = {
    GRADE_A: {
      label: 'GRADE A · EXPORT',
      pill: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/25',
      textColor: 'text-emerald-600 dark:text-emerald-400',
      barColor: 'bg-emerald-500',
      icon: <CheckCircle size={18} weight="fill" className="text-emerald-500" />,
      subtitle: `Optimal surface quality (≤ ${gradeAThreshold.toFixed(1)}% export threshold).`,
      route: 'Chute #1 (Packaging / Export)',
    },
    GRADE_B: {
      label: 'GRADE B · COMMERCIAL',
      pill: 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/25',
      textColor: 'text-amber-600 dark:text-amber-400',
      barColor: 'bg-amber-500',
      icon: <CheckCircle size={18} weight="fill" className="text-amber-500" />,
      subtitle: `Minor cosmetic blemish (≤ ${gradeBThreshold.toFixed(1)}% commercial threshold).`,
      route: 'Chute #2 (Secondary Sort)',
    },
    REJECT: {
      label: 'REJECT · SCRAP',
      pill: 'bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/25',
      textColor: 'text-rose-600 dark:text-rose-400',
      barColor: 'bg-rose-500',
      icon: <XCircle size={18} weight="fill" className="text-rose-500" />,
      subtitle: reject_reason || `Defect exceeds commercial limit (${defect_ratio_percent.toFixed(1)}% > ${gradeBThreshold.toFixed(1)}%).`,
      route: 'Chute #3 (Reject Chute)',
    },
    NO_OBJECT: {
      label: 'STANDBY · NO FRUIT',
      pill: 'bg-slate-500/10 text-slate-600 dark:text-slate-400 border-slate-500/20',
      textColor: 'text-slate-500 dark:text-slate-400',
      barColor: 'bg-slate-400',
      icon: <MinusCircle size={18} weight="bold" className="text-slate-400" />,
      subtitle: 'Conveyor belt empty. Awaiting produce feed.',
      route: 'Conveyor Belt (Standby)',
    },
  }[gradeKey];

  // Timing metrics
  const totalMs = Math.max(0.1, timing?.total_ms || 0);
  const inferenceMs = timing?.inference_ms || 0;
  const fps = (1000.0 / totalMs).toFixed(0);

  // Calibrated tolerance progress: 0% to 7% scale (max limit)
  const maxScale = Math.max(7.0, gradeBThreshold + 2.0);
  const fillPercent = Math.min(100, Math.max(0, (defect_ratio_percent / maxScale) * 100));
  const gradeAPercent = (gradeAThreshold / maxScale) * 100;
  const gradeBPercent = (gradeBThreshold / maxScale) * 100;

  return (
    <div className="w-full rounded-2xl border border-slate-200/80 dark:border-[#262B33] bg-white dark:bg-[#16191E] shadow-sm p-5 space-y-4 transition-colors">
      {/* 1. Header: Verdict Pill + Defect % + Route Pill */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            {statusConfig.icon}
            <span className={`px-2.5 py-1 rounded-lg border text-xs font-bold font-mono uppercase tracking-wide ${statusConfig.pill}`}>
              {statusConfig.label}
            </span>
          </div>

          <span className="text-slate-200 dark:text-slate-800">|</span>

          {/* Core Defect Metric */}
          <div className="flex items-baseline gap-1.5">
            <span className={`text-xl font-bold font-mono tabular-nums ${statusConfig.textColor}`}>
              {defect_ratio_percent.toFixed(2)}%
            </span>
            <span className="text-xs text-slate-400 dark:text-slate-500">
              defect area
            </span>
          </div>
        </div>

        {/* Route Target Pill */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-slate-50 dark:bg-[#1D222A] text-xs font-medium text-slate-700 dark:text-slate-300">
          <ArrowBendDownRight size={14} className="text-blue-600 dark:text-sky-400 shrink-0" />
          <span className="text-slate-400 dark:text-slate-500 font-mono text-[11px]">ROUTE:</span>
          <span className="font-semibold text-slate-800 dark:text-slate-200">{statusConfig.route}</span>
        </div>
      </div>

      {/* Subtitle / Diagnostic Reason */}
      <p className="text-xs text-slate-500 dark:text-slate-400 font-normal leading-relaxed -mt-1">
        {statusConfig.subtitle}
      </p>

      {/* 2. Sleek Calibrated Tolerance Bar */}
      <div className="pt-1">
        <div className="relative h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800/80 overflow-hidden">
          {/* Active progress fill */}
          <div
            style={{ width: `${fillPercent}%` }}
            className={`h-full ${statusConfig.barColor} transition-all duration-300 rounded-full`}
            title={`Defect Area: ${defect_ratio_percent.toFixed(2)}%`}
          />
        </div>

        {/* Threshold Markers & Labels */}
        <div className="relative mt-1.5 text-[11px] font-mono text-slate-400 dark:text-slate-500 flex justify-between">
          <span>0%</span>

          {/* Grade A Tick */}
          <span
            style={{ left: `${gradeAPercent}%` }}
            className="absolute -translate-x-1/2 flex items-center gap-1"
            title={`Grade A export limit: ≤ ${gradeAThreshold}%`}
          >
            <span className="text-slate-300 dark:text-slate-700">•</span>
            <span>A ≤ {gradeAThreshold.toFixed(1)}%</span>
          </span>

          {/* Grade B Tick */}
          <span
            style={{ left: `${gradeBPercent}%` }}
            className="absolute -translate-x-1/2 flex items-center gap-1"
            title={`Grade B commercial limit: ≤ ${gradeBThreshold}%`}
          >
            <span className="text-slate-300 dark:text-slate-700">•</span>
            <span>B ≤ {gradeBThreshold.toFixed(1)}%</span>
          </span>

          <span>Reject &gt; {gradeBThreshold.toFixed(1)}%</span>
        </div>
      </div>

      {/* 3. Streamlined Defect Flaws List */}
      <div className="border-t border-slate-100 dark:border-slate-800/80 pt-3">
        {defects.length > 0 ? (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-[11px] font-mono font-medium text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-2">
              <span className="flex items-center gap-1.5">
                <Sparkle size={13} className="text-blue-500 dark:text-sky-400" />
                Detected Surface Flaws ({defects.length})
              </span>
              <span>Hover row to highlight on canvas</span>
            </div>

            {defects.map((def) => {
              const isHovered = hoveredDefectId === def.defect_id;
              const isCritical =
                def.defect_type.toLowerCase().includes('rot') ||
                def.defect_type.toLowerCase().includes('decay');

              // Format defect name cleanly (e.g. "cosmetic_defect" -> "Cosmetic Defect")
              const cleanType = def.defect_type
                .replace(/_/g, ' ')
                .replace(/\b\w/g, (c) => c.toUpperCase());

              return (
                <div
                  key={def.defect_id}
                  onMouseEnter={() => setHoveredDefectId(def.defect_id)}
                  onMouseLeave={() => setHoveredDefectId(null)}
                  className={`flex items-center justify-between px-3 py-2 rounded-xl border text-xs transition-all cursor-pointer ${
                    isHovered
                      ? 'border-blue-300 dark:border-blue-600 bg-blue-50/50 dark:bg-blue-950/30 text-blue-900 dark:text-blue-200 shadow-2xs'
                      : 'border-slate-100 dark:border-slate-800/80 bg-slate-50/60 dark:bg-[#1A1F26] text-slate-700 dark:text-slate-300 hover:bg-slate-100/60 dark:hover:bg-[#1F252E]'
                  }`}
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span className="font-mono font-bold text-xs text-slate-400 dark:text-slate-500">
                      #{def.defect_id}
                    </span>
                    <span className="font-semibold truncate">
                      {cleanType}
                    </span>
                    {isCritical && (
                      <span className="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-600 dark:text-rose-400 border border-rose-500/20 text-[10px] font-mono font-bold uppercase tracking-wider">
                        Critical
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 font-mono text-xs text-slate-500 dark:text-slate-400 shrink-0">
                    <span className="flex items-center gap-1">
                      <SlidersHorizontal size={13} className="text-slate-400" />
                      {(def.confidence * 100).toFixed(0)}%
                    </span>
                    <span className="text-slate-300 dark:text-slate-700">•</span>
                    <span className="flex items-center gap-1 font-semibold text-slate-700 dark:text-slate-200">
                      <CornersOut size={13} className="text-slate-400" />
                      {def.pixel_area.toLocaleString()} px
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-xs text-emerald-600 dark:text-emerald-400 font-mono py-1 flex items-center gap-2">
            <CheckCircle size={15} weight="bold" />
            <span>Surface clean. No defect polygons identified above tolerance cutoff.</span>
          </div>
        )}
      </div>

      {/* 4. Quiet, Minimal Telemetry Strip */}
      <div className="border-t border-slate-100 dark:border-slate-800/80 pt-2.5 flex flex-wrap items-center justify-between text-[11px] font-mono text-slate-400 dark:text-slate-500">
        <div className="flex items-center gap-3">
          <span>
            Inference: <strong className="text-slate-700 dark:text-slate-300 font-semibold">{inferenceMs.toFixed(1)} ms</strong>
          </span>
          <span>•</span>
          <span>
            Total: <strong className="text-slate-700 dark:text-slate-300 font-semibold">{totalMs.toFixed(0)} ms</strong>
          </span>
          <span>•</span>
          <span>
            Speed: <strong className="text-slate-700 dark:text-slate-300 font-semibold">{fps} FPS</strong>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span>ONNX Runtime</span>
          <span>•</span>
          <span>CPUExecutionProvider</span>
        </div>
      </div>
    </div>
  );
};
