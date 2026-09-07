"""Base detector interface and ONNX segmentation detector implementation."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar

import cv2
import numpy as np
from ultralytics import YOLO

from src.core.exceptions import InferenceError, ModelLoadError


class BaseDetector(ABC):
    """Abstract base detector for segmentation inference."""

    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """Load model weights or ONNX computational graph."""

    @abstractmethod
    def predict(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.40,
        iou_threshold: float = 0.45,
    ) -> dict[str, Any]:
        """Perform segmentation inference on an input RGB image."""


class ONNXDetector(BaseDetector):
    """Production ONNX Runtime segmentation detector."""

    FRUIT_CLASS_NAMES: ClassVar[set[str]] = {
        "apple",
        "banana",
        "orange",
        "fruit",
        "healthy",
        "fruit_body",
        "apple_good",
        "apple_moderate",
        "apple_bad",
    }
    DEFECT_CLASS_NAMES: ClassVar[set[str]] = {
        "rot",
        "bruise",
        "scab",
        "scratch",
        "defect",
        "defective",
        "critical_defect",
        "cosmetic_defect",
    }
    ANATOMICAL_CLASS_NAMES: ClassVar[set[str]] = {"stem_calyx", "stem", "calyx"}

    def __init__(self, model_path: str | None = None) -> None:
        """Initialize detector and optionally load model."""
        self.model: YOLO | None = None
        self.defect_expert: YOLO | None = None
        self.model_path: str | None = None
        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: str) -> None:
        """Load ONNX segmentation model.

        Args:
            model_path: Path to .onnx file.

        Raises:
            ModelLoadError: If file is missing or invalid.
        """
        path = Path(model_path)
        if not path.exists():
            raise ModelLoadError(f"ONNX model file not found at: {model_path}")
        try:
            self.model = YOLO(str(path), task="segment")
            self.model_path = str(path)
            # Load Stage-2 Defect Specialist if available in models/onnx
            expert_path = path.parent / "defect_expert_s.onnx"
            if not expert_path.exists():
                expert_path = Path(__file__).resolve().parent.parent.parent / "models" / "onnx" / "defect_expert_s.onnx"
            if expert_path.exists():
                try:
                    self.defect_expert = YOLO(str(expert_path), task="segment")
                except (FileNotFoundError, RuntimeError, ValueError, OSError):
                    self.defect_expert = None
        except Exception as e:
            raise ModelLoadError(f"Failed to load ONNX model: {e!s}") from e

    @staticmethod
    def normalize_surface_illumination(crop_rgb: np.ndarray) -> np.ndarray:
        """Apply CIELAB CLAHE normalization to remove 3D curvature shadows and glares.

        Args:
            crop_rgb: Cropped fruit RGB image.

        Returns:
            Illumination-normalized RGB image.
        """
        if crop_rgb.size == 0:
            return crop_rgb
        lab = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l_norm = clahe.apply(l_channel)
        norm_lab = cv2.merge((l_norm, a_channel, b_channel))
        return cv2.cvtColor(norm_lab, cv2.COLOR_LAB2RGB)

    def _extract_surface_anomalies(
        self,
        image_rgb: np.ndarray,
        fruit_mask: np.ndarray,
    ) -> tuple[np.ndarray, list[dict[str, Any]]]:
        """Detect surface blemishes (rot / bruise patches) on fruit mask.

        Uses CIELAB color-space delta and saturation anomalies within the segmented fruit.

        Args:
            image_rgb: Source RGB image.
            fruit_mask: Boolean mask of fruit body (H, W).

        Returns:
            Tuple of (Combined defect boolean mask, list of defect descriptor dicts).
        """
        if not np.any(fruit_mask):
            return np.zeros_like(fruit_mask, dtype=bool), []

        # Convert to LAB color space for perceptual luminance and chromaticity
        lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2LAB)
        l_channel, _a, _b = cv2.split(lab)

        # Fruit interior statistics
        fruit_l = l_channel[fruit_mask]
        mean_l = np.mean(fruit_l)
        std_l = np.std(fruit_l)

        # Anomaly mask: significantly darker regions (rot) or discolored bruising
        rot_mask = (l_channel < (mean_l - 1.8 * std_l)) & fruit_mask
        rot_mask = cv2.morphologyEx(
            rot_mask.astype(np.uint8),
            cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
        ).astype(bool)

        h, w = image_rgb.shape[:2]
        defects = []

        # Find connected defect contours
        contours, _ = cv2.findContours(
            rot_mask.astype(np.uint8),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        for i, cnt in enumerate(contours):
            area = int(cv2.contourArea(cnt))
            if area < 50:  # Ignore tiny micro-noise (< 50 pixels)
                rot_mask[
                    cv2.drawContours(np.zeros((h, w), dtype=np.uint8), [cnt], -1, 1, -1)
                    == 1
                ] = False
                continue

            x, y, bw, bh = cv2.boundingRect(cnt)
            # Normalize polygon coordinates
            polygon = [
                {"x": round(float(pt[0][0]) / w, 4), "y": round(float(pt[0][1]) / h, 4)}
                for pt in cnt
            ]

            # Categorize severity: very dark = rot, moderate = bruise
            cnt_mask = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(cnt_mask, [cnt], -1, 1, -1)
            defect_mean_l = np.mean(l_channel[cnt_mask == 1]) if np.any(cnt_mask) else 0

            defect_type = "rot" if defect_mean_l < (mean_l - 2.2 * std_l) else "bruise"

            defects.append(
                {
                    "defect_id": i + 1,
                    "defect_type": defect_type,
                    "confidence": 0.85,
                    "bbox": {
                        "x_min": round(x / w, 4),
                        "y_min": round(y / h, 4),
                        "x_max": round((x + bw) / w, 4),
                        "y_max": round((y + bh) / h, 4),
                    },
                    "polygon": polygon,
                    "pixel_area": area,
                }
            )

        return rot_mask, defects

    def predict(
        self,
        image: np.ndarray,
        confidence_threshold: float = 0.40,
        iou_threshold: float = 0.45,
        two_stage: bool = False,
    ) -> dict[str, Any]:
        """Perform segmentation and defect quantification.

        Args:
            image: Input RGB image (H, W, 3).
            confidence_threshold: Confidence threshold for fruit detection.
            iou_threshold: NMS IOU threshold.

        Returns:
            Structured dictionary with fruit details, defect lists, and pixel counts.
        """
        if self.model is None:
            raise InferenceError(
                "Detector model is not loaded. Call load_model() first."
            )

        h, w = image.shape[:2]
        # Ultralytics assumes BGR input arrays and performs internal BGR->RGB inversion
        bgr_input = (
            cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if (
                image.ndim == 3
                and image.shape[2] == 3
                and image.shape[0] > 1
                and image.shape[1] > 1
            )
            else image
        )
        # Candidate confidence threshold: query low to allow micro-defect detection
        candidate_conf = max(0.18, confidence_threshold * 0.55)
        results = self.model.predict(
            source=bgr_input,
            conf=candidate_conf,
            iou=iou_threshold,
            imgsz=640,
            verbose=False,
        )

        fruit_info: dict[str, Any] | None = None
        fruit_mask_combined = np.zeros((h, w), dtype=bool)
        defects_list: list[dict[str, Any]] = []

        if results and len(results) > 0:
            res = results[0]
            if res.masks is not None and res.boxes is not None:
                boxes = res.boxes
                masks = res.masks.data.cpu().numpy()  # (N, H_out, W_out)
                class_ids = boxes.cls.cpu().numpy().astype(int)
                confidences = boxes.conf.cpu().numpy()
                xyxy = boxes.xyxy.cpu().numpy()

                for i, (cls_id, conf, box) in enumerate(
                    zip(class_ids, confidences, xyxy, strict=False)
                ):
                    class_name = self.model.names.get(cls_id, "object").lower()

                    # Calibrated per-class filtering
                    if class_name == "apple_moderate":
                        min_conf = max(0.40, confidence_threshold * 1.15)
                    elif class_name in self.FRUIT_CLASS_NAMES:
                        min_conf = confidence_threshold
                    else:
                        min_conf = max(0.18, confidence_threshold * 0.55)
                    if conf < min_conf:
                        continue

                    # Resize mask to original image resolution
                    raw_mask = masks[i]
                    resized_mask = (
                        cv2.resize(raw_mask, (w, h), interpolation=cv2.INTER_LINEAR)
                        > 0.5
                    )

                    # Check if this is a fruit object
                    if class_name in self.FRUIT_CLASS_NAMES:
                        fruit_mask_combined |= resized_mask
                        x1, y1, x2, y2 = box

                        # Extract contour polygon for fruit
                        contours, _ = cv2.findContours(
                            resized_mask.astype(np.uint8),
                            cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE,
                        )
                        fruit_poly = []
                        if contours:
                            largest_cnt = max(contours, key=cv2.contourArea)
                            fruit_poly = [
                                {
                                    "x": round(float(pt[0][0]) / w, 4),
                                    "y": round(float(pt[0][1]) / h, 4),
                                }
                                for pt in largest_cnt
                            ]

                        fruit_px = int(np.sum(resized_mask))
                        is_healthy_produce = class_name in {"apple_good", "healthy"}
                        fruit_info = {
                            "fruit_id": 1,
                            "fruit_type": (
                                "apple" if "apple" in class_name else class_name
                            ),
                            "confidence": round(float(conf), 4),
                            "bbox": {
                                "x_min": round(float(x1) / w, 4),
                                "y_min": round(float(y1) / h, 4),
                                "x_max": round(float(x2) / w, 4),
                                "y_max": round(float(y2) / h, 4),
                            },
                            "polygon": fruit_poly,
                            "pixel_area": fruit_px,
                            "is_healthy": is_healthy_produce,
                        }

                        # Single model produce direct grading mapping
                        if class_name == "apple_bad":
                            defects_list.append(
                                {
                                    "defect_id": len(defects_list) + 1,
                                    "defect_type": "critical_defect",
                                    "confidence": round(float(conf), 4),
                                    "bbox": fruit_info["bbox"],
                                    "polygon": fruit_poly,
                                    "pixel_area": int(fruit_px * 0.15),
                                }
                            )
                        elif class_name == "apple_moderate":
                            defects_list.append(
                                {
                                    "defect_id": len(defects_list) + 1,
                                    "defect_type": "cosmetic_defect",
                                    "confidence": round(float(conf), 4),
                                    "bbox": fruit_info["bbox"],
                                    "polygon": fruit_poly,
                                    "pixel_area": int(fruit_px * 0.03),
                                }
                            )

                    # Check if trained model predicted defect class directly
                    elif class_name in self.DEFECT_CLASS_NAMES:
                        # Spatial intersection: defect must reside on fruit body
                        if np.any(fruit_mask_combined):
                            valid_defect_mask = resized_mask & fruit_mask_combined
                        else:
                            valid_defect_mask = resized_mask

                        defect_area = int(np.sum(valid_defect_mask))
                        if defect_area < 30:
                            continue  # Suppress tiny noise or background artifacts

                        x1, y1, x2, y2 = box
                        contours, _ = cv2.findContours(
                            valid_defect_mask.astype(np.uint8),
                            cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE,
                        )
                        defect_poly = []
                        if contours:
                            largest_cnt = max(contours, key=cv2.contourArea)
                            defect_poly = [
                                {
                                    "x": round(float(pt[0][0]) / w, 4),
                                    "y": round(float(pt[0][1]) / h, 4),
                                }
                                for pt in largest_cnt
                            ]

                        defects_list.append(
                            {
                                "defect_id": len(defects_list) + 1,
                                "defect_type": class_name,
                                "confidence": round(float(conf), 4),
                                "bbox": {
                                    "x_min": round(float(x1) / w, 4),
                                    "y_min": round(float(y1) / h, 4),
                                    "x_max": round(float(x2) / w, 4),
                                    "y_max": round(float(y2) / h, 4),
                                },
                                "polygon": defect_poly,
                                "pixel_area": defect_area,
                            }
                        )

        # Stage 2: High-Resolution Zoom & Surface Illumination Normalization
        if two_stage and fruit_info is not None:
            fb = fruit_info["bbox"]
            fx1, fy1 = int(fb["x_min"] * w), int(fb["y_min"] * h)
            fx2, fy2 = int(fb["x_max"] * w), int(fb["y_max"] * h)
            pad_x = int(0.05 * (fx2 - fx1))
            pad_y = int(0.05 * (fy2 - fy1))
            cx1 = max(0, fx1 - pad_x)
            cy1 = max(0, fy1 - pad_y)
            cx2 = min(w, fx2 + pad_x)
            cy2 = min(h, fy2 + pad_y)
            crop_w, crop_h = cx2 - cx1, cy2 - cy1

            # Only zoom if fruit occupies a sub-region
            if (
                crop_w > 50
                and crop_h > 50
                and (crop_w < int(w * 0.92) or crop_h < int(h * 0.92))
            ):
                fruit_crop = image[cy1:cy2, cx1:cx2]
                norm_crop = self.normalize_surface_illumination(fruit_crop)
                norm_crop_bgr = (
                    cv2.cvtColor(norm_crop, cv2.COLOR_RGB2BGR)
                    if (norm_crop.ndim == 3 and norm_crop.shape[2] == 3)
                    else norm_crop
                )
                defect_model = (
                    self.defect_expert if self.defect_expert is not None else self.model
                )
                crop_res = defect_model.predict(
                    source=norm_crop_bgr,
                    conf=max(0.18, confidence_threshold * 0.75),
                    iou=iou_threshold,
                    imgsz=640,
                    verbose=False,
                )
                if crop_res and len(crop_res) > 0 and crop_res[0].masks is not None:
                    c_res = crop_res[0]
                    c_boxes = c_res.boxes
                    c_masks = c_res.masks.data.cpu().numpy()
                    c_classes = c_boxes.cls.cpu().numpy().astype(int)
                    c_confs = c_boxes.conf.cpu().numpy()
                    c_xyxy = c_boxes.xyxy.cpu().numpy()

                    for c_cls, c_conf, c_box, c_mask in zip(
                        c_classes, c_confs, c_xyxy, c_masks, strict=False
                    ):
                        c_name = defect_model.names.get(c_cls, "object").lower()
                        if c_name in self.DEFECT_CLASS_NAMES:
                            # Remap mask to global coordinate system
                            crop_mask_full = np.zeros((h, w), dtype=bool)
                            local_mask_resized = (
                                cv2.resize(
                                    c_mask,
                                    (crop_w, crop_h),
                                    interpolation=cv2.INTER_NEAREST,
                                )
                                > 0.5
                            )
                            crop_mask_full[cy1:cy2, cx1:cx2] = local_mask_resized

                            # Strict spatial intersection with fruit body
                            valid_crop_defect = crop_mask_full & fruit_mask_combined
                            defect_area = int(np.sum(valid_crop_defect))
                            if defect_area < 30:
                                continue

                            # Check overlap with existing defects to prevent duplicate counting
                            overlap = False
                            for existing in defects_list:
                                ex_b = existing["bbox"]
                                b1 = [
                                    c_box[0] + cx1,
                                    c_box[1] + cy1,
                                    c_box[2] + cx1,
                                    c_box[3] + cy1,
                                ]
                                b2 = [
                                    ex_b["x_min"] * w,
                                    ex_b["y_min"] * h,
                                    ex_b["x_max"] * w,
                                    ex_b["y_max"] * h,
                                ]
                                x_l = max(b1[0], b2[0])
                                y_t = max(b1[1], b2[1])
                                x_r = min(b1[2], b2[2])
                                y_b = min(b1[3], b2[3])
                                if x_r > x_l and y_b > y_t:
                                    inter = (x_r - x_l) * (y_b - y_t)
                                    a1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
                                    a2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
                                    iou = inter / float(a1 + a2 - inter + 1e-6)
                                    if iou > 0.3:
                                        overlap = True
                                        break
                            if overlap:
                                continue

                            gx1, gy1 = c_box[0] + cx1, c_box[1] + cy1
                            gx2, gy2 = c_box[2] + cx1, c_box[3] + cy1
                            contours, _ = cv2.findContours(
                                valid_crop_defect.astype(np.uint8),
                                cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE,
                            )
                            defect_poly = []
                            if contours:
                                largest_cnt = max(contours, key=cv2.contourArea)
                                defect_poly = [
                                    {
                                        "x": round(float(pt[0][0]) / w, 4),
                                        "y": round(float(pt[0][1]) / h, 4),
                                    }
                                    for pt in largest_cnt
                                ]

                            defects_list.append(
                                {
                                    "defect_id": len(defects_list) + 1,
                                    "defect_type": c_name,
                                    "confidence": round(float(c_conf), 4),
                                    "bbox": {
                                        "x_min": round(float(gx1) / w, 4),
                                        "y_min": round(float(gy1) / h, 4),
                                        "x_max": round(float(gx2) / w, 4),
                                        "y_max": round(float(gy2) / h, 4),
                                    },
                                    "polygon": defect_poly,
                                    "pixel_area": defect_area,
                                }
                            )

        # If model is baseline without explicit defect classes, analyze surface anomalies on fruit
        is_healthy = fruit_info.get("is_healthy", False) if fruit_info else False
        if fruit_info is not None and not defects_list and not is_healthy:
            _defect_mask, anomalies = self._extract_surface_anomalies(
                image, fruit_mask_combined
            )
            defects_list = anomalies

        # If no fruit body exists in frame, suppress all defects (zero false positives on empty belt)
        if fruit_info is None:
            defects_list = []

        total_defect_pixels = sum(d["pixel_area"] for d in defects_list)
        total_fruit_pixels = fruit_info["pixel_area"] if fruit_info else 0

        return {
            "fruit": fruit_info,
            "defects": defects_list,
            "fruit_pixel_area": total_fruit_pixels,
            "defect_pixel_area": total_defect_pixels,
            "defect_types": [d["defect_type"] for d in defects_list],
        }
