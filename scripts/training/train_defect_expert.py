"""Train and export Stage-2 Defect Specialist (YOLOv8s-seg) on zoomed fruit dataset."""
import os
import shutil
from pathlib import Path

import onnxruntime as ort
from onnxruntime.quantization import QuantType, quantize_dynamic
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parents[2]


def train_and_export_defect_expert(epochs: int = 25, batch_size: int = 16, imgsz: int = 640) -> None:
    data_yaml = (BASE_DIR / "data/fruit_defects_zoomed/data.yaml").resolve()
    base_model = (BASE_DIR / "models/weights/yolov8s-seg.pt").resolve()

    print("\n==================================================")
    print("TRAINING STAGE-2 DEFECT SPECIALIST (YOLOv8s-seg)")
    print(f"Dataset:    {data_yaml}")
    print(f"Base:       {base_model}")
    print(f"Epochs:     {epochs} | Batch: {batch_size} | Imgsz: {imgsz}")
    print("Hardware:   NVIDIA GeForce RTX 3070 (device=0)")
    print("==================================================\n")

    model = YOLO(str(base_model))

    # Train model on RTX 3070 GPU
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=0,
        amp=True,
        cos_lr=True,
        box=7.5,
        cls=1.5,
        hsv_s=0.6,
        hsv_v=0.4,
        close_mosaic=5,
        project="runs/segment",
        name="defect_expert_s_run",
        exist_ok=True,
        workers=2,
        verbose=True,
    )

    # Locate best.pt
    run_dir = Path("runs/segment/defect_expert_s_run")
    if not (run_dir / "weights" / "best.pt").exists():
        alt_path = Path("C:/Users/ZeeqRyz/Desktop/Deep Learning Project/runs/segment/runs/segment/defect_expert_s_run")
        if (alt_path / "weights" / "best.pt").exists():
            run_dir = alt_path

    best_pt = run_dir / "weights" / "best.pt"
    if not best_pt.exists():
        raise FileNotFoundError(f"Trained weights not found in {run_dir}")

    target_pt = Path("models/weights/defect_expert_s.pt")
    shutil.copy(best_pt, target_pt)
    print(f"\n[OK] Defect Specialist weights saved to: {target_pt}")

    # Copy plots to reports/defect_expert/
    reports_dir = Path("reports/defect_expert")
    reports_dir.mkdir(parents=True, exist_ok=True)
    for f in run_dir.glob("*.png"):
        shutil.copy(f, reports_dir / f.name)
    for f in run_dir.glob("*.csv"):
        shutil.copy(f, reports_dir / f.name)
    print(f"[OK] Training plots and metrics copied to: {reports_dir}")

    # 1. Export FP32 ONNX
    print("\n--- Exporting Defect Specialist to ONNX FP32 ---")
    fine_tuned = YOLO(str(target_pt))
    exported_onnx = fine_tuned.export(
        format="onnx",
        imgsz=imgsz,
        opset=12,
        simplify=True,
    )
    target_onnx = Path("models/onnx/defect_expert_s.onnx")
    shutil.copy(exported_onnx, target_onnx)
    print(f"[OK] Exported FP32 ONNX: {target_onnx} ({os.path.getsize(target_onnx)/(1024*1024):.2f} MB)")

    # 2. Dynamic INT8 Quantization
    print("\n--- Quantizing Defect Specialist to ONNX INT8 ---")
    target_int8 = Path("models/onnx/defect_expert_s_int8.onnx")
    quantize_dynamic(
        model_input=str(target_onnx),
        model_output=str(target_int8),
        weight_type=QuantType.QUInt8,
    )
    fp32_sz = os.path.getsize(target_onnx) / (1024 * 1024)
    int8_sz = os.path.getsize(target_int8) / (1024 * 1024)
    reduction = (1.0 - (int8_sz / fp32_sz)) * 100.0
    print(f"[OK] Quantized INT8 ONNX: {target_int8} ({int8_sz:.2f} MB, {reduction:.1f}% reduction)")

    # Verify sessions
    sess = ort.InferenceSession(str(target_onnx), providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    print(f"[OK] FP32 Session verified. Outputs: {[o.name for o in sess.get_outputs()]}")
    sess_q = ort.InferenceSession(str(target_int8), providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
    print(f"[OK] INT8 Session verified. Outputs: {[o.name for o in sess_q.get_outputs()]}")
    print("\n==================================================")
    print("STAGE-2 DEFECT SPECIALIST TRAINING & EXPORT COMPLETED")
    print("==================================================")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Stage-2 Defect Specialist")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch", type=int, default=16)
    args = parser.parse_args()
    train_and_export_defect_expert(epochs=args.epochs, batch_size=args.batch)
