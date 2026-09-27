from __future__ import annotations

from pathlib import Path

import pygame

INK = (216, 221, 132)
INK_BRIGHT = (247, 239, 161)
INK_MUTED = (132, 142, 87)
SCREEN_BLACK = (5, 9, 8)
PANEL = (17, 23, 20)
PANEL_MID = (29, 36, 30)
BORDER = (127, 137, 80)
BORDER_DARK = (55, 64, 45)
AMBER = (237, 193, 91)
GREEN = (101, 191, 91)
RED = (224, 82, 67)
BLUE = (93, 159, 177)
CYAN = (110, 220, 230)

PHOTO_GRID = 64  # photos are shrunk to this many pixels per side, then blown up: chunky pixel art
UPRIGHT_PHOTOS = ("cat_02", "cat_04", "cat_07", "other_01", "other_06", "other_07")


_FONT_CACHE: dict[tuple[int, bool], pygame.font.Font] = {}


def font(size: int, bold: bool = False) -> pygame.font.Font:
    """Cached system font. A cached font dies if pygame is re-initialised, so it is re-checked."""
    key = (size, bold)
    cached = _FONT_CACHE.get(key)
    if cached is not None:
        try:
            cached.size("A")
            return cached
        except pygame.error:
            pass
    created = pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)
    _FONT_CACHE[key] = created
    return created


def draw_text(
    surface: pygame.Surface,
    text: str,
    text_font: pygame.font.Font,
    color: tuple[int, int, int],
    position: tuple[int, int],
    anchor: str = "topleft",
) -> pygame.Rect:
    rendered = text_font.render(text, False, color)
    rect = rendered.get_rect()
    setattr(rect, anchor, position)
    surface.blit(rendered, rect)
    return rect


def wrap_text(text: str, text_font: pygame.font.Font, width: int) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if not current or text_font.size(candidate)[0] <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(
    surface: pygame.Surface,
    text: str,
    text_font: pygame.font.Font,
    color: tuple[int, int, int],
    rect: pygame.Rect,
    line_height: int,
    center: bool = False,
) -> None:
    for index, line in enumerate(wrap_text(text, text_font, rect.width)):
        if center:
            draw_text(surface, line, text_font, color, (rect.centerx, rect.y + index * line_height), "midtop")
        else:
            draw_text(surface, line, text_font, color, (rect.x, rect.y + index * line_height))


def load_optional_image(root: Path, relative: str) -> pygame.Surface | None:
    """Load an image if it exists; the game must run before the art is delivered."""
    path = Path(root) / relative
    if not path.is_file():
        return None
    try:
        return pygame.image.load(str(path)).convert_alpha()
    except pygame.error:
        return None


def pixelate_photo(image: pygame.Surface, grid: int = PHOTO_GRID) -> pygame.Surface:
    """Real photo -> retro pixel art that is still easy to read: chunky cells, 8 tones per colour,
    contrast stretched per photo so dark or pale pictures do not turn into grey mush."""
    small = pygame.transform.smoothscale(image.convert(), (grid, grid))
    pixels = [small.get_at((x, y))[:3] for y in range(grid) for x in range(grid)]
    lows = [min(p[c] for p in pixels) for c in range(3)]
    highs = [max(p[c] for p in pixels) for c in range(3)]
    low, high = min(lows), max(highs)
    span = max(1, high - low)
    step = 255 / 7
    for index, (r, g, b) in enumerate(pixels):
        stretched = [max(0, min(255, (c - low) * 255 / span)) for c in (r, g, b)]
        r, g, b = (round(round(c / step) * step) for c in stretched)
        small.set_at((index % grid, index // grid), (int(r * 0.97), min(255, int(g * 1.01)), int(b * 0.93)))
    return pygame.transform.scale(small, image.get_size())


def _load_image(path: Path) -> pygame.Surface | None:
    try:
        image = pygame.image.load(str(path))
    except pygame.error:
        return None
    if path.suffix.lower() in (".jpg", ".jpeg"):  # photos get the pixel-art treatment
        return pixelate_photo(image)
    return image.convert_alpha()


def load_folder(root: Path, folder: str, prefix: str = "") -> list[pygame.Surface]:
    directory = Path(root) / folder
    if not directory.is_dir():
        return []
    images: list[pygame.Surface] = []
    for path in sorted(p for p in directory.iterdir() if p.stem.startswith(prefix) and p.suffix.lower() in (".png", ".jpg", ".jpeg")):
        image = _load_image(path)
        if image is not None:
            images.append(image)
    return images


def load_named_images(root: Path, folder: str, strip_prefix: str = "") -> dict[str, pygame.Surface]:
    """Images of a folder keyed by file name (without extension and prefix)."""
    directory = Path(root) / folder
    images: dict[str, pygame.Surface] = {}
    if not directory.is_dir():
        return images
    for path in sorted(directory.glob("*.png")):
        try:
            images[path.stem.removeprefix(strip_prefix)] = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            continue
    return images


def load_scientists(root: Path, upright_only: bool = False) -> list[pygame.Surface]:
    """Pixelated animal photos used by the jigsaw and memory captchas."""
    photos = load_folder(root, "captcha/tiles")
    if upright_only:
        wanted = [image for image, path in zip(photos, sorted(Path(root, "captcha/tiles").iterdir())) if path.stem in UPRIGHT_PHOTOS]
        photos = wanted or photos
    return photos


ROTATE_PHOTO_GRID = 128  # a much lighter filter than the cat tiles: this captcha needs to be read fast
ROTATE_PHOTO_INSTRUCTIONS = {
    "person": "Gire a imagem até a pessoa ficar em pé.",
    "bottle": "Gire a imagem até a garrafa ficar em pé.",
    "chair": "Gire a imagem até a cadeira ficar em pé.",
    "lamp": "Gire a imagem até o abajur ficar em pé.",
    "cactus": "Gire a imagem até o cacto ficar em pé.",
    "guitar": "Gire a imagem até o violão ficar em pé.",
    "vase": "Gire a imagem até o vaso ficar em pé.",
    "wineglass": "Gire a imagem até a garrafa de vinho ficar em pé.",
}


def load_rotate_photos(root: Path) -> dict[str, pygame.Surface]:
    """Real, lightly pixelated photos for the 'rotate until it stands up' captcha."""
    directory = Path(root) / "captcha" / "rotate"
    photos: dict[str, pygame.Surface] = {}
    if not directory.is_dir():
        return photos
    for path in sorted(directory.glob("*.jpg")):
        try:
            raw = pygame.image.load(str(path)).convert()
        except pygame.error:
            continue
        photos[path.stem] = pixelate_photo(raw, grid=ROTATE_PHOTO_GRID)
    return photos


def fit_square(image: pygame.Surface, size: int) -> pygame.Surface:
    """Crop the image to a square (a bit above the middle, where the face is) and scale it."""
    width, height = image.get_size()
    side = min(width, height)
    crop = pygame.Rect((width - side) // 2, 0, side, side)
    return pygame.transform.smoothscale(image.subsurface(crop), (size, size))


def fit_box(image: pygame.Surface, box: tuple[int, int]) -> pygame.Surface:
    """Scale to cover `box`, cropping the overflow (a bit above the middle)."""
    scale = max(box[0] / image.get_width(), box[1] / image.get_height())
    scaled = pygame.transform.smoothscale(
        image, (max(1, round(image.get_width() * scale)), max(1, round(image.get_height() * scale)))
    )
    crop = pygame.Rect(0, round((scaled.get_height() - box[1]) * 0.4), box[0], box[1])
    crop.centerx = scaled.get_rect().centerx
    return scaled.subsurface(crop).copy()


def draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    hovered: bool,
    accent: tuple[int, int, int] = AMBER,
    size: int = 20,
) -> None:
    pygame.draw.rect(surface, PANEL_MID if hovered else PANEL, rect)
    pygame.draw.rect(surface, INK_BRIGHT if hovered else accent, rect, 3)
    draw_text(surface, label, font(size, True), INK_BRIGHT, rect.center, "center")
