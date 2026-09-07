# Architecture Essentials (Non-Negotiable Rules)

This document contains condensed, non-negotiable architectural rules. AI agents and contributors must adhere to these invariants at all times.

---

## 1. Inference Invariants
* **Input Resolution:** Fixed at $640 \times 640 \times 3$ with letterboxing. Never stretch or distort aspect ratio.
* **Coordinate System:** All bounding boxes and mask coordinates stored internally as normalized $[0.0, 1.0]$ floats before rendering to original frame dimensions.
* **Latency Budget:** Total pipeline latency (preprocess + inference + mask postprocess + grading) must remain under $50\text{ ms}$ on CPU and $20\text{ ms}$ on GPU.
* **Primary Runtime:** Production inference code MUST run through `ONNXDetector` via `onnxruntime`. PyTorch is reserved exclusively for training and model export.

---

## 2. Defect Grading Rules
* **Area Ratio Calculation:**
  $$\text{Defect Ratio} = \frac{\text{Total Defect Pixels}}{\text{Total Fruit Body Pixels}} \times 100$$
* **Zero-Tolerance Defect:** The class `rot` is an absolute reject regardless of defect area percentage.
* **Strict Thresholds:**
  * $\le 1.0\%$ Defect Area $\rightarrow$ `PASS_GRADE_A`
  * $> 1.0\%$ and $\le 5.0\%$ Defect Area $\rightarrow$ `PASS_GRADE_B`
  * $> 5.0\%$ Defect Area $\rightarrow$ `REJECT`
  * Missing fruit body detection $\rightarrow$ `ERROR_NO_OBJECT`

---

## 3. API Contract Invariants
* **Statelessness:** The inference service (`POST /api/v1/inspect`) must be strictly stateless. No session state or memory leaks across requests.
* **Response Format:** Must strictly follow the `InspectionResponse` Pydantic schema in [Data.md](file:///c:/Users/ZeeqRyz/Desktop/Food%20Defect%20AI/Data.md).
* **Execution Time Reporting:** All responses must return `timing_ms` broken down into `preprocess_ms`, `inference_ms`, `postprocess_ms`, and `total_ms`.

---

## 4. Code Structure Invariants
* No business logic inside API route handlers. Routes only parse inputs, call core services (`src.core.detector` and `src.core.grader`), and return responses.
* OpenCV image format standard: Convert BGR to RGB immediately upon reading. Internal pipeline operates strictly on RGB.
