# Tool Capabilities & Execution Skills (Skills.md)

This document catalogs the exact CLI tools, scripts, commands, and environment skills permitted during execution.

---

## 1. Environment & Package Management
* **Virtual Environment Creation:**
  ```powershell
  python -m venv .venv
  .venv\Scripts\Activate.ps1
  ```
* **Dependency Installation:**
  ```powershell
  pip install -r requirements.txt
  ```

---

## 2. Model Training & Export Skills
* **Train YOLOv8-seg Baseline:**
  ```powershell
  yolo segment train data=data/dataset.yaml model=yolov8n-seg.pt epochs=50 imgsz=640 batch=16
  ```
* **Export PyTorch to ONNX Format:**
  ```powershell
  yolo export model=models/weights/best.pt format=onnx imgsz=640 dynamic=False opset=12 simplify=True
  ```
* **Benchmark ONNX Latency:**
  ```powershell
  python -m src.utils.benchmark --model models/onnx/best.onnx --iterations 100 --warmup 10
  ```

---

## 3. Microservice & Dashboard Execution
* **Run FastAPI Backend (Dev Mode):**
  ```powershell
  uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
  ```
* **Run Streamlit Dashboard:**
  ```powershell
  streamlit run src/ui/dashboard.py --server.port 8501
  ```
* **Run Full Integration Test Suite:**
  ```powershell
  pytest tests/ -v
  ```

---

## 4. Container Operations
* **Build Docker Image:**
  ```powershell
  docker build -f deploy/Dockerfile -t food-defect-aoi:latest .
  ```
* **Launch Multi-Container Stack (FastAPI + Streamlit):**
  ```powershell
  docker-compose -f deploy/docker-compose.yml up -d
  ```
