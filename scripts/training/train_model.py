"""Train and export YOLOv8-seg on the Fruit Defect dataset."""
import shutil
from pathlib import Path

from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parents[2]


def train_and_export(epochs: int = 10, batch_size: int = 8, imgsz: int = 640) -> None:
    data_yaml = (BASE_DIR / "data/fruit_defects/data.yaml").resolve()
    base_model = (BASE_DIR / "models/weights/best_s.pt").resolve()
    if not base_model.exists():
        base_model = (BASE_DIR / "models/weights/best.pt").resolve()

    print(f"=== Starting YOLOv8-seg Training ({epochs} epochs, batch {batch_size}) ===")
    print(f"Dataset config: {data_yaml}")
    print(f"Base weights:   {base_model}")

    model = YOLO(str(base_model))

    # Train model
    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        project="runs/segment",
        name="fruit_defect_run",
        exist_ok=True,
        workers=2,
        verbose=True,
    )

    trained_weights = Path("runs/segment/fruit_defect_run/weights/best.pt")
    if trained_weights.exists():
        target_pt = Path("models/weights/best.pt")
        shutil.copy(trained_weights, target_pt)
        print(f"\n[OK] Copied fine-tuned weights to: {target_pt}")

        # Export to ONNX
        print("\n=== Exporting Fine-Tuned Model to ONNX ===")
        fine_tuned_model = YOLO(str(target_pt))
        exported_onnx = fine_tuned_model.export(
            format="onnx",
            imgsz=imgsz,
            opset=12,
            simplify=True,
        )
        target_onnx = Path("models/onnx/best.onnx")
        shutil.copy(exported_onnx, target_onnx)
        print(f"[OK] Exported ONNX model saved to: {target_onnx}")
        print("\n=== Training & ONNX Export Successfully Completed ===")
    else:
        print("[ERROR] Could not find trained weights at:", trained_weights)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train YOLOv8-seg on Fruit Defect dataset")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=8, help="Batch size")
    args = parser.parse_args()

    train_and_export(epochs=args.epochs, batch_size=args.batch)
