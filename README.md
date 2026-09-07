<div align="center">

# 🍎 Food Defect AI

### Industrial Automated Optical Inspection (AOI) System

High-throughput, real-time computer vision platform engineered for **24/7 industrial conveyor** food quality grading and automated defect rejection.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![ONNX Runtime](https://img.shields.io/badge/runtime-ONNX-005CED.svg?logo=onnx&logoColor=white)](https://onnxruntime.ai/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/frontend-React%2019-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS v4](https://img.shields.io/badge/styles-Tailwind%20v4-38B2AC.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/tests-126%20passed-2ea44f.svg?logo=pytest&logoColor=white)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

<!-- Add your screenshots here -->
<!-- ![Dashboard Preview](docs/assets/dashboard-preview.png) -->

</div>

---

## ⚡ Key Features

- **Real-Time Instance Segmentation** — YOLOv8s-seg with ONNX Runtime for pixel-level defect detection under 20ms
- **4-Class Defect Detection** — Identifies rot, bruise, scab, and scratch with color-space anomaly fallback
- **Deterministic 3-Grade Sorting** — Rule-based grading engine: Grade A → Grade B → Reject with zero-tolerance rot policy
- **Dual Precision Inference** — FP32 (accuracy) and INT8 quantized (speed) models selectable per-request
- **Spatial Intersection Filtering** — Suppresses false positives by validating defect-to-fruit body overlap
- **Industrial React 19 Dashboard** — Live reticle canvas, conveyor telemetry, audit logs, and sorting calibration
- **Standalone Gradio Terminal** — Lightweight operator UI for single-frame inspection and diagnostics
- **Docker-Ready Deployment** — Production containerization with `docker compose up`

---

## 🏗️ System Architecture

```
Camera Feed ──► Letterbox Resize (640×640) ──► ONNX Runtime (FP32 / INT8)
                                                        │
                                                        ▼
                                               Instance Segmentation
                                               (Fruit Body + Defects)
                                                        │
                                                        ▼
                                              Spatial Intersection Filter
                                              (Suppress False Positives)
                                                        │
                                                        ▼
Reject Solenoid ◄── PASS / REJECT ◄── Grading Engine (Rule-Based Classification)
                                                        │
                                                        ▼
                                              Dashboard / Audit Log
```

---

## 📊 Model Performance

| Metric | Box Detection | Instance Segmentation |
|--------|:------------:|:--------------------:|
| **Precision** | 77.8% | 77.0% |
| **Recall** | 50.4% | 50.2% |
| **mAP@50** | 50.7% | 50.1% |
| **mAP@50-95** | 47.1% | 47.4% |

| Property | FP32 Model | INT8 Quantized |
|----------|:----------:|:--------------:|
| **Format** | ONNX | ONNX |
| **Input Size** | 640×640 | 640×640 |
| **Inference** | ~15ms | ~9ms |
| **Precision Trade-off** | Baseline | ≤1% mAP drop |

> **Training:** 30 epochs on YOLOv8s-seg with copy-paste defect augmentation, GPU thermal monitoring, and RTX 3070 thermal sentinel.

---

## 🎯 Grading Logic

The grading engine applies deterministic industrial rules in priority order:

| Priority | Condition | Grade | Action |
|:--------:|-----------|:-----:|:------:|
| 1 | No fruit body detected | `NO_OBJECT` | Skip |
| 2 | Active rot or critical defect present | `REJECT` | ❌ Eject |
| 3 | Defect ratio > 5.0% | `REJECT` | ❌ Eject |
| 4 | Defect ratio ≤ 1.0% | `GRADE A` | ✅ Pass |
| 5 | Defect ratio ≤ 5.0% | `GRADE B` | ✅ Pass |

> **Zero-Tolerance Policy:** Any detection of `rot` or `critical_defect` triggers immediate rejection regardless of surface area ratio.

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|:-------:|---------|
| **AI Runtime** | ONNX Runtime | ≥1.17.0 | FP32/INT8 inference engine |
| **Model** | YOLOv8s-seg (Ultralytics) | ≥8.2.0 | Instance segmentation backbone |
| **Backend API** | FastAPI + Uvicorn | ≥0.110.0 | High-throughput REST service |
| **Frontend** | React 19 + TypeScript | ^19.2.8 | Operator workstation dashboard |
| **Styling** | Tailwind CSS v4 | ^4.3.3 | Utility-first responsive design |
| **State** | Zustand | ^5.0.15 | Lightweight client state management |
| **Data Fetching** | TanStack React Query | ^5.102.8 | Server state & cache management |
| **Build Tool** | Vite 8 | ^8.2.2 | Frontend bundling & HMR |
| **Operator UI** | Gradio 5 | ≥5.0.0 | Standalone inspection terminal |
| **Dashboard** | Streamlit | ≥1.32.0 | Factory analytics dashboard |
| **Computer Vision** | OpenCV | ≥4.9.0 | Image preprocessing & overlays |
| **Testing** | pytest | ≥8.1.0 | 126-test 3-tier test suite |
| **Linting** | Ruff + OxLint | ≥0.4.0 | Python & TypeScript code quality |

---

## 🚀 Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend development)
- NVIDIA GPU with CUDA / DirectML (optional — CPU execution supported)

### 1. Clone & Install

```bash
# Clone the repository
git clone https://github.com/luqshzeeq3601-art/food-defect-ai.git
cd food-defect-ai

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy and edit environment config
cp .env.example .env
```

Key variables in `.env`:

```env
# Server
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8008

# Model Paths
DEFAULT_ONNX_MODEL=models/onnx/best_s.onnx
QUANTIZED_ONNX_MODEL=models/onnx/best_s_int8.onnx

# Grading Thresholds
CONFIDENCE_THRESHOLD=0.35
IOU_THRESHOLD=0.45
GRADE_A_THRESHOLD_PERCENT=1.0
GRADE_B_THRESHOLD_PERCENT=5.0
MIN_DEFECT_AREA_PIXELS=50
ENABLE_SPATIAL_INTERSECTION_FILTER=true
```

### 3. Launch the Application

#### Option A: Unified Web Station (FastAPI + React 19)
```bash
# Production mode (serves prebuilt React dist)
python scripts/run_web.py

# Development mode with Vite hot reload
python scripts/run_web.py --dev
```

#### Option B: Standalone Gradio Operator Terminal
```bash
python scripts/run_gradio.py --port 7860
```

---

## 🐳 Docker Deployment

### Standalone Container
```bash
# Build the image
docker build -f deploy/Dockerfile -t food-defect-aoi .

# Run (API on :8000, Dashboard on :8501)
docker run -d -p 8000:8000 -p 8501:8501 food-defect-aoi
```

### Docker Compose (Full Stack)
```bash
# Build and start all services
docker compose -f deploy/docker-compose.yml up --build

# Run in background
docker compose -f deploy/docker-compose.yml up -d

# Stop and clean up
docker compose -f deploy/docker-compose.yml down
```

---

## 🔌 API Reference

### Health Check

```bash
curl http://localhost:8008/api/v1/health
```

```json
{
  "status": "healthy",
  "model_loaded": true,
  "execution_provider": "CUDAExecutionProvider",
  "version": "1.0.0"
}
```

### Inspect Image

```bash
curl -X POST http://localhost:8008/api/v1/inspect \
  -F "file=@fruit_sample.jpg" \
  -G -d "precision=fp32" -d "return_overlay=true"
```

```json
{
  "inspection_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-09-07T09:00:00Z",
  "image_width": 1920,
  "image_height": 1080,
  "fruit": {
    "fruit_id": 0,
    "fruit_type": "apple",
    "confidence": 0.94,
    "pixel_area": 185000
  },
  "defects": [
    {
      "defect_id": 1,
      "defect_type": "bruise",
      "confidence": 0.87,
      "pixel_area": 1200
    }
  ],
  "defect_ratio_percent": 0.65,
  "grade": "PASS_GRADE_A",
  "reject_reason": null,
  "timing": {
    "preprocess_ms": 2.1,
    "inference_ms": 9.3,
    "postprocess_ms": 3.4,
    "grading_ms": 0.1,
    "total_ms": 14.9
  },
  "overlay_image_base64": "..."
}
```

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `precision` | `string` | `"fp32"` | Model precision: `"fp32"` or `"int8"` |
| `return_overlay` | `bool` | `true` | Include annotated image in response |

---

## 🖥️ Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server with hot reload
npm run dev

# Build production bundle
npm run build

# Lint TypeScript
npm run lint
```

---

## 🧪 Testing & Verification

### Run Full Test Suite (126 Tests)
```bash
pytest -v --tb=short
```

### Test Tiers

| Tier | Tests | Scope |
|------|:-----:|-------|
| **Unit** | Core grading logic, FP suppression, quantization parity | `tests/unit/` |
| **Integration** | FastAPI endpoints, Gradio interface contracts | `tests/integration/` |
| **E2E (4-Tier)** | Feature coverage → boundary cases → pairwise combos → production scenarios | `tests/e2e/` |

### Linting
```bash
# Python
ruff check src/ tests/

# TypeScript (from frontend/)
cd frontend && npm run lint
```

---

## 📁 Repository Structure

```
food-defect-ai/
├── README.md                  # This file
├── AGENTS.md                  # Developer guidelines & coding standards
├── pyproject.toml             # Python packaging, pytest & ruff config
├── requirements.txt           # Production dependencies
├── .env.example               # Environment variable template
│
├── src/                       # Application source code
│   ├── api/                   #   FastAPI REST service + schemas
│   ├── core/                  #   ONNX detector, grading engine, config
│   ├── ui/                    #   Gradio terminal & Streamlit dashboard
│   └── utils/                 #   Metrics, benchmarking & quantization
│
├── frontend/                  # React 19 + TypeScript + Vite workstation
│   ├── src/                   #   Components, state, API layer
│   └── dist/                  #   Production build (served by FastAPI)
│
├── models/                    # Model zoo
│   ├── architectures/         #   YOLOv8s-seg YAML specs
│   ├── onnx/                  #   Production ONNX models (FP32 & INT8)
│   └── weights/               #   PyTorch training checkpoints
│
├── data/                      # Data pipeline
│   └── samples/               #   Golden test fixtures & conveyor backgrounds
│
├── scripts/                   # MLOps tooling
│   ├── run_web.py             #   Web station launcher
│   ├── run_gradio.py          #   Gradio terminal launcher
│   ├── data/                  #   Dataset synthesis & augmentation
│   ├── training/              #   YOLO training & thermal monitoring
│   ├── evaluation/            #   Model evaluation pipelines
│   └── export/                #   ONNX export & INT8 quantization
│
├── tests/                     # 3-tier test suite (126 tests)
│   ├── unit/                  #   Domain logic & grading tests
│   ├── integration/           #   API & Gradio contract tests
│   └── e2e/                   #   4-tier industrial scenario tests
│
├── deploy/                    # Containerization
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── reports/                   # Training metrics & confusion matrices
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Architecture Design](docs/architecture/ARCHITECTURE.md) | System design & component diagrams |
| [Architecture Essentials](docs/architecture/ARCHITECTURE-ESSENTIALS.md) | Non-negotiable invariants & contracts |
| [Product Requirements (PRD)](docs/specifications/PRD.md) | Functional & non-functional requirements |
| [Data Models & API Contracts](docs/specifications/Data.md) | Schema definitions & data flow |
| [Security Guidelines](docs/specifications/Security.md) | Industrial security & hardening |
| [Test Verification Plan](docs/testing/TEST_READY.md) | QA strategy & coverage reports |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/onnx-detector`)
3. Follow [AGENTS.md](AGENTS.md) coding standards (PEP 8, type hints, Google docstrings)
4. Write tests (`pytest -v --tb=short`) — maintain ≥90% coverage on core logic
5. Lint your code (`ruff check src/ tests/`)
6. Commit using [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `test:`, `docs:`)
7. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built for industrial-grade food quality assurance**

*Engineered for 24/7 conveyor deployment with deterministic sorting decisions*

</div>
