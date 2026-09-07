/**
 * TypeScript definitions matching backend Pydantic schemas.
 */

export interface BoundingBox {
  x_min: number;
  y_min: number;
  x_max: number;
  y_max: number;
}

export interface PolygonPoint {
  x: number;
  y: number;
}

export type DefectType = 'rot' | 'bruise' | 'scab' | 'scratch' | string;

export interface DetectedDefect {
  defect_id: number;
  defect_type: DefectType;
  confidence: number;
  bbox: BoundingBox;
  polygon: PolygonPoint[];
  pixel_area: number;
}

export interface DetectedFruit {
  fruit_id: number;
  fruit_type: string;
  confidence: number;
  bbox: BoundingBox;
  polygon: PolygonPoint[];
  pixel_area: number;
}

export interface InspectionTiming {
  preprocess_ms: number;
  inference_ms: number;
  postprocess_ms: number;
  grading_ms: number;
  total_ms: number;
}

export type InspectionGrade =
  | 'PASS_GRADE_A'
  | 'PASS_GRADE_B'
  | 'GRADE_A'
  | 'GRADE_B'
  | 'REJECT'
  | 'NO_OBJECT'
  | string;

export function normalizeGrade(
  grade: string | undefined | null
): 'GRADE_A' | 'GRADE_B' | 'REJECT' | 'NO_OBJECT' {
  if (!grade) return 'NO_OBJECT';
  const g = grade.toUpperCase();
  if (g === 'PASS_GRADE_A' || g === 'GRADE_A' || g === 'A') return 'GRADE_A';
  if (g === 'PASS_GRADE_B' || g === 'GRADE_B' || g === 'B') return 'GRADE_B';
  if (g === 'REJECT') return 'REJECT';
  return 'NO_OBJECT';
}

export interface InspectionResponse {
  inspection_id: string;
  timestamp: string;
  image_width: number;
  image_height: number;
  fruit: DetectedFruit | null;
  defects: DetectedDefect[];
  defect_ratio_percent: number;
  grade: InspectionGrade;
  reject_reason: string | null;
  timing: InspectionTiming;
  overlay_image_base64: string | null;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  execution_provider: string;
  version: string;
}

export interface InspectRequestOptions {
  file: File | Blob;
  precision?: 'fp32' | 'int8';
  returnOverlay?: boolean;
}

export interface InspectionHistoryItem {
  id: string;
  timestamp: string;
  sampleName: string;
  grade: InspectionGrade;
  defectRatio: number;
  defectCount: number;
  latencyMs: number;
  rejectReason: string | null;
  precision: 'fp32' | 'int8';
}
