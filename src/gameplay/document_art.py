"""Code-drawn pictures for the case papers (radar photo, ID photos, maps, QR code...).

Every picture here is a stand-in for an optional real image: when
`assets/cases/<case>/<name>.png` exists the renderer uses that file instead. The `inset`
helpers draw the details that a generated photo could never get right (plate letters, blurry
serial numbers), so they are always painted by code, on top of whichever picture is used.
"""

from __future__ import annotations

import math
import random

import pygame

INK = (30, 30, 28)


def _font(size: int, bold: bool = True) -> pygame.font.Font:
    return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)


def _text(surface: pygame.Surface, text: str, size: int, color, center, bold: bool = True) -> pygame.Rect:
    rendered = _font(size, bold).render(text, False, color)
    rect = rendered.get_rect(center=center)
    surface.blit(rendered, rect)
    return rect


NOMINAL_HEIGHT = 172  # the scenes below are laid out for this height and cropped to the real one
NATIVE = {"face_round", "face_square"}  # these scale themselves
CROP_TOP = {"radar": 28, "serial": 26, "crowd": 34, "gps": 24, "mall": 24, "badge": 6, "qr": 8, "telemetry": 10}


def draw_art(kind: str, size: tuple[int, int], seed: str = "") -> pygame.Surface:
    drawer = ARTS.get(kind, _generic)
    rng = random.Random(seed or kind)
    if kind in NATIVE or size[1] >= NOMINAL_HEIGHT:
        surface = pygame.Surface(size)
        drawer(surface, rng)
        return surface
    scene = pygame.Surface((size[0], NOMINAL_HEIGHT))
    drawer(scene, rng)
    top = min(CROP_TOP.get(kind, 0), NOMINAL_HEIGHT - size[1])
    return scene.subsurface(pygame.Rect(0, top, size[0], size[1])).copy()


# --- photos ---------------------------------------------------------------------------------


def _generic(surface: pygame.Surface, rng: random.Random) -> None:
    surface.fill((70, 80, 76))
    pygame.draw.line(surface, (110, 120, 110), (0, 0), surface.get_size(), 3)
    pygame.draw.line(surface, (110, 120, 110), (0, surface.get_height()), (surface.get_width(), 0), 3)


def _radar(surface: pygame.Surface, rng: random.Random) -> None:
    w, h = surface.get_size()
    surface.fill((58, 66, 74))
    for y in range(h):  # road fading to the horizon
        shade = 40 + y * 30 // h
        pygame.draw.line(surface, (shade, shade + 4, shade + 8), (0, y), (w, y))
    pygame.draw.rect(surface, (120, 130, 118), (0, 0, w, 46))  # toll-booth roof
    pygame.draw.rect(surface, (200, 190, 60), (0, 40, w, 6))
    for x in range(0, w, 60):
        pygame.draw.rect(surface, (235, 235, 225), (x + 10, h - 30, 34, 6))
    body = pygame.Rect(w // 2 - 130, 60, 260, 96)  # rear of a silver sedan
    pygame.draw.rect(surface, (176, 182, 190), body, border_radius=16)
    pygame.draw.rect(surface, (96, 116, 130), (body.x + 30, body.y - 26, body.width - 60, 40), border_radius=10)
    for x in (body.x + 12, body.right - 42):
        pygame.draw.rect(surface, (200, 40, 40), (x, body.y + 18, 30, 14), border_radius=4)
    for x in (body.x + 16, body.right - 56):
        pygame.draw.circle(surface, (20, 20, 22), (x + 20, body.bottom + 4), 20)
    plate = pygame.Rect(body.centerx - 46, body.y + 46, 92, 30)
    pygame.draw.rect(surface, (222, 222, 210), plate, border_radius=3)
    pygame.draw.rect(surface, INK, plate, 2, border_radius=3)
    for _ in range(90):  # mud
        px, py = rng.randrange(plate.x - 8, plate.right + 8), rng.randrange(plate.y - 4, plate.bottom + 10)
        pygame.draw.circle(surface, (84, 62, 38), (px, py), rng.randint(1, 4))
    _text(surface, "ABC-1284", 17, (60, 50, 40), plate.center)
    pygame.draw.rect(surface, (250, 250, 180), (8, 34, 172, 22))
    _text(surface, "CAM 07  12/10  14:32:08", 13, INK, (94, 45))


def _face(surface: pygame.Surface, rng: random.Random, *, round_face: bool, glasses: bool, goatee: bool) -> None:
    w, h = surface.get_size()
    k = h / 172

    def n(value: float) -> int:
        return round(value * k)

    surface.fill((150, 156, 160))
    pygame.draw.rect(surface, (128, 136, 142), (0, h - n(40), w, n(40)))
    cx, cy = w // 2, h // 2 + n(8)
    pygame.draw.rect(surface, (56, 72, 96), (cx - n(90), cy + n(58), n(180), n(90)), border_radius=n(30))  # shirt
    skin = (222, 178, 140)
    if round_face:
        pygame.draw.ellipse(surface, skin, (cx - n(60), cy - n(78), n(120), n(130)))
    else:
        pygame.draw.rect(surface, skin, (cx - n(56), cy - n(78), n(112), n(134)), border_radius=n(14))
    pygame.draw.ellipse(surface, (48, 36, 28), (cx - n(62), cy - n(92), n(124), n(48)))  # hair
    for x in (cx - n(24), cx + n(24)):
        pygame.draw.circle(surface, (250, 250, 250), (x, cy - n(24)), n(10))
        pygame.draw.circle(surface, (40, 30, 24), (x, cy - n(24)), n(5))
    pygame.draw.line(surface, (150, 100, 80), (cx, cy - n(16)), (cx - n(4), cy + n(8)), 3)
    pygame.draw.arc(surface, (150, 70, 60), (cx - n(20), cy + n(14), n(40), n(22)), math.pi * 1.15, math.pi * 1.85, 3)
    if glasses:
        for x in (cx - n(24), cx + n(24)):
            pygame.draw.circle(surface, INK, (x, cy - n(24)), n(17), 3)
        pygame.draw.line(surface, INK, (cx - n(7), cy - n(24)), (cx + n(7), cy - n(24)), 3)
    if goatee:
        pygame.draw.polygon(surface, (48, 36, 28), [(cx - n(22), cy + n(30)), (cx + n(22), cy + n(30)), (cx, cy + n(60))])
    pygame.draw.rect(surface, (250, 250, 236), (10, 10, 110, 20))
    _text(surface, "FOTO 3x4", 13, INK, (65, 20))


def _face_round(surface: pygame.Surface, rng: random.Random) -> None:
    _face(surface, rng, round_face=True, glasses=True, goatee=False)


def _face_square(surface: pygame.Surface, rng: random.Random) -> None:
    _face(surface, rng, round_face=False, glasses=False, goatee=True)


def _crowd(surface: pygame.Surface, rng: random.Random) -> None:
    w, h = surface.get_size()
    surface.fill((176, 184, 196))
    pygame.draw.rect(surface, (90, 94, 88), (0, h - 50, w, 50))
    for x in range(-20, w + 20, 46):  # heads and shoulders
        y = h - 60 - rng.randrange(0, 38)
        tone = rng.choice([(220, 176, 140), (170, 120, 90), (120, 84, 62), (238, 200, 170)])
        pygame.draw.circle(surface, tone, (x, y), 17)
        pygame.draw.rect(surface, rng.choice([(200, 60, 50), (60, 80, 150), (240, 240, 230), (50, 50, 60)]), (x - 22, y + 16, 44, 60), border_radius=10)
    for x in (70, 240, 410):  # signs
        pygame.draw.line(surface, (110, 90, 60), (x, 30), (x, 120), 4)
        pygame.draw.rect(surface, (250, 250, 240), (x - 34, 16, 68, 40))
        pygame.draw.rect(surface, (200, 50, 40), (x - 34, 16, 68, 40), 3)
        pygame.draw.line(surface, (200, 50, 40), (x - 22, 30), (x + 22, 30), 3)
        pygame.draw.line(surface, (200, 50, 40), (x - 22, 42), (x + 12, 42), 3)


def _serial(surface: pygame.Surface, rng: random.Random) -> None:
    w, h = surface.get_size()
    surface.fill((70, 72, 74))
    for y in range(0, h, 4):
        shade = 96 + rng.randrange(-6, 7)
        pygame.draw.line(surface, (shade, shade + 2, shade + 6), (0, y), (w, y), 4)  # brushed metal
    for x in (30, w - 30):
        pygame.draw.circle(surface, (60, 62, 66), (x, 34), 12)
        pygame.draw.circle(surface, (130, 132, 136), (x, 34), 12, 2)
    plate = pygame.Rect(90, 60, w - 180, 80)
    pygame.draw.rect(surface, (150, 152, 156), plate, border_radius=6)
    pygame.draw.rect(surface, (40, 42, 44), plate, 3, border_radius=6)
    _text(surface, "SN-99", 34, (54, 54, 56), (plate.centerx - 66, plate.centery))
    smear = pygame.Surface((70, 60), pygame.SRCALPHA)  # the smudged digit
    pygame.draw.ellipse(smear, (28, 26, 24, 200), (6, 8, 56, 44))
    for _ in range(50):
        pygame.draw.circle(smear, (60, 56, 50, 120), (rng.randrange(70), rng.randrange(60)), rng.randint(2, 6))
    surface.blit(smear, (plate.centerx + 8, plate.centery - 30))
    _text(surface, "2", 34, (54, 54, 56), (plate.centerx + 108, plate.centery))


# --- diagrams -------------------------------------------------------------------------------


def _gps(surface: pygame.Surface, rng: random.Random) -> None:
    w, h = surface.get_size()
    surface.fill((214, 222, 200))
    for x in range(0, w, 34):
        pygame.draw.line(surface, (196, 206, 184), (x, 0), (x, h))
    for y in range(0, h, 34):
        pygame.draw.line(surface, (196, 206, 184), (0, y), (w, y))
    gate = (150, h // 2 + 6)
    pygame.draw.circle(surface, (60, 110, 60), gate, 58, 3)  # allowed radius (50 m)
    pygame.draw.rect(surface, (60, 60, 60), (gate[0] - 8, gate[1] - 8, 16, 16))
    _text(surface, "GUARITA", 13, INK, (gate[0], gate[1] + 24))
    _text(surface, "raio permitido: 50 m", 13, (50, 100, 50), (gate[0] - 6, gate[1] - 72))
    spot = (gate[0] + 46, gate[1] - 10)  # raw GPS point, 40 m out
    pygame.draw.circle(surface, (200, 60, 50), spot, 35, 2)  # +-30 m error
    pygame.draw.circle(surface, (200, 60, 50), spot, 6)
    _text(surface, "posição do celular", 13, (170, 40, 30), (spot[0] + 128, spot[1] - 6))
    _text(surface, "círculo vermelho = margem de erro", 12, (120, 50, 40), (spot[0] + 128, spot[1] + 14), False)
    pygame.draw.line(surface, (60, 60, 60), gate, spot, 2)
    _text(surface, "40 m", 13, INK, ((gate[0] + spot[0]) // 2 - 4, (gate[1] + spot[1]) // 2 + 16))


def _mall(surface: pygame.Surface, rng: random.Random) -> None:
    w, h = surface.get_size()
    surface.fill((232, 226, 208))
    pygame.draw.rect(surface, (200, 194, 176), (14, 14, w - 28, h - 28), 3)
    pygame.draw.rect(surface, (250, 248, 238), (w // 2 - 24, 24, 48, h - 48))  # long corridor
    pygame.draw.rect(surface, (250, 248, 238), (40, h // 2 - 20, w - 80, 40))
    _text(surface, "NORTE", 15, INK, (w // 2, 36))
    _text(surface, "SUL", 15, INK, (w // 2, h - 34))
    hatch = pygame.Rect(w // 2 - 24, h - 80, 48, 30)
    pygame.draw.rect(surface, (170, 110, 60), hatch)
    for x in range(hatch.x, hatch.right, 8):
        pygame.draw.line(surface, (110, 70, 40), (x, hatch.y), (x + 8, hatch.bottom), 2)
    _text(surface, "tapume", 12, (110, 70, 40), (hatch.right + 40, hatch.centery), False)
    for i in range(10):  # people crowding the north corridor
        pygame.draw.circle(surface, (60, 90, 170), (w // 2 - 14 + (i % 3) * 14, 64 + (i // 3) * 14), 5)
    pygame.draw.polygon(surface, (60, 150, 70), [(w - 110, h // 2 - 12), (w - 70, h // 2), (w - 110, h // 2 + 12)])
    _text(surface, "setas de saída", 12, (40, 110, 50), (w - 104, h // 2 + 30), False)


def _badge(surface: pygame.Surface, rng: random.Random) -> None:
    w, h = surface.get_size()
    surface.fill((176, 180, 182))
    card = pygame.Rect(w // 2 - 130, 10, 260, h - 20)
    pygame.draw.rect(surface, (244, 244, 236), card, border_radius=12)
    pygame.draw.rect(surface, (40, 60, 120), (card.x, card.y, card.width, 34), border_top_left_radius=12, border_top_right_radius=12)
    _text(surface, "CRACHÁ DE ACESSO", 14, (255, 255, 255), (card.centerx, card.y + 17))
    pygame.draw.rect(surface, (198, 178, 150), (card.x + 14, card.y + 46, 70, 82))
    pygame.draw.circle(surface, (226, 184, 148), (card.x + 49, card.y + 78), 20)
    _text(surface, "SIN-4042", 24, INK, (card.x + 176, card.y + 70))
    _text(surface, "Carlos M.", 15, (70, 70, 66), (card.x + 176, card.y + 100), False)
    for i in range(30):
        pygame.draw.rect(surface, INK, (card.x + 14 + i * 7, card.bottom - 26, rng.choice([2, 3, 4]), 16))


def _qr(surface: pygame.Surface, rng: random.Random) -> None:
    w, h = surface.get_size()
    surface.fill((200, 204, 206))
    cells = 21
    cell = (h - 30) // cells
    left = w // 2 - cells * cell // 2
    top = (h - cells * cell) // 2
    pygame.draw.rect(surface, (250, 250, 250), (left - 8, top - 8, cells * cell + 16, cells * cell + 16))
    for row in range(cells):
        for column in range(cells):
            finder = (row < 7 and (column < 7 or column > cells - 8)) or (row > cells - 8 and column < 7)
            if finder:
                edge = row in (0, 6, cells - 7, cells - 1) or column in (0, 6, cells - 7, cells - 1)
                edge = edge or (row % (cells - 7) in (0, 6)) or (column % (cells - 7) in (0, 6))
                core = 2 <= row % (cells - 7) <= 4 and 2 <= column % (cells - 7) <= 4
                on = edge or core
            else:
                on = rng.random() < 0.5
            if on:
                pygame.draw.rect(surface, INK, (left + column * cell, top + row * cell, cell, cell))
    _text(surface, "XJ-992A-44", 15, INK, (left + cells * cell + 80, h // 2))


def _telemetry(surface: pygame.Surface, rng: random.Random) -> None:
    w, h = surface.get_size()
    surface.fill((16, 24, 20))
    for x in range(0, w, 40):
        pygame.draw.line(surface, (32, 52, 40), (x, 0), (x, h))
    for y in range(0, h, 38):
        pygame.draw.line(surface, (32, 52, 40), (0, y), (w, y))
    cut = int(w * 0.62)
    points = [(x, h // 2 + math.sin(x / 26) * 26 + rng.randint(-2, 2)) for x in range(10, cut, 4)]
    pygame.draw.lines(surface, (110, 230, 130), False, points, 3)
    noisy = [(x, rng.randint(10, h - 10)) for x in range(cut, w - 10, 6)]
    pygame.draw.lines(surface, (230, 110, 90), False, noisy, 2)
    pygame.draw.line(surface, (240, 210, 90), (cut, 0), (cut, h), 2)
    _text(surface, "14:01", 13, (240, 210, 90), (cut - 30, 14))
    _text(surface, "14:02  dados corrompidos", 13, (230, 110, 90), (cut + 118, 14))
    _text(surface, "giroscópio (graus)", 13, (110, 230, 130), (110, h - 14))


ARTS = {
    "radar": _radar,
    "face_round": _face_round,
    "face_square": _face_square,
    "crowd": _crowd,
    "serial": _serial,
    "gps": _gps,
    "mall": _mall,
    "badge": _badge,
    "qr": _qr,
    "telemetry": _telemetry,
}


# --- insets: details that are always painted by code -----------------------------------------


def draw_plate_inset(surface: pygame.Surface, rect: pygame.Rect, text: str, muddy: bool, seed: str) -> None:
    """A magnified crop of a license plate, like the corner box of a radar photo."""
    rng = random.Random(seed)
    pygame.draw.rect(surface, (0, 0, 0), rect.inflate(6, 6))
    pygame.draw.rect(surface, (230, 230, 218), rect)
    pygame.draw.rect(surface, (40, 70, 160), (rect.x, rect.y, rect.width, 14))
    _text(surface, "BRASIL", 10, (255, 255, 255), (rect.centerx, rect.y + 7))
    _text(surface, text, max(16, rect.height // 2), (40, 36, 32), (rect.centerx, rect.centery + 8))
    if muddy:
        for _ in range(110):
            px = rng.randrange(rect.x, rect.right)
            py = rng.randrange(rect.y + 12, rect.bottom)
            pygame.draw.circle(surface, (96, 70, 42), (px, py), rng.randint(1, 3))


def pixelate_picture(image: pygame.Surface, size: tuple[int, int], cell: int = 4, levels: int = 6) -> pygame.Surface:
    """Real photo -> painterly pixel art that matches the game: chunky cells, few colours, warm-green tint."""
    width, height = size
    small = pygame.transform.smoothscale(image.convert(), (max(1, width // cell), max(1, height // cell)))
    step = 255 / (levels - 1)
    for y in range(small.get_height()):
        for x in range(small.get_width()):
            r, g, b, _ = small.get_at((x, y))
            r, g, b = (round(round(c / step) * step) for c in (r, g, b))
            luma = (r + g + b) / 3
            r, g, b = (int(c * 0.72 + luma * 0.28) for c in (r, g, b))  # slightly washed, like an old monitor
            small.set_at((x, y), (min(255, int(r * 0.96 + 6)), min(255, int(g * 1.02 + 8)), min(255, int(b * 0.9 + 4))))
    return pygame.transform.scale(small, (small.get_width() * cell, small.get_height() * cell))


def draw_newsroom_placeholder(size: tuple[int, int], seed: str) -> pygame.Surface:
    """Stand-in for a case's own newspaper picture (see prompts_jornal.md) until it is delivered.

    A generic halftone newsprint texture with a "story still being verified" stamp, so an empty
    slot reads as an intentional placeholder rather than a broken image.
    """
    rng = random.Random(seed)
    width, height = size
    surface = pygame.Surface(size)
    base = 158 + rng.randrange(-6, 6)
    surface.fill((base, base - 6, base - 16))
    dot = max(2, height // 60)
    for y in range(0, height, dot * 2):
        for x in range(0, width, dot * 2):
            shade = base - 30 - rng.randrange(0, 26)
            pygame.draw.circle(surface, (shade, shade - 4, shade - 10), (x + dot, y + dot), dot // 2 + 1)
    pygame.draw.rect(surface, (70, 62, 50), surface.get_rect(), max(2, height // 60))
    label = pygame.Surface((width + 80, 46), pygame.SRCALPHA)
    pygame.draw.rect(label, (52, 44, 34), (0, 0, label.get_width(), 46))
    _text(label, "MATÉRIA EM APURAÇÃO", max(14, height // 12), (232, 220, 190), (label.get_width() // 2, 23))
    tilted = pygame.transform.rotate(label, -6)
    surface.blit(tilted, tilted.get_rect(center=(width // 2, height // 2)))
    return surface
