# Product Requirements Document (PRD)

## 1. Executive Summary & Vision
* **Project Name:** Automated Food / Agricultural Defect Inspection & Grading System (Food-Defect-AOI)
* **Target Alignment:** Industrial Automated Optical Inspection (AOI) pipelines (e.g., ViTrox sorting and defect detection architectures).
* **Core Value:** Replaces subjective, fatigue-prone manual sorting and brittle classical OpenCV thresholding with an optimized deep learning instance segmentation pipeline (YOLOv8-seg + ONNX Runtime) to achieve real-time defect grading at conveyor-belt speeds.

---

## 2. Problem Statement
1. **Classical Vision Limitations:** Standard thresholding/edge detection fails when illumination fluctuates, fruit shapes vary, or defects blend into healthy skin.
2. **Defect Quantification Gap:** Standard bounding-box object detection only detects presence, not the physical surface area percentage required for industrial grade classification.
3. **Speed vs. Accuracy Tradeoff:** High-accuracy segmentation models often exhibit high latency without specialized optimization (e.g., ONNX, TensorRT).

---

## 3. User Personas
* **AOI Machine Operator:** Needs a high-visibility real-time dashboard displaying Pass/Reject counts, visual defect contours, and sorting alerts on the line.
* **QA / Quality Engineer:** Needs configurable defect tolerance thresholds, audit logs, and statistical defect breakdown (e.g., % rot vs % bruise).
* **Systems / Machine Vision Engineer:** Needs low-latency microservices (FastAPI), clear ONNX inference pipelines, and containerized deployment (Docker).

---

## 4. Key Functional Requirements

### FR-1: Image Ingestion
* Ingest high-resolution images via HTTP REST API (`/api/v1/inspect`) or local batch directory.
* Support common industrial image formats: PNG, JPEG, BMP (up to 10MB per frame).

### FR-2: AI Instance Segmentation
* Detect fruit boundaries and defect boundaries simultaneously using **YOLOv8-seg**.
* Supported defect classes: `rot`, `bruise`, `scab`, `scratch`.
* Extract exact polygon coordinates and binary masks for both fruit body and defects.

### FR-3: Defect Area Quantification & Grading Logic
* Compute Defect Surface Area Ratio:
  $$\text{Defect Ratio (\%)} = \left( \frac{\sum \text{Defect Mask Pixels}}{\text{Fruit Mask Pixels}} \right) \times 100$$
* Apply configurable rule-based grading:
  * **Grade A (Premium Pass):** Defect Ratio $< 1.0\%$ and zero rot.
  * **Grade B (Commercial Pass):** Defect Ratio between $1.0\%$ and $5.0\%$ with non-critical flaws (minor bruise/scratch).
  * **Reject:** Defect Ratio $> 5.0\%$ OR presence of active rot.

### FR-4: High-Performance ONNX Inference
* Provide PyTorch-to-ONNX export pipeline.
* Execute inference using ONNX Runtime with multi-thread CPU/GPU execution providers.
* Target inference latency: $\le 30\text{ ms}$ at $640\times640$ resolution.

### FR-5: Operator Dashboard (Streamlit)
* Display real-time inspection view with overlaid segmentation masks and bounding boxes.
* Show inspection metrics card: Grade badge, Defect %, Inference Latency (ms), and Confidence Score.
* Allow operators to dynamically adjust defect threshold slider for testing calibration.

### FR-6: Audit & Logging
* Return structured JSON response with defect breakdown, polygon points, and execution timing.
* Persist inspection history for yield analysis and traceability.

---

## 5. Non-Functional Requirements

| Metric | Requirement |
| :--- | :--- |
| **Inference Latency** | $\le 30\text{ ms}$ on GPU, $\le 75\text{ ms}$ on modern multi-core CPU |
| **Throughput** | Capable of processing $\ge 30$ FPS simulated conveyor stream |
| **Model Size** | ONNX model file $\le 50\text{ MB}$ (YOLOv8n-seg or YOLOv8s-seg) |
| **Reliability** | Graceful fallback on unreadable/corrupt images with structured HTTP 422 errors |
| **Portability** | Single-command deployment via Docker & Docker Compose |

---

## 6. Success Metrics & KPIs
* **False Acceptance Rate (FAR):** $< 2\%$ for severe defects (rot).
* **Inference Speedup:** $\ge 2.5\times$ speed improvement moving from raw PyTorch to ONNX Runtime.
* **API Availability:** $99.9\%$ uptime during simulated conveyor test runs.
