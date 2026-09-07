"""Generate realistic synthetic fruit frames with known defect areas for testing."""
import os

import cv2
import numpy as np

os.makedirs("data/samples", exist_ok=True)

def generate_fruit(
    filename: str,
    has_rot: bool = False,
    has_bruise: bool = False,
) -> None:
    # 640x640 blank conveyor background (light gray industrial conveyor belt)
    h, w = 640, 640
    img = np.full((h, w, 3), 210, dtype=np.uint8)

    # Conveyor belt subtle horizontal texture
    for y in range(0, h, 20):
        img[y:y+2, :] = 195

    # Draw apple body (Red gradient ellipse)
    center = (320, 330)
    axes = (160, 175)
    
    # Base red apple
    cv2.ellipse(img, center, axes, 0, 0, 360, (20, 30, 210), -1)
    # Add 3D lighting gradient
    cv2.ellipse(img, (280, 280), (120, 130), -15, 0, 360, (40, 60, 235), -1)
    cv2.ellipse(img, (250, 250), (60, 70), -20, 0, 360, (80, 100, 245), -1)

    # Apple stem
    cv2.line(img, (320, 160), (325, 120), (30, 60, 90), 5)

    if has_rot:
        # Severe dark rot lesion
        cv2.ellipse(img, (380, 360), (45, 40), 25, 0, 360, (15, 25, 40), -1)
        cv2.circle(img, (380, 360), 25, (10, 15, 25), -1)

    if has_bruise:
        # Surface brown discoloration bruise
        cv2.ellipse(img, (260, 390), (35, 25), -30, 0, 360, (20, 60, 110), -1)

    # Save as RGB/BGR
    cv2.imwrite(filename, img)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_fruit("data/samples/sample_apple_healthy.jpg", has_rot=False, has_bruise=False)
    generate_fruit("data/samples/sample_apple_bruised.jpg", has_rot=False, has_bruise=True)
    generate_fruit("data/samples/sample_apple_rotten.jpg", has_rot=True, has_bruise=False)
