import React, { useState, useRef } from 'react';
import { Crosshair } from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';
import { ViewportToolbar } from './ViewportToolbar';

export const OpticalCanvas: React.FC = () => {
  const {
    activeImage,
    currentResult,
    layers,
    hoveredDefectId,
    setHoveredDefectId,
    zoom,
  } = useInspectionStore();

  const [naturalWidth, setNaturalWidth] = useState<number>(640);
  const [naturalHeight, setNaturalHeight] = useState<number>(640);
  const imgRef = useRef<HTMLImageElement>(null);

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setNaturalWidth(img.naturalWidth || 640);
    setNaturalHeight(img.naturalHeight || 640);
  };

  const fruit = currentResult?.fruit;
  const defects = currentResult?.defects || [];

  return (
    <div className="flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xs">
      {/* Top Viewport Layer Controls & Meta */}
      <ViewportToolbar
        imageWidth={currentResult?.image_width || naturalWidth}
        imageHeight={currentResult?.image_height || naturalHeight}
      />

      {/* Main Viewport Container */}
      <div className="relative flex min-h-[360px] items-center justify-center overflow-auto bg-[#F8FAFC] p-4">
        {activeImage ? (
          <div
            className="relative transition-transform duration-150 ease-out"
            style={{ transform: `scale(${zoom})`, transformOrigin: 'center center' }}
          >
            {/* Base Optical Image */}
            <img
              ref={imgRef}
              src={activeImage}
              alt="Optical Inspection Frame"
              onLoad={handleImageLoad}
              className="max-h-[460px] w-auto rounded-lg border border-gray-200 object-contain shadow-md"
            />

            {/* Vector Reticle & Defect Overlay SVG */}
            {currentResult && (
              <svg
                viewBox={`0 0 ${naturalWidth} ${naturalHeight}`}
                className="pointer-events-auto absolute inset-0 h-full w-full"
              >
                {/* 1. Fruit Body Contour */}
                {layers.showFruit && fruit?.polygon && fruit.polygon.length > 0 && (
                  <polygon
                    points={fruit.polygon
                      .map((p) => `${p.x * naturalWidth},${p.y * naturalHeight}`)
                      .join(' ')}
                    fill="rgba(16, 185, 129, 0.1)"
                    stroke="#10B981"
                    strokeWidth="2.5"
                    strokeDasharray="4 2"
                  />
                )}

                {/* 2. Fruit Bounding Box */}
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

                {/* 3. Defects (Polygons, Masks, & Reticles) */}
                {layers.showDefects &&
                  defects.map((defect) => {
                    const isHovered = hoveredDefectId === defect.defect_id;
                    const isRot = defect.defect_type.toLowerCase().includes('rot');
                    const strokeColor = isRot ? '#EF4444' : '#F59E0B';
                    const fillColor = isRot
                      ? 'rgba(239, 68, 68, 0.5)'
                      : 'rgba(245, 158, 11, 0.5)';

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
                        className="cursor-pointer transition-opacity"
                      >
                        {/* Crosshair guidelines on hover */}
                        {isHovered && (
                          <>
                            <line
                              x1="0"
                              y1={by + bh / 2}
                              x2={naturalWidth}
                              y2={by + bh / 2}
                              stroke="#0284C7"
                              strokeWidth="1.5"
                              strokeDasharray="4 2"
                            />
                            <line
                              x1={bx + bw / 2}
                              y1="0"
                              x2={bx + bw / 2}
                              y2={naturalHeight}
                              stroke="#0284C7"
                              strokeWidth="1.5"
                              strokeDasharray="4 2"
                            />
                          </>
                        )}

                        {/* Defect Polygon Mask */}
                        {polyPoints && (
                          <polygon
                            points={polyPoints}
                            fill={fillColor}
                            stroke={isHovered ? '#0284C7' : strokeColor}
                            strokeWidth={isHovered ? '3.5' : '2'}
                            className="transition-all"
                          />
                        )}

                        {/* Defect Bounding Box */}
                        {layers.showBBoxes && (
                          <rect
                            x={bx}
                            y={by}
                            width={bw}
                            height={bh}
                            fill="none"
                            stroke={isHovered ? '#0284C7' : strokeColor}
                            strokeWidth={isHovered ? '2' : '1.5'}
                            strokeDasharray={isHovered ? 'none' : '4 2'}
                          />
                        )}

                        {/* Defect Label Tag */}
                        {layers.showLabels && (
                          <g transform={`translate(${bx}, ${Math.max(18, by - 6)})`}>
                            <rect
                              x="-2"
                              y="-14"
                              width={bw > 80 ? bw + 4 : 84}
                              height="16"
                              rx="3"
                              fill="#FFFFFF"
                              stroke={isHovered ? '#0284C7' : strokeColor}
                              strokeWidth="1.5"
                              className="shadow-xs"
                            />
                            <text
                              x="3"
                              y="-3"
                              fill={strokeColor}
                              fontSize="10"
                              fontFamily="JetBrains Mono"
                              fontWeight="700"
                            >
                              #{defect.defect_id} {defect.defect_type.toUpperCase()}
                            </text>
                          </g>
                        )}
                      </g>
                    );
                  })}
              </svg>
            )}
          </div>
        ) : (
          /* Standby State */
          <div className="flex flex-col items-center justify-center p-8 text-center">
            <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-500 shadow-xs">
              <Crosshair size={24} weight="bold" />
            </div>
            <h3 className="text-xs font-bold text-gray-700">
              Optical Viewport Standby
            </h3>
            <p className="mt-0.5 max-w-xs text-[11px] text-gray-400">
              Select a sample above to view interactive segmentation masks.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
