from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "backgrounds" / "audit_base_v2.png"
OUTPUT = ROOT / "assets" / "backgrounds" / "audit_base_v6.png"

# Keep every source pixel. Only the inner data display needs transparency so
# the live rows can be drawn without covering the original frame and scrollbar.
DATA_DISPLAY_RECT = (1375, 482, 1698, 720)


def main() -> None:
    image = Image.open(SOURCE).convert("RGBA")
    pixels = image.load()
    left, top, right, bottom = DATA_DISPLAY_RECT
    for y in range(top, bottom):
        for x in range(left, right):
            red, green, blue, _ = pixels[x, y]
            pixels[x, y] = (red, green, blue, 0)
    image.save(OUTPUT)
    print(f"Restored background written to {OUTPUT}")


if __name__ == "__main__":
    main()
