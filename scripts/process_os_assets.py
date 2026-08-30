from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OS_DIR = ROOT / "assets" / "os"
RESAMPLE = Image.Resampling.LANCZOS


def trim_alpha(image: Image.Image, minimum_pixels: int = 8) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    width, height = rgba.size
    rows = []
    columns = []

    for y in range(height):
        if sum(1 for value in alpha.crop((0, y, width, y + 1)).get_flattened_data() if value > 48) >= minimum_pixels:
            rows.append(y)
    for x in range(width):
        if sum(1 for value in alpha.crop((x, 0, x + 1, height)).get_flattened_data() if value > 48) >= minimum_pixels:
            columns.append(x)

    if not rows or not columns:
        return rgba
    padding = 8
    left = max(0, min(columns) - padding)
    top = max(0, min(rows) - padding)
    right = min(width, max(columns) + padding + 1)
    bottom = min(height, max(rows) + padding + 1)
    return rgba.crop((left, top, right, bottom))


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    source = trim_alpha(image)
    source.thumbnail(size, RESAMPLE)
    output = Image.new("RGBA", size, (0, 0, 0, 0))
    position = (
        (size[0] - source.width) // 2,
        (size[1] - source.height) // 2,
    )
    output.alpha_composite(source, position)
    return output


def process_icons() -> None:
    sheet = Image.open(OS_DIR / "app_icons_sheet.png").convert("RGBA")
    half_width = sheet.width // 2
    half_height = sheet.height // 2
    quadrants = {
        "icon_audit.png": (0, 0, half_width, half_height),
        "icon_browser.png": (half_width, 0, sheet.width, half_height),
        "icon_calculator.png": (0, half_height, half_width, sheet.height),
        "icon_documents.png": (half_width, half_height, sheet.width, sheet.height),
    }
    for filename, box in quadrants.items():
        icon = fit(sheet.crop(box), (96, 96))
        icon.save(OS_DIR / filename)


def process_cursor() -> None:
    cursor = trim_alpha(Image.open(OS_DIR / "cursor_source.png"), minimum_pixels=24)
    cursor.thumbnail((44, 54), RESAMPLE)
    output = Image.new("RGBA", (48, 58), (0, 0, 0, 0))
    output.alpha_composite(cursor, (0, 0))
    output.save(OS_DIR / "cursor.png")


def process_shells() -> None:
    for source_name, output_name in (
        ("desktop_shell.png", "desktop_screen.png"),
        ("login_shell.png", "login_screen.png"),
    ):
        source = Image.open(OS_DIR / source_name).convert("RGB")
        source.resize((1600, 900), RESAMPLE).save(OS_DIR / output_name)

    login_source = Image.open(OS_DIR / "login_shell.png").convert("RGBA")
    avatar = login_source.crop((770, 340, 1005, 590))
    fit(avatar, (88, 88)).save(OS_DIR / "user_avatar.png")

    start = trim_alpha(Image.open(OS_DIR / "start_menu_skin.png"), minimum_pixels=20)
    start.resize((350, 676), RESAMPLE).save(OS_DIR / "start_menu.png")

    window = trim_alpha(Image.open(OS_DIR / "window_skin.png"), minimum_pixels=20)
    window.save(OS_DIR / "window.png")

    calculator = trim_alpha(Image.open(OS_DIR / "calculator_skin.png"), minimum_pixels=20)
    calculator.resize((500, 710), RESAMPLE).save(OS_DIR / "calculator.png")


def main() -> None:
    process_shells()
    process_icons()
    process_cursor()
    print("Assets do sistema processados em assets/os.")


if __name__ == "__main__":
    main()
