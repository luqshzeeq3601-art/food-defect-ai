"""Industrial AOI Benchmarking Suite: PyTorch FP32 vs ONNX FP32 vs ONNX INT8."""

import argparse
import os
import time
from pathlib import Path

import numpy as np
from ultralytics import YOLO


def run_single_benchmark(
    model_path: str, task: str, dummy_img: np.ndarray, iterations: int, warmup: int
):
    path = Path(model_path)
    if not path.exists():
        return None

    size_mb = os.path.getsize(path) / (1024 * 1024)
    model = YOLO(str(path), task=task) if task else YOLO(str(path))

    # Warmup
    for _ in range(warmup):
        _ = model.predict(dummy_img, verbose=False)

    times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = model.predict(dummy_img, verbose=False)
        times.append((time.perf_counter() - t0) * 1000.0)

    return {
        "path": str(path),
        "size_mb": size_mb,
        "mean_ms": float(np.mean(times)),
        "std_ms": float(np.std(times)),
        "p95_ms": float(np.percentile(times, 95)),
        "fps": 1000.0 / float(np.mean(times)),
    }


BASE_DIR = Path(__file__).resolve().parent.parent.parent


def benchmark_suite(
    pt_path: str = str(BASE_DIR / "models" / "weights" / "best_s.pt"),
    onnx_fp32_path: str = str(BASE_DIR / "models" / "onnx" / "best_s.onnx"),
    onnx_int8_path: str = str(BASE_DIR / "models" / "onnx" / "best_s_int8.onnx"),
    iterations: int = 30,
    warmup: int = 5,
) -> None:
    print(f"\n{'='*75}")
    print("AUTOMATED OPTICAL INSPECTION (AOI) BENCHMARK SUITE")
    print(f"Iterations: {iterations} | Warmup: {warmup} | Input: 640x640x3 RGB")
    print(f"{'='*75}")

    dummy_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)

    res_pt = run_single_benchmark(
        pt_path, task=None, dummy_img=dummy_img, iterations=iterations, warmup=warmup
    )
    res_fp32 = run_single_benchmark(
        onnx_fp32_path,
        task="segment",
        dummy_img=dummy_img,
        iterations=iterations,
        warmup=warmup,
    )
    res_int8 = run_single_benchmark(
        onnx_int8_path,
        task="segment",
        dummy_img=dummy_img,
        iterations=iterations,
        warmup=warmup,
    )

    print(
        "\n| Model Variant           | File Size | Mean Latency | P95 Latency | Throughput | vs PyTorch |"
    )
    print(
        "| :---------------------- | :-------: | :----------: | :---------: | :--------: | :--------: |"
    )

    baseline_ms = res_pt["mean_ms"] if res_pt else 1.0

    for label, res in [
        ("PyTorch FP32", res_pt),
        ("ONNX FP32", res_fp32),
        ("ONNX INT8 Quantized", res_int8),
    ]:
        if res:
            speedup = baseline_ms / res["mean_ms"]
            print(
                f"| {label:<23} | {res['size_mb']:>6.2f} MB | {res['mean_ms']:>8.2f} ms | "
                f"{res['p95_ms']:>7.2f} ms | {res['fps']:>6.1f} FPS | {speedup:>8.2f}x |"
            )

    print(f"{'='*75}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark AOI Vision Models")
    parser.add_argument(
        "--iterations", type=int, default=20, help="Benchmark iterations"
    )
    parser.add_argument("--warmup", type=int, default=5, help="Warmup iterations")
    args = parser.parse_args()

    benchmark_suite(iterations=args.iterations, warmup=args.warmup)
