import React, { useState, useRef } from 'react';
import {
  Camera,
  Minus,
  Plus,
  CornersOut,
  Leaf,
  Warning,
  BoundingBox,
  Tag,
  CaretLeft,
  CaretRight,
} from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';
import { PRESET_SAMPLES, type PresetSample } from '../constants/presets';
import { normalizeGrade } from '../api/types';

interface OpticalViewportCardProps {
  onSelectSample?: (sample: PresetSample) => void;
}

export const OpticalViewportCard: React.FC<OpticalViewportCardProps> = ({ onSelectSample }) => {
  const {
    activeImage,
    currentResult,
    layers,
    toggleLayer,
    hoveredDefectId,
    setHoveredDefectId,
    zoom,
    setZoom,
    sampleName,
    setActiveImage,
  } = useInspectionStore();

  const [naturalWidth, setNaturalWidth] = useState<number>(432);
  const [naturalHeight, setNaturalHeight] = useState<number>(432);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Find index in preset samples for navigation
  const currentSampleIdx = PRESET_SAMPLES.findIndex(
    (s) => s.name === sampleName || s.path === activeImage
  );

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setNaturalWidth(img.naturalWidth || 432);
    setNaturalHeight(img.naturalHeight || 432);
  };

  const handleToggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen?.().then(() => setIsFullscreen(true)).catch(() => {});
    } else {
      document.exitFullscreen?.().then(() => setIsFullscreen(false)).catch(() => {});
    }
  };

  const handleDownloadSnapshot = () => {
    if (!activeImage) return;
    const link = document.createElement('a');
    link.href = activeImage;
    link.download = `AOI_${sampleName.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleNavigate = async (direction: 'prev' | 'next') => {
    const total = PRESET_SAMPLES.length;
    let nextIdx = 0;
    if (currentSampleIdx >= 0) {
      nextIdx = direction === 'next' ? (currentSampleIdx + 1) % total : (currentSampleIdx - 1 + total) % total;
    } else {
      nextIdx = direction === 'next' ? 0 : total - 1;
    }

    const nextSample = PRESET_SAMPLES[nextIdx];
    if (onSelectSample) {
      onSelectSample(nextSample);
    } else {
      try {
        const resp = await fetch(nextSample.path);
        const blob = await resp.blob();
        const objectUrl = URL.createObjectURL(blob);
        setActiveImage(objectUrl, blob, nextSample.name);
      } catch (err) {
        console.error('Failed to cycle frame:', err);
      }
    }
  };

  const fruit = currentResult?.fruit;
  const defects = currentResult?.defects || [];
  const gradeKey = normalizeGrade(currentResult?.grade);

  return (
    <div
      ref={containerRef}
      className={`rounded-3xl border border-slate-200/80 dark:border-[#262B33] bg-white dark:bg-[#16191E] p-5 sm:p-6 shadow-sm space-y-4 transition-colors ${
        isFullscreen ? 'fixed inset-0 z-50 p-6 rounded-none bg-[#0B0F19]' : ''
      }`}
    >
      {/* Top Header */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-2xl bg-blue-50 dark:bg-blue-950/50 text-[#2563EB] dark:text-sky-400 shadow-2xs">
            <Camera size={22} weight="fill" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white leading-tight tracking-tight">
              Viewport
            </h2>
            <p className="text-xs text-slate-400 dark:text-slate-500 font-medium">
              Visualize detection layers and results
            </p>
          </div>
        </div>

        {/* Top-Right Controls */}
        <div className="flex items-center gap-2">
          {/* Snapshot Button */}
          <button
            type="button"
            onClick={handleDownloadSnapshot}
            className="flex items-center gap-1.5 rounded-xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#1A1F26] px-3.5 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-2xs cursor-pointer"
            title="Save Snapshot"
          >
            <Camera size={15} weight="bold" className="text-[#2563EB] dark:text-sky-400" />
            <span className="hidden xs:inline">Snapshot</span>
          </button>

          {/* Vertical Separator */}
          <div className="h-4 w-px bg-slate-200 dark:bg-slate-800 hidden sm:block" />

          {/* Zoom Controls Pill */}
          <div className="flex items-center rounded-xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#1A1F26] px-2 py-1 text-xs font-mono text-slate-700 dark:text-slate-300 shadow-2xs">
            <button
              type="button"
              onClick={() => setZoom(Math.max(0.5, zoom - 0.25))}
              className="p-1 text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors cursor-pointer"
              title="Zoom Out"
            >
              <Minus size={12} weight="bold" />
            </button>
            <span className="min-w-[40px] text-center font-bold text-[11px] text-slate-800 dark:text-slate-200">
              {Math.round(zoom * 100)}%
            </span>
            <button
              type="button"
              onClick={() => setZoom(Math.min(3.0, zoom + 0.25))}
              className="p-1 text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-colors cursor-pointer"
              title="Zoom In"
            >
              <Plus size={12} weight="bold" />
            </button>
          </div>

          {/* Vertical Separator */}
          <div className="h-4 w-px bg-slate-200 dark:bg-slate-800 hidden sm:block" />

          {/* Fullscreen Button */}
          <button
            type="button"
            onClick={handleToggleFullscreen}
            className="rounded-xl border border-slate-200/80 dark:border-slate-800 bg-white dark:bg-[#1A1F26] p-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors shadow-2xs cursor-pointer"
            title="Toggle Fullscreen"
          >
            <CornersOut size={15} weight="bold" />
          </button>
        </div>
      </div>

      {/* Layers Toggle Bar */}
      <div className="flex flex-wrap items-center gap-2 pt-0.5">
        <span className="text-xs font-bold text-slate-700 dark:text-slate-300 mr-1">
          Layers
        </span>

        {/* Fruit Contour */}
        <button
          type="button"
          onClick={() => toggleLayer('showFruit')}
          className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer border ${
            layers.showFruit
              ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200/90 dark:border-emerald-900/60 text-emerald-700 dark:text-emerald-300'
              : 'bg-white dark:bg-[#1A1F26] border-slate-200/80 dark:border-slate-800 text-slate-400 dark:text-slate-500 opacity-60'
          }`}
        >
          <Leaf size={14} weight="duotone" className={layers.showFruit ? 'text-emerald-600' : 'text-slate-400'} />
          <span>Fruit Contour</span>
        </button>

        {/* Defect Masks */}
        <button
          type="button"
          onClick={() => toggleLayer('showDefects')}
          className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer border ${
            layers.showDefects
              ? 'bg-rose-50 dark:bg-rose-950/40 border-rose-200/90 dark:border-rose-900/60 text-rose-700 dark:text-rose-300'
              : 'bg-white dark:bg-[#1A1F26] border-slate-200/80 dark:border-slate-800 text-slate-400 dark:text-slate-500 opacity-60'
          }`}
        >
          <Warning size={14} weight="duotone" className={layers.showDefects ? 'text-rose-600' : 'text-slate-400'} />
          <span>Defect Masks</span>
        </button>

        {/* Bounding Boxes */}
        <button
          type="button"
          onClick={() => toggleLayer('showBBoxes')}
          className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer border ${
            layers.showBBoxes
              ? 'bg-blue-50 dark:bg-blue-950/40 border-blue-200/90 dark:border-blue-900/60 text-[#2563EB] dark:text-sky-300'
              : 'bg-white dark:bg-[#1A1F26] border-slate-200/80 dark:border-slate-800 text-slate-400 dark:text-slate-500 opacity-60'
          }`}
        >
          <BoundingBox size={14} weight="duotone" className={layers.showBBoxes ? 'text-[#2563EB]' : 'text-slate-400'} />
          <span>Bounding Boxes</span>
        </button>

        {/* Defect Tags */}
        <button
          type="button"
          onClick={() => toggleLayer('showLabels')}
          className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer border ${
            layers.showLabels
              ? 'bg-amber-50 dark:bg-amber-950/40 border-amber-200/90 dark:border-amber-900/60 text-amber-800 dark:text-amber-300'
              : 'bg-white dark:bg-[#1A1F26] border-slate-200/80 dark:border-slate-800 text-slate-400 dark:text-slate-500 opacity-60'
          }`}
        >
          <Tag size={14} weight="duotone" className={layers.showLabels ? 'text-amber-600' : 'text-slate-400'} />
          <span>Defect Tags</span>
        </button>
      </div>

      {/* Viewport Dark Canvas Chamber */}
      <div className="relative flex min-h-[380px] md:min-h-[440px] items-center justify-center overflow-hidden rounded-3xl bg-[#131722] border border-slate-800 p-4 select-none">
        {/* Carousel Left Navigation Button */}
        <button
          type="button"
          onClick={() => handleNavigate('prev')}
          className="absolute left-4 top-1/2 -translate-y-1/2 z-20 flex h-10 w-10 items-center justify-center rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-xs transition-all shadow-md cursor-pointer hover:scale-105"
          title="Previous Sample"
        >
          <CaretLeft size={18} weight="bold" />
        </button>

        {/* Carousel Right Navigation Button */}
        <button
          type="button"
          onClick={() => handleNavigate('next')}
          className="absolute right-4 top-1/2 -translate-y-1/2 z-20 flex h-10 w-10 items-center justify-center rounded-full bg-white/10 hover:bg-white/20 text-white backdrop-blur-xs transition-all shadow-md cursor-pointer hover:scale-105"
          title="Next Sample"
        >
          <CaretRight size={18} weight="bold" />
        </button>

        {activeImage ? (
          <div
            className="relative transition-transform duration-150 ease-out flex items-center justify-center"
            style={{ transform: `scale(${zoom})`, transformOrigin: 'center center' }}
          >
            {/* Optical Frame */}
            <img
              src={activeImage}
              alt="Optical Inspection Frame"
              onLoad={handleImageLoad}
              className="max-h-[400px] w-auto rounded-lg object-contain shadow-2xl"
            />

            {/* Vector Reticle & Defect Overlay SVG */}
            {currentResult && (
              <svg
                viewBox={`0 0 ${naturalWidth} ${naturalHeight}`}
                className="pointer-events-auto absolute inset-0 h-full w-full"
              >
                {/* Fruit Contour */}
                {layers.showFruit && fruit?.polygon && fruit.polygon.length > 0 && (
                  <polygon
                    points={fruit.polygon
                      .map((p) => `${p.x * naturalWidth},${p.y * naturalHeight}`)
                      .join(' ')}
                    fill="rgba(16, 185, 129, 0.15)"
                    stroke="#10B981"
                    strokeWidth="2.5"
                    strokeDasharray="4 2"
                  />
                )}

                {/* Fruit BBox */}
                {layers.showBBoxes && fruit?.bbox && (
                  <rect
                    x={fruit.bbox.x_min * naturalWidth}
                    y={fruit.bbox.y_min * naturalHeight}
                    width={(fruit.bbox.x_max - fruit.bbox.x_min) * naturalWidth}
                    height={(fruit.bbox.y_max - fruit.bbox.y_min) * naturalHeight}
                    fill="none"
                    stroke="#10B981"
                    strokeWidth="1.5"
                    strokeOpacity="0.7"
                  />
                )}

                {/* Fruit BBox Tag */}
                {layers.showLabels && fruit?.bbox && (() => {
                  const fruitConf = Math.round(fruit.confidence * 100);
                  const fruitGrade = gradeKey === 'GRADE_A' ? 'GRADE A' : gradeKey === 'GRADE_B' ? 'GRADE B' : 'REJECT';
                  const fruitText = `PRODUCE · ${fruitConf}% · ${fruitGrade}`;
                  const tagW = fruitText.length * 6.8 + 14;
                  const fx = fruit.bbox.x_min * naturalWidth;
                  const fy = Math.max(18, fruit.bbox.y_min * naturalHeight - 6);

                  return (
                    <g transform={`translate(${fx}, ${fy})`}>
                      <rect
                        x="-2"
                        y="-16"
                        width={tagW}
                        height="18"
                        rx="3"
                        fill="#0F172A"
                        stroke="#10B981"
                        strokeWidth="1.5"
                      />
                      <text
                        x="4"
                        y="-3"
                        fill="#10B981"
                        fontSize="10"
                        fontFamily="var(--font-mono)"
                        fontWeight="700"
                      >
                        {fruitText}
                      </text>
                    </g>
                  );
                })()}

                {/* Defect Bounding Boxes & Tags */}
                {layers.showDefects &&
                  defects.map((defect) => {
                    const isHovered = hoveredDefectId === defect.defect_id;
                    const isRot = defect.defect_type.toLowerCase().includes('rot') || defect.defect_type.toLowerCase().includes('bad');
                    const strokeColor = isRot ? '#EF4444' : '#F59E0B';
                    const fillColor = isRot
                      ? 'rgba(239, 68, 68, 0.45)'
                      : 'rgba(245, 158, 11, 0.45)';

                    const polyPoints = defect.polygon
                      ?.map((p) => `${p.x * naturalWidth},${p.y * naturalHeight}`)
                      .join(' ');

                    const bx = defect.bbox.x_min * naturalWidth;
                    const by = defect.bbox.y_min * naturalHeight;
                    const bw = (defect.bbox.x_max - defect.bbox.x_min) * naturalWidth;
                    const bh = (defect.bbox.y_max - defect.bbox.y_min) * naturalHeight;

                    return (
                      <g
                        key={defect.defect_id}
                        onMouseEnter={() => setHoveredDefectId(defect.defect_id)}
                        onMouseLeave={() => setHoveredDefectId(null)}
                        className="cursor-pointer"
                      >
                        {polyPoints && (
                          <polygon
                            points={polyPoints}
                            fill={fillColor}
                            stroke={isHovered ? '#38BDF8' : strokeColor}
                            strokeWidth={isHovered ? '3.5' : '2'}
                          />
                        )}

                        {layers.showBBoxes && (
                          <rect
                            x={bx}
                            y={by}
                            width={bw}
                            height={bh}
                            fill="none"
                            stroke={isHovered ? '#38BDF8' : strokeColor}
                            strokeWidth={isHovered ? '2' : '1.5'}
                            strokeDasharray="4 2"
                          />
                        )}

                        {layers.showLabels && (() => {
                          const confPercent = Math.round(defect.confidence * 100);
                          const cleanType = defect.defect_type.replace(/_/g, ' ').toUpperCase();
                          const defectGrade = isRot
                            ? 'REJECT'
                            : (gradeKey === 'GRADE_A' ? 'GRADE A' : gradeKey === 'GRADE_B' ? 'GRADE B' : 'REJECT');
                          const labelText = `#${defect.defect_id} ${cleanType} · ${confPercent}% · ${defectGrade}`;
                          const tagW = Math.max(bw > 80 ? bw + 6 : 92, labelText.length * 6.8 + 14);

                          return (
                            <g transform={`translate(${bx}, ${Math.max(18, by - 6)})`}>
                              <rect
                                x="-2"
                                y="-16"
                                width={tagW}
                                height="18"
                                rx="3"
                                fill="#0F172A"
                                stroke={isHovered ? '#38BDF8' : strokeColor}
                                strokeWidth="1.5"
                              />
                              <text
                                x="4"
                                y="-3"
                                fill={isHovered ? '#38BDF8' : strokeColor}
                                fontSize="10"
                                fontFamily="var(--font-mono)"
                                fontWeight="700"
                              >
                                {labelText}
                              </text>
                            </g>
                          );
                        })()}
                      </g>
                    );
                  })}
              </svg>
            )}
          </div>
        ) : (
          /* Standby State */
          <div className="flex flex-col items-center justify-center p-8 text-center select-none">
            <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#1E2536] text-slate-400 shadow-inner">
              <Camera size={28} weight="regular" />
            </div>
            <h3 className="text-sm font-bold text-white tracking-wide">
              Optical Viewport Standby
            </h3>
            <p className="mt-1 max-w-sm text-xs text-slate-400 font-medium leading-relaxed">
              Upload a frame or select a quick preset to initiate optical defect segmentation.
            </p>
          </div>
        )}

        {/* Bottom Left Frame Info Pill */}
        <div className="absolute bottom-4 left-4 z-20 flex items-center gap-2 rounded-full bg-[#1C2230]/90 border border-slate-700/60 px-3.5 py-1 text-[11px] font-mono text-slate-300 backdrop-blur-xs shadow-md">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          <span>
            Frame {currentSampleIdx >= 0 ? currentSampleIdx + 1 : 1} / {PRESET_SAMPLES.length}
          </span>
          <span className="text-slate-600">|</span>
          <span>{naturalWidth} × {naturalHeight} px</span>
        </div>

        {/* Bottom Right Active Frame Pill */}
        <div className="absolute bottom-4 right-4 z-20 flex items-center gap-2 rounded-full bg-[#1C2230]/90 border border-slate-700/60 px-3.5 py-1 text-[11px] font-mono text-slate-300 backdrop-blur-xs shadow-md">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Active Frame</span>
        </div>
      </div>
    </div>
  );
};
