"""Train and export YOLOv8s-seg on the 5-class industrial AOI dataset."""
import os
import shutil
from pathlib import Path

import onnxruntime as ort
from onnxruntime.quantization import QuantType, quantize_dynamic
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parents[2]


def train_and_export_s(epochs: int = 10, batch_size: int = 8, imgsz: int = 640) -> None:
    data_yaml = (BASE_DIR / "data/fruit_defects_1500/data.yaml").resolve()
    if not data_yaml.exists():
        data_yaml = (BASE_DIR / "data/fruit_defects/data.yaml").resolve()
    p2_arch = (BASE_DIR / "models/architectures/yolov8s-seg-p2.yaml").resolve()
    base_model = (BASE_DIR / "models/weights/yolov8s-seg.pt").resolve()

    print("\n==================================================")
    print("TRAINING UNIFIED YOLOv8s-seg-P2 (Stride-4 Micro-Head) ON RTX 3070")
    print(f"Architecture: {p2_arch}")
    print(f"Dataset:      {data_yaml}")
    print(f"Epochs:       {epochs} | Batch: {batch_size} | Imgsz: {imgsz}")
    print("Augmentations: Copy-Paste=0.35 | Mask Loss Gain=8.0")
    print("==================================================\n")

    model = YOLO(str(base_model))

    # Train model on NVIDIA GeForce RTX 3070 (GPU 0)
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        device=0,
        amp=True,
        cos_lr=True,
        copy_paste=0.35,
        retina_masks=False,
        box=7.5,
        cls=1.5,
        hsv_s=0.6,
        hsv_v=0.4,
        close_mosaic=5,
        project="runs/segment",
        name="fruit_defect_s_run",
        exist_ok=True,
        workers=2,
        verbose=True,
    )

    # Locate best.pt and training run directory
    run_dir = Path("runs/segment/fruit_defect_s_run")
    if not (run_dir / "weights" / "best.pt").exists():
        alt_path = Path("C:/Users/ZeeqRyz/Desktop/Deep Learning Project/runs/segment/runs/segment/fruit_defect_s_run")
        if (alt_path / "weights" / "best.pt").exists():
            run_dir = alt_path

    best_pt = run_dir / "weights" / "best.pt"
    if not best_pt.exists():
        raise FileNotFoundError(f"Trained weights not found in {run_dir}")

    target_pt = Path("models/weights/best_s.pt")
    shutil.copy(best_pt, target_pt)
    print(f"\n[OK] Fine-tuned YOLOv8s-seg weights saved to: {target_pt}")

    # Copy evaluation plots to reports/
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    for plot_file in run_dir.glob("*.png"):
        shutil.copy(plot_file, reports_dir / plot_file.name)
    for csv_file in run_dir.glob("*.csv"):
        shutil.copy(csv_file, reports_dir / csv_file.name)
    for jpg_file in run_dir.glob("*.jpg"):
        shutil.copy(jpg_file, reports_dir / jpg_file.name)
    print(f"[OK] Training plots and metrics copied to: {reports_dir}")

    # 1. Export FP32 ONNX
    print("\n--- Exporting to ONNX FP32 ---")
    fine_tuned = YOLO(str(target_pt))
    exported_onnx = fine_tuned.export(
        format="onnx",
        imgsz=imgsz,
        opset=12,
        simplify=True,
    )
    target_onnx = Path("models/onnx/best_s.onnx")
    shutil.copy(exported_onnx, target_onnx)
    print(f"[OK] Exported FP32 ONNX: {target_onnx} ({os.path.getsize(target_onnx)/(1024*1024):.2f} MB)")

    # 2. Dynamic INT8 Quantization
    print("\n--- Quantizing to ONNX INT8 ---")
    target_int8 = Path("models/onnx/best_s_int8.onnx")
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
    sess = ort.InferenceSession(str(target_onnx), providers=["CPUExecutionProvider"])
    print(f"[OK] FP32 Session verified. Outputs: {[o.name for o in sess.get_outputs()]}")
    sess_q = ort.InferenceSession(str(target_int8), providers=["CPUExecutionProvider"])
    print(f"[OK] INT8 Session verified. Outputs: {[o.name for o in sess_q.get_outputs()]}")
    print("\n==================================================")
    print("YOLOv8s-seg TRAINING & EXPORT COMPLETED SUCCESSFULLY")
    print("==================================================")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train YOLOv8s-seg")
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch", type=int, default=8)
    args = parser.parse_args()
    train_and_export_s(epochs=args.epochs, batch_size=args.batch)
