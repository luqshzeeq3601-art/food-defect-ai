import React from 'react';
import {
  MagnifyingGlassPlus,
  MagnifyingGlassMinus,
  ArrowsIn,
  Camera,
} from '@phosphor-icons/react';
import { useInspectionStore } from '../store/useInspectionStore';

interface ViewportToolbarProps {
  imageWidth?: number;
  imageHeight?: number;
  onSnapshot?: () => void;
}

export const ViewportToolbar: React.FC<ViewportToolbarProps> = ({
  imageWidth,
  imageHeight,
  onSnapshot,
}) => {
  const { layers, toggleLayer, zoom, setZoom, resetZoom, activeImage, sampleName } =
    useInspectionStore();

  const handleDownloadImage = () => {
    if (onSnapshot) {
      onSnapshot();
      return;
    }
    if (!activeImage) return;

    const link = document.createElement('a');
    link.href = activeImage;
    link.download = `AOI_${sampleName.replace(/\s+/g, '_')}_${new Date().toISOString().slice(0, 10)}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 bg-white px-4 py-2 text-xs">
      {/* Layer Toggles */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-mono uppercase tracking-wider text-gray-400">
          Layers:
        </span>
        <button
          type="button"
          onClick={() => toggleLayer('showFruit')}
          className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-xs font-medium transition-all cursor-pointer ${
            layers.showFruit
              ? 'border-emerald-300 bg-emerald-50 text-emerald-700 shadow-2xs font-semibold'
              : 'border-gray-200 bg-white text-gray-400 hover:text-gray-700'
          }`}
        >
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
          Fruit Contour
        </button>

        <button
          type="button"
          onClick={() => toggleLayer('showDefects')}
          className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-xs font-medium transition-all cursor-pointer ${
            layers.showDefects
              ? 'border-rose-300 bg-rose-50 text-rose-700 shadow-2xs font-semibold'
              : 'border-gray-200 bg-white text-gray-400 hover:text-gray-700'
          }`}
        >
          <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
          Defect Masks
        </button>

        <button
          type="button"
          onClick={() => toggleLayer('showBBoxes')}
          className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-xs font-medium transition-all cursor-pointer ${
            layers.showBBoxes
              ? 'border-blue-300 bg-blue-50 text-blue-700 shadow-2xs font-semibold'
              : 'border-gray-200 bg-white text-gray-400 hover:text-gray-700'
          }`}
        >
          Bounding Boxes
        </button>

        <button
          type="button"
          onClick={() => toggleLayer('showLabels')}
          className={`flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-xs font-medium transition-all cursor-pointer ${
            layers.showLabels
              ? 'border-amber-300 bg-amber-50 text-amber-800 shadow-2xs font-semibold'
              : 'border-gray-200 bg-white text-gray-400 hover:text-gray-700'
          }`}
        >
          Defect Tags
        </button>
      </div>

      {/* Viewport Zoom & Actions */}
      <div className="flex items-center gap-2.5">
        {imageWidth && imageHeight && (
          <span className="font-mono text-[11px] text-gray-400">
            {imageWidth} × {imageHeight} px
          </span>
        )}

        {/* Snapshot / Frame Export */}
        {activeImage && (
          <button
            type="button"
            onClick={handleDownloadImage}
            className="flex items-center gap-1 rounded-lg border border-gray-200 bg-gray-50/80 px-2 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-900 transition-colors shadow-2xs cursor-pointer"
            title="Download Frame Snapshot"
          >
            <Camera size={13} className="text-blue-500" />
            <span className="text-[11px]">Snapshot</span>
          </button>
        )}

        {/* Zoom Controls */}
        <div className="flex items-center gap-1 rounded-lg border border-gray-200 bg-gray-50/80 p-0.5">
          <button
            type="button"
            onClick={() => setZoom(zoom - 0.25)}
            className="rounded p-1 text-gray-500 hover:bg-white hover:text-gray-800 transition-colors shadow-2xs cursor-pointer"
            title="Zoom Out"
          >
            <MagnifyingGlassMinus size={13} />
          </button>
          <span className="w-9 text-center font-mono text-[11px] font-semibold text-gray-700">
            {Math.round(zoom * 100)}%
          </span>
          <button
            type="button"
            onClick={() => setZoom(zoom + 0.25)}
            className="rounded p-1 text-gray-500 hover:bg-white hover:text-gray-800 transition-colors shadow-2xs cursor-pointer"
            title="Zoom In"
          >
            <MagnifyingGlassPlus size={13} />
          </button>
          {zoom !== 1.0 && (
            <button
              type="button"
              onClick={resetZoom}
              className="rounded p-1 text-gray-500 hover:bg-white hover:text-gray-800 transition-colors shadow-2xs cursor-pointer"
              title="Reset Zoom (100%)"
            >
              <ArrowsIn size={13} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
