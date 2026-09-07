import React, { useState, useEffect } from 'react';
import { X, Gear, Check, DownloadSimple, Cpu, SlidersHorizontal } from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [nmsThreshold, setNmsThreshold] = useState<number>(0.45);
  const [triggerMode, setTriggerMode] = useState<'manual' | 'optical_sensor' | 'continuous'>('manual');
  const [autoInspectOnUpload, setAutoInspectOnUpload] = useState<boolean>(true);
  const [isSaved, setIsSaved] = useState<boolean>(false);

  const { modelPrecision, confidenceThreshold, gradeAThreshold, gradeBThreshold } =
    useInspectionStore();

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

  const handleExportConfig = () => {
    const config = {
      station: 'Inspec-Belt AI',
      export_time: new Date().toISOString(),
      model: {
        precision: modelPrecision,
        confidence_threshold: confidenceThreshold,
        nms_threshold: nmsThreshold,
        execution_provider: 'CPUExecutionProvider',
        thread_pool_size: 4,
      },
      sorting_thresholds: {
        grade_a_max_defect_percent: gradeAThreshold,
        grade_b_max_defect_percent: gradeBThreshold,
        rot_defect_tolerance_percent: 0.0,
      },
      conveyor_trigger: {
        mode: triggerMode,
        auto_inspect_on_upload: autoInspectOnUpload,
      },
    };

    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `InspecBelt_AOI_Config_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSave = () => {
    setIsSaved(true);
    setTimeout(() => {
      setIsSaved(false);
      onClose();
    }, 400);
  };

  return (
    <div
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-xs p-4 animate-in fade-in duration-150"
    >
      <div className="relative w-full max-w-lg overflow-hidden rounded-2xl border border-gray-200 dark:border-[#262B33] bg-white dark:bg-[#16191E] shadow-2xl transition-colors">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-100 dark:border-slate-800 px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400">
              <Gear size={20} weight="bold" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-gray-900 dark:text-white">Station Configuration</h3>
              <p className="text-xs text-gray-500 dark:text-slate-400">
                Inference parameters & conveyor trigger settings
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 dark:hover:bg-slate-800 hover:text-gray-700 dark:hover:text-slate-200 transition-colors cursor-pointer"
          >
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          {/* NMS IoU Threshold */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-gray-700 dark:text-slate-300 flex items-center gap-1.5">
                <SlidersHorizontal size={14} className="text-blue-500 dark:text-sky-400" />
                NMS IoU Overlap Threshold
              </span>
              <span className="font-mono font-bold text-blue-600 dark:text-sky-400">{nmsThreshold.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min={0.1}
              max={0.9}
              step={0.05}
              value={nmsThreshold}
              onChange={(e) => setNmsThreshold(parseFloat(e.target.value))}
              className="w-full accent-blue-600 dark:accent-sky-400 cursor-pointer"
            />
            <div className="flex justify-between text-[11px] font-mono text-gray-500 dark:text-slate-400">
              <span>0.10 (Aggressive Dedup)</span>
              <span>0.90 (Allow Overlaps)</span>
            </div>
          </div>

          {/* Conveyor Trigger Mode */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-700 dark:text-slate-300 block">
              Conveyor Optical Sensor Trigger Mode
            </label>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <button
                type="button"
                onClick={() => setTriggerMode('manual')}
                className={`p-2.5 rounded-xl border text-center transition-all cursor-pointer ${
                  triggerMode === 'manual'
                    ? 'border-blue-400 dark:border-blue-600 bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 font-bold shadow-xs'
                    : 'border-gray-200 dark:border-slate-800 text-gray-600 dark:text-slate-400 bg-white dark:bg-[#1A1F26] hover:bg-gray-50 dark:hover:bg-slate-800'
                }`}
              >
                Manual (Space/Click)
              </button>
              <button
                type="button"
                onClick={() => setTriggerMode('optical_sensor')}
                className={`p-2.5 rounded-xl border text-center transition-all cursor-pointer ${
                  triggerMode === 'optical_sensor'
                    ? 'border-blue-400 dark:border-blue-600 bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 font-bold shadow-xs'
                    : 'border-gray-200 dark:border-slate-800 text-gray-600 dark:text-slate-400 bg-white dark:bg-[#1A1F26] hover:bg-gray-50 dark:hover:bg-slate-800'
                }`}
              >
                Optical Sensor
              </button>
              <button
                type="button"
                onClick={() => setTriggerMode('continuous')}
                className={`p-2.5 rounded-xl border text-center transition-all cursor-pointer ${
                  triggerMode === 'continuous'
                    ? 'border-blue-400 dark:border-blue-600 bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 font-bold shadow-xs'
                    : 'border-gray-200 dark:border-slate-800 text-gray-600 dark:text-slate-400 bg-white dark:bg-[#1A1F26] hover:bg-gray-50 dark:hover:bg-slate-800'
                }`}
              >
                Continuous Stream
              </button>
            </div>
          </div>

          {/* Auto-Inspect Switch */}
          <div className="flex items-center justify-between rounded-xl border border-gray-200 dark:border-slate-800 bg-gray-50/50 dark:bg-[#1A1F26] p-3.5">
            <div>
              <p className="text-xs font-semibold text-gray-800 dark:text-slate-200">Auto-Inspect On Ingestion</p>
              <p className="text-[11px] text-gray-500 dark:text-slate-400">
                Immediately trigger inference when a frame is uploaded or selected
              </p>
            </div>
            <button
              type="button"
              onClick={() => setAutoInspectOnUpload(!autoInspectOnUpload)}
              className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-hidden ${
                autoInspectOnUpload ? 'bg-blue-600' : 'bg-gray-300 dark:bg-slate-700'
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out ${
                  autoInspectOnUpload ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* Engine Telemetry Card */}
          <div className="rounded-xl border border-blue-100 dark:border-blue-900/50 bg-blue-50/40 dark:bg-blue-950/20 p-4 space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-blue-900 dark:text-blue-300">
              <Cpu size={16} className="text-blue-600 dark:text-sky-400" />
              <span>Runtime Engine Diagnostics</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-gray-600 dark:text-slate-400">
              <div>Runtime: <span className="text-gray-900 dark:text-slate-200 font-semibold">ONNX v1.20</span></div>
              <div>Execution: <span className="text-gray-900 dark:text-slate-200 font-semibold">CPUExecutionProvider</span></div>
              <div>Active Model: <span className="text-gray-900 dark:text-slate-200 font-semibold">{modelPrecision.toUpperCase()}</span></div>
              <div>Resolution: <span className="text-gray-900 dark:text-slate-200 font-semibold">640 × 640 px</span></div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between border-t border-gray-100 dark:border-slate-800 bg-gray-50/50 dark:bg-[#1A1F26] px-6 py-4">
          <button
            type="button"
            onClick={handleExportConfig}
            className="flex items-center gap-1.5 text-xs font-semibold text-gray-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-sky-400 transition-colors cursor-pointer"
          >
            <DownloadSimple size={15} weight="bold" />
            <span>Export JSON Config</span>
          </button>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-[#16191E] px-4 py-2 text-xs font-semibold text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors shadow-2xs cursor-pointer"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="flex items-center gap-1.5 rounded-xl bg-blue-600 dark:bg-blue-600 hover:bg-blue-700 dark:hover:bg-blue-500 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all cursor-pointer"
            >
              {isSaved ? (
                <>
                  <Check size={14} weight="bold" />
                  <span>Saved!</span>
                </>
              ) : (
                <span>Save Settings</span>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
