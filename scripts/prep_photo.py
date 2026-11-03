"""
Preprocesses a source photo for ASCII conversion.
Steps: remove background → CLAHE contrast → white background composite.
Usage: python scripts/prep_photo.py source-photo.jpg
Output: source-prepped.png
"""

import sys
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("source-photo.jpg")
OUT = SRC.parent / "source-prepped.png"


def main():
    img = Image.open(SRC).convert("RGB")

    # crop: keep face + neck only (top 48%), small horizontal padding removal
    w, h = img.size
    pad_x = int(w * 0.06)
    img = img.crop((pad_x, 0, w - pad_x, int(h * 0.50)))

    # strong contrast + sharpness for ASCII legibility
    img = ImageEnhance.Contrast(img).enhance(2.4)
    img = ImageEnhance.Sharpness(img).enhance(3.0)
    img = ImageEnhance.Brightness(img).enhance(0.95)
    # second contrast pass to push darks darker / lights lighter
    img = ImageEnhance.Contrast(img).enhance(1.4)

    img.save(OUT)
    print(f"Saved → {OUT}")


if __name__ == "__main__":
    main()
