"""Create a sharper copy of the fixed audit background without changing its layout."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "backgrounds" / "audit_base_v2.png"
OUTPUT = ROOT / "assets" / "backgrounds" / "audit_base_v5.png"


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")
    sharpened = image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=180, threshold=3))
    sharpened = ImageEnhance.Contrast(sharpened).enhance(1.035)

    # The original cutout ends early and hides the lower data rows behind black.
    # Restore transparency only inside that existing screen, leaving its bezel intact.
    pixels = sharpened.load()
    for y in range(482, 720):
        for x in range(1375, 1698):
            red, green, blue, _ = pixels[x, y]
            pixels[x, y] = (red, green, blue, 0)
    sharpened.save(OUTPUT, "PNG", optimize=True)
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
