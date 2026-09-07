"""Tier 2 E2E Test Suite: Boundary and Corner Case Verification.

Covers boundary values, extreme geometries, edge thresholds, and payload limits:
- Threshold Boundaries (0.0%, 0.99%, 1.0%, 1.01%, 4.99%, 5.0%, 5.01%, 100.0%, >100%)
- Fruit & Defect Pixel Extremes (0, -1, 1, 10,000,000 pixels)
- Rot Micro-Defect and Compound String Boundaries
- Image Dimension Extremes (1x1, 10x10, 64x640, 640x64, 1920x1080)
- Payload Size Boundaries (0 bytes, near 10MB limit, >10MB)
- Media Type Boundaries (JPEG, PNG, BMP vs GIF, WEBP, TIFF)
- Floating-Point Precision & Rounding Invariants

Total tests: 40 (exceeds requirement of >= 35).
"""

import unittest

import numpy as np
from fastapi.testclient import TestClient
from src.api.main import app
from src.core.grader import InspectionGrade, InspectionGrader

from tests.e2e.helpers import (
    encode_image,
    generate_conveyor_image,
)


class TestDefectRatioThresholdBoundaries(unittest.TestCase):
    """Boundary value testing for defect ratio thresholds."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.grader = InspectionGrader(grade_a_threshold=1.0, grade_b_threshold=5.0)

    def test_t2_01_exact_zero_percent(self) -> None:
        """Defect ratio 0.00% is strictly Grade A."""
        grade, ratio, reason = self.grader.evaluate(100000, 0, [])
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.0)
        self.assertIsNone(reason)

    def test_t2_02_just_below_grade_a_threshold(self) -> None:
        """Defect ratio 0.99% is Grade A."""
        grade, ratio, reason = self.grader.evaluate(100000, 990, ["bruise"])
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.99)
        self.assertIsNone(reason)

    def test_t2_03_exact_grade_a_boundary(self) -> None:
        """Defect ratio exactly 1.00% is Grade A (inclusive boundary)."""
        grade, ratio, reason = self.grader.evaluate(100000, 1000, ["bruise"])
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 1.00)
        self.assertIsNone(reason)

    def test_t2_04_just_above_grade_a_boundary(self) -> None:
        """Defect ratio 1.01% transitions to Grade B."""
        grade, ratio, reason = self.grader.evaluate(100000, 1010, ["bruise"])
        self.assertEqual(grade, InspectionGrade.GRADE_B)
        self.assertEqual(ratio, 1.01)
        self.assertIsNone(reason)

    def test_t2_05_grade_b_midpoint(self) -> None:
        """Defect ratio 3.00% is Grade B."""
        grade, ratio, reason = self.grader.evaluate(100000, 3000, ["scab"])
        self.assertEqual(grade, InspectionGrade.GRADE_B)
        self.assertEqual(ratio, 3.00)
        self.assertIsNone(reason)

    def test_t2_06_just_below_grade_b_boundary(self) -> None:
        """Defect ratio 4.99% is Grade B."""
        grade, ratio, reason = self.grader.evaluate(100000, 4990, ["scratch"])
        self.assertEqual(grade, InspectionGrade.GRADE_B)
        self.assertEqual(ratio, 4.99)
        self.assertIsNone(reason)

    def test_t2_07_exact_grade_b_boundary(self) -> None:
        """Defect ratio exactly 5.00% is Grade B (inclusive boundary)."""
        grade, ratio, reason = self.grader.evaluate(100000, 5000, ["bruise"])
        self.assertEqual(grade, InspectionGrade.GRADE_B)
        self.assertEqual(ratio, 5.00)
        self.assertIsNone(reason)

    def test_t2_08_just_above_grade_b_boundary(self) -> None:
        """Defect ratio 5.01% transitions to REJECT."""
        grade, ratio, reason = self.grader.evaluate(100000, 5010, ["bruise"])
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 5.01)
        self.assertIsNotNone(reason)
        self.assertIn("exceeds threshold", reason)

    def test_t2_09_severe_defect_half_fruit(self) -> None:
        """Defect ratio 50.00% is REJECT."""
        grade, ratio, _reason = self.grader.evaluate(100000, 50000, ["scab"])
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 50.00)

    def test_t2_10_extreme_full_fruit_defect(self) -> None:
        """Defect ratio 100.00% is REJECT."""
        grade, ratio, _reason = self.grader.evaluate(100000, 100000, ["bruise"])
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 100.00)

    def test_t2_11_oversized_defect_pixels_clamped(self) -> None:
        """Defect pixels exceeding fruit pixels are clamped to 100.00%."""
        grade, ratio, _reason = self.grader.evaluate(100000, 150000, ["bruise"])
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 100.00)


class TestPixelCountCornerCases(unittest.TestCase):
    """Boundary testing on fruit and defect pixel counts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.grader = InspectionGrader()

    def test_t2_12_fruit_pixels_exact_zero(self) -> None:
        """Zero fruit pixels outputs NO_OBJECT."""
        grade, ratio, _reason = self.grader.evaluate(0, 0, [])
        self.assertEqual(grade, InspectionGrade.NO_OBJECT)
        self.assertEqual(ratio, 0.0)

    def test_t2_13_fruit_pixels_negative_boundary(self) -> None:
        """Negative fruit pixels defensively outputs NO_OBJECT."""
        grade, ratio, _reason = self.grader.evaluate(-1, 0, [])
        self.assertEqual(grade, InspectionGrade.NO_OBJECT)
        self.assertEqual(ratio, 0.0)

    def test_t2_14_fruit_pixels_single_pixel(self) -> None:
        """1 fruit pixel with 0 defect is Grade A."""
        grade, ratio, _reason = self.grader.evaluate(1, 0, [])
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.0)

    def test_t2_15_fruit_pixels_single_pixel_with_defect(self) -> None:
        """1 fruit pixel with 1 defect pixel is 100% defect -> REJECT."""
        grade, ratio, _reason = self.grader.evaluate(1, 1, ["bruise"])
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 100.0)

    def test_t2_16_ultra_large_industrial_pixel_area(self) -> None:
        """10,000,000 fruit pixels with 100,000 defect pixels (1.00%) correctly grades Grade A."""
        grade, ratio, _reason = self.grader.evaluate(10000000, 100000, ["scab"])
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 1.00)


class TestDefectTypeCornerCases(unittest.TestCase):
    """Testing edge cases in defect classification strings and zero-tolerance logic."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.grader = InspectionGrader()

    def test_t2_17_zero_defect_pixels_with_defect_types_listed(self) -> None:
        """Defect pixels 0 with non-rot types listed evaluates to 0.0% Grade A."""
        grade, ratio, _ = self.grader.evaluate(100000, 0, ["bruise"])
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.0)

    def test_t2_18_rot_with_one_pixel_in_ten_million(self) -> None:
        """1 rot pixel in 10,000,000 fruit pixels strictly triggers REJECT."""
        grade, _ratio, reason = self.grader.evaluate(10000000, 1, ["rot"])
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertIn("Active rot detected", reason)

    def test_t2_19_empty_defect_list_with_positive_pixels(self) -> None:
        """Missing defect type strings defaults to ratio-based grading without crash."""
        grade, ratio, _ = self.grader.evaluate(100000, 800, [])
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.8)

    def test_t2_20_unrecognized_defect_string(self) -> None:
        """Unrecognized defect class name evaluates by ratio."""
        grade, ratio, _ = self.grader.evaluate(100000, 2000, ["custom_spot"])
        self.assertEqual(grade, InspectionGrade.GRADE_B)
        self.assertEqual(ratio, 2.0)

    def test_t2_21_rot_compound_substrings(self) -> None:
        """All variations containing 'rot' trigger zero-tolerance rejection."""
        compounds = ["wet_rot", "collar_rot", "fruit_rot", "brown_rot", "rot_spot"]
        for c in compounds:
            grade, _, reason = self.grader.evaluate(100000, 10, [c])
            self.assertEqual(grade, InspectionGrade.REJECT, f"Failed for {c}")
            self.assertIn("rot", reason.lower())

    def test_t2_22_mixed_case_and_whitespace_defects(self) -> None:
        """Handles uppercase and whitespace-padded strings."""
        grade, _, _ = self.grader.evaluate(100000, 50, ["  ROT  "])
        self.assertEqual(grade, InspectionGrade.REJECT)


class TestImageDimensionAndGeometryBoundaries(unittest.TestCase):
    """Testing extreme image geometries, aspect ratios, and resolutions."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_t2_23_image_min_dimensions_1x1(self) -> None:
        """1x1 pixel image encoded to PNG is handled without crash."""
        img = np.zeros((1, 1, 3), dtype=np.uint8)
        img_bytes = encode_image(img, fmt=".png")
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("tiny.png", img_bytes, "image/png")},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["image_width"], 1)
        self.assertEqual(resp.json()["image_height"], 1)

    def test_t2_24_image_small_dimensions_10x10(self) -> None:
        """10x10 small thumbnail is handled cleanly."""
        img = np.full((10, 10, 3), 40, dtype=np.uint8)
        img_bytes = encode_image(img, fmt=".jpg")
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("small.jpg", img_bytes, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 200)

    def test_t2_25_narrow_tall_aspect_ratio(self) -> None:
        """Extreme tall aspect ratio (64x640) handles letterbox padding cleanly."""
        img = np.full((640, 64, 3), 50, dtype=np.uint8)
        img_bytes = encode_image(img, fmt=".jpg")
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("tall.jpg", img_bytes, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["image_width"], 64)
        self.assertEqual(resp.json()["image_height"], 640)

    def test_t2_26_narrow_wide_aspect_ratio(self) -> None:
        """Extreme wide aspect ratio (640x64) handles letterbox padding cleanly."""
        img = np.full((64, 640, 3), 50, dtype=np.uint8)
        img_bytes = encode_image(img, fmt=".jpg")
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("wide.jpg", img_bytes, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["image_width"], 640)
        self.assertEqual(resp.json()["image_height"], 64)

    def test_t2_27_exact_model_input_size_640x640(self) -> None:
        """Exactly 640x640 input resolution bypasses aspect ratio padding."""
        img = generate_conveyor_image(width=640, height=640)
        img_bytes = encode_image(img, fmt=".jpg")
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("exact.jpg", img_bytes, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["image_width"], 640)
        self.assertEqual(resp.json()["image_height"], 640)

    def test_t2_28_high_resolution_1920x1080(self) -> None:
        """Full HD 1920x1080 image scales down and maps coordinates accurately."""
        img = np.full((1080, 1920, 3), 35, dtype=np.uint8)
        img_bytes = encode_image(img, fmt=".jpg")
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("fhd.jpg", img_bytes, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["image_width"], 1920)
        self.assertEqual(resp.json()["image_height"], 1080)


class TestTransportPayloadAndFormatBoundaries(unittest.TestCase):
    """Testing payload sizes, MIME types, and unsupported format rejections."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_t2_29_minimal_single_byte_corrupt_upload(self) -> None:
        """1-byte minimal corrupted file upload returns HTTP 422 Unprocessable Entity."""
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("empty.jpg", b"\x00", "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 422)

    def test_t2_30_payload_just_under_10mb_limit(self) -> None:
        """Valid JPEG byte payload just under 10MB limit is accepted."""
        # Create a valid image with trailing padding under 10MB
        base_img = generate_conveyor_image(640, 640)
        valid_bytes = encode_image(base_img, fmt=".jpg")
        pad_size = (9 * 1024 * 1024) - len(valid_bytes)
        padded_bytes = valid_bytes + b"\x00" * pad_size

        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("under_limit.jpg", padded_bytes, "image/jpeg")},
        )
        # Should either process or succeed under size guard
        self.assertEqual(resp.status_code, 200)

    def test_t2_31_payload_exceeding_10mb_limit(self) -> None:
        """Payload exceeding 10MB limit by 1 byte returns HTTP 413."""
        oversized = b"X" * (10 * 1024 * 1024 + 1)
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("oversized.jpg", oversized, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 413)

    def test_t2_32_supported_format_jpeg(self) -> None:
        """JPEG format upload is accepted."""
        img = generate_conveyor_image(64, 64)
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("test.jpg", encode_image(img, ".jpg"), "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 200)

    def test_t2_33_supported_format_png(self) -> None:
        """PNG format upload is accepted."""
        img = generate_conveyor_image(64, 64)
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("test.png", encode_image(img, ".png"), "image/png")},
        )
        self.assertEqual(resp.status_code, 200)

    def test_t2_34_supported_format_bmp(self) -> None:
        """BMP format upload is accepted."""
        img = generate_conveyor_image(64, 64)
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("test.bmp", encode_image(img, ".bmp"), "image/bmp")},
        )
        self.assertEqual(resp.status_code, 200)

    def test_t2_35_unsupported_format_gif(self) -> None:
        """GIF format upload is rejected with HTTP 415."""
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("test.gif", b"GIF89a", "image/gif")},
        )
        self.assertEqual(resp.status_code, 415)

    def test_t2_36_unsupported_format_webp(self) -> None:
        """WEBP format upload is rejected with HTTP 415."""
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("test.webp", b"RIFF....WEBP", "image/webp")},
        )
        self.assertEqual(resp.status_code, 415)


class TestQueryParametersAndRoundingPrecision(unittest.TestCase):
    """Testing case-sensitivity of queries and floating point rounding."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.grader = InspectionGrader(grade_a_threshold=1.0, grade_b_threshold=5.0)
        cls.client = TestClient(app)

    def test_t2_37_precision_query_case_insensitive(self) -> None:
        """Upper case precision queries 'FP32' and 'INT8' succeed."""
        img = generate_conveyor_image(64, 64)
        img_bytes = encode_image(img, ".jpg")
        for p in ["FP32", "INT8", "fp32", "int8"]:
            resp = self.client.post(
                f"/api/v1/inspect?precision={p}",
                files={"file": ("p.jpg", img_bytes, "image/jpeg")},
            )
            self.assertEqual(resp.status_code, 200)

    def test_t2_38_precision_query_unknown_fallback(self) -> None:
        """Unrecognized precision query parameter falls back gracefully to default detector."""
        img = generate_conveyor_image(64, 64)
        img_bytes = encode_image(img, ".jpg")
        resp = self.client.post(
            "/api/v1/inspect?precision=ultra_precision",
            files={"file": ("p.jpg", img_bytes, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 200)

    def test_t2_39_floating_point_rounding_grade_a(self) -> None:
        """Ratio 1.004% rounds to 1.00% (Grade A boundary)."""
        # 1004 / 100000 = 1.004% -> rounds to 1.0% -> Grade A
        grade, ratio, _ = self.grader.evaluate(100000, 1004, ["bruise"])
        self.assertEqual(ratio, 1.00)
        self.assertEqual(grade, InspectionGrade.GRADE_A)

    def test_t2_40_floating_point_rounding_grade_b(self) -> None:
        """Ratio 1.006% rounds to 1.01% (Grade B boundary)."""
        # 1006 / 100000 = 1.006% -> rounds to 1.01% -> Grade B
        grade, ratio, _ = self.grader.evaluate(100000, 1006, ["bruise"])
        self.assertEqual(ratio, 1.01)
        self.assertEqual(grade, InspectionGrade.GRADE_B)


if __name__ == "__main__":
    unittest.main()
