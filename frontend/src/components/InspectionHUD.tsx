import React from 'react';
import {
  Check,
  X,
  Minus,
  ArrowBendDownRight,
  CaretDown,
  Sparkle,
  Info,
  Crosshair,
  BoundingBox,
  Gauge,
  Clock,
  Stack,
  Cpu,
  Circuitry,
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

  const { defect_ratio_percent = 0, reject_reason = null, defects = [], timing } = result || {};
  const gradeKey = result ? normalizeGrade(result.grade) : 'NO_OBJECT';

  // Status configurations matching industrial sorting visual design
  const statusConfig = {
    GRADE_A: {
      gradeText: 'GRADE A',
      subText: 'EXPORT QUALITY',
      badgeBg: 'bg-[#F0FDF4] dark:bg-emerald-950/30 border-[#DCFCE7] dark:border-emerald-800/40',
      iconBg: 'bg-[#10B981]',
      icon: <Check size={18} weight="bold" className="text-white" />,
      textColor: 'text-[#15803D] dark:text-emerald-400',
      subTextColor: 'text-[#166534] dark:text-emerald-300 font-bold',
      defectColor: 'text-[#15803D] dark:text-emerald-400',
      barGradient: 'from-emerald-400 to-emerald-500',
      subtitle: `Optimal surface quality (≤ ${gradeAThreshold.toFixed(1)}% export threshold).`,
      route: 'Chute #1 (Packaging / Export)',
    },
    GRADE_B: {
      gradeText: 'GRADE B',
      subText: 'COMMERCIAL',
      badgeBg: 'bg-[#FFFBEB] dark:bg-amber-950/30 border-[#FEF3C7] dark:border-amber-800/40',
      iconBg: 'bg-[#F59E0B]',
      icon: <Check size={18} weight="bold" className="text-white" />,
      textColor: 'text-[#D97706] dark:text-amber-400',
      subTextColor: 'text-[#92400E] dark:text-amber-300 font-bold',
      defectColor: 'text-[#D97706] dark:text-amber-400',
      barGradient: 'from-amber-400 to-amber-500',
      subtitle: `Minor cosmetic blemish (≤ ${gradeBThreshold.toFixed(1)}% commercial threshold).`,
      route: 'Chute #2 (Secondary Sort)',
    },
    REJECT: {
      gradeText: 'REJECT',
      subText: 'DEFECTIVE / ROT',
      badgeBg: 'bg-[#FFF1F2] dark:bg-rose-950/30 border-[#FFE4E6] dark:border-rose-800/40',
      iconBg: 'bg-[#F43F5E]',
      icon: <X size={18} weight="bold" className="text-white" />,
      textColor: 'text-[#E11D48] dark:text-rose-400',
      subTextColor: 'text-[#9F1239] dark:text-rose-300 font-bold',
      defectColor: 'text-[#E11D48] dark:text-rose-400',
      barGradient: 'from-rose-500 to-rose-600',
      subtitle: reject_reason || `Defect exceeds commercial limit (${defect_ratio_percent.toFixed(1)}% > ${gradeBThreshold.toFixed(1)}%).`,
      route: 'Chute #3 (Scrap Reject)',
    },
    NO_OBJECT: {
      gradeText: 'STANDBY',
      subText: 'AWAITING FEED',
      badgeBg: 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-700',
      iconBg: 'bg-slate-400 dark:bg-slate-600',
      icon: <Minus size={18} weight="bold" className="text-white" />,
      textColor: 'text-slate-700 dark:text-slate-300',
      subTextColor: 'text-slate-500 dark:text-slate-400',
      defectColor: 'text-slate-500 dark:text-slate-400',
      barGradient: 'from-slate-300 to-slate-400',
      subtitle: 'Conveyor belt ready. Ingest a frame and press Space to inspect.',
      route: 'Chute Routing (Standby)',
    },
  }[gradeKey];

  // Timing metrics
  const totalMs = timing?.total_ms || 0;
  const inferenceMs = timing?.inference_ms || 0;
  const fps = totalMs > 0 ? (1000.0 / totalMs).toFixed(0) : '0';

  // Calibrated tolerance progress bar calculation
  const maxScale = Math.max(10.0, gradeBThreshold * 1.35, defect_ratio_percent * 1.15);
  const fillPercent = result ? Math.min(100, Math.max(0, (defect_ratio_percent / maxScale) * 100)) : 0;
  const gradeAPercent = (gradeAThreshold / maxScale) * 100;
  const gradeBPercent = (gradeBThreshold / maxScale) * 100;

  return (
    <div className="w-full rounded-3xl border border-slate-200/80 dark:border-[#262B33] bg-white dark:bg-[#16191E] shadow-sm p-5 sm:p-6 space-y-5 transition-colors">
      {/* 1. Header: Grade Badge + Defect Area + Route Pill */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left: Grade badge & Defect metric */}
        <div className="flex flex-wrap items-center gap-3 sm:gap-4">
          {/* Grade Badge Squircle */}
          <div className={`flex items-center gap-3 px-3.5 py-2 rounded-2xl border shadow-2xs ${statusConfig.badgeBg}`}>
            <div className={`h-8 w-8 rounded-xl flex items-center justify-center shadow-xs ${statusConfig.iconBg}`}>
              {statusConfig.icon}
            </div>
            <div className="flex flex-col text-left">
              <span className={`font-black text-xs sm:text-sm font-mono tracking-wider ${statusConfig.textColor}`}>
                {statusConfig.gradeText}
              </span>
              <span className={`text-[9px] sm:text-[10px] font-bold tracking-widest uppercase font-mono ${statusConfig.subTextColor}`}>
                {statusConfig.subText}
              </span>
            </div>
          </div>

          {/* Vertical Divider */}
          <div className="h-8 w-px bg-slate-200 dark:bg-slate-800 hidden sm:block" />

          {/* Core Defect Metric & Subtitle */}
          <div className="flex flex-col">
            <div className="flex items-baseline gap-1.5">
              <span className={`text-2xl sm:text-3xl font-black font-mono tracking-tight tabular-nums ${statusConfig.defectColor}`}>
                {defect_ratio_percent.toFixed(2)}%
              </span>
              <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
                defect area
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-normal leading-tight mt-0.5">
              {statusConfig.subtitle}
            </p>
          </div>
        </div>

        {/* Right: Route Pill Dropdown */}
        <div className="flex items-center gap-3 px-4 py-2 rounded-2xl border border-slate-200/90 dark:border-slate-800 bg-[#F8FAFC]/90 dark:bg-[#1C2129] shadow-2xs min-w-[210px] justify-between">
          <div className="flex items-center gap-2.5">
            <ArrowBendDownRight size={16} weight="bold" className="text-[#2563EB] dark:text-sky-400 shrink-0" />
            <div className="flex flex-col text-left">
              <span className="text-[9px] font-bold font-mono tracking-wider text-slate-400 dark:text-slate-500 uppercase">
                ROUTE
              </span>
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">
                {statusConfig.route}
              </span>
            </div>
          </div>
          <CaretDown size={13} weight="bold" className="text-slate-400 shrink-0 ml-1" />
        </div>
      </div>

      {/* 2. Calibrated Tolerance Bar */}
      <div className="pt-1">
        <div className="relative h-2.5 w-full rounded-full bg-[#EEF2F6] dark:bg-slate-800/80 overflow-hidden">
          {/* Subtle reject background zone indicator on right */}
          <div
            style={{ left: `${gradeBPercent}%`, width: `${100 - gradeBPercent}%` }}
            className="absolute top-0 bottom-0 bg-rose-500/10 dark:bg-rose-500/20"
          />

          {/* Active progress fill */}
          <div
            style={{ width: `${fillPercent}%` }}
            className={`h-full bg-gradient-to-r ${statusConfig.barGradient} transition-all duration-300 rounded-full shadow-2xs`}
            title={`Defect Area: ${defect_ratio_percent.toFixed(2)}%`}
          />
        </div>

        {/* Threshold Markers & Labels */}
        <div className="relative mt-2 text-[11px] font-mono text-slate-500 dark:text-slate-400 flex items-center justify-between">
          <span>0%</span>

          {/* Grade A Tick */}
          <div
            style={{ left: `${gradeAPercent}%` }}
            className="absolute -translate-x-1/2 flex items-center gap-1 text-slate-600 dark:text-slate-400"
            title={`Grade A export limit: ≤ ${gradeAThreshold}%`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-slate-400 dark:bg-slate-600" />
            <span>A ≤ {gradeAThreshold.toFixed(1)}%</span>
          </div>

          {/* Grade B Tick */}
          <div
            style={{ left: `${gradeBPercent}%` }}
            className="absolute -translate-x-1/2 flex items-center gap-1 text-slate-600 dark:text-slate-400"
            title={`Grade B commercial limit: ≤ ${gradeBThreshold}%`}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-slate-400 dark:bg-slate-600" />
            <span>B ≤ {gradeBThreshold.toFixed(1)}%</span>
          </div>

          {/* Reject Limit */}
          <div className="flex items-center gap-1 text-rose-600 dark:text-rose-400 font-medium">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
            <span>Reject &gt; {gradeBThreshold.toFixed(1)}%</span>
          </div>
        </div>
      </div>

      {/* 3. Detected Surface Flaws Section */}
      <div className="rounded-2xl border border-blue-100/80 dark:border-blue-900/30 bg-[#F0F7FF]/50 dark:bg-[#131E2E]/30 p-3 sm:p-3.5 space-y-2.5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-800 dark:text-slate-200">
            <Sparkle size={15} weight="fill" className="text-[#2563EB] dark:text-sky-400" />
            <span>Detected Surface Flaws ({defects.length})</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 dark:text-slate-500 font-normal">
            <Info size={14} />
            <span>Hover row to highlight on canvas</span>
          </div>
        </div>

        {defects.length > 0 ? (
          <div className="space-y-2">
            {defects.map((def) => {
              const isHovered = hoveredDefectId === def.defect_id;
              const cleanType = def.defect_type
                .replace(/_/g, ' ')
                .replace(/\b\w/g, (c) => c.toUpperCase());

              return (
                <div
                  key={def.defect_id}
                  onMouseEnter={() => setHoveredDefectId(def.defect_id)}
                  onMouseLeave={() => setHoveredDefectId(null)}
                  className={`flex items-center justify-between px-4 py-2.5 rounded-xl border text-xs transition-all cursor-pointer ${
                    isHovered
                      ? 'border-blue-400 dark:border-blue-500 bg-blue-50/80 dark:bg-blue-950/40 shadow-xs'
                      : 'border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#16191E] hover:border-slate-300 dark:hover:border-slate-700 shadow-2xs'
                  }`}
                >
                  {/* Defect ID & Name */}
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="px-2.5 py-0.5 rounded-lg bg-blue-50 dark:bg-blue-950/60 text-[#2563EB] dark:text-sky-400 font-bold font-mono text-xs border border-blue-100/60 dark:border-blue-900/40">
                      #{def.defect_id}
                    </span>
                    <span className="font-bold text-xs text-slate-800 dark:text-slate-100 truncate">
                      {cleanType}
                    </span>
                  </div>

                  {/* Confidence & Area metrics */}
                  <div className="flex items-center gap-3 font-mono text-xs text-slate-800 dark:text-slate-200 shrink-0">
                    <div className="flex items-center gap-1.5">
                      <Crosshair size={14} className="text-slate-400" />
                      <span className="font-bold text-slate-900 dark:text-white">{(def.confidence * 100).toFixed(0)}%</span>
                    </div>

                    <div className="h-3.5 w-px bg-slate-200 dark:bg-slate-700" />

                    <div className="flex items-center gap-1.5">
                      <BoundingBox size={14} className="text-slate-400" />
                      <span className="font-bold text-slate-900 dark:text-white">{def.pixel_area.toLocaleString()} px</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="px-4 py-2.5 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#16191E] text-xs font-mono text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
            <Check size={14} weight="bold" />
            <span>Surface clean. No defect polygons identified above tolerance cutoff.</span>
          </div>
        )}
      </div>

      {/* 4. Telemetry Bottom Strip with 5 Individual Pill Chips */}
      <div className="flex flex-wrap items-center justify-between gap-2.5 pt-1">
        {/* Left: 3 Performance Metric Chips */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Inference Chip */}
          <div className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-[#F8FAFC]/90 dark:bg-[#1A1F26] shadow-2xs">
            <Gauge size={17} className="text-emerald-500 shrink-0" />
            <div className="flex flex-col text-left">
              <span className="text-[9px] font-medium text-slate-400 dark:text-slate-500">
                Inference
              </span>
              <span className="text-xs font-bold font-mono text-slate-800 dark:text-slate-200 tabular-nums">
                {inferenceMs.toFixed(1)} ms
              </span>
            </div>
          </div>

          {/* Total Chip */}
          <div className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-[#F8FAFC]/90 dark:bg-[#1A1F26] shadow-2xs">
            <Clock size={17} className="text-blue-500 shrink-0" />
            <div className="flex flex-col text-left">
              <span className="text-[9px] font-medium text-slate-400 dark:text-slate-500">
                Total
              </span>
              <span className="text-xs font-bold font-mono text-slate-800 dark:text-slate-200 tabular-nums">
                {totalMs.toFixed(0)} ms
              </span>
            </div>
          </div>

          {/* Speed Chip */}
          <div className="flex items-center gap-2.5 px-3.5 py-1.5 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-[#F8FAFC]/90 dark:bg-[#1A1F26] shadow-2xs">
            <Stack size={17} className="text-indigo-500 shrink-0" />
            <div className="flex flex-col text-left">
              <span className="text-[9px] font-medium text-slate-400 dark:text-slate-500">
                Speed
              </span>
              <span className="text-xs font-bold font-mono text-slate-800 dark:text-slate-200 tabular-nums">
                {fps} FPS
              </span>
            </div>
          </div>
        </div>

        {/* Right: 2 Runtime Engine Chips */}
        <div className="flex items-center gap-2">
          {/* ONNX Runtime Chip */}
          <div className="flex items-center gap-2 px-3.5 py-2 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-[#F8FAFC]/90 dark:bg-[#1A1F26] shadow-2xs">
            <Cpu size={15} className="text-slate-500 dark:text-slate-400 shrink-0" />
            <span className="text-xs font-bold font-mono text-slate-700 dark:text-slate-300">
              ONNX Runtime
            </span>
          </div>

          {/* CPU Execution Provider Chip */}
          <div className="flex items-center gap-2 px-3.5 py-2 rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-[#F8FAFC]/90 dark:bg-[#1A1F26] shadow-2xs">
            <Circuitry size={15} className="text-slate-500 dark:text-slate-400 shrink-0" />
            <span className="text-xs font-bold font-mono text-slate-700 dark:text-slate-300">
              CPUExecutionProvider
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
