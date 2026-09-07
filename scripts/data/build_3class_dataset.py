"""Remap 5-Class Dataset into Consolidated 3-Class Industrial Dataset.

Classes:
0: fruit_body (Clean baseline)
1: critical_defect (Rot, soft decay -> immediate REJECT)
2: cosmetic_defect (Bruises, scabs -> Grade A/B area grading)
(Class 4 stem_calyx is filtered out as it is natural anatomy, not a defect).
"""

import shutil
from pathlib import Path

import yaml

DATASET_DIR = Path("data/fruit_defects")
BACKUP_DIR = Path("data/fruit_defects_backup_5class")

NEW_NAMES = {
    0: "fruit_body",
    1: "critical_defect",
    2: "cosmetic_defect",
}

CLASS_MAP = {
    0: 0,  # fruit_body -> fruit_body
    1: 1,  # rot -> critical_defect
    2: 2,  # bruise -> cosmetic_defect
    3: 2,  # scab -> cosmetic_defect
    # 4: omitted (stem_calyx is natural fruit anatomy)
}


def consolidate_dataset() -> None:
    # 1. Back up existing dataset
    if not BACKUP_DIR.exists():
        print(f"[INFO] Backing up 5-class dataset to {BACKUP_DIR}...")
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy(DATASET_DIR / "data.yaml", BACKUP_DIR / "data.yaml")
        for split in ["train", "valid", "test"]:
            if (DATASET_DIR / split).exists():
                shutil.copytree(DATASET_DIR / split, BACKUP_DIR / split, dirs_exist_ok=True)
        print("[OK] Backup created.")

    # 2. Process labels in train, valid, test
    total_modified = 0
    total_instances = 0
    class_counts = {0: 0, 1: 0, 2: 0}

    for split in ["train", "valid", "test"]:
        labels_dir = DATASET_DIR / split / "labels"
        if not labels_dir.exists():
            continue

        for lbl_file in labels_dir.glob("*.txt"):
            with open(lbl_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []
            for line in lines:
                parts = line.strip().split()
                if not parts:
                    continue
                old_cls = int(parts[0])
                if old_cls in CLASS_MAP:
                    new_cls = CLASS_MAP[old_cls]
                    new_lines.append(f"{new_cls} " + " ".join(parts[1:]) + "\n")
                    class_counts[new_cls] += 1
                    total_instances += 1

            with open(lbl_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            total_modified += 1

        # Remove labels.cache so Ultralytics rescans the new classes
        cache_file = DATASET_DIR / split / "labels.cache"
        if cache_file.exists():
            cache_file.unlink()

    # 3. Write new data.yaml
    data_yaml = {
        "path": "data/fruit_defects",
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "names": NEW_NAMES,
        "nc": len(NEW_NAMES),
    }
    with open(DATASET_DIR / "data.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(data_yaml, f, sort_keys=False)

    print(f"[OK] Consolidated {total_modified} label files into 3-class schema.")
    print(f"     Instances by class: {class_counts}")
    print(f"     Class 0 (fruit_body): {class_counts[0]}")
    print(f"     Class 1 (critical_defect): {class_counts[1]}")
    print(f"     Class 2 (cosmetic_defect): {class_counts[2]}")
    print(f"[OK] Updated {DATASET_DIR / 'data.yaml'}")


if __name__ == "__main__":
    consolidate_dataset()
