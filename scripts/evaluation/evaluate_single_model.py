"""Comprehensive Test Set Evaluation for Single YOLOv8s-seg Produce Sorting Model.

Evaluates ONNX detector on the 253 unseen test images (231 produce + 22 negative conveyor frames)
measuring overall grading accuracy, per-class recall/precision, empty belt false alarm rate, and latency.
"""

import json
import sys
import time
from pathlib import Path
from typing import Any

import cv2

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.core.detector import ONNXDetector
from src.core.grader import InspectionGrade, InspectionGrader

TEST_IMG_DIR = BASE_DIR / "data" / "roboflow_kuka" / "test" / "images"
TEST_LBL_DIR = BASE_DIR / "data" / "roboflow_kuka" / "test" / "labels"
ONNX_MODEL_PATH = BASE_DIR / "models" / "onnx" / "best_s.onnx"
REPORT_OUTPUT = BASE_DIR / "reports" / "test_set_evaluation.json"


def get_ground_truth_grade(img_file: Path) -> tuple[InspectionGrade, str]:
    """Determine ground truth grade from filename or label file.

    Args:
        img_file: Image path in test set.

    Returns:
        Tuple of (InspectionGrade, ground_truth_class_name).
    """
    if "neg_" in img_file.name or "conveyor_neg" in img_file.name:
        return InspectionGrade.NO_OBJECT, "empty_conveyor"

    lbl_file = TEST_LBL_DIR / f"{img_file.stem}.txt"
    if not lbl_file.exists():
        return InspectionGrade.NO_OBJECT, "empty_conveyor"

    with open(lbl_file, "r", encoding="utf-8") as f:
        lines = [line.strip().split() for line in f if line.strip()]

    if not lines:
        return InspectionGrade.NO_OBJECT, "empty_conveyor"

    # Identify dominant class in image
    class_ids = [int(l[0]) for l in lines]
    # Priority: Bad (Reject) > Moderate (Grade B) > Good (Grade A)
    if 0 in class_ids:
        return InspectionGrade.REJECT, "apple_bad"
    elif 2 in class_ids:
        return InspectionGrade.GRADE_B, "apple_moderate"
    elif 1 in class_ids:
        return InspectionGrade.GRADE_A, "apple_good"
    else:
        return InspectionGrade.GRADE_A, "apple_good"


def evaluate_test_set(
    model_path: Path = ONNX_MODEL_PATH,
    confidence_threshold: float = 0.35,
) -> dict[str, Any]:
    """Run full test set evaluation.

    Args:
        model_path: Path to ONNX model.
        confidence_threshold: Detector confidence cutoff.

    Returns:
        Evaluation summary metrics dictionary.
    """
    if not model_path.exists():
        raise FileNotFoundError(f"ONNX model missing at: {model_path}")

    detector = ONNXDetector(str(model_path))
    grader = InspectionGrader()

    test_images = list(TEST_IMG_DIR.glob("*.*"))
    print(
        f"Evaluating {len(test_images)} unseen test images using {model_path.name}..."
    )

    latencies: list[float] = []
    matrix = {
        gt.value: {pred.value: 0 for pred in InspectionGrade} for gt in InspectionGrade
    }

    correct = 0
    total = len(test_images)

    for i, img_path in enumerate(test_images):
        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            continue
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        gt_grade, _gt_class = get_ground_truth_grade(img_path)

        start = time.perf_counter()
        pred_res = detector.predict(
            img_rgb, confidence_threshold=confidence_threshold, two_stage=False
        )
        lat = (time.perf_counter() - start) * 1000.0
        latencies.append(lat)

        fruit = pred_res.get("fruit")
        defects = pred_res.get("defects", [])

        if fruit is None:
            pred_grade = InspectionGrade.NO_OBJECT
        else:
            fruit_px = fruit.get("pixel_area", 0)
            defect_px = sum(d.get("pixel_area", 0) for d in defects)
            defect_types = [d.get("defect_type", "") for d in defects]
            pred_grade, _, _ = grader.evaluate(fruit_px, defect_px, defect_types)

        matrix[gt_grade.value][pred_grade.value] += 1
        if pred_grade == gt_grade:
            correct += 1

    overall_acc = (correct / total) * 100.0 if total > 0 else 0.0
    avg_lat = sum(latencies) / len(latencies) if latencies else 0.0

    # Negative belt false alarm rate
    total_negatives = sum(matrix[InspectionGrade.NO_OBJECT.value].values())
    neg_correct = matrix[InspectionGrade.NO_OBJECT.value][
        InspectionGrade.NO_OBJECT.value
    ]
    neg_false_alarms = total_negatives - neg_correct
    false_alarm_rate = (
        (neg_false_alarms / total_negatives) * 100.0 if total_negatives > 0 else 0.0
    )

    summary = {
        "total_test_images": total,
        "overall_accuracy_pct": round(overall_acc, 2),
        "avg_latency_ms": round(avg_lat, 2),
        "false_alarm_rate_pct": round(false_alarm_rate, 2),
        "confusion_matrix": matrix,
    }

    print("\n" + "=" * 65)
    print("TEST SET EVALUATION SUMMARY")
    print("=" * 65)
    print(f"Overall Accuracy:       {overall_acc:.2f}% ({correct}/{total})")
    print(
        f"Empty Belt False Alarms: {false_alarm_rate:.2f}% ({neg_false_alarms}/{total_negatives})"
    )
    print(f"Average GPU Latency:    {avg_lat:.2f} ms")
    print("=" * 65)

    REPORT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved evaluation report to: {REPORT_OUTPUT}")

    return summary


if __name__ == "__main__":
    evaluate_test_set()
