"""FastAPI application for Food Defect AOI inference."""

import base64
import time
import uuid
from datetime import datetime, timezone

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.schemas import (
    BoundingBox,
    DetectedDefect,
    DetectedFruit,
    HealthResponse,
    InspectionResponse,
    InspectionTiming,
    PolygonPoint,
)
from src.core.config import settings
from src.core.detector import ONNXDetector
from src.core.grader import InspectionGrader

app = FastAPI(
    title=settings.APP_NAME,
    description="High-Speed Automated Optical Inspection (AOI) Pipeline for Food Defect Sorting",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Grader & ONNX Detectors
grader = InspectionGrader(
    grade_a_threshold=settings.GRADE_A_THRESHOLD_PERCENT,
    grade_b_threshold=settings.GRADE_B_THRESHOLD_PERCENT,
)

detector_fp32: ONNXDetector | None = None
if settings.DEFAULT_ONNX_MODEL.exists():
    detector_fp32 = ONNXDetector(str(settings.DEFAULT_ONNX_MODEL))

detector_int8: ONNXDetector | None = None
if settings.QUANTIZED_ONNX_MODEL.exists():
    detector_int8 = ONNXDetector(str(settings.QUANTIZED_ONNX_MODEL))


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check service health and model availability."""
    is_loaded = detector_fp32 is not None and detector_fp32.model is not None
    return HealthResponse(
        status="healthy" if is_loaded else "degraded",
        model_loaded=is_loaded,
        execution_provider="CPUExecutionProvider",
        version="0.2.0",
    )


@app.post("/api/v1/inspect", response_model=InspectionResponse)
async def inspect_food_item(
    file: UploadFile = File(  # noqa: B008
        ..., description="Target image file (JPEG, PNG, BMP)"
    ),
    precision: str = Query(
        default="fp32", description="Inference precision: 'fp32' or 'int8'"
    ),
    return_overlay: bool = Query(
        default=True, description="Whether to return annotated base64 overlay"
    ),
) -> InspectionResponse:
    """Inspect food item for defects and return quality grade."""
    start_time = time.perf_counter()

    # MIME type validation (Security.md)
    if file.content_type not in ["image/jpeg", "image/png", "image/bmp"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported image format. Allowed formats: JPEG, PNG, BMP.",
        )

    # Read bytes with file size guard
    image_bytes = await file.read()
    if len(image_bytes) > settings.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size exceeds limit of {settings.MAX_IMAGE_SIZE_BYTES // (1024*1024)}MB.",
        )

    # Decode image to numpy array
    t_pre_start = time.perf_counter()
    nparr = np.frombuffer(image_bytes, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image_bgr is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not decode image file.",
        )
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w = image_rgb.shape[:2]
    preprocess_ms = (time.perf_counter() - t_pre_start) * 1000.0

    active_detector = (
        detector_int8
        if precision.lower() == "int8" and detector_int8 is not None
        else detector_fp32
    )
    if active_detector is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Requested ONNX model ({precision.upper()}) is not loaded.",
        )

    # Inference execution (calibrated confidence threshold for INT8 quantization)
    t_infer_start = time.perf_counter()
    active_conf = 0.15 if precision.lower() == "int8" else settings.CONFIDENCE_THRESHOLD
    pred = active_detector.predict(
        image_rgb,
        confidence_threshold=active_conf,
        iou_threshold=settings.IOU_THRESHOLD,
    )
    inference_ms = (time.perf_counter() - t_infer_start) * 1000.0

    # Grading rule engine
    t_grade_start = time.perf_counter()
    grade, ratio, reject_reason = grader.evaluate(
        fruit_pixels=pred["fruit_pixel_area"],
        defect_pixels=pred["defect_pixel_area"],
        defect_types=pred["defect_types"],
    )
    grading_ms = (time.perf_counter() - t_grade_start) * 1000.0

    # Optional annotated overlay creation
    t_post_start = time.perf_counter()
    overlay_b64: str | None = None
    if return_overlay:
        annotated_rgb = image_rgb.copy()
        # Draw fruit contours/boxes
        if pred["fruit"]:
            f = pred["fruit"]
            bx1, by1 = int(f["bbox"]["x_min"] * w), int(f["bbox"]["y_min"] * h)
            bx2, by2 = int(f["bbox"]["x_max"] * w), int(f["bbox"]["y_max"] * h)
            cv2.rectangle(annotated_rgb, (bx1, by1), (bx2, by2), (0, 220, 0), 2)
            cv2.putText(
                annotated_rgb,
                f"{f['fruit_type'].upper()} ({f['confidence']:.2f})",
                (bx1, max(20, by1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 220, 0),
                2,
            )

        # Draw defect contours/boxes
        for d in pred["defects"]:
            dx1, dy1 = int(d["bbox"]["x_min"] * w), int(d["bbox"]["y_min"] * h)
            dx2, dy2 = int(d["bbox"]["x_max"] * w), int(d["bbox"]["y_max"] * h)
            color = (230, 30, 30) if d["defect_type"] == "rot" else (240, 140, 20)
            cv2.rectangle(annotated_rgb, (dx1, dy1), (dx2, dy2), color, 2)
            cv2.putText(
                annotated_rgb,
                f"{d['defect_type'].upper()} [{d['pixel_area']}px]",
                (dx1, max(20, dy1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

        # Encode overlay to JPEG base64
        annotated_bgr = cv2.cvtColor(annotated_rgb, cv2.COLOR_RGB2BGR)
        _, buffer = cv2.imencode(".jpg", annotated_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
        overlay_b64 = base64.b64encode(buffer).decode("utf-8")

    postprocess_ms = (time.perf_counter() - t_post_start) * 1000.0
    total_ms = (time.perf_counter() - start_time) * 1000.0

    # Format fruit Pydantic model
    fruit_obj = None
    if pred["fruit"]:
        fruit_obj = DetectedFruit(
            fruit_id=pred["fruit"]["fruit_id"],
            fruit_type=pred["fruit"]["fruit_type"],
            confidence=pred["fruit"]["confidence"],
            bbox=BoundingBox(**pred["fruit"]["bbox"]),
            polygon=[PolygonPoint(**p) for p in pred["fruit"]["polygon"]],
            pixel_area=pred["fruit"]["pixel_area"],
        )

    # Format defect Pydantic models
    defects_obj = [
        DetectedDefect(
            defect_id=d["defect_id"],
            defect_type=d["defect_type"],
            confidence=d["confidence"],
            bbox=BoundingBox(**d["bbox"]),
            polygon=[PolygonPoint(**p) for p in d["polygon"]],
            pixel_area=d["pixel_area"],
        )
        for d in pred["defects"]
    ]

    return InspectionResponse(
        inspection_id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        image_width=w,
        image_height=h,
        fruit=fruit_obj,
        defects=defects_obj,
        defect_ratio_percent=ratio,
        grade=grade,
        reject_reason=reject_reason,
        timing=InspectionTiming(
            preprocess_ms=round(preprocess_ms, 2),
            inference_ms=round(inference_ms, 2),
            postprocess_ms=round(postprocess_ms, 2),
            grading_ms=round(grading_ms, 2),
            total_ms=round(total_ms, 2),
        ),
        overlay_image_base64=overlay_b64,
    )


# Serve built modern web station if dist folder exists
frontend_dist = settings.FRONTEND_DIST
if frontend_dist.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(frontend_dist), html=True),
        name="frontend",
    )
