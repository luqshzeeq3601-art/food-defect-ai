"""Streamlit Operator Dashboard for Automated Optical Inspection (AOI)."""

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import cv2
import numpy as np
import streamlit as st
from PIL import Image

from src.core.detector import ONNXDetector
from src.core.grader import InspectionGrade, InspectionGrader

st.set_page_config(
    page_title="Food Defect AOI Inspector",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header { font-size: 2.1rem; font-weight: 700; color: #0F172A; margin-bottom: 0.1rem; }
    .sub-header { font-size: 1.0rem; color: #475569; margin-bottom: 1.2rem; }
    .badge-pass { background-color: #DCFCE7; color: #15803D; padding: 6px 14px; border-radius: 8px; font-weight: 700; font-size: 1.1rem; display: inline-block; }
    .badge-warn { background-color: #FEF3C7; color: #B45309; padding: 6px 14px; border-radius: 8px; font-weight: 700; font-size: 1.1rem; display: inline-block; }
    .badge-reject { background-color: #FEE2E2; color: #B91C1C; padding: 6px 14px; border-radius: 8px; font-weight: 700; font-size: 1.1rem; display: inline-block; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="main-header">Automated Optical Inspection (AOI) - Food Defect Sorting</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Industrial Machine Vision Pipeline • YOLOv8-seg • ONNX Runtime Acceleration</div>',
    unsafe_allow_html=True,
)


@st.cache_resource
def load_detector(model_choice: str) -> ONNXDetector:
    if "INT8" in model_choice:
        model_path = BASE_DIR / "models" / "onnx" / "best_s_int8.onnx"
    else:
        model_path = BASE_DIR / "models" / "onnx" / "best_s.onnx"

    if not model_path.exists():
        st.error(f"Model file not found: {model_path}")
        st.stop()
    return ONNXDetector(str(model_path))


# Sidebar Controls
with st.sidebar:
    st.header("⚙️ AOI Calibration")
    model_choice = st.selectbox(
        "Inference Model (GPU Trained)",
        [
            "YOLOv8s-seg FP32 (Production - 45.2 MB)",
            "YOLOv8s-seg INT8 (Quantized - 11.8 MB)",
        ],
    )
    grade_a_tol = st.slider("Grade A Max Defect (%)", 0.0, 3.0, 1.0, 0.1)
    grade_b_tol = st.slider("Grade B Max Defect (%)", 1.0, 10.0, 5.0, 0.5)
    conf_threshold = st.slider("Detection Confidence", 0.10, 1.00, 0.35, 0.05)

    st.divider()
    st.markdown("**Select Sample Frame:**")
    sample_files = {
        "Defective Fruit (Dataset Test)": str(BASE_DIR / "data/samples/dataset_defective_fruit.jpg"),
        "Healthy Fruit (Dataset Test)": str(BASE_DIR / "data/samples/dataset_healthy_fruit.jpg"),
        "Empty Conveyor Belt (Negative Test)": str(BASE_DIR / "data/samples/negative_backgrounds/conveyor_empty_01.jpg"),
        "Defective Apple (Rot Simulated)": str(BASE_DIR / "data/samples/defective_apple_rot.jpg"),
        "Healthy Apple": str(BASE_DIR / "data/samples/real_apple.jpg"),
        "Healthy Orange": str(BASE_DIR / "data/samples/real_orange.jpg"),
        "Healthy Banana": str(BASE_DIR / "data/samples/real_banana.jpg"),
    }
    selected_sample = st.selectbox(
        "Preset Conveyor Capture", ["None (Use Upload)"] + list(sample_files.keys())
    )

    st.divider()
    st.markdown("**Simulated Station:** `ViTrox Inspec-Belt #01`")
    st.markdown(
        f"**Model Footprint:** `{'3.52 MB (INT8)' if 'INT8' in model_choice else '12.67 MB (FP32)'}`"
    )
    st.markdown("**Runtime Provider:** `CPUExecutionProvider (ONNX)`")

detector = load_detector(model_choice)
grader = InspectionGrader(grade_a_threshold=grade_a_tol, grade_b_threshold=grade_b_tol)

# Load target image
target_image = None
if selected_sample != "None (Use Upload)":
    sample_path = sample_files[selected_sample]
    if Path(sample_path).exists():
        target_image = Image.open(sample_path)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📷 Optical Camera Feed")
    uploaded_file = st.file_uploader(
        "Upload Camera Image",
        type=["jpg", "jpeg", "png", "bmp"],
        help="Upload an image to inspect",
    )
    if uploaded_file is not None:
        target_image = Image.open(uploaded_file)

    if target_image:
        st.image(
            target_image, caption="Raw Captured Frame (Conveyor)", use_column_width=True
        )
    else:
        st.info(
            "Awaiting optical frame. Upload an image or select a sample preset on the left."
        )

with col2:
    st.subheader("🔬 AI Segmentation & Grading Analysis")
    if target_image:
        # Prepare RGB image
        img_np = np.array(target_image.convert("RGB"))
        h, w = img_np.shape[:2]

        # Run ONNX inference with timing
        t0 = time.perf_counter()
        pred = detector.predict(img_np, confidence_threshold=conf_threshold)
        t_infer = (time.perf_counter() - t0) * 1000.0

        # Evaluate Grade
        grade, ratio, reject_reason = grader.evaluate(
            fruit_pixels=pred["fruit_pixel_area"],
            defect_pixels=pred["defect_pixel_area"],
            defect_types=pred["defect_types"],
        )

        # Draw visual overlay
        annotated = img_np.copy()
        if pred["fruit"]:
            f = pred["fruit"]
            bx1, by1 = int(f["bbox"]["x_min"] * w), int(f["bbox"]["y_min"] * h)
            bx2, by2 = int(f["bbox"]["x_max"] * w), int(f["bbox"]["y_max"] * h)
            cv2.rectangle(annotated, (bx1, by1), (bx2, by2), (0, 220, 0), 2)
            cv2.putText(
                annotated,
                f"{f['fruit_type'].upper()} ({f['confidence']:.2f})",
                (bx1, max(20, by1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 220, 0),
                2,
            )

        for d in pred["defects"]:
            dx1, dy1 = int(d["bbox"]["x_min"] * w), int(d["bbox"]["y_min"] * h)
            dx2, dy2 = int(d["bbox"]["x_max"] * w), int(d["bbox"]["y_max"] * h)
            color = (230, 30, 30) if d["defect_type"] == "rot" else (240, 140, 20)
            cv2.rectangle(annotated, (dx1, dy1), (dx2, dy2), color, 2)
            cv2.putText(
                annotated,
                f"{d['defect_type'].upper()} [{d['pixel_area']}px]",
                (dx1, max(20, dy1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

        # KPI Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            if grade == InspectionGrade.GRADE_A:
                st.markdown(
                    '<div class="badge-pass">PASS (GRADE A)</div>',
                    unsafe_allow_html=True,
                )
            elif grade == InspectionGrade.GRADE_B:
                st.markdown(
                    '<div class="badge-warn">PASS (GRADE B)</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="badge-reject">REJECT</div>', unsafe_allow_html=True
                )
        with m2:
            st.metric(
                "Defect Ratio", f"{ratio}%", delta=f"{ratio - grade_b_tol:.1f}% vs tol"
            )
        with m3:
            st.metric("ONNX Latency", f"{t_infer:.1f} ms", delta="Optimized")
        with m4:
            fps = 1000.0 / max(1.0, t_infer)
            st.metric("Throughput", f"{fps:.0f} FPS")

        if reject_reason:
            st.error(f"Rejection Reason: {reject_reason}")
        else:
            st.success("Inspection Passed: Surface quality meets specifications.")

        st.image(
            annotated,
            caption="Segmented Defect Overlay (Polygons + Bounding Boxes)",
            use_column_width=True,
        )

        # Defects Breakdown Table
        if pred["defects"]:
            st.markdown("### Defect Details")
            table_data = [
                {
                    "Defect ID": d["defect_id"],
                    "Type": d["defect_type"].upper(),
                    "Confidence": f"{d['confidence']:.2%}",
                    "Pixel Area": d["pixel_area"],
                    "Location": f"({d['bbox']['x_min']:.2f}, {d['bbox']['y_min']:.2f})",
                }
                for d in pred["defects"]
            ]
            st.dataframe(table_data, use_container_width=True)
        else:
            st.info("Zero defects identified on product surface.")
    else:
        st.write(
            "Live analysis and segmented defect overlay will appear here upon frame capture."
        )
