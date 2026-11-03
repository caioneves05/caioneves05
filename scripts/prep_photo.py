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

    # auto-crop: find bounding box of non-white pixels (the subject)
    gray = np.array(img.convert("L"))
    rows_with_content = np.where(np.any(gray < 230, axis=1))[0]
    cols_with_content = np.where(np.any(gray < 230, axis=0))[0]

    if len(rows_with_content) and len(cols_with_content):
        pad = int(min(h, w) * 0.03)
        top    = max(0, rows_with_content[0] - pad)
        bottom = min(h, rows_with_content[-1] + pad)
        left   = max(0, cols_with_content[0] - pad)
        right  = min(w, cols_with_content[-1] + pad)
        img = img.crop((left, top, right, bottom))

    # contrast + sharpness for ASCII legibility
    img = ImageEnhance.Contrast(img).enhance(1.7)
    img = ImageEnhance.Sharpness(img).enhance(2.2)

    img.save(OUT)
    print(f"Saved → {OUT}")


if __name__ == "__main__":
    main()
