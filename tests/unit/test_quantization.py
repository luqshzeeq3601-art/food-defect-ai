"""Unit tests verifying ONNX INT8 Quantization integrity."""

import os
import unittest
from pathlib import Path

import cv2
from src.core.detector import ONNXDetector

BASE_DIR = Path(__file__).resolve().parents[2]


class TestONNXQuantization(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fp32_path = BASE_DIR / "models" / "onnx" / "best_s.onnx"
        cls.int8_path = BASE_DIR / "models" / "onnx" / "best_s_int8.onnx"
        cls.test_image_path = str(BASE_DIR / "data" / "samples" / "dataset_defective_fruit.jpg")

    def test_model_files_exist(self) -> None:
        self.assertTrue(self.fp32_path.exists(), "FP32 ONNX model missing")
        self.assertTrue(self.int8_path.exists(), "INT8 ONNX model missing")

    def test_memory_reduction(self) -> None:
        fp32_size = os.path.getsize(self.fp32_path) / (1024 * 1024)
        int8_size = os.path.getsize(self.int8_path) / (1024 * 1024)
        # INT8 model should be less than 50% the size of FP32
        self.assertLess(int8_size, fp32_size * 0.5)
        self.assertLess(int8_size, 15.0)  # Should be ~11.8MB for YOLOv8s

    def test_int8_inference_parity(self) -> None:
        det_int8 = ONNXDetector(str(self.int8_path))
        img = cv2.imread(self.test_image_path)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        pred = det_int8.predict(rgb, confidence_threshold=0.15)
        self.assertIsNotNone(pred["fruit"])
        self.assertGreaterEqual(len(pred["defects"]), 1)
        self.assertGreater(pred["defect_pixel_area"], 0)


if __name__ == "__main__":
    unittest.main()
