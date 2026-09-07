"""Industrial Operator Dashboard for Automated Optical Inspection (AOI) with Gradio."""

import datetime
import sys
import time
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import cv2
import gradio as gr
import numpy as np
from PIL import Image

from src.core.detector import ONNXDetector
from src.core.grader import InspectionGrade, InspectionGrader

# Model paths anchored to project root
MODEL_PATH_FP32 = BASE_DIR / "models" / "onnx" / "best_s.onnx"
MODEL_PATH_INT8 = BASE_DIR / "models" / "onnx" / "best_s_int8.onnx"

# Preset Conveyor Captures anchored to project root
PRESET_SAMPLES: dict[str, str] = {
    "Defective Fruit (Dataset Test)": str(BASE_DIR / "data/samples/sample_apple_rot_real.jpg"),
    "Healthy Fruit (Dataset Test)": str(BASE_DIR / "data/samples/sample_fruit_grade_a.jpg"),
    "Defective Apple (Rot Simulated)": str(BASE_DIR / "data/samples/defective_apple_rot.jpg"),
    "Healthy Apple": str(BASE_DIR / "data/samples/real_apple.jpg"),
    "Healthy Orange": str(BASE_DIR / "data/samples/real_orange.jpg"),
    "Healthy Banana": str(BASE_DIR / "data/samples/real_banana.jpg"),
    "Empty Conveyor Belt (Negative Test)": str(BASE_DIR / "data/samples/negative_backgrounds/conveyor_empty_01.jpg"),
    "Sample Rotten Apple": str(BASE_DIR / "data/samples/sample_apple_rotten.jpg"),
    "Sample Bruised Apple": str(BASE_DIR / "data/samples/sample_apple_bruised.jpg"),
    "Sample Healthy Apple": str(BASE_DIR / "data/samples/sample_apple_healthy.jpg"),
}

# Detector cache for production reuse across sessions
_DETECTOR_CACHE: dict[str, ONNXDetector] = {}


def get_detector(model_choice: str) -> ONNXDetector:
    """Retrieve or lazily initialize cached ONNX detector instance.

    Args:
        model_choice: String identifying FP32 or INT8 model precision.

    Returns:
        Cached ONNXDetector instance.
    """
    is_int8 = "INT8" in model_choice
    cache_key = "int8" if is_int8 else "fp32"
    model_path = MODEL_PATH_INT8 if is_int8 else MODEL_PATH_FP32

    if cache_key not in _DETECTOR_CACHE:
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        _DETECTOR_CACHE[cache_key] = ONNXDetector(str(model_path))

    return _DETECTOR_CACHE[cache_key]


# Clean Industrial Machine Vision CSS (Anti-Slop, High-Legibility Tokens)
CUSTOM_CSS = """
:root {
    --bg-base: #0B0F19;
    --surface-card: #111827;
    --surface-subtle: #162032;
    --border-line: #1F2937;
    --border-highlight: #374151;
    --accent-cyan: #06B6D4;
    --text-primary: #F9FAFB;
    --text-secondary: #9CA3AF;
    --text-muted: #6B7280;
    --grade-pass-a: #10B981;
    --grade-pass-b: #F59E0B;
    --grade-reject: #EF4444;
}

body, .gradio-container {
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif !important;
}

/* Compact Industrial Header */
.aoi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: var(--surface-card);
    border: 1px solid var(--border-line);
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 16px;
}

.aoi-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.aoi-icon-box {
    width: 38px;
    height: 38px;
    border-radius: 6px;
    background: rgba(6, 182, 212, 0.1);
    border: 1px solid rgba(6, 182, 212, 0.25);
    display: flex;
    align-items: center;
    justify-content: center;
}

.aoi-title-box h1 {
    font-size: 1.15rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 2px 0;
    letter-spacing: -0.01em;
}

.aoi-title-box p {
    font-size: 0.78rem;
    color: var(--text-secondary);
    margin: 0;
}

.aoi-telemetry-cluster {
    display: flex;
    gap: 8px;
}

.telemetry-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--surface-subtle);
    border: 1px solid var(--border-line);
    border-radius: 4px;
    padding: 4px 10px;
    font-size: 0.72rem;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    color: var(--text-secondary);
}

.telemetry-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--accent-cyan);
}

/* Industrial KPI Grid */
.kpi-hud-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 12px;
}

.kpi-card {
    background: var(--surface-card);
    border: 1px solid var(--border-line);
    border-radius: 6px;
    padding: 12px 14px;
    display: flex;
    flex-direction: column;
}

.kpi-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 1.35rem;
    font-weight: 700;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    color: #FFFFFF;
}

.kpi-delta {
    font-size: 0.72rem;
    margin-top: 3px;
    color: var(--text-secondary);
}

/* Decision Status Badge */
.badge-status {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-align: center;
}

.badge-grade-a {
    background: rgba(16, 185, 129, 0.12);
    color: #10B981;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.badge-grade-b {
    background: rgba(245, 158, 11, 0.12);
    color: #F59E0B;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

.badge-reject {
    background: rgba(239, 68, 68, 0.12);
    color: #EF4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

.badge-no-obj {
    background: rgba(107, 114, 128, 0.12);
    color: #9CA3AF;
    border: 1px solid rgba(107, 114, 128, 0.4);
}

/* Alert Boxes */
.alert-box {
    border-radius: 6px;
    padding: 10px 14px;
    margin-top: 10px;
    font-size: 0.82rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

.alert-reject {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.35);
    color: #F87171;
}

.alert-pass {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #34D399;
}

/* Visual Legend Bar */
.visual-legend-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    background: var(--surface-card);
    border: 1px solid var(--border-line);
    border-radius: 6px;
    padding: 6px 14px;
    margin-bottom: 10px;
    font-size: 0.74rem;
    color: var(--text-secondary);
}

.legend-swatch {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 2px;
    margin-right: 5px;
}
"""


def render_html_header() -> str:
    """Generate industrial machine vision header with SVG reticle and live telemetry.

    Returns:
        Raw HTML string for the header banner.
    """
    return """
    <div class="aoi-header">
        <div class="aoi-header-left">
            <div class="aoi-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#06B6D4" stroke-width="1.8">
                    <circle cx="12" cy="12" r="9" stroke-opacity="0.5"/>
                    <circle cx="12" cy="12" r="3.5"/>
                    <line x1="12" y1="1" x2="12" y2="5"/>
                    <line x1="12" y1="19" x2="12" y2="23"/>
                    <line x1="1" y1="12" x2="5" y2="12"/>
                    <line x1="19" y1="12" x2="23" y2="12"/>
                </svg>
            </div>
            <div class="aoi-title-box">
                <h1>ViTrox Inspec-Belt AI • Automated Optical Inspection (AOI)</h1>
                <p>Surface Defect Delineation & Sorting Pipeline • YOLOv8-seg ONNX Engine</p>
            </div>
        </div>
        <div class="aoi-telemetry-cluster">
            <span class="telemetry-pill"><span class="telemetry-dot"></span>STATION #01 (ONLINE)</span>
            <span class="telemetry-pill">INFERENCE: ONNX RUNTIME</span>
            <span class="telemetry-pill">LATENCY BUDGET: &lt;50ms</span>
        </div>
    </div>
    """


def render_kpi_hud(
    grade: InspectionGrade,
    ratio: float,
    reject_reason: str | None,
    t_infer: float,
    fruit_pixels: int,
    defect_pixels: int,
    grade_b_tol: float,
) -> str:
    """Render clean, high-contrast industrial KPI HUD.

    Args:
        grade: Inspection grade enumeration value.
        ratio: Defect surface area ratio in percent.
        reject_reason: Optional rejection diagnostic message.
        t_infer: Inference latency in milliseconds.
        fruit_pixels: Total segmented fruit body pixels.
        defect_pixels: Total defect pixels.
        grade_b_tol: Grade B tolerance threshold in percent.

    Returns:
        Structured HTML string for the HUD container.
    """
    fps = 1000.0 / max(0.5, t_infer)
    delta_vs_tol = ratio - grade_b_tol
    delta_str = f"{delta_vs_tol:+.1f}% vs Grade B limit ({grade_b_tol}%)"

    if grade == InspectionGrade.GRADE_A:
        badge_html = '<div class="badge-status badge-grade-a">PASS (GRADE A)</div>'
        status_desc = "Optimal Surface (Export Quality)"
    elif grade == InspectionGrade.GRADE_B:
        badge_html = '<div class="badge-status badge-grade-b">PASS (GRADE B)</div>'
        status_desc = "Commercial / Domestic Tier"
    elif grade == InspectionGrade.REJECT:
        badge_html = '<div class="badge-status badge-reject">REJECTED</div>'
        status_desc = "Tolerance Exceeded / Active Rot"
    else:
        badge_html = '<div class="badge-status badge-no-obj">NO OBJECT</div>'
        status_desc = "Empty Conveyor Belt"

    if reject_reason:
        alert_html = f"""
        <div class="alert-box alert-reject">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div><strong>Rejection Reason:</strong> {reject_reason}</div>
        </div>
        """
    elif grade in (InspectionGrade.GRADE_A, InspectionGrade.GRADE_B):
        alert_html = """
        <div class="alert-box alert-pass">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
            <div><strong>Inspection Verified:</strong> Surface quality satisfies factory sorting limits.</div>
        </div>
        """
    else:
        alert_html = ""

    return f"""
    <div>
        <div class="kpi-hud-grid">
            <div class="kpi-card">
                <div class="kpi-label">Optical Quality Grade</div>
                {badge_html}
                <div class="kpi-delta">{status_desc}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Defect Area Ratio</div>
                <div class="kpi-value">{ratio:.2f}%</div>
                <div class="kpi-delta">{delta_str}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">ONNX Latency</div>
                <div class="kpi-value">{t_infer:.1f} ms</div>
                <div class="kpi-delta">Effective {fps:.1f} FPS</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Quantified Pixels</div>
                <div class="kpi-value">{defect_pixels:,} / {fruit_pixels:,}</div>
                <div class="kpi-delta">Defect px / Fruit px</div>
            </div>
        </div>
        {alert_html}
    </div>
    """


def render_visual_legend() -> str:
    """Render compact color legend for viewports.

    Returns:
        HTML string containing color-coded legend swatches.
    """
    return """
    <div class="visual-legend-bar">
        <span><strong style="color:#FFF;">Legend:</strong></span>
        <span><span class="legend-swatch" style="background: #10B981;"></span>Fruit Body</span>
        <span><span class="legend-swatch" style="background: #EF4444;"></span>Critical Rot (Zero-Tolerance)</span>
        <span><span class="legend-swatch" style="background: #F59E0B;"></span>Surface Blemish / Scab / Scratch</span>
    </div>
    """


def draw_industrial_visualizations(
    image: np.ndarray,
    pred: dict[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    """Render multi-layer semantic overlay and high-contrast binary defect heatmap.

    Args:
        image: Original RGB frame (H, W, 3).
        pred: Structured prediction dictionary from ONNXDetector.

    Returns:
        Tuple of (Semantic annotated RGB frame, Binary defect isolation RGB frame).
    """
    h, w = image.shape[:2]
    annotated = image.copy()
    defect_mask_canvas = np.zeros((h, w, 3), dtype=np.uint8)

    fruit = pred.get("fruit")
    defects = pred.get("defects", [])

    # 1. Render Fruit Boundary & Label
    if fruit:
        poly_pts = fruit.get("polygon", [])
        if poly_pts:
            pts = np.array(
                [[int(p["x"] * w), int(p["y"] * h)] for p in poly_pts],
                dtype=np.int32,
            )
            cv2.polylines(
                annotated,
                [pts],
                isClosed=True,
                color=(16, 185, 129),
                thickness=2,
            )

        bx = fruit.get("bbox", {})
        if bx:
            fx1, fy1 = int(bx["x_min"] * w), int(bx["y_min"] * h)
            fx2, fy2 = int(bx["x_max"] * w), int(bx["y_max"] * h)
            cv2.rectangle(annotated, (fx1, fy1), (fx2, fy2), (16, 185, 129), 2)
            label = f"{fruit.get('fruit_type', 'FRUIT').upper()} ({fruit.get('confidence', 0.0):.2f})"
            cv2.putText(
                annotated,
                label,
                (fx1 + 6, max(22, fy1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (16, 185, 129),
                2,
                cv2.LINE_AA,
            )

    # 2. Render Defect Polygons, Masks, and Heatmap Canvas
    for d in defects:
        defect_type = d.get("defect_type", "defect").lower()
        is_rot = "rot" in defect_type or "critical" in defect_type

        # Color: Crimson for Rot, Warm Amber for Bruise/Scab/Scratch
        color_rgb = (239, 68, 68) if is_rot else (245, 158, 11)

        poly_pts = d.get("polygon", [])
        if poly_pts:
            pts = np.array(
                [[int(p["x"] * w), int(p["y"] * h)] for p in poly_pts],
                dtype=np.int32,
            )
            overlay_slice = annotated.copy()
            cv2.fillPoly(overlay_slice, [pts], color_rgb)
            cv2.addWeighted(overlay_slice, 0.45, annotated, 0.55, 0, annotated)
            cv2.polylines(annotated, [pts], isClosed=True, color=color_rgb, thickness=2)

            cv2.fillPoly(defect_mask_canvas, [pts], color_rgb)
            cv2.polylines(
                defect_mask_canvas,
                [pts],
                isClosed=True,
                color=(255, 255, 255),
                thickness=1,
            )

        bx = d.get("bbox", {})
        if bx:
            dx1, dy1 = int(bx["x_min"] * w), int(bx["y_min"] * h)
            dx2, dy2 = int(bx["x_max"] * w), int(bx["y_max"] * h)
            cv2.rectangle(annotated, (dx1, dy1), (dx2, dy2), color_rgb, 2)
            cv2.rectangle(defect_mask_canvas, (dx1, dy1), (dx2, dy2), (80, 80, 80), 1)

            d_label = f"#{d.get('defect_id', 0)} {defect_type.upper()} [{d.get('pixel_area', 0)}px]"
            cv2.putText(
                annotated,
                d_label,
                (dx1, max(18, dy1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color_rgb,
                2,
                cv2.LINE_AA,
            )
            cv2.putText(
                defect_mask_canvas,
                d_label,
                (dx1, max(18, dy1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                color_rgb,
                1,
                cv2.LINE_AA,
            )

    return annotated, defect_mask_canvas


def inspect_frame(
    image: np.ndarray | None,
    model_choice: str,
    conf_threshold: float,
    grade_a_tol: float,
    grade_b_tol: float,
    history_state: list[list[Any]] | None,
) -> tuple[
    np.ndarray | None,
    np.ndarray | None,
    str,
    list[list[Any]],
    list[list[Any]],
]:
    """Execute complete end-to-end inspection pipeline for the Gradio interface.

    Args:
        image: Captured optical frame as RGB NumPy array.
        model_choice: Selected inference model precision name.
        conf_threshold: Confidence filtering threshold (0.1 - 1.0).
        grade_a_tol: Maximum defect ratio percentage for Grade A pass.
        grade_b_tol: Maximum defect ratio percentage for Grade B pass.
        history_state: In-memory session audit history rows.

    Returns:
        Tuple of:
            - Semantic overlay image (H, W, 3).
            - Binary defect isolation image (H, W, 3).
            - KPI HUD HTML string.
            - Defect breakdown table rows.
            - Updated session audit history rows.
    """
    if history_state is None:
        history_state = []

    # Defensive check: empty or invalid image frame
    if image is None:
        empty_hud = """
        <div class="alert-box alert-reject">
            <strong>Awaiting Camera Capture:</strong> Upload an optical inspection frame or select a preset capture on the left.
        </div>
        """
        return None, None, empty_hud, [], history_state

    # Ensure 3-channel RGB image format
    if image.ndim == 2:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    elif image.shape[2] == 4:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    else:
        image_rgb = image.copy()

    # Load cached detector and initialize grader
    detector = get_detector(model_choice)
    grader = InspectionGrader(
        grade_a_threshold=grade_a_tol, grade_b_threshold=grade_b_tol
    )

    # Time end-to-end inference
    t0 = time.perf_counter()
    pred = detector.predict(image_rgb, confidence_threshold=conf_threshold)
    t_infer_ms = (time.perf_counter() - t0) * 1000.0

    # Evaluate quality grade
    grade, ratio, reject_reason = grader.evaluate(
        fruit_pixels=pred.get("fruit_pixel_area", 0),
        defect_pixels=pred.get("defect_pixel_area", 0),
        defect_types=pred.get("defect_types", []),
    )

    # Render visualizations
    annotated_img, defect_mask_img = draw_industrial_visualizations(image_rgb, pred)

    # Format KPI HUD
    kpi_html = render_kpi_hud(
        grade=grade,
        ratio=ratio,
        reject_reason=reject_reason,
        t_infer=t_infer_ms,
        fruit_pixels=pred.get("fruit_pixel_area", 0),
        defect_pixels=pred.get("defect_pixel_area", 0),
        grade_b_tol=grade_b_tol,
    )

    # Build Defect Breakdown Table
    defect_table_rows: list[list[Any]] = []
    for d in pred.get("defects", []):
        defect_type = d.get("defect_type", "defect").upper()
        conf = f"{d.get('confidence', 0.0):.1%}"
        area = d.get("pixel_area", 0)
        bx = d.get("bbox", {})
        loc = f"({bx.get('x_min', 0.0):.2f}, {bx.get('y_min', 0.0):.2f}) to ({bx.get('x_max', 0.0):.2f}, {bx.get('y_max', 0.0):.2f})"
        severity = "CRITICAL (ZERO-TOLERANCE)" if "ROT" in defect_type else "COSMETIC"
        defect_table_rows.append(
            [
                d.get("defect_id", 1),
                defect_type,
                severity,
                conf,
                area,
                loc,
            ]
        )

    # Append to Session Audit History
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M:%S UTC")
    model_tag = "INT8" if "INT8" in model_choice else "FP32"
    grade_label = grade.value if hasattr(grade, "value") else str(grade)
    defect_count = len(pred.get("defects", []))

    new_history = [
        [
            timestamp,
            model_tag,
            grade_label,
            f"{ratio:.2f}%",
            defect_count,
            f"{t_infer_ms:.1f} ms",
            reject_reason or "PASS",
        ]
    ] + history_state[
        :49
    ]  # Keep latest 50 logs

    return annotated_img, defect_mask_img, kpi_html, defect_table_rows, new_history


def load_preset_image(preset_name: str) -> np.ndarray | None:
    """Load sample image array from preset selection.

    Args:
        preset_name: Key from PRESET_SAMPLES.

    Returns:
        RGB NumPy array or None if not found.
    """
    if preset_name not in PRESET_SAMPLES:
        return None

    path_str = PRESET_SAMPLES[preset_name]
    path = Path(path_str)
    if not path.exists():
        return None

    pil_img = Image.open(path).convert("RGB")
    return np.array(pil_img)


def build_gradio_app() -> gr.Blocks:
    """Build and configure declarative Gradio application workspace.

    Returns:
        gr.Blocks application instance.
    """
    with gr.Blocks(title="Food Defect AOI Inspector") as demo:
        audit_history_state = gr.State(value=[])

        # Compact Industrial Header
        gr.HTML(render_html_header())

        with gr.Row():
            # LEFT COLUMN: Conveyor Controls & Calibration
            with gr.Column(scale=4):
                with gr.Group():
                    gr.Markdown("### Conveyor Camera Feed")

                    preset_dropdown = gr.Dropdown(
                        choices=["None (Use Camera / Upload)"]
                        + list(PRESET_SAMPLES.keys()),
                        value="None (Use Camera / Upload)",
                        label="Preset Conveyor Capture",
                    )

                    camera_input = gr.Image(
                        label="Optical Frame Input",
                        type="numpy",
                        sources=["upload", "clipboard", "webcam"],
                    )

                with gr.Group():
                    gr.Markdown("### Sorting Calibration")

                    model_dropdown = gr.Dropdown(
                        choices=[
                            "YOLOv8s-seg FP32 (Production - 45.2 MB)",
                            "YOLOv8s-seg INT8 (Quantized - 11.8 MB)",
                        ],
                        value="YOLOv8s-seg FP32 (Production - 45.2 MB)",
                        label="Model Precision",
                    )

                    confidence_slider = gr.Slider(
                        minimum=0.10,
                        maximum=1.00,
                        value=0.35,
                        step=0.05,
                        label="Confidence Threshold",
                    )

                    with gr.Row():
                        grade_a_slider = gr.Slider(
                            minimum=0.0,
                            maximum=3.0,
                            value=1.0,
                            step=0.1,
                            label="Grade A Max Defect (%)",
                        )
                        grade_b_slider = gr.Slider(
                            minimum=1.0,
                            maximum=10.0,
                            value=5.0,
                            step=0.5,
                            label="Grade B Max Defect (%)",
                        )

                with gr.Row():
                    inspect_btn = gr.Button(
                        "Run Inspection",
                        variant="primary",
                        size="lg",
                    )
                    clear_btn = gr.Button("Reset", size="lg")

            # RIGHT COLUMN: Viewports & Telemetry HUD
            with gr.Column(scale=6):
                # Real-Time KPI HUD Container
                kpi_hud = gr.HTML(value="""
                    <div class="kpi-card" style="text-align: center; padding: 20px;">
                        <span style="color: var(--text-secondary); font-size: 0.95rem;">
                            Awaiting camera capture. Select a conveyor capture preset or upload an optical image.
                        </span>
                    </div>
                    """)

                # Color Legend Bar
                gr.HTML(render_visual_legend())

                # Viewport Tabs
                with gr.Tabs():
                    with gr.TabItem("Semantic Defect Overlay"):
                        overlay_output = gr.Image(
                            label="Multi-Layer Segmentation Overlay",
                            interactive=False,
                            show_label=True,
                        )
                    with gr.TabItem("Binary Defect Mask"):
                        mask_output = gr.Image(
                            label="Isolated Defect Mask",
                            interactive=False,
                            show_label=True,
                        )

                # Defect Quantification Details Table
                with gr.Accordion("Defect Quantification Breakdown", open=True):
                    defect_table = gr.Dataframe(
                        headers=[
                            "ID",
                            "Type",
                            "Severity",
                            "Confidence",
                            "Pixel Area",
                            "Coordinates (Norm)",
                        ],
                        datatype=["number", "str", "str", "str", "number", "str"],
                        interactive=False,
                        wrap=True,
                    )

                # Session Audit Log
                with gr.Accordion("Session Inspection Audit Log", open=False):
                    audit_table = gr.Dataframe(
                        headers=[
                            "Time",
                            "Precision",
                            "Grade",
                            "Defect Ratio",
                            "Defect Count",
                            "Latency",
                            "Reason",
                        ],
                        datatype=["str", "str", "str", "str", "number", "str", "str"],
                        interactive=False,
                        wrap=True,
                    )

        # Reactive Event Bindings
        # 1. Preset dropdown loads image
        preset_dropdown.change(
            fn=load_preset_image,
            inputs=[preset_dropdown],
            outputs=[camera_input],
        )

        # 2. When camera input changes, trigger automatic inspection
        camera_input.change(
            fn=inspect_frame,
            inputs=[
                camera_input,
                model_dropdown,
                confidence_slider,
                grade_a_slider,
                grade_b_slider,
                audit_history_state,
            ],
            outputs=[
                overlay_output,
                mask_output,
                kpi_hud,
                defect_table,
                audit_history_state,
            ],
        ).then(
            fn=lambda hist: hist,
            inputs=[audit_history_state],
            outputs=[audit_table],
        )

        # 3. Sliders or model change trigger re-inspection
        for component in [
            model_dropdown,
            confidence_slider,
            grade_a_slider,
            grade_b_slider,
        ]:
            component.change(
                fn=inspect_frame,
                inputs=[
                    camera_input,
                    model_dropdown,
                    confidence_slider,
                    grade_a_slider,
                    grade_b_slider,
                    audit_history_state,
                ],
                outputs=[
                    overlay_output,
                    mask_output,
                    kpi_hud,
                    defect_table,
                    audit_history_state,
                ],
            ).then(
                fn=lambda hist: hist,
                inputs=[audit_history_state],
                outputs=[audit_table],
            )

        # 4. Manual Run button
        inspect_btn.click(
            fn=inspect_frame,
            inputs=[
                camera_input,
                model_dropdown,
                confidence_slider,
                grade_a_slider,
                grade_b_slider,
                audit_history_state,
            ],
            outputs=[
                overlay_output,
                mask_output,
                kpi_hud,
                defect_table,
                audit_history_state,
            ],
        ).then(
            fn=lambda hist: hist,
            inputs=[audit_history_state],
            outputs=[audit_table],
        )

        # 5. Clear button
        clear_btn.click(
            fn=lambda: (
                None,
                None,
                None,
                """
                <div class="kpi-card" style="text-align: center; padding: 20px;">
                    <span style="color: var(--text-secondary); font-size: 0.95rem;">
                        Inspection reset. Select a conveyor capture preset or upload an optical image.
                    </span>
                </div>
                """,
                [],
                "None (Use Camera / Upload)",
            ),
            inputs=[],
            outputs=[
                camera_input,
                overlay_output,
                mask_output,
                kpi_hud,
                defect_table,
                preset_dropdown,
            ],
        )

    return demo


def launch_app(
    host: str = "127.0.0.1",
    port: int = 7860,
    share: bool = False,
) -> None:
    """Launch the Gradio AOI dashboard application.

    Args:
        host: Network interface host to bind.
        port: Local port number.
        share: Whether to generate a public Hugging Face share link.
    """
    theme = gr.themes.Soft(
        primary_hue="cyan",
        secondary_hue="blue",
        neutral_hue="slate",
    )
    app = build_gradio_app()
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        theme=theme,
        css=CUSTOM_CSS,
    )


if __name__ == "__main__":
    launch_app()
