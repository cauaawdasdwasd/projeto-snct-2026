"""Animated tutorial films for the six protocols, drawn entirely by code.

Every film follows the same script so the player learns the rhythm:
    intro card (2.4s) -> demonstration with typed captions -> stamp verdict.
They are rendered on demand at FILM_SIZE, so the game needs no video codec, and
`scripts/render_protocol_videos.py` exports the very same frames to MP4.
"""

from __future__ import annotations

import math
import random

import pygame

from src.gameplay.protocols import PROTOCOLS, Protocol

FILM_SIZE = (540, 285)
INTRO_END = 2.4
VERDICT_START = 11.6
DURATION = 15.2
CAPTION_TOP = 250

BG = (6, 12, 10)
GRID = (9, 25, 20)
INK = (216, 221, 132)
BRIGHT = (247, 239, 161)
MUTED = (132, 142, 87)
AMBER = (237, 193, 91)
GREEN = (101, 191, 91)
RED = (224, 82, 67)
PURPLE = (160, 92, 172)
BLUE = (93, 159, 177)
PAPER = (220, 208, 169)
PAPER_LIGHT = (235, 225, 190)
PAPER_INK = (45, 40, 30)
DARK = (17, 23, 20)

STAMP_COLORS = {"approve": GREEN, "deny": RED, "review": AMBER, "violation": PURPLE}
ACCENTS = {"blue": (69, 105, 119), "olive": (74, 92, 52), "amber": (158, 113, 39), "red": (155, 61, 52)}


# ------------------------------------------------------------------ math
def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def ramp(t: float, start: float, end: float) -> float:
    return clamp01((t - start) / (end - start)) if end > start else float(t >= start)


def ease_out(x: float) -> float:
    return 1 - (1 - clamp01(x)) ** 3


def ease_in_out(x: float) -> float:
    x = clamp01(x)
    return x * x * (3 - 2 * x)


def lerp(a: float, b: float, x: float) -> float:
    return a + (b - a) * x


def typed(text: str, t: float, start: float, cps: float = 34.0) -> str:
    count = int(max(0.0, t - start) * cps)
    return text[:count]


def path_position(keys: list[tuple[float, tuple[float, float]]], t: float) -> tuple[float, float]:
    """Smoothly move through (time, point) keyframes."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t <= t1:
            x = ease_in_out((t - t0) / (t1 - t0))
            return lerp(p0[0], p1[0], x), lerp(p0[1], p1[1], x)
    return keys[-1][1]


# ---------------------------------------------------------------- canvas
class Film:
    """Base class: intro, caption bar, verdict stamp and CRT look."""

    def __init__(self, protocol: Protocol, portrait: pygame.Surface | None) -> None:
        self.protocol = protocol
        self.portrait = portrait
        self.surface = pygame.Surface(FILM_SIZE)
        self.font_tiny = self._font(13)
        self.font_small = self._font(15, bold=True)
        self.font_body = self._font(18, bold=True)
        self.font_big = self._font(30, bold=True)
        self.font_huge = self._font(42, bold=True)
        self.font_stamp = self._font(34, bold=True)
        self.crt = self._build_crt()
        self.captions: list[tuple[float, float, str]] = []
        self.events: list[tuple[float, str]] = []
        self.setup()
        self.events = sorted(
            [(0.2, "forward"), (INTRO_END + 0.1, "paper"), (VERDICT_START + 0.62, "stamp")] + self.events
        )

    # subclasses fill these
    def setup(self) -> None:
        raise NotImplementedError

    def scene(self, s: pygame.Surface, tm: float) -> None:
        raise NotImplementedError

    # ------------------------------------------------------------- frame
    def render(self, t: float) -> pygame.Surface:
        s = self.surface
        s.fill(BG)
        self._draw_grid(s, t)
        self.scene(s, t - INTRO_END)
        self._draw_caption(s, t - INTRO_END)
        if t >= VERDICT_START:
            self._draw_verdict(s, t - VERDICT_START)
        if t < INTRO_END + 0.5:
            self._draw_intro(s, t)
        s.blit(self.crt, (0, 0))
        self._draw_flicker(s, t)
        return s

    # -------------------------------------------------------- decoration
    def _draw_grid(self, s: pygame.Surface, t: float) -> None:
        for x in range(0, FILM_SIZE[0], 30):
            pygame.draw.line(s, GRID, (x, 0), (x, FILM_SIZE[1]))
        shift = int(t * 14) % 30
        for y in range(-30 + shift, FILM_SIZE[1], 30):
            pygame.draw.line(s, GRID, (0, y), (FILM_SIZE[0], y))

    def _draw_intro(self, s: pygame.Surface, t: float) -> None:
        fade = 1.0 - ramp(t, INTRO_END - 0.1, INTRO_END + 0.5)
        overlay = pygame.Surface(FILM_SIZE, pygame.SRCALPHA)
        overlay.fill((4, 8, 7, round(255 * fade)))
        slide = ease_out(ramp(t, 0.1, 0.9))
        if self.portrait is not None:
            height = 150
            scale = height / self.portrait.get_height()
            portrait = pygame.transform.smoothscale(
                self.portrait, (max(1, round(self.portrait.get_width() * scale)), height)
            )
            frame = portrait.get_rect(midleft=(int(lerp(-160, 46, slide)), 128))
            pygame.draw.rect(overlay, (*INK, round(255 * fade)), frame.inflate(10, 10), 3)
            portrait = portrait.copy()
            portrait.set_alpha(round(255 * fade))
            overlay.blit(portrait, frame)
        number = f"PROTOCOLO {self.protocol.number:02d}"
        self._text(overlay, number, self.font_small, (*AMBER, round(255 * fade)), (250, 68))
        name = typed(self.protocol.scientist.upper(), t, 0.7, 26)
        self._text(overlay, name, self.font_big, (*BRIGHT, round(255 * fade)), (250, 92))
        title = typed(self.protocol.title, t, 1.3, 30)
        self._text(overlay, title, self.font_body, (*INK, round(255 * fade)), (250, 136))
        if int(t * 3) % 2 == 0 and t < INTRO_END:
            pygame.draw.rect(overlay, (*BRIGHT, round(255 * fade)), (250 + self.font_body.size(title)[0] + 4, 138, 10, 18))
        hint = self.protocol.menu_hint
        self._wrap(overlay, hint, self.font_tiny, (*MUTED, round(255 * fade)), pygame.Rect(250, 172, 270, 40), 17)
        s.blit(overlay, (0, 0))

    def _draw_caption(self, s: pygame.Surface, tm: float) -> None:
        pygame.draw.rect(s, (3, 7, 6), (0, CAPTION_TOP, FILM_SIZE[0], FILM_SIZE[1] - CAPTION_TOP))
        pygame.draw.line(s, MUTED, (0, CAPTION_TOP), (FILM_SIZE[0], CAPTION_TOP), 2)
        for start, end, text in self.captions:
            if start <= tm < end + 0.4:
                shown = typed(text, tm, start, 46)
                self._text(s, shown, self.font_body, BRIGHT, (14, CAPTION_TOP + 10))
                if int(tm * 3) % 2 == 0 and len(shown) < len(text):
                    width = self.font_body.size(shown)[0]
                    pygame.draw.rect(s, BRIGHT, (14 + width + 3, CAPTION_TOP + 12, 9, 17))
                break

    def _draw_verdict(self, s: pygame.Surface, tv: float) -> None:
        dim = pygame.Surface(FILM_SIZE, pygame.SRCALPHA)
        dim.fill((0, 0, 0, round(190 * ramp(tv, 0, 0.35))))
        s.blit(dim, (0, 0))
        color = STAMP_COLORS.get(self.protocol.expected_stamp, AMBER)
        label = self.protocol.verdict
        self._text(s, "DECISÃO CORRETA", self.font_small, MUTED, (FILM_SIZE[0] // 2, 74), "center")
        # the stamp slams down: big and transparent first, then normal size with a shake
        progress = ramp(tv, 0.42, 0.62)
        if progress > 0:
            scale = lerp(2.4, 1.0, ease_out(progress))
            stamp = pygame.Surface((330, 96), pygame.SRCALPHA)
            pygame.draw.rect(stamp, color, stamp.get_rect(), 6)
            pygame.draw.rect(stamp, color, stamp.get_rect().inflate(-16, -16), 2)
            text = self.font_stamp.render(label, False, color)
            stamp.blit(text, text.get_rect(center=stamp.get_rect().center))
            stamp = pygame.transform.rotate(stamp, 6)
            stamp = pygame.transform.smoothscale(
                stamp, (round(stamp.get_width() * scale), round(stamp.get_height() * scale))
            )
            stamp.set_alpha(round(255 * clamp01(progress * 1.4)))
            shake = 0
            if 0.62 <= tv < 0.95:
                shake = round(math.sin(tv * 90) * (0.95 - tv) * 14)
            s.blit(stamp, stamp.get_rect(center=(FILM_SIZE[0] // 2 + shake, 138 + shake // 2)))
        reason = typed(self.protocol.reason, tv, 1.0, 40)
        self._wrap(s, reason, self.font_body, BRIGHT, pygame.Rect(40, 196, FILM_SIZE[0] - 80, 50), 24, center=True)

    def _build_crt(self) -> pygame.Surface:
        crt = pygame.Surface(FILM_SIZE, pygame.SRCALPHA)
        for y in range(0, FILM_SIZE[1], 3):
            pygame.draw.line(crt, (0, 0, 0, 46), (0, y), (FILM_SIZE[0], y))
        for step in range(14):
            alpha = round(64 * (1 - step / 14) ** 2)
            pygame.draw.rect(crt, (0, 0, 0, alpha), crt.get_rect().inflate(-step * 2, -step * 2), 2)
        return crt

    def _draw_flicker(self, s: pygame.Surface, t: float) -> None:
        y = int((t * 90) % (FILM_SIZE[1] + 40)) - 20
        band = pygame.Surface((FILM_SIZE[0], 14), pygame.SRCALPHA)
        band.fill((216, 221, 132, 10))
        s.blit(band, (0, y))
        noise = random.Random(int(t * 24))
        for _ in range(14):
            s.set_at((noise.randrange(FILM_SIZE[0]), noise.randrange(FILM_SIZE[1])), (120, 135, 90))

    # ----------------------------------------------------------- helpers
    def paper(self, s: pygame.Surface, rect: pygame.Rect, title: str, accent: str = "blue") -> None:
        pygame.draw.rect(s, (0, 0, 0), rect.move(4, 4))
        pygame.draw.rect(s, PAPER, rect)
        pygame.draw.rect(s, ACCENTS[accent], (rect.x, rect.y, rect.width, 26))
        self._text(s, title, self.font_tiny, PAPER_LIGHT, (rect.x + 10, rect.y + 6))
        pygame.draw.rect(s, PAPER_INK, rect, 3)

    def field(
        self,
        s: pygame.Surface,
        rect: pygame.Rect,
        label: str,
        value: str,
        color: tuple[int, int, int] = PAPER_INK,
        glow: float = 0.0,
        big: bool = False,
    ) -> None:
        self._text(s, label, self.font_tiny, (91, 81, 58), (rect.x, rect.y - 15))
        pygame.draw.rect(s, PAPER_LIGHT, rect)
        pygame.draw.line(s, (159, 143, 101), rect.bottomleft, rect.bottomright, 3)
        font = self.font_big if big else self.font_small
        rendered = font.render(value, False, color)
        s.blit(rendered, rendered.get_rect(midleft=(rect.x + 8, rect.centery)))
        if glow > 0:
            grown = rect.inflate(round(10 * glow), round(10 * glow))
            pygame.draw.rect(s, AMBER, grown, 3)

    def cursor(self, s: pygame.Surface, position: tuple[float, float], click: float = 0.0) -> None:
        x, y = round(position[0]), round(position[1])
        if click > 0:
            radius = round(6 + click * 22)
            ring = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*BRIGHT, round(200 * (1 - click))), (radius + 2, radius + 2), radius, 2)
            s.blit(ring, (x - radius - 2, y - radius - 2))
        points = [(x, y), (x, y + 19), (x + 5, y + 14), (x + 9, y + 23), (x + 13, y + 21), (x + 9, y + 12), (x + 16, y + 12)]
        pygame.draw.polygon(s, (0, 0, 0), [(px + 2, py + 2) for px, py in points])
        pygame.draw.polygon(s, BRIGHT, points)
        pygame.draw.polygon(s, (0, 0, 0), points, 1)

    @staticmethod
    def click_at(t: float, when: float) -> float:
        return ramp(t, when, when + 0.45) if t >= when else 0.0

    def badge(self, s: pygame.Surface, center: tuple[int, int], text: str, color: tuple[int, int, int], x: float) -> None:
        if x <= 0:
            return
        scale = ease_out(x)
        rendered = self.font_body.render(text, False, BRIGHT)
        rect = rendered.get_rect().inflate(28, 16)
        rect.width = round(rect.width * (0.6 + 0.4 * scale))
        rect.center = center
        pygame.draw.rect(s, (0, 0, 0), rect.move(3, 3))
        pygame.draw.rect(s, DARK, rect)
        pygame.draw.rect(s, color, rect, 3)
        if rect.width >= rendered.get_width() + 20:
            s.blit(rendered, rendered.get_rect(center=rect.center))

    def check(self, s: pygame.Surface, center: tuple[int, int], color: tuple[int, int, int], x: float, size: int = 8) -> None:
        if x <= 0:
            return
        cx, cy = center
        p1 = (cx - size, cy)
        p2 = (cx - size * 0.3, cy + size * 0.8)
        p3 = (cx + size, cy - size * 0.9)
        pygame.draw.line(s, color, p1, (lerp(p1[0], p2[0], clamp01(x * 2)), lerp(p1[1], p2[1], clamp01(x * 2))), 4)
        if x > 0.5:
            pygame.draw.line(s, color, p2, (lerp(p2[0], p3[0], clamp01(x * 2 - 1)), lerp(p2[1], p3[1], clamp01(x * 2 - 1))), 4)

    def cross(self, s: pygame.Surface, center: tuple[int, int], color: tuple[int, int, int], x: float, size: int = 8) -> None:
        if x <= 0:
            return
        cx, cy = center
        reach = size * clamp01(x * 2)
        pygame.draw.line(s, color, (cx - reach, cy - reach), (cx + reach, cy + reach), 4)
        if x > 0.5:
            reach = size * clamp01(x * 2 - 1)
            pygame.draw.line(s, color, (cx + reach, cy - reach), (cx - reach, cy + reach), 4)

    def dashed(self, s: pygame.Surface, start: tuple[float, float], end: tuple[float, float], color: tuple[int, int, int], progress: float = 1.0) -> None:
        delta = pygame.Vector2(end) - pygame.Vector2(start)
        length = delta.length() * clamp01(progress)
        if length <= 0:
            return
        direction = delta.normalize()
        distance = 0.0
        while distance < length:
            a = pygame.Vector2(start) + direction * distance
            b = pygame.Vector2(start) + direction * min(distance + 8, length)
            pygame.draw.line(s, color, a, b, 3)
            distance += 14

    def person(self, s: pygame.Surface, center: tuple[int, int], color: tuple[int, int, int], size: float = 1.0) -> None:
        cx, cy = center
        pygame.draw.circle(s, color, (cx, round(cy - 16 * size)), round(8 * size))
        body = pygame.Rect(0, 0, round(26 * size), round(24 * size))
        body.midtop = (cx, round(cy - 6 * size))
        pygame.draw.rect(s, color, body, border_top_left_radius=round(12 * size), border_top_right_radius=round(12 * size))

    def _text(self, s: pygame.Surface, text: str, font: pygame.font.Font, color, position: tuple[int, int], anchor: str = "topleft") -> None:
        rendered = font.render(text, False, color[:3])
        if len(color) == 4:
            rendered.set_alpha(color[3])
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        s.blit(rendered, rect)

    def _wrap(self, s: pygame.Surface, text: str, font: pygame.font.Font, color, rect: pygame.Rect, line_height: int, center: bool = False) -> None:
        lines: list[str] = []
        current = ""
        for word in text.split(" "):
            candidate = f"{current} {word}".strip()
            if not current or font.size(candidate)[0] <= rect.width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        for index, line in enumerate(lines[:3]):
            if center:
                self._text(s, line, font, color, (rect.centerx, rect.y + index * line_height), "midtop")
            else:
                self._text(s, line, font, color, (rect.x, rect.y + index * line_height))

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)


# ============================================================ the six films
class GraceFilm(Film):
    def setup(self) -> None:
        self.captions = [
            (0.4, 3.6, "1. Pegue o ID da pessoa analisada."),
            (3.6, 6.6, "2. Compare com o ID do registro usado pela IA."),
            (6.6, 9.0, "IDs diferentes = pessoas diferentes."),
        ]
        self.events = [(2.9, "click"), (4.8, "click"), (5.9, "error"), (7.4, "error")]

    def scene(self, s: pygame.Surface, tm: float) -> None:
        slide = ease_out(ramp(tm, 0, 0.9))
        left = pygame.Rect(20 - round((1 - slide) * 320), 14, 236, 176)
        right = pygame.Rect(284 + round((1 - slide) * 320), 14, 236, 176)
        self.paper(s, left, "PESSOA ANALISADA", "blue")
        self.paper(s, right, "REGISTRO USADO PELA IA", "red")
        self.field(s, pygame.Rect(left.x + 14, left.y + 52, 208, 30), "NOME", "Ana Ribeiro")
        self.field(s, pygame.Rect(right.x + 14, right.y + 52, 208, 30), "NOME", "A. Ribeiro")
        left_id = pygame.Rect(left.x + 14, left.y + 112, 208, 44)
        right_id = pygame.Rect(right.x + 14, right.y + 112, 208, 44)
        left_glow = ramp(tm, 1.4, 2.0)
        right_glow = ramp(tm, 3.6, 4.2)
        compare = tm - 4.9
        index = int(compare / 0.32) if compare > 0 else -1
        for owner, rect, digits, glow in (("l", left_id, "482731", left_glow), ("r", right_id, "482713", right_glow)):
            self._text(s, "ID", self.font_tiny, (91, 81, 58), (rect.x, rect.y - 15))
            pygame.draw.rect(s, PAPER_LIGHT, rect)
            pygame.draw.line(s, (159, 143, 101), rect.bottomleft, rect.bottomright, 3)
            for i, digit in enumerate(digits):
                x = rect.x + 14 + i * 30
                mismatch = i >= 4
                color = PAPER_INK
                if 0 <= i <= index:
                    if mismatch:
                        pygame.draw.rect(s, RED, (x - 4, rect.y + 4, 26, 36))
                        color = BRIGHT
                    else:
                        pygame.draw.rect(s, (160, 205, 140), (x - 4, rect.y + 4, 26, 36))
                s.blit(self.font_big.render(digit, False, color), (x, rect.y + 6))
            if glow > 0:
                pygame.draw.rect(s, AMBER, rect.inflate(round(10 * glow), round(10 * glow)), 3)
        if right_glow > 0:
            self.dashed(s, (left_id.right + 4, left_id.centery), (right_id.x - 4, right_id.centery), AMBER, right_glow)
        for i in range(min(6, max(0, index + 1))):
            x = left_id.x + 14 + i * 30 + 11
            good = i < 4
            self.check(s, (x, left_id.y - 22), GREEN, ramp(compare - i * 0.32, 0, 0.25), 6) if good else self.cross(
                s, (x, left_id.y - 22), RED, ramp(compare - i * 0.32, 0, 0.25), 6
            )
        badge = ramp(tm, 6.9, 7.4)
        self.badge(s, (270, 214), "≠  DIFERENTES", RED, badge)
        if badge > 0:
            self.person(s, (100, 224), BLUE, 0.6)
            self.person(s, (440, 224), (150, 150, 130), 0.6)
            self._text(s, "ANA", self.font_tiny, BLUE, (100, 233), "midtop")
            self._text(s, "OUTRA PESSOA", self.font_tiny, (170, 170, 150), (440, 233), "midtop")
        cursor = path_position(
            [(0.9, (270, 245)), (1.9, (left_id.x + 70, left_id.centery)), (3.2, (left_id.x + 70, left_id.centery)),
             (4.0, (right_id.x + 70, right_id.centery)), (9.0, (right_id.x + 70, right_id.centery))],
            tm,
        )
        if tm > 0.9 and tm < 8:
            self.cursor(s, cursor, max(self.click_at(tm, 2.4), self.click_at(tm, 4.2)))


class KatherineFilm(Film):
    def setup(self) -> None:
        self.captions = [
            (0.4, 3.0, "1. Pegue os números dos documentos."),
            (3.0, 6.6, "2. Refaça a conta com a calculadora."),
            (6.6, 9.0, "44 ÷ 40 = 110%. A IA disse 90%."),
        ]
        self.events = [(1.7, "click"), (2.5, "click"), (5.6, "success"), (7.4, "error")]

    def scene(self, s: pygame.Surface, tm: float) -> None:
        slide = ease_out(ramp(tm, 0, 0.9))
        left = pygame.Rect(20 - round((1 - slide) * 320), 14, 236, 176)
        right = pygame.Rect(284 + round((1 - slide) * 320), 14, 236, 176)
        self.paper(s, left, "META DA EQUIPE", "olive")
        self.paper(s, right, "RELATÓRIO DA IA", "red")
        self.field(s, pygame.Rect(left.x + 14, left.y + 52, 100, 30), "META", "40 tarefas", glow=ramp(tm, 1.2, 1.7))
        self.field(s, pygame.Rect(left.x + 124, left.y + 52, 100, 30), "CONCLUÍDAS", "44 tarefas", glow=ramp(tm, 2.0, 2.5))
        bar = pygame.Rect(left.x + 14, left.y + 116, 208, 22)
        pygame.draw.rect(s, PAPER_LIGHT, bar)
        fill = ramp(tm, 0.8, 2.4)
        pygame.draw.rect(s, GREEN, (bar.x, bar.y, round(bar.width * 44 / 50 * fill), bar.height))
        marker_x = bar.x + round(bar.width * 40 / 50)
        pygame.draw.line(s, RED, (marker_x, bar.y - 8), (marker_x, bar.bottom + 8), 3)
        self._text(s, "META", self.font_tiny, RED, (marker_x, bar.bottom + 10), "midtop")
        self._text(s, "PRODUTIVIDADE", self.font_tiny, (91, 81, 58), (right.x + 14, right.y + 42))
        self._text(s, "90%", self.font_huge, RED, (right.centerx, right.y + 96), "center")
        if tm > 6.9:
            pygame.draw.line(s, RED, (right.x + 50, right.y + 68), (right.right - 50, right.y + 126), 5)
        calc_show = ease_out(ramp(tm, 2.9, 3.5))
        if calc_show > 0:
            card = pygame.Rect(0, 0, 210, 138)
            card.center = (270, 100 + round((1 - calc_show) * 200))
            pygame.draw.rect(s, (0, 0, 0), card.move(4, 4))
            pygame.draw.rect(s, DARK, card)
            pygame.draw.rect(s, BRIGHT, card, 3)
            self._text(s, "CALCULADORA", self.font_tiny, MUTED, (card.x + 10, card.y + 8))
            expression = typed("44 ÷ 40 =", tm, 3.7, 6)
            self._text(s, expression, self.font_body, INK, (card.right - 12, card.y + 34), "topright")
            result_progress = ease_out(ramp(tm, 5.0, 6.3))
            if result_progress > 0:
                value = round(110 * result_progress)
                self._text(s, f"{value}%", self.font_huge, GREEN, (card.centerx, card.y + 92), "center")
        badge = ramp(tm, 7.0, 7.5)
        self.badge(s, (270, 220), "CONTA DA IA ERRADA", RED, badge)
        cursor = path_position(
            [(0.9, (270, 245)), (1.9, (left.x + 40, left.y + 78)), (2.6, (left.x + 160, left.y + 78)), (3.4, (300, 190)), (9.0, (300, 190))],
            tm,
        )
        if 0.9 < tm < 3.6:
            self.cursor(s, cursor, max(self.click_at(tm, 1.7), self.click_at(tm, 2.5)))


class AdaFilm(Film):
    def setup(self) -> None:
        self.captions = [
            (0.4, 3.2, "1. Leia os requisitos da vaga."),
            (3.2, 6.4, "2. O motivo da IA: 'não sabe Java'."),
            (6.4, 9.0, "Java não é requisito. Dado certo, critério errado."),
        ]
        self.events = [(1.1, "toggle"), (1.7, "toggle"), (2.3, "toggle"), (6.0, "error"), (7.2, "error")]

    def scene(self, s: pygame.Surface, tm: float) -> None:
        slide = ease_out(ramp(tm, 0, 0.9))
        left = pygame.Rect(20 - round((1 - slide) * 320), 14, 236, 200)
        right = pygame.Rect(284 + round((1 - slide) * 320), 14, 236, 200)
        self.paper(s, left, "VAGA: ANALISTA DE DADOS", "blue")
        self.paper(s, right, "DECISÃO DA IA", "red")
        self._text(s, "REQUISITOS", self.font_tiny, (91, 81, 58), (left.x + 14, left.y + 38))
        items = ("SQL", "Estatística", "2 anos de experiência")
        for i, item in enumerate(items):
            y = left.y + 62 + i * 36
            appear = ramp(tm, 0.7 + i * 0.6, 1.1 + i * 0.6)
            if appear <= 0:
                continue
            box = pygame.Rect(left.x + 16, y, 22, 22)
            pygame.draw.rect(s, PAPER_LIGHT, box)
            pygame.draw.rect(s, PAPER_INK, box, 2)
            self.check(s, box.center, (60, 140, 60), ramp(tm, 1.0 + i * 0.6, 1.5 + i * 0.6), 6)
            self._text(s, item, self.font_small, PAPER_INK, (left.x + 50, y + 3))
        slot = pygame.Rect(left.x + 16, left.y + 62 + 3 * 36, 204, 26)
        scan = ramp(tm, 3.6, 5.8)
        if scan > 0:
            y = left.y + 56 + round(scan * 3 * 36)
            band = pygame.Surface((204, 24), pygame.SRCALPHA)
            band.fill((237, 193, 91, 90))
            s.blit(band, (left.x + 16, min(y, slot.y - 6)))
        if tm > 5.8:
            pygame.draw.rect(s, RED, slot, 2)
            self._text(s, "JAVA?  NÃO ESTÁ NA LISTA", self.font_tiny, RED, (slot.x + 8, slot.y + 7))
        self._text(s, "NEGAR CANDIDATA", self.font_body, RED, (right.x + 14, right.y + 50))
        reason = typed("Motivo: ela não sabe Java", tm, 2.9, 24)
        self._text(s, reason, self.font_small, PAPER_INK, (right.x + 14, right.y + 96))
        if tm > 6.3:
            width = self.font_small.size("Motivo: ela não sabe Java")[0]
            pygame.draw.line(s, RED, (right.x + 14, right.y + 105), (right.x + 14 + width, right.y + 105), 4)
        self.badge(s, (270, 232), "CRITÉRIO QUE NÃO EXISTE", RED, ramp(tm, 6.9, 7.4))
        if 3.3 < tm < 6.0:
            magnifier = path_position([(3.3, (right.x + 30, right.y + 140)), (4.0, (left.x + 120, left.y + 70)), (5.8, (left.x + 120, left.y + 150))], tm)
            pygame.draw.circle(s, BRIGHT, (round(magnifier[0]), round(magnifier[1])), 15, 3)
            pygame.draw.line(s, BRIGHT, (magnifier[0] + 11, magnifier[1] + 11), (magnifier[0] + 24, magnifier[1] + 24), 4)


class RadiaFilm(Film):
    def setup(self) -> None:
        self.captions = [
            (0.4, 3.0, "1. Veja quais dados a IA consultou."),
            (3.0, 6.0, "2. Histórico médico é restrito. Exige autorização."),
            (6.0, 9.0, "Autorização: NÃO. Acesso não é permissão."),
        ]
        self.events = [(2.0, "scroll"), (4.4, "error"), (6.6, "error")]

    def scene(self, s: pygame.Surface, tm: float) -> None:
        slide = ease_out(ramp(tm, 0, 0.9))
        file_rect = pygame.Rect(24 - round((1 - slide) * 200), 44, 150, 120)
        ai_rect = pygame.Rect(366 + round((1 - slide) * 200), 44, 150, 120)
        self.paper(s, file_rect, "HISTÓRICO MÉDICO", "red")
        pygame.draw.rect(s, RED, (file_rect.x + 12, file_rect.y + 42, 82, 22))
        self._text(s, "RESTRITO", self.font_tiny, BRIGHT, (file_rect.x + 20, file_rect.y + 47))
        pygame.draw.rect(s, PAPER_INK, (file_rect.x + 12, file_rect.y + 76, 120, 8))
        pygame.draw.rect(s, PAPER_INK, (file_rect.x + 12, file_rect.y + 92, 90, 8))
        pygame.draw.rect(s, DARK, ai_rect)
        pygame.draw.rect(s, BLUE, ai_rect, 3)
        self._text(s, "IA DE RH", self.font_small, BLUE, (ai_rect.centerx, ai_rect.y + 12), "midtop")
        self._text(s, "risco de", self.font_tiny, MUTED, (ai_rect.centerx, ai_rect.y + 46), "midtop")
        self._text(s, "afastamento", self.font_tiny, MUTED, (ai_rect.centerx, ai_rect.y + 62), "midtop")
        # data packets travel from the file to the AI
        stream = ramp(tm, 1.2, 8.5)
        if stream > 0 and tm < 8.8:
            for i in range(6):
                phase = ((tm - 1.2) * 0.55 + i / 6) % 1.0
                x = lerp(file_rect.right + 6, ai_rect.x - 6, phase)
                pygame.draw.rect(s, AMBER, (round(x), 100 + round(math.sin(phase * 9) * 5), 10, 8))
        # the lock says NO, yet the data goes through
        lock_show = ease_out(ramp(tm, 2.8, 3.5))
        if lock_show > 0:
            cx, cy = 270, 92
            shake = round(math.sin(tm * 40) * 3) if 4.3 < tm < 5.2 else 0
            body = pygame.Rect(0, 0, 54, 42)
            body.center = (cx + shake, cy + 10)
            pygame.draw.arc(s, BRIGHT, pygame.Rect(body.x + 8, body.y - 26, 38, 44), 0, math.pi, 5)
            pygame.draw.rect(s, RED if tm > 4.3 else AMBER, body)
            pygame.draw.rect(s, BRIGHT, body, 3)
            pygame.draw.circle(s, DARK, body.center, 6)
            self._text(s, "AUTORIZAÇÃO:", self.font_tiny, MUTED, (cx, cy + 44), "midtop")
            if tm > 4.0:
                self._text(s, "NÃO", self.font_big, RED, (cx, cy + 58), "midtop")
        if tm > 5.4:
            verdict = typed("NÃO CONTRATAR", tm, 5.4, 24)
            self._text(s, verdict, self.font_small, RED, (ai_rect.centerx, ai_rect.bottom + 14), "midtop")
        self.badge(s, (270, 222), "ACESSO  ≠  PERMISSÃO", PURPLE, ramp(tm, 6.6, 7.1))


class FeiFeiFilm(Film):
    def setup(self) -> None:
        self.captions = [
            (0.4, 3.2, "1. Veja o histórico que treinou a IA."),
            (3.2, 6.4, "2. Compare quem tem o mesmo desempenho."),
            (6.4, 9.0, "Mesmo desempenho, nota diferente: viés."),
        ]
        self.events = [(2.0, "scroll"), (5.0, "toggle"), (5.8, "error")]

    def scene(self, s: pygame.Surface, tm: float) -> None:
        slide = ease_out(ramp(tm, 0, 0.9))
        left = pygame.Rect(20 - round((1 - slide) * 320), 14, 250, 200)
        right = pygame.Rect(292 + round((1 - slide) * 320), 14, 228, 200)
        self.paper(s, left, "HISTÓRICO DE PROMOÇÕES", "olive")
        base = left.y + 176
        grow = ease_out(ramp(tm, 0.7, 2.4))
        for i, (label, value, color) in enumerate((("HOMENS", 81, GREEN), ("MULHERES", 34, RED))):
            x = left.x + 34 + i * 106
            height = round(110 * value / 100 * grow)
            pygame.draw.rect(s, color, (x, base - height, 64, height))
            pygame.draw.rect(s, PAPER_INK, (x, base - round(110 * value / 100), 64, round(110 * value / 100)), 2)
            self._text(s, f"{round(value * grow)}%", self.font_body, PAPER_INK, (x + 32, base - height - 22), "midtop")
            self._text(s, label, self.font_tiny, PAPER_INK, (x + 32, base + 4), "midtop")
        self.paper(s, right, "NOTA DA IA", "red")
        arrow = ramp(tm, 2.6, 3.4)
        if arrow > 0:
            y = 110
            pygame.draw.line(s, AMBER, (left.right + 2, y), (left.right + 2 + round(20 * arrow), y), 4)
            pygame.draw.polygon(s, AMBER, [(left.right + 22, y - 8), (left.right + 22, y + 8), (left.right + 32, y)])
        for i, (name, note, color, when) in enumerate((("PESQUISADORA A", 62, RED, 4.2), ("PESQUISADOR B", 88, GREEN, 5.0))):
            y = right.y + 44 + i * 74
            self._text(s, name, self.font_tiny, PAPER_INK, (right.x + 14, y))
            self._text(s, "desempenho 90", self.font_tiny, (91, 81, 58), (right.x + 14, y + 16))
            pygame.draw.rect(s, PAPER_LIGHT, (right.x + 14, y + 36, 200, 14))
            pygame.draw.rect(s, (110, 140, 90), (right.x + 14, y + 36, round(200 * 0.9 * ramp(tm, 3.4, 4.2)), 14))
            appear = ramp(tm, when, when + 0.6)
            if appear > 0:
                self._text(s, f"NOTA {round(note * appear)}", self.font_small, color, (right.right - 12, y + 2), "topright")
        self.badge(s, (270, 232), "MESMO DESEMPENHO, NOTA DIFERENTE", PURPLE, ramp(tm, 6.8, 7.3))


class MargaretFilm(Film):
    def setup(self) -> None:
        self.captions = [
            (0.4, 3.2, "1. Dois documentos oficiais se contradizem."),
            (3.2, 6.4, "2. Não escolha o que parece mais certo."),
            (6.4, 9.0, "Sem resposta segura, chame uma pessoa."),
        ]
        self.events = [(2.0, "toggle"), (4.6, "error"), (6.8, "success")]

    def scene(self, s: pygame.Surface, tm: float) -> None:
        slide = ease_out(ramp(tm, 0, 0.9))
        left = pygame.Rect(20 - round((1 - slide) * 320), 14, 220, 150)
        right = pygame.Rect(300 + round((1 - slide) * 320), 14, 220, 150)
        self.paper(s, left, "REGISTRO DE PROMOÇÕES", "blue")
        self.paper(s, right, "SISTEMA INTERNO", "amber")
        self.field(s, pygame.Rect(left.x + 12, left.y + 56, 196, 34), "CARGO", "Pesquisadora Jr.")
        self._text(s, "desde maio", self.font_tiny, (91, 81, 58), (left.x + 12, left.y + 100))
        self.field(s, pygame.Rect(right.x + 12, right.y + 56, 196, 34), "CARGO", "Técnica de Lab.")
        pulse = 0.5 + 0.5 * math.sin(tm * 6)
        appear = ramp(tm, 1.4, 2.0)
        if appear > 0:
            self.dashed(s, (left.right + 6, 88), (right.x - 6, 88), RED, appear)
            size = round(34 + pulse * 6)
            question = pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=True).render("?", False, RED)
            s.blit(question, question.get_rect(center=(270, 88)))
        if tm > 2.6:
            self._text(s, "A DECISÃO DEPENDE DO CARGO ATUAL", self.font_small, AMBER, (270, 172), "midtop")
        gauge = ramp(tm, 3.6, 4.6)
        if gauge > 0:
            box = pygame.Rect(30, 204, 200, 30)
            pygame.draw.rect(s, DARK, box)
            pygame.draw.rect(s, MUTED, box, 2)
            self._text(s, "CERTEZA DA IA", self.font_tiny, MUTED, (box.x + 8, box.y - 14))
            width = round(184 * lerp(0.8, 0.12, ease_out(gauge)))
            pygame.draw.rect(s, RED, (box.x + 8, box.y + 8, width, 18))
        human = ease_out(ramp(tm, 5.0, 6.0))
        if human > 0:
            self.person(s, (300, 232 + round((1 - human) * 60)), BLUE, 0.9)
            self.check(s, (345, 214), GREEN, ramp(tm, 6.2, 6.8), 9)
        self.badge(s, (430, 218), "REVISÃO HUMANA", AMBER, ramp(tm, 6.6, 7.1))


FILM_CLASSES = {
    "grace_hopper": GraceFilm,
    "katherine_johnson": KatherineFilm,
    "ada_lovelace": AdaFilm,
    "radia_perlman": RadiaFilm,
    "fei_fei_li": FeiFeiFilm,
    "margaret_hamilton": MargaretFilm,
}


def create_film(slug: str, portrait: pygame.Surface | None) -> Film:
    protocol = next(p for p in PROTOCOLS if p.slug == slug)
    return FILM_CLASSES[slug](protocol, portrait)
