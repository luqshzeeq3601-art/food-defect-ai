"""Augmented oversampling pipeline to balance produce defect classes."""

import glob
from pathlib import Path

import cv2
import numpy as np


def flip_polygon_labels(lines: list[str]) -> list[str]:
    """Flip polygon normalized x coordinates horizontally (x' = 1.0 - x).

    Args:
        lines: YOLO segmentation label file lines.

    Returns:
        List of updated label strings with flipped x-coordinates.
    """
    flipped_lines = []
    for line in lines:
        parts = line.strip().split()
        if not parts:
            continue
        cls_id = parts[0]
        coords = [float(c) for c in parts[1:]]
        # Coordinates alternate: x0, y0, x1, y1, ...
        flipped_coords = []
        for i in range(0, len(coords), 2):
            x = coords[i]
            y = coords[i + 1]
            flipped_x = round(max(0.0, min(1.0, 1.0 - x)), 6)
            flipped_coords.extend([flipped_x, y])

        coord_str = " ".join(f"{c:.6f}" for c in flipped_coords)
        flipped_lines.append(f"{cls_id} {coord_str}\n")
    return flipped_lines


def apply_clahe_lab(img_bgr: np.ndarray) -> np.ndarray:
    """Apply CLAHE to L channel in LAB color space to equalize lighting.

    Args:
        img_bgr: Input BGR image.

    Returns:
        Lighting-equalized BGR image.
    """
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l_chan, a_chan, b_chan = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_equalized = clahe.apply(l_chan)
    merged_lab = cv2.merge([l_equalized, a_chan, b_chan])
    return cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)


def apply_lighting_jitter(img_bgr: np.ndarray, alpha: float, beta: int) -> np.ndarray:
    """Apply linear contrast and brightness scaling.

    Args:
        img_bgr: Input BGR image.
        alpha: Contrast multiplier.
        beta: Brightness offset.

    Returns:
        Adjusted BGR image.
    """
    return cv2.convertScaleAbs(img_bgr, alpha=alpha, beta=beta)


def oversample_training_split(
    dataset_dir: str = "data/roboflow_kuka",
) -> dict[str, int]:
    """Balance minority classes (apple_good and apple_moderate) in the train set.

    Args:
        dataset_dir: Path to Roboflow KUKA dataset directory.

    Returns:
        Dictionary of summary statistics.
    """
    train_labels_dir = Path(dataset_dir) / "train" / "labels"
    train_images_dir = Path(dataset_dir) / "train" / "images"

    label_files = sorted(glob.glob(str(train_labels_dir / "*.txt")))
    initial_labels_count = len(label_files)

    created_good = 0
    created_mod = 0

    for lbl_path_str in label_files:
        lbl_path = Path(lbl_path_str)
        # Skip previously generated augmented files to remain idempotent
        if "_aug_" in lbl_path.stem:
            continue

        with open(lbl_path, "r") as f:
            lines = f.readlines()

        if not lines:
            continue  # Negative frame, keep as-is

        classes = {int(line.split()[0]) for line in lines}

        # Corresponding image file (can be .jpg or .png)
        img_candidates = [
            train_images_dir / f"{lbl_path.stem}.jpg",
            train_images_dir / f"{lbl_path.stem}.png",
        ]
        img_path = next((p for p in img_candidates if p.exists()), None)
        if img_path is None:
            continue

        img_bgr = cv2.imread(str(img_path))
        if img_bgr is None:
            continue

        # Case 1: Contains apple_good (Class 1) -> Generate 2 variants
        if 1 in classes:
            # Variant 1: Horizontal Flip + Contrast scale
            img_v1 = cv2.flip(img_bgr, 1)
            img_v1 = apply_lighting_jitter(img_v1, alpha=1.05, beta=10)
            labels_v1 = flip_polygon_labels(lines)

            stem_v1 = f"{lbl_path.stem}_aug_good_v1"
            cv2.imwrite(str(train_images_dir / f"{stem_v1}.jpg"), img_v1)
            with open(train_labels_dir / f"{stem_v1}.txt", "w") as f:
                f.writelines(labels_v1)

            # Variant 2: CLAHE LAB lighting equalization (No flip, same coordinates)
            img_v2 = apply_clahe_lab(img_bgr)
            stem_v2 = f"{lbl_path.stem}_aug_good_v2"
            cv2.imwrite(str(train_images_dir / f"{stem_v2}.jpg"), img_v2)
            with open(train_labels_dir / f"{stem_v2}.txt", "w") as f:
                f.writelines(lines)

            created_good += 2

        # Case 2: Contains apple_moderate (Class 2) and NOT apple_good -> Generate 1 variant
        elif 2 in classes:
            # Variant 1: Horizontal Flip + mild lighting adjustment
            img_v1 = cv2.flip(img_bgr, 1)
            img_v1 = apply_lighting_jitter(img_v1, alpha=0.95, beta=-8)
            labels_v1 = flip_polygon_labels(lines)

            stem_v1 = f"{lbl_path.stem}_aug_mod_v1"
            cv2.imwrite(str(train_images_dir / f"{stem_v1}.jpg"), img_v1)
            with open(train_labels_dir / f"{stem_v1}.txt", "w") as f:
                f.writelines(labels_v1)

            created_mod += 1

    final_labels_count = len(glob.glob(str(train_labels_dir / "*.txt")))
    stats = {
        "initial_images": initial_labels_count,
        "created_apple_good_variants": created_good,
        "created_apple_moderate_variants": created_mod,
        "total_augmented_added": created_good + created_mod,
        "final_images": final_labels_count,
    }
    print(f"Oversampling complete: {stats}")
    return stats


if __name__ == "__main__":
    oversample_training_split()
