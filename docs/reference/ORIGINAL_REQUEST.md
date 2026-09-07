# Original User Request

## Initial Request — 2026-09-03T09:39:11Z

Build an industrial Automated Optical Inspection (AOI) food defect grading system that uses YOLOv8s-seg instance segmentation and optimized ONNX/TensorRT edge runtimes to inspect produce on high-speed conveyor belts.

Working directory: c:\Users\ZeeqRyz\Desktop\Food Defect AI
Integrity mode: development

## Requirements

### R1. Model Upgrade & Export Pipeline
Implement and train YOLOv8s-seg (Small Instance Segmentation, 11.2M parameters) on multi-class defect data. Export the trained model to optimized ONNX Runtime and TensorRT formats targeting fixed 640x640 resolution with deterministic inference latency <= 15 ms on GPU and <= 35 ms on CPU.

### R2. Industrial Dataset & Negative Sample Integration
Structure a multi-class instance segmentation dataset containing polygon mask annotations across 5 industrial classes (fruit_body, rot, bruise, scab, stem_calyx). Inject 15% empty conveyor belt negative sample frames to suppress false alarms on bare rollers and shadows.

### R3. Spatial Filtering & AOI Grading Rule Engine
Implement a two-stage geometric defect quantification engine where defect masks are strictly intersected with the segmented fruit body. Calculate defect surface percentage and automatically grade items into Grade A, Grade B, or Reject (with zero-tolerance immediate rejection for active rot).

### R4. Production Serving & Operator Terminal
Deploy a high-throughput async FastAPI inference service (/api/v1/inspect) containerized with Docker, coupled with an interactive Streamlit operator dashboard featuring real-time mask overlays, defect breakdown tables, and Pass/Reject yield metrics.

## Acceptance Criteria

### Model Performance & Latency
- [ ] YOLOv8s-seg trained and exported to models/onnx/best_s.onnx and quantized INT8 variant.
- [ ] Validation defect recall >= 97% and mask mAP50 >= 90%.
- [ ] Inference latency verified at <= 35 ms on CPU and <= 15 ms on GPU via automated benchmark script.

### False Alarm Suppression & Safety
- [ ] Empty conveyor belt test frames produce exactly 0 defect detections and output NO_OBJECT.
- [ ] Defects outside fruit perimeter are geometrically filtered out.
- [ ] Active rot instances trigger immediate REJECT classification regardless of size.

### System Verification & Delivery
- [ ] Unit and integration test suite (pytest tests/) passes 100% with >= 90% coverage on grading logic.
- [ ] FastAPI /api/v1/inspect returns structured JSON matching Data.md contract within latency budget.
- [ ] Streamlit dashboard renders live segmented overlays and defect classification cards.
