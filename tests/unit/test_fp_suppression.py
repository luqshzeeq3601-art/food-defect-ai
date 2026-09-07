"""Tests verifying false positive suppression on negative conveyor backgrounds."""

import unittest
from pathlib import Path

import cv2
from src.core.detector import ONNXDetector
from src.core.grader import InspectionGrade, InspectionGrader

BASE_DIR = Path(__file__).resolve().parents[2]


class TestFalsePositiveSuppression(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.detector = ONNXDetector(str(BASE_DIR / "models" / "onnx" / "best_s.onnx"))
        cls.grader = InspectionGrader()
        cls.negative_sample = str(BASE_DIR / "data" / "samples" / "negative_backgrounds" / "conveyor_empty_01.jpg")

    def test_negative_conveyor_has_no_defects(self) -> None:
        img = cv2.imread(self.negative_sample)
        self.assertIsNotNone(img, "Could not load negative conveyor sample")
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        pred = self.detector.predict(rgb, confidence_threshold=0.30)

        # On empty conveyor, there should be zero false positive fruit and zero defects
        self.assertIsNone(pred["fruit"], "Stray fruit detected on empty belt")
        self.assertEqual(
            len(pred["defects"]), 0, "Stray defects detected on empty belt"
        )
        self.assertEqual(pred["defect_pixel_area"], 0)

        grade, ratio, _reason = self.grader.evaluate(
            fruit_pixels=pred["fruit_pixel_area"],
            defect_pixels=pred["defect_pixel_area"],
            defect_types=pred["defect_types"],
        )
        self.assertEqual(grade, InspectionGrade.NO_OBJECT)
        self.assertEqual(ratio, 0.0)


if __name__ == "__main__":
    unittest.main()
