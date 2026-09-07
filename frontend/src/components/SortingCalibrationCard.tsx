import React, { useState } from 'react';
import {
  SlidersHorizontal,
  Globe,
  Storefront,
  Plant,
  Leaf,
  Crosshair,
  Warning,
  PencilSimple,
  Cpu,
  CaretDown,
  CaretUp,
  Lightning,
  Gauge,
  WarningCircle,
} from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';

interface QualityProfile {
  id: string;
  name: string;
  sub: string;
  gradeA: number;
  gradeB: number;
  icon: React.ReactNode;
  theme: {
    bg: string;
    border: string;
    iconBg: string;
    iconColor: string;
    ringColor: string;
  };
}

const QUALITY_PROFILES: QualityProfile[] = [
  {
    id: 'export',
    name: 'Export',
    sub: 'Zero blemish specs',
    gradeA: 1.0,
    gradeB: 3.5,
    icon: <Globe size={20} weight="duotone" />,
    theme: {
      bg: 'bg-blue-50/50 dark:bg-blue-950/20',
      border: 'border-blue-200/80 dark:border-blue-900/50',
      iconBg: 'bg-blue-100/80 dark:bg-blue-900/60',
      iconColor: 'text-[#2563EB] dark:text-sky-400',
      ringColor: 'ring-[#2563EB]',
    },
  },
  {
    id: 'commercial',
    name: 'Market Standard',
    sub: 'Domestic retail',
    gradeA: 1.5,
    gradeB: 5.0,
    icon: <Storefront size={20} weight="duotone" />,
    theme: {
      bg: 'bg-amber-50/40 dark:bg-amber-950/20',
      border: 'border-amber-200/70 dark:border-amber-900/40',
      iconBg: 'bg-amber-100/80 dark:bg-amber-900/60',
      iconColor: 'text-amber-600 dark:text-amber-400',
      ringColor: 'ring-amber-500',
    },
  },
  {
    id: 'processing',
    name: 'Juice Yield',
    sub: 'Processing recovery',
    gradeA: 3.0,
    gradeB: 8.0,
    icon: <Plant size={20} weight="duotone" />,
    theme: {
      bg: 'bg-emerald-50/40 dark:bg-emerald-950/20',
      border: 'border-emerald-200/70 dark:border-emerald-900/40',
      iconBg: 'bg-emerald-100/80 dark:bg-emerald-900/60',
      iconColor: 'text-emerald-600 dark:text-emerald-400',
      ringColor: 'ring-emerald-500',
    },
  },
];

export const SortingCalibrationCard: React.FC = () => {
  const {
    modelPrecision,
    confidenceThreshold,
    gradeAThreshold,
    gradeBThreshold,
    setModelPrecision,
    setConfidenceThreshold,
    setGradeAThreshold,
    setGradeBThreshold,
  } = useInspectionStore();

  const [customMode, setCustomMode] = useState<boolean>(false);
  const [showAdvanced, setShowAdvanced] = useState<boolean>(true);

  // Active profile matching
  const activeProfile = QUALITY_PROFILES.find(
    (p) =>
      Math.abs(p.gradeA - gradeAThreshold) < 0.05 &&
      Math.abs(p.gradeB - gradeBThreshold) < 0.05
  );

  const handleApplyProfile = (profile: QualityProfile) => {
    setGradeAThreshold(profile.gradeA);
    setGradeBThreshold(profile.gradeB);
  };

  const handleSensitivity = (level: 'tolerant' | 'standard' | 'alert') => {
    if (level === 'tolerant') setConfidenceThreshold(0.45);
    else if (level === 'standard') setConfidenceThreshold(0.35);
    else setConfidenceThreshold(0.25);
  };

  const currentSensitivity =
    confidenceThreshold >= 0.40
      ? 'tolerant'
      : confidenceThreshold <= 0.28
      ? 'alert'
      : 'standard';

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-[#262B33] bg-white dark:bg-[#16191E] p-5 sm:p-6 shadow-sm space-y-5 text-left transition-colors">
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-2xl bg-blue-50 dark:bg-blue-950/50 text-[#2563EB] dark:text-sky-400 shadow-2xs">
            <SlidersHorizontal size={22} weight="bold" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white leading-tight tracking-tight">
              Sorting & Calibration
            </h2>
            <p className="text-xs text-slate-400 dark:text-slate-500 font-medium">
              Grade Limits & Sensor Sensitivity
            </p>
          </div>
        </div>

        <span className="flex items-center gap-1.5 rounded-full bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-400 border border-rose-100 dark:border-rose-900/60 px-3 py-1 text-xs font-mono font-bold tracking-wider shrink-0">
          <WarningCircle size={14} weight="fill" className="text-rose-500" />
          <span>ROT = REJECT</span>
        </span>
      </div>

      {/* 1. Target Quality Recipe */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono uppercase font-bold text-slate-400 dark:text-slate-500 tracking-wider">
            Target Quality Recipe
          </span>
          <button
            type="button"
            onClick={() => setCustomMode(!customMode)}
            className="flex items-center gap-1 text-xs font-semibold text-[#2563EB] dark:text-sky-400 hover:underline cursor-pointer"
          >
            <span>{customMode ? 'Standard Presets' : 'Custom Mode'}</span>
            <PencilSimple size={13} weight="bold" />
          </button>
        </div>

        {customMode ? (
          /* Custom Sliders */
          <div className="rounded-2xl border border-blue-200/80 dark:border-[#262B33] bg-blue-50/20 dark:bg-[#1A1F26] p-4 space-y-3.5">
            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-emerald-700 dark:text-emerald-400 font-bold">Grade A Limit (Export)</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">≤ {gradeAThreshold.toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="0.2"
                max="3.0"
                step="0.1"
                value={gradeAThreshold}
                onChange={(e) => setGradeAThreshold(parseFloat(e.target.value))}
                className="w-full accent-[#2563EB] cursor-pointer"
              />
            </div>

            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-amber-700 dark:text-amber-400 font-bold">Grade B Limit (Commercial)</span>
                <span className="font-bold text-slate-800 dark:text-slate-200">≤ {gradeBThreshold.toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="8.0"
                step="0.2"
                value={gradeBThreshold}
                onChange={(e) => setGradeBThreshold(parseFloat(e.target.value))}
                className="w-full accent-amber-600 cursor-pointer"
              />
            </div>
          </div>
        ) : (
          /* 3 Quality Recipe Cards */
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 sm:gap-3">
            {QUALITY_PROFILES.map((prof) => {
              const isSelected = activeProfile?.id === prof.id;
              return (
                <button
                  key={prof.id}
                  type="button"
                  onClick={() => handleApplyProfile(prof)}
                  className={`group relative flex flex-col justify-between p-3.5 sm:p-4 rounded-2xl border text-left transition-all cursor-pointer ${
                    prof.theme.bg
                  } ${prof.theme.border} ${
                    isSelected
                      ? `ring-2 ${prof.theme.ringColor} shadow-sm scale-[1.01]`
                      : 'hover:border-slate-300 dark:hover:border-slate-700 hover:shadow-xs'
                  }`}
                >
                  {/* Top Row: Icon + Title Stack */}
                  <div className="flex items-center gap-3">
                    <div
                      className={`h-10 w-10 shrink-0 rounded-xl ${prof.theme.iconBg} ${prof.theme.iconColor} flex items-center justify-center transition-transform group-hover:scale-105`}
                    >
                      {prof.icon}
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-xs sm:text-sm font-bold text-slate-900 dark:text-white leading-tight truncate">
                        {prof.name}
                      </h4>
                      <p className="text-[11px] text-slate-400 dark:text-slate-500 font-medium truncate mt-0.5">
                        {prof.sub}
                      </p>
                    </div>
                  </div>

                  {/* Bottom Threshold Container */}
                  <div className="w-full bg-white dark:bg-[#16191E] rounded-xl px-3 py-1.5 mt-3 flex items-center justify-start gap-1.5 text-xs font-mono font-bold border border-slate-100/90 dark:border-slate-800 shadow-2xs">
                    <span className="text-[#2563EB] dark:text-sky-400">A ≤{prof.gradeA}%</span>
                    <span className="text-slate-300 dark:text-slate-600">•</span>
                    <span className="text-[#2563EB] dark:text-sky-400">B ≤{prof.gradeB}%</span>
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 2. Defect Sensitivity */}
      <div className="space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono uppercase font-bold text-slate-400 dark:text-slate-500 tracking-wider">
            Defect Sensitivity
          </span>
          <span className="text-xs font-mono text-slate-400 dark:text-slate-500">
            Cutoff:{' '}
            <strong className="text-[#2563EB] dark:text-sky-400 font-bold">
              {confidenceThreshold.toFixed(2)}
            </strong>
          </span>
        </div>

        <div className="grid grid-cols-3 gap-2 sm:gap-3">
          {/* Tolerant */}
          <button
            type="button"
            onClick={() => handleSensitivity('tolerant')}
            className={`py-2.5 sm:py-3 px-2 rounded-2xl text-xs font-semibold flex items-center justify-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
              currentSensitivity === 'tolerant'
                ? 'bg-[#2563EB] text-white font-bold shadow-md shadow-blue-500/25'
                : 'bg-slate-50/90 dark:bg-[#1A1F26] border border-slate-200/80 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#222832]'
            }`}
          >
            <Leaf size={16} weight={currentSensitivity === 'tolerant' ? 'fill' : 'regular'} />
            <span>Tolerant (0.45)</span>
          </button>

          {/* Standard */}
          <button
            type="button"
            onClick={() => handleSensitivity('standard')}
            className={`py-2.5 sm:py-3 px-2 rounded-2xl text-xs font-semibold flex items-center justify-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
              currentSensitivity === 'standard'
                ? 'bg-[#2563EB] text-white font-bold shadow-md shadow-blue-500/25'
                : 'bg-slate-50/90 dark:bg-[#1A1F26] border border-slate-200/80 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#222832]'
            }`}
          >
            <Crosshair size={16} weight="bold" />
            <span>Standard (0.35)</span>
          </button>

          {/* High Alert */}
          <button
            type="button"
            onClick={() => handleSensitivity('alert')}
            className={`py-2.5 sm:py-3 px-2 rounded-2xl text-xs font-semibold flex items-center justify-center gap-1.5 sm:gap-2 transition-all cursor-pointer ${
              currentSensitivity === 'alert'
                ? 'bg-[#2563EB] text-white font-bold shadow-md shadow-blue-500/25'
                : 'bg-slate-50/90 dark:bg-[#1A1F26] border border-slate-200/80 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#222832]'
            }`}
          >
            <Warning size={16} weight={currentSensitivity === 'alert' ? 'fill' : 'regular'} />
            <span>High Alert (0.25)</span>
          </button>
        </div>
      </div>

      {/* 3. Advanced Engine Runtime (Accordion Container) */}
      <div className="rounded-2xl border border-slate-200/80 dark:border-slate-800 bg-slate-50/40 dark:bg-[#16191E] overflow-hidden transition-all">
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full p-3.5 sm:p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50 dark:hover:bg-[#1A1F26] transition-colors"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/50 text-[#2563EB] dark:text-sky-400">
              <Cpu size={20} weight="fill" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white leading-tight">
                Advanced Engine Runtime
              </h3>
              <p className="text-xs text-slate-400 dark:text-slate-500 font-medium">
                Select the ONNX execution model
              </p>
            </div>
          </div>

          <div className="text-slate-400 dark:text-slate-500 p-1">
            {showAdvanced ? <CaretUp size={16} weight="bold" /> : <CaretDown size={16} weight="bold" />}
          </div>
        </button>

        {showAdvanced && (
          <div className="px-4 pb-4 pt-1 space-y-2 border-t border-slate-100 dark:border-slate-800/80">
            <span className="text-[10px] font-mono uppercase font-bold text-slate-400 dark:text-slate-500 tracking-wider block mt-2">
              ONNX Execution Model
            </span>
            <div className="grid grid-cols-2 gap-2.5 sm:gap-3">
              {/* FP32 */}
              <button
                type="button"
                onClick={() => setModelPrecision('fp32')}
                className={`py-3 px-4 rounded-2xl flex items-center justify-center gap-2 text-xs sm:text-sm transition-all cursor-pointer ${
                  modelPrecision === 'fp32'
                    ? 'border-2 border-[#2563EB] bg-blue-50/70 dark:bg-blue-950/40 text-[#2563EB] dark:text-sky-300 font-bold shadow-2xs'
                    : 'border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#1A1F26] text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 font-medium'
                }`}
              >
                <Lightning size={16} weight="fill" className="text-[#2563EB] dark:text-sky-400" />
                <span>FP32 (Precision)</span>
              </button>

              {/* INT8 */}
              <button
                type="button"
                onClick={() => setModelPrecision('int8')}
                className={`py-3 px-4 rounded-2xl flex items-center justify-center gap-2 text-xs sm:text-sm transition-all cursor-pointer ${
                  modelPrecision === 'int8'
                    ? 'border-2 border-[#2563EB] bg-blue-50/70 dark:bg-blue-950/40 text-[#2563EB] dark:text-sky-300 font-bold shadow-2xs'
                    : 'border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#1A1F26] text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 font-medium'
                }`}
              >
                <Gauge size={16} weight="bold" className="text-slate-500 dark:text-slate-400" />
                <span>INT8 (Edge Speed)</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

