"""Unit tests for the Gradio Operator Dashboard and inspection pipeline."""

import unittest

import gradio as gr
from src.core.grader import InspectionGrade
from src.ui.gradio_app import (
    build_gradio_app,
    get_detector,
    inspect_frame,
    load_preset_image,
    render_html_header,
    render_kpi_hud,
)


class TestGradioApp(unittest.TestCase):
    """Test suite for Gradio UI components, rendering, and reactive pipeline."""

    def test_header_html_rendered(self) -> None:
        """Verify the custom SVG header HTML contains telemetry and station info."""
        header = render_html_header()
        self.assertIn("ViTrox Inspec-Belt AI", header)
        self.assertIn("STATION #01", header)
        self.assertIn("ONNX RUNTIME", header)

    def test_kpi_hud_rendering(self) -> None:
        """Verify KPI HUD generates expected status badges and metrics."""
        hud_a = render_kpi_hud(
            grade=InspectionGrade.GRADE_A,
            ratio=0.5,
            reject_reason=None,
            t_infer=15.2,
            fruit_pixels=50000,
            defect_pixels=250,
            grade_b_tol=5.0,
        )
        self.assertIn("PASS (GRADE A)", hud_a)
        self.assertIn("0.50%", hud_a)
        self.assertIn("15.2 ms", hud_a)

        hud_reject = render_kpi_hud(
            grade=InspectionGrade.REJECT,
            ratio=7.5,
            reject_reason="Defect area exceeds threshold",
            t_infer=18.0,
            fruit_pixels=50000,
            defect_pixels=3750,
            grade_b_tol=5.0,
        )
        self.assertIn("REJECTED", hud_reject)
        self.assertIn("Rejection Reason", hud_reject)
        self.assertIn("Defect area exceeds threshold", hud_reject)

    def test_get_detector_caching(self) -> None:
        """Verify detector instances are properly loaded and cached."""
        det_fp32 = get_detector("YOLOv8s-seg FP32")
        self.assertIsNotNone(det_fp32)
        det_fp32_repeat = get_detector("YOLOv8s-seg FP32")
        self.assertIs(det_fp32, det_fp32_repeat)

        det_int8 = get_detector("YOLOv8s-seg INT8")
        self.assertIsNotNone(det_int8)
        self.assertIsNot(det_fp32, det_int8)

    def test_load_preset_image(self) -> None:
        """Verify sample images load as 3-channel RGB numpy arrays."""
        img = load_preset_image("Healthy Apple")
        self.assertIsNotNone(img)
        self.assertEqual(img.ndim, 3)
        self.assertEqual(img.shape[2], 3)

        invalid_img = load_preset_image("NonExistentPreset")
        self.assertIsNone(invalid_img)

    def test_inspect_frame_none_input(self) -> None:
        """Verify inspect_frame handles None input gracefully without exception."""
        overlay, mask, kpi, table, hist = inspect_frame(
            image=None,
            model_choice="YOLOv8s-seg FP32",
            conf_threshold=0.35,
            grade_a_tol=1.0,
            grade_b_tol=5.0,
            history_state=[],
        )
        self.assertIsNone(overlay)
        self.assertIsNone(mask)
        self.assertIn("Awaiting Camera Capture", kpi)
        self.assertEqual(len(table), 0)
        self.assertEqual(len(hist), 0)

    def test_inspect_frame_healthy_sample(self) -> None:
        """Verify inspection of a healthy sample produces valid outputs and Grade A."""
        img = load_preset_image("Healthy Fruit (Dataset Test)")
        self.assertIsNotNone(img)

        overlay, mask, kpi, table, hist = inspect_frame(
            image=img,
            model_choice="YOLOv8s-seg FP32",
            conf_threshold=0.35,
            grade_a_tol=1.0,
            grade_b_tol=5.0,
            history_state=[],
        )
        self.assertIsNotNone(overlay)
        self.assertIsNotNone(mask)
        self.assertEqual(overlay.shape, img.shape)
        self.assertEqual(mask.shape, img.shape)
        self.assertIn("PASS (GRADE A)", kpi)
        self.assertLessEqual(len(table), 3)
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0][1], "FP32")
        self.assertEqual(hist[0][2], "PASS_GRADE_A")

    def test_inspect_frame_defective_sample(self) -> None:
        """Verify inspection of a defective rot sample detects defect and flags rejection."""
        img = load_preset_image("Defective Fruit (Dataset Test)")
        self.assertIsNotNone(img)

        overlay, mask, kpi, table, hist = inspect_frame(
            image=img,
            model_choice="YOLOv8s-seg FP32",
            conf_threshold=0.35,
            grade_a_tol=1.0,
            grade_b_tol=5.0,
            history_state=[],
        )
        self.assertIsNotNone(overlay)
        self.assertIsNotNone(mask)
        self.assertIn("REJECTED", kpi)
        self.assertGreater(len(table), 0)
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0][1], "FP32")
        self.assertEqual(hist[0][2], "REJECT")

    def test_inspect_frame_empty_conveyor(self) -> None:
        """Verify empty conveyor belt produces NO OBJECT status without crashing."""
        img = load_preset_image("Empty Conveyor Belt (Negative Test)")
        self.assertIsNotNone(img)

        overlay, mask, kpi, table, hist = inspect_frame(
            image=img,
            model_choice="YOLOv8s-seg FP32",
            conf_threshold=0.35,
            grade_a_tol=1.0,
            grade_b_tol=5.0,
            history_state=[],
        )
        self.assertIsNotNone(overlay)
        self.assertIsNotNone(mask)
        self.assertIn("NO OBJECT", kpi)
        self.assertEqual(len(table), 0)
        self.assertEqual(hist[0][2], "NO_OBJECT")

    def test_build_gradio_app_structure(self) -> None:
        """Verify that build_gradio_app returns a valid gr.Blocks application."""
        demo = build_gradio_app()
        self.assertIsInstance(demo, gr.Blocks)
        self.assertEqual(demo.title, "Food Defect AOI Inspector")


if __name__ == "__main__":
    unittest.main()
