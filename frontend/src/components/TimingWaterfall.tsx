import React from 'react';
import { Timer } from '@phosphor-icons/react';
import type { InspectionTiming } from '../api/types';

interface TimingWaterfallProps {
  timing?: InspectionTiming;
}

export const TimingWaterfall: React.FC<TimingWaterfallProps> = ({ timing }) => {
  if (!timing) return null;

  const total = Math.max(0.1, timing.total_ms);
  const fps = 1000.0 / total;

  const stages = [
    { label: 'Preprocess', ms: timing.preprocess_ms, color: 'bg-blue-500' },
    { label: 'ONNX Inference', ms: timing.inference_ms, color: 'bg-cyan-500' },
    { label: 'Postprocess', ms: timing.postprocess_ms, color: 'bg-indigo-500' },
    { label: 'Grading Rule', ms: timing.grading_ms, color: 'bg-emerald-500' },
  ];

  return (
    <div className="space-y-2 rounded-xl border border-[#E5EBF5] bg-white p-4 text-xs shadow-xs">
      <div className="flex items-center justify-between border-b border-gray-100 pb-2">
        <span className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-gray-800">
          <Timer size={16} className="text-blue-600" weight="bold" />
          Pipeline Latency Waterfall
        </span>
        <div className="flex items-center gap-2 font-mono">
          <span className="font-bold text-gray-900">{timing.total_ms.toFixed(1)} ms</span>
          <span className="text-gray-300">|</span>
          <span className="text-emerald-600 font-bold">{fps.toFixed(0)} FPS</span>
        </div>
      </div>

      {/* Latency Proportional Bar */}
      <div className="flex h-2.5 w-full overflow-hidden rounded-full bg-gray-100 shadow-inner">
        {stages.map((stg) => {
          const pct = Math.max(2, (stg.ms / total) * 100);
          return (
            <div
              key={stg.label}
              style={{ width: `${pct}%` }}
              className={`${stg.color} transition-all duration-300`}
              title={`${stg.label}: ${stg.ms.toFixed(2)} ms`}
            />
          );
        })}
      </div>

      {/* Stage Labels Grid */}
      <div className="grid grid-cols-4 gap-2 font-mono text-[10px] text-gray-500">
        {stages.map((stg) => (
          <div key={stg.label} className="truncate">
            <span className="text-gray-400 block truncate">{stg.label}</span>
            <span className="text-gray-800 font-bold">{stg.ms.toFixed(1)}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
};
