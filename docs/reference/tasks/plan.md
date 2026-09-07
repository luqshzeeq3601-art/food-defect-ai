# Implementation Plan: Modern Machine Vision Web Station (Food Defect AI)

## Overview
Create a high-performance, modern web application for the Food Defect AI Automated Optical Inspection (AOI) pipeline. The frontend will be built using **Vite + React 19 + TypeScript + Tailwind CSS v4**, connecting directly to the high-speed FastAPI ONNX backend (`/api/v1/inspect`). Designed with strict anti-slop principles from `/frontend-design` and `/design-taste-frontend`, the interface provides an industrial, high-density operator workspace tailored for factory quality control engineers.

---

## Design Read & Aesthetic Vision
* **Design Read**: Industrial Machine Vision Operator Console & Factory Quality Station for automated conveyor sorting lines, with a high-contrast, clean Swiss-industrial dark language, prioritizing dense technical telemetry, zero decorative fluff, authentic SVG reticles, and direct physical workflow.
* **Dial Settings**: `DESIGN_VARIANCE: 5` (Structured, utilitarian symmetry) | `MOTION_INTENSITY: 4` (Restrained, functional transitions) | `VISUAL_DENSITY: 8` (High data density, low wasted space).
* **Anti-Slop Directives**:
  * No generic AI-purple gradients, floating mesh orbs, or bloated double-bezel cards.
  * No fake "Step 1-2-3" onboarding banners or gimmicky analog needle gauges.
  * No emojis in UI labels; use crisp `@phosphor-icons/react` glyphs.
  * Single signature element: **Interactive Optical Reticle Canvas** with toggleable vector overlays (fruit contour, defect masks, defect IDs, and heatmaps) with pan/zoom and table row-hover synchronization.

---

## Tech Stack & Architecture Decisions
1. **Frontend Core**: `Vite 6` + `React 19` + `TypeScript`:
   - Blazing fast hot module replacement (<50ms) and minimal bundle size.
   - Generates static bundle (`frontend/dist`) that can also be served directly by FastAPI or deployed standalone.
2. **Styling & Design Tokens**: `Tailwind CSS v4`:
   - Bespoke industrial color system: deep carbon base (`#0B0F19`), surface cards (`#111827`), hairline borders (`#1F2937`), and high-contrast status accents (Emerald `#10B981`, Amber `#F59E0B`, Crimson `#EF4444`, Reticle Cyan `#06B6D4`).
3. **State & Network**:
   - `TanStack Query (React Query v5)`: Robust mutation and query caching for `/api/v1/inspect` and `/api/v1/health`.
   - `Zustand`: Minimalist store for viewport layer toggles, calibration sliders, and inspection history buffer.
4. **Interactive Visualization**:
   - Custom SVG/Canvas vector engine rendering normalized bounding boxes and polygon contours directly over the original image, enabling row-hover cross-hair highlighting without server roundtrips.

---

## Task List & Phases

### Phase 1: Project Scaffold & Foundation
- [ ] **Task 1**: Initialize Vite + React 19 + TypeScript project in `frontend/` with package configuration.
- [ ] **Task 2**: Configure Tailwind CSS v4, custom industrial color tokens, font stack (`Plus Jakarta Sans` + `JetBrains Mono`), and install `@phosphor-icons/react`.

### Checkpoint: Foundation
- [ ] Vite dev server boots cleanly; Tailwind styles and fonts load without errors.

### Phase 2: API Client & State Layer
- [ ] **Task 3**: Create strongly typed API client matching backend Pydantic schemas (`InspectionResponse`, `DetectedDefect`, `InspectionTiming`) with TanStack Query hooks.
- [ ] **Task 4**: Implement Zustand store for inspection state, viewport layer toggles, calibration thresholds, and session audit history.

### Checkpoint: API & State
- [ ] Health check hook connects to `http://localhost:8000/api/v1/health` and displays backend status.

### Phase 3: Core Interactive Workstation
- [ ] **Task 5**: Build compact industrial Header with station ID, live backend connection indicator, and telemetry latency summary.
- [ ] **Task 6**: Build Conveyor Ingestion & Calibration sidebar (preset test image selector, file upload, webcam trigger, confidence & grade sliders).
- [ ] **Task 7**: Build Interactive Optical Reticle Canvas with pan/zoom and toggleable vector layers (fruit polygon, defect masks, bounding boxes, labels).
- [ ] **Task 8**: Build Industrial Decision Deck (High-contrast Pass A / Pass B / Reject / No Object status badge, tolerance delta, and 4-stage timing waterfall).
- [ ] **Task 9**: Build Defect Quantification Breakdown table with row-hover crosshair linking and session audit log with CSV export.

### Checkpoint: Core Features
- [ ] End-to-end flow works: selecting a preset or uploading an image sends request to FastAPI, renders vector overlay, updates decision banner, and populates defect table.

### Phase 4: Polish, Optimization & Verification
- [ ] **Task 10**: Add responsive layout optimizations, keyboard shortcuts (Space to inspect, R to reset), production build check, and update launcher scripts.

---

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| CORS issues between Vite dev server (port 5173) and FastAPI (port 8000) | Medium | FastAPI already configures `CORSMiddleware` with `allow_origins=["*"]`; Vite proxy can also be configured. |
| Large image payload upload latency over HTTP | Low | Validate image size on client before upload; limit to 10MB as enforced by backend. |
| Canvas polygon alignment offset on scaled images | Medium | Calculate scale factors dynamically based on natural image aspect ratio vs viewport container. |

---

## Open Questions
- None. Backend contracts and test samples are fully available.

---

## Project Timeline & Gantt Visuals

| Document View | Chart Image Preview |
|---|---|
| **Executive Summary Gantt** | `docs/assets/gantt/executive-summary-gantt.png` |
| **Detailed WBS Gantt** | `docs/assets/gantt/wbs-gantt.png` |
| **Component Dependency Timeline** | `docs/assets/gantt/component-dependency-timeline.png` |

