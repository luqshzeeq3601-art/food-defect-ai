import React, { useState, useEffect, useCallback } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from './components/Header';
import { ConveyorIngestionCard } from './components/ConveyorIngestionCard';
import { SortingCalibrationCard } from './components/SortingCalibrationCard';
import { OpticalViewportCard } from './components/OpticalViewportCard';
import { InspectionHUD } from './components/InspectionHUD';
import { AuditLogCard } from './components/AuditLogCard';
import { SamplePickerModal } from './components/SamplePickerModal';
import { SettingsModal } from './components/SettingsModal';
import { HelpModal } from './components/HelpModal';
import { useInspectionStore } from './store/useInspectionStore';
import { useInspectMutation } from './api/hooks';
import type { PresetSample } from './constants/presets';
import { normalizeGrade } from './api/types';
import { WarningCircle } from '@phosphor-icons/react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
    },
  },
});

const MainStation: React.FC = () => {
  const [isSampleModalOpen, setIsSampleModalOpen] = useState<boolean>(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState<boolean>(false);
  const [isHelpModalOpen, setIsHelpModalOpen] = useState<boolean>(false);

  const {
    activeImage,
    activeFile,
    sampleName,
    modelPrecision,
    currentResult,
    setActiveImage,
    setCurrentResult,
    addHistoryItem,
    resetAll,
  } = useInspectionStore();

  const inspectMutation = useInspectMutation();

  // Core execution routine for running an inspection on a Blob or File
  const runInspectionOnBlob = useCallback(
    (fileToInspect: File | Blob, name: string) => {
      inspectMutation.mutate(
        {
          file: fileToInspect,
          precision: modelPrecision,
          returnOverlay: true,
        },
        {
          onSuccess: (data) => {
            setCurrentResult(data);

            const now = new Date();
            const timeStr = `${String(now.getUTCHours()).padStart(2, '0')}:${String(
              now.getUTCMinutes()
            ).padStart(2, '0')}:${String(now.getUTCSeconds()).padStart(2, '0')}`;

            const normGrade = normalizeGrade(data.grade);
            let routeStr = 'Export Line #1';
            if (normGrade === 'GRADE_B') routeStr = 'Sort #2';
            else if (normGrade === 'REJECT') routeStr = 'Reject #3';
            else if (normGrade === 'NO_OBJECT') routeStr = 'Standby';

            addHistoryItem({
              id: data.inspection_id || String(Date.now()),
              timestamp: timeStr,
              sampleName: name,
              thumbnailUrl: activeImage || undefined,
              route: routeStr,
              grade: data.grade,
              defectRatio: data.defect_ratio_percent,
              defectCount: data.defects.length,
              latencyMs: data.timing.total_ms,
              rejectReason: data.reject_reason,
              precision: modelPrecision,
            });
          },
        }
      );
    },
    [modelPrecision, inspectMutation, setCurrentResult, addHistoryItem, activeImage]
  );

  // Handle selecting a sample from the modal: loads image and inspects immediately
  const handleSelectSample = async (sample: PresetSample) => {
    try {
      const resp = await fetch(sample.path);
      const blob = await resp.blob();
      const objectUrl = URL.createObjectURL(blob);
      setActiveImage(objectUrl, blob, sample.name);
      runInspectionOnBlob(blob, sample.name);
    } catch (err) {
      console.error('Failed to load sample:', err);
    }
  };

  // Trigger inspection logic manually (or from hotkey)
  const handleInspect = useCallback(async () => {
    if (!activeImage) {
      setIsSampleModalOpen(true);
      return;
    }

    let fileToInspect: File | Blob | null = activeFile;

    if (!fileToInspect && activeImage) {
      try {
        const resp = await fetch(activeImage);
        fileToInspect = await resp.blob();
      } catch (err) {
        console.error('Failed to get blob:', err);
        return;
      }
    }

    if (fileToInspect) {
      runInspectionOnBlob(fileToInspect, sampleName);
    }
  }, [activeImage, activeFile, sampleName, runInspectionOnBlob]);

  // Keyboard shortcuts (Ctrl + Enter & Space = Inspect, R = Reset, Esc = Modals)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (['INPUT', 'SELECT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }

      if ((e.ctrlKey && e.key === 'Enter') || e.code === 'Space') {
        e.preventDefault();
        handleInspect();
      } else if (e.key === 'r' || e.key === 'R') {
        resetAll();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleInspect, resetAll]);

  // Auto-inspect when an image file is uploaded from drag-and-drop
  useEffect(() => {
    if (activeFile && !currentResult && !inspectMutation.isPending) {
      runInspectionOnBlob(activeFile, sampleName);
    }
  }, [activeFile]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="min-h-screen flex flex-col bg-[#F4F7FC] dark:bg-[#0D0F12] text-[#1E293B] dark:text-[#F3F4F6] transition-colors">
      {/* Top Header matching reference image exactly */}
      <Header />

      {/* Main Two-Column Layout matching reference image */}
      <main className="flex-1 p-5 md:p-6 w-full mx-auto space-y-4">
        {/* Error Notification */}
        {inspectMutation.isError && (
          <div className="flex items-center gap-2.5 rounded-xl border border-rose-200 dark:border-rose-900/60 bg-rose-50 dark:bg-rose-950/40 p-3.5 text-xs text-rose-800 dark:text-rose-300 shadow-xs">
            <WarningCircle size={18} className="shrink-0 text-rose-500" weight="bold" />
            <span>
              <strong>Inspection Error:</strong> {inspectMutation.error?.message || 'Inference failed.'}
            </span>
          </div>
        )}

        {/* 2-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* Left Column (~30%): Conveyor Ingestion + Sorting Calibration */}
          <div className="lg:col-span-4 space-y-5">
            <ConveyorIngestionCard
              onOpenSampleModal={() => setIsSampleModalOpen(true)}
              onSelectSample={handleSelectSample}
              onTriggerInspect={handleInspect}
              isInspecting={inspectMutation.isPending}
            />

            <SortingCalibrationCard />
          </div>

          {/* Right Column (~70%): Optical Viewport + Audit Log (+ Diagnostic Deck when active) */}
          <div className="lg:col-span-8 space-y-5">
            {/* Top Right: Optical Viewport Card */}
            <OpticalViewportCard onSelectSample={handleSelectSample} />

            {/* Unified Industrial Inspection HUD */}
            <div className="animate-in fade-in duration-200">
              <InspectionHUD result={currentResult} />
            </div>

            {/* Bottom Right: Session Inspection Audit Log Card */}
            <AuditLogCard />
          </div>
        </div>
      </main>

      {/* Footer matching reference screenshot */}
      <footer className="border-t border-[#E5EBF5] dark:border-[#262B33] bg-white dark:bg-[#16191E] px-6 py-2.5 flex flex-wrap items-center justify-between text-[11px] text-gray-500 dark:text-[#94A3B8] font-medium transition-colors">
        <div className="flex items-center gap-2">
          <span>Inspec-Belt AI v0.2.0</span>
          <span>|</span>
          <span>YOLOv8s-seg ONNX</span>
          <span>|</span>
          <span>FastAPI Real-Time Pipeline</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setIsSettingsModalOpen(true)}
            className="hover:text-blue-600 dark:hover:text-sky-400 transition-colors cursor-pointer"
          >
            Settings
          </button>
          <span>•</span>
          <button
            type="button"
            onClick={() => setIsHelpModalOpen(true)}
            className="hover:text-blue-600 dark:hover:text-sky-400 transition-colors cursor-pointer"
          >
            Help & Hotkeys
          </button>
          <span>•</span>
          <span className="text-gray-500 dark:text-slate-400">Built for smarter quality inspection.</span>
        </div>
      </footer>

      {/* Visual Sample Library Modal */}
      <SamplePickerModal
        isOpen={isSampleModalOpen}
        onClose={() => setIsSampleModalOpen(false)}
        onSelectSample={handleSelectSample}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
      />

      {/* Help Modal */}
      <HelpModal
        isOpen={isHelpModalOpen}
        onClose={() => setIsHelpModalOpen(false)}
      />
    </div>
  );
};

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MainStation />
    </QueryClientProvider>
  );
}
