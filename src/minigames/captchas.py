"""The 'prove you are human' mini-games. Each one lives on a 720x360 canvas.

Coordinates given to the event handlers are already local to that canvas.
Every game works without extra art (drawings are made in code) and picks up the
optional images from assets/captcha/ when they exist.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import pygame

from src.minigames.common import (
    AMBER,
    BORDER,
    BORDER_DARK,
    CYAN,
    GREEN,
    INK,
    INK_BRIGHT,
    INK_MUTED,
    PANEL,
    PANEL_MID,
    RED,
    SCREEN_BLACK,
    draw_button,
    draw_text,
    draw_wrapped,
    fit_box,
    fit_square,
    font,
    load_folder,
    load_optional_image,
    load_rotate_photos,
    load_scientists,
    ROTATE_PHOTO_INSTRUCTIONS,
)

CANVAS = (720, 360)


class Captcha:
    """Base class: a small game the player must win to continue working."""

    kind = "base"
    title = "VERIFICAÇÃO HUMANA"
    instruction = ""

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        self.rng = rng
        self.assets_root = Path(assets_root)
        self.solved = False
        self.failures = 0
        self.events: list[str] = []
        self.hover: tuple[int, int] | None = None

    # -- lifecycle -------------------------------------------------------
    def update(self, dt: float) -> None:  # pragma: no cover - default is static
        return None

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        return None

    def on_mouse_up(self, pos: tuple[int, int]) -> None:
        return None

    def on_mouse_move(self, pos: tuple[int, int]) -> None:
        self.hover = pos

    def on_key(self, event: pygame.event.Event) -> None:
        return None

    def render(self, surface: pygame.Surface) -> None:
        raise NotImplementedError

    # -- helpers ---------------------------------------------------------
    def take_events(self) -> list[str]:
        events, self.events = self.events, []
        return events

    def fail(self) -> None:
        self.failures += 1
        self.events.append("error")

    def win(self) -> None:
        self.solved = True
        self.events.append("success")

    def hovering(self, rect: pygame.Rect) -> bool:
        return self.hover is not None and rect.collidepoint(self.hover)


# ---------------------------------------------------------------------------
# 1. Wobbly text
# ---------------------------------------------------------------------------
class WobblyTextCaptcha(Captcha):
    kind = "wobbly"
    instruction = "Digite as letras que aparecem na imagem e aperte Enter."
    ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ2345679"
    VERIFY = pygame.Rect(240, 304, 240, 44)
    REFRESH = pygame.Rect(496, 304, 180, 44)

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.entry = ""
        self.text = ""
        self.image = pygame.Surface((10, 10))
        self.time = 0.0
        self._new_text()

    def _new_text(self) -> None:
        self.text = "".join(self.rng.choice(self.ALPHABET) for _ in range(5))
        self.image = self._build_image()

    def _build_image(self) -> pygame.Surface:
        image = pygame.Surface((520, 130), pygame.SRCALPHA)
        image.fill((22, 30, 24))
        for _ in range(9):
            color = (self.rng.randrange(60, 140), self.rng.randrange(80, 160), self.rng.randrange(50, 120))
            pygame.draw.line(
                image,
                color,
                (self.rng.randrange(520), self.rng.randrange(130)),
                (self.rng.randrange(520), self.rng.randrange(130)),
                self.rng.choice((1, 2)),
            )
        big = font(72, True)
        for index, char in enumerate(self.text):
            glyph = big.render(char, False, (self.rng.randrange(190, 250), self.rng.randrange(190, 250), self.rng.randrange(100, 190)))
            glyph = pygame.transform.rotate(glyph, self.rng.randint(-22, 22))
            image.blit(glyph, glyph.get_rect(center=(70 + index * 94, 68 + self.rng.randint(-14, 14))))
        for _ in range(140):
            image.set_at((self.rng.randrange(520), self.rng.randrange(130)), (210, 220, 150))
        return image

    def update(self, dt: float) -> None:
        self.time += dt

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.VERIFY.collidepoint(pos):
            self._check()
        elif self.REFRESH.collidepoint(pos):
            self.entry = ""
            self._new_text()
            self.events.append("click")

    def on_key(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_BACKSPACE:
            self.entry = self.entry[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._check()
        else:
            typed = getattr(event, "unicode", "").upper()
            if typed and typed in self.ALPHABET + "01" and len(self.entry) < len(self.text):
                self.entry += typed
                self.events.append("click")

    def _check(self) -> None:
        if self.entry == self.text:
            self.win()
            return
        self.entry = ""
        self._new_text()
        self.fail()

    def render(self, surface: pygame.Surface) -> None:
        wobble = int(math.sin(self.time * 3) * 3)
        surface.blit(self.image, (100, 20 + wobble))
        pygame.draw.rect(surface, BORDER, pygame.Rect(100, 20 + wobble, 520, 130), 3)
        box = pygame.Rect(240, 190, 240, 64)
        pygame.draw.rect(surface, SCREEN_BLACK, box)
        pygame.draw.rect(surface, INK_BRIGHT, box, 3)
        shown = self.entry + ("_" if int(self.time * 2) % 2 == 0 and len(self.entry) < len(self.text) else "")
        draw_text(surface, shown, font(44, True), INK_BRIGHT, box.center, "center")
        draw_text(surface, "SUA RESPOSTA", font(15), INK_MUTED, (box.x, box.y - 20))
        draw_button(surface, self.VERIFY, "VERIFICAR", self.hovering(self.VERIFY))
        draw_button(surface, self.REFRESH, "OUTRO TEXTO", self.hovering(self.REFRESH), BORDER_DARK, 17)


# ---------------------------------------------------------------------------
# 2. Cat grid
# ---------------------------------------------------------------------------
def _draw_cat(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    palette = ((232, 150, 62), (150, 152, 165), (44, 44, 54), (232, 228, 214), (198, 120, 88))
    fur = palette[variant % len(palette)]
    dark = tuple(max(0, c - 60) for c in fur)
    cx, cy = rect.center
    pygame.draw.polygon(surface, fur, [(cx - 34, cy - 8), (cx - 30, cy - 40), (cx - 10, cy - 22)])
    pygame.draw.polygon(surface, fur, [(cx + 34, cy - 8), (cx + 30, cy - 40), (cx + 10, cy - 22)])
    pygame.draw.polygon(surface, (240, 160, 170), [(cx - 29, cy - 16), (cx - 28, cy - 32), (cx - 18, cy - 22)])
    pygame.draw.polygon(surface, (240, 160, 170), [(cx + 29, cy - 16), (cx + 28, cy - 32), (cx + 18, cy - 22)])
    pygame.draw.ellipse(surface, fur, pygame.Rect(cx - 36, cy - 26, 72, 62))
    for side in (-1, 1):
        eye = pygame.Rect(cx + side * 16 - 7, cy - 6, 14, 15)
        pygame.draw.ellipse(surface, (200, 230, 120), eye)
        pygame.draw.ellipse(surface, (10, 10, 10), eye.inflate(-9, 0))
        for i in range(3):
            pygame.draw.line(surface, dark, (cx + side * 22, cy + 12 + i * 4), (cx + side * 46, cy + 8 + i * 6), 1)
    pygame.draw.polygon(surface, (240, 130, 150), [(cx - 4, cy + 9), (cx + 4, cy + 9), (cx, cy + 15)])
    pygame.draw.lines(surface, dark, False, [(cx - 8, cy + 20), (cx, cy + 16), (cx + 8, cy + 20)], 2)


def _draw_dog(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    fur = ((170, 116, 66), (90, 66, 44))[variant % 2]
    cx, cy = rect.center
    pygame.draw.ellipse(surface, tuple(max(0, c - 40) for c in fur), pygame.Rect(cx - 44, cy - 24, 24, 52))
    pygame.draw.ellipse(surface, tuple(max(0, c - 40) for c in fur), pygame.Rect(cx + 20, cy - 24, 24, 52))
    pygame.draw.ellipse(surface, fur, pygame.Rect(cx - 30, cy - 30, 60, 64))
    pygame.draw.ellipse(surface, (226, 200, 160), pygame.Rect(cx - 17, cy + 2, 34, 26))
    pygame.draw.ellipse(surface, (12, 12, 12), pygame.Rect(cx - 7, cy + 4, 14, 9))
    for side in (-1, 1):
        pygame.draw.circle(surface, (16, 16, 16), (cx + side * 13, cy - 8), 5)


def _draw_bread(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    cx, cy = rect.center
    body = pygame.Rect(cx - 40, cy - 22, 80, 50)
    pygame.draw.rect(surface, (206, 150, 76), body, border_radius=22)
    pygame.draw.rect(surface, (150, 96, 44), body, 3, border_radius=22)
    for i in range(3):
        pygame.draw.line(surface, (240, 206, 130), (cx - 22 + i * 18, cy - 12), (cx - 12 + i * 18, cy + 16), 3)


def _draw_robot(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    cx, cy = rect.center
    pygame.draw.line(surface, (180, 180, 190), (cx, cy - 40), (cx, cy - 26), 3)
    pygame.draw.circle(surface, RED, (cx, cy - 42), 5)
    head = pygame.Rect(cx - 34, cy - 26, 68, 58)
    pygame.draw.rect(surface, (150, 156, 170), head, border_radius=8)
    pygame.draw.rect(surface, (80, 86, 100), head, 3, border_radius=8)
    for side in (-1, 1):
        pygame.draw.rect(surface, CYAN, pygame.Rect(cx + side * 16 - 8, cy - 12, 16, 14))
    for i in range(4):
        pygame.draw.line(surface, (60, 64, 76), (cx - 16 + i * 11, cy + 14), (cx - 16 + i * 11, cy + 24), 3)


def _draw_owl(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    cx, cy = rect.center
    pygame.draw.polygon(surface, (110, 78, 50), [(cx - 32, cy - 20), (cx - 26, cy - 40), (cx - 12, cy - 26)])
    pygame.draw.polygon(surface, (110, 78, 50), [(cx + 32, cy - 20), (cx + 26, cy - 40), (cx + 12, cy - 26)])
    pygame.draw.ellipse(surface, (130, 92, 60), pygame.Rect(cx - 36, cy - 30, 72, 70))
    for side in (-1, 1):
        pygame.draw.circle(surface, (238, 224, 170), (cx + side * 16, cy - 6), 14)
        pygame.draw.circle(surface, (250, 190, 40), (cx + side * 16, cy - 6), 8)
        pygame.draw.circle(surface, (10, 10, 10), (cx + side * 16, cy - 6), 4)
    pygame.draw.polygon(surface, (236, 160, 50), [(cx - 5, cy + 6), (cx + 5, cy + 6), (cx, cy + 18)])


def _draw_rabbit(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    cx, cy = rect.center
    for side in (-1, 1):
        pygame.draw.ellipse(surface, (232, 228, 224), pygame.Rect(cx + side * 16 - 9, cy - 46, 18, 46))
        pygame.draw.ellipse(surface, (240, 170, 180), pygame.Rect(cx + side * 16 - 4, cy - 40, 8, 32))
    pygame.draw.ellipse(surface, (238, 234, 228), pygame.Rect(cx - 32, cy - 14, 64, 56))
    for side in (-1, 1):
        pygame.draw.circle(surface, (30, 30, 34), (cx + side * 13, cy + 6), 4)
    pygame.draw.circle(surface, (240, 150, 160), (cx, cy + 16), 4)


NON_CAT_DRAWERS = (_draw_dog, _draw_bread, _draw_robot, _draw_owl, _draw_rabbit)


class CatGridCaptcha(Captcha):
    kind = "cats"
    instruction = "Selecione todas as imagens que têm GATOS."
    VERIFY = pygame.Rect(440, 300, 240, 44)
    TILE = 104
    GAP = 8
    ORIGIN = (36, 10)

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.cat_images = load_folder(assets_root, "captcha/tiles", "cat_")
        self.other_images = load_folder(assets_root, "captcha/tiles", "other_")
        self.tiles: list[tuple[bool, int]] = []
        self.selected: set[int] = set()
        self._deal()

    def _deal(self) -> None:
        cats = self.rng.randint(3, 5)
        cat_pool = len(self.cat_images) or 5
        other_pool = len(self.other_images) or len(NON_CAT_DRAWERS)
        tiles = [(True, self.rng.randrange(cat_pool)) for _ in range(cats)]
        tiles += [(False, self.rng.randrange(other_pool)) for _ in range(9 - cats)]
        self.rng.shuffle(tiles)
        self.tiles = tiles
        self.selected = set()

    def tile_rect(self, index: int) -> pygame.Rect:
        row, column = divmod(index, 3)
        return pygame.Rect(
            self.ORIGIN[0] + column * (self.TILE + self.GAP),
            self.ORIGIN[1] + row * (self.TILE + self.GAP),
            self.TILE,
            self.TILE,
        )

    def cat_indices(self) -> set[int]:
        return {index for index, (is_cat, _) in enumerate(self.tiles) if is_cat}

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        for index in range(9):
            if self.tile_rect(index).collidepoint(pos):
                self.selected.symmetric_difference_update({index})
                self.events.append("toggle")
                return
        if self.VERIFY.collidepoint(pos):
            if self.selected == self.cat_indices():
                self.win()
            else:
                self.fail()
                self._deal()

    def render(self, surface: pygame.Surface) -> None:
        for index, (is_cat, variant) in enumerate(self.tiles):
            rect = self.tile_rect(index)
            pygame.draw.rect(surface, (32, 44, 36) if (index % 2) else (38, 50, 42), rect)
            images = self.cat_images if is_cat else self.other_images
            if images:
                image = pygame.transform.smoothscale(images[variant % len(images)], rect.size)
                surface.blit(image, rect)
            elif is_cat:
                _draw_cat(surface, rect, variant)
            else:
                NON_CAT_DRAWERS[variant % len(NON_CAT_DRAWERS)](surface, rect, variant)
            selected = index in self.selected
            pygame.draw.rect(surface, AMBER if selected else BORDER_DARK, rect, 4 if selected else 2)
            if selected:
                pygame.draw.circle(surface, AMBER, (rect.right - 14, rect.y + 14), 11)
                pygame.draw.lines(surface, SCREEN_BLACK, False, [(rect.right - 20, rect.y + 14), (rect.right - 15, rect.y + 19), (rect.right - 8, rect.y + 9)], 3)
        draw_wrapped(surface, "Clique em cada quadrado que tenha um gato. Depois verifique.", font(19), INK, pygame.Rect(440, 40, 240, 120), 26)
        draw_wrapped(surface, "Atenção: nem tudo que é fofo é gato.", font(15), INK_MUTED, pygame.Rect(440, 180, 240, 40), 20)
        draw_button(surface, self.VERIFY, "VERIFICAR", self.hovering(self.VERIFY))


# ---------------------------------------------------------------------------
# 3. Rotate the portrait upright
# ---------------------------------------------------------------------------
def _sky_and_ground(size: int, ground_top: int) -> pygame.Surface:
    scene = pygame.Surface((size, size), pygame.SRCALPHA)
    for y in range(size):
        shade = y / size
        pygame.draw.line(scene, (70 + int(90 * shade), 150 + int(70 * shade), 230), (0, y), (size, y))
    pygame.draw.circle(scene, (255, 226, 90), (size - 56, 52), 26)  # the sun is always up
    for cx, cy in ((54, 60), (150, 34)):
        for dx, dy, r in ((0, 0, 16), (16, 4, 13), (-16, 5, 12)):
            pygame.draw.circle(scene, (250, 250, 255), (cx + dx, cy + dy), r)
    pygame.draw.rect(scene, (74, 168, 84), (0, ground_top, size, size - ground_top))
    pygame.draw.rect(scene, (52, 130, 62), (0, ground_top, size, 6))
    return scene


def _scene_person(size: int) -> pygame.Surface:
    scene = _sky_and_ground(size, 176)
    cx = size // 2
    pygame.draw.line(scene, (40, 40, 60), (cx - 8, 138), (cx - 12, 186), 8)  # legs
    pygame.draw.line(scene, (40, 40, 60), (cx + 8, 138), (cx + 12, 186), 8)
    pygame.draw.ellipse(scene, (30, 30, 30), (cx - 26, 182, 20, 10))  # shoes
    pygame.draw.ellipse(scene, (30, 30, 30), (cx + 6, 182, 20, 10))
    pygame.draw.rect(scene, (220, 70, 60), (cx - 20, 88, 40, 56), border_radius=8)  # shirt
    pygame.draw.line(scene, (220, 70, 60), (cx - 20, 96), (cx - 42, 128), 8)  # arms
    pygame.draw.line(scene, (220, 70, 60), (cx + 20, 96), (cx + 42, 128), 8)
    pygame.draw.circle(scene, (238, 200, 160), (cx, 66), 22)  # head
    pygame.draw.circle(scene, (250, 250, 250), (cx - 8, 62), 5)
    pygame.draw.circle(scene, (250, 250, 250), (cx + 8, 62), 5)
    pygame.draw.circle(scene, (20, 20, 20), (cx - 8, 63), 2)
    pygame.draw.circle(scene, (20, 20, 20), (cx + 8, 63), 2)
    pygame.draw.arc(scene, (150, 60, 50), (cx - 10, 68, 20, 14), math.pi * 1.1, math.pi * 1.9, 3)
    pygame.draw.rect(scene, (60, 40, 30), (cx - 22, 42, 44, 12), border_top_left_radius=12, border_top_right_radius=12)  # hair
    pygame.draw.rect(scene, (120, 84, 50), (28, 150, 10, 30))  # tree
    pygame.draw.circle(scene, (40, 130, 60), (33, 140), 22)
    return scene


def _scene_house(size: int) -> pygame.Surface:
    scene = _sky_and_ground(size, 170)
    pygame.draw.rect(scene, (236, 210, 150), (66, 104, 108, 76))
    pygame.draw.polygon(scene, (190, 70, 60), [(54, 108), (120, 52), (186, 108)])
    pygame.draw.rect(scene, (150, 60, 50), (150, 56, 14, 30))  # chimney
    for k in range(3):  # smoke rises
        pygame.draw.circle(scene, (235, 235, 240), (160 + k * 5, 44 - k * 14), 7 + k * 2)
    pygame.draw.rect(scene, (110, 70, 44), (108, 134, 26, 46))  # door
    pygame.draw.circle(scene, (240, 200, 60), (128, 158), 2)
    for x in (76, 146):
        pygame.draw.rect(scene, (120, 190, 240), (x, 118, 22, 20))
        pygame.draw.rect(scene, (80, 60, 40), (x, 118, 22, 20), 2)
    pygame.draw.polygon(scene, (200, 180, 140), [(108, 180), (134, 180), (150, 236), (90, 236)])  # path
    return scene


def _scene_rocket(size: int) -> pygame.Surface:
    scene = _sky_and_ground(size, 190)
    cx = size // 2
    pygame.draw.polygon(scene, (255, 170, 40), [(cx - 12, 168), (cx + 12, 168), (cx, 206)])  # flame is below
    pygame.draw.ellipse(scene, (236, 236, 244), (cx - 20, 50, 40, 124))
    pygame.draw.polygon(scene, (210, 50, 50), [(cx - 20, 82), (cx + 20, 82), (cx, 42)])  # red nose on top
    pygame.draw.circle(scene, (70, 140, 210), (cx, 104), 11)
    pygame.draw.circle(scene, (30, 60, 100), (cx, 104), 11, 3)
    pygame.draw.polygon(scene, (210, 50, 50), [(cx - 20, 140), (cx - 42, 176), (cx - 20, 164)])
    pygame.draw.polygon(scene, (210, 50, 50), [(cx + 20, 140), (cx + 42, 176), (cx + 20, 164)])
    return scene


def _scene_robot(size: int) -> pygame.Surface:
    scene = _sky_and_ground(size, 184)
    cx = size // 2
    pygame.draw.rect(scene, (110, 120, 140), (cx - 30, 118, 60, 58), border_radius=6)  # body
    pygame.draw.rect(scene, (80, 90, 110), (cx - 30, 176, 22, 14))  # feet
    pygame.draw.rect(scene, (80, 90, 110), (cx + 8, 176, 22, 14))
    pygame.draw.rect(scene, (150, 160, 180), (cx - 36, 58, 72, 56), border_radius=10)  # head
    pygame.draw.circle(scene, (110, 230, 130), (cx - 14, 84), 8)
    pygame.draw.circle(scene, (110, 230, 130), (cx + 14, 84), 8)
    pygame.draw.line(scene, (80, 90, 110), (cx, 58), (cx, 38), 4)  # antenna on top
    pygame.draw.circle(scene, (230, 80, 70), (cx, 34), 6)
    pygame.draw.line(scene, (80, 90, 110), (cx - 30, 130), (cx - 50, 156), 7)
    pygame.draw.line(scene, (80, 90, 110), (cx + 30, 130), (cx + 50, 156), 7)
    return scene


ROTATE_SCENES = (
    (_scene_person, "Gire a imagem até a pessoa ficar em pé."),
    (_scene_house, "Gire a imagem até a casa ficar em pé."),
    (_scene_rocket, "Gire a imagem até o foguete apontar para cima."),
    (_scene_robot, "Gire a imagem até o robô ficar em pé."),
)


class RotateCaptcha(Captcha):
    kind = "rotate"
    instruction = "Gire a imagem até a pessoa ficar em pé."
    LEFT = pygame.Rect(180, 304, 90, 44)
    RIGHT = pygame.Rect(450, 304, 90, 44)
    VERIFY = pygame.Rect(280, 304, 160, 44)
    CENTER = (360, 150)
    SIZE = 240
    TOLERANCE = 12

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        options: list[tuple] = list(ROTATE_SCENES)
        for name, photo in load_rotate_photos(assets_root).items():
            instruction = ROTATE_PHOTO_INSTRUCTIONS.get(name, "Gire a imagem até ficar em pé.")
            options.append((lambda size, image=photo: fit_square(image, size), instruction))
        drawer, self.instruction = rng.choice(options)
        self.image = drawer(self.SIZE)
        self.angle = rng.choice([-1, 1]) * rng.randrange(45, 166, 15)
        self.dragging = False
        self._last_x = 0
        self._mask = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self._mask, (255, 255, 255, 255), (self.SIZE // 2, self.SIZE // 2), self.SIZE // 2)

    def upright(self) -> bool:
        wrapped = ((self.angle + 180) % 360) - 180
        return abs(wrapped) <= self.TOLERANCE

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.LEFT.collidepoint(pos):
            self.angle -= 15
            self.events.append("click")
        elif self.RIGHT.collidepoint(pos):
            self.angle += 15
            self.events.append("click")
        elif self.VERIFY.collidepoint(pos):
            self.win() if self.upright() else self.fail()
        elif pygame.Vector2(pos).distance_to(self.CENTER) < self.SIZE / 2 + 10:
            self.dragging = True
            self._last_x = pos[0]

    def on_mouse_up(self, pos: tuple[int, int]) -> None:
        self.dragging = False

    def on_mouse_move(self, pos: tuple[int, int]) -> None:
        super().on_mouse_move(pos)
        if self.dragging:
            self.angle += (pos[0] - self._last_x) * 0.9
            self._last_x = pos[0]

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, (28, 38, 32), self.CENTER, self.SIZE // 2 + 8)
        frame = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        rotated = pygame.transform.rotate(self.image, -self.angle)
        frame.blit(rotated, rotated.get_rect(center=(self.SIZE // 2, self.SIZE // 2)))
        frame.blit(self._mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)  # keep the picture inside the circle
        surface.blit(frame, frame.get_rect(center=self.CENTER))
        pygame.draw.circle(surface, AMBER if self.upright() else BORDER, self.CENTER, self.SIZE // 2 + 8, 4)
        draw_text(surface, "arraste a foto ou use as setas", font(15), INK_MUTED, (self.CENTER[0], 286), "midtop")
        for rect, direction in ((self.LEFT, -1), (self.RIGHT, 1)):
            hovered = self.hovering(rect)
            pygame.draw.rect(surface, PANEL_MID if hovered else PANEL, rect)
            pygame.draw.rect(surface, INK_BRIGHT if hovered else AMBER, rect, 3)
            cx, cy = rect.center
            pygame.draw.polygon(surface, INK_BRIGHT, [(cx + 10 * direction, cy), (cx - 10 * direction, cy - 12), (cx - 10 * direction, cy + 12)])
        draw_button(surface, self.VERIFY, "É ESSA!", self.hovering(self.VERIFY))


# ---------------------------------------------------------------------------
# 4. Swap jigsaw
# ---------------------------------------------------------------------------
class SwapPuzzleCaptcha(Captcha):
    kind = "puzzle"
    instruction = "Monte o quebra-cabeça: clique em duas peças para trocá-las de lugar."
    PIECE = 108
    ORIGIN = (36, 12)

    def __init__(self, rng: random.Random, assets_root: Path, columns: int = 3, rows: int = 2) -> None:
        super().__init__(rng, assets_root)
        self.columns, self.rows = columns, rows
        portraits = load_scientists(assets_root)
        board = (columns * self.PIECE, rows * self.PIECE)
        self.image = fit_box(rng.choice(portraits), board) if portraits else self._fallback(board)
        count = columns * rows
        slots = list(range(count))
        while sum(1 for i, s in enumerate(slots) if i == s) > count // 3:
            rng.shuffle(slots)
        self.slots = slots
        self.selected: int | None = None

    @staticmethod
    def _fallback(board: tuple[int, int]) -> pygame.Surface:
        image = pygame.Surface(board)
        for y in range(board[1]):
            pygame.draw.line(image, (60 + y // 3 % 120, 110, 90), (0, y), (board[0], y))
        pygame.draw.circle(image, (230, 200, 150), (board[0] // 2, board[1] // 2 - 20), 60)
        return image

    def slot_rect(self, index: int) -> pygame.Rect:
        row, column = divmod(index, self.columns)
        return pygame.Rect(self.ORIGIN[0] + column * self.PIECE, self.ORIGIN[1] + row * self.PIECE, self.PIECE, self.PIECE)

    def piece_source(self, piece: int) -> pygame.Rect:
        row, column = divmod(piece, self.columns)
        return pygame.Rect(column * self.PIECE, row * self.PIECE, self.PIECE, self.PIECE)

    def is_complete(self) -> bool:
        return all(index == piece for index, piece in enumerate(self.slots))

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        for index in range(len(self.slots)):
            if not self.slot_rect(index).collidepoint(pos):
                continue
            if self.selected is None:
                self.selected = index
                self.events.append("toggle")
            elif self.selected == index:
                self.selected = None
            else:
                other = self.selected
                self.slots[index], self.slots[other] = self.slots[other], self.slots[index]
                self.selected = None
                self.events.append("click")
                if self.is_complete():
                    self.win()
            return

    def render(self, surface: pygame.Surface) -> None:
        for index, piece in enumerate(self.slots):
            rect = self.slot_rect(index)
            surface.blit(self.image, rect, self.piece_source(piece))
            correct = index == piece
            pygame.draw.rect(surface, GREEN if correct else BORDER_DARK, rect, 3 if correct else 1)
            if self.selected == index:
                pygame.draw.rect(surface, AMBER, rect, 5)
        preview_width = 220
        preview = pygame.transform.smoothscale(self.image, (preview_width, round(preview_width * self.image.get_height() / self.image.get_width())))
        origin = (470, 40)
        surface.blit(preview, origin)
        pygame.draw.rect(surface, BORDER, pygame.Rect(origin, preview.get_size()), 2)
        draw_text(surface, "É ISTO QUE VOCÊ PRECISA MONTAR", font(14), INK_MUTED, (origin[0], origin[1] - 20))
        right = sum(1 for i, p in enumerate(self.slots) if i == p)
        draw_text(surface, f"{right} de {len(self.slots)} peças no lugar", font(18, True), INK_BRIGHT, (origin[0], origin[1] + preview.get_height() + 20))


# ---------------------------------------------------------------------------
# 5. Memory pairs
# ---------------------------------------------------------------------------
class MemoryCaptcha(Captcha):
    kind = "memory"
    instruction = "Encontre os pares de cartas iguais."
    CARD = (96, 108)
    GAP = 12
    ORIGIN = (28, 8)

    def __init__(self, rng: random.Random, assets_root: Path, pairs: int = 4) -> None:
        super().__init__(rng, assets_root)
        portraits = load_scientists(assets_root)
        rng.shuffle(portraits)
        self.faces = [fit_square(image, 84) for image in portraits[:pairs]]
        while len(self.faces) < pairs:  # never happens with the six protocol portraits
            self.faces.append(self._fallback(len(self.faces)))
        self.back = load_optional_image(assets_root, "captcha/cards/card_back.png")
        cards = list(range(pairs)) * 2
        rng.shuffle(cards)
        self.cards = cards
        self.up: set[int] = set()
        self.matched: set[int] = set()
        self.pending: list[int] = []
        self.wait = 0.0
        self.flips = 0
        self.columns = 4

    @staticmethod
    def _fallback(seed: int) -> pygame.Surface:
        image = pygame.Surface((84, 84))
        image.fill((40 + seed * 30 % 160, 90, 120))
        return image

    def card_rect(self, index: int) -> pygame.Rect:
        row, column = divmod(index, self.columns)
        return pygame.Rect(
            self.ORIGIN[0] + column * (self.CARD[0] + self.GAP),
            self.ORIGIN[1] + row * (self.CARD[1] + self.GAP),
            *self.CARD,
        )

    def update(self, dt: float) -> None:
        if self.wait > 0:
            self.wait -= dt
            if self.wait <= 0:
                for index in self.pending:
                    self.up.discard(index)
                self.pending = []

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.wait > 0:
            return
        for index in range(len(self.cards)):
            if index in self.up or index in self.matched or not self.card_rect(index).collidepoint(pos):
                continue
            self.up.add(index)
            self.events.append("click")
            self.pending.append(index)
            if len(self.pending) == 2:
                self.flips += 1
                first, second = self.pending
                if self.cards[first] == self.cards[second]:
                    self.matched.update(self.pending)
                    self.pending = []
                    self.events.append("toggle")
                    if len(self.matched) == len(self.cards):
                        self.win()
                else:
                    self.wait = 0.75
            return

    def render(self, surface: pygame.Surface) -> None:
        for index, card in enumerate(self.cards):
            rect = self.card_rect(index)
            face_up = index in self.up or index in self.matched
            pygame.draw.rect(surface, (40, 50, 42) if face_up else PANEL_MID, rect)
            if face_up:
                surface.blit(self.faces[card], self.faces[card].get_rect(center=rect.center))
                pygame.draw.rect(surface, GREEN if index in self.matched else AMBER, rect, 4)
            else:
                if self.back is not None:
                    surface.blit(pygame.transform.smoothscale(self.back, rect.size), rect)
                else:
                    pygame.draw.rect(surface, (20, 44, 36), rect.inflate(-12, -12))
                    pygame.draw.circle(surface, GREEN, rect.center, 18, 3)
                    pygame.draw.circle(surface, GREEN, rect.center, 6)
                pygame.draw.rect(surface, BORDER if self.hovering(rect) else BORDER_DARK, rect, 3)
        draw_text(surface, f"Pares: {len(self.matched) // 2} de {len(self.cards) // 2}", font(22, True), INK_BRIGHT, (480, 60))
        draw_text(surface, f"Jogadas: {self.flips}", font(18), INK, (480, 100))
        draw_wrapped(surface, "Vire duas cartas por vez. Se forem iguais, elas ficam abertas.", font(16), INK_MUTED, pygame.Rect(480, 150, 220, 100), 22)


# ---------------------------------------------------------------------------
# 6. Space invaders
# ---------------------------------------------------------------------------
INVADER_FRAMES = (
    (
        ("..#.....#..", "...#...#...", "..#######..", ".##.###.##.", "###########", "#.#######.#", "#.#.....#.#", "...##.##..."),
        ("..#.....#..", "#..#...#..#", "#.#######.#", "###.###.###", "###########", ".#########.", "..#.....#..", ".#.......#."),
    ),
    (
        ("...####...", ".########.", "##########", "###..##..##", "##########", "..##..##..", ".##.##.##.", "##......##"),
        ("...####...", ".########.", "##########", "###..##..##", "##########", "..##..##..", "##.####.##", ".#......#."),
    ),
    (
        ("....##....", "...####...", "..######..", ".##.##.##.", "##########", "..#.##.#..", ".#......#.", "..#....#.."),
        ("....##....", "...####...", "..######..", ".##.##.##.", "##########", ".#..##..#.", "#.#....#.#", ".#......#."),
    ),
)
PLAYER_SPRITE = ("....#....", "...###...", "...###...", ".#######.", "#########", "#########")


def _pixel_surface(rows: tuple[str, ...], color: tuple[int, int, int], scale: int) -> pygame.Surface:
    width = max(len(row) for row in rows)
    surface = pygame.Surface((width * scale, len(rows) * scale), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char == "#":
                pygame.draw.rect(surface, color, (x * scale, y * scale, scale, scale))
    return surface


class InvadersCaptcha(Captcha):
    kind = "invaders"
    instruction = "Mova o mouse, clique para atirar e derrote todos os bots."
    COLUMNS = 5
    ROWS = 3
    ENEMY = (46, 34)
    SPACING = (66, 52)

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.images = load_folder(assets_root, "captcha/invaders", "enemy_")
        self.player_image = load_optional_image(assets_root, "captcha/invaders/player_ship.png")
        self.enemy_colors = ((120, 230, 130), (110, 200, 230), (240, 200, 90))
        self.sprites = [
            [_pixel_surface(frame, self.enemy_colors[kind], 4) for frame in frames]
            for kind, frames in enumerate(INVADER_FRAMES)
        ]
        self.player_sprite = _pixel_surface(PLAYER_SPRITE, (247, 239, 161), 5)
        self.player_x = CANVAS[0] / 2
        self.target_x = CANVAS[0] / 2
        self.move = 0
        self.cooldown = 0.0
        self.time = 0.0
        self.bullets: list[pygame.Vector2] = []
        self.enemies: list[dict] = []
        self.direction = 1
        self.kills = 0
        self._reset_wave()

    def _reset_wave(self) -> None:
        self.enemies = [
            {"pos": pygame.Vector2(80 + column * self.SPACING[0], 30 + row * self.SPACING[1]), "kind": row % 3}
            for row in range(self.ROWS)
            for column in range(self.COLUMNS)
        ]
        self.bullets = []
        self.direction = 1

    @property
    def player_y(self) -> float:
        return CANVAS[1] - 46

    def on_mouse_move(self, pos: tuple[int, int]) -> None:
        super().on_mouse_move(pos)
        self.target_x = pos[0]

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        self.fire()

    def on_key(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.move = -1
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.move = 1
            elif event.key == pygame.K_SPACE:
                self.fire()
        elif event.type == pygame.KEYUP and event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
            self.move = 0

    def fire(self) -> None:
        if self.cooldown <= 0 and not self.solved:
            self.bullets.append(pygame.Vector2(self.player_x, self.player_y - 10))
            self.cooldown = 0.3
            self.events.append("click")

    def update(self, dt: float) -> None:
        if self.solved:
            return
        self.time += dt
        self.cooldown = max(0.0, self.cooldown - dt)
        if self.move:
            self.target_x = self.player_x + self.move * 400 * dt
        self.player_x += max(-520 * dt, min(520 * dt, self.target_x - self.player_x))
        self.player_x = max(30, min(CANVAS[0] - 30, self.player_x))

        alive = len(self.enemies)
        speed = 52 * (1 + (self.COLUMNS * self.ROWS - alive) * 0.06)
        step = speed * dt * self.direction
        left = min(e["pos"].x for e in self.enemies)
        right = max(e["pos"].x for e in self.enemies) + self.ENEMY[0]
        if (right + step > CANVAS[0] - 10 and self.direction > 0) or (left + step < 10 and self.direction < 0):
            self.direction *= -1
            for enemy in self.enemies:
                enemy["pos"].y += 16
        else:
            for enemy in self.enemies:
                enemy["pos"].x += step

        for bullet in self.bullets:
            bullet.y -= 460 * dt
        self.bullets = [b for b in self.bullets if b.y > -10]
        for bullet in list(self.bullets):
            for enemy in self.enemies:
                rect = pygame.Rect(enemy["pos"], self.ENEMY)
                if rect.collidepoint(bullet):
                    self.enemies.remove(enemy)
                    self.bullets.remove(bullet)
                    self.kills += 1
                    self.events.append("toggle")
                    break
        if not self.enemies:
            self.win()
        elif max(e["pos"].y for e in self.enemies) + self.ENEMY[1] >= self.player_y - 4:
            self.fail()
            self._reset_wave()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((8, 14, 12))
        rng = random.Random(4)
        for _ in range(40):
            surface.set_at((rng.randrange(CANVAS[0]), rng.randrange(CANVAS[1])), (90, 110, 80))
        frame = int(self.time * 2) % 2
        for enemy in self.enemies:
            rect = pygame.Rect(enemy["pos"], self.ENEMY)
            if self.images:
                image = self.images[enemy["kind"] % len(self.images)]
                surface.blit(pygame.transform.smoothscale(image, rect.size), rect)
            else:
                sprite = self.sprites[enemy["kind"]][frame]
                surface.blit(sprite, sprite.get_rect(center=rect.center))
        for bullet in self.bullets:
            pygame.draw.rect(surface, INK_BRIGHT, (bullet.x - 2, bullet.y - 8, 4, 14))
        if self.player_image is not None:
            ship = pygame.transform.smoothscale(self.player_image, (54, 54))
            surface.blit(ship, ship.get_rect(center=(self.player_x, self.player_y)))
        else:
            surface.blit(self.player_sprite, self.player_sprite.get_rect(center=(self.player_x, self.player_y)))
        pygame.draw.line(surface, BORDER_DARK, (0, self.player_y + 26), (CANVAS[0], self.player_y + 26), 2)
        draw_text(surface, f"BOTS: {len(self.enemies)}", font(16, True), INK_BRIGHT, (10, 8))
        draw_text(surface, "clique ou ESPAÇO = atirar", font(14), INK_MUTED, (CANVAS[0] - 10, 8), "topright")


# ---------------------------------------------------------------------------
# 7. Traffic light grid (classic "select all squares with..." captcha)
# ---------------------------------------------------------------------------
def _draw_traffic_light(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    cx, cy = rect.center
    body = pygame.Rect(0, 0, 34, 78)
    body.center = (cx, cy)
    pygame.draw.rect(surface, (46, 46, 52), body, border_radius=8)
    pygame.draw.rect(surface, (20, 20, 24), body, 3, border_radius=8)
    colors = ((224, 82, 67), (232, 193, 91), (101, 191, 91))
    lit = variant % 3
    for index, color in enumerate(colors):
        on = index == lit
        shade = color if on else tuple(max(0, c // 4) for c in color)
        center = (cx, body.y + 16 + index * 24)
        pygame.draw.circle(surface, shade, center, 9)
        if on:
            pygame.draw.circle(surface, color, center, 13, 2)
    pygame.draw.rect(surface, (30, 30, 34), pygame.Rect(cx - 3, body.bottom, 6, 16))
    pygame.draw.rect(surface, (30, 30, 34), pygame.Rect(cx - 16, body.bottom + 16, 32, 6))


def _draw_car(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    palette = ((210, 70, 60), (70, 120, 200), (220, 190, 70))
    body = palette[variant % len(palette)]
    cx, cy = rect.center
    pygame.draw.rect(surface, body, pygame.Rect(cx - 38, cy - 4, 76, 26), border_radius=8)
    pygame.draw.rect(surface, body, pygame.Rect(cx - 22, cy - 22, 44, 22), border_top_left_radius=10, border_top_right_radius=10)
    pygame.draw.rect(surface, (200, 226, 232), pygame.Rect(cx - 16, cy - 18, 32, 14))
    for side in (-1, 1):
        pygame.draw.circle(surface, (24, 24, 24), (cx + side * 24, cy + 24), 10)
        pygame.draw.circle(surface, (140, 144, 150), (cx + side * 24, cy + 24), 4)


def _draw_bike(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    cx, cy = rect.center
    for side in (-1, 1):
        pygame.draw.circle(surface, (30, 30, 34), (cx + side * 22, cy + 18), 18, 3)
    pygame.draw.line(surface, (200, 80, 60), (cx - 22, cy + 18), (cx, cy - 6), 4)
    pygame.draw.line(surface, (200, 80, 60), (cx, cy - 6), (cx + 22, cy + 18), 4)
    pygame.draw.line(surface, (200, 80, 60), (cx - 8, cy + 18), (cx + 22, cy + 18), 4)
    pygame.draw.line(surface, (60, 60, 66), (cx, cy - 6), (cx - 2, cy - 22), 4)


def _draw_cone(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    cx, cy = rect.center
    pygame.draw.polygon(surface, (224, 120, 40), [(cx, cy - 36), (cx - 26, cy + 30), (cx + 26, cy + 30)])
    pygame.draw.rect(surface, (240, 236, 226), pygame.Rect(cx - 20, cy + 6, 40, 8))
    pygame.draw.rect(surface, (40, 40, 40), pygame.Rect(cx - 32, cy + 30, 64, 8), border_radius=3)


def _draw_hydrant(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    cx, cy = rect.center
    pygame.draw.rect(surface, (196, 50, 46), pygame.Rect(cx - 14, cy - 26, 28, 52), border_radius=10)
    pygame.draw.circle(surface, (196, 50, 46), (cx, cy - 30), 12)
    for side in (-1, 1):
        pygame.draw.circle(surface, (150, 40, 36), (cx + side * 16, cy - 4), 6)
    pygame.draw.rect(surface, (150, 40, 36), pygame.Rect(cx - 18, cy + 24, 36, 8))


def _draw_cloud(surface: pygame.Surface, rect: pygame.Rect, variant: int) -> None:
    cx, cy = rect.center
    for dx, dy, r in ((0, 0, 22), (20, 6, 16), (-20, 6, 16), (10, -10, 14), (-8, -12, 12)):
        pygame.draw.circle(surface, (232, 234, 238), (cx + dx, cy + dy), r)


NON_TRAFFIC_DRAWERS = (_draw_car, _draw_bike, _draw_cone, _draw_hydrant, _draw_cloud)


class TrafficGridCaptcha(Captcha):
    kind = "traffic"
    instruction = "Selecione todos os quadrados que têm SEMÁFORO."
    VERIFY = pygame.Rect(440, 300, 240, 44)
    TILE = 104
    GAP = 8
    ORIGIN = (36, 10)

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.tiles: list[tuple[bool, int]] = []
        self.selected: set[int] = set()
        self._deal()

    def _deal(self) -> None:
        count = self.rng.randint(3, 5)
        tiles = [(True, self.rng.randrange(3)) for _ in range(count)]
        tiles += [(False, self.rng.randrange(len(NON_TRAFFIC_DRAWERS))) for _ in range(9 - count)]
        self.rng.shuffle(tiles)
        self.tiles = tiles
        self.selected = set()

    def tile_rect(self, index: int) -> pygame.Rect:
        row, column = divmod(index, 3)
        return pygame.Rect(
            self.ORIGIN[0] + column * (self.TILE + self.GAP),
            self.ORIGIN[1] + row * (self.TILE + self.GAP),
            self.TILE,
            self.TILE,
        )

    def target_indices(self) -> set[int]:
        return {index for index, (is_target, _) in enumerate(self.tiles) if is_target}

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        for index in range(9):
            if self.tile_rect(index).collidepoint(pos):
                self.selected.symmetric_difference_update({index})
                self.events.append("toggle")
                return
        if self.VERIFY.collidepoint(pos):
            if self.selected == self.target_indices():
                self.win()
            else:
                self.fail()
                self._deal()

    def render(self, surface: pygame.Surface) -> None:
        for index, (is_target, variant) in enumerate(self.tiles):
            rect = self.tile_rect(index)
            pygame.draw.rect(surface, (32, 44, 36) if (index % 2) else (38, 50, 42), rect)
            if is_target:
                _draw_traffic_light(surface, rect, variant)
            else:
                NON_TRAFFIC_DRAWERS[variant % len(NON_TRAFFIC_DRAWERS)](surface, rect, variant)
            selected = index in self.selected
            pygame.draw.rect(surface, AMBER if selected else BORDER_DARK, rect, 4 if selected else 2)
            if selected:
                pygame.draw.circle(surface, AMBER, (rect.right - 14, rect.y + 14), 11)
                pygame.draw.lines(surface, SCREEN_BLACK, False, [(rect.right - 20, rect.y + 14), (rect.right - 15, rect.y + 19), (rect.right - 8, rect.y + 9)], 3)
        draw_wrapped(surface, "Clique em cada quadrado com semáforo. Depois verifique.", font(19), INK, pygame.Rect(440, 40, 240, 120), 26)
        draw_wrapped(surface, "Atenção: cone e hidrante não contam.", font(15), INK_MUTED, pygame.Rect(440, 180, 240, 40), 20)
        draw_button(surface, self.VERIFY, "VERIFICAR", self.hovering(self.VERIFY))


# ---------------------------------------------------------------------------
# 8. Simon-style beep sequence ("audio" captcha, played back as coloured flashes)
# ---------------------------------------------------------------------------
PAD_COLORS = ((224, 82, 67), (232, 193, 91), (101, 191, 91), (93, 159, 220))
PAD_NAMES = ("vermelho", "amarelo", "verde", "azul")


class SimonBeepCaptcha(Captcha):
    kind = "simon"
    instruction = "Memorize a sequência de cores que pisca e repita clicando na mesma ordem."
    PAD_SIZE = 140
    GAP = 18
    ORIGIN = (200, 30)
    ROUNDS_TO_WIN = 3
    START_LENGTH = 3
    STEP_SECONDS = 0.62
    FLASH_SECONDS = 0.5
    WRONG_PAUSE_SECONDS = 1.1

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.pads = tuple(self._pad_rect(index) for index in range(4))
        self.round = 0
        self.sequence: list[int] = []
        self.input_index = 0
        self.phase = "showing"
        self.show_index = 0
        self.show_timer = 0.0
        self.time = 0.0
        self.flash: dict[int, float] = {}
        self.wrong_pad: int | None = None
        self.correct_pad: int | None = None
        self._new_sequence()

    def _pad_rect(self, index: int) -> pygame.Rect:
        row, column = divmod(index, 2)
        return pygame.Rect(
            self.ORIGIN[0] + column * (self.PAD_SIZE + self.GAP),
            self.ORIGIN[1] + row * (self.PAD_SIZE + self.GAP),
            self.PAD_SIZE,
            self.PAD_SIZE,
        )

    def _new_sequence(self) -> None:
        self.round = 0
        self.sequence = [self.rng.randrange(4) for _ in range(self.START_LENGTH)]
        self._start_showing()

    def _start_showing(self) -> None:
        self.phase = "showing"
        self.show_index = 0
        self.show_timer = 0.7
        self.input_index = 0
        self.wrong_pad = None
        self.correct_pad = None
        self.flash = {}

    def update(self, dt: float) -> None:
        self.time += dt
        if self.phase == "wrong":
            self.show_timer -= dt
            if self.show_timer <= 0:
                self._new_sequence()
            return
        if self.phase == "showing":
            self.show_timer -= dt
            if self.show_timer <= 0:
                if self.show_index < len(self.sequence):
                    pad = self.sequence[self.show_index]
                    self.flash[pad] = self.FLASH_SECONDS
                    self.events.append("click")
                    self.show_index += 1
                    self.show_timer = self.STEP_SECONDS
                else:
                    self.phase = "waiting"
        for pad in list(self.flash):
            self.flash[pad] -= dt
            if self.flash[pad] <= 0:
                del self.flash[pad]

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.phase != "waiting":
            return
        for index, rect in enumerate(self.pads):
            if not rect.collidepoint(pos):
                continue
            expected = self.sequence[self.input_index]
            if index != expected:
                self.wrong_pad = index
                self.correct_pad = expected
                self.phase = "wrong"
                self.show_timer = self.WRONG_PAUSE_SECONDS
                self.fail()
                return
            self.flash[index] = self.FLASH_SECONDS
            self.events.append("toggle")
            self.input_index += 1
            if self.input_index == len(self.sequence):
                self.round += 1
                if self.round >= self.ROUNDS_TO_WIN:
                    self.win()
                else:
                    self.sequence.append(self.rng.randrange(4))
                    self._start_showing()
            return

    def render(self, surface: pygame.Surface) -> None:
        pulse = 0.5 + 0.5 * math.sin(self.time * 5.0)
        for index, rect in enumerate(self.pads):
            base = PAD_COLORS[index]
            lit = index in self.flash
            if self.phase == "wrong" and index == self.wrong_pad:
                color = RED
            elif self.phase == "wrong" and index == self.correct_pad:
                color = GREEN
            elif lit:
                color = (245, 245, 250)
            else:
                color = base
            pygame.draw.rect(surface, color, rect, border_radius=16)
            if self.phase == "wrong" and index in (self.wrong_pad, self.correct_pad):
                glow = rect.inflate(14, 14)
                pygame.draw.rect(surface, color, glow, 6, border_radius=20)
                pygame.draw.rect(surface, SCREEN_BLACK, rect, 10, border_radius=16)
            elif lit:
                glow = rect.inflate(14, 14)
                pygame.draw.rect(surface, INK_BRIGHT, glow, 6, border_radius=20)
                pygame.draw.rect(surface, SCREEN_BLACK, rect, 10, border_radius=16)
            elif self.phase == "waiting":
                ready = round(160 + 70 * pulse)
                pygame.draw.rect(surface, (ready, ready, ready), rect, 4, border_radius=16)
            else:
                pygame.draw.rect(surface, BORDER_DARK, rect, 4, border_radius=16)
        if self.phase == "wrong":
            status, status_color = f"ERRADO! Era o {PAD_NAMES[self.correct_pad]}.", RED
        elif self.phase == "showing":
            status, status_color = "MEMORIZE A SEQUÊNCIA...", AMBER
        else:
            status, status_color = "SUA VEZ: CLIQUE NA MESMA ORDEM", GREEN
        chip = pygame.Rect(30, 26, 470, 40)
        pygame.draw.rect(surface, SCREEN_BLACK, chip, border_radius=8)
        pygame.draw.rect(surface, status_color, chip, 2, border_radius=8)
        draw_text(surface, status, font(19, True), status_color, chip.center, "center")
        draw_text(surface, f"Rodada {min(self.round + 1, self.ROUNDS_TO_WIN)} de {self.ROUNDS_TO_WIN}", font(16), INK_MUTED, (40, 80))
        draw_text(surface, f"Sequência: {len(self.sequence)} passos", font(14), INK_MUTED, (40, 104))
        draw_wrapped(surface, "Um robô decoraria isso fácil. Você consegue?", font(14), INK_MUTED, pygame.Rect(40, 300, 150, 50), 18)


# ---------------------------------------------------------------------------
# 9. Chimp test: memorize the numbered tiles, then click them back in order
# ---------------------------------------------------------------------------
class ChimpSequenceCaptcha(Captcha):
    kind = "chimp"
    instruction = "Memorize onde cada número está. Quando sumirem, clique na ordem de 1 até o último."
    COLUMNS = 4
    ROWS = 3
    CELL = 110
    ORIGIN = (40, 10)
    ROUNDS_TO_WIN = 4
    START_COUNT = 3
    REVEAL_SECONDS = 1.7
    WRONG_PAUSE_SECONDS = 1.2

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.slots = tuple(self._slot_rect(index) for index in range(self.COLUMNS * self.ROWS))
        self.round = 0
        self.count = self.START_COUNT
        self.positions: list[int] = []
        self.phase = "showing"
        self.timer = 0.0
        self.next_expected = 0
        self.correct_slots: set[int] = set()
        self.wrong_slot: int | None = None
        self._deal()

    def _slot_rect(self, index: int) -> pygame.Rect:
        row, column = divmod(index, self.COLUMNS)
        return pygame.Rect(
            self.ORIGIN[0] + column * self.CELL,
            self.ORIGIN[1] + row * self.CELL,
            self.CELL - 14,
            self.CELL - 14,
        )

    def _deal(self) -> None:
        self.positions = self.rng.sample(range(len(self.slots)), min(self.count, len(self.slots)))
        self.phase = "showing"
        self.timer = self.REVEAL_SECONDS
        self.next_expected = 0
        self.correct_slots = set()
        self.wrong_slot = None

    def update(self, dt: float) -> None:
        if self.phase in ("showing", "wrong"):
            self.timer -= dt
            if self.timer <= 0:
                if self.phase == "showing":
                    self.phase = "waiting"
                else:
                    self.count = self.START_COUNT
                    self.round = 0
                    self._deal()

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.phase != "waiting":
            return
        for index, rect in enumerate(self.slots):
            if not rect.collidepoint(pos):
                continue
            expected_slot = self.positions[self.next_expected]
            if index != expected_slot:
                self.wrong_slot = index
                self.phase = "wrong"
                self.timer = self.WRONG_PAUSE_SECONDS
                self.fail()
                return
            self.correct_slots.add(index)
            self.events.append("toggle")
            self.next_expected += 1
            if self.next_expected >= len(self.positions):
                self.round += 1
                if self.round >= self.ROUNDS_TO_WIN:
                    self.win()
                else:
                    self.count += 1
                    self._deal()
            return

    def render(self, surface: pygame.Surface) -> None:
        reveal_all = self.phase in ("showing", "wrong")
        for index, rect in enumerate(self.slots):
            in_play = index in self.positions
            if self.phase == "wrong" and index == self.wrong_slot:
                pygame.draw.rect(surface, RED, rect, border_radius=10)
                glow = rect.inflate(10, 10)
                pygame.draw.rect(surface, RED, glow, 4, border_radius=14)
            elif index in self.correct_slots:
                pygame.draw.rect(surface, GREEN, rect, border_radius=10)
            elif reveal_all and in_play:
                pygame.draw.rect(surface, AMBER, rect, border_radius=10)
            else:
                pygame.draw.rect(surface, PANEL_MID, rect, border_radius=10)
            pygame.draw.rect(surface, BORDER_DARK, rect, 2, border_radius=10)
            if (reveal_all and in_play) or index in self.correct_slots:
                number = self.positions.index(index) + 1
                draw_text(surface, str(number), font(26, True), SCREEN_BLACK, rect.center, "center")

        if self.phase == "wrong":
            status, status_color = "ERRADO! Veja a ordem certa e tente de novo.", RED
        elif self.phase == "showing":
            status, status_color = "MEMORIZE AS POSIÇÕES...", AMBER
        else:
            status, status_color = f"CLIQUE NA ORDEM  ·  PRÓXIMO: {self.next_expected + 1}", GREEN
        chip = pygame.Rect(500, 16, 210, 60)
        pygame.draw.rect(surface, SCREEN_BLACK, chip, border_radius=8)
        pygame.draw.rect(surface, status_color, chip, 2, border_radius=8)
        draw_wrapped(surface, status, font(15, True), status_color, chip.inflate(-16, -12), 18, center=True)
        draw_text(surface, f"Rodada {min(self.round + 1, self.ROUNDS_TO_WIN)} de {self.ROUNDS_TO_WIN}", font(15), INK_MUTED, (500, 84))
        draw_text(surface, f"{self.count} números nesta rodada", font(14), INK_MUTED, (500, 106))
        draw_wrapped(surface, "O nome é sério: chimpanzés treinados vencem humanos nesse teste.", font(13), INK_MUTED, pygame.Rect(500, 260, 210, 90), 17)


# ---------------------------------------------------------------------------
# 10. Whack-a-bot: reflex game, only click the robots
# ---------------------------------------------------------------------------
def _draw_human_icon(surface: pygame.Surface, rect: pygame.Rect) -> None:
    cx, cy = rect.center
    pygame.draw.ellipse(surface, (196, 92, 70), pygame.Rect(cx - 30, cy + 6, 60, 46))
    pygame.draw.circle(surface, (230, 196, 160), (cx, cy - 16), 24)
    pygame.draw.arc(surface, (60, 40, 30), pygame.Rect(cx - 24, cy - 40, 48, 36), math.pi * 0.05, math.pi * 0.95, 10)
    for side in (-1, 1):
        pygame.draw.circle(surface, (20, 20, 20), (cx + side * 8, cy - 18), 3)
    pygame.draw.arc(surface, (140, 70, 50), pygame.Rect(cx - 10, cy - 8, 20, 12), math.pi, math.tau, 2)


class WhackABotCaptcha(Captcha):
    kind = "whackabot"
    instruction = "Clique só nos ROBÔS assim que aparecerem. Um humano custa 2 acertos."
    TARGET_HITS = 10
    COLUMNS = 3
    ROWS = 3
    CELL = 112
    ORIGIN = (50, 10)

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.hits = 0
        self.spawn_timer = 0.0
        self.active: dict[int, dict] = {}
        self.slots = tuple(self._slot_rect(index) for index in range(self.COLUMNS * self.ROWS))
        self.difficulty = 0.0
        self._schedule_next()

    def _slot_rect(self, index: int) -> pygame.Rect:
        row, column = divmod(index, self.COLUMNS)
        return pygame.Rect(
            self.ORIGIN[0] + column * self.CELL,
            self.ORIGIN[1] + row * self.CELL,
            self.CELL - 14,
            self.CELL - 14,
        )

    def _schedule_next(self) -> None:
        self.spawn_timer = max(0.28, 0.62 - self.difficulty * 0.015)

    def update(self, dt: float) -> None:
        self.difficulty += dt
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            free = [index for index in range(len(self.slots)) if index not in self.active]
            if free:
                slot = self.rng.choice(free)
                is_robot = self.rng.random() < 0.62
                self.active[slot] = {
                    "kind": "robot" if is_robot else "human",
                    "life": self.rng.uniform(0.85, 1.25),
                    "grow": 0.0,
                }
            self._schedule_next()
        for slot in list(self.active):
            entry = self.active[slot]
            entry["grow"] = min(1.0, entry["grow"] + dt * 6)
            entry["life"] -= dt
            if entry["life"] <= 0:
                del self.active[slot]

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        for slot, entry in list(self.active.items()):
            if not self.slots[slot].collidepoint(pos):
                continue
            if entry["kind"] == "robot":
                self.hits += 1
                self.events.append("toggle")
                del self.active[slot]
                if self.hits >= self.TARGET_HITS:
                    self.win()
            else:
                self.hits = max(0, self.hits - 2)
                self.fail()
                del self.active[slot]
            return

    def render(self, surface: pygame.Surface) -> None:
        for rect in self.slots:
            pygame.draw.rect(surface, PANEL_MID, rect, border_radius=10)
            pygame.draw.rect(surface, BORDER_DARK, rect, 2, border_radius=10)
        for slot, entry in self.active.items():
            shrink = round(30 * (1 - entry["grow"]))
            rect = self.slots[slot].inflate(-shrink, -shrink)
            if entry["kind"] == "robot":
                _draw_robot(surface, rect, 0)
            else:
                _draw_human_icon(surface, rect)
        draw_text(surface, f"ROBÔS: {self.hits}/{self.TARGET_HITS}", font(20, True), INK_BRIGHT, (520, 20))
        draw_wrapped(surface, "Clique nos robôs assim que surgirem. Cuidado: acertar um humano tira 2 pontos.", font(15), INK_MUTED, pygame.Rect(520, 60, 190, 160), 20)


# ---------------------------------------------------------------------------
TIERS = {
    "easy": ("wobbly", "cats", "rotate"),
    "medium": ("puzzle", "memory"),
    "hard": ("invaders", "memory6", "puzzle9"),
}


def create_captcha(kind: str, rng: random.Random, assets_root: Path) -> Captcha:
    if kind == "wobbly":
        return WobblyTextCaptcha(rng, assets_root)
    if kind == "cats":
        return CatGridCaptcha(rng, assets_root)
    if kind == "rotate":
        return RotateCaptcha(rng, assets_root)
    if kind == "puzzle":
        return SwapPuzzleCaptcha(rng, assets_root, 3, 2)
    if kind == "puzzle9":
        return SwapPuzzleCaptcha(rng, assets_root, 3, 3)
    if kind == "memory":
        return MemoryCaptcha(rng, assets_root, 4)
    if kind == "memory6":
        return MemoryCaptcha(rng, assets_root, 6)
    if kind == "invaders":
        return InvadersCaptcha(rng, assets_root)
    if kind == "traffic":
        return TrafficGridCaptcha(rng, assets_root)
    if kind == "simon":
        return SimonBeepCaptcha(rng, assets_root)
    if kind == "whackabot":
        return WhackABotCaptcha(rng, assets_root)
    if kind == "chimp":
        return ChimpSequenceCaptcha(rng, assets_root)
    raise ValueError(f"Unknown captcha: {kind}")
