import React, { useRef, useState } from 'react';
import {
  Camera,
  CloudArrowUp,
  Play,
  ArrowCounterClockwise,
  CheckCircle,
  CircleNotch,
  SquaresFour,
  Sparkle,
  Image as ImageIcon,
  CaretRight,
  XCircle,
  X,
  Check,
  Warning,
  Circle,
} from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';
import { PRESET_SAMPLES, type PresetSample } from '../constants/presets';

type PresetFilter = 'ALL' | 'REJECT' | 'PASS_GRADE_A' | 'PASS_GRADE_B' | 'NO_OBJECT';

interface ConveyorIngestionCardProps {
  onOpenSampleModal: () => void;
  onSelectSample?: (sample: PresetSample) => void;
  onTriggerInspect?: () => void;
  isInspecting?: boolean;
}

export const ConveyorIngestionCard: React.FC<ConveyorIngestionCardProps> = ({
  onOpenSampleModal,
  onSelectSample,
  onTriggerInspect,
  isInspecting = false,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [activeFilter, setActiveFilter] = useState<PresetFilter>('ALL');

  const { activeImage, sampleName, setActiveImage, resetAll } = useInspectionStore();

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const objectUrl = URL.createObjectURL(file);
    setActiveImage(objectUrl, file, file.name);
    e.target.value = '';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      const objectUrl = URL.createObjectURL(file);
      setActiveImage(objectUrl, file, file.name);
    }
  };

  const filteredSamples = PRESET_SAMPLES.filter((s) => {
    if (activeFilter === 'ALL') return true;
    return s.expectedGrade === activeFilter;
  });

  return (
    <div className="rounded-3xl border border-slate-200/80 dark:border-[#262B33] bg-white dark:bg-[#16191E] p-5 sm:p-6 shadow-sm space-y-4 sm:space-y-5 transition-colors">
      {/* Top Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-2xl bg-[#2563EB] text-white shadow-xs shadow-blue-500/20">
            <Camera size={22} weight="fill" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white leading-tight tracking-tight">
              Frame Ingestion
            </h2>
            <p className="text-xs text-slate-400 dark:text-slate-500 font-medium">
              Conveyor Optical Sensor Feed
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {activeImage && (
            <button
              type="button"
              onClick={resetAll}
              className="hidden sm:flex items-center gap-1 text-[11px] font-mono text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 transition-colors p-1.5 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/40 cursor-pointer"
              title="Reset conveyor frame (R)"
            >
              <ArrowCounterClockwise size={13} />
              <span>Reset (R)</span>
            </button>
          )}
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50/90 dark:bg-blue-950/50 border border-blue-100 dark:border-blue-900/50 text-blue-600 dark:text-sky-400 text-xs font-medium shrink-0">
            <Sparkle size={13} weight="fill" className="text-blue-500 dark:text-sky-400" />
            <span className="hidden xs:inline">Supports JPEG, PNG, BMP</span>
            <span className="xs:hidden">JPEG, PNG</span>
          </div>
        </div>
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/bmp"
        onChange={handleFileUpload}
        className="hidden"
      />

      {/* Main Drag & Drop Zone */}
      {activeImage ? (
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="relative overflow-hidden rounded-2xl border border-blue-200 dark:border-blue-900/60 bg-blue-50/25 dark:bg-[#1A1F26] p-3.5 sm:p-4 transition-all flex items-center justify-between gap-3"
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className="relative h-14 w-20 shrink-0 overflow-hidden rounded-xl border border-blue-100 dark:border-slate-800 bg-slate-900 shadow-xs">
              <img
                src={activeImage}
                alt="Loaded produce frame"
                className="h-full w-full object-cover"
              />
              <span className="absolute bottom-1 right-1 flex items-center gap-0.5 rounded bg-emerald-600 text-white px-1 py-0.2 text-[8px] font-bold font-mono">
                <CheckCircle size={8} weight="bold" />
                READY
              </span>
            </div>

            <div className="min-w-0">
              <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-blue-600 dark:text-sky-400 bg-blue-50 dark:bg-blue-950/60 px-1.5 py-0.5 rounded">
                Active Conveyor Capture
              </span>
              <p className="text-xs sm:text-sm font-bold text-slate-800 dark:text-slate-100 truncate mt-0.5">
                {sampleName}
              </p>
              <p className="text-[11px] text-slate-400 dark:text-slate-500 font-mono">
                Drop new image here or choose preset below
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 shrink-0">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-blue-300 transition-colors cursor-pointer"
            >
              Browse
            </button>
            <button
              type="button"
              onClick={resetAll}
              className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-xl transition-colors cursor-pointer"
              title="Reset frame"
            >
              <ArrowCounterClockwise size={16} />
            </button>
          </div>
        </div>
      ) : (
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className="group relative cursor-pointer overflow-hidden rounded-2xl border-2 border-dashed border-blue-200 dark:border-blue-900/60 bg-gradient-to-r from-blue-50/40 via-white to-blue-50/20 dark:from-slate-900/40 dark:via-[#16191E] dark:to-slate-900/40 py-7 sm:py-9 px-4 sm:px-6 text-center transition-all hover:border-blue-400 dark:hover:border-sky-500 hover:bg-blue-50/60 dark:hover:bg-[#1A1F26]"
        >
          {/* Left Tilted Photo Cards Illustration (matches mockup) */}
          <div className="pointer-events-none absolute left-4 sm:left-7 top-1/2 -translate-y-1/2 hidden md:block select-none opacity-80 group-hover:scale-105 transition-transform duration-300">
            <div className="relative w-20 h-16">
              {/* Back tilted card */}
              <div className="absolute left-0 top-0 w-13 h-11 rounded-xl bg-blue-100 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 -rotate-12 shadow-sm flex items-center justify-center">
                <ImageIcon size={20} className="text-blue-400 dark:text-blue-500 opacity-60" weight="duotone" />
              </div>
              {/* Front card */}
              <div className="absolute left-5 top-2 w-13 h-11 rounded-xl bg-white dark:bg-slate-800 border border-blue-200 dark:border-blue-700 rotate-6 shadow-md flex items-center justify-center">
                <ImageIcon size={20} className="text-blue-500 dark:text-sky-400" weight="duotone" />
              </div>
            </div>
          </div>

          {/* Center Cloud & Headline */}
          <div className="mx-auto max-w-xs sm:max-w-sm">
            <div className="mx-auto mb-2 flex h-13 w-13 items-center justify-center text-[#2563EB] dark:text-sky-400 group-hover:scale-110 transition-transform duration-200">
              <CloudArrowUp size={50} weight="regular" />
            </div>
            <h3 className="text-sm sm:text-base font-bold text-slate-800 dark:text-slate-100 tracking-tight">
              Drop conveyor capture here
            </h3>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1 font-normal">
              or{' '}
              <span className="text-[#2563EB] dark:text-sky-400 font-semibold underline underline-offset-2 hover:text-blue-700">
                browse files
              </span>{' '}
              (JPEG, PNG, BMP)
            </p>
          </div>

          {/* Right Curved Arrow & Hand-drawn Note (matches mockup) */}
          <div className="pointer-events-none absolute right-4 sm:right-7 top-1/2 -translate-y-1/2 hidden md:flex flex-col items-center select-none opacity-75">
            <span className="text-[11px] italic text-slate-400 dark:text-slate-400 font-medium tracking-tight whitespace-nowrap">
              Drag & drop<br />images here
            </span>
            <svg
              width="44"
              height="32"
              viewBox="0 0 48 36"
              fill="none"
              className="text-slate-400 dark:text-slate-500 mt-0.5 -rotate-6"
            >
              <path
                d="M 42 4 C 36 18, 22 26, 8 28"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
              />
              <path
                d="M 8 28 L 16 23 M 8 28 L 13 34"
                stroke="currentColor"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </div>
      )}

      {/* Primary Action Button: Run Inspection */}
      <button
        type="button"
        onClick={onTriggerInspect}
        disabled={isInspecting}
        className="w-full flex items-center justify-center gap-2.5 rounded-2xl bg-[#2563EB] hover:bg-blue-700 active:scale-[0.99] text-white py-3.5 px-6 font-bold text-sm sm:text-base transition-all shadow-md shadow-blue-500/25 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer"
      >
        {isInspecting ? (
          <>
            <CircleNotch size={18} weight="bold" className="animate-spin" />
            <span>Scanning Optical Belt...</span>
          </>
        ) : (
          <>
            <Play size={16} weight="fill" />
            <span>Run Inspection</span>
            <span className="ml-1 px-2.5 py-0.5 rounded-md bg-white/20 text-white text-xs font-mono font-semibold">
              Space
            </span>
          </>
        )}
      </button>

      {/* Quick Presets Section */}
      <div className="pt-1 space-y-3">
        {/* Presets Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-slate-900 dark:text-white">
              Quick Presets
            </span>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-normal hidden sm:inline">
              Use sample images to try the model
            </span>
          </div>

          <button
            type="button"
            onClick={onOpenSampleModal}
            className="flex items-center gap-1 text-xs font-semibold text-[#2563EB] dark:text-sky-400 hover:text-blue-700 dark:hover:text-sky-300 transition-colors cursor-pointer"
          >
            <SquaresFour size={15} weight="bold" />
            <span>All Samples</span>
            <CaretRight size={13} weight="bold" />
          </button>
        </div>

        {/* Filter Tabs Row (matches mockup pills) */}
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5">
          {/* ALL */}
          <button
            type="button"
            onClick={() => setActiveFilter('ALL')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer shrink-0 ${
              activeFilter === 'ALL'
                ? 'bg-[#2563EB] text-white shadow-xs shadow-blue-500/20'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200/70 dark:hover:bg-slate-700'
            }`}
          >
            <SquaresFour size={14} weight="fill" />
            <span>All</span>
          </button>

          {/* REJECT */}
          <button
            type="button"
            onClick={() => setActiveFilter('REJECT')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer shrink-0 ${
              activeFilter === 'REJECT'
                ? 'bg-rose-600 text-white shadow-xs shadow-rose-500/20'
                : 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-200/80 dark:border-rose-900/60 hover:bg-rose-100/70'
            }`}
          >
            <XCircle
              size={15}
              weight="fill"
              className={activeFilter === 'REJECT' ? 'text-white' : 'text-rose-500'}
            />
            <span>REJECT</span>
          </button>

          {/* GRADE A */}
          <button
            type="button"
            onClick={() => setActiveFilter('PASS_GRADE_A')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer shrink-0 ${
              activeFilter === 'PASS_GRADE_A'
                ? 'bg-emerald-600 text-white shadow-xs shadow-emerald-500/20'
                : 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200/80 dark:border-emerald-900/60 hover:bg-emerald-100/70'
            }`}
          >
            <CheckCircle
              size={15}
              weight="fill"
              className={activeFilter === 'PASS_GRADE_A' ? 'text-white' : 'text-emerald-500'}
            />
            <span>GRADE A</span>
          </button>

          {/* GRADE B */}
          <button
            type="button"
            onClick={() => setActiveFilter('PASS_GRADE_B')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer shrink-0 ${
              activeFilter === 'PASS_GRADE_B'
                ? 'bg-amber-600 text-white shadow-xs shadow-amber-500/20'
                : 'bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 border border-amber-200/80 dark:border-amber-900/60 hover:bg-amber-100/70'
            }`}
          >
            <Warning
              size={15}
              weight="fill"
              className={activeFilter === 'PASS_GRADE_B' ? 'text-white' : 'text-amber-500'}
            />
            <span>GRADE B</span>
          </button>

          {/* NO OBJECT */}
          <button
            type="button"
            onClick={() => setActiveFilter('NO_OBJECT')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold transition-all cursor-pointer shrink-0 ${
              activeFilter === 'NO_OBJECT'
                ? 'bg-slate-700 text-white shadow-xs'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700 hover:bg-slate-200/70'
            }`}
          >
            <Circle
              size={13}
              weight="fill"
              className={activeFilter === 'NO_OBJECT' ? 'text-white' : 'text-slate-400'}
            />
            <span>NO OBJECT</span>
          </button>
        </div>

        {/* 8 Preset Thumbnail Cards (matches mockup 1:1) */}
        <div
          ref={scrollContainerRef}
          className="flex gap-2.5 overflow-x-auto pb-2 pt-1 scroll-smooth snap-x scrollbar-thin"
        >
          {filteredSamples.map((sample) => {
            const isSelected = sampleName === sample.name;
            const isReject = sample.expectedGrade === 'REJECT';
            const isGradeA = sample.expectedGrade === 'PASS_GRADE_A';
            const isGradeB = sample.expectedGrade === 'PASS_GRADE_B';
            const isNoObject = sample.expectedGrade === 'NO_OBJECT';

            return (
              <button
                key={sample.id}
                type="button"
                onClick={() => onSelectSample?.(sample)}
                className={`group relative flex-shrink-0 w-28 sm:w-32 rounded-xl overflow-hidden border text-left transition-all cursor-pointer snap-start ${
                  isSelected
                    ? 'ring-2 ring-blue-500 shadow-md shadow-blue-500/20 border-blue-400 scale-[1.02]'
                    : 'border-slate-200/90 dark:border-slate-800 bg-slate-900 hover:border-blue-300 dark:hover:border-slate-700 hover:scale-[1.02]'
                }`}
                title={sample.description}
              >
                {/* Thumbnail Image */}
                <div className="relative h-18 sm:h-20 w-full overflow-hidden bg-slate-900">
                  <img
                    src={sample.path}
                    alt={sample.name}
                    className="h-full w-full object-cover transition-transform duration-200 group-hover:scale-105"
                    loading="lazy"
                  />
                </div>

                {/* Attached Grade Banner Footer */}
                <div
                  className={`py-1.5 px-1.5 text-[10px] font-bold font-mono text-center flex items-center justify-center gap-1 border-t ${
                    isReject
                      ? 'bg-rose-50 dark:bg-rose-950/80 text-rose-700 dark:text-rose-300 border-rose-200/80 dark:border-rose-900/60'
                      : isGradeA
                      ? 'bg-emerald-50 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-900/60'
                      : isGradeB
                      ? 'bg-amber-50 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-900/60'
                      : 'bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700'
                  }`}
                >
                  {isReject && (
                    <X size={10} weight="bold" className="text-rose-600 dark:text-rose-400" />
                  )}
                  {isGradeA && (
                    <Check size={10} weight="bold" className="text-emerald-600 dark:text-emerald-400" />
                  )}
                  {isGradeB && (
                    <Warning size={10} weight="fill" className="text-amber-600 dark:text-amber-400" />
                  )}
                  {isNoObject && <Circle size={8} weight="fill" className="text-slate-500" />}
                  <span className="truncate">
                    {sample.badgeText ||
                      (isReject
                        ? 'REJECT'
                        : isGradeA
                        ? 'GRADE A'
                        : isGradeB
                        ? 'GRADE B'
                        : 'NO OBJECT')}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

