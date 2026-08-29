from __future__ import annotations

import math
import random
from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame

from src.core.preferences import UserPreferences
from src.core.scene import Scene
from src.core.settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from src.ui.settings_panel import SettingsPanel

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.audio import AudioManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager


CRT_SCREEN_RECT = pygame.Rect(400, 174, 1120, 720)
INK = (208, 218, 167)
INK_BRIGHT = (245, 239, 164)
INK_MUTED = (98, 118, 81)
AMBER = (220, 168, 61)
RED = (176, 63, 45)
GREEN = (100, 158, 72)
LINE = (58, 75, 51)

MAIN_COMMANDS = ("INICIAR TURNO", "TREINAMENTO", "CONFIGURAÇÕES", "CRÉDITOS")
TUTORIAL_PAGES = (
    (
        "01 // LEIA E CRUZE",
        "Nenhum documento conta a história inteira.",
        (
            "Abra os documentos e a decisão da IA.",
            "Compare nomes, IDs, datas, contas e permissões.",
            "Consulte o protocolo quando a regra não estiver clara.",
        ),
    ),
    (
        "02 // PESQUISE",
        "Alguns rastros só aparecem na base interna.",
        (
            "Abra BASE INTERNA ou pressione CTRL + F.",
            "Digite um nome, ID, código ou empresa e pressione ENTER.",
            "Resultados parecidos podem pertencer a pessoas diferentes.",
        ),
    ),
    (
        "03 // DECIDA",
        "O carimbo responde à decisão da IA, não ao seu humor.",
        (
            "APROVAR: a decisão e os dados estão corretos.",
            "NEGAR: há erro objetivo na decisão.",
            "REVISÃO ou VIOLAÇÃO: use apenas quando o protocolo exigir.",
        ),
    ),
    (
        "04 // ENVIE",
        "Uma decisão confirmada produz consequências.",
        (
            "Carimbe o documento de decisão final.",
            "Confirme e envie para receber o próximo caso.",
            "Ao fim do turno, o noticiário revela o que aconteceu.",
        ),
    ),
)
TUTORIAL_BACK_RECT = pygame.Rect(455, 804, 190, 48)
TUTORIAL_PREV_RECT = pygame.Rect(1188, 804, 84, 48)
TUTORIAL_NEXT_RECT = pygame.Rect(1284, 804, 136, 48)
TEAM = (
    "CAUÃ DANIEL ABREU",
    "LETÍCIA FAUSTINO SORCHETI",
    "MARIAH LUIZA SOARES DE OLIVEIRA",
    "PEDRO GONÇALVES DA SILVA",
)


class MainMenuScene(Scene):
    """Old CRT title screen with mouse-driven physical parallax."""

    def __init__(
        self,
        manager: SceneManager,
        assets: AssetManager,
        input_manager: InputManager,
        audio: AudioManager | None = None,
        preferences_provider: Callable[[], UserPreferences] | None = None,
        apply_preferences: Callable[[UserPreferences], bool] | None = None,
    ) -> None:
        super().__init__(manager, assets, input_manager)
        self.audio = audio
        self.preferences_provider = preferences_provider or UserPreferences
        self.preferences = self.preferences_provider()
        self.view = "main"
        self.main_selection = 0
        self.tutorial_page = 0
        self.tutorial_hovered: str | None = None
        self.elapsed = 0.0
        self.parallax = pygame.Vector2()
        self.head_offset = (0, 0)

        background = self.assets.load_image("backgrounds/menu_crt_v1.png", alpha=False)
        self.background = pygame.transform.smoothscale(
            background,
            (VIRTUAL_WIDTH, VIRTUAL_HEIGHT),
        ).convert()
        self.screen_noise = self._build_screen_noise()
        self.scanlines = self._build_scanlines()
        self.screen_mask = self._build_screen_mask()
        self.screen_layer = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)

        self.font_tiny = self._font(16)
        self.font_small = self._font(20)
        self.font_body = self._font(25)
        self.font_body_bold = self._font(27, bold=True)
        self.font_title = self._font(73, bold=True)
        self.font_section = self._font(39, bold=True)

        self.main_rects = tuple(
            pygame.Rect(1035, 330 + index * 80, 390, 62)
            for index in range(len(MAIN_COMMANDS))
        )
        self.credits_back_rect = pygame.Rect(1190, 770, 230, 58)
        self.settings = SettingsPanel(
            pygame.Rect(445, 192, 1030, 680),
            audio,
            apply_preferences,
            draw_frame=False,
        )

    def on_enter(self) -> None:
        self.preferences = self.preferences_provider()
        self.elapsed = 0.0
        self.parallax.update(0, 0)
        self.head_offset = (0, 0)
        self.view = "main"
        self.main_selection = 0
        self.tutorial_page = 0
        self.tutorial_hovered = None
        if self.audio is not None:
            self.audio.play_music_sequence(("menu",), fade_ms=700)

    def handle_escape(self) -> bool:
        if self.view != "main":
            self._play_click(0.65)
            self.view = "main"
        return True

    def handle_event(self, event: pygame.event.Event) -> None:
        pointer = self._corrected_pointer(self.input_manager.mouse_position)
        if self.view == "settings":
            action = self.settings.handle_event(event, pointer)
            if action == "applied":
                self.preferences = self.settings.applied_preferences.copy()
            elif action == "back":
                self.view = "main"
            return

        if event.type == pygame.MOUSEMOTION:
            self._update_hover(pointer)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(pointer)
            return
        if event.type != pygame.KEYDOWN:
            return

        if self.view == "credits":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._play_click()
                self.view = "main"
            return
        if self.view == "tutorial":
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._change_tutorial_page(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
                if self.tutorial_page == len(TUTORIAL_PAGES) - 1:
                    self._play_click()
                    self.view = "main"
                else:
                    self._change_tutorial_page(1)
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.main_selection = (self.main_selection - 1) % len(MAIN_COMMANDS)
            self._play_click(0.5)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.main_selection = (self.main_selection + 1) % len(MAIN_COMMANDS)
            self._play_click(0.5)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate_main_command(self.main_selection)

    def update(self, dt: float) -> None:
        self.elapsed += dt
        pointer = self.input_manager.mouse_position
        if pointer is None:
            target = pygame.Vector2()
        else:
            target = pygame.Vector2(
                (pointer[0] / VIRTUAL_WIDTH - 0.5) * 12.0,
                (pointer[1] / VIRTUAL_HEIGHT - 0.5) * 8.0,
            )
        response = 1.0 - math.exp(-3.6 * dt)
        self.parallax += (target - self.parallax) * response
        idle_x = math.sin(self.elapsed * 0.47) * 0.65
        idle_y = math.sin(self.elapsed * 0.39 + 1.1) * 0.45
        self.head_offset = (
            round(self.parallax.x + idle_x),
            round(self.parallax.y + idle_y),
        )
        if self.view == "settings":
            self.settings.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.background, (0, 0))
        self.screen_layer.fill((0, 0, 0, 0))
        self._render_screen_base(self.screen_layer)
        if self.view == "main":
            self._render_main(self.screen_layer)
        elif self.view == "settings":
            self.settings.render(self.screen_layer)
        elif self.view == "tutorial":
            self._render_tutorial(self.screen_layer)
        else:
            self._render_credits(self.screen_layer)
        self._render_screen_finish(self.screen_layer)

        screen_content = self.screen_layer.subsurface(CRT_SCREEN_RECT).copy()
        screen_content.blit(self.screen_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(screen_content, CRT_SCREEN_RECT.topleft)

    def _update_hover(self, pointer: tuple[int, int] | None) -> None:
        if pointer is None:
            return
        if self.view == "main":
            for index, rect in enumerate(self.main_rects):
                if rect.collidepoint(pointer):
                    self.main_selection = index
                    return
        elif self.view == "tutorial":
            self.tutorial_hovered = None
            for action, rect in (
                ("back", TUTORIAL_BACK_RECT),
                ("previous", TUTORIAL_PREV_RECT),
                ("next", TUTORIAL_NEXT_RECT),
            ):
                if rect.collidepoint(pointer):
                    self.tutorial_hovered = action
                    return

    def _handle_click(self, pointer: tuple[int, int] | None) -> None:
        if pointer is None:
            return
        if self.view == "main":
            for index, rect in enumerate(self.main_rects):
                if rect.collidepoint(pointer):
                    self._activate_main_command(index)
                    return
        elif self.view == "tutorial":
            if TUTORIAL_BACK_RECT.collidepoint(pointer):
                self._play_click()
                self.view = "main"
            elif TUTORIAL_PREV_RECT.collidepoint(pointer):
                self._change_tutorial_page(-1)
            elif TUTORIAL_NEXT_RECT.collidepoint(pointer):
                if self.tutorial_page == len(TUTORIAL_PAGES) - 1:
                    self._play_click()
                    self.view = "main"
                else:
                    self._change_tutorial_page(1)
        elif self.credits_back_rect.collidepoint(pointer):
            self._play_click()
            self.view = "main"

    def _activate_main_command(self, index: int) -> None:
        self._play_click()
        if index == 0:
            self.manager.switch_to("audit")
        elif index == 1:
            self.tutorial_page = 0
            self.view = "tutorial"
        elif index == 2:
            self.settings.open(self.preferences)
            self.view = "settings"
        else:
            self.view = "credits"

    def _render_screen_base(self, surface: pygame.Surface) -> None:
        tint = pygame.Surface(CRT_SCREEN_RECT.size, pygame.SRCALPHA)
        tint.fill((0, 18, 12, 88))
        surface.blit(tint, CRT_SCREEN_RECT.topleft)
        surface.blit(self.screen_noise, CRT_SCREEN_RECT.topleft)

        if self.view != "settings":
            self._text(surface, "SISTEMA DE AUDITORIA // ESTAÇÃO 04", self.font_tiny, INK_MUTED, (455, 224))
            pulse = (math.sin(self.elapsed * 2.7) + 1.0) * 0.5
            led = (70 + round(pulse * 35), 130 + round(pulse * 35), 55)
            pygame.draw.circle(surface, led, (1365, 230), 5)
            self._text(surface, "ONLINE", self.font_tiny, GREEN, (1380, 220))
            pygame.draw.line(surface, LINE, (450, 254), (1470, 254), 2)

    def _render_main(self, surface: pygame.Surface) -> None:
        reveal = max(0.0, min(1.0, (self.elapsed - 0.16) / 0.7))
        self._text(surface, "CENTRAL DE REVISÃO", self.font_small, AMBER, (455, 310))
        title = self.font_title.render("SOB ANÁLISE", False, INK_BRIGHT)
        title.set_alpha(round(255 * reveal))
        surface.blit(title, (449, 342))
        pygame.draw.rect(surface, RED, (455, 431, round(500 * reveal), 6))

        self._text(surface, "TURNO DISPONÍVEL", self.font_tiny, INK_MUTED, (458, 478))
        self._text(surface, "06 DECISÕES PENDENTES", self.font_body_bold, INK, (455, 504))
        pygame.draw.line(surface, LINE, (995, 294), (995, 716), 2)

        self._text(surface, "OPERAÇÕES", self.font_tiny, INK_MUTED, (1035, 306))
        for index, (label, rect) in enumerate(zip(MAIN_COMMANDS, self.main_rects)):
            active = index == self.main_selection
            if active:
                pygame.draw.rect(surface, (25, 35, 26), rect)
                pygame.draw.rect(surface, AMBER, (rect.x, rect.y, 5, rect.height))
                pygame.draw.polygon(
                    surface,
                    INK_BRIGHT,
                    ((rect.right - 26, rect.centery - 8), (rect.right - 12, rect.centery), (rect.right - 26, rect.centery + 8)),
                )
            pygame.draw.line(surface, LINE, rect.bottomleft, rect.bottomright, 2)
            self._text(surface, f"0{index + 1}", self.font_tiny, AMBER if active else INK_MUTED, (rect.x + 20, rect.y + 22))
            self._text(surface, label, self.font_body_bold, INK_BRIGHT if active else INK, (rect.x + 67, rect.y + 16))

        trace = []
        for x in range(460, 955, 16):
            y = 691 + round(math.sin(x * 0.034 + self.elapsed * 1.7) * 9)
            trace.append((x, y))
        pygame.draw.lines(surface, (64, 102, 61), False, trace, 2)
        self._text(surface, "SNCT 2026 // VERSÃO 0.1", self.font_tiny, INK_MUTED, (455, 750))

    def _render_tutorial(self, surface: pygame.Surface) -> None:
        title, lead, instructions = TUTORIAL_PAGES[self.tutorial_page]
        self._text(surface, "TREINAMENTO DE AUDITORIA", self.font_tiny, AMBER, (455, 294))
        self._text(surface, title, self.font_section, INK_BRIGHT, (455, 330))
        self._text(surface, lead, self.font_small, INK, (458, 394))
        pygame.draw.line(surface, LINE, (455, 438), (965, 438), 2)

        y = 474
        for index, instruction in enumerate(instructions, start=1):
            pygame.draw.rect(surface, (18, 27, 20), pygame.Rect(457, y - 5, 40, 34))
            pygame.draw.rect(surface, LINE, pygame.Rect(457, y - 5, 40, 34), 2)
            self._text(surface, f"{index:02d}", self.font_tiny, AMBER, (477, y + 3), "center")
            self._draw_wrapped(surface, instruction, self.font_small, INK, pygame.Rect(515, y - 2, 440, 56))
            y += 86

        pygame.draw.line(surface, LINE, (995, 294), (995, 755), 2)
        self._render_tutorial_diagram(surface)

        page_text = f"{self.tutorial_page + 1:02d} / {len(TUTORIAL_PAGES):02d}"
        self._text(surface, page_text, self.font_tiny, INK_MUTED, (1100, 820), "center")
        self._draw_button(surface, TUTORIAL_BACK_RECT, "VOLTAR", self.tutorial_hovered == "back")
        self._draw_button(surface, TUTORIAL_PREV_RECT, "<", self.tutorial_hovered == "previous")
        next_label = "CONCLUIR" if self.tutorial_page == len(TUTORIAL_PAGES) - 1 else ">"
        self._draw_button(surface, TUTORIAL_NEXT_RECT, next_label, self.tutorial_hovered == "next")

    def _render_tutorial_diagram(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(1035, 326, 390, 388)
        pygame.draw.rect(surface, (7, 14, 10), panel)
        pygame.draw.rect(surface, LINE, panel, 2)

        if self.tutorial_page == 0:
            for index, (x, y, color) in enumerate(((1081, 397, AMBER), (1165, 366, GREEN), (1249, 420, RED))):
                paper = pygame.Rect(x, y, 138, 186)
                pygame.draw.rect(surface, (192, 184, 139), paper)
                pygame.draw.rect(surface, color, paper, 4)
                self._text(surface, f"DOC 0{index + 1}", self.font_tiny, (42, 46, 34), (paper.x + 14, paper.y + 18))
                for line_y in range(paper.y + 57, paper.bottom - 18, 24):
                    pygame.draw.line(surface, (91, 91, 68), (paper.x + 14, line_y), (paper.right - 14, line_y), 2)
        elif self.tutorial_page == 1:
            search = pygame.Rect(1072, 372, 316, 54)
            pygame.draw.rect(surface, (15, 24, 18), search)
            pygame.draw.rect(surface, AMBER, search, 2)
            self._text(surface, "LAB-48270_", self.font_small, INK_BRIGHT, (1090, 388))
            for index, label in enumerate(("ANA RIBEIRO // LAB-4827O", "ARTUR RIBEIRO // LAB-48270", "AMANDA RIBEIRO // LAB-4827Q")):
                result = pygame.Rect(1072, 454 + index * 66, 316, 52)
                pygame.draw.rect(surface, (25, 34, 25) if index == 1 else (10, 18, 13), result)
                pygame.draw.rect(surface, AMBER if index == 1 else LINE, (result.x, result.y, 4, result.height))
                self._text(surface, label, self.font_tiny, INK_BRIGHT if index == 1 else INK_MUTED, (result.x + 14, result.y + 17))
        elif self.tutorial_page == 2:
            labels = (("APROVAR", GREEN), ("NEGAR", RED), ("REVISÃO", AMBER), ("VIOLAÇÃO", (142, 78, 151)))
            for index, (label, color) in enumerate(labels):
                stamp = pygame.Rect(1068 + (index % 2) * 168, 376 + (index // 2) * 130, 150, 94)
                pygame.draw.rect(surface, (21, 25, 20), stamp)
                pygame.draw.rect(surface, color, stamp, 3)
                pygame.draw.circle(surface, color, (stamp.centerx, stamp.y + 29), 14, 3)
                self._text(surface, label, self.font_tiny, color, (stamp.centerx, stamp.y + 60), "center")
        else:
            page = pygame.Rect(1103, 356, 255, 320)
            pygame.draw.rect(surface, (211, 202, 157), page)
            pygame.draw.rect(surface, (91, 81, 57), page, 3)
            self._text(surface, "NOTICIÁRIO DO DIA", self.font_body_bold, (40, 42, 32), (page.centerx, page.y + 28), "center")
            pygame.draw.line(surface, (70, 63, 45), (page.x + 18, page.y + 67), (page.right - 18, page.y + 67), 3)
            self._draw_wrapped(surface, "AUDITORIA EVITA PREJUÍZO MILIONÁRIO", self.font_small, (54, 51, 36), pygame.Rect(page.x + 20, page.y + 88, page.width - 40, 74))
            pygame.draw.rect(surface, (95, 105, 77), pygame.Rect(page.x + 20, page.y + 176, page.width - 40, 88))
            for line_y in (page.y + 284, page.y + 302):
                pygame.draw.line(surface, (101, 94, 67), (page.x + 20, line_y), (page.right - 20, line_y), 2)

    def _change_tutorial_page(self, direction: int) -> None:
        next_page = max(0, min(len(TUTORIAL_PAGES) - 1, self.tutorial_page + direction))
        if next_page == self.tutorial_page:
            return
        self.tutorial_page = next_page
        self._play_click(0.55)

    def _render_credits(self, surface: pygame.Surface) -> None:
        self._text(surface, "CRÉDITOS", self.font_section, INK_BRIGHT, (500, 292))
        self._text(surface, "EQUIPE DE DESENVOLVIMENTO", self.font_tiny, AMBER, (502, 343))
        y = 392
        for index, name in enumerate(TEAM, start=1):
            self._text(surface, f"0{index}", self.font_tiny, AMBER, (520, y + 6))
            self._text(surface, name, self.font_body_bold, INK, (575, y))
            pygame.draw.line(surface, LINE, (500, y + 47), (1415, y + 47), 2)
            y += 78
        self._draw_button(surface, self.credits_back_rect, "VOLTAR", True)

    def _render_screen_finish(self, surface: pygame.Surface) -> None:
        surface.blit(self.scanlines, CRT_SCREEN_RECT.topleft)
        glass = pygame.Surface(CRT_SCREEN_RECT.size, pygame.SRCALPHA)
        pygame.draw.ellipse(glass, (172, 207, 175, 13), (-180, -300, 920, 510))
        surface.blit(glass, CRT_SCREEN_RECT.topleft)

        if self.elapsed < 0.82:
            progress = max(0.0, min(1.0, self.elapsed / 0.82))
            boot = pygame.Surface(CRT_SCREEN_RECT.size, pygame.SRCALPHA)
            boot.fill((0, 0, 0, round(255 * (1.0 - progress))))
            line_y = round(CRT_SCREEN_RECT.height / 2)
            pygame.draw.line(boot, (202, 226, 164, round(210 * (1.0 - progress))), (90, line_y), (CRT_SCREEN_RECT.width - 90, line_y), 3)
            surface.blit(boot, CRT_SCREEN_RECT.topleft)

    def _corrected_pointer(self, pointer: tuple[int, int] | None) -> tuple[int, int] | None:
        if pointer is None:
            return None
        scale = self.input_manager.viewport.scale
        if scale <= 0:
            return pointer
        offset_x = round(round(self.head_offset[0] * scale) / scale)
        offset_y = round(round(self.head_offset[1] * scale) / scale)
        return pointer[0] - offset_x, pointer[1] - offset_y

    def _draw_button(self, surface: pygame.Surface, rect: pygame.Rect, label: str, active: bool) -> None:
        pygame.draw.rect(surface, (25, 34, 25) if active else (8, 15, 11), rect)
        pygame.draw.rect(surface, AMBER if active else LINE, rect, 3 if active else 2)
        self._text(surface, label, self.font_body_bold, INK_BRIGHT if active else INK, rect.center, "center")

    @staticmethod
    def _build_screen_noise() -> pygame.Surface:
        overlay = pygame.Surface(CRT_SCREEN_RECT.size, pygame.SRCALPHA)
        rng = random.Random(904)
        for _ in range(2800):
            overlay.set_at(
                (rng.randrange(CRT_SCREEN_RECT.width), rng.randrange(CRT_SCREEN_RECT.height)),
                (156, 184, 132, rng.choice((10, 14, 18, 22))),
            )
        return overlay

    @staticmethod
    def _build_scanlines() -> pygame.Surface:
        overlay = pygame.Surface(CRT_SCREEN_RECT.size, pygame.SRCALPHA)
        for y in range(0, CRT_SCREEN_RECT.height, 4):
            pygame.draw.line(overlay, (0, 0, 0, 31), (0, y), (CRT_SCREEN_RECT.width, y))
        return overlay

    @staticmethod
    def _build_screen_mask() -> pygame.Surface:
        mask = pygame.Surface(CRT_SCREEN_RECT.size, pygame.SRCALPHA)
        # Measured against menu_crt_v1.png after its 1920x1080 upscale. The glass
        # is slightly barrel-shaped, so a rounded rectangle paints over the bezel.
        glass_points = (
            (65, 38),
            (128, 21),
            (404, 15),
            (748, 17),
            (1001, 30),
            (1058, 50),
            (1081, 90),
            (1087, 606),
            (1067, 652),
            (1022, 678),
            (806, 691),
            (519, 696),
            (232, 691),
            (94, 680),
            (54, 652),
            (34, 606),
            (29, 113),
            (40, 67),
        )
        pygame.draw.polygon(
            mask,
            (255, 255, 255, 255),
            glass_points,
        )
        return mask

    def _play_click(self, volume: float = 0.8) -> None:
        if self.audio is not None:
            self.audio.play("click", volume)

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
        y = rect.y
        for word in words:
            candidate = f"{line} {word}".strip()
            if not line or font.size(candidate)[0] <= rect.width:
                line = candidate
                continue
            cls._text(surface, line, font, color, (rect.x, y))
            y += font.get_linesize()
            line = word
        if line and y < rect.bottom:
            cls._text(surface, line, font, color, (rect.x, y))
