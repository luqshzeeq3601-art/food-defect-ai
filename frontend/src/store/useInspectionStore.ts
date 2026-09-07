import { create } from 'zustand';
import type { InspectionHistoryItem, InspectionResponse } from '../api/types';

interface ViewportLayers {
  showFruit: boolean;
  showDefects: boolean;
  showBBoxes: boolean;
  showLabels: boolean;
  showHeatmap: boolean;
}

interface InspectionState {
  // Input image state
  activeImage: string | null;
  activeFile: File | Blob | null;
  sampleName: string;

  // Calibration parameters
  modelPrecision: 'fp32' | 'int8';
  confidenceThreshold: number;
  gradeAThreshold: number;
  gradeBThreshold: number;

  // Viewport display controls
  layers: ViewportLayers;
  hoveredDefectId: number | null;
  zoom: number;

  // Result & status
  currentResult: InspectionResponse | null;
  history: InspectionHistoryItem[];

  // Actions
  setActiveImage: (imageUrl: string | null, file: File | Blob | null, sampleName?: string) => void;
  setModelPrecision: (precision: 'fp32' | 'int8') => void;
  setConfidenceThreshold: (val: number) => void;
  setGradeAThreshold: (val: number) => void;
  setGradeBThreshold: (val: number) => void;
  toggleLayer: (layer: keyof ViewportLayers) => void;
  setHoveredDefectId: (id: number | null) => void;
  setZoom: (zoom: number) => void;
  resetZoom: () => void;
  setCurrentResult: (result: InspectionResponse | null) => void;
  addHistoryItem: (item: InspectionHistoryItem) => void;
  deleteHistoryItem: (id: string) => void;
  clearHistory: () => void;
  resetAll: () => void;
}

const DEFAULT_DEMO_HISTORY: InspectionHistoryItem[] = [
  {
    id: 'demo-1',
    timestamp: '08:45:35',
    sampleName: 'Surface Bruise / Scab (GRADE B)',
    thumbnailUrl: '/samples/real_orange.jpg',
    route: 'Sort #2',
    grade: 'PASS_GRADE_B',
    defectRatio: 3.0,
    defectCount: 1,
    latencyMs: 50.0,
    rejectReason: null,
    precision: 'fp32',
  },
  {
    id: 'demo-2',
    timestamp: '07:59:04',
    sampleName: 'Defective Fruit (Active Rot Test)',
    thumbnailUrl: '/samples/real_banana.jpg',
    route: 'Reject #3',
    grade: 'REJECT',
    defectRatio: 15.0,
    defectCount: 2,
    latencyMs: 268.4,
    rejectReason: 'Active rot detected (zero-tolerance)',
    precision: 'fp32',
  },
  {
    id: 'demo-3',
    timestamp: '07:58:46',
    sampleName: 'Market Banana (Tropical)',
    thumbnailUrl: '/samples/real_banana.jpg',
    route: 'Reject #3',
    grade: 'REJECT',
    defectRatio: 13.2,
    defectCount: 1,
    latencyMs: 216.7,
    rejectReason: 'Defect area (13.20%) exceeds threshold (8.0%)',
    precision: 'fp32',
  },
];

export const useInspectionStore = create<InspectionState>((set) => ({
  activeImage: null,
  activeFile: null,
  sampleName: 'Conveyor Feed',

  modelPrecision: 'fp32',
  confidenceThreshold: 0.35,
  gradeAThreshold: 3.0,
  gradeBThreshold: 8.0,

  layers: {
    showFruit: true,
    showDefects: true,
    showBBoxes: true,
    showLabels: true,
    showHeatmap: false,
  },
  hoveredDefectId: null,
  zoom: 1.0,

  currentResult: null,
  history: DEFAULT_DEMO_HISTORY,

  setActiveImage: (imageUrl, file, sampleName = 'Manual Upload') =>
    set({
      activeImage: imageUrl,
      activeFile: file,
      sampleName,
      currentResult: null,
      hoveredDefectId: null,
      zoom: 1.0,
    }),

  setModelPrecision: (modelPrecision) => set({ modelPrecision }),
  setConfidenceThreshold: (confidenceThreshold) => set({ confidenceThreshold }),
  setGradeAThreshold: (gradeAThreshold) => set({ gradeAThreshold }),
  setGradeBThreshold: (gradeBThreshold) => set({ gradeBThreshold }),

  toggleLayer: (layer) =>
    set((state) => ({
      layers: {
        ...state.layers,
        [layer]: !state.layers[layer],
      },
    })),

  setHoveredDefectId: (hoveredDefectId) => set({ hoveredDefectId }),
  setZoom: (zoom) => set({ zoom: Math.max(0.5, Math.min(3.0, zoom)) }),
  resetZoom: () => set({ zoom: 1.0 }),

  setCurrentResult: (currentResult) => set({ currentResult }),

  addHistoryItem: (item) =>
    set((state) => ({
      history: [item, ...state.history].slice(0, 50),
    })),

  deleteHistoryItem: (id) =>
    set((state) => ({
      history: state.history.filter((item) => item.id !== id),
    })),

  clearHistory: () => set({ history: [] }),

  resetAll: () =>
    set({
      activeImage: null,
      activeFile: null,
      sampleName: 'Conveyor Feed',
      currentResult: null,
      hoveredDefectId: null,
      zoom: 1.0,
    }),
}));
