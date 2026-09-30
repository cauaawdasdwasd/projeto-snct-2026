"""The 'prove you are human' mini-games. Each one lives on a 720x360 canvas.

Coordinates given to the event handlers are already local to that canvas.
Every game works without extra art (drawings are made in code) and picks up the
optional images from assets/captcha/ when they exist.
"""

from __future__ import annotations

import math
import random
from collections import deque
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
# 3. Rotate the portrait upright (real photos only, see assets/captcha/rotate/)
# ---------------------------------------------------------------------------
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
        photos = load_rotate_photos(assets_root)
        name, photo = rng.choice(list(photos.items()))
        self.instruction = ROTATE_PHOTO_INSTRUCTIONS.get(name, "Gire a imagem até ficar em pé.")
        self.image = fit_square(photo, self.SIZE)
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
        self.kind = "puzzle9" if columns == 3 and rows == 3 else "puzzle"
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
        self.kind = "memory6" if pairs == 6 else "memory"
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
    ORIGIN = (260, 26)
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
                    self.events.append(f"pad_{pad}")
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
            self.events.append(f"pad_{index}")
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
            if lit or (self.phase == "wrong" and index in (self.wrong_pad, self.correct_pad)):
                pygame.draw.rect(surface, SCREEN_BLACK, rect, 5, border_radius=16)
            elif self.phase == "waiting":
                ready = round(160 + 70 * pulse)
                pygame.draw.rect(surface, (ready, ready, ready), rect, 4, border_radius=16)
            else:
                pygame.draw.rect(surface, BORDER_DARK, rect, 4, border_radius=16)

        if self.phase == "wrong":
            status, status_color = f"ERRADO! Era o {PAD_NAMES[self.correct_pad]}.", RED
        elif self.phase == "showing":
            status, status_color = "MEMORIZE...", AMBER
        else:
            status, status_color = "SUA VEZ: CLIQUE NA ORDEM", GREEN
        chip = pygame.Rect(20, 20, 220, 40)
        pygame.draw.rect(surface, SCREEN_BLACK, chip, border_radius=8)
        pygame.draw.rect(surface, status_color, chip, 2, border_radius=8)
        draw_wrapped(surface, status, font(15, True), status_color, chip.inflate(-16, -8), 18, center=True)
        draw_text(surface, f"Rodada {min(self.round + 1, self.ROUNDS_TO_WIN)} de {self.ROUNDS_TO_WIN}", font(16), INK_MUTED, (20, 76))
        draw_text(surface, f"Sequência: {len(self.sequence)} passos", font(14), INK_MUTED, (20, 100))
        draw_wrapped(surface, "Um robô decoraria isso fácil. Você consegue?", font(14), INK_MUTED, pygame.Rect(20, 300, 220, 50), 18)


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
# 10. Wire cut: read the manual, cut the one wire it points to (Keep Talking-style)
# ---------------------------------------------------------------------------
WIRE_PALETTE = (
    ("VERMELHO", (214, 70, 60)),
    ("AZUL", (70, 130, 200)),
    ("AMARELO", (224, 190, 70)),
    ("BRANCO", (230, 230, 226)),
    ("PRETO", (60, 60, 66)),
)
WIRE_CODE_LETTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ"
WIRE_CODE_DIGITS = "0123456789"


def _wire_generate_code(rng: random.Random) -> str:
    """A little serial number, like the one on a Keep Talking bomb: 6 letters/digits,
    mixed independently so the letter/digit split varies run to run (never a fixed tie
    that would make the 'more letters than digits' rule always resolve the same way).
    At least one digit is guaranteed so the digit-based rules always have something
    to evaluate."""
    chars = [rng.choice(WIRE_CODE_LETTERS) if rng.random() < 0.5 else rng.choice(WIRE_CODE_DIGITS) for _ in range(6)]
    if not any(c in WIRE_CODE_DIGITS for c in chars):
        chars[rng.randrange(len(chars))] = rng.choice(WIRE_CODE_DIGITS)
    return "".join(chars)


def _wire_last_digit_odd(code: str) -> bool:
    digits = [c for c in code if c.isdigit()]
    return bool(digits) and int(digits[-1]) % 2 == 1


def _wire_digit_sum_even(code: str) -> bool:
    digits = [int(c) for c in code if c.isdigit()]
    return sum(digits) % 2 == 0


def _wire_has_vowel(code: str) -> bool:
    return any(c in "AEIOU" for c in code)


def _wire_more_letters_than_digits(code: str) -> bool:
    letters = sum(1 for c in code if c.isalpha())
    digits = sum(1 for c in code if c.isdigit())
    return letters > digits


# Each rule reads the serial code and picks between two colors that are guaranteed to
# be the *only* wire of their color on the board, so the answer is never ambiguous -
# the same design trick real bomb-defusal manuals use (a clear decision, not a puzzle
# with two right answers).
WIRE_CONDITIONS = (
    (_wire_last_digit_odd, "CÓDIGO {code} — último dígito ÍMPAR: corte {color_true}. PAR: corte {color_false}."),
    (_wire_digit_sum_even, "CÓDIGO {code} — soma dos dígitos PAR: corte {color_true}. ÍMPAR: corte {color_false}."),
    (_wire_has_vowel, "CÓDIGO {code} — tem VOGAL: corte {color_true}. Sem vogal: corte {color_false}."),
    (_wire_more_letters_than_digits, "CÓDIGO {code} — mais LETRAS que números: corte {color_true}. Senão: corte {color_false}."),
)


class WireCutCaptcha(Captcha):
    kind = "wires"
    instruction = "Leia o código e a regra com atenção, depois corte o fio certo. Errar reinicia tudo."
    WIRE_COUNT = 5
    ROUNDS_TO_WIN = 3
    WIRE_HEIGHT = 30
    GAP = 12
    ORIGIN_Y = 90
    LEFT_X = 96
    WIRE_LENGTH = 528
    TERMINAL_WIDTH = 26
    WRONG_PAUSE_SECONDS = 1.3
    RIGHT_PAUSE_SECONDS = 0.6

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.round = 0
        self.wires: list[tuple[str, tuple[int, int, int]]] = []
        self.code = ""
        self.rule_text = ""
        self.correct_index = 0
        self.cut_index: int | None = None
        self.phase = "active"  # active | wrong | right
        self.timer = 0.0
        self._deal()

    def _deal(self) -> None:
        while True:
            self.wires = [self.rng.choice(WIRE_PALETTE) for _ in range(self.WIRE_COUNT)]
            counts: dict[str, int] = {}
            for name, _ in self.wires:
                counts[name] = counts.get(name, 0) + 1
            unique_colors = [name for name, count in counts.items() if count == 1]
            if len(unique_colors) >= 2:
                break
        self.code = _wire_generate_code(self.rng)
        color_true, color_false = self.rng.sample(unique_colors, 2)
        condition, template = self.rng.choice(WIRE_CONDITIONS)
        target_color = color_true if condition(self.code) else color_false
        self.correct_index = next(index for index, (name, _) in enumerate(self.wires) if name == target_color)
        self.rule_text = template.format(code=self.code, color_true=color_true, color_false=color_false)
        self.cut_index = None
        self.phase = "active"

    def wire_rect(self, index: int) -> pygame.Rect:
        y = self.ORIGIN_Y + index * (self.WIRE_HEIGHT + self.GAP)
        return pygame.Rect(self.LEFT_X, y, self.WIRE_LENGTH, self.WIRE_HEIGHT)

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.phase != "active":
            return
        for index in range(self.WIRE_COUNT):
            if not self.wire_rect(index).collidepoint(pos):
                continue
            self.cut_index = index
            if index == self.correct_index:
                self.events.append("toggle")
                self.round += 1
                self.phase = "right"
                self.timer = self.RIGHT_PAUSE_SECONDS
            else:
                self.phase = "wrong"
                self.timer = self.WRONG_PAUSE_SECONDS
                self.fail()
            return

    def update(self, dt: float) -> None:
        if self.phase in ("wrong", "right"):
            self.timer -= dt
            if self.timer <= 0:
                if self.phase == "right" and self.round >= self.ROUNDS_TO_WIN:
                    self.win()
                    return
                if self.phase == "wrong":
                    self.round = 0
                self._deal()

    def render(self, surface: pygame.Surface) -> None:
        panel_color = RED if self.phase == "wrong" else (GREEN if self.phase == "right" else AMBER)
        panel = pygame.Rect(20, 8, 680, 74)
        pygame.draw.rect(surface, SCREEN_BLACK, panel, border_radius=8)
        pygame.draw.rect(surface, panel_color, panel, 2, border_radius=8)
        draw_wrapped(surface, self.rule_text, font(16, True), panel_color, pygame.Rect(panel.x + 14, panel.y + 8, panel.width - 28, panel.height - 16), 20, center=True)

        for index, (_, rgb) in enumerate(self.wires):
            rect = self.wire_rect(index)
            is_cut = index == self.cut_index

            backplate = pygame.Rect(
                rect.x - self.TERMINAL_WIDTH - 6, rect.y - 6,
                rect.width + 2 * self.TERMINAL_WIDTH + 12, self.WIRE_HEIGHT + 12,
            )
            pygame.draw.rect(surface, (24, 28, 26), backplate, border_radius=6)
            for term_x in (rect.x - self.TERMINAL_WIDTH, rect.right):
                terminal = pygame.Rect(term_x, rect.y - 3, self.TERMINAL_WIDTH, self.WIRE_HEIGHT + 6)
                pygame.draw.rect(surface, (98, 102, 110), terminal, border_radius=4)
                pygame.draw.rect(surface, (44, 46, 52), terminal, 2, border_radius=4)
                pygame.draw.circle(surface, (36, 38, 44), terminal.center, 4)

            body = rgb if not is_cut else tuple(max(0, c // 3) for c in rgb)
            radius = self.WIRE_HEIGHT // 2
            if not is_cut:
                pygame.draw.rect(surface, (8, 10, 9), rect.move(0, 3), border_radius=radius)
                pygame.draw.rect(surface, body, rect, border_radius=radius)
                highlight = tuple(min(255, c + 55) for c in body)
                pygame.draw.rect(surface, highlight, pygame.Rect(rect.x + 8, rect.y + 4, rect.width - 16, 5), border_radius=3)
                shade = tuple(max(0, c - 45) for c in body)
                pygame.draw.rect(surface, shade, pygame.Rect(rect.x + 8, rect.bottom - 8, rect.width - 16, 4), border_radius=2)
            else:
                stub_width = rect.width // 2 - 16
                left_stub = pygame.Rect(rect.x, rect.y, stub_width, self.WIRE_HEIGHT)
                right_stub = pygame.Rect(rect.right - stub_width, rect.y, stub_width, self.WIRE_HEIGHT)
                for stub in (left_stub, right_stub):
                    pygame.draw.rect(surface, body, stub, border_radius=radius)
                spark = GREEN if index == self.correct_index else RED
                cx, cy = rect.centerx, rect.centery
                for dx, dy in ((-18, -12), (-18, 12), (18, -12), (18, 12)):
                    pygame.draw.line(surface, spark, (cx + dx, cy + dy), (cx + dx // 4, cy), 3)
                pygame.draw.circle(surface, spark, (cx, cy), 4)

        status_y = self.ORIGIN_Y + self.WIRE_COUNT * (self.WIRE_HEIGHT + self.GAP)
        draw_text(surface, f"Rodada {min(self.round + 1, self.ROUNDS_TO_WIN)} de {self.ROUNDS_TO_WIN}", font(15), INK_MUTED, (40, status_y))
        if self.phase == "wrong":
            draw_text(surface, "FIO ERRADO! Nova instrução chegando...", font(18, True), RED, (360, status_y + 26), "center")
        elif self.phase == "right" and self.round < self.ROUNDS_TO_WIN:
            draw_text(surface, "Fio certo. Próxima instrução...", font(18, True), GREEN, (360, status_y + 26), "center")


# ---------------------------------------------------------------------------
# 11. Termo: a Wordle-style guesser, word bank tuned to the game's own themes
# ---------------------------------------------------------------------------
TERMO_WORDS = (
    "DADOS", "ROBOS", "ATOMO", "TESTE", "FALHA", "CHAVE", "SENHA", "VETOR",
    "PROVA", "FONTE", "TELAS", "REDES", "CIFRA", "VIRUS", "PIXEL", "ERROS",
    "LOGIN", "FORTE", "CACHE", "BOLHA", "PODER", "PAPEL", "FICHA", "CASOS",
    "TURNO", "ALVOS", "PASSO", "TECLA", "MODEM", "BUSCA", "MEDIA", "CURVA",
    "PLACA", "DISCO", "ETICA", "JUSTA", "REGRA", "NORMA", "FORCA", "GENES",
    "FOTON", "LASER", "RAIOS", "ONDAS", "CAMPO", "MASSA", "FORMA", "RUIDO",
    "SINAL", "LIVRO", "MUNDO", "VERDE", "CERTO",
)
TERMO_ALPHABET = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def _score_sequence(guess: str, target: str) -> list[str]:
    """Classic Wordle scoring, generalized to any equal-length sequence of characters:
    exact position first, then leftover items - shared by the letter Termo and the
    numeric vault so both show the same per-slot correct/present/absent feedback."""
    result = ["absent"] * len(guess)
    remaining = list(target)
    for index, item in enumerate(guess):
        if item == target[index]:
            result[index] = "correct"
            remaining[index] = None
    for index, item in enumerate(guess):
        if result[index] == "correct":
            continue
        if item in remaining:
            result[index] = "present"
            remaining[remaining.index(item)] = None
    return result


def _score_termo_guess(guess: str, target: str) -> list[str]:
    return _score_sequence(guess, target)


class TermoCaptcha(Captcha):
    kind = "termo"
    instruction = "Adivinhe a palavra de 5 letras. Verde: posição certa. Amarelo: letra certa, lugar errado."
    WORD_LENGTH = 5
    MAX_GUESSES = 6
    TILE = 52
    GAP = 8
    ORIGIN = (40, 16)
    RIGHT_PAUSE_SECONDS = 0.8
    WRONG_PAUSE_SECONDS = 1.6
    INVALID_WORD_SECONDS = 0.8

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.target = ""
        self.guesses: list[str] = []
        self.results: list[list[str]] = []
        self.current_letters: list[str] = [""] * self.WORD_LENGTH
        self.cursor = 0
        self.phase = "active"  # active | wrong | right
        self.timer = 0.0
        self.invalid_timer = 0.0
        self._deal()

    def _deal(self) -> None:
        self.target = self.rng.choice(TERMO_WORDS)
        self.guesses = []
        self.results = []
        self.current_letters = [""] * self.WORD_LENGTH
        self.cursor = 0
        self.phase = "active"
        self.invalid_timer = 0.0

    def _tile_rect(self, row: int, column: int) -> pygame.Rect:
        x = self.ORIGIN[0] + column * (self.TILE + self.GAP)
        y = self.ORIGIN[1] + row * (self.TILE + self.GAP)
        return pygame.Rect(x, y, self.TILE, self.TILE)

    def on_key(self, event: pygame.event.Event) -> None:
        if self.phase != "active" or event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_LEFT:
            self.cursor = max(0, self.cursor - 1)
        elif event.key == pygame.K_RIGHT:
            self.cursor = min(self.WORD_LENGTH - 1, self.cursor + 1)
        elif event.key == pygame.K_BACKSPACE:
            if self.current_letters[self.cursor]:
                self.current_letters[self.cursor] = ""
            elif self.cursor > 0:
                self.cursor -= 1
                self.current_letters[self.cursor] = ""
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._submit()
        else:
            typed = getattr(event, "unicode", "").upper()
            if typed and typed in TERMO_ALPHABET:
                self.current_letters[self.cursor] = typed
                self.events.append("click")
                if self.cursor < self.WORD_LENGTH - 1:
                    self.cursor += 1

    def _submit(self) -> None:
        if "" in self.current_letters:
            return
        guess = "".join(self.current_letters)
        if guess not in TERMO_WORDS:
            # Not a real word from the bank: rejected for free, same as real Wordle -
            # it doesn't consume one of the limited guesses or cost any time.
            self.invalid_timer = self.INVALID_WORD_SECONDS
            self.events.append("click")
            return
        self.guesses.append(guess)
        self.results.append(_score_termo_guess(guess, self.target))
        self.current_letters = [""] * self.WORD_LENGTH
        self.cursor = 0
        if guess == self.target:
            self.phase = "right"
            self.timer = self.RIGHT_PAUSE_SECONDS
        elif len(self.guesses) >= self.MAX_GUESSES:
            self.phase = "wrong"
            self.timer = self.WRONG_PAUSE_SECONDS
            self.fail()
        else:
            self.events.append("toggle")

    def update(self, dt: float) -> None:
        if self.invalid_timer > 0:
            self.invalid_timer = max(0.0, self.invalid_timer - dt)
        if self.phase in ("wrong", "right"):
            self.timer -= dt
            if self.timer <= 0:
                if self.phase == "right":
                    self.win()
                    return
                self._deal()

    def render(self, surface: pygame.Surface) -> None:
        state_colors = {"correct": GREEN, "present": AMBER, "absent": PANEL_MID}
        for row in range(self.MAX_GUESSES):
            for column in range(self.WORD_LENGTH):
                rect = self._tile_rect(row, column)
                letter = ""
                text_color = INK_BRIGHT
                if row < len(self.guesses):
                    letter = self.guesses[row][column]
                    state = self.results[row][column]
                    pygame.draw.rect(surface, state_colors[state], rect, border_radius=6)
                    text_color = SCREEN_BLACK if state != "absent" else INK_MUTED
                elif row == len(self.guesses):
                    is_cursor = column == self.cursor
                    pygame.draw.rect(surface, PANEL, rect, border_radius=6)
                    pygame.draw.rect(surface, AMBER if is_cursor else INK_BRIGHT, rect, 3 if is_cursor else 2, border_radius=6)
                    letter = self.current_letters[column]
                else:
                    pygame.draw.rect(surface, (22, 30, 26), rect, border_radius=6)
                    pygame.draw.rect(surface, BORDER_DARK, rect, 2, border_radius=6)
                if letter:
                    draw_text(surface, letter, font(26, True), text_color, rect.center, "center")

        panel_x = 400
        draw_text(surface, "TERMO", font(22, True), GREEN, (panel_x, 18))
        draw_text(surface, f"TENTATIVA {min(len(self.guesses) + 1, self.MAX_GUESSES)}/{self.MAX_GUESSES}", font(14), INK_MUTED, (panel_x, 50))
        draw_wrapped(surface, "Digite, use ←/→ para corrigir uma letra e aperte Enter.", font(13), INK_MUTED, pygame.Rect(panel_x, 72, 300, 40), 17)
        legend_y = 122
        for label, color in (
            ("posição certa", GREEN),
            ("letra certa, lugar errado", AMBER),
            ("não está na palavra", BORDER_DARK),
        ):
            pygame.draw.rect(surface, color, pygame.Rect(panel_x, legend_y, 16, 16), border_radius=3)
            draw_wrapped(surface, label, font(13), INK_MUTED, pygame.Rect(panel_x + 24, legend_y - 2, 290, 40), 16)
            legend_y += 30
        if self.invalid_timer > 0:
            draw_text(surface, "NÃO É UMA PALAVRA VÁLIDA", font(15, True), RED, (panel_x, 244))
        elif self.phase == "wrong":
            draw_text(surface, f"A PALAVRA ERA: {self.target}", font(17, True), RED, (panel_x, 244))
        elif self.phase == "right":
            draw_text(surface, "ACERTOU!", font(19, True), GREEN, (panel_x, 244))


# ---------------------------------------------------------------------------
# 12. Vault: crack a 4-digit code Mastermind-style (like the gun-safe keypad in
#     Lockdown Protocol) - each guess reveals how many digits are exactly right and
#     how many are the right digit in the wrong spot.
# ---------------------------------------------------------------------------
VAULT_NUMPAD = (
    ("1", "2", "3"),
    ("4", "5", "6"),
    ("7", "8", "9"),
    ("C", "0", "OK"),
)


def _score_vault_guess(guess: str, code: str) -> list[str]:
    return _score_sequence(guess, code)


class VaultCaptcha(Captcha):
    kind = "cofre"
    instruction = "Descubra a senha de 4 dígitos. Verde: posição certa. Amarelo: dígito certo, lugar errado."
    CODE_LENGTH = 4
    MAX_ATTEMPTS = 9
    TILE = 30
    TILE_GAP = 6
    HISTORY_ORIGIN = (20, 14)
    LEGEND_X = 190
    DIGIT_BOX = (55, 62)
    DIGIT_ORIGIN = (430, 16)
    DIGIT_GAP = 8
    NUMPAD_BUTTON = (60, 48)
    NUMPAD_ORIGIN = (430, 96)
    NUMPAD_GAP = 8
    RIGHT_PAUSE_SECONDS = 0.9
    WRONG_PAUSE_SECONDS = 1.8

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.code = ""
        self.guesses: list[str] = []
        self.results: list[list[str]] = []
        self.current_digits: list[str] = []
        self.phase = "active"  # active | wrong | right
        self.timer = 0.0
        self._deal()

    def _deal(self) -> None:
        self.code = "".join(self.rng.sample("0123456789", self.CODE_LENGTH))
        self.guesses = []
        self.results = []
        self.current_digits = []
        self.phase = "active"

    def _digit_box_rect(self, index: int) -> pygame.Rect:
        x = self.DIGIT_ORIGIN[0] + index * (self.DIGIT_BOX[0] + self.DIGIT_GAP)
        return pygame.Rect(x, self.DIGIT_ORIGIN[1], *self.DIGIT_BOX)

    def _history_tile_rect(self, row: int, column: int) -> pygame.Rect:
        x = self.HISTORY_ORIGIN[0] + column * (self.TILE + self.TILE_GAP)
        y = self.HISTORY_ORIGIN[1] + row * (self.TILE + self.TILE_GAP)
        return pygame.Rect(x, y, self.TILE, self.TILE)

    def _numpad_rect(self, row: int, column: int) -> pygame.Rect:
        x = self.NUMPAD_ORIGIN[0] + column * (self.NUMPAD_BUTTON[0] + self.NUMPAD_GAP)
        y = self.NUMPAD_ORIGIN[1] + row * (self.NUMPAD_BUTTON[1] + self.NUMPAD_GAP)
        return pygame.Rect(x, y, *self.NUMPAD_BUTTON)

    def _press(self, label: str) -> None:
        if label == "C":
            if self.current_digits:
                self.current_digits.pop()
        elif label == "OK":
            self._submit()
        elif len(self.current_digits) < self.CODE_LENGTH:
            self.current_digits.append(label)
            self.events.append("click")

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.phase != "active":
            return
        for row, labels in enumerate(VAULT_NUMPAD):
            for column, label in enumerate(labels):
                if self._numpad_rect(row, column).collidepoint(pos):
                    self._press(label)
                    return

    def on_key(self, event: pygame.event.Event) -> None:
        if self.phase != "active" or event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_BACKSPACE:
            if self.current_digits:
                self.current_digits.pop()
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._submit()
        else:
            typed = getattr(event, "unicode", "")
            if typed.isdigit() and len(self.current_digits) < self.CODE_LENGTH:
                self.current_digits.append(typed)
                self.events.append("click")

    def _submit(self) -> None:
        if len(self.current_digits) != self.CODE_LENGTH:
            return
        guess = "".join(self.current_digits)
        self.guesses.append(guess)
        self.results.append(_score_vault_guess(guess, self.code))
        self.current_digits = []
        if guess == self.code:
            self.phase = "right"
            self.timer = self.RIGHT_PAUSE_SECONDS
        elif len(self.guesses) >= self.MAX_ATTEMPTS:
            self.phase = "wrong"
            self.timer = self.WRONG_PAUSE_SECONDS
            self.fail()
        else:
            self.events.append("toggle")

    def update(self, dt: float) -> None:
        if self.phase in ("wrong", "right"):
            self.timer -= dt
            if self.timer <= 0:
                if self.phase == "right":
                    self.win()
                    return
                self._deal()

    def render(self, surface: pygame.Surface) -> None:
        state_colors = {"correct": GREEN, "present": AMBER, "absent": PANEL_MID}
        for row in range(self.MAX_ATTEMPTS):
            for column in range(self.CODE_LENGTH):
                rect = self._history_tile_rect(row, column)
                if row < len(self.guesses):
                    digit = self.guesses[row][column]
                    state = self.results[row][column]
                    pygame.draw.rect(surface, state_colors[state], rect, border_radius=5)
                    text_color = SCREEN_BLACK if state != "absent" else INK_MUTED
                    draw_text(surface, digit, font(15, True), text_color, rect.center, "center")
                else:
                    pygame.draw.rect(surface, (22, 30, 26), rect, border_radius=5)
                    pygame.draw.rect(surface, BORDER_DARK, rect, 1, border_radius=5)

        draw_text(
            surface,
            f"TENTATIVA {min(len(self.guesses) + 1, self.MAX_ATTEMPTS)}/{self.MAX_ATTEMPTS}",
            font(13, True),
            INK_MUTED,
            (self.LEGEND_X, self.HISTORY_ORIGIN[1]),
        )
        legend_y = self.HISTORY_ORIGIN[1] + 32
        for label, color in (
            ("posição certa", GREEN),
            ("dígito certo, lugar errado", AMBER),
            ("não está na senha", PANEL_MID),
        ):
            pygame.draw.rect(surface, color, pygame.Rect(self.LEGEND_X, legend_y, 16, 16), border_radius=3)
            draw_wrapped(surface, label, font(13), INK_MUTED, pygame.Rect(self.LEGEND_X + 24, legend_y - 2, 210, 40), 16)
            legend_y += 34

        if self.phase == "wrong":
            draw_text(surface, f"COFRE TRAVADO. SENHA ERA {self.code}.", font(15, True), RED, (self.LEGEND_X, legend_y + 8))
        elif self.phase == "right":
            draw_text(surface, "COFRE ABERTO!", font(17, True), GREEN, (self.LEGEND_X, legend_y + 8))

        for index in range(self.CODE_LENGTH):
            rect = self._digit_box_rect(index)
            pygame.draw.rect(surface, PANEL, rect, border_radius=6)
            is_cursor = index == len(self.current_digits)
            pygame.draw.rect(surface, AMBER if is_cursor else INK_BRIGHT, rect, 2, border_radius=6)
            if index < len(self.current_digits):
                draw_text(surface, self.current_digits[index], font(28, True), INK_BRIGHT, rect.center, "center")

        for row, labels in enumerate(VAULT_NUMPAD):
            for column, label in enumerate(labels):
                rect = self._numpad_rect(row, column)
                if label == "OK":
                    color = GREEN
                elif label == "C":
                    color = RED
                else:
                    color = PANEL_MID
                pygame.draw.rect(surface, color, rect, border_radius=6)
                pygame.draw.rect(surface, BORDER_DARK, rect, 2, border_radius=6)
                text_color = SCREEN_BLACK if label in ("OK", "C") else INK_BRIGHT
                draw_text(surface, label, font(19, True), text_color, rect.center, "center")


# ---------------------------------------------------------------------------
# 13. Hold and release: press the button, watch the number, let go at the right
#     moment - a "The Button"-style reflex-under-a-rule module.
# ---------------------------------------------------------------------------
BUTTON_RULES = (
    ("PAR", lambda digit: digit % 2 == 0),
    ("ÍMPAR", lambda digit: digit % 2 == 1),
    ("MAIOR QUE 6", lambda digit: digit > 6),
    ("MENOR QUE 3", lambda digit: digit < 3),
)


class HoldReleaseCaptcha(Captcha):
    kind = "botao"
    instruction = "Clique e segure o botão. Solte só quando o número satisfizer a regra."
    ROUNDS_TO_WIN = 3
    MIN_HOLD_SECONDS = 1.0
    DIGIT_STEP_SECONDS = 0.9
    RIGHT_PAUSE_SECONDS = 0.6
    WRONG_PAUSE_SECONDS = 1.3
    BUTTON_CENTER = (200, 180)
    BUTTON_RADIUS = 90

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.round = 0
        self.rule_label = ""
        self.rule_check = None
        self.phase = "idle"  # idle | holding | right | wrong
        self.hold_time = 0.0
        self.digit = 0
        self.digit_timer = 0.0
        self.timer = 0.0
        self._new_rule()

    def _new_rule(self) -> None:
        self.rule_label, self.rule_check = self.rng.choice(BUTTON_RULES)

    def _roll_digit(self) -> int:
        """A fresh digit that is never the same as the one just shown, so every digit
        stays on screen for exactly DIGIT_STEP_SECONDS - no digit can luck into a
        repeat draw and visibly linger longer than the others."""
        choices = [d for d in range(10) if d != self.digit]
        return self.rng.choice(choices)

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.phase != "idle":
            return
        if pygame.Vector2(pos).distance_to(self.BUTTON_CENTER) <= self.BUTTON_RADIUS:
            self.phase = "holding"
            self.hold_time = 0.0
            self.digit = self.rng.randrange(10)
            self.digit_timer = 0.0
            self.events.append("click")

    def on_mouse_up(self, pos: tuple[int, int]) -> None:
        if self.phase != "holding":
            return
        ok = self.hold_time >= self.MIN_HOLD_SECONDS and self.rule_check(self.digit)
        if ok:
            self.round += 1
            self.phase = "right"
            self.timer = self.RIGHT_PAUSE_SECONDS
            self.events.append("toggle")
        else:
            self.phase = "wrong"
            self.timer = self.WRONG_PAUSE_SECONDS
            self.fail()

    def update(self, dt: float) -> None:
        if self.phase == "holding":
            self.hold_time += dt
            self.digit_timer += dt
            if self.digit_timer >= self.DIGIT_STEP_SECONDS:
                self.digit_timer -= self.DIGIT_STEP_SECONDS
                self.digit = self._roll_digit()
        elif self.phase in ("right", "wrong"):
            self.timer -= dt
            if self.timer <= 0:
                if self.phase == "right":
                    if self.round >= self.ROUNDS_TO_WIN:
                        self.win()
                        return
                else:
                    self.round = 0
                self._new_rule()
                self.phase = "idle"

    def render(self, surface: pygame.Surface) -> None:
        if self.phase == "holding":
            color = AMBER
        elif self.phase == "right":
            color = GREEN
        elif self.phase == "wrong":
            color = RED
        else:
            color = PANEL_MID
        pygame.draw.circle(surface, color, self.BUTTON_CENTER, self.BUTTON_RADIUS)
        pygame.draw.circle(surface, SCREEN_BLACK, self.BUTTON_CENTER, self.BUTTON_RADIUS, 4)
        if self.phase == "holding":
            draw_text(surface, str(self.digit), font(48, True), SCREEN_BLACK, self.BUTTON_CENTER, "center")
            ready = self.hold_time >= self.MIN_HOLD_SECONDS
            draw_text(
                surface,
                "PRONTO PRA SOLTAR" if ready else "SEGURE...",
                font(14, True),
                SCREEN_BLACK,
                (self.BUTTON_CENTER[0], self.BUTTON_CENTER[1] + self.BUTTON_RADIUS + 22),
                "center",
            )
        elif self.phase == "idle":
            draw_text(surface, "CLIQUE E SEGURE", font(15, True), INK_MUTED, self.BUTTON_CENTER, "center")

        panel_x = 460
        draw_text(surface, "REGRA:", font(14, True), INK_MUTED, (panel_x, 30))
        draw_wrapped(surface, f"Solte quando o número for {self.rule_label}.", font(18, True), AMBER, pygame.Rect(panel_x, 52, 230, 60), 22)
        draw_text(surface, f"Rodada {min(self.round + 1, self.ROUNDS_TO_WIN)} de {self.ROUNDS_TO_WIN}", font(14), INK_MUTED, (panel_x, 150))
        draw_wrapped(surface, f"Segure pelo menos {self.MIN_HOLD_SECONDS:.0f}s antes de soltar.", font(13), INK_MUTED, pygame.Rect(panel_x, 176, 230, 40), 17)
        if self.phase == "wrong":
            draw_text(surface, "ERRADO! Nova regra chegando...", font(15, True), RED, (panel_x, 260))
        elif self.phase == "right" and self.round < self.ROUNDS_TO_WIN:
            draw_text(surface, "Certo! Próxima regra...", font(15, True), GREEN, (panel_x, 260))


# ---------------------------------------------------------------------------
# 14. Hidden maze: navigate a generated maze from start to exit with the arrows
# ---------------------------------------------------------------------------
MAZE_DIRECTIONS = (((0, -1), "UP"), ((0, 1), "DOWN"), ((-1, 0), "LEFT"), ((1, 0), "RIGHT"))
MAZE_KEY_DELTAS = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
}


class MazeCaptcha(Captcha):
    kind = "labirinto"
    instruction = "Use as setas do teclado para levar o ponto verde até a saída vermelha."
    COLUMNS = 6
    ROWS = 5
    CELL = 56
    ORIGIN = (36, 20)

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.passages: set[frozenset[tuple[int, int]]] = set()
        self.player = (0, 0)
        self.goal = (0, 0)
        self._deal()

    def _deal(self) -> None:
        self.passages = self._generate_maze()
        self.player = (0, 0)
        self.goal = self._farthest_cell(self.player)

    def _generate_maze(self) -> set[frozenset[tuple[int, int]]]:
        """Randomized depth-first backtracker: guarantees exactly one path between
        any two cells (a 'perfect' maze), so the puzzle never has a dead ambiguity."""
        start = (0, 0)
        visited = {start}
        stack = [start]
        passages: set[frozenset[tuple[int, int]]] = set()
        while stack:
            cx, cy = stack[-1]
            neighbors = [
                (cx + dx, cy + dy)
                for (dx, dy), _ in MAZE_DIRECTIONS
                if 0 <= cx + dx < self.COLUMNS and 0 <= cy + dy < self.ROWS and (cx + dx, cy + dy) not in visited
            ]
            if neighbors:
                nxt = self.rng.choice(neighbors)
                passages.add(frozenset({(cx, cy), nxt}))
                visited.add(nxt)
                stack.append(nxt)
            else:
                stack.pop()
        return passages

    def _farthest_cell(self, start: tuple[int, int]) -> tuple[int, int]:
        """The goal is the cell requiring the longest path from the start, so the
        maze always demands real navigation instead of one lucky step."""
        distance = {start: 0}
        queue = deque([start])
        farthest = start
        while queue:
            cell = queue.popleft()
            for (dx, dy), _ in MAZE_DIRECTIONS:
                neighbor = (cell[0] + dx, cell[1] + dy)
                if (
                    0 <= neighbor[0] < self.COLUMNS
                    and 0 <= neighbor[1] < self.ROWS
                    and neighbor not in distance
                    and frozenset({cell, neighbor}) in self.passages
                ):
                    distance[neighbor] = distance[cell] + 1
                    queue.append(neighbor)
                    if distance[neighbor] > distance[farthest]:
                        farthest = neighbor
        return farthest

    def _cell_rect(self, x: int, y: int) -> pygame.Rect:
        return pygame.Rect(self.ORIGIN[0] + x * self.CELL, self.ORIGIN[1] + y * self.CELL, self.CELL, self.CELL)

    def on_key(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        delta = MAZE_KEY_DELTAS.get(event.key)
        if delta is None:
            return
        neighbor = (self.player[0] + delta[0], self.player[1] + delta[1])
        if (
            0 <= neighbor[0] < self.COLUMNS
            and 0 <= neighbor[1] < self.ROWS
            and frozenset({self.player, neighbor}) in self.passages
        ):
            self.player = neighbor
            self.events.append("click")
            if self.player == self.goal:
                self.win()

    def render(self, surface: pygame.Surface) -> None:
        for y in range(self.ROWS):
            for x in range(self.COLUMNS):
                pygame.draw.rect(surface, (20, 28, 22), self._cell_rect(x, y))
        for y in range(self.ROWS):
            for x in range(self.COLUMNS):
                rect = self._cell_rect(x, y)
                if x + 1 < self.COLUMNS and frozenset({(x, y), (x + 1, y)}) not in self.passages:
                    pygame.draw.line(surface, BORDER, rect.topright, rect.bottomright, 3)
                if y + 1 < self.ROWS and frozenset({(x, y), (x, y + 1)}) not in self.passages:
                    pygame.draw.line(surface, BORDER, rect.bottomleft, rect.bottomright, 3)
        outer = pygame.Rect(self.ORIGIN[0], self.ORIGIN[1], self.COLUMNS * self.CELL, self.ROWS * self.CELL)
        pygame.draw.rect(surface, BORDER, outer, 3)

        pygame.draw.circle(surface, RED, self._cell_rect(*self.goal).center, 14)
        pygame.draw.circle(surface, GREEN, self._cell_rect(*self.player).center, 14)

        panel_x = 440
        draw_text(surface, "SAÍDA DO LABIRINTO", font(15, True), INK_BRIGHT, (panel_x, 30))
        draw_wrapped(surface, "Use ↑ ↓ ← → para mover o ponto verde até o ponto vermelho.", font(14), INK_MUTED, pygame.Rect(panel_x, 60, 230, 80), 19)


# ---------------------------------------------------------------------------
# 15. Instrument panel: hold two drifting cockpit gauges inside their safe band at
#     the same time - a "keep the plane steady through turbulence" juggling module.
# ---------------------------------------------------------------------------
class InstrumentsCaptcha(Captcha):
    kind = "instrumentos"
    instruction = "Segure as setas para manter os DOIS ponteiros na faixa verde ao mesmo tempo."
    GAUGE_MIN = 0.0
    GAUGE_MAX = 100.0
    HOLD_SECONDS = 2.2
    SAFE_HALF_WIDTH = 11.0
    NUDGE_SPEED = 46.0
    JERK = 26.0
    MAX_VELOCITY = 30.0
    LABELS = ("ALTITUDE", "INCLINAÇÃO")
    GAUGE_CENTERS = ((190, 150), (190, 300))
    GAUGE_SIZE = (320, 34)

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.targets = [0.0, 0.0]
        self.gauges = [0.0, 0.0]
        self.velocity = [0.0, 0.0]
        self.held_up = False
        self.held_down = False
        self.held_left = False
        self.held_right = False
        self.hold_timer = 0.0
        self._deal()

    def _deal(self) -> None:
        self.targets = [self.rng.uniform(30.0, 70.0), self.rng.uniform(30.0, 70.0)]
        self.gauges = [self.rng.uniform(self.GAUGE_MIN, self.GAUGE_MAX) for _ in range(2)]
        self.velocity = [0.0, 0.0]
        self.hold_timer = 0.0

    def on_key(self, event: pygame.event.Event) -> None:
        if event.type not in (pygame.KEYDOWN, pygame.KEYUP):
            return
        pressed = event.type == pygame.KEYDOWN
        if event.key == pygame.K_UP:
            self.held_up = pressed
        elif event.key == pygame.K_DOWN:
            self.held_down = pressed
        elif event.key == pygame.K_LEFT:
            self.held_left = pressed
        elif event.key == pygame.K_RIGHT:
            self.held_right = pressed

    def _clamp(self, value: float) -> float:
        return max(self.GAUGE_MIN, min(self.GAUGE_MAX, value))

    def update(self, dt: float) -> None:
        for index in range(2):
            jerked = self.velocity[index] + self.rng.uniform(-self.JERK, self.JERK) * dt
            self.velocity[index] = max(-self.MAX_VELOCITY, min(self.MAX_VELOCITY, jerked))
            self.gauges[index] = self._clamp(self.gauges[index] + self.velocity[index] * dt)
        if self.held_up:
            self.gauges[0] = self._clamp(self.gauges[0] + self.NUDGE_SPEED * dt)
        if self.held_down:
            self.gauges[0] = self._clamp(self.gauges[0] - self.NUDGE_SPEED * dt)
        if self.held_right:
            self.gauges[1] = self._clamp(self.gauges[1] + self.NUDGE_SPEED * dt)
        if self.held_left:
            self.gauges[1] = self._clamp(self.gauges[1] - self.NUDGE_SPEED * dt)

        both_safe = all(abs(self.gauges[i] - self.targets[i]) <= self.SAFE_HALF_WIDTH for i in range(2))
        if both_safe:
            self.hold_timer += dt
            if self.hold_timer >= self.HOLD_SECONDS:
                self.win()
        else:
            self.hold_timer = 0.0

    def render(self, surface: pygame.Surface) -> None:
        draw_text(surface, "PAINEL DE INSTRUMENTOS", font(18, True), INK_BRIGHT, (30, 24))
        draw_wrapped(
            surface,
            "Segure ↑/↓ para ALTITUDE e ←/→ para INCLINAÇÃO. Mantenha os dois na faixa verde ao mesmo tempo.",
            font(13),
            INK_MUTED,
            pygame.Rect(30, 52, 620, 40),
            17,
        )

        for index, (label, center) in enumerate(zip(self.LABELS, self.GAUGE_CENTERS)):
            rect = pygame.Rect(0, 0, *self.GAUGE_SIZE)
            rect.center = center
            pygame.draw.rect(surface, (20, 28, 22), rect, border_radius=8)
            span = self.GAUGE_MAX - self.GAUGE_MIN
            lo = (self.targets[index] - self.SAFE_HALF_WIDTH - self.GAUGE_MIN) / span
            hi = (self.targets[index] + self.SAFE_HALF_WIDTH - self.GAUGE_MIN) / span
            safe_rect = pygame.Rect(rect.x + round(rect.width * lo), rect.y, round(rect.width * (hi - lo)), rect.height)
            pygame.draw.rect(surface, (28, 66, 34), safe_rect, border_radius=8)
            pygame.draw.rect(surface, BORDER, rect, 2, border_radius=8)

            value_ratio = (self.gauges[index] - self.GAUGE_MIN) / span
            needle_x = rect.x + round(rect.width * value_ratio)
            in_safe = abs(self.gauges[index] - self.targets[index]) <= self.SAFE_HALF_WIDTH
            pygame.draw.line(surface, GREEN if in_safe else RED, (needle_x, rect.y - 6), (needle_x, rect.bottom + 6), 4)
            draw_text(surface, label, font(14, True), AMBER, (rect.x, rect.y - 26))

        stable_color = GREEN if self.hold_timer > 0 else INK_MUTED
        draw_text(surface, f"ESTÁVEL: {self.hold_timer:0.1f}s / {self.HOLD_SECONDS:0.1f}s", font(15, True), stable_color, (30, 340))


# ---------------------------------------------------------------------------
# 16. Control tower radio: decode a short ICAO phonetic-alphabet callsign before the
#     signal drops - a "read the radio fast" module in the same family as KTANE.
# ---------------------------------------------------------------------------
NATO_ALPHABET = {
    "A": "ALFA", "B": "BRAVO", "C": "CHARLIE", "D": "DELTA", "E": "ECHO", "F": "FOXTROT",
    "G": "GOLF", "H": "HOTEL", "I": "INDIA", "J": "JULIETT", "K": "KILO", "L": "LIMA",
    "M": "MIKE", "N": "NOVEMBER", "O": "OSCAR", "P": "PAPA", "Q": "QUEBEC", "R": "ROMEO",
    "S": "SIERRA", "T": "TANGO", "U": "UNIFORM", "V": "VICTOR", "W": "WHISKEY", "X": "XRAY",
    "Y": "YANKEE", "Z": "ZULU",
    "0": "ZERO", "1": "WUN", "2": "TOO", "3": "TREE", "4": "FOWER", "5": "FIFE",
    "6": "SIX", "7": "SEVEN", "8": "EIGHT", "9": "NINER",
}
RADIO_CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class RadioCaptcha(Captcha):
    kind = "radio"
    instruction = "Decodifique o alfabeto fonético da torre e digite o codinome exato."
    CODE_LENGTH = 4
    ROUNDS_TO_WIN = 2
    RIGHT_PAUSE_SECONDS = 0.8
    WRONG_PAUSE_SECONDS = 1.5

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.round = 0
        self.code = ""
        self.words: list[str] = []
        self.current = ""
        self.phase = "active"  # active | wrong | right
        self.timer = 0.0
        self._deal()

    def _deal(self) -> None:
        self.code = "".join(self.rng.choice(RADIO_CHARSET) for _ in range(self.CODE_LENGTH))
        self.words = [NATO_ALPHABET[char] for char in self.code]
        self.current = ""
        self.phase = "active"

    def on_key(self, event: pygame.event.Event) -> None:
        if self.phase != "active" or event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_BACKSPACE:
            self.current = self.current[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._submit()
        else:
            typed = getattr(event, "unicode", "").upper()
            if typed and typed in RADIO_CHARSET and len(self.current) < self.CODE_LENGTH:
                self.current += typed
                self.events.append("click")

    def _submit(self) -> None:
        if len(self.current) != self.CODE_LENGTH:
            return
        if self.current == self.code:
            self.round += 1
            self.phase = "right"
            self.timer = self.RIGHT_PAUSE_SECONDS
            self.events.append("toggle")
        else:
            self.phase = "wrong"
            self.timer = self.WRONG_PAUSE_SECONDS
            self.fail()

    def update(self, dt: float) -> None:
        if self.phase in ("wrong", "right"):
            self.timer -= dt
            if self.timer <= 0:
                if self.phase == "right":
                    if self.round >= self.ROUNDS_TO_WIN:
                        self.win()
                        return
                else:
                    self.round = 0
                self._deal()

    def render(self, surface: pygame.Surface) -> None:
        draw_text(surface, "TORRE DE CONTROLE", font(20, True), CYAN, (30, 20))
        draw_text(surface, f"Rodada {min(self.round + 1, self.ROUNDS_TO_WIN)} de {self.ROUNDS_TO_WIN}", font(14), INK_MUTED, (30, 50))

        y = 90
        for index, word in enumerate(self.words):
            draw_text(surface, f"{index + 1}. {word}", font(24, True), AMBER, (30, y))
            y += 42

        box_origin = (430, 130)
        for index in range(self.CODE_LENGTH):
            rect = pygame.Rect(box_origin[0] + index * 64, box_origin[1], 54, 64)
            pygame.draw.rect(surface, PANEL, rect, border_radius=8)
            is_cursor = index == len(self.current)
            pygame.draw.rect(surface, AMBER if is_cursor else INK_BRIGHT, rect, 3 if is_cursor else 2, border_radius=8)
            if index < len(self.current):
                draw_text(surface, self.current[index], font(30, True), INK_BRIGHT, rect.center, "center")

        draw_wrapped(
            surface,
            "Digite as letras/números correspondentes e aperte Enter.",
            font(13),
            INK_MUTED,
            pygame.Rect(430, 210, 260, 60),
            18,
        )
        if self.phase == "wrong":
            draw_text(surface, f"ERRADO! ERA {self.code}", font(16, True), RED, (430, 280))
        elif self.phase == "right":
            draw_text(surface, "CONFIRMADO!", font(16, True), GREEN, (430, 280))


# ---------------------------------------------------------------------------
# 17. Visual memory: memorize a lit pattern on a grid that grows each round
#     (3x3 -> 4x4 -> 5x5), inspired by Human Benchmark's "Visual Memory" test.
# ---------------------------------------------------------------------------
class VisualMemoryCaptcha(Captcha):
    kind = "padrao"
    instruction = "Memorize os quadrados acesos e clique de volta neles, na ordem que quiser."
    SIZES = (3, 4, 5)
    REVEAL_SECONDS = 1.6
    RIGHT_PAUSE_SECONDS = 0.6
    WRONG_PAUSE_SECONDS = 1.6
    CELL = 52
    GAP = 6
    GRID_BOX = (20, 16, 340, 328)  # x, y, width, height the grid is centered inside

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.round_index = 0
        self.phase = "showing"  # showing | answering | right | wrong
        self.timer = 0.0
        self.pattern: set[tuple[int, int]] = set()
        self.clicked: set[tuple[int, int]] = set()
        self.wrong_cell: tuple[int, int] | None = None
        self._deal_round()

    def _grid_size(self) -> int:
        return self.SIZES[self.round_index]

    def _deal_round(self) -> None:
        size = self._grid_size()
        cells = [(x, y) for x in range(size) for y in range(size)]
        self.rng.shuffle(cells)
        lit_count = size * size // 2
        self.pattern = set(cells[:lit_count])
        self.clicked = set()
        self.wrong_cell = None
        self.phase = "showing"
        self.timer = self.REVEAL_SECONDS

    def _origin(self) -> tuple[int, int]:
        size = self._grid_size()
        total = size * self.CELL + (size - 1) * self.GAP
        box_x, box_y, box_w, box_h = self.GRID_BOX
        return box_x + (box_w - total) // 2, box_y + (box_h - total) // 2

    def _cell_rect(self, x: int, y: int) -> pygame.Rect:
        origin_x, origin_y = self._origin()
        return pygame.Rect(
            origin_x + x * (self.CELL + self.GAP),
            origin_y + y * (self.CELL + self.GAP),
            self.CELL,
            self.CELL,
        )

    def _cell_at(self, pos: tuple[int, int]) -> tuple[int, int] | None:
        size = self._grid_size()
        for x in range(size):
            for y in range(size):
                if self._cell_rect(x, y).collidepoint(pos):
                    return x, y
        return None

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.phase != "answering":
            return
        cell = self._cell_at(pos)
        if cell is None or cell in self.clicked:
            return
        if cell not in self.pattern:
            self.wrong_cell = cell
            self.phase = "wrong"
            self.timer = self.WRONG_PAUSE_SECONDS
            self.fail()
            return
        self.clicked.add(cell)
        self.events.append("click")
        if self.clicked == self.pattern:
            self.phase = "right"
            self.timer = self.RIGHT_PAUSE_SECONDS
            self.events.append("toggle")

    def update(self, dt: float) -> None:
        if self.phase == "showing":
            self.timer -= dt
            if self.timer <= 0:
                self.phase = "answering"
        elif self.phase in ("right", "wrong"):
            self.timer -= dt
            if self.timer <= 0:
                if self.phase == "right":
                    if self.round_index >= len(self.SIZES) - 1:
                        self.win()
                        return
                    self.round_index += 1
                else:
                    self.round_index = 0
                self._deal_round()

    def render(self, surface: pygame.Surface) -> None:
        size = self._grid_size()
        for x in range(size):
            for y in range(size):
                rect = self._cell_rect(x, y)
                cell = (x, y)
                if self.phase == "showing":
                    color = CYAN if cell in self.pattern else (24, 32, 27)
                elif self.phase == "wrong":
                    if cell == self.wrong_cell:
                        color = RED
                    elif cell in self.pattern:
                        color = GREEN
                    else:
                        color = (24, 32, 27)
                elif cell in self.clicked:
                    color = GREEN
                else:
                    color = (30, 40, 34)
                pygame.draw.rect(surface, color, rect, border_radius=6)
                pygame.draw.rect(surface, BORDER_DARK, rect, 2, border_radius=6)

        panel_x = 400
        draw_text(surface, "MEMÓRIA VISUAL", font(19, True), INK_BRIGHT, (panel_x, 20))
        draw_text(surface, f"Grade {size}x{size} — rodada {self.round_index + 1} de {len(self.SIZES)}", font(14), INK_MUTED, (panel_x, 52))
        if self.phase == "showing":
            status, status_color = "MEMORIZE...", AMBER
        elif self.phase == "wrong":
            status, status_color = "ERRADO! Recomeçando do 3x3.", RED
        elif self.phase == "right":
            status, status_color = "TUDO CERTO!", GREEN
        else:
            status, status_color = f"CLIQUE OS {len(self.pattern)} QUADRADOS CERTOS", GREEN
        draw_wrapped(surface, status, font(15, True), status_color, pygame.Rect(panel_x, 84, 300, 50), 19)
        draw_text(surface, f"Encontrados: {len(self.clicked)} de {len(self.pattern)}", font(13), INK_MUTED, (panel_x, 150))


# ---------------------------------------------------------------------------
# 18. Connect the wires: an Among Us-style wiring task - match each colored
#     connector on the left to its twin on the right, which the board shuffles.
# ---------------------------------------------------------------------------
CONNECT_WIRE_COLORS = (RED, AMBER, GREEN, CYAN)
CONNECT_WIRE_NAMES = ("VERMELHO", "AMARELO", "VERDE", "CIANO")


class ConnectWiresCaptcha(Captcha):
    kind = "conectar_fios"
    instruction = "Ligue cada conector da esquerda ao da mesma cor à direita."
    LEFT_X = 120
    RIGHT_X = 380
    TOP_Y = 50
    ROW_GAP = 72
    RADIUS = 20
    RIGHT_PAUSE_SECONDS = 0.6
    WRONG_PAUSE_SECONDS = 1.3

    def __init__(self, rng: random.Random, assets_root: Path) -> None:
        super().__init__(rng, assets_root)
        self.phase = "active"  # active | right | wrong
        self.timer = 0.0
        self.selected_left: int | None = None
        self.wrong_pair: tuple[int, int] | None = None
        self.right_order: list[int] = []
        self.connections: dict[int, int] = {}
        self._deal()

    def _deal(self) -> None:
        self.right_order = list(range(len(CONNECT_WIRE_COLORS)))
        self.rng.shuffle(self.right_order)
        self.connections = {}
        self.selected_left = None
        self.wrong_pair = None
        self.phase = "active"

    def _left_center(self, row: int) -> tuple[int, int]:
        return (self.LEFT_X, self.TOP_Y + row * self.ROW_GAP)

    def _right_center(self, row: int) -> tuple[int, int]:
        return (self.RIGHT_X, self.TOP_Y + row * self.ROW_GAP)

    def on_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.phase != "active":
            return
        count = len(CONNECT_WIRE_COLORS)
        used_left = set(self.connections.keys())
        used_right = set(self.connections.values())
        for row in range(count):
            if row in used_left:
                continue
            if pygame.Vector2(pos).distance_to(self._left_center(row)) <= self.RADIUS + 8:
                self.selected_left = row
                self.events.append("click")
                return
        if self.selected_left is None:
            return
        for row in range(count):
            if row in used_right:
                continue
            if pygame.Vector2(pos).distance_to(self._right_center(row)) <= self.RADIUS + 8:
                chosen_left = self.selected_left
                self.selected_left = None
                if self.right_order[row] == chosen_left:
                    self.connections[chosen_left] = row
                    self.events.append("toggle")
                    if len(self.connections) == count:
                        self.phase = "right"
                        self.timer = self.RIGHT_PAUSE_SECONDS
                else:
                    self.wrong_pair = (chosen_left, row)
                    self.phase = "wrong"
                    self.timer = self.WRONG_PAUSE_SECONDS
                    self.fail()
                return

    def update(self, dt: float) -> None:
        if self.phase in ("right", "wrong"):
            self.timer -= dt
            if self.timer <= 0:
                if self.phase == "right":
                    self.win()
                    return
                self._deal()

    def render(self, surface: pygame.Surface) -> None:
        count = len(CONNECT_WIRE_COLORS)
        for left_row, right_row in self.connections.items():
            pygame.draw.line(surface, CONNECT_WIRE_COLORS[left_row], self._left_center(left_row), self._right_center(right_row), 6)
        if self.phase == "wrong" and self.wrong_pair is not None:
            left_row, right_row = self.wrong_pair
            pygame.draw.line(surface, RED, self._left_center(left_row), self._right_center(right_row), 6)
        if self.selected_left is not None and self.hover is not None:
            pygame.draw.line(surface, INK_BRIGHT, self._left_center(self.selected_left), self.hover, 3)

        for row in range(count):
            center = self._left_center(row)
            pygame.draw.circle(surface, CONNECT_WIRE_COLORS[row], center, self.RADIUS)
            ring = INK_BRIGHT if self.selected_left == row else SCREEN_BLACK
            pygame.draw.circle(surface, ring, center, self.RADIUS, 4 if self.selected_left == row else 3)
        for row in range(count):
            center = self._right_center(row)
            pygame.draw.circle(surface, CONNECT_WIRE_COLORS[self.right_order[row]], center, self.RADIUS)
            pygame.draw.circle(surface, SCREEN_BLACK, center, self.RADIUS, 3)

        panel_x = 460
        draw_text(surface, "PAINEL DE FIAÇÃO", font(18, True), INK_BRIGHT, (panel_x, 30))
        draw_wrapped(
            surface,
            "Clique um conector da esquerda, depois o da mesma cor à direita. A ordem da direita muda toda vez.",
            font(13),
            INK_MUTED,
            pygame.Rect(panel_x, 62, 230, 100),
            17,
        )
        draw_text(surface, f"Ligados: {len(self.connections)} de {count}", font(14), INK_MUTED, (panel_x, 170))
        if self.phase == "wrong":
            left_row, _ = self.wrong_pair
            draw_text(surface, f"ERRADO! Não era {CONNECT_WIRE_NAMES[left_row]}.", font(14, True), RED, (panel_x, 210))
        elif self.phase == "right":
            draw_text(surface, "FIAÇÃO CORRETA!", font(15, True), GREEN, (panel_x, 210))


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
    if kind == "wires":
        return WireCutCaptcha(rng, assets_root)
    if kind == "termo":
        return TermoCaptcha(rng, assets_root)
    if kind == "cofre":
        return VaultCaptcha(rng, assets_root)
    if kind == "botao":
        return HoldReleaseCaptcha(rng, assets_root)
    if kind == "labirinto":
        return MazeCaptcha(rng, assets_root)
    if kind == "instrumentos":
        return InstrumentsCaptcha(rng, assets_root)
    if kind == "radio":
        return RadioCaptcha(rng, assets_root)
    if kind == "padrao":
        return VisualMemoryCaptcha(rng, assets_root)
    if kind == "conectar_fios":
        return ConnectWiresCaptcha(rng, assets_root)
    raise ValueError(f"Unknown captcha: {kind}")
