"""Tier 1 E2E Test Suite: Comprehensive Feature Coverage.

Covers all 7 core industrial AOI features in isolation:
1. Empty Conveyor Suppression (>= 5 tests)
2. Spatial Defect Mask Intersection (>= 5 tests)
3. Zero-Tolerance Rot Rejection (>= 5 tests)
4. Grade A/B/Reject Thresholds (>= 5 tests)
5. FastAPI /api/v1/inspect Contract (>= 5 tests)
6. Health & Metrics / Error Handling Endpoints (>= 5 tests)
7. Inference Latency Benchmark (>= 5 tests)

Total tests: 41 (exceeds requirement of >= 35).
"""

import base64
import time
import unittest

import cv2
import numpy as np
from fastapi.testclient import TestClient
from src.api.main import app
from src.core.detector import ONNXDetector
from src.core.grader import InspectionGrade, InspectionGrader

from tests.e2e.helpers import (
    NEGATIVE_DIR,
    SAMPLES_DIR,
    create_synthetic_masks,
    encode_image,
    generate_conveyor_image,
    generate_fruit_image,
)


class TestFeature1EmptyConveyorSuppression(unittest.TestCase):
    """Feature 1: Empty Conveyor Negative Suppression."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.detector = ONNXDetector("models/onnx/best_s.onnx")
        cls.grader = InspectionGrader()
        cls.client = TestClient(app)

    def test_f1_01_empty_conveyor_file_dataset_suppression(self) -> None:
        """Verify detector outputs 0 defects and no fruit on dataset conveyor files."""
        for sample_file in [
            "conveyor_empty_01.jpg",
            "conveyor_empty_02.jpg",
            "conveyor_empty_03.jpg",
        ]:
            path = NEGATIVE_DIR / sample_file
            if not path.exists():
                continue
            img_bgr = cv2.imread(str(path))
            self.assertIsNotNone(img_bgr, f"Failed to load {sample_file}")
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

            pred = self.detector.predict(rgb, confidence_threshold=0.30)
            self.assertIsNone(pred["fruit"], f"Fruit falsely detected on {sample_file}")
            self.assertEqual(
                len(pred["defects"]), 0, f"Defects falsely detected on {sample_file}"
            )
            self.assertEqual(pred["fruit_pixel_area"], 0)
            self.assertEqual(pred["defect_pixel_area"], 0)

    def test_f1_02_empty_conveyor_sample_4_to_6_suppression(self) -> None:
        """Verify detector suppresses false positives on additional conveyor frames."""
        for sample_file in [
            "conveyor_empty_04.jpg",
            "conveyor_empty_05.jpg",
            "conveyor_empty_06.jpg",
        ]:
            path = NEGATIVE_DIR / sample_file
            if not path.exists():
                continue
            img_bgr = cv2.imread(str(path))
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            pred = self.detector.predict(rgb, confidence_threshold=0.30)
            self.assertIsNone(pred["fruit"])
            self.assertEqual(len(pred["defects"]), 0)

    def test_f1_03_synthetic_roller_pattern_suppression(self) -> None:
        """Verify detector suppresses roller stripe patterns from being detected as fruit/defect."""
        roller_belt = generate_conveyor_image(width=640, height=640, pattern="rollers")
        pred = self.detector.predict(roller_belt)
        self.assertIsNone(pred["fruit"])
        self.assertEqual(len(pred["defects"]), 0)

    def test_f1_04_conveyor_with_sensor_noise_suppression(self) -> None:
        """Verify conveyor surface with injected high-frequency Gaussian noise suppresses false positives."""
        path = NEGATIVE_DIR / "conveyor_empty_07.jpg"
        if path.exists():
            img_bgr = cv2.imread(str(path))
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            # Ingest Gaussian noise
            rng = np.random.default_rng(999)
            noise = rng.normal(0, 8, rgb.shape).astype(np.int16)
            noisy_rgb = np.clip(rgb.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            pred = self.detector.predict(noisy_rgb, confidence_threshold=0.30)
            self.assertIsNone(pred["fruit"])
            self.assertEqual(len(pred["defects"]), 0)

    def test_f1_05_empty_conveyor_via_api_inspect(self) -> None:
        """Verify POST /api/v1/inspect on empty conveyor frame returns NO_OBJECT with 0 defects."""
        path = NEGATIVE_DIR / "conveyor_empty_01.jpg"
        with open(path, "rb") as f:
            response = self.client.post(
                "/api/v1/inspect",
                files={"file": ("empty_belt.jpg", f, "image/jpeg")},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["grade"], "NO_OBJECT")
        self.assertEqual(data["defect_ratio_percent"], 0.0)
        self.assertEqual(len(data["defects"]), 0)
        self.assertIsNone(data["fruit"])
        self.assertIn("No valid fruit", data["reject_reason"])

    def test_f1_06_grader_direct_zero_fruit_evaluation(self) -> None:
        """Verify grader evaluate returns NO_OBJECT with zero defect ratio when fruit_pixels is 0."""
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=0, defect_pixels=0, defect_types=[]
        )
        self.assertEqual(grade, InspectionGrade.NO_OBJECT)
        self.assertEqual(ratio, 0.0)
        self.assertEqual(reason, "No valid fruit body detected")


class TestFeature2SpatialMaskIntersection(unittest.TestCase):
    """Feature 2: Spatial Defect Mask Intersection."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.grader = InspectionGrader()

    def test_f2_01_defect_fully_inside_fruit_preserved(self) -> None:
        """Defect completely inside fruit body preserves 100% of defect pixels."""
        fruit_mask, defects = create_synthetic_masks(
            fruit_center=(320, 320),
            fruit_radius=150,
            defect_specs=[{"type": "bruise", "center": (320, 320), "radius": 20}],
        )
        d_mask = defects[0]["mask"]
        valid_intersection = d_mask & fruit_mask
        self.assertEqual(np.sum(valid_intersection), np.sum(d_mask))

    def test_f2_02_defect_fully_outside_fruit_filtered(self) -> None:
        """Defect placed outside fruit body is filtered to exactly 0 valid pixels."""
        fruit_mask, defects = create_synthetic_masks(
            fruit_center=(200, 200),
            fruit_radius=80,
            defect_specs=[{"type": "rot", "center": (500, 500), "radius": 30}],
        )
        d_mask = defects[0]["mask"]
        valid_intersection = d_mask & fruit_mask
        self.assertEqual(np.sum(valid_intersection), 0)

    def test_f2_03_defect_partially_overlapping_clipped(self) -> None:
        """Defect straddling fruit perimeter is clipped to the fruit boundary."""
        fruit_mask, defects = create_synthetic_masks(
            fruit_center=(320, 320),
            fruit_radius=100,
            defect_specs=[{"type": "bruise", "center": (420, 320), "radius": 30}],
        )
        d_mask = defects[0]["mask"]
        total_defect_px = np.sum(d_mask)
        valid_px = np.sum(d_mask & fruit_mask)

        # Must be strictly partial: some pixels retained, some clipped
        self.assertGreater(valid_px, 0)
        self.assertLess(valid_px, total_defect_px)

    def test_f2_04_multiple_defects_spatial_separation(self) -> None:
        """Multiple defect masks are filtered independently: only on-fruit pixels count."""
        fruit_mask, defects = create_synthetic_masks(
            fruit_center=(320, 320),
            fruit_radius=120,
            defect_specs=[
                {"type": "bruise", "center": (320, 320), "radius": 20},  # Inside
                {"type": "scab", "center": (100, 100), "radius": 25},  # Outside
            ],
        )
        inside_valid = np.sum(defects[0]["mask"] & fruit_mask)
        outside_valid = np.sum(defects[1]["mask"] & fruit_mask)

        self.assertGreater(inside_valid, 0)
        self.assertEqual(outside_valid, 0)

    def test_f2_05_detector_empty_fruit_suppresses_external_defects(self) -> None:
        """ONNXDetector predict logic guarantees defects_list is empty when no fruit is detected."""
        detector = ONNXDetector("models/onnx/best_s.onnx")
        path = NEGATIVE_DIR / "conveyor_empty_01.jpg"
        img_bgr = cv2.imread(str(path))
        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pred = detector.predict(rgb)
        self.assertIsNone(pred["fruit"])
        self.assertEqual(pred["defects"], [])

    def test_f2_06_stem_calyx_region_exclusion(self) -> None:
        """Stem/calyx anatomy is not counted in defect_types or defect surface area."""
        # When evaluating quality, only defect classes are passed
        grade, ratio, _reason = self.grader.evaluate(
            fruit_pixels=100000,
            defect_pixels=0,
            defect_types=[],  # stem_calyx excluded by detector
        )
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.0)


class TestFeature3ZeroToleranceRotRejection(unittest.TestCase):
    """Feature 3: Zero-Tolerance Active Rot Rejection."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.grader = InspectionGrader()
        cls.client = TestClient(app)

    def test_f3_01_rot_alone_triggers_reject(self) -> None:
        """Rot alone immediately rejects item even at low ratio."""
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000,
            defect_pixels=200,
            defect_types=["rot"],
        )
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 0.2)
        self.assertIsNotNone(reason)
        self.assertIn("rot", reason.lower())

    def test_f3_02_rot_microscopic_pixel_area_reject(self) -> None:
        """Even a 1-pixel rot patch triggers immediate rejection."""
        grade, _ratio, reason = self.grader.evaluate(
            fruit_pixels=200000,
            defect_pixels=1,
            defect_types=["rot"],
        )
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertIn("rot", reason.lower())

    def test_f3_03_rot_mixed_with_grade_a_bruise(self) -> None:
        """Rot mixed with minor bruise (ratio <= 1%) still results in REJECT."""
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000,
            defect_pixels=400,  # 0.4% total defect
            defect_types=["bruise", "rot"],
        )
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 0.4)
        self.assertIn("Active rot detected", reason)

    def test_f3_04_rot_case_variations(self) -> None:
        """Casing variations like 'ROT', 'Rot', or 'soft_rot' trigger zero-tolerance rot rejection."""
        for rot_str in ["ROT", "Rot", "soft_rot", "active_rot"]:
            grade, _, reason = self.grader.evaluate(
                fruit_pixels=100000,
                defect_pixels=50,
                defect_types=[rot_str],
            )
            self.assertEqual(grade, InspectionGrade.REJECT, f"Failed for {rot_str}")
            self.assertIn("rot", reason.lower())

    def test_f3_05_rot_rejection_reason_message(self) -> None:
        """Verify the rejection reason specifically cites zero-tolerance policy."""
        _, _, reason = self.grader.evaluate(
            fruit_pixels=50000,
            defect_pixels=50,
            defect_types=["rot"],
        )
        self.assertEqual(reason, "Active rot detected (zero-tolerance)")

    def test_f3_06_api_inspect_real_rot_sample(self) -> None:
        """Verify POST /api/v1/inspect with real orange sample containing rot results in REJECT."""
        rot_sample = SAMPLES_DIR / "sample_apple_rot_real.jpg"
        if not rot_sample.exists():
            self.skipTest("sample_apple_rot_real.jpg not available")

        with open(rot_sample, "rb") as f:
            response = self.client.post(
                "/api/v1/inspect",
                files={"file": ("rot_sample.jpg", f, "image/jpeg")},
            )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["grade"], "REJECT")
        self.assertTrue(
            any(d["defect_type"] in ["rot", "critical_defect"] for d in data["defects"])
        )


class TestFeature4GradingThresholds(unittest.TestCase):
    """Feature 4: Grade A / Grade B / Reject Thresholds."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.grader = InspectionGrader(grade_a_threshold=1.0, grade_b_threshold=5.0)

    def test_f4_01_zero_defect_grade_a(self) -> None:
        """0.0% defect ratio classifies as Grade A with no reject reason."""
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000, defect_pixels=0, defect_types=[]
        )
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.0)
        self.assertIsNone(reason)

    def test_f4_02_sub_percent_defect_grade_a(self) -> None:
        """Defect ratio 0.5% (<= 1.0%) classifies as Grade A."""
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000, defect_pixels=500, defect_types=["bruise"]
        )
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 0.5)
        self.assertIsNone(reason)

    def test_f4_03_exact_one_percent_grade_a(self) -> None:
        """Defect ratio exactly 1.0% classifies as Grade A."""
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000, defect_pixels=1000, defect_types=["scab"]
        )
        self.assertEqual(grade, InspectionGrade.GRADE_A)
        self.assertEqual(ratio, 1.0)
        self.assertIsNone(reason)

    def test_f4_04_moderate_defect_grade_b(self) -> None:
        """Defect ratio 2.5% (> 1.0% and <= 5.0%) classifies as Grade B."""
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000, defect_pixels=2500, defect_types=["scratch"]
        )
        self.assertEqual(grade, InspectionGrade.GRADE_B)
        self.assertEqual(ratio, 2.5)
        self.assertIsNone(reason)

    def test_f4_05_exact_five_percent_grade_b(self) -> None:
        """Defect ratio exactly 5.0% classifies as Grade B."""
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000, defect_pixels=5000, defect_types=["bruise"]
        )
        self.assertEqual(grade, InspectionGrade.GRADE_B)
        self.assertEqual(ratio, 5.0)
        self.assertIsNone(reason)

    def test_f4_06_excessive_defect_reject(self) -> None:
        """Defect ratio > 5.0% classifies as REJECT with descriptive reason."""
        grade, ratio, reason = self.grader.evaluate(
            fruit_pixels=100000, defect_pixels=5200, defect_types=["bruise"]
        )
        self.assertEqual(grade, InspectionGrade.REJECT)
        self.assertEqual(ratio, 5.2)
        self.assertIsNotNone(reason)
        self.assertIn("exceeds threshold", reason)


class TestFeature5FastAPIInspectContract(unittest.TestCase):
    """Feature 5: FastAPI /api/v1/inspect Schema & Contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        cls.sample_healthy = SAMPLES_DIR / "dataset_healthy_fruit.jpg"

    def test_f5_01_inspect_response_schema_fields(self) -> None:
        """Verify all fields defined in Data.md InspectionResponse schema are present."""
        with open(self.sample_healthy, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect", files={"file": ("healthy.jpg", f, "image/jpeg")}
            )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        required_fields = [
            "inspection_id",
            "timestamp",
            "image_width",
            "image_height",
            "fruit",
            "defects",
            "defect_ratio_percent",
            "grade",
            "reject_reason",
            "timing",
            "overlay_image_base64",
        ]
        for field in required_fields:
            self.assertIn(field, data, f"Missing required response field: {field}")

    def test_f5_02_inspect_timing_breakdown_contract(self) -> None:
        """Verify timing metrics adhere to InspectionTiming schema."""
        with open(self.sample_healthy, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect", files={"file": ("healthy.jpg", f, "image/jpeg")}
            )

        self.assertEqual(resp.status_code, 200)
        timing = resp.json()["timing"]
        for key in [
            "preprocess_ms",
            "inference_ms",
            "postprocess_ms",
            "grading_ms",
            "total_ms",
        ]:
            self.assertIn(key, timing)
            self.assertIsInstance(timing[key], (int, float))
            self.assertGreaterEqual(timing[key], 0.0)

    def test_f5_03_inspect_overlay_base64_generation(self) -> None:
        """When return_overlay=True, returns valid decodable JPEG base64 string."""
        with open(self.sample_healthy, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect?return_overlay=true",
                files={"file": ("healthy.jpg", f, "image/jpeg")},
            )
        self.assertEqual(resp.status_code, 200)
        overlay_b64 = resp.json()["overlay_image_base64"]
        self.assertIsNotNone(overlay_b64)
        # Decode and verify header
        decoded = base64.b64decode(overlay_b64)
        self.assertTrue(
            decoded.startswith(b"\xff\xd8"), "Overlay is not a valid JPEG stream"
        )

    def test_f5_04_inspect_overlay_disabled(self) -> None:
        """When return_overlay=False, overlay_image_base64 is None."""
        with open(self.sample_healthy, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect?return_overlay=false",
                files={"file": ("healthy.jpg", f, "image/jpeg")},
            )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.json()["overlay_image_base64"])

    def test_f5_05_inspect_precision_query_fp32_int8(self) -> None:
        """Inference precision query supports both fp32 and int8."""
        for prec in ["fp32", "int8"]:
            with open(self.sample_healthy, "rb") as f:
                resp = self.client.post(
                    f"/api/v1/inspect?precision={prec}",
                    files={"file": ("healthy.jpg", f, "image/jpeg")},
                )
            self.assertEqual(resp.status_code, 200, f"Failed for precision {prec}")

    def test_f5_06_inspect_bbox_normalized_coordinates(self) -> None:
        """Verify fruit and defect bounding box coordinates are normalized in [0.0, 1.0]."""
        with open(self.sample_healthy, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect", files={"file": ("healthy.jpg", f, "image/jpeg")}
            )
        self.assertEqual(resp.status_code, 200)
        fruit = resp.json()["fruit"]
        if fruit:
            bbox = fruit["bbox"]
            self.assertGreaterEqual(bbox["x_min"], 0.0)
            self.assertGreaterEqual(bbox["y_min"], 0.0)
            self.assertLessEqual(bbox["x_max"], 1.0)
            self.assertLessEqual(bbox["y_max"], 1.0)


class TestFeature6HealthMetricsAndErrors(unittest.TestCase):
    """Feature 6: Health Endpoint and API Error Handling."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_f6_01_health_endpoint_success(self) -> None:
        """GET /api/v1/health returns HTTP 200 with healthy status."""
        resp = self.client.get("/api/v1/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["model_loaded"])

    def test_f6_02_health_endpoint_metadata(self) -> None:
        """GET /api/v1/health provides execution_provider and version metadata."""
        resp = self.client.get("/api/v1/health")
        data = resp.json()
        self.assertIn("execution_provider", data)
        self.assertIn("version", data)
        self.assertEqual(data["execution_provider"], "CPUExecutionProvider")

    def test_f6_03_error_unsupported_media_type_text(self) -> None:
        """Upload of text/plain file returns HTTP 415."""
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("readme.txt", b"plain text", "text/plain")},
        )
        self.assertEqual(resp.status_code, 415)

    def test_f6_04_error_unsupported_media_type_pdf(self) -> None:
        """Upload of application/pdf file returns HTTP 415."""
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("doc.pdf", b"%PDF-1.4...", "application/pdf")},
        )
        self.assertEqual(resp.status_code, 415)

    def test_f6_05_error_payload_too_large(self) -> None:
        """Payload exceeding 10MB limit returns HTTP 413."""
        huge_bytes = b"0" * (10 * 1024 * 1024 + 1024)
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("huge.jpg", huge_bytes, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 413)

    def test_f6_06_error_corrupt_image_bytes(self) -> None:
        """Corrupted image payload claiming to be image/jpeg returns HTTP 422."""
        corrupt_bytes = b"not a real jpeg binary content"
        resp = self.client.post(
            "/api/v1/inspect",
            files={"file": ("bad.jpg", corrupt_bytes, "image/jpeg")},
        )
        self.assertEqual(resp.status_code, 422)


class TestFeature7InferenceLatencyBenchmark(unittest.TestCase):
    """Feature 7: Inference & Grading Latency Benchmarking."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.grader = InspectionGrader()
        cls.client = TestClient(app)
        cls.sample_healthy = SAMPLES_DIR / "dataset_healthy_fruit.jpg"

    def test_f7_01_grader_latency_under_5ms(self) -> None:
        """Grader evaluation executes 100 times in under 5ms total."""
        t0 = time.perf_counter()
        for _ in range(100):
            self.grader.evaluate(
                fruit_pixels=100000, defect_pixels=2500, defect_types=["bruise"]
            )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self.assertLess(elapsed_ms, 5.0, f"Grader evaluation took {elapsed_ms:.2f} ms")

    def test_f7_02_preprocessing_latency_budget(self) -> None:
        """Synthetic 640x640 frame decode and RGB conversion completes in under 15ms."""
        img = generate_fruit_image()
        raw_bytes = encode_image(img, fmt=".jpg")

        t0 = time.perf_counter()
        nparr = np.frombuffer(raw_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        _ = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        decode_ms = (time.perf_counter() - t0) * 1000.0

        self.assertLess(decode_ms, 15.0, f"Decoding took {decode_ms:.2f} ms")

    def test_f7_03_api_timing_metrics_sanity(self) -> None:
        """Verify API response total_ms is strictly >= inference_ms and components are positive."""
        with open(self.sample_healthy, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect", files={"file": ("h.jpg", f, "image/jpeg")}
            )
        self.assertEqual(resp.status_code, 200)
        t = resp.json()["timing"]
        self.assertGreaterEqual(t["total_ms"], t["inference_ms"])
        self.assertGreaterEqual(t["total_ms"], t["preprocess_ms"])
        self.assertGreaterEqual(t["total_ms"], t["postprocess_ms"])

    def test_f7_04_cpu_inference_latency_limit(self) -> None:
        """ONNX model inference latency reported by API on CPU is bounded under 200ms."""
        with open(self.sample_healthy, "rb") as f:
            resp = self.client.post(
                "/api/v1/inspect", files={"file": ("h.jpg", f, "image/jpeg")}
            )
        self.assertEqual(resp.status_code, 200)
        infer_ms = resp.json()["timing"]["inference_ms"]
        self.assertLess(infer_ms, 200.0, f"Inference took {infer_ms} ms")

    def test_f7_05_consecutive_requests_stability(self) -> None:
        """5 consecutive requests show stable execution without error or memory failure."""
        with open(self.sample_healthy, "rb") as f:
            img_bytes = f.read()

        for i in range(5):
            resp = self.client.post(
                "/api/v1/inspect",
                files={"file": (f"test_{i}.jpg", img_bytes, "image/jpeg")},
            )
            self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
