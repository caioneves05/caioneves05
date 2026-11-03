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

    # boost contrast and sharpness for better ASCII detail
    img = ImageEnhance.Contrast(img).enhance(1.8)
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = ImageEnhance.Brightness(img).enhance(1.1)

    img.save(OUT)
    print(f"Saved → {OUT}")


if __name__ == "__main__":
    main()
