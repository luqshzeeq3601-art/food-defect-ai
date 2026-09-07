import type { HealthResponse, InspectionResponse, InspectRequestOptions } from './types';

const API_BASE = ''; // Uses Vite proxy to http://127.0.0.1:8000

/**
 * Fetch backend service health and model status.
 */
export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/v1/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status: ${response.status}`);
  }
  return response.json();
}

/**
 * Send optical frame image to FastAPI inspection endpoint.
 */
export async function inspectFoodItem({
  file,
  precision = 'fp32',
  returnOverlay = true,
}: InspectRequestOptions): Promise<InspectionResponse> {
  const formData = new FormData();
  formData.append('file', file, file instanceof File ? file.name : 'optical_frame.jpg');

  const params = new URLSearchParams({
    precision,
    return_overlay: returnOverlay ? 'true' : 'false',
  });

  const response = await fetch(`${API_BASE}/api/v1/inspect?${params.toString()}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let errorDetail = `Inspection failed with status: ${response.status}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorDetail = errJson.detail;
      }
    } catch {
      // ignore json parse error
    }
    throw new Error(errorDetail);
  }

  return response.json();
}
