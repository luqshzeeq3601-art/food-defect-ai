# Food Defect AI - Modern Web Station Task List

## Phase 1: Foundation & Scaffold

### Task 1: Initialize Frontend Scaffold
**Description:** Scaffold a new modern React 19 application using Vite and TypeScript in `frontend/`.
**Acceptance criteria:**
- [x] `frontend/package.json` created with Vite, React 19, TypeScript, and scripts.
- [x] `frontend/index.html` configured with clean industrial title and font links.
- [x] Project builds with `npm run build` without TypeScript errors.
**Verification:**
- [x] Run `cd frontend && npm install && npm run build`
**Dependencies:** None
**Files likely touched:**
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
**Estimated scope:** Medium (3-5 files)

---

### Task 2: Configure Styling, Fonts & Icons
**Description:** Set up Tailwind CSS v4, custom machine vision color tokens, typography (`Plus Jakarta Sans` and `JetBrains Mono`), and install `@phosphor-icons/react`.
**Acceptance criteria:**
- [x] Tailwind configured with `--bg-base: #0B0F19`, `--surface-card: #111827`, and status colors.
- [x] Font imports for `Plus Jakarta Sans` (UI) and `JetBrains Mono` (telemetry) active.
- [x] `@phosphor-icons/react` installed and verified.
**Verification:**
- [x] Check styles render in `frontend/src/App.tsx` with high-contrast theme.
**Dependencies:** Task 1
**Files likely touched:**
- `frontend/src/index.css`
- `frontend/tailwind.config.js` or CSS theme tokens
**Estimated scope:** Small (1-2 files)

---

## Checkpoint 1: Foundation
- [x] Dev server runs on `http://localhost:5173`
- [x] Fonts and Tailwind CSS styles load cleanly
- [x] Review foundation before proceeding to API layer

---

## Phase 2: API Client & State Management

### Task 3: Implement TypeScript API Client & TanStack Query
**Description:** Create strongly typed data contracts matching FastAPI Pydantic schemas and TanStack Query hooks for `/api/v1/health` and `/api/v1/inspect`.
**Acceptance criteria:**
- [x] TypeScript interfaces for `InspectionResponse`, `DetectedFruit`, `DetectedDefect`, `InspectionTiming`.
- [x] `useHealthQuery` hook polling `/api/v1/health`.
- [x] `useInspectMutation` hook sending multipart form data (`file`, `precision`, `return_overlay`).
**Verification:**
- [x] Unit test or mockup fetch verifying typed responses from backend.
**Dependencies:** Task 2
**Files likely touched:**
- `frontend/src/api/types.ts`
- `frontend/src/api/client.ts`
- `frontend/src/api/hooks.ts`
**Estimated scope:** Small (3 files)

---

### Task 4: Implement Zustand Inspection Store
**Description:** Create lightweight Zustand store to manage active image, selected preset, calibration thresholds, viewport layer toggles, and session audit history.
**Acceptance criteria:**
- [x] Store tracks `activeImage`, `selectedPreset`, `confidenceThreshold`, `gradeAThreshold`, `gradeBThreshold`.
- [x] Layer toggles: `showFruitPolygon`, `showDefects`, `showBBoxes`, `showHeatmap`, `hoveredDefectId`.
- [x] Session history keeps latest 50 inspection records.
**Verification:**
- [x] Zustand store state updates correctly on test actions.
**Dependencies:** Task 3
**Files likely touched:**
- `frontend/src/store/useInspectionStore.ts`
**Estimated scope:** Small (1 file)

---

## Checkpoint 2: API & State
- [x] Backend health indicator reflects FastAPI running status
- [x] State mutations update smoothly
- [x] Review state layer before building UI components

---

## Phase 3: Core Interactive Workstation

### Task 5: Industrial Header & Telemetry Bar
**Description:** Build compact top navigation bar with station identifier (`ViTrox Inspec-Belt Station #01`), live backend connection pulse, active model indicator, and latency budget readout.
**Acceptance criteria:**
- [x] Status indicator turns green when backend is online and red/amber when disconnected.
- [x] Displays active ONNX model precision and runtime environment.
- [x] Zero bloated banners or marketing fluff.
**Verification:**
- [x] Visual verification against design read and anti-slop guidelines.
**Dependencies:** Task 4
**Files likely touched:**
- `frontend/src/components/Header.tsx`
**Estimated scope:** Small (1 file)

---

### Task 6: Conveyor Ingestion & Calibration Sidebar
**Description:** Build left sidebar for optical frame ingestion (preset library dropdown, camera drag & drop / webcam trigger) and sorting calibration sliders.
**Acceptance criteria:**
- [x] Quick-select factory presets (Defective Fruit, Healthy Apple, Rotten Apple, Empty Conveyor).
- [x] Drag-and-drop / file picker for custom camera frames with image preview.
- [x] Sliders for Confidence (0.1 - 1.0), Grade A limit (0 - 3%), Grade B limit (1 - 10%).
- [x] High-contrast "Run Inspection" action button and "Reset" button.
**Verification:**
- [x] Changing presets loads image into store and triggers inspection.
**Dependencies:** Task 5
**Files likely touched:**
- `frontend/src/components/ConveyorControls.tsx`
- `frontend/src/components/CalibrationPanel.tsx`
**Estimated scope:** Medium (2-3 files)

---

### Task 7: Interactive Optical Reticle Canvas Viewport
**Description:** Build interactive HTML5 Canvas / SVG vector viewport overlaying normalized bounding boxes, fruit contour, and defect polygons over the optical frame with zoom, pan, and hover highlighting.
**Acceptance criteria:**
- [x] Dynamic aspect ratio scaling matching optical image dimensions.
- [x] Smooth vector rendering of fruit boundary (green) and defects (red for rot, amber for cosmetic).
- [x] Hovering a defect highlights its bounding box and label with crosshair reticle.
- [x] Layer toggle pills (Fruit, Defects, Boxes, Labels).
**Verification:**
- [x] Visual verification with defective sample image showing pixel-accurate defect polygons.
**Dependencies:** Task 6
**Files likely touched:**
- `frontend/src/components/OpticalCanvas.tsx`
- `frontend/src/components/ViewportToolbar.tsx`
**Estimated scope:** Medium (2-3 files)

---

### Task 8: Industrial Decision Deck & Latency Waterfall
**Description:** Build prominent quality verdict card (`PASS (GRADE A)`, `PASS (GRADE B)`, `REJECTED`, `NO OBJECT`) with factory routing directive, defect ratio tolerance delta, and 4-stage timing waterfall bar.
**Acceptance criteria:**
- [x] High-contrast color-coded verdict banner with routing action (e.g. `ROUTE: PACKAGING CONVEYOR 1`).
- [x] Defect ratio tolerance gauge showing exact numerical delta vs limits.
- [x] Latency breakdown showing preprocess, inference, postprocess, and grading ms.
**Verification:**
- [x] Verify Grade A, Grade B, Reject, and Empty Conveyor states render correct verdict cards.
**Dependencies:** Task 7
**Files likely touched:**
- `frontend/src/components/DecisionDeck.tsx`
- `frontend/src/components/TimingWaterfall.tsx`
**Estimated scope:** Small (2 files)

---

### Task 9: Defect Quantification Table & Session Audit Log
**Description:** Build interactive data table listing quantified defect instances with pixel area, classification, and coordinates, plus session history with CSV export.
**Acceptance criteria:**
- [x] Interactive defect table: hovering row sets `hoveredDefectId` in store, highlighting the canvas polygon.
- [x] Audit log tracks timestamp, model, grade, defect ratio, and latency for up to 50 runs.
- [x] CSV export button downloads session inspection history.
**Verification:**
- [x] Hovering row highlights defect on canvas; clicking export downloads valid CSV.
**Dependencies:** Task 8
**Files likely touched:**
- `frontend/src/components/DefectTable.tsx`
- `frontend/src/components/AuditLog.tsx`
**Estimated scope:** Medium (2 files)

---

## Checkpoint 3: End-to-End System
- [x] Complete inspection cycle works from preset/upload to canvas rendering and table population
- [x] Zero unhandled errors or console warnings
- [x] Operator experience is fast, responsive, and easy to understand

---

## Phase 4: Polish, Optimization & Deployment

### Task 10: Production Build & Runner Integration
**Description:** Optimize bundle, verify production build (`npm run build`), and add convenient launcher command.
**Acceptance criteria:**
- [x] `npm run build` generates optimized static bundle in `frontend/dist`.
- [x] Standalone launcher script or npm script to run web frontend alongside FastAPI.
**Verification:**
- [x] Run production preview and test all features.
**Dependencies:** Task 9
**Files likely touched:**
- `package.json` / `scripts/run_web.py`
**Estimated scope:** Small (1-2 files)
