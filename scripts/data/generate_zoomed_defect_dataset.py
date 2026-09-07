"""Generate High-Zoom Defect Dataset for Stage-2 Defect Specialist Model.

Crops every fruit instance at high resolution with 5% padding, normalizes coordinates,
and maps defect polygons into the zoomed crop frame.
"""
import shutil
from pathlib import Path

import cv2
import numpy as np


def generate_zoomed_dataset(
    source_dir: Path = Path("data/fruit_defects_1500"),
    target_dir: Path = Path("data/fruit_defects_zoomed"),
    target_size: int = 640,
    padding_ratio: float = 0.05,
) -> None:
    source_dir = source_dir.resolve()
    target_dir = target_dir.resolve()
    
    print("==================================================")
    print("GENERATING STAGE-2 HIGH-ZOOM DEFECT DATASET")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    print("==================================================")

    if target_dir.exists():
        shutil.rmtree(target_dir)

    split_counts = {}

    for split in ["train", "valid", "test"]:
        img_src_dir = source_dir / split / "images"
        lbl_src_dir = source_dir / split / "labels"
        
        img_dst_dir = target_dir / split / "images"
        lbl_dst_dir = target_dir / split / "labels"
        img_dst_dir.mkdir(parents=True, exist_ok=True)
        lbl_dst_dir.mkdir(parents=True, exist_ok=True)

        if not img_src_dir.exists():
            continue

        fruit_crops_count = 0
        defects_remapped_count = 0

        image_paths = sorted(list(img_src_dir.glob("*.jpg")) + list(img_src_dir.glob("*.png")))
        for img_path in image_paths:
            lbl_path = lbl_src_dir / f"{img_path.stem}.txt"
            if not lbl_path.exists():
                continue

            lines = [l.strip() for l in lbl_path.read_text(encoding="utf-8").splitlines() if l.strip()]
            if not lines:
                continue

            # Parse fruit body polygon (class 0)
            fruit_lines = []
            defect_lines = []
            for line in lines:
                parts = line.split()
                cls_id = int(parts[0])
                coords = [float(p) for p in parts[1:]]
                if cls_id == 0:
                    fruit_lines.append(coords)
                elif cls_id in (1, 2):
                    defect_lines.append((cls_id, coords))

            # Only process if a fruit body is present
            if not fruit_lines:
                continue

            img = cv2.imread(str(img_path))
            if img is None:
                continue
            h, w = img.shape[:2]

            for f_idx, f_coords in enumerate(fruit_lines):
                xs = f_coords[0::2]
                ys = f_coords[1::2]
                if not xs or not ys:
                    continue

                min_x, max_x = min(xs), max(xs)
                min_y, max_y = min(ys), max(ys)

                # Add padding
                pad_x = (max_x - min_x) * padding_ratio
                pad_y = (max_y - min_y) * padding_ratio
                x1 = max(0.0, min_x - pad_x)
                y1 = max(0.0, min_y - pad_y)
                x2 = min(1.0, max_x + pad_x)
                y2 = min(1.0, max_y + pad_y)

                crop_w = x2 - x1
                crop_h = y2 - y1
                if crop_w <= 0.05 or crop_h <= 0.05:
                    continue

                # Pixel crop
                px1, px2 = int(x1 * w), int(x2 * w)
                py1, py2 = int(y1 * h), int(y2 * h)
                fruit_crop = img[py1:py2, px1:px2]
                if fruit_crop.size == 0:
                    continue

                # Resize to standard model size
                resized_crop = cv2.resize(fruit_crop, (target_size, target_size), interpolation=cv2.INTER_LINEAR)

                # Remap defect annotations
                remapped_defects = []
                for d_cls, d_coords in defect_lines:
                    d_xs = d_coords[0::2]
                    d_ys = d_coords[1::2]

                    # Check if defect lies within this fruit crop
                    mean_dx = sum(d_xs) / len(d_xs)
                    mean_dy = sum(d_ys) / len(d_ys)
                    if not (x1 <= mean_dx <= x2 and y1 <= mean_dy <= y2):
                        continue

                    # Remap coords to [0, 1] relative to crop
                    new_coords = []
                    for x, y in zip(d_xs, d_ys):
                        nx = np.clip((x - x1) / crop_w, 0.0, 1.0)
                        ny = np.clip((y - y1) / crop_h, 0.0, 1.0)
                        new_coords.extend([nx, ny])

                    # Remap classes: 1 -> 0 (critical_defect), 2 -> 1 (cosmetic_defect)
                    target_cls = d_cls - 1
                    coord_str = " ".join([f"{c:.5f}" for c in new_coords])
                    remapped_defects.append(f"{target_cls} {coord_str}")
                    defects_remapped_count += 1

                # Save cropped image and labels
                crop_name = f"{img_path.stem}_crop{f_idx}"
                dst_img_path = img_dst_dir / f"{crop_name}.jpg"
                dst_lbl_path = lbl_dst_dir / f"{crop_name}.txt"

                cv2.imwrite(str(dst_img_path), resized_crop)
                dst_lbl_path.write_text("\n".join(remapped_defects), encoding="utf-8")
                fruit_crops_count += 1

        split_counts[split] = (fruit_crops_count, defects_remapped_count)
        print(f"[{split.upper()}] Generated {fruit_crops_count} zoomed fruit crops | {defects_remapped_count} defect instances remapped")

    # Generate data.yaml
    yaml_content = f"""path: {target_dir.as_posix()}
train: train/images
val: valid/images
test: test/images

nc: 2
names:
  0: critical_defect
  1: cosmetic_defect
"""
    (target_dir / "data.yaml").write_text(yaml_content, encoding="utf-8")
    print(f"\n[OK] Dataset yaml written to: {target_dir / 'data.yaml'}")
    print("Stage-2 High-Zoom Dataset generation complete!\n")

if __name__ == "__main__":
    generate_zoomed_dataset()
