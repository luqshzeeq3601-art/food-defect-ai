import React, { useRef } from 'react';
import { UploadSimple, FileImage, ArrowsClockwise } from '@phosphor-icons/react';
import { PRESET_SAMPLES } from '../constants/presets';
import { useInspectionStore } from '../store/useInspectionStore';

interface ConveyorControlsProps {
  onTriggerInspect: () => void;
  isInspecting: boolean;
}

export const ConveyorControls: React.FC<ConveyorControlsProps> = ({
  onTriggerInspect,
  isInspecting,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const activeImage = useInspectionStore((s) => s.activeImage);
  const sampleName = useInspectionStore((s) => s.sampleName);
  const setActiveImage = useInspectionStore((s) => s.setActiveImage);
  const resetAll = useInspectionStore((s) => s.resetAll);

  // Load sample frame from presets
  const handleSelectPreset = async (presetId: string) => {
    const preset = PRESET_SAMPLES.find((p) => p.id === presetId);
    if (!preset) return;

    try {
      const resp = await fetch(preset.path);
      const blob = await resp.blob();
      const objectUrl = URL.createObjectURL(blob);
      setActiveImage(objectUrl, blob, preset.name);
    } catch (err) {
      console.error('Failed to load preset sample:', err);
    }
  };

  // Handle local file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    setActiveImage(objectUrl, file, file.name);
  };

  // Handle drag and drop
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      const objectUrl = URL.createObjectURL(file);
      setActiveImage(objectUrl, file, file.name);
    }
  };

  return (
    <div className="space-y-4 rounded-lg border border-[#1F2937] bg-[#111827] p-4">
      <div className="flex items-center justify-between border-b border-[#1F2937] pb-2.5">
        <h2 className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-gray-300">
          <FileImage size={16} className="text-cyan-400" />
          Conveyor Ingestion
        </h2>
        {activeImage && (
          <button
            onClick={resetAll}
            className="flex items-center gap-1 text-[11px] font-mono text-gray-400 hover:text-white transition-colors"
          >
            <ArrowsClockwise size={12} />
            RESET
          </button>
        )}
      </div>

      {/* Preset Selector Dropdown */}
      <div className="space-y-1.5">
        <label className="text-[11px] font-medium uppercase tracking-wider text-gray-400">
          Preset Conveyor Capture
        </label>
        <select
          onChange={(e) => handleSelectPreset(e.target.value)}
          defaultValue=""
          className="w-full rounded border border-[#1F2937] bg-[#0B0F19] px-3 py-2 text-xs text-gray-200 focus:border-cyan-500 focus:outline-none transition-colors"
        >
          <option value="" disabled>
            Select a calibrated factory capture...
          </option>
          {PRESET_SAMPLES.map((sample) => (
            <option key={sample.id} value={sample.id}>
              {sample.name}
            </option>
          ))}
        </select>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className="group relative flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-[#1F2937] bg-[#0B0F19]/60 p-4 text-center hover:border-cyan-500/50 hover:bg-[#0B0F19] transition-all"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/bmp"
          onChange={handleFileUpload}
          className="hidden"
        />
        <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-full bg-cyan-500/10 text-cyan-400 group-hover:scale-105 transition-transform">
          <UploadSimple size={18} />
        </div>
        <p className="text-xs font-medium text-gray-300">
          Drop optical frame or <span className="text-cyan-400 underline">browse</span>
        </p>
        <p className="mt-0.5 text-[10px] text-gray-500">
          Supports JPEG, PNG, BMP (Max 10MB)
        </p>
      </div>

      {/* Active Ingestion Indicator */}
      {activeImage && (
        <div className="rounded border border-[#1F2937] bg-[#0B0F19] p-2.5 flex items-center justify-between text-xs">
          <div className="truncate pr-2">
            <span className="text-[10px] uppercase tracking-wider text-gray-500 block">
              Active Frame
            </span>
            <span className="font-mono text-gray-200 font-medium truncate block">
              {sampleName}
            </span>
          </div>
          <button
            onClick={onTriggerInspect}
            disabled={isInspecting}
            className="shrink-0 rounded bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 px-3 py-1.5 text-xs font-semibold text-gray-950 transition-colors shadow-[0_0_12px_rgba(6,182,212,0.3)]"
          >
            {isInspecting ? 'Scanning...' : 'Inspect'}
          </button>
        </div>
      )}
    </div>
  );
};
