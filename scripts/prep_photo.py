"""
Preprocesses a source photo for ASCII conversion.
Steps: remove background → CLAHE contrast → white background composite.
Usage: python scripts/prep_photo.py source-photo.jpg
Output: source-prepped.png
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("source-photo.jpg")
OUT = SRC.parent / "source-prepped.png"


def main():
    img = Image.open(SRC).convert("RGB")
    w, h = img.size

    # replace near-black background with white
    arr = np.array(img)
    bg_mask = np.all(arr < 40, axis=2)
    arr[bg_mask] = [255, 255, 255]
    img = Image.fromarray(arr)

    # detect top of hair (first non-white row) and crop a face-height window from there
    gray = np.array(img.convert("L"))
    non_white_rows = np.where(np.any(gray < 220, axis=1))[0]
    top = max(0, non_white_rows[0] - int(h * 0.01)) if len(non_white_rows) else 0

    # face window = ~55% of original height starting from hair top
    face_h = int(h * 0.52)
    bottom = min(h, top + face_h)
    pad_x = int(w * 0.07)
    img = img.crop((pad_x, top, w - pad_x, bottom))

    # contrast + sharpness for ASCII legibility
    img = ImageEnhance.Contrast(img).enhance(1.8)
    img = ImageEnhance.Sharpness(img).enhance(2.2)

    img.save(OUT)
    print(f"Saved → {OUT}")


if __name__ == "__main__":
    main()
