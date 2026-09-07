"""Post-training INT8 dynamic quantization for ONNX instance segmentation models."""

import os
from pathlib import Path

import onnxruntime as ort
from onnxruntime.quantization import QuantType, quantize_dynamic

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def quantize_model(
    input_model_path: str = str(BASE_DIR / "models" / "onnx" / "best_s.onnx"),
    output_model_path: str = str(BASE_DIR / "models" / "onnx" / "best_s_int8.onnx"),
) -> Path:
    """Quantize FP32 ONNX model to INT8 precision.

    Args:
        input_model_path: Source FP32 ONNX path.
        output_model_path: Output INT8 quantized ONNX path.

    Returns:
        Path to quantized model.
    """
    in_path = Path(input_model_path)
    if not in_path.is_absolute() and not in_path.exists():
        in_path = BASE_DIR / in_path

    out_path = Path(output_model_path)
    if not out_path.is_absolute():
        out_path = BASE_DIR / out_path

    if not in_path.exists():
        raise FileNotFoundError(f"Source ONNX model not found: {in_path}")

    print(f"Quantizing: {in_path} -> {out_path}")
    orig_size = os.path.getsize(in_path) / (1024 * 1024)

    quantize_dynamic(
        model_input=str(in_path),
        model_output=str(out_path),
        weight_type=QuantType.QUInt8,
    )

    quant_size = os.path.getsize(out_path) / (1024 * 1024)
    reduction = (1 - (quant_size / orig_size)) * 100.0

    print("=" * 45)
    print(f"Original FP32 Size:   {orig_size:.2f} MB")
    print(f"Quantized INT8 Size:  {quant_size:.2f} MB")
    print(f"Memory Reduction:     {reduction:.1f}%")
    print("=" * 45)

    # Verify session load
    session = ort.InferenceSession(str(out_path), providers=["CPUExecutionProvider"])
    inputs = [i.name for i in session.get_inputs()]
    outputs = [o.name for o in session.get_outputs()]
    print(f"[OK] Verified INT8 model graph. Inputs: {inputs}, Outputs: {outputs}")

    return out_path


if __name__ == "__main__":
    quantize_model()
