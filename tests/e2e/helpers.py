"""Synthetic fixtures and helper utilities for deterministic E2E testing."""

from pathlib import Path

import cv2
import numpy as np

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLES_DIR = WORKSPACE_ROOT / "data" / "samples"
NEGATIVE_DIR = SAMPLES_DIR / "negative_backgrounds"


def generate_conveyor_image(
    width: int = 640,
    height: int = 640,
    pattern: str = "plain",
    noise_std: float = 0.0,
) -> np.ndarray:
    """Generate deterministic synthetic conveyor belt images.

    Args:
        width: Image width in pixels.
        height: Image height in pixels.
        pattern: Conveyor pattern: 'plain', 'rollers', 'shadow', 'glare', 'textured'.
        noise_std: Standard deviation of Gaussian sensor noise.

    Returns:
        RGB image numpy array of shape (height, width, 3), dtype uint8.
    """
    img = np.full((height, width, 3), 35, dtype=np.uint8)

    if pattern == "rollers":
        for y in range(0, height, 70):
            cv2.line(img, (0, y), (width, y), (55, 55, 60), 4)
            cv2.line(
                img,
                (0, min(height - 1, y + 2)),
                (width, min(height - 1, y + 2)),
                (20, 20, 25),
                2,
            )
    elif pattern == "shadow":
        for y in range(height):
            factor = 0.5 + 0.5 * (y / max(1, height))
            img[y, :] = np.clip(img[y, :] * factor, 10, 80).astype(np.uint8)
    elif pattern == "glare":
        cv2.line(img, (0, height // 2), (width, height // 2), (180, 180, 180), 8)
        img = cv2.GaussianBlur(img, (21, 21), 0)
    elif pattern == "textured":
        rng = np.random.default_rng(42)
        texture = rng.integers(-8, 8, (height, width, 3), dtype=np.int16)
        img = np.clip(img.astype(np.int16) + texture, 0, 255).astype(np.uint8)

    if noise_std > 0:
        rng = np.random.default_rng(123)
        noise = rng.normal(0, noise_std, img.shape).astype(np.int16)
        img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return img


def generate_fruit_image(
    width: int = 640,
    height: int = 640,
    center: tuple[int, int] = (320, 320),
    radius: int = 160,
    base_color: tuple[int, int, int] = (40, 190, 50),
    defects: list[dict] | None = None,
    with_stem: bool = False,
) -> np.ndarray:
    """Generate synthetic fruit images with optional defects and conveyor background.

    Args:
        width: Frame width.
        height: Frame height.
        center: Fruit center (x, y).
        radius: Fruit radius.
        base_color: Fruit body RGB color.
        defects: Optional list of dicts with keys 'type', 'offset', 'radius'.
        with_stem: If True, draws a brown stem depression.

    Returns:
        RGB image numpy array of shape (height, width, 3).
    """
    img = generate_conveyor_image(width=width, height=height, pattern="plain")

    # Draw circular fruit body
    cv2.circle(img, center, radius, base_color, -1)

    if with_stem:
        # Stem / calyx depression near top
        stem_center = (center[0], center[1] - radius + 15)
        cv2.circle(img, stem_center, 12, (30, 25, 20), -1)
        cv2.line(
            img, stem_center, (stem_center[0], stem_center[1] - 25), (60, 45, 30), 4
        )

    if defects:
        for d in defects:
            dtype = d.get("type", "bruise")
            ox, oy = d.get("offset", (0, 0))
            dr = d.get("radius", 20)
            dcenter = (center[0] + ox, center[1] + oy)

            if dtype == "rot":
                color = (20, 15, 10)  # Very dark black/brown
            elif dtype == "bruise":
                color = (70, 95, 45)  # Darkened discolored bruise
            elif dtype == "scab":
                color = (85, 75, 55)  # Mottled scab
            else:
                color = (60, 60, 60)

            cv2.circle(img, dcenter, dr, color, -1)

    return img


def encode_image(image: np.ndarray, fmt: str = ".jpg", quality: int = 90) -> bytes:
    """Encode an RGB numpy image array to compressed bytes.

    Args:
        image: RGB image numpy array.
        fmt: Image extension: '.jpg', '.png', '.bmp'.
        quality: Compression quality for JPEG.

    Returns:
        Encoded bytes.
    """
    bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    params = [cv2.IMWRITE_JPEG_QUALITY, quality] if fmt == ".jpg" else []
    success, buffer = cv2.imencode(fmt, bgr, params)
    if not success:
        raise ValueError(f"Failed to encode image to format {fmt}")
    return buffer.tobytes()


def create_synthetic_masks(
    height: int = 640,
    width: int = 640,
    fruit_center: tuple[int, int] = (320, 320),
    fruit_radius: int = 150,
    defect_specs: list[dict] | None = None,
) -> tuple[np.ndarray, list[dict]]:
    """Generate exact boolean masks for fruit and defects.

    Useful for precise, deterministic mathematical tests of spatial filtering.

    Args:
        height: Mask height.
        width: Mask width.
        fruit_center: Center of fruit disk.
        fruit_radius: Radius of fruit disk.
        defect_specs: List of dicts: {'type': str, 'center': (x, y), 'radius': int}

    Returns:
        Tuple of:
            - boolean array fruit_mask (height, width)
            - list of dicts: {'type': str, 'mask': bool_array, 'pixel_area': int}
    """
    fruit_mask = np.zeros((height, width), dtype=np.uint8)
    cv2.circle(fruit_mask, fruit_center, fruit_radius, 1, -1)
    fruit_mask_bool = fruit_mask == 1

    defect_list = []
    if defect_specs:
        for spec in defect_specs:
            d_type = spec.get("type", "bruise")
            d_center = spec.get("center", fruit_center)
            d_radius = spec.get("radius", 20)
            d_mask = np.zeros((height, width), dtype=np.uint8)
            cv2.circle(d_mask, d_center, d_radius, 1, -1)
            d_bool = d_mask == 1
            defect_list.append(
                {
                    "type": d_type,
                    "mask": d_bool,
                    "pixel_area": int(np.sum(d_bool)),
                }
            )

    return fruit_mask_bool, defect_list
