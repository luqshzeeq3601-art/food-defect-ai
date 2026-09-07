import React from 'react';
import { SlidersHorizontal, Lightning } from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';

interface CalibrationPanelProps {
  onTriggerInspect: () => void;
  isInspecting: boolean;
}

export const CalibrationPanel: React.FC<CalibrationPanelProps> = ({
  onTriggerInspect,
  isInspecting,
}) => {
  const {
    modelPrecision,
    confidenceThreshold,
    gradeAThreshold,
    gradeBThreshold,
    setModelPrecision,
    setConfidenceThreshold,
    setGradeAThreshold,
    setGradeBThreshold,
    activeImage,
  } = useInspectionStore();

  return (
    <div className="space-y-4 rounded-lg border border-[#1F2937] bg-[#111827] p-4">
      <div className="flex items-center justify-between border-b border-[#1F2937] pb-2.5">
        <h2 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-gray-300">
          <SlidersHorizontal size={16} className="text-cyan-400" />
          Sorting Calibration
        </h2>
      </div>

      {/* Model Precision Selector */}
      <div className="space-y-1.5">
        <label className="text-[11px] font-medium uppercase tracking-wider text-gray-400">
          Model Engine Precision
        </label>
        <div className="grid grid-cols-2 gap-2">
          <button
            type="button"
            onClick={() => setModelPrecision('fp32')}
            className={`rounded border px-3 py-1.5 text-xs font-mono font-medium transition-all ${
              modelPrecision === 'fp32'
                ? 'border-cyan-500 bg-cyan-500/15 text-cyan-300 shadow-[0_0_10px_rgba(6,182,212,0.2)]'
                : 'border-[#1F2937] bg-[#0B0F19] text-gray-400 hover:text-gray-200'
            }`}
          >
            FP32 (45.2 MB)
          </button>
          <button
            type="button"
            onClick={() => setModelPrecision('int8')}
            className={`rounded border px-3 py-1.5 text-xs font-mono font-medium transition-all ${
              modelPrecision === 'int8'
                ? 'border-cyan-500 bg-cyan-500/15 text-cyan-300 shadow-[0_0_10px_rgba(6,182,212,0.2)]'
                : 'border-[#1F2937] bg-[#0B0F19] text-gray-400 hover:text-gray-200'
            }`}
          >
            INT8 (11.8 MB)
          </button>
        </div>
      </div>

      {/* Confidence Threshold */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-xs">
          <label className="text-[11px] font-medium uppercase tracking-wider text-gray-400">
            Detection Confidence
          </label>
          <span className="font-mono text-cyan-400 font-semibold">
            {confidenceThreshold.toFixed(2)}
          </span>
        </div>
        <input
          type="range"
          min={0.1}
          max={1.0}
          step={0.05}
          value={confidenceThreshold}
          onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
          className="w-full accent-cyan-500 cursor-pointer"
        />
        <div className="flex justify-between text-[10px] font-mono text-gray-500">
          <span>0.10 (Sensitive)</span>
          <span>1.00 (Strict)</span>
        </div>
      </div>

      {/* Tolerance Limits: Grade A & B */}
      <div className="space-y-3 pt-1 border-t border-[#1F2937]/60">
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[11px] font-medium uppercase tracking-wider text-emerald-400">
              Grade A Max Defect
            </span>
            <span className="font-mono text-emerald-400 font-semibold">
              {gradeAThreshold.toFixed(1)}%
            </span>
          </div>
          <input
            type="range"
            min={0.0}
            max={3.0}
            step={0.1}
            value={gradeAThreshold}
            onChange={(e) => setGradeAThreshold(parseFloat(e.target.value))}
            className="w-full accent-emerald-500 cursor-pointer"
          />
        </div>

        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs">
            <span className="text-[11px] font-medium uppercase tracking-wider text-amber-400">
              Grade B Max Defect
            </span>
            <span className="font-mono text-amber-400 font-semibold">
              {gradeBThreshold.toFixed(1)}%
            </span>
          </div>
          <input
            type="range"
            min={1.0}
            max={10.0}
            step={0.5}
            value={gradeBThreshold}
            onChange={(e) => setGradeBThreshold(parseFloat(e.target.value))}
            className="w-full accent-amber-500 cursor-pointer"
          />
        </div>
      </div>

      {/* Main Trigger Button */}
      <button
        type="button"
        disabled={!activeImage || isInspecting}
        onClick={onTriggerInspect}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-cyan-500 px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-gray-950 transition-all hover:bg-cyan-400 hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] disabled:cursor-not-allowed disabled:opacity-40"
      >
        <Lightning size={16} weight="fill" />
        {isInspecting ? 'Running Inspection...' : 'Run AOI Inspection'}
      </button>
    </div>
  );
};
