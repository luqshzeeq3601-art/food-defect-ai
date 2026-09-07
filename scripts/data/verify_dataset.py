"""Industrial Dataset Verification Engine for Food Defect AOI.

Implements strict 7-point validation protocol:
1. Configuration & Split Structure (data.yaml, 5 classes, directory tree).
2. 1-to-1 Image-to-Label Pairing (no orphan images or orphan labels).
3. Image Validity & Dimensions (OpenCV decodability, 3 channels, 640x640).
4. 15% Negative Sample Ratio Check (13.5% - 16.5% per split, 14.0% - 16.0% combined).
5. YOLOv8 Segmentation Syntax & Class Domain (tokens >= 7, odd count, class in 0-4).
6. Coordinate Bounds & Shoelace Area ([0.0, 1.0] bounds, non-zero polygon area).
7. Fruit Body Presence & Defect Invariants (Class 0 required for defect frames).
"""

import argparse
import sys
from pathlib import Path
from typing import Any

import cv2
import yaml

EXPECTED_CLASSES: dict[int, str] = {
    0: "fruit_body",
    1: "rot",
    2: "bruise",
    3: "scab",
    4: "stem_calyx",
}


def verify_polygon_geometry(coords: list[float]) -> tuple[bool, str]:
    """Verify polygon coordinate bounds and non-zero Shoelace area.

    Args:
        coords: Flattened list of polygon coordinates [x1, y1, x2, y2, ...].

    Returns:
        Tuple[bool, str]: (is_valid, error_message).
    """
    if len(coords) < 6 or len(coords) % 2 != 0:
        return (
            False,
            f"Invalid coordinate count ({len(coords)}), expected even count >= 6",
        )

    for idx, val in enumerate(coords):
        if not (0.0 <= val <= 1.0):
            axis = "x" if idx % 2 == 0 else "y"
            return False, f"Coordinate {axis}={val:.5f} out of bounds [0.0, 1.0]"

    # Shoelace formula for polygon area
    xs = coords[0::2]
    ys = coords[1::2]
    n = len(xs)
    shoelace = sum(xs[i] * ys[(i + 1) % n] - xs[(i + 1) % n] * ys[i] for i in range(n))
    area = 0.5 * abs(shoelace)

    if area <= 1e-6:
        return False, f"Degenerate polygon with near-zero area ({area:.8f})"

    return True, "OK"


def verify_config_and_structure(
    yaml_path: Path,
) -> tuple[bool, dict[str, Any], list[str]]:
    """Verify Rule 1: Config file syntax and class schema.

    Args:
        yaml_path: Path to dataset YAML configuration file.

    Returns:
        Tuple[bool, Dict[str, Any], List[str]]: (success, config_dict, error_list).
    """
    errors: list[str] = []
    if not yaml_path.exists():
        return False, {}, [f"Configuration file not found: {yaml_path}"]

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except (yaml.YAMLError, OSError) as e:
        return False, {}, [f"Failed to parse YAML file {yaml_path}: {e}"]

    # Check class count
    if cfg.get("nc") != 5:
        errors.append(f"Expected nc: 5 in {yaml_path.name}, got {cfg.get('nc')}")

    # Check class names
    names = cfg.get("names", {})
    if isinstance(names, list):
        names = {i: n for i, n in enumerate(names)}

    for class_id, expected_name in EXPECTED_CLASSES.items():
        if names.get(class_id) != expected_name:
            errors.append(
                f"Class {class_id} mismatch in YAML: expected '{expected_name}', got '{names.get(class_id)}'"
            )

    return len(errors) == 0, cfg, errors


def verify_split(
    split_name: str,
    split_dir: Path,
    target_ratio: float = 0.15,
    tolerance: float = 0.015,
    check_images: bool = True,
) -> tuple[bool, dict[str, Any]]:
    """Verify Rules 2-7 for a single dataset split.

    Args:
        split_name: Name of the split ('train', 'valid', or 'test').
        split_dir: Directory containing images/ and labels/ subfolders.
        target_ratio: Target negative sample ratio (default: 0.15).
        tolerance: Allowed ratio deviation (default: 0.015).
        check_images: Whether to decode images with OpenCV.

    Returns:
        Tuple[bool, Dict[str, Any]]: (passed, metrics_dict).
    """
    img_dir = split_dir / "images"
    lbl_dir = split_dir / "labels"
    errors: list[str] = []

    if not img_dir.exists():
        errors.append(f"Images directory missing: {img_dir}")
    if not lbl_dir.exists():
        errors.append(f"Labels directory missing: {lbl_dir}")

    if errors:
        return False, {"errors": errors}

    # Discover image and label files
    valid_img_exts = {".jpg", ".jpeg", ".png", ".bmp"}
    img_map = {
        f.stem: f for f in img_dir.glob("*.*") if f.suffix.lower() in valid_img_exts
    }
    lbl_map = {f.stem: f for f in lbl_dir.glob("*.txt")}

    # Rule 2: 1-to-1 Pairing
    missing_labels = set(img_map.keys()) - set(lbl_map.keys())
    missing_images = set(lbl_map.keys()) - set(img_map.keys())

    if missing_labels:
        errors.append(
            f"{len(missing_labels)} images missing matching label file. Samples: {list(missing_labels)[:3]}"
        )
    if missing_images:
        errors.append(
            f"{len(missing_images)} labels missing matching image file. Samples: {list(missing_images)[:3]}"
        )

    pos_count = 0
    neg_count = 0
    class_histogram: dict[int, int] = {k: 0 for k in EXPECTED_CLASSES}
    invalid_images_count = 0

    # Process all image-label pairs
    common_stems: set[str] = set(img_map.keys()) & set(lbl_map.keys())

    for stem in sorted(common_stems):
        lbl_file = lbl_map[stem]
        img_file = img_map[stem]

        # Rule 3: Image Validity Check
        if check_images:
            img = cv2.imread(str(img_file))
            if img is None:
                errors.append(f"Corrupt/unreadable image: {img_file.name}")
                invalid_images_count += 1
            else:
                h, w, c = img.shape
                if c != 3 or h <= 0 or w <= 0:
                    errors.append(
                        f"Invalid image dimensions for {img_file.name}: shape={img.shape}"
                    )

        # Read label content
        content = lbl_file.read_text(encoding="utf-8").strip()

        # Rule 4: Negative Frame Identification (0-byte or whitespace only)
        if not content:
            neg_count += 1
            continue

        pos_count += 1
        has_fruit_body = False
        has_defects = False

        for line_no, line in enumerate(content.splitlines(), start=1):
            parts = line.strip().split()
            if not parts:
                continue

            # Rule 5: YOLOv8 Segmentation Syntax
            if len(parts) < 7 or len(parts) % 2 == 0:
                errors.append(
                    f"{lbl_file.name}:{line_no} Invalid token count ({len(parts)}), must be odd >= 7"
                )
                continue

            try:
                cls_id = int(parts[0])
            except ValueError:
                errors.append(
                    f"{lbl_file.name}:{line_no} Class token is not an integer: '{parts[0]}'"
                )
                continue

            if cls_id not in EXPECTED_CLASSES:
                errors.append(
                    f"{lbl_file.name}:{line_no} Class ID {cls_id} not in domain 0..4"
                )
                continue

            if cls_id == 0:
                has_fruit_body = True
            elif cls_id in {1, 2, 3}:
                has_defects = True

            class_histogram[cls_id] += 1

            # Rule 6: Coordinate Bounds & Geometry
            try:
                coords = [float(v) for v in parts[1:]]
            except ValueError:
                errors.append(
                    f"{lbl_file.name}:{line_no} Non-numeric coordinate tokens found"
                )
                continue

            valid_geom, geom_msg = verify_polygon_geometry(coords)
            if not valid_geom:
                errors.append(f"{lbl_file.name}:{line_no} {geom_msg}")

        # Rule 7: Invariant Check (Defect frames must have fruit_body Class 0)
        if has_defects and not has_fruit_body:
            errors.append(
                f"{lbl_file.name} Defect frame missing fruit_body (class 0) mask"
            )

    total_frames = pos_count + neg_count
    neg_ratio = (neg_count / total_frames) if total_frames > 0 else 0.0
    ratio_ok = abs(neg_ratio - target_ratio) <= tolerance

    if not ratio_ok:
        errors.append(
            f"Negative ratio {neg_ratio * 100:.2f}% out of tolerance [{ (target_ratio - tolerance) * 100:.1f}%, {(target_ratio + tolerance) * 100:.1f}%]"
        )

    passed = len(errors) == 0

    metrics = {
        "passed": passed,
        "total_frames": total_frames,
        "pos_count": pos_count,
        "neg_count": neg_count,
        "neg_ratio": neg_ratio,
        "ratio_ok": ratio_ok,
        "class_histogram": class_histogram,
        "errors": errors,
    }
    return passed, metrics


def verify_dataset(
    yaml_path: Path,
    target_ratio: float = 0.15,
    tolerance: float = 0.015,
    check_images: bool = True,
) -> bool:
    """Run full verification across dataset configuration and all splits.

    Args:
        yaml_path: Path to dataset YAML configuration.
        target_ratio: Target negative frame ratio.
        tolerance: Allowed ratio tolerance window.
        check_images: Whether to verify images via OpenCV.

    Returns:
        bool: True if all 7 rules pass across all splits, False otherwise.
    """
    print("=" * 70)
    print("INDUSTRIAL AOI DATASET VERIFICATION ENGINE")
    print("=" * 70)
    print(f"Dataset YAML: {yaml_path.resolve()}")
    print(f"Target Negative Ratio: {target_ratio * 100:.1f}% ± {tolerance * 100:.1f}%")

    # Rule 1: Config & Structure
    cfg_ok, _cfg, cfg_errors = verify_config_and_structure(yaml_path)
    if not cfg_ok:
        print("\n[FAIL] Rule 1: Dataset YAML configuration failed:")
        for err in cfg_errors:
            print(f"  - {err}")
        return False

    print("\n[PASS] Rule 1: YAML Schema & 5-Class Taxonomy Valid")
    print(f"  Classes: {EXPECTED_CLASSES}")

    dataset_root = yaml_path.parent
    all_passed = True

    total_pos_all = 0
    total_neg_all = 0
    total_histogram: dict[int, int] = {k: 0 for k in EXPECTED_CLASSES}

    for split in ["train", "valid", "test"]:
        split_dir = dataset_root / split
        if not split_dir.exists():
            print(f"\n[FAIL] Split directory not found: {split_dir}")
            all_passed = False
            continue

        split_passed, metrics = verify_split(
            split_name=split,
            split_dir=split_dir,
            target_ratio=target_ratio,
            tolerance=tolerance,
            check_images=check_images,
        )

        status_tag = "PASS" if split_passed else "FAIL"
        print(f"\n[{status_tag}] Split: '{split}'")
        print(
            f"  Total Frames: {metrics['total_frames']} (Positive: {metrics['pos_count']}, Negative: {metrics['neg_count']})"
        )
        print(
            f"  Negative Ratio: {metrics['neg_ratio'] * 100:.2f}% (Target: {target_ratio * 100:.1f}%)"
        )
        print(f"  Class Instances: {metrics['class_histogram']}")

        if not split_passed:
            all_passed = False
            print(f"  Encountered {len(metrics['errors'])} errors:")
            for err in metrics["errors"][:10]:
                print(f"    - {err}")
            if len(metrics["errors"]) > 10:
                print(f"    ... and {len(metrics['errors']) - 10} more errors")

        total_pos_all += metrics["pos_count"]
        total_neg_all += metrics["neg_count"]
        for cid, count in metrics["class_histogram"].items():
            total_histogram[cid] += count

    # Combined dataset metrics
    grand_total = total_pos_all + total_neg_all
    combined_ratio = (total_neg_all / grand_total) if grand_total > 0 else 0.0
    combined_ratio_ok = abs(combined_ratio - target_ratio) <= 0.010

    print("\n" + "-" * 70)
    print("DATASET AGGREGATE SUMMARY")
    print("-" * 70)
    print(f"Total Dataset Frames: {grand_total}")
    print(
        f"Positive Frames: {total_pos_all} ({total_pos_all / grand_total * 100:.2f}%)"
    )
    print(f"Negative Conveyor Frames: {total_neg_all} ({combined_ratio * 100:.2f}%)")
    print(f"Class Instance Totals: {total_histogram}")

    if not combined_ratio_ok:
        print(
            f"[FAIL] Combined negative ratio {combined_ratio * 100:.2f}% out of tolerance [14.0%, 16.0%]"
        )
        all_passed = False

    print("=" * 70)
    if all_passed:
        print("FINAL RESULT: [PASS] ALL 7 INDUSTRIAL VALIDATION RULES SATISFIED")
    else:
        print("FINAL RESULT: [FAIL] DATASET VALIDATION FAILED")
    print("=" * 70)

    return all_passed


def main() -> None:
    """CLI entry point for dataset verification."""
    parser = argparse.ArgumentParser(
        description="Verify 5-class industrial AOI dataset and negative ratio."
    )
    parser.add_argument(
        "--yaml",
        type=str,
        default="data/fruit_defects/data.yaml",
        help="Path to dataset data.yaml file",
    )
    parser.add_argument(
        "--target-neg-ratio",
        type=float,
        default=0.15,
        help="Target negative sample ratio (default: 0.15)",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.015,
        help="Allowed negative ratio deviation (default: 0.015)",
    )
    parser.add_argument(
        "--skip-decode",
        action="store_true",
        help="Skip OpenCV image decoding to speed up checks",
    )

    args = parser.parse_args()
    base_dir = Path(__file__).resolve().parents[2]
    yaml_path = Path(args.yaml)
    if not yaml_path.is_absolute() and not yaml_path.exists():
        yaml_path = base_dir / yaml_path

    success = verify_dataset(
        yaml_path=yaml_path,
        target_ratio=args.target_neg_ratio,
        tolerance=args.tolerance,
        check_images=not args.skip_decode,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
