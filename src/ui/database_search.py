from __future__ import annotations

import unicodedata
from typing import TYPE_CHECKING

import pygame

from src.gameplay.cases import AuditCase, SearchRecord

if TYPE_CHECKING:
    from src.core.audio import AudioManager


SEARCH_BUTTON_RECT = pygame.Rect(686, 69, 174, 36)
SEARCH_INPUT_RECT = pygame.Rect(86, 126, 1110, 52)
SEARCH_SUBMIT_RECT = pygame.Rect(1212, 126, 244, 52)
SEARCH_CLOSE_RECT = pygame.Rect(1430, 35, 42, 42)
RESULTS_RECT = pygame.Rect(86, 218, 1370, 414)

INK = (216, 222, 165)
INK_BRIGHT = (247, 239, 159)
INK_MUTED = (107, 124, 85)
AMBER = (206, 157, 62)
GREEN = (103, 161, 78)
SCREEN_BLACK = (4, 9, 7)
PANEL = (14, 21, 17)
PANEL_SELECTED = (27, 36, 27)
LINE = (64, 78, 53)


class DatabaseSearch:
    """Keyboard-driven internal search index with case-specific records."""

    def __init__(self, case: AuditCase, audio: AudioManager | None = None) -> None:
        self.audio = audio
        self.case = case
        self.is_open = False
        self.query = ""
        self.last_query = ""
        self.results: tuple[SearchRecord, ...] = ()
        self.selected_result = 0
        self.launcher_hovered = False
        self.input_hovered = False
        self.submit_hovered = False
        self.close_hovered = False

        self.font_tiny = self._font(15)
        self.font_small = self._font(18)
        self.font_body = self._font(21)
        self.font_body_bold = self._font(21, bold=True)
        self.font_title = self._font(31, bold=True)

    @property
    def is_available(self) -> bool:
        return bool(self.case.search_records)

    def set_case(self, case: AuditCase) -> None:
        self.close()
        self.case = case
        self.query = ""
        self.last_query = ""
        self.results = ()
        self.selected_result = 0

    def open(self) -> bool:
        if not self.is_available:
            return False
        self.is_open = True
        self.query = ""
        self.last_query = ""
        self.results = ()
        self.selected_result = 0
        pygame.key.start_text_input()
        return True

    def close(self) -> None:
        if self.is_open:
            pygame.key.stop_text_input()
        self.is_open = False

    def update_hover(self, position: tuple[int, int] | None) -> None:
        self.launcher_hovered = bool(
            self.is_available
            and not self.is_open
            and position is not None
            and SEARCH_BUTTON_RECT.collidepoint(position)
        )
        if not self.is_open:
            return
        self.input_hovered = bool(position and SEARCH_INPUT_RECT.collidepoint(position))
        self.submit_hovered = bool(position and SEARCH_SUBMIT_RECT.collidepoint(position))
        self.close_hovered = bool(position and SEARCH_CLOSE_RECT.collidepoint(position))
        if position is not None:
            for index, rect in enumerate(self._result_rects()):
                if rect.collidepoint(position):
                    self.selected_result = index
                    break

    def handle_launcher_click(self, position: tuple[int, int] | None) -> bool:
        if position is None or not self.is_available or not SEARCH_BUTTON_RECT.collidepoint(position):
            return False
        return self.open()

    def handle_event(
        self,
        event: pygame.event.Event,
        position: tuple[int, int] | None,
    ) -> None:
        if event.type == pygame.MOUSEMOTION:
            self.update_hover(position)
            return
        if event.type == pygame.TEXTINPUT:
            if len(self.query) < 48:
                self.query += event.text
            return
        if event.type == pygame.MOUSEWHEEL:
            self._move_selection(-event.y)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if position is None:
                return
            if SEARCH_CLOSE_RECT.collidepoint(position):
                self._play("click")
                self.close()
            elif SEARCH_SUBMIT_RECT.collidepoint(position):
                self._search()
            else:
                for index, rect in enumerate(self._result_rects()):
                    if rect.collidepoint(position):
                        self.selected_result = index
                        self._play("click", 0.55)
                        break
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_BACKSPACE:
            self.query = self.query[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._search()
        elif event.key == pygame.K_UP:
            self._move_selection(-1)
        elif event.key == pygame.K_DOWN:
            self._move_selection(1)

    def render_launcher(self, surface: pygame.Surface) -> None:
        if not self.is_available:
            return
        pygame.draw.rect(surface, PANEL_SELECTED if self.launcher_hovered else SCREEN_BLACK, SEARCH_BUTTON_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if self.launcher_hovered else LINE, SEARCH_BUTTON_RECT, 2)
        icon = pygame.Rect(SEARCH_BUTTON_RECT.x + 8, SEARCH_BUTTON_RECT.y + 7, 22, 22)
        pygame.draw.circle(surface, AMBER if self.launcher_hovered else INK_MUTED, icon.center, 8, 2)
        pygame.draw.line(surface, AMBER if self.launcher_hovered else INK_MUTED, (icon.centerx + 6, icon.centery + 6), (icon.right, icon.bottom), 2)
        self._text(surface, "BASE INTERNA", self.font_tiny, INK_BRIGHT if self.launcher_hovered else INK, (SEARCH_BUTTON_RECT.x + 38, SEARCH_BUTTON_RECT.y + 10))

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((3, 7, 6))
        pygame.draw.rect(surface, (8, 14, 11), (28, 22, 1498, 650))
        pygame.draw.rect(surface, (74, 87, 58), (28, 22, 1498, 650), 3)
        self._text(surface, "BASE INTERNA DE CONSULTA", self.font_title, INK_BRIGHT, (84, 48))
        self._text(surface, "ÍNDICE CORPORATIVO // RESULTADOS SIMULADOS", self.font_tiny, AMBER, (86, 88))
        self._draw_close(surface)

        pygame.draw.rect(surface, PANEL_SELECTED if self.input_hovered else SCREEN_BLACK, SEARCH_INPUT_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if self.input_hovered else LINE, SEARCH_INPUT_RECT, 2)
        query_text = self.query if self.query else "Digite nome, ID, código ou empresa..."
        query_color = INK_BRIGHT if self.query else INK_MUTED
        self._text(surface, query_text, self.font_body, query_color, (SEARCH_INPUT_RECT.x + 17, SEARCH_INPUT_RECT.y + 14))
        if int(pygame.time.get_ticks() / 520) % 2 == 0:
            cursor_x = SEARCH_INPUT_RECT.x + 17 + self.font_body.size(self.query)[0]
            pygame.draw.line(surface, INK_BRIGHT, (cursor_x, SEARCH_INPUT_RECT.y + 13), (cursor_x, SEARCH_INPUT_RECT.bottom - 13), 2)
        self._draw_submit(surface)

        pygame.draw.rect(surface, (5, 11, 9), RESULTS_RECT)
        pygame.draw.rect(surface, LINE, RESULTS_RECT, 2)
        if not self.last_query:
            self._text(surface, "A BASE ACEITA TERMOS PARCIAIS E COMBINAÇÕES.", self.font_small, INK_MUTED, (112, 252))
            self._text(surface, "Exemplos: nome + sobrenome, ID funcional, número de protocolo ou código de carga.", self.font_small, INK, (112, 287))
            return
        if not self.results:
            self._text(surface, f"NENHUM RESULTADO PARA: {self.last_query}", self.font_body_bold, AMBER, (112, 256))
            self._text(surface, "Confira letras, números e hífens ou tente menos termos.", self.font_small, INK_MUTED, (112, 295))
            return

        self._text(surface, f"{len(self.results):02d} RESULTADO(S) PARA: {self.last_query}", self.font_tiny, GREEN, (104, 194))
        for index, (record, rect) in enumerate(zip(self.results, self._result_rects())):
            selected = index == self.selected_result
            pygame.draw.rect(surface, PANEL_SELECTED if selected else PANEL, rect)
            pygame.draw.rect(surface, AMBER if selected else LINE, (rect.x, rect.y, 5, rect.height))
            self._text(surface, record.title, self.font_body_bold, INK_BRIGHT if selected else INK, (rect.x + 20, rect.y + 8))
            self._text(surface, record.source.upper(), self.font_tiny, AMBER if selected else INK_MUTED, (rect.right - 18, rect.y + 10), "topright")
            snippet_rect = pygame.Rect(rect.x + 20, rect.y + 37, rect.width - 40, 34)
            self._draw_wrapped(surface, record.snippet, self.font_tiny, INK if selected else INK_MUTED, snippet_rect)

    def _search(self) -> None:
        self.last_query = self.query.strip()
        self.selected_result = 0
        if not self.last_query:
            self.results = ()
            self._play("click", 0.55)
            return
        query = self._normalize(self.last_query)
        tokens = query.split()
        scored: list[tuple[int, SearchRecord]] = []
        for record in self.case.search_records:
            title = self._normalize(record.title)
            source = self._normalize(record.source)
            snippet = self._normalize(record.snippet)
            keywords = self._normalize(" ".join(record.keywords))
            combined = " ".join((title, source, snippet, keywords))
            if not all(token in combined for token in tokens):
                continue
            score = sum(5 for token in tokens if token in title)
            score += sum(3 for token in tokens if token in keywords)
            score += sum(1 for token in tokens if token in source or token in snippet)
            if query in title:
                score += 8
            scored.append((score, record))
        scored.sort(key=lambda item: (-item[0], item[1].title))
        self.results = tuple(record for _, record in scored[:5])
        self._play("confirm" if self.results else "click", 0.55)

    def _move_selection(self, direction: int) -> None:
        if not self.results:
            return
        self.selected_result = (self.selected_result + direction) % len(self.results)
        self._play("click", 0.4)

    def _result_rects(self) -> tuple[pygame.Rect, ...]:
        return tuple(
            pygame.Rect(102, 232 + index * 78, 1338, 70)
            for index in range(len(self.results))
        )

    def _draw_submit(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, PANEL_SELECTED if self.submit_hovered else PANEL, SEARCH_SUBMIT_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if self.submit_hovered else LINE, SEARCH_SUBMIT_RECT, 2)
        self._text(surface, "PESQUISAR", self.font_body_bold, INK_BRIGHT, SEARCH_SUBMIT_RECT.center, "center")

    def _draw_close(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, PANEL_SELECTED if self.close_hovered else PANEL, SEARCH_CLOSE_RECT)
        pygame.draw.rect(surface, INK_BRIGHT if self.close_hovered else LINE, SEARCH_CLOSE_RECT, 2)
        pygame.draw.line(surface, INK_BRIGHT, (1442, 47), (1460, 65), 2)
        pygame.draw.line(surface, INK_BRIGHT, (1460, 47), (1442, 65), 2)

    def _play(self, name: str, volume: float = 0.75) -> None:
        if self.audio is not None:
            self.audio.play(name, volume)

    @staticmethod
    def _normalize(value: str) -> str:
        decomposed = unicodedata.normalize("NFKD", value.casefold())
        plain = "".join(character for character in decomposed if not unicodedata.combining(character))
        return " ".join("".join(character if character.isalnum() else " " for character in plain).split())

    @staticmethod
    def _font(size: int, bold: bool = False) -> pygame.font.Font:
        return pygame.font.SysFont(("Consolas", "Courier New", "monospace"), size, bold=bold)

    @staticmethod
    def _text(
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        position: tuple[int, int],
        anchor: str = "topleft",
    ) -> None:
        rendered = font.render(text, False, color)
        rect = rendered.get_rect()
        setattr(rect, anchor, position)
        surface.blit(rendered, rect)

    @classmethod
    def _draw_wrapped(
        cls,
        surface: pygame.Surface,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        rect: pygame.Rect,
    ) -> None:
        words = text.split()
        line = ""
        lines: list[str] = []
        for word in words:
            candidate = f"{line} {word}".strip()
            if not line or font.size(candidate)[0] <= rect.width:
                line = candidate
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
        for index, item in enumerate(lines[:2]):
            cls._text(surface, item, font, color, (rect.x, rect.y + index * 17))
