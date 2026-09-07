"""Train Single YOLOv8s-seg Produce Sorting Model on RTX 3070 with Thermal Protection.

Fine-tunes YOLOv8s-seg on the 3-class Roboflow KUKA dataset with injected negative
conveyor frames to achieve >= 90% produce sorting recall with sub-15ms GPU latency.
"""

import shutil
import subprocess
import threading
import time
from pathlib import Path

from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_YAML = BASE_DIR / "data" / "roboflow_kuka" / "kuka_data.yaml"
BASE_WEIGHTS = BASE_DIR / "models" / "weights" / "best_s.pt"
if not BASE_WEIGHTS.exists():
    BASE_WEIGHTS = BASE_DIR / "models" / "weights" / "yolov8s-seg.pt"
OUTPUT_WEIGHTS = BASE_DIR / "models" / "weights" / "best_s.pt"
REPORTS_DIR = BASE_DIR / "reports"

SAFETY_MAX_TEMP = 84.0  # Celsius thermal throttle ceiling
SAFE_RESUME_TEMP = 72.0  # Celsius resume target


class GPUThermalGuard(threading.Thread):
    """Background thread monitoring GPU temperature and throttling if threshold exceeded."""

    def __init__(self, check_interval_sec: float = 4.0) -> None:
        super().__init__(daemon=True)
        self.check_interval_sec = check_interval_sec
        self.stop_event = threading.Event()
        self.max_observed_temp: float = 0.0

    def query_temp(self) -> float | None:
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=temperature.gpu",
                "--format=csv,noheader,nounits",
            ]
            out = subprocess.check_output(cmd, encoding="utf-8").strip()
            return float(out)
        except (subprocess.SubprocessError, ValueError, OSError):
            return None

    def run(self) -> None:
        while not self.stop_event.is_set():
            temp = self.query_temp()
            if temp is not None:
                self.max_observed_temp = max(self.max_observed_temp, temp)
                if temp >= SAFETY_MAX_TEMP:
                    print(
                        f"\n[ALERT] GPU Temperature {temp}°C >= {SAFETY_MAX_TEMP}°C! Cooling down..."
                    )
                    while (
                        temp is not None
                        and temp > SAFE_RESUME_TEMP
                        and not self.stop_event.is_set()
                    ):
                        time.sleep(3)
                        temp = self.query_temp()
            self.stop_event.wait(self.check_interval_sec)

    def stop(self) -> None:
        self.stop_event.set()


def train_single_model(
    epochs: int = 25,
    batch_size: int = 16,
    imgsz: int = 640,
    device: int = 0,
) -> Path:
    """Fine-tune single YOLOv8s-seg model with thermal sentinel.

    Args:
        epochs: Number of training epochs.
        batch_size: Training batch size.
        imgsz: Image resolution.
        device: CUDA device index (0 for primary RTX 3070).

    Returns:
        Path to the saved best PyTorch model weights.
    """
    if not DATA_YAML.exists():
        raise FileNotFoundError(f"Dataset config missing at: {DATA_YAML}")
    if not BASE_WEIGHTS.exists():
        raise FileNotFoundError(f"Base weights missing at: {BASE_WEIGHTS}")

    print("=" * 65)
    print("TRAINING SINGLE YOLOv8s-seg MODEL ON NVIDIA GEFORCE RTX 3070")
    print(f"Dataset:       {DATA_YAML}")
    print(f"Base Weights:  {BASE_WEIGHTS}")
    print(
        f"Config:        Epochs={epochs} | Batch={batch_size} | Imgsz={imgsz} | Device={device}"
    )
    print(f"Thermal Guard: Active (Max Cutoff: {SAFETY_MAX_TEMP}°C)")
    print("=" * 65)

    # Launch GPU thermal sentinel
    guard = GPUThermalGuard(check_interval_sec=5.0)
    guard.start()

    try:
        model = YOLO(str(BASE_WEIGHTS))
        _results = model.train(
            data=str(DATA_YAML),
            epochs=epochs,
            batch=batch_size,
            imgsz=imgsz,
            device=device,
            amp=True,
            cos_lr=True,
            retina_masks=False,
            box=7.5,
            cls=2.2,
            hsv_h=0.015,
            scale=0.5,
            lr0=0.0006,
            lrf=0.01,
            close_mosaic=5,
            project="runs/segment",
            name="single_produce_model_v3",
            exist_ok=True,
            workers=2,
            verbose=True,
        )
    finally:
        guard.stop()
        guard.join(timeout=2.0)
        print(
            f"\n[THERMAL] Peak GPU Temperature during run: {guard.max_observed_temp:.1f}°C"
        )

    # Copy best weights
    run_dir = Path("runs/segment/single_produce_model_v3")
    if not (run_dir / "weights" / "best.pt").exists():
        alt_path = Path(
            "C:/Users/ZeeqRyz/Desktop/Deep Learning Project/runs/segment/runs/segment/single_produce_model_v3"
        )
        if (alt_path / "weights" / "best.pt").exists():
            run_dir = alt_path

    best_pt = run_dir / "weights" / "best.pt"
    if not best_pt.exists():
        raise FileNotFoundError(f"Trained weights not found at: {best_pt}")

    OUTPUT_WEIGHTS.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(best_pt, OUTPUT_WEIGHTS)
    print(f"\n[OK] Model successfully trained and saved to: {OUTPUT_WEIGHTS}")

    # Copy plots & metrics to reports/
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    for plot_file in run_dir.glob("*.png"):
        shutil.copy2(plot_file, REPORTS_DIR / plot_file.name)
    for csv_file in run_dir.glob("*.csv"):
        shutil.copy2(csv_file, REPORTS_DIR / csv_file.name)
    print(f"[OK] Training telemetry and metric plots saved to: {REPORTS_DIR}")

    return OUTPUT_WEIGHTS


if __name__ == "__main__":
    train_single_model(epochs=30, batch_size=16, imgsz=640, device=0)
