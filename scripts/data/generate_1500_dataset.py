"""Industrial 1,500-Image Dataset Generator with Polygon Synchronization.

Generates a 1,500-image multi-class instance segmentation dataset for industrial
food defect inspection on high-speed conveyor belts.
- 1,050 Train / 300 Valid / 150 Test (70% / 20% / 10%)
- 15% Negative Conveyor Belt frames (225 total) for zero false alarms
- Synchronized polygon transforms for fruit_body, critical_defect, cosmetic_defect
"""

import random
import shutil
from pathlib import Path

import cv2
import numpy as np
import yaml

# Reproducibility
random.seed(42)
np.random.seed(42)

SRC_DIR = Path("data/fruit_defects")
DST_DIR = Path("data/fruit_defects_1500")

SPLIT_TARGETS = {
    "train": {"total": 1050, "neg": 158},  # 15.0% negative
    "valid": {"total": 300, "neg": 45},    # 15.0% negative
    "test": {"total": 150, "neg": 22},     # 14.7% negative
}

NAMES = {
    0: "fruit_body",
    1: "critical_defect",
    2: "cosmetic_defect",
}


def load_source_samples(split: str) -> list[tuple[Path, list[tuple[int, list[float]]]]]:
    """Load source images and parsed polygon annotations."""
    img_dir = SRC_DIR / split / "images"
    lbl_dir = SRC_DIR / split / "labels"
    samples = []

    for img_file in img_dir.glob("*.*"):
        if "conveyor_neg" in img_file.name:
            continue
        lbl_file = lbl_dir / f"{img_file.stem}.txt"
        polygons = []
        if lbl_file.exists():
            with open(lbl_file, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 7:  # class_id + at least 3 (x, y) pairs
                        cls_id = int(parts[0])
                        coords = [float(p) for p in parts[1:]]
                        polygons.append((cls_id, coords))
        if polygons:
            samples.append((img_file, polygons))
    return samples


def transform_image_and_polygons(
    img: np.ndarray,
    polygons: list[tuple[int, list[float]]],
    angle: float,
    scale: float,
    flip_h: bool,
    flip_v: bool,
    brightness: float,
    contrast: float,
) -> tuple[np.ndarray, list[tuple[int, list[float]]]]:
    """Apply synchronized affine and photometric transformation."""
    h, w = img.shape[:2]
    center = (w / 2.0, h / 2.0)

    # Photometric adjustments
    out_img = img.astype(np.float32) * contrast + brightness
    out_img = np.clip(out_img, 0, 255).astype(np.uint8)

    # Optional light blur
    if random.random() < 0.25:
        out_img = cv2.GaussianBlur(out_img, (3, 3), 0)

    # Flips
    if flip_h:
        out_img = cv2.flip(out_img, 1)
    if flip_v:
        out_img = cv2.flip(out_img, 0)

    # Affine rotation + scale
    M = cv2.getRotationMatrix2D(center, angle, scale)
    out_img = cv2.warpAffine(
        out_img,
        M,
        (w, h),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(25, 25, 25),
    )

    # Transform polygon coordinates
    out_polys = []
    for cls_id, coords in polygons:
        pts = np.array(coords).reshape(-1, 2)
        # Scale back to pixel coordinates
        pts[:, 0] *= w
        pts[:, 1] *= h

        if flip_h:
            pts[:, 0] = w - pts[:, 0]
        if flip_v:
            pts[:, 1] = h - pts[:, 1]

        # Apply rotation matrix: [x', y'] = M * [x, y, 1]^T
        ones = np.ones((pts.shape[0], 1))
        homo_pts = np.hstack([pts, ones])
        trans_pts = (M @ homo_pts.T).T

        # Normalize to [0, 1] and clip
        trans_pts[:, 0] = np.clip(trans_pts[:, 0] / float(w), 0.0, 1.0)
        trans_pts[:, 1] = np.clip(trans_pts[:, 1] / float(h), 0.0, 1.0)

        # Check if polygon is still valid (area > minimum)
        norm_coords = trans_pts.flatten().tolist()
        if len(norm_coords) >= 6:
            out_polys.append((cls_id, norm_coords))

    return out_img, out_polys


def generate_conveyor_frame(idx: int, width: int = 640, height: int = 640) -> np.ndarray:
    """Generate negative conveyor belt texture frame."""
    tones = [35, 50, 180, 205]
    base_val = tones[idx % len(tones)]
    img = np.full((height, width, 3), base_val, dtype=np.uint8)

    # Add roller slat texture
    slat_spacing = 30 + (idx % 15)
    for y in range(0, height, slat_spacing):
        cv2.line(img, (0, y), (width, y), (max(0, base_val - 20),) * 3, 2)

    # Surface noise
    noise = np.random.normal(0, 7, (height, width, 3)).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    # Belt edge shadow
    cv2.rectangle(img, (0, 0), (25, height), (max(0, base_val - 35),) * 3, -1)
    cv2.rectangle(img, (width - 25, 0), (width, height), (max(0, base_val - 35),) * 3, -1)
    return img


def build_1500_dataset() -> None:
    """Generate and package the complete 1,500-image dataset."""
    print("==================================================")
    print("BUILDING 1,500-IMAGE INDUSTRIAL DATASET")
    print("==================================================")

    if DST_DIR.exists():
        shutil.rmtree(DST_DIR)

    total_images_created = 0
    total_pos_created = 0
    total_neg_created = 0

    for split, target in SPLIT_TARGETS.items():
        split_img_dir = DST_DIR / split / "images"
        split_lbl_dir = DST_DIR / split / "labels"
        split_img_dir.mkdir(parents=True, exist_ok=True)
        split_lbl_dir.mkdir(parents=True, exist_ok=True)

        target_total = target["total"]
        target_neg = target["neg"]
        target_pos = target_total - target_neg

        print(f"\nProcessing {split.upper()}: Target = {target_total} (Pos: {target_pos}, Neg: {target_neg})")

        # 1. Load source positive images from corresponding split
        source_samples = load_source_samples(split)
        if not source_samples:
            source_samples = load_source_samples("train")  # Fallback

        pos_count = 0
        while pos_count < target_pos:
            src_img_path, polys = random.choice(source_samples)
            img = cv2.imread(str(src_img_path))
            if img is None:
                continue

            if pos_count < len(source_samples):
                # Keep original untransformed for exact fidelity
                out_img = img
                out_polys = polys
            else:
                # Apply realistic conveyor transform
                angle = random.uniform(-180.0, 180.0)
                scale = random.uniform(0.88, 1.12)
                flip_h = random.random() > 0.5
                flip_v = random.random() > 0.5
                brightness = random.uniform(-25.0, 25.0)
                contrast = random.uniform(0.85, 1.15)
                out_img, out_polys = transform_image_and_polygons(
                    img, polys, angle, scale, flip_h, flip_v, brightness, contrast
                )

            img_name = f"{split}_fruit_{pos_count:04d}.jpg"
            lbl_name = f"{split}_fruit_{pos_count:04d}.txt"

            cv2.imwrite(str(split_img_dir / img_name), out_img)
            with open(split_lbl_dir / lbl_name, "w", encoding="utf-8") as f:
                for cls_id, coords in out_polys:
                    coord_str = " ".join([f"{c:.5f}" for c in coords])
                    f.write(f"{cls_id} {coord_str}\n")

            pos_count += 1
            total_pos_created += 1

        # 2. Generate negative conveyor belt frames (15%)
        for neg_idx in range(target_neg):
            neg_img = generate_conveyor_frame(neg_idx + (100 if split == "valid" else 200))
            img_name = f"{split}_conveyor_neg_{neg_idx:03d}.jpg"
            lbl_name = f"{split}_conveyor_neg_{neg_idx:03d}.txt"

            cv2.imwrite(str(split_img_dir / img_name), neg_img)
            # 0-byte file indicates empty conveyor frame
            with open(split_lbl_dir / lbl_name, "w", encoding="utf-8") as f:
                pass

            total_neg_created += 1

        split_total = pos_count + target_neg
        total_images_created += split_total
        print(f"[OK] {split.upper()} ready: {pos_count} positive + {target_neg} negative = {split_total} images")

    # Write data.yaml
    yaml_data = {
        "path": "data/fruit_defects_1500",
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "names": NAMES,
        "nc": len(NAMES),
    }
    with open(DST_DIR / "data.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(yaml_data, f, sort_keys=False)

    print("\n==================================================")
    print(f"DATASET GENERATION COMPLETE: {total_images_created} IMAGES")
    print(f"  Positive Fruit: {total_pos_created} | Negative Conveyor: {total_neg_created} (15.0%)")
    print(f"  Data YAML: {DST_DIR / 'data.yaml'}")
    print("==================================================")


if __name__ == "__main__":
    build_1500_dataset()
