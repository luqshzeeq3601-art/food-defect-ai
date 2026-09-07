import React, { useEffect } from 'react';
import {
  X,
  Question,
  Keyboard,
  ShieldCheck,
  CheckCircle,
  WarningCircle,
  XCircle,
  Camera,
} from '@phosphor-icons/react';

interface HelpModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HelpModal: React.FC<HelpModalProps> = ({ isOpen, onClose }) => {
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
      <div className="relative w-full max-w-xl overflow-hidden rounded-3xl border border-slate-200/80 dark:border-[#262B33] bg-white dark:bg-[#16191E] shadow-2xl transition-colors">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-blue-50 dark:bg-blue-950/50 text-[#2563EB] dark:text-sky-400 shadow-2xs">
              <Question size={22} weight="bold" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-white leading-tight tracking-tight">
                Operator Guide & Reference
              </h3>
              <p className="text-xs text-slate-400 dark:text-slate-500 font-medium">
                Industrial AOI station operating protocols & keyboard shortcuts
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-700 dark:hover:text-slate-200 transition-colors cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto text-xs text-gray-700 dark:text-slate-300">
          {/* Section 1: Hotkeys */}
          <div>
            <h4 className="flex items-center gap-1.5 font-bold text-gray-900 dark:text-white mb-2.5">
              <Keyboard size={16} className="text-blue-600 dark:text-sky-400" />
              Keyboard Hotkeys
            </h4>
            <div className="grid grid-cols-3 gap-2 font-mono">
              <div className="rounded-xl border border-gray-200 dark:border-slate-800 bg-gray-50/60 dark:bg-[#1A1F26] p-2.5 text-center">
                <kbd className="inline-block rounded-md border border-gray-300 dark:border-slate-700 bg-white dark:bg-[#16191E] px-2 py-1 text-xs font-bold text-gray-800 dark:text-slate-200 shadow-2xs">
                  Space
                </kbd>
                <span className="block mt-1.5 text-[11px] font-sans text-gray-600 dark:text-slate-400">
                  Run Inspection
                </span>
              </div>
              <div className="rounded-xl border border-gray-200 dark:border-slate-800 bg-gray-50/60 dark:bg-[#1A1F26] p-2.5 text-center">
                <kbd className="inline-block rounded-md border border-gray-300 dark:border-slate-700 bg-white dark:bg-[#16191E] px-2 py-1 text-xs font-bold text-gray-800 dark:text-slate-200 shadow-2xs">
                  R
                </kbd>
                <span className="block mt-1.5 text-[11px] font-sans text-gray-600 dark:text-slate-400">
                  Reset Conveyor
                </span>
              </div>
              <div className="rounded-xl border border-gray-200 dark:border-slate-800 bg-gray-50/60 dark:bg-[#1A1F26] p-2.5 text-center">
                <kbd className="inline-block rounded-md border border-gray-300 dark:border-slate-700 bg-white dark:bg-[#16191E] px-2 py-1 text-xs font-bold text-gray-800 dark:text-slate-200 shadow-2xs">
                  Esc
                </kbd>
                <span className="block mt-1.5 text-[11px] font-sans text-gray-600 dark:text-slate-400">
                  Close Dialogs
                </span>
              </div>
            </div>
          </div>

          {/* Section 2: Quality Standards */}
          <div>
            <h4 className="flex items-center gap-1.5 font-bold text-gray-900 dark:text-white mb-2.5">
              <ShieldCheck size={16} className="text-blue-600 dark:text-sky-400" />
              Grading & Sorting Standards
            </h4>
            <div className="space-y-2">
              <div className="flex items-start gap-2.5 rounded-xl border border-emerald-100 dark:border-emerald-900/50 bg-emerald-50/50 dark:bg-emerald-950/20 p-3">
                <CheckCircle size={18} weight="fill" className="text-emerald-500 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-emerald-900 dark:text-emerald-300">Grade A (Premium / Export)</div>
                  <p className="text-[11px] text-emerald-800 dark:text-emerald-400 mt-0.5">
                    Defect ratio ≤ 1.0% of total fruit surface area. Zero rot or fungal decay. Routed to Packaging Conveyor #1.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 rounded-xl border border-amber-100 dark:border-amber-900/50 bg-amber-50/50 dark:bg-amber-950/20 p-3">
                <WarningCircle size={18} weight="fill" className="text-amber-500 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-amber-900 dark:text-amber-300">Grade B (Commercial / Processing)</div>
                  <p className="text-[11px] text-amber-800 dark:text-amber-400 mt-0.5">
                    Defect ratio between 1.0% and 5.0%. Cosmetic blemishes only. Zero rot. Routed to Secondary Sort #2.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-2.5 rounded-xl border border-rose-100 dark:border-rose-900/50 bg-rose-50/50 dark:bg-rose-950/20 p-3">
                <XCircle size={18} weight="fill" className="text-rose-500 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-rose-900 dark:text-rose-300">Reject (Industrial Scrap)</div>
                  <p className="text-[11px] text-rose-800 dark:text-rose-400 mt-0.5">
                    Defect ratio &gt; 5.0% OR any detected rot flaw (zero-tolerance policy). Automatically diverted to Reject Chute #3.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Camera Feed Ingestion */}
          <div>
            <h4 className="flex items-center gap-1.5 font-bold text-gray-900 dark:text-white mb-2">
              <Camera size={16} className="text-blue-600 dark:text-sky-400" />
              Optical Frame Ingestion
            </h4>
            <ul className="list-disc list-inside space-y-1 text-[11px] text-gray-600 dark:text-slate-400 leading-relaxed">
              <li><strong>Sample Library:</strong> Use the 8 pre-calibrated factory captures to test healthy vs defective apples.</li>
              <li><strong>Local File Upload:</strong> Drag & drop any camera capture directly into the Conveyor dropzone.</li>
              <li><strong>Real-Time Overlay:</strong> Hover over rows in the defect table to isolate and locate flaws on the canvas.</li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end border-t border-gray-100 dark:border-slate-800 bg-gray-50/50 dark:bg-[#1A1F26] px-6 py-4">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl bg-blue-600 hover:bg-blue-700 px-5 py-2 text-xs font-semibold text-white shadow-sm transition-all cursor-pointer"
          >
            Got It
          </button>
        </div>
      </div>
    </div>
  );
};
