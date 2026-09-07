# Food Defect AI: Industrial Automated Optical Inspection (AOI) System

High-throughput, real-time Computer Vision inspection platform engineered for 24/7 industrial conveyor food quality grading and automated defect rejection.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![ONNX Runtime](https://img.shields.io/badge/runtime-ONNX-005CED.svg)](https://onnxruntime.ai/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/frontend-React%2019-61DAFB.svg)](https://react.dev/)
[![Tailwind CSS v4](https://img.shields.io/badge/styles-Tailwind%20v4-38B2AC.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/tests-126%20passed-success.svg)]()

---

## 1. System Overview

Food Defect AI processes high-speed camera streams over industrial conveyor belts to classify produce, detect defects (rot, bruise, scab, scratch) at pixel-level segmentation, calculate defect surface ratios, and issue deterministic pass/reject sorting decisions in under $20\text{ ms}$.

```
Camera Feed ──► Letterbox (640x640) ──► ONNX Runtime (FP32/INT8)
                                                │
                                                ▼
Reject Solenoid ◄── PASS/REJECT ◄── Grader Engine (Rule Calculation)
```

---

## 2. Repository Layout

```
Food Defect AI/
├── README.md                  # Project overview & operator quickstart
├── AGENTS.md                  # Developer guidelines & coding standards
├── pyproject.toml             # Python packaging, pytest & ruff configuration
├── requirements.txt           # Production dependencies
│
├── docs/                      # Centralized documentation
│   ├── architecture/          # System design & non-negotiable invariants
│   │   ├── ARCHITECTURE.md
│   │   └── ARCHITECTURE-ESSENTIALS.md
│   ├── specifications/        # Product, data schemas & security specs
│   │   ├── PRD.md
│   │   ├── Data.md
│   │   └── Security.md
│   ├── testing/               # QA test strategy & verification reports
│   │   └── TEST_READY.md
│   └── reference/             # Historical context & tasks
│       ├── Skills.md
│       ├── ORIGINAL_REQUEST.md
│       └── tasks/
│
├── src/                       # Application source code
│   ├── api/                   # High-throughput FastAPI REST service
│   ├── core/                  # ONNX inference runtime & AOI grading logic
│   ├── ui/                    # Operator terminal (Gradio) & factory dashboard (Streamlit)
│   └── utils/                 # Metrics, benchmarking & quantization tools
│
├── frontend/                  # React 19 + TypeScript + Vite operator workstation
│   ├── dist/                  # Production static assets served by FastAPI
│   └── src/                   # High-density reticle canvas & telemetry UI
│
├── models/                    # Model zoo & inference graphs
│   ├── architectures/         # YOLOv8s-seg neural network specifications
│   ├── onnx/                  # Production ONNX models (FP32 & INT8)
│   └── weights/               # PyTorch training checkpoints
│
├── data/                      # Data pipeline assets
│   ├── samples/               # Golden test samples & conveyor background fixtures
│   ├── raw/                   # Ingested camera frames
│   ├── processed/             # Cleaned production records
│   └── datasets/              # Training datasets & benchmarks
│
├── scripts/                   # MLOps & operational tooling
│   ├── run_web.py             # Unified web station launcher (FastAPI + Vite)
│   ├── run_gradio.py          # Operator terminal launcher (Gradio)
│   ├── data/                  # Dataset synthesis, augmentation & validation
│   ├── training/              # YOLO model training & thermal monitoring
│   ├── evaluation/            # Precision/recall & test set evaluation
│   └── export/                # ONNX export & INT8 quantization
│
├── tests/                     # 3-tier comprehensive test suite
│   ├── conftest.py            # Global fixtures & path resolution
│   ├── unit/                  # Fast domain & logic unit tests
│   ├── integration/           # API and Gradio interface tests
│   └── e2e/                   # 4-tier industrial scenario E2E tests
│
├── deploy/                    # Containerization & orchestration
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── reports/                   # Training metrics, telemetry & confusion matrices
```

---

## 3. Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend development)
- NVIDIA GPU with CUDA / DirectML (optional; CPU execution supported)

### Installation
```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install backend dependencies
pip install -r requirements.txt
```

### Launching Stations

#### Option A: Unified Modern Web Station (FastAPI + React 19)
```bash
# Run production station (FastAPI serves prebuilt React dist)
python scripts/run_web.py

# Or launch development mode with Vite hot reload
python scripts/run_web.py --dev
```

#### Option B: Standalone Gradio Operator Terminal
```bash
python scripts/run_gradio.py --port 7860
```

---

## 4. Testing & Verification

Run the complete 3-tier test suite:
```bash
pytest -v --tb=short
```

Run linter checks:
```bash
ruff check src/ tests/
```

---

## 5. Documentation Directory

- [Architecture Design](docs/architecture/ARCHITECTURE.md)
- [Architecture Essentials & Invariants](docs/architecture/ARCHITECTURE-ESSENTIALS.md)
- [Product Requirements Document (PRD)](docs/specifications/PRD.md)
- [Data Models & API Contracts](docs/specifications/Data.md)
- [Industrial Security Guidelines](docs/specifications/Security.md)
- [Testing Verification Plan](docs/testing/TEST_READY.md)
