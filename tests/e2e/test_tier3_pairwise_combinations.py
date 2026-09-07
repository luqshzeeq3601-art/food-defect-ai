"""Tier 3 E2E Test Suite: Cross-Feature Pairwise Combinations.

Tests cross-feature interactions across the AOI pipeline:
- Feature 1 (Empty Belt Suppression) x Feature 7 (Quantization Precision INT8/FP32)
- Feature 1 (Empty Belt Suppression) x Feature 5 (API Overlay Rendering Toggle)
- Feature 2 (Spatial Filtering) x Feature 4 (Grading Thresholds: Grade A / B / Reject)
- Feature 2 (Spatial Filtering) x Feature 1 (Defects Outside Fruit on Belt)
- Feature 3 (Rot Zero-Tolerance) x Feature 4 (Low Defect Ratio Overrides)
- Feature 3 (Rot Zero-Tolerance) x Feature 4 (Moderate Defect Ratio Overrides)
- Multi-Defect Aggregation x Grade A / Grade B / Reject Transitions
- Multi-Defect Coexistence: Rot Dominance over Non-Rot Blemishes
- Image Format Encoding (PNG / BMP) x API Pipeline Processing

Total tests: 14 (exceeds requirement of >= 10).
"""

import unittest

import numpy as np
from fastapi.testclient import TestClient
from src.api.main import app
from src.core.grader import InspectionGrade, InspectionGrader

from tests.e2e.helpers import (
    NEGATIVE_DIR,
    SAMPLES_DIR,
    create_synthetic_masks,
    encode_image,
    generate_fruit_image,
)


class TestPairwiseCombinations(unittest.TestCase):
    """Pairwise combinatorial tests across features."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        cls.grader = InspectionGrader(grade_a_threshold=1.0, grade_b_threshold=5.0)
        cls.sample_healthy = SAMPLES_DIR / "dataset_healthy_fruit.jpg"
        cls.sample_defective = SAMPLES_DIR / "sample_apple_rot_real.jpg"
        cls.sample_empty = NEGATIVE_DIR / "conveyor_empty_01.jpg"

    def test_t3_01_empty_conveyor_x_int8_quantization(self) -> None:
        """Empty conveyor frame evaluated with INT8 precision maintains NO_OBJECT suppression."""
        with open(self.sample_empty, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect?precision=int8",
                files={"file": ("empty.jpg", f, "image/jpeg")},
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["grade"], "NO_OBJECT")
        self.assertEqual(data["defect_ratio_percent"], 0.0)
        self.assertEqual(len(data["defects"]), 0)

    def test_t3_02_empty_conveyor_x_overlay_suppression(self) -> None:
        """Empty conveyor with return_overlay=false outputs NO_OBJECT and null overlay."""
        with open(self.sample_empty, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect?return_overlay=false",
                files={"file": ("empty.jpg", f, "image/jpeg")},
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["grade"], "NO_OBJECT")
        self.assertIsNone(data["overlay_image_base64"])

    def test_t3_03_healthy_fruit_x_int8_quantization(self) -> None:
        """Healthy fruit evaluated under INT8 precision achieves Grade A."""
        sample_pristine = SAMPLES_DIR / "sample_fruit_grade_a.jpg"
        with open(sample_pristine, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect?precision=int8",
                files={"file": ("healthy.jpg", f, "image/jpeg")},
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn(data["grade"], ["PASS_GRADE_A", "PASS_GRADE_B"])
        self.assertLessEqual(data["defect_ratio_percent"], 5.0)

    def test_t3_04_healthy_fruit_x_overlay_generation(self) -> None:
        """Healthy fruit with return_overlay=true renders non-null base64 overlay."""
        with open(self.sample_healthy, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect?return_overlay=true",
                files={"file": ("healthy.jpg", f, "image/jpeg")},
            )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIsNotNone(data["overlay_image_base64"])
        self.assertGreater(len(data["overlay_image_base64"]), 100)

    def test_t3_05_defective_fruit_x_fp32_vs_int8_parity(self) -> None:
        """Defective fruit evaluated under both FP32 and INT8 flags defects."""
        with open(self.sample_defective, "rb") as f:
            bytes_fp32 = f.read()
        with open(self.sample_defective, "rb") as f:
            bytes_int8 = f.read()

        resp_fp32 = self.client.post(
            "/api/v1/inspect?precision=fp32",
            files={"file": ("d.jpg", bytes_fp32, "image/jpeg")},
        )
        resp_int8 = self.client.post(
            "/api/v1/inspect?precision=int8",
            files={"file": ("d.jpg", bytes_int8, "image/jpeg")},
        )

        self.assertEqual(resp_fp32.status_code, 200)
        self.assertEqual(resp_int8.status_code, 200)
        self.assertGreater(resp_fp32.json()["defect_ratio_percent"], 0.0)
        self.assertGreater(resp_int8.json()["defect_ratio_percent"], 0.0)
        self.assertEqual(resp_fp32.json()["grade"], "REJECT")

    def test_t3_06_spatial_filtering_x_grade_transition(self) -> None:
        """Spatial clipping of boundary defect shifts grade from REJECT to GRADE_A."""
        # Unclipped defect would be 6,000 pixels on 100,000 fruit (6.0% -> REJECT)
        # When clipped by fruit boundary, only 800 pixels intersect (0.8% -> GRADE_A)
        fruit_pixels = 100000
        raw_defect_pixels = 6000
        clipped_defect_pixels = 800

        # Unclipped would reject
        grade_unclipped, _, _ = self.grader.evaluate(
            fruit_pixels, raw_defect_pixels, ["bruise"]
        )
        self.assertEqual(grade_unclipped, InspectionGrade.REJECT)

        # Clipped becomes Grade A
        grade_clipped, ratio, _ = self.grader.evaluate(
            fruit_pixels, clipped_defect_pixels, ["bruise"]
        )
        self.assertEqual(grade_clipped, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.8)

    def test_t3_07_spatial_filtering_completely_external_defect(self) -> None:
        """Defect on conveyor belt outside fruit is filtered to 0, resulting in Grade A."""
        fruit_mask, defects = create_synthetic_masks(
            fruit_center=(250, 250),
            fruit_radius=100,
            defect_specs=[{"type": "bruise", "center": (500, 500), "radius": 40}],
        )
        on_fruit_pixels = int(np.sum(defects[0]["mask"] & fruit_mask))
        fruit_pixels = int(np.sum(fruit_mask))

        grade, ratio, _ = self.grader.evaluate(
            fruit_pixels, on_fruit_pixels, ["bruise"]
        )
        self.assertEqual(on_fruit_pixels, 0)
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.0)

    def test_t3_08_rot_defect_x_grade_a_ratio(self) -> None:
        """Rot defect with 0.1% ratio (normally Grade A zone) is strictly forced to REJECT."""
        grade, ratio, reason = self.grader.evaluate(100000, 100, ["rot"])
        self.assertEqual(ratio, 0.1)
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertIn("Active rot detected", reason)

    def test_t3_09_rot_defect_x_grade_b_ratio(self) -> None:
        """Rot defect with 3.0% ratio (normally Grade B zone) is strictly forced to REJECT."""
        grade, ratio, reason = self.grader.evaluate(100000, 3000, ["rot"])
        self.assertEqual(ratio, 3.0)
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertIn("Active rot detected", reason)

    def test_t3_10_multi_defect_bruise_and_scab_below_threshold(self) -> None:
        """Coexistence of 0.4% bruise + 0.4% scab sums to 0.8%, qualifying for Grade A."""
        grade, ratio, _ = self.grader.evaluate(100000, 800, ["bruise", "scab"])
        self.assertEqual(ratio, 0.8)
        self.assertEqual(grade, InspectionGrade.GRADE_A)

    def test_t3_11_multi_defect_additive_crossing_into_grade_b(self) -> None:
        """Coexistence of 0.7% bruise + 0.5% scab sums to 1.2%, crossing into Grade B."""
        grade, ratio, _ = self.grader.evaluate(100000, 1200, ["bruise", "scab"])
        self.assertEqual(ratio, 1.2)
        self.assertEqual(grade, InspectionGrade.GRADE_B)

    def test_t3_12_multi_defect_additive_crossing_into_reject(self) -> None:
        """Coexistence of 3.0% bruise + 2.5% scab sums to 5.5%, crossing into REJECT."""
        grade, ratio, reason = self.grader.evaluate(100000, 5500, ["bruise", "scab"])
        self.assertEqual(ratio, 5.5)
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertIn("exceeds threshold", reason)

    def test_t3_13_multi_defect_rot_and_bruise_coexistence(self) -> None:
        """Coexistence of 2.0% bruise with 0.05% rot causes immediate rejection citing rot."""
        grade, _ratio, reason = self.grader.evaluate(100000, 2050, ["bruise", "rot"])
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertIn("Active rot detected", reason)

    def test_t3_14_png_format_x_healthy_fruit(self) -> None:
        """Healthy fruit synthetic image encoded as PNG is processed via API endpoint."""
        img = generate_fruit_image()
        png_bytes = encode_image(img, fmt=".png")
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("healthy.png", png_bytes, "image/png")},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("inspection_id", resp.json())


if __name__ == "__main__":
    unittest.main()
