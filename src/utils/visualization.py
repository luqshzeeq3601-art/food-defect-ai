"""Overlay rendering utilities for defect masks and bounding boxes."""

import numpy as np


def draw_defect_overlay(
    image: np.ndarray,
    defect_mask: np.ndarray | None = None,
    fruit_mask: np.ndarray | None = None,
    color_defect: tuple[int, int, int] = (255, 0, 0),
    color_fruit: tuple[int, int, int] = (0, 255, 0),
    alpha: float = 0.4,
) -> np.ndarray:
    """Blend segmentation masks onto an image frame.

    Args:
        image: Original RGB image (H, W, 3).
        defect_mask: Boolean mask array (H, W) where True = defect.
        fruit_mask: Boolean mask array (H, W) where True = fruit body.
        color_defect: RGB tuple for defect mask overlay.
        color_fruit: RGB tuple for fruit boundary overlay.
        alpha: Transparency alpha blend factor.

    Returns:
        Annotated RGB image.
    """
    annotated = image.copy()
    if fruit_mask is not None:
        annotated[fruit_mask] = (
            (1 - alpha * 0.5) * annotated[fruit_mask]
            + (alpha * 0.5) * np.array(color_fruit)
        ).astype(np.uint8)

    if defect_mask is not None:
        annotated[defect_mask] = (
            (1 - alpha) * annotated[defect_mask] + alpha * np.array(color_defect)
        ).astype(np.uint8)

    return annotated
