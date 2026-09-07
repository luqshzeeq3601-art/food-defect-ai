"""Export Fine-Tuned Single YOLOv8s-seg Model to ONNX and INT8 Formats.

Exports PyTorch weights to optimized ONNX Runtime format with fixed 640x640 resolution,
generates dynamic INT8 quantized edge variant, and benchmarks deterministic latency.
"""

import shutil
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
from onnxruntime.quantization import QuantType, quantize_dynamic
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parents[2]
WEIGHTS_PT = BASE_DIR / "models" / "weights" / "best_s.pt"
ONNX_FP32 = BASE_DIR / "models" / "onnx" / "best_s.onnx"
ONNX_INT8 = BASE_DIR / "models" / "onnx" / "best_s_int8.onnx"


def export_to_onnx(
    weights_path: Path = WEIGHTS_PT, output_path: Path = ONNX_FP32
) -> Path:
    """Export PyTorch segmentation model to ONNX.

    Args:
        weights_path: Path to input .pt weights.
        output_path: Path for output .onnx graph.

    Returns:
        Path to exported ONNX file.
    """
    if not weights_path.exists():
        raise FileNotFoundError(f"Source weights not found at: {weights_path}")

    print(f"\n[EXPORT] Converting {weights_path} to ONNX (imgsz=640, opset=17)...")
    model = YOLO(str(weights_path), task="segment")
    exported_file = model.export(
        format="onnx",
        imgsz=640,
        dynamic=False,
        simplify=True,
        opset=17,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(exported_file, output_path)
    print(
        f"[EXPORT] Saved FP32 ONNX model to: {output_path} ({output_path.stat().st_size / (1024*1024):.1f} MB)"
    )
    return output_path


def quantize_to_int8(fp32_path: Path = ONNX_FP32, int8_path: Path = ONNX_INT8) -> Path:
    """Apply dynamic INT8 quantization to ONNX model.

    Args:
        fp32_path: Path to FP32 ONNX model.
        int8_path: Path for INT8 quantized model.

    Returns:
        Path to quantized INT8 file.
    """
    print("\n[QUANTIZE] Applying dynamic INT8 quantization...")
    quantize_dynamic(
        model_input=str(fp32_path),
        model_output=str(int8_path),
        weight_type=QuantType.QUInt8,
    )
    print(
        f"[QUANTIZE] Saved INT8 ONNX model to: {int8_path} ({int8_path.stat().st_size / (1024*1024):.1f} MB)"
    )
    return int8_path


def benchmark_onnx(model_path: Path, runs: int = 50) -> tuple[float, str]:
    """Benchmark ONNX model inference latency.

    Args:
        model_path: Path to .onnx file.
        runs: Number of warmup and test iterations.

    Returns:
        Tuple of (average latency in ms, active execution provider).
    """
    available_providers = ort.get_available_providers()
    providers = (
        ["CUDAExecutionProvider", "CPUExecutionProvider"]
        if "CUDAExecutionProvider" in available_providers
        else ["CPUExecutionProvider"]
    )

    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session = ort.InferenceSession(
        str(model_path), sess_options=sess_options, providers=providers
    )
    active_provider = session.get_providers()[0]

    input_name = session.get_inputs()[0].name
    dummy_input = np.random.randn(1, 3, 640, 640).astype(np.float32)

    # Warmup
    for _ in range(10):
        _ = session.run(None, {input_name: dummy_input})

    # Benchmark
    start = time.perf_counter()
    for _ in range(runs):
        _ = session.run(None, {input_name: dummy_input})
    avg_latency = ((time.perf_counter() - start) / runs) * 1000.0

    return avg_latency, active_provider


def main() -> None:
    """Run full export, quantization, and edge verification pipeline."""
    print("=" * 65)
    print("SINGLE YOLOv8s-seg ONNX & INT8 EDGE EXPORT PIPELINE")
    print("=" * 65)

    fp32_path = export_to_onnx()
    int8_path = quantize_to_int8()

    fp32_lat, fp32_prov = benchmark_onnx(fp32_path)
    int8_lat, int8_prov = benchmark_onnx(int8_path)

    print("\n" + "=" * 65)
    print("BENCHMARK VERIFICATION RESULTS")
    print("=" * 65)
    print(
        f"FP32 Model: {fp32_lat:.2f} ms ({fp32_prov}) [Size: {fp32_path.stat().st_size / (1024*1024):.1f} MB]"
    )
    print(
        f"INT8 Model: {int8_lat:.2f} ms ({int8_prov}) [Size: {int8_path.stat().st_size / (1024*1024):.1f} MB]"
    )
    print("=" * 65)


if __name__ == "__main__":
    main()
