import React, { useState, useRef } from 'react';
import {
  Camera,
  MagnifyingGlassPlus,
  MagnifyingGlassMinus,
  ArrowsIn,
  CornersOut,
  CameraRotate,
  SquaresFour,
} from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';
import { normalizeGrade } from '../api/types';

export const OpticalViewportCard: React.FC = () => {
  const {
    activeImage,
    currentResult,
    layers,
    toggleLayer,
    hoveredDefectId,
    setHoveredDefectId,
    zoom,
    setZoom,
    resetZoom,
    sampleName,
  } = useInspectionStore();

  const [naturalWidth, setNaturalWidth] = useState<number>(640);
  const [naturalHeight, setNaturalHeight] = useState<number>(640);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [showGrid, setShowGrid] = useState<boolean>(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setNaturalWidth(img.naturalWidth || 640);
    setNaturalHeight(img.naturalHeight || 640);
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

  const fruit = currentResult?.fruit;
  const defects = currentResult?.defects || [];
  const gradeKey = normalizeGrade(currentResult?.grade);

  return (
    <div
      ref={containerRef}
      className={`rounded-2xl border border-[#E5EBF5] dark:border-[#262B33] bg-white dark:bg-[#16191E] p-5 shadow-[0_2px_12px_rgba(0,0,0,0.03)] flex flex-col justify-between transition-colors ${
        isFullscreen ? 'fixed inset-0 z-50 p-6 rounded-none bg-[#0B0F19]' : ''
      }`}
    >
      <div>
        {/* Card Header matching reference screenshot exactly */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 shadow-2xs">
              <Camera size={18} weight="bold" />
            </div>
            <h2 className="text-sm font-bold text-gray-900 dark:text-white leading-tight">
              Viewport
            </h2>
          </div>

          {/* Top-Right Controls: Zoom, Grid, Fullscreen */}
          <div className="flex items-center gap-2">
            {/* Snapshot Button (when image present) */}
            {activeImage && (
              <button
                type="button"
                onClick={handleDownloadSnapshot}
                className="flex items-center gap-1 rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-[#1D222A] px-2 py-1 text-xs font-medium text-gray-600 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors shadow-2xs cursor-pointer"
                title="Save Snapshot"
              >
                <CameraRotate size={13} className="text-blue-500 dark:text-sky-400" />
                <span className="text-[11px]">Snapshot</span>
              </button>
            )}

            {/* Zoom Controls Pill */}
            <div className="flex items-center rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-[#1D222A] px-1.5 py-1 text-xs font-mono shadow-2xs">
              <button
                type="button"
                onClick={() => setZoom(zoom - 0.25)}
                className="p-0.5 text-gray-400 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 transition-colors cursor-pointer"
                title="Zoom Out"
              >
                <MagnifyingGlassMinus size={13} />
              </button>
              <span className="mx-1.5 font-bold text-gray-700 dark:text-slate-200 text-[11px] w-9 text-center">
                {Math.round(zoom * 100)}%
              </span>
              <button
                type="button"
                onClick={() => setZoom(zoom + 0.25)}
                className="p-0.5 text-gray-400 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 transition-colors cursor-pointer"
                title="Zoom In"
              >
                <MagnifyingGlassPlus size={13} />
              </button>
              {zoom !== 1.0 && (
                <button
                  type="button"
                  onClick={resetZoom}
                  className="ml-1 p-0.5 text-gray-400 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 transition-colors cursor-pointer"
                  title="Reset 100%"
                >
                  <ArrowsIn size={12} />
                </button>
              )}
            </div>

            {/* Grid Toggle Button */}
            <button
              type="button"
              onClick={() => setShowGrid(!showGrid)}
              className={`rounded-lg border p-1.5 transition-colors shadow-2xs cursor-pointer ${
                showGrid
                  ? 'border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 font-bold'
                  : 'border-gray-200 dark:border-slate-700 bg-white dark:bg-[#1D222A] text-gray-500 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 hover:bg-gray-50 dark:hover:bg-slate-800'
              }`}
              title="Toggle Alignment Grid"
            >
              <SquaresFour size={14} />
            </button>

            {/* Fullscreen / Expand Button */}
            <button
              type="button"
              onClick={handleToggleFullscreen}
              className="rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-[#1D222A] p-1.5 text-gray-500 dark:text-slate-400 hover:text-gray-800 dark:hover:text-slate-200 hover:bg-gray-50 dark:hover:bg-slate-800 transition-colors shadow-2xs cursor-pointer"
              title="Toggle Fullscreen"
            >
              <CornersOut size={14} />
            </button>
          </div>
        </div>

        {/* Layer Toggles (Visible when inspection result is active) */}
        {currentResult && (
          <div className="flex flex-wrap items-center gap-1.5 mb-3 text-xs">
            <span className="text-[11px] font-mono text-gray-500 dark:text-slate-400 uppercase font-bold mr-1">
              Layers:
            </span>
            <button
              type="button"
              onClick={() => toggleLayer('showFruit')}
              className={`rounded-lg border px-2 py-0.5 text-[11px] font-medium transition-all cursor-pointer ${
                layers.showFruit
                  ? 'border-emerald-300 dark:border-emerald-700 bg-emerald-50 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300 font-semibold'
                  : 'border-gray-200 dark:border-slate-700 text-gray-400 dark:text-slate-400 bg-white dark:bg-[#1D222A]'
              }`}
            >
              Fruit Contour
            </button>
            <button
              type="button"
              onClick={() => toggleLayer('showDefects')}
              className={`rounded-lg border px-2 py-0.5 text-[11px] font-medium transition-all cursor-pointer ${
                layers.showDefects
                  ? 'border-rose-300 dark:border-rose-700 bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 font-semibold'
                  : 'border-gray-200 dark:border-slate-700 text-gray-400 dark:text-slate-400 bg-white dark:bg-[#1D222A]'
              }`}
            >
              Defect Masks
            </button>
            <button
              type="button"
              onClick={() => toggleLayer('showBBoxes')}
              className={`rounded-lg border px-2 py-0.5 text-[11px] font-medium transition-all cursor-pointer ${
                layers.showBBoxes
                  ? 'border-blue-300 dark:border-blue-700 bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 font-semibold'
                  : 'border-gray-200 dark:border-slate-700 text-gray-400 dark:text-slate-400 bg-white dark:bg-[#1D222A]'
              }`}
            >
              Bounding Boxes
            </button>
            <button
              type="button"
              onClick={() => toggleLayer('showLabels')}
              className={`rounded-lg border px-2 py-0.5 text-[11px] font-medium transition-all cursor-pointer ${
                layers.showLabels
                  ? 'border-amber-300 dark:border-amber-700 bg-amber-50 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300 font-semibold'
                  : 'border-gray-200 dark:border-slate-700 text-gray-400 dark:text-slate-400 bg-white dark:bg-[#1D222A]'
              }`}
            >
              Defect Tags
            </button>
          </div>
        )}

        {/* Viewport Canvas (Dark #111827 matching reference image) */}
        <div className="relative flex min-h-[380px] md:min-h-[420px] items-center justify-center overflow-hidden rounded-2xl bg-[#111827] border border-gray-800 p-4">
          {/* Subtle Industrial Grid Overlay */}
          {showGrid && (
            <div
              className="pointer-events-none absolute inset-0 opacity-15"
              style={{
                backgroundImage:
                  'linear-gradient(to right, #38BDF8 1px, transparent 1px), linear-gradient(to bottom, #38BDF8 1px, transparent 1px)',
                backgroundSize: '32px 32px',
              }}
            />
          )}

          {activeImage ? (
            <div
              className="relative transition-transform duration-150 ease-out flex items-center justify-center"
              style={{ transform: `scale(${zoom})`, transformOrigin: 'center center' }}
            >
              {/* Optical Base Image */}
              <img
                src={activeImage}
                alt="Optical Inspection Frame"
                onLoad={handleImageLoad}
                className="max-h-[420px] w-auto rounded-lg border border-gray-700 object-contain shadow-2xl"
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

                  {/* Fruit BBox Tag with Confidence % and Grade */}
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

                  {/* Defects */}
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
                          {isHovered && (
                            <>
                              <line
                                x1="0"
                                y1={by + bh / 2}
                                x2={naturalWidth}
                                y2={by + bh / 2}
                                stroke="#38BDF8"
                                strokeWidth="1.5"
                                strokeDasharray="4 2"
                              />
                              <line
                                x1={bx + bw / 2}
                                y1="0"
                                x2={bx + bw / 2}
                                y2={naturalHeight}
                                stroke="#38BDF8"
                                strokeWidth="1.5"
                                strokeDasharray="4 2"
                              />
                            </>
                          )}

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
                              strokeDasharray={isHovered ? 'none' : '4 2'}
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
            /* Standby State matching reference screenshot exactly */
            <div className="flex flex-col items-center justify-center p-8 text-center select-none">
              <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-[#1E293B] text-gray-400 shadow-inner">
                <Camera size={28} weight="regular" />
              </div>
              <h3 className="text-sm font-bold text-white tracking-wide">
                Optical Viewport Standby
              </h3>
              <p className="mt-1 max-w-sm text-xs text-gray-400 font-medium leading-relaxed">
                Upload a frame from the left to initiate optical defect segmentation.
              </p>
            </div>
          )}

          {/* Bottom-left Pill Badge */}
          <div className="absolute bottom-3 left-3 flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-black/60 border border-gray-700/60 text-[11px] font-mono text-gray-300 backdrop-blur-xs shadow-md">
            {activeImage ? (
              <>
                <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Active Frame ({naturalWidth}x{naturalHeight})</span>
              </>
            ) : (
              <>
                <span className="text-gray-500 font-bold">⊘</span>
                <span className="text-gray-400">No frame</span>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
