"""Automated 5-Class Industrial Dataset Builder & Negative Conveyor Injector.

This script converts the raw 2-class fruit defect dataset into an industrial
5-class instance segmentation dataset (fruit_body, rot, bruise, scab, stem_calyx)
and injects 15% negative conveyor belt frames to suppress false alarms.
"""

import shutil
from pathlib import Path

import cv2
import numpy as np

# Deterministic random seed for reproducibility
np.random.seed(42)

CLASSES: dict[int, str] = {
    0: "fruit_body",
    1: "rot",
    2: "bruise",
    3: "scab",
    4: "stem_calyx",
}

NEGATIVE_COUNTS: dict[str, int] = {
    "train": 30,
    "valid": 8,
    "test": 4,
}


def backup_existing_dataset(dataset_dir: Path, backup_dir: Path) -> None:
    """Safely back up the raw 2-class dataset to a backup directory.

    Args:
        dataset_dir: Path to source dataset directory.
        backup_dir: Path to backup destination directory.
    """
    if backup_dir.exists():
        print(f"[INFO] Backup already exists at {backup_dir}. Skipping duplicate copy.")
        return

    print(f"[INFO] Creating complete backup at {backup_dir}...")
    backup_dir.mkdir(parents=True, exist_ok=True)

    yaml_src = dataset_dir / "data.yaml"
    if yaml_src.exists():
        shutil.copy(yaml_src, backup_dir / "data.yaml")

    for split in ["train", "valid", "test"]:
        split_src = dataset_dir / split
        split_dst = backup_dir / split
        if split_src.exists():
            shutil.copytree(split_src, split_dst, dirs_exist_ok=True)

    print(f"[OK] Successfully backed up 2-class dataset to {backup_dir}")


def generate_conveyor_texture(
    idx: int, width: int = 640, height: int = 640
) -> np.ndarray:
    """Generate synthetic industrial conveyor belt image.

    Includes roller slats, lighting vignette gradients, and wear scratch lines.

    Args:
        idx: Index used for deterministic tone and spacing variation.
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        np.ndarray: Generated BGR image of shape (height, width, 3).
    """
    tones = [40, 60, 195, 210]  # dark rubber vs light PVC
    base_val = tones[idx % len(tones)]
    img = np.full((height, width, 3), base_val, dtype=np.uint8)

    # Rollers / horizontal slat grooves
    spacing = 30 + (idx % 15)
    for y in range(0, height, spacing):
        groove_val = max(0, base_val - 25)
        img[y : y + 2, :] = groove_val

    # Lighting vignette horizontal gradient
    grad = np.tile(np.linspace(0.85, 1.15, width), (height, 1))
    img = np.clip(img * grad[:, :, np.newaxis], 0, 255).astype(np.uint8)

    # Factory surface micro-scratches
    rng = np.random.RandomState(42 + idx)
    for _ in range(5):
        x1, y1 = int(rng.randint(0, width)), int(rng.randint(0, height))
        x2, y2 = int(x1 + rng.randint(-50, 50)), int(y1 + rng.randint(-5, 5))
        scratch_val = int(max(0, base_val - 20))
        cv2.line(img, (x1, y1), (x2, y2), (scratch_val, scratch_val, scratch_val), 1)

    return img


def contour_to_polygon_str(
    class_id: int, cnt: np.ndarray, width: int = 640, height: int = 640
) -> str | None:
    """Approximate contour and format as a YOLOv8 polygon annotation string.

    Args:
        class_id: Integer class identifier (0-4).
        cnt: OpenCV contour points.
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        Optional[str]: Formatted string "<class_id> x1 y1 x2 y2 ...\\n", or None if degenerate.
    """
    perimeter = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.0025 * perimeter, True)
    pts = approx.reshape(-1, 2)
    if len(pts) < 3:
        return None

    coords: list[str] = []
    for pt in pts:
        x_norm = float(np.clip(pt[0] / float(width), 0.0, 1.0))
        y_norm = float(np.clip(pt[1] / float(height), 0.0, 1.0))
        coords.extend([f"{x_norm:.5f}", f"{y_norm:.5f}"])

    return f"{class_id} " + " ".join(coords) + "\n"


def process_fruit_image(img_path: Path, is_originally_healthy: bool) -> list[str]:
    """Segment fruit body and extract multi-class defect polygons.

    Args:
        img_path: Path to the fruit image file.
        is_originally_healthy: Whether the fruit was labeled as healthy originally.

    Returns:
        List[str]: List of YOLOv8 polygon string annotations.
    """
    img = cv2.imread(str(img_path))
    if img is None:
        return []

    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_chan = lab[:, :, 0]

    # Saliency segmentation for fruit body
    hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    if float(sat.max()) < 10.0:
        # Grayscale / desaturated fallback
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners = [gray[0, 0], gray[0, -1], gray[-1, 0], gray[-1, -1]]
        is_light_bg = float(np.mean(corners)) > 127.0
        thresh_type = cv2.THRESH_BINARY_INV if is_light_bg else cv2.THRESH_BINARY
        _, f_mask = cv2.threshold(gray, 0, 255, thresh_type + cv2.THRESH_OTSU)
    else:
        _, f_mask = cv2.threshold(sat, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    cnts, _ = cv2.findContours(f_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return []

    largest_cnt = max(cnts, key=cv2.contourArea)
    if cv2.contourArea(largest_cnt) < 5000:
        return []

    lines: list[str] = []

    # 1. Class 0: Fruit Body
    f_body_str = contour_to_polygon_str(0, largest_cnt, w, h)
    if f_body_str:
        lines.append(f_body_str)

    clean_f_mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(clean_f_mask, [largest_cnt], -1, 255, -1)
    f_bool = clean_f_mask == 255

    f_l = l_chan[f_bool]
    mean_l = float(np.mean(f_l))
    std_l = float(np.std(f_l))

    # 2. Class 4: Stem/Calyx cavity (Polar notch in upper 25% of fruit body)
    bx, by, bw, bh = cv2.boundingRect(largest_cnt)
    stem_roi = np.zeros((h, w), dtype=bool)
    stem_roi[by : by + int(bh * 0.25), bx + int(bw * 0.3) : bx + int(bw * 0.7)] = True
    stem_mask = stem_roi & f_bool & (l_chan < (mean_l - 1.2 * std_l))
    s_cnts, _ = cv2.findContours(
        stem_mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    s_cands = [sc for sc in s_cnts if 60 <= cv2.contourArea(sc) <= 2000]
    if s_cands:
        best_stem = max(s_cands, key=cv2.contourArea)
        s_str = contour_to_polygon_str(4, best_stem, w, h)
        if s_str:
            lines.append(s_str)

    # Healthy fruit images do not receive rot, bruise, or scab annotations
    if is_originally_healthy:
        return lines

    # 3. Class 1: Rot (dark necrotic lesions, area >= 150)
    rot_m = (l_chan < (mean_l - 2.1 * std_l)) & f_bool & (~stem_mask)
    r_cnts, _ = cv2.findContours(
        rot_m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    r_valid = sorted(
        [rc for rc in r_cnts if cv2.contourArea(rc) >= 150],
        key=cv2.contourArea,
        reverse=True,
    )[:4]
    for rc in r_valid:
        r_str = contour_to_polygon_str(1, rc, w, h)
        if r_str:
            lines.append(r_str)

    # 4. Class 2: Bruise (subsurface contusions, area >= 200)
    bruise_m = (
        (l_chan >= (mean_l - 2.0 * std_l))
        & (l_chan < (mean_l - 1.3 * std_l))
        & f_bool
        & (~stem_mask)
    )
    b_cnts, _ = cv2.findContours(
        bruise_m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    b_valid = sorted(
        [bc for bc in b_cnts if cv2.contourArea(bc) >= 200],
        key=cv2.contourArea,
        reverse=True,
    )[:4]
    for bc in b_valid:
        b_str = contour_to_polygon_str(2, bc, w, h)
        if b_str:
            lines.append(b_str)

    # 5. Class 3: Scab (corky texture via Laplacian roughness, area >= 100)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    lap = np.abs(cv2.Laplacian(gray, cv2.CV_64F))
    scab_m = (lap > 28) & f_bool & (~stem_mask) & (~rot_m)
    scab_m = cv2.morphologyEx(
        scab_m.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)
    )
    sc_cnts, _ = cv2.findContours(scab_m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sc_valid = sorted(
        [sc for sc in sc_cnts if cv2.contourArea(sc) >= 100],
        key=cv2.contourArea,
        reverse=True,
    )[:4]
    for sc in sc_valid:
        sc_str = contour_to_polygon_str(3, sc, w, h)
        if sc_str:
            lines.append(sc_str)

    return lines


def update_data_yaml(dataset_dir: Path) -> None:
    """Write verified 5-class configuration to data.yaml with relative paths.

    Args:
        dataset_dir: Path to dataset directory.
    """
    content = """path: data/fruit_defects
train: train/images
val: valid/images
test: test/images

names:
  0: fruit_body
  1: rot
  2: bruise
  3: scab
  4: stem_calyx

nc: 5
"""
    yaml_path = dataset_dir / "data.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Updated {yaml_path} to 5-class schema with relative path")


def purge_label_caches(dataset_dir: Path) -> None:
    """Delete stale Ultralytics labels.cache files across all splits.

    Args:
        dataset_dir: Path to dataset directory.
    """
    for split in ["train", "valid", "test"]:
        cache_file = dataset_dir / split / "labels.cache"
        if cache_file.exists():
            cache_file.unlink()
            print(f"[OK] Purged stale cache: {cache_file}")


def build_dataset(workspace_root: Path | None = None) -> None:
    """Execute complete dataset conversion and negative frame injection.

    Args:
        workspace_root: Optional workspace root directory.
    """
    if workspace_root is None:
        workspace_root = Path(__file__).resolve().parents[2]

    dataset_dir = workspace_root / "data" / "fruit_defects"
    backup_dir = workspace_root / "data" / "fruit_defects_backup_2class"

    backup_existing_dataset(dataset_dir, backup_dir)

    global_neg_idx = 1

    for split, neg_count in NEGATIVE_COUNTS.items():
        img_dir = dataset_dir / split / "images"
        lbl_dir = dataset_dir / split / "labels"
        lbl_dir.mkdir(parents=True, exist_ok=True)

        # 1. Process existing fruit images
        image_files = sorted(
            [
                p
                for p in img_dir.glob("*.*")
                if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
                and not p.name.startswith("conveyor_neg_")
            ]
        )
        print(f"\nProcessing {split} split ({len(image_files)} fruit images)...")

        fruit_processed = 0
        for img_p in image_files:
            # Check original label in backup to determine if healthy
            orig_lbl = backup_dir / split / "labels" / f"{img_p.stem}.txt"
            is_healthy = False
            if orig_lbl.exists():
                with open(orig_lbl, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    # Class 1 was healthy, or empty label meant healthy/unannotated fruit
                    if first_line.startswith("1 ") or not first_line:
                        is_healthy = True

            poly_lines = process_fruit_image(img_p, is_healthy)
            target_lbl = lbl_dir / f"{img_p.stem}.txt"
            with open(target_lbl, "w", encoding="utf-8") as f:
                f.writelines(poly_lines)
            fruit_processed += 1

        print(f"Processed {fruit_processed} fruit image labels in {split}")

        # 2. Inject negative conveyor frames
        print(f"Injecting {neg_count} negative conveyor frames in {split}...")
        for _ in range(neg_count):
            neg_name = f"conveyor_neg_{global_neg_idx:03d}"
            neg_img_p = img_dir / f"{neg_name}.jpg"
            neg_lbl_p = lbl_dir / f"{neg_name}.txt"

            neg_img = generate_conveyor_texture(global_neg_idx)
            cv2.imwrite(str(neg_img_p), neg_img)

            # Create 0-byte empty label file per Ultralytics protocol
            neg_lbl_p.touch()

            global_neg_idx += 1

    purge_label_caches(dataset_dir)
    update_data_yaml(dataset_dir)
    print("\n[SUCCESS] 5-Class Industrial Dataset conversion completed successfully!")


if __name__ == "__main__":
    build_dataset()
