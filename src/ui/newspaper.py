from __future__ import annotations

import random

import pygame

from src.gameplay.cases import CaseResult
from src.ui.case_dialog import STAMP_LABELS


INK = (42, 36, 27)
INK_MUTED = (92, 78, 57)
PAPER = (211, 199, 158)
PAPER_LIGHT = (226, 216, 178)
PAPER_DARK = (158, 139, 98)
RED = (139, 43, 37)
GREEN = (54, 96, 55)
SCREEN_BLACK = (4, 7, 6)

NEWSPAPER_RECT = pygame.Rect(64, 20, 1426, 656)
CLOSE_RECT = pygame.Rect(1428, 35, 42, 42)
HERO_IMAGE_RECT = pygame.Rect(92, 269, 820, 319)
ARTICLE_COLUMN_RECT = pygame.Rect(944, 269, 492, 319)
PREVIOUS_RECT = pygame.Rect(92, 611, 52, 44)
PAGE_LABEL_RECT = pygame.Rect(152, 611, 172, 44)
NEXT_RECT = pygame.Rect(332, 611, 52, 44)
RESTART_RECT = pygame.Rect(1126, 611, 324, 44)


class FinalNewspaper:
    """Paginated end-of-shift newspaper with one illustrated consequence per page."""

    def __init__(self, article_images: dict[str, pygame.Surface]) -> None:
        self.article_images = article_images
        self.results: tuple[CaseResult, ...] = ()
        self.page_index = 0
        self.is_open = False
        self.hovered_control: str | None = None
        self.paper_background = self._build_paper_background()
        self.font_tiny = self._font(14)
        self.font_small = self._font(17)
        self.font_body = self._font(19)
        self.font_body_bold = self._font(19, bold=True)
        self.font_article = self._serif_font(25, bold=True)
        self.font_headline = self._serif_font(35, bold=True)
        self.font_masthead = self._serif_font(48, bold=True)

    @property
    def page_count(self) -> int:
        return len(self.results)

    def open(self, results: list[CaseResult]) -> None:
        self.results = tuple(results)
        self.page_index = 0
        self.is_open = True
        self.hovered_control = None

    def close(self) -> None:
        self.is_open = False
        self.hovered_control = None

    def handle_escape(self) -> bool:
        if not self.is_open:
            return False
        self.close()
        return True

    def handle_key_down(self, key: int) -> bool:
        if not self.is_open:
            return False
        if key in (pygame.K_LEFT, pygame.K_a):
            self.page_index = max(0, self.page_index - 1)
            return True
        if key in (pygame.K_RIGHT, pygame.K_d):
            self.page_index = min(self.page_count - 1, self.page_index + 1)
            return True
        return False

    def handle_mouse_down(self, position: tuple[int, int]) -> str | None:
        if not self.is_open:
            return None
        if CLOSE_RECT.collidepoint(position):
            self.close()
            return "close"
        if PREVIOUS_RECT.collidepoint(position):
            self.page_index = max(0, self.page_index - 1)
            return "previous"
        if NEXT_RECT.collidepoint(position):
            self.page_index = min(self.page_count - 1, self.page_index + 1)
            return "next"
        if RESTART_RECT.collidepoint(position):
            return "restart"
        return "consume"

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.hovered_control = None
        if not self.is_open or position is None:
            return
        controls = (
            ("close", CLOSE_RECT),
            ("previous", PREVIOUS_RECT),
            ("next", NEXT_RECT),
            ("restart", RESTART_RECT),
        )
        for control, rect in controls:
            if rect.collidepoint(position):
                self.hovered_control = control
                return

    def render(self, surface: pygame.Surface) -> None:
        if not self.is_open or not self.results:
            return
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 224))
        surface.blit(dim, (0, 0))
        surface.blit(self.paper_background, NEWSPAPER_RECT)

        result = self.results[self.page_index]
        article = result.case.newspaper_correct if result.correct else result.case.newspaper_incorrect
        self._draw_masthead(surface, result)
        self._draw_headline(surface, article.headline, result.correct)
        self._draw_hero_image(surface, article.image_asset)
        self._draw_article_column(surface, result, article.body)
        self._draw_navigation(surface)
        self._draw_close(surface)

    def _draw_masthead(self, surface: pygame.Surface, result: CaseResult) -> None:
        self._draw_text(surface, "O AUDITOR DIÁRIO", self.font_masthead, INK, (777, 35), anchor="midtop")
        self._draw_text(
            surface,
            "Notícias tão confiáveis quanto os dados que você deixou passar",
            self.font_tiny,
            INK_MUTED,
            (777, 84),
            anchor="midtop",
        )
        pygame.draw.line(surface, INK, (88, 105), (1465, 105), 4)
        pygame.draw.line(surface, INK, (88, 111), (1465, 111), 1)
        self._draw_text(surface, result.case.newspaper_section, self.font_tiny, RED, (91, 118))
        self._draw_text(surface, "25 DE AGOSTO DE 2026", self.font_tiny, INK_MUTED, (777, 118), anchor="midtop")
        self._draw_text(surface, "EDIÇÃO EXTRA", self.font_tiny, INK_MUTED, (1461, 118), anchor="topright")

    def _draw_headline(self, surface: pygame.Surface, headline: str, correct: bool) -> None:
        self._draw_wrapped_text(
            surface,
            headline,
            self.font_headline,
            INK if correct else RED,
            pygame.Rect(92, 145, 1368, 104),
            line_height=36,
            max_lines=3,
            center=True,
        )
        pygame.draw.line(surface, INK, (88, 253), (1465, 253), 3)

    def _draw_hero_image(self, surface: pygame.Surface, image_asset: str) -> None:
        pygame.draw.rect(surface, INK, HERO_IMAGE_RECT.inflate(6, 6))
        image = self.article_images[image_asset]
        surface.blit(self._cover_image(image, HERO_IMAGE_RECT.size), HERO_IMAGE_RECT)
        self._draw_text(
            surface,
            "ILUSTRAÇÃO RECONSTITUÍDA PELA REDAÇÃO",
            self.font_tiny,
            PAPER_LIGHT,
            (HERO_IMAGE_RECT.x + 12, HERO_IMAGE_RECT.bottom - 24),
        )

    def _draw_article_column(
        self,
        surface: pygame.Surface,
        result: CaseResult,
        body: str,
    ) -> None:
        color = GREEN if result.correct else RED
        pygame.draw.line(
            surface,
            PAPER_DARK,
            (ARTICLE_COLUMN_RECT.x - 17, ARTICLE_COLUMN_RECT.y),
            (ARTICLE_COLUMN_RECT.x - 17, ARTICLE_COLUMN_RECT.bottom),
            2,
        )
        status = "DESASTRE EVITADO" if result.correct else "DESASTRE AUTORIZADO"
        self._draw_text(surface, status, self.font_article, color, ARTICLE_COLUMN_RECT.topleft)
        self._draw_wrapped_text(
            surface,
            body,
            self.font_body,
            INK,
            pygame.Rect(ARTICLE_COLUMN_RECT.x, ARTICLE_COLUMN_RECT.y + 45, ARTICLE_COLUMN_RECT.width, 150),
            line_height=23,
            max_lines=7,
        )

        decision_rect = pygame.Rect(ARTICLE_COLUMN_RECT.x, ARTICLE_COLUMN_RECT.y + 210, ARTICLE_COLUMN_RECT.width, 91)
        pygame.draw.rect(surface, PAPER_LIGHT, decision_rect)
        pygame.draw.rect(surface, color, decision_rect, 3)
        self._draw_text(surface, "DECISÃO REGISTRADA PELO AUDITOR", self.font_tiny, INK_MUTED, (decision_rect.x + 15, decision_rect.y + 13))
        self._draw_text(
            surface,
            STAMP_LABELS.get(result.selected_stamp, result.selected_stamp.upper()),
            self.font_article,
            color,
            (decision_rect.x + 15, decision_rect.y + 43),
        )
        self._draw_text(
            surface,
            "CORRETA" if result.correct else "INCORRETA",
            self.font_body_bold,
            color,
            (decision_rect.right - 16, decision_rect.y + 49),
            anchor="topright",
        )

    def _draw_navigation(self, surface: pygame.Surface) -> None:
        pygame.draw.line(surface, INK, (88, 602), (1465, 602), 3)
        self._draw_arrow_button(
            surface,
            PREVIOUS_RECT,
            -1,
            self.page_index > 0,
            self.hovered_control == "previous",
        )
        self._draw_arrow_button(
            surface,
            NEXT_RECT,
            1,
            self.page_index < self.page_count - 1,
            self.hovered_control == "next",
        )
        pygame.draw.rect(surface, PAPER_LIGHT, PAGE_LABEL_RECT)
        pygame.draw.rect(surface, INK, PAGE_LABEL_RECT, 2)
        self._draw_text(
            surface,
            f"PÁGINA {self.page_index + 1}/{self.page_count}",
            self.font_body_bold,
            INK,
            PAGE_LABEL_RECT.center,
            anchor="center",
        )

        hovered = self.hovered_control == "restart"
        pygame.draw.rect(surface, INK if hovered else PAPER_LIGHT, RESTART_RECT)
        pygame.draw.rect(surface, INK, RESTART_RECT, 2)
        self._draw_text(
            surface,
            "REINICIAR TURNO",
            self.font_body_bold,
            PAPER_LIGHT if hovered else INK,
            RESTART_RECT.center,
            anchor="center",
        )

    def _draw_arrow_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        direction: int,
        enabled: bool,
        hovered: bool,
    ) -> None:
        active = enabled and hovered
        pygame.draw.rect(surface, INK if active else PAPER_LIGHT, rect)
        pygame.draw.rect(surface, INK if enabled else PAPER_DARK, rect, 2)
        color = PAPER_LIGHT if active else INK if enabled else PAPER_DARK
        cx, cy = rect.center
        points = (
            ((cx + 6, cy - 11), (cx - 8, cy), (cx + 6, cy + 11))
            if direction < 0
            else ((cx - 6, cy - 11), (cx + 8, cy), (cx - 6, cy + 11))
        )
        pygame.draw.polygon(surface, color, points)

    def _draw_close(self, surface: pygame.Surface) -> None:
        hovered = self.hovered_control == "close"
        pygame.draw.rect(surface, INK if hovered else PAPER_LIGHT, CLOSE_RECT)
        pygame.draw.rect(surface, INK, CLOSE_RECT, 2)
        color = PAPER_LIGHT if hovered else INK
        center_x, center_y = CLOSE_RECT.center
        pygame.draw.line(surface, color, (center_x - 9, center_y - 9), (center_x + 9, center_y + 9), 3)
        pygame.draw.line(surface, color, (center_x + 9, center_y - 9), (center_x - 9, center_y + 9), 3)

    @staticmethod
    def _cover_image(image: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
        target_width, target_height = size
        scale = max(target_width / image.get_width(), target_height / image.get_height())
        scaled = pygame.transform.scale(
            image,
            (round(image.get_width() * scale), round(image.get_height() * scale)),
        )
        excess_y = max(0, scaled.get_height() - target_height)
        crop_rect = pygame.Rect(0, round(excess_y * 0.25), target_width, target_height)
        crop_rect.centerx = scaled.get_rect().centerx
        return scaled.subsurface(crop_rect).copy()

    @staticmethod
    def _build_paper_background() -> pygame.Surface:
        surface = pygame.Surface(NEWSPAPER_RECT.size)
        surface.fill(PAPER)
        randomizer = random.Random("sob-analise-newspaper-pages")
        for _ in range(2100):
            x = randomizer.randrange(surface.get_width())
            y = randomizer.randrange(surface.get_height())
            shade = randomizer.choice((-8, -5, 4, 7))
            color = tuple(max(0, min(255, channel + shade)) for channel in PAPER)
            pygame.draw.rect(surface, color, (x, y, 2, 2))
        pygame.draw.rect(surface, SCREEN_BLACK, surface.get_rect(), 6)
        pygame.draw.rect(surface, PAPER_DARK, surface.get_rect().inflate(-18, -18), 2)
        return surface

    def _draw_wrapped_text(
        self,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        rect: pygame.Rect,
        *,
        line_height: int,
        max_lines: int,
        center: bool = False,
    ) -> int:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if not current or font.size(candidate)[0] <= rect.width:
                current = candidate
            else:
                lines.append(current)
                current = word
            if len(lines) >= max_lines:
                break
        if current and len(lines) < max_lines:
            lines.append(current)
        for index, line in enumerate(lines):
            position = (rect.centerx, rect.y + index * line_height) if center else (rect.x, rect.y + index * line_height)
            self._draw_text(
                surface,
                line,
                font,
                color,
                position,
                anchor="midtop" if center else "topleft",
            )
        return max(1, len(lines))

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)

    @staticmethod
    def _serif_font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Georgia", "Times New Roman", "serif"), size, bold=bold)

    @staticmethod
    def _draw_text(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        position: tuple[int, int],
        *,
        anchor: str = "topleft",
    ) -> None:
        rendered = font.render(text, False, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)
