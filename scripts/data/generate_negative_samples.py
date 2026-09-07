"""Generate empty conveyor belt negative sample images for false-positive suppression."""
from pathlib import Path

import cv2
import numpy as np


def generate_empty_conveyors(output_dir: str = "data/samples/negative_backgrounds", count: int = 10) -> None:
    """Generate empty conveyor belt textures without fruit or defects.

    Args:
        output_dir: Directory where empty frames will be saved.
        count: Number of variations to create.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    h, w = 640, 640

    for idx in range(count):
        # Base conveyor tone (dark gray / metallic / rubber belt)
        base_color = int(np.random.randint(180, 220))
        img = np.full((h, w, 3), base_color, dtype=np.uint8)

        # Roller slat grooves
        slat_spacing = int(np.random.randint(25, 45))
        for y in range(0, h, slat_spacing):
            groove_color = max(0, base_color - int(np.random.randint(20, 35)))
            img[y:y+2, :] = groove_color

        # Subtle lighting vignette / gradient
        grad = np.tile(np.linspace(0.9, 1.1, w), (h, 1))
        img = np.clip(img * grad[:, :, np.newaxis], 0, 255).astype(np.uint8)

        # Add minor industrial surface dust/scratches
        num_scratches = np.random.randint(3, 8)
        for _ in range(num_scratches):
            x1, y1 = np.random.randint(0, w), np.random.randint(0, h)
            x2, y2 = x1 + np.random.randint(-40, 40), y1 + np.random.randint(-4, 4)
            cv2.line(img, (x1, y1), (x2, y2), (base_color - 15, base_color - 15, base_color - 15), 1)

        file_path = out_path / f"conveyor_empty_{idx+1:02d}.jpg"
        cv2.imwrite(str(file_path), img)

    print(f"[OK] Generated {count} negative conveyor frames in: {out_path}")

if __name__ == "__main__":
    generate_empty_conveyors()
