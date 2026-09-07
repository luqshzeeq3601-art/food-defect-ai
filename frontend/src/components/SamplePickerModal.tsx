import React, { useEffect } from 'react';
import { X, Check } from '@phosphor-icons/react';
import { PRESET_SAMPLES, type PresetSample } from '../constants/presets';
import { useInspectionStore } from '../store/useInspectionStore';

interface SamplePickerModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSample: (sample: PresetSample) => void;
}

export const SamplePickerModal: React.FC<SamplePickerModalProps> = ({
  isOpen,
  onClose,
  onSelectSample,
}) => {
  const sampleName = useInspectionStore((s) => s.sampleName);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-in fade-in duration-150"
    >
      <div className="relative w-full max-w-2xl overflow-hidden rounded-2xl border border-gray-200 dark:border-[#262B33] bg-white dark:bg-[#16191E] shadow-2xl transition-colors">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 px-6 py-4">
          <div>
            <h3 className="text-sm font-bold text-gray-900 dark:text-white">
              Calibrated Conveyor Sample Library
            </h3>
            <p className="text-xs text-gray-500 dark:text-slate-400">
              Select a pre-calibrated factory capture to test defect segmentation
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-800 hover:text-gray-700 dark:hover:text-slate-200 transition-colors cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Samples Grid */}
        <div className="max-h-[60vh] overflow-y-auto p-6 grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          {PRESET_SAMPLES.map((sample) => {
            const isSelected = sampleName === sample.name;
            let badgeClass = 'bg-gray-100 dark:bg-slate-800 text-gray-600 dark:text-slate-300 border border-gray-200 dark:border-slate-700';
            if (sample.expectedGrade === 'REJECT') {
              badgeClass = 'bg-rose-50 dark:bg-rose-950/50 text-rose-600 dark:text-rose-300 border border-rose-200 dark:border-rose-800';
            } else if (sample.expectedGrade === 'PASS_GRADE_B') {
              badgeClass = 'bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800';
            } else if (sample.expectedGrade === 'PASS_GRADE_A') {
              badgeClass = 'bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800';
            } else if (sample.expectedGrade === 'NO_OBJECT') {
              badgeClass = 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700';
            }

            return (
              <div
                key={sample.id}
                onClick={() => {
                  onSelectSample(sample);
                  onClose();
                }}
                className={`group relative cursor-pointer overflow-hidden rounded-xl border p-2.5 transition-all text-left ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50/40 dark:bg-blue-950/30 shadow-sm ring-2 ring-blue-500/20'
                    : 'border-gray-200 dark:border-slate-800 bg-white dark:bg-[#1A1F26] hover:border-blue-300 dark:hover:border-blue-600 hover:shadow-sm'
                }`}
              >
                <div className="aspect-square w-full overflow-hidden rounded-lg bg-gray-100 dark:bg-slate-900 mb-2">
                  <img
                    src={sample.path}
                    alt={sample.name}
                    className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-200"
                  />
                </div>
                <div className="flex items-center justify-between gap-1 mb-1">
                  <span
                    className={`rounded px-1.5 py-0.5 text-[11px] font-bold uppercase tracking-wider ${badgeClass}`}
                  >
                    {sample.badgeText || sample.category}
                  </span>
                  {isSelected && (
                    <span className="flex h-4 w-4 items-center justify-center rounded-full bg-blue-500 text-white">
                      <Check size={10} weight="bold" />
                    </span>
                  )}
                </div>
                <h4 className="text-xs font-bold text-gray-800 dark:text-slate-100 line-clamp-1">
                  {sample.name}
                </h4>
                <p className="text-[11px] text-gray-500 dark:text-slate-400 line-clamp-2 mt-0.5">
                  {sample.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
