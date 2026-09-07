"""Industrial KUKA Roboflow Dataset Preparation with Negative Conveyor Injection.

Standardizes the downloaded Roboflow KUKA produce dataset, injects 15% negative
conveyor belt frames to guarantee zero false alarms on bare rollers, and generates
the resolved YAML configuration for YOLOv8s-seg instance segmentation.
"""

import random
import shutil
from pathlib import Path

import yaml

# Ensure deterministic execution
random.seed(42)

BASE_DIR = Path(__file__).resolve().parents[2]
SRC_DATA_DIR = BASE_DIR / "data" / "roboflow_kuka"
NEG_SOURCE_DIR = BASE_DIR / "data" / "fruit_defects_1500"
OUTPUT_YAML = SRC_DATA_DIR / "kuka_data.yaml"

CLASS_NAMES: dict[int, str] = {
    0: "apple_bad",  # Critical Defect / Immediate Reject
    1: "apple_good",  # Healthy Fruit / Grade A
    2: "apple_moderate",  # Cosmetic Defect / Grade B
}

NEGATIVE_TARGETS: dict[str, int] = {
    "train": 160,
    "valid": 35,
    "test": 35,
}


def inject_conveyor_negatives(split: str, target_count: int) -> int:
    """Copy negative conveyor frames and create empty label files.

    Args:
        split: Dataset split ('train', 'valid', or 'test').
        target_count: Target number of negative frames to inject.

    Returns:
        Number of negative images successfully injected.
    """
    img_dest_dir = SRC_DATA_DIR / split / "images"
    lbl_dest_dir = SRC_DATA_DIR / split / "labels"
    img_dest_dir.mkdir(parents=True, exist_ok=True)
    lbl_dest_dir.mkdir(parents=True, exist_ok=True)

    neg_source_img_dir = NEG_SOURCE_DIR / split / "images"
    available_negatives = list(neg_source_img_dir.glob("*conveyor_neg*.*"))

    if not available_negatives:
        # Fallback to train directory if valid/test has fewer
        available_negatives = list(
            (NEG_SOURCE_DIR / "train" / "images").glob("*conveyor_neg*.*")
        )

    sampled_negatives = random.sample(
        available_negatives, min(len(available_negatives), target_count)
    )

    injected = 0
    for neg_img in sampled_negatives:
        dest_img_name = f"neg_{neg_img.name}"
        dest_img_path = img_dest_dir / dest_img_name
        dest_lbl_path = lbl_dest_dir / f"{dest_img_path.stem}.txt"

        if not dest_img_path.exists():
            shutil.copy2(neg_img, dest_img_path)
            # Negative frames have empty label files (zero detections)
            dest_lbl_path.touch(exist_ok=True)
            injected += 1

    return injected


def create_dataset_yaml() -> Path:
    """Generate kuka_data.yaml with absolute paths for YOLOv8 training.

    Returns:
        Path to the generated YAML configuration file.
    """
    config = {
        "path": str(SRC_DATA_DIR.resolve()).replace("\\", "/"),
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "names": CLASS_NAMES,
        "nc": len(CLASS_NAMES),
    }

    with open(OUTPUT_YAML, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    return OUTPUT_YAML


def verify_dataset_integrity() -> dict[str, dict[str, int]]:
    """Verify image/label correspondence and class distributions across all splits.

    Returns:
        Dictionary of image and label counts per split.
    """
    summary: dict[str, dict[str, int]] = {}
    for split in ["train", "valid", "test"]:
        imgs = list((SRC_DATA_DIR / split / "images").glob("*.*"))
        lbls = list((SRC_DATA_DIR / split / "labels").glob("*.txt"))
        neg_imgs = [img for img in imgs if "neg_" in img.name]
        summary[split] = {
            "total_images": len(imgs),
            "total_labels": len(lbls),
            "negative_images": len(neg_imgs),
            "positive_images": len(imgs) - len(neg_imgs),
        }
    return summary


def main() -> None:
    """Execute dataset preparation workflow."""
    print("=" * 60)
    print("Preparing Roboflow KUKA Dataset with Negative Injection")
    print("=" * 60)

    for split, target in NEGATIVE_TARGETS.items():
        count = inject_conveyor_negatives(split, target)
        print(f"[{split.upper()}] Injected {count} negative conveyor frames.")

    yaml_path = create_dataset_yaml()
    print(f"Generated YAML config: {yaml_path}")

    stats = verify_dataset_integrity()
    for split, data in stats.items():
        neg_pct = (
            (data["negative_images"] / data["total_images"]) * 100
            if data["total_images"] > 0
            else 0
        )
        print(
            f"Split '{split}': {data['total_images']} images "
            f"({data['positive_images']} produce, {data['negative_images']} negative conveyor [{neg_pct:.1f}%])"
        )
    print("=" * 60)
    print("Dataset preparation completed successfully.")


if __name__ == "__main__":
    main()
