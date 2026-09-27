from __future__ import annotations

import math
import random
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING
import unicodedata

import pygame

from src.core.preferences import UserPreferences
from src.core.scene import Scene
from src.core.settings import DEBUG_LAYOUT_RECTS, DEBUG_UI
from src.gameplay.cases import CASES, SHIFT_SIZE, TUTORIAL_CASE, CaseResult, pick_shift
from src.gameplay.comparison_links import Link, find_link
from src.gameplay.protocols import PROTOCOLS
from src.gameplay.document_renderer import DocumentRenderer, EvidenceRegion
from src.gameplay import document_art
from src.ui.ai_decision_panel import (
    CLOSE_RECT as AI_REPORT_CLOSE_RECT,
    OPEN_BUTTON_RECT as AI_REPORT_OPEN_RECT,
    AIDecisionPanel,
)
from src.ui.calculator_popup import CalculatorPopup
from src.ui.case_dialog import (
    BRIEFING_START_RECT,
    CONFIRM_YES_RECT,
    CaseDialog,
    STAMP_LABELS,
)
from src.ui.case_document import PREVIEW_SIZE, CaseDocument
from src.ui.case_hint import CaseHint
from src.ui.comparison_card import ComparisonCard
from src.ui.side_by_side import SideBySide
from src.minigames.captchas import create_captcha
from src.minigames.common import load_named_images
from src.minigames.director import (
    SKIP_PENALTY,
    TIME_BONUS_SECONDS,
    WRONG_ANSWER_PENALTY,
    ComplicationDirector,
    case_time_limit,
)
from src.minigames.popups import PopupSwarm
from src.minigames.story import (
    CAPTCHA_QUOTES,
    FAILED_QUOTES,
    POPUP_QUOTES,
    SKIPPED_QUOTE,
    SOLVED_QUOTES,
    TIMEOUT_QUOTE,
)
from src.minigames.verify9 import Verify9
from src.ui.captcha_overlay import CaptchaOverlay
from src.ui.conclusion_panel import ConclusionPanel
from src.ui.game_setup import GameSetup
from src.ui.story_intro import StoryIntro
from src.ui.toast import Toast
from src.ui.credential_note import CredentialNote
from src.ui.database_search import DatabaseSearch
from src.ui.document_inspector import DocumentInspector
from src.ui.item_inspector import ItemInspector
from src.ui.newspaper import HERO_IMAGE_RECT, FinalNewspaper
from src.ui.os_cursor import OSCursor
from src.ui.pause_menu import PauseMenu
from src.ui.protocol_panel import ProtocolPanel
from src.ui.signature_pad import (
    CONFIRM_RECT as SIGNATURE_CONFIRM_RECT,
    DRAW_RECT as SIGNATURE_DRAW_RECT,
    SignaturePad,
)
from src.ui.stamp_button import StampButton

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.audio import AudioManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager


SCREEN_BASE_COLOR = (4, 7, 6)
MONITOR_BASE_COLOR = (4, 12, 10)
WORKSPACE_SCREEN_COLOR = (6, 18, 15)
COMPARE_PENDING = (237, 193, 91)
COMPARE_EQUAL = (101, 191, 91)
COMPARE_DIFFERENT = (224, 82, 67)
COMPARE_RELATED = (222, 186, 82)
COMPARE_NONE = (150, 156, 140)
LINK_COLORS = {
    "equal": COMPARE_EQUAL,
    "different": COMPARE_DIFFERENT,
    "related": COMPARE_RELATED,
    "none": COMPARE_NONE,
}

MONITOR_SCREEN_RECT = pygame.Rect(186, 87, 1554, 696)
DOCUMENT_WORKSPACE = pygame.Rect(294, 63, 867, 630)
# The visible screen is a window into a larger desk. Right-dragging explores it.
DESK_CONTENT_BOUNDS = DOCUMENT_WORKSPACE.inflate(1200, 900)
PROTOCOL_RECT = pygame.Rect(0, 0, 273, 696)
AI_DECISION_RECT = pygame.Rect(1188, 3, 366, 324)
AI_DATA_RECT = pygame.Rect(1188, 345, 366, 219)
STAMP_BASE_AREA = pygame.Rect(432, 807, 1035, 162)
STATUS_LED_CENTER = (1388, 1013)

DEBUG_TEXT_POSITION = (500, 786)
STAMP_STATUS_POSITION = (960, 786)

DESK_ZOOM_OUT_RECT = pygame.Rect(1008, 72, 38, 34)
DESK_ZOOM_LABEL_RECT = pygame.Rect(1052, 72, 56, 34)
DESK_ZOOM_IN_RECT = pygame.Rect(1114, 72, 37, 34)
CASE_PROGRESS_RECT = pygame.Rect(304, 72, 112, 34)
CASE_STORY_RECT = pygame.Rect(424, 72, 138, 34)
CLOCK_RECT = pygame.Rect(1024, 118, 124, 56)
POPUP_AREA = pygame.Rect(310, 190, 840, 470)
CASE_GUIDANCE_RECT = pygame.Rect(304, 114, 847, 64)
CASE_SUBMIT_RECT = pygame.Rect(786, 579, 370, 51)
CALCULATOR_BUTTON_RECT = pygame.Rect(570, 72, 165, 34)
COMPARE_BUTTON_RECT = pygame.Rect(743, 72, 140, 34)
DESK_ZOOM_LEVELS = (0.65, 0.75, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8)
NEWS_SHUTDOWN_DURATION = 2.15
NEWS_REVEAL_DURATION = 0.7
HEAD_SWAY_X = 2
HEAD_SWAY_Y = 1

STAMP_LAYOUT = (
    ("approve", "stamps/approve.png", (616, 888)),
    ("deny", "stamps/deny.png", (848, 888)),
    ("review", "stamps/review.png", (1079, 888)),
    ("violation", "stamps/violation.png", (1309, 888)),
)

FINAL_SHEET_POSITION = (564, 207)
DOCUMENT_ROW_TOP = 190
ZOOM_BY_DOCUMENT_COUNT = {2: 1.0, 3: 0.9, 4: 0.65}


@dataclass(frozen=True)
class EvidenceSelection:
    document_id: str
    key: str
    value: str
    note: str


class AuditScene(Scene):
    """Playable desk for a full turn of algorithmic decision audits."""

    @property
    def camera_motion_enabled(self) -> bool:
        return False

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
        self.tutorial_active = True
        self.seen_case_ids: set[str] = set()
        self.shift_cases = pick_shift(self.seen_case_ids)
        self.completed_pairs: set[frozenset[str]] = set()
        self.read_document_ids: set[str] = set()
        self.document_flash: tuple[str | None, float] = (None, 0.0)
        self.final_parked = True
        self.case_index = -1
        self.case_results: list[CaseResult] = []
        self.case = TUTORIAL_CASE
        self.desk_zoom = 1.0
        self.desk_panning = False
        self.last_desk_pan_position: tuple[int, int] | None = None
        self.head_motion_time = 0.0
        self.head_offset = (0, 0)
        self.hovered_desk_control: str | None = None
        self.calculator_hovered = False
        self.compare_hovered = False
        self.side_view = SideBySide()
        self.story_hovered = False
        self.submit_hovered = False
        self.terminal_overlay = self.assets.load_image("backgrounds/novo_sprite_teste.png")
        self.monitor_surface = pygame.Surface(MONITOR_SCREEN_RECT.size, pygame.SRCALPHA)
        self.popup_surface = pygame.Surface(MONITOR_SCREEN_RECT.size, pygame.SRCALPHA)
        self.monitor_glass = self._build_monitor_glass()
        self.small_font = pygame.font.SysFont(("Consolas", "Courier New", "monospace"), 19)
        self.guide_font = pygame.font.SysFont(("Consolas", "Courier New", "monospace"), 16)
        self.status_font = pygame.font.SysFont(
            ("Consolas", "Courier New", "monospace"),
            20,
            bold=True,
        )
        self.transition_title_font = pygame.font.SysFont(
            ("Consolas", "Courier New", "monospace"),
            54,
            bold=True,
        )
        self.transition_body_font = pygame.font.SysFont(
            ("Consolas", "Courier New", "monospace"),
            22,
            bold=True,
        )

        self.document_renderer = DocumentRenderer()
        self.stamp_marks = self._load_stamp_marks()
        self.documents = self._create_documents()
        self._apply_case_layout()
        self.stamp_buttons = self._create_stamp_buttons()
        self.protocol_panel = ProtocolPanel(self._load_protocol_portraits(), self._play_sound)
        self.ai_decision_panel = AIDecisionPanel(self.case)
        self.document_inspector = DocumentInspector(self.case.evidence_summary)
        self.case_dialog = CaseDialog(self.case)
        self.case_hint = CaseHint(self.case)
        self.credential_note = CredentialNote(
            self.assets.load_image("ui/heart_note.png")
        )
        self.item_inspector = ItemInspector(
            self.assets.assets_root / "models" / "heart_note.glb",
            "Post-it de acesso",
        )
        self.os_cursor = OSCursor(
            self.assets.load_image("os/cursor.png"),
            MONITOR_SCREEN_RECT,
        )
        self.database_search = DatabaseSearch(self.case, audio)
        self.signature_pad = SignaturePad()
        self.newspaper = FinalNewspaper(self._load_newspaper_images())
        self.pause_menu = PauseMenu(
            audio,
            self.preferences_provider,
            apply_preferences,
        )

        self.evidence_notes: dict[str, str] = {}
        self.comparison_anchor: EvidenceSelection | None = None
        self.comparison_result: tuple[EvidenceSelection, EvidenceSelection, Link] | None = None
        self.hovered_evidence: EvidenceSelection | None = None
        self.active_document: CaseDocument | None = None
        self.selected_stamp_id: str | None = None
        self.case_completed = False
        self.ai_report_seen = False
        self.inspected_document_ids: set[str] = set()
        self.newspaper_transition: str | None = None
        self.newspaper_transition_time = 0.0
        self.calculator = CalculatorPopup()
        self.verify9 = Verify9(self.assets.assets_root)
        self.story_intro = StoryIntro(self.verify9)
        self.captcha_overlay = CaptchaOverlay(self.verify9)
        self.toast = Toast(self.verify9)
        popup_icons = load_named_images(self.assets.assets_root, "captcha/ads", "ad_")
        for name, image in load_named_images(self.assets.assets_root, "captcha/nelson").items():
            popup_icons[name] = image
        popup_icons["verify9"] = popup_icons.get("verify9") or self.verify9.images.get("suspicious")
        self.popups = PopupSwarm(
            POPUP_AREA,
            icons={k: v for k, v in popup_icons.items() if v is not None},
            limits=pygame.Rect(0, 0, *MONITOR_SCREEN_RECT.size),
        )
        self.director = ComplicationDirector()
        self.clock_enabled = False
        self.clock_limit = 0.0
        self.clock_left = 0.0
        self.clock_elapsed = 0.0
        self.clock_plan: list = []
        self.clock_plan_index = 0
        self.captchas_solved = 0
        self.captchas_shown = 0
        self.time_flash: tuple[str, float] = ("", 0.0)
        self.timeout_time = 0.0
        self.setup = GameSetup()
        self.needs_setup = True
        self.conclusion_panel = ConclusionPanel()
        self.conclusion_done = False
        self.conclusion_answers = (0, 0)
        self.comparison_card = ComparisonCard()

    def on_enter(self) -> None:
        self.pause_menu.close()
        self.credential_note.clear_hover()
        self.item_inspector.close()
        self.head_offset = (0, 0)
        if self.needs_setup:
            self.setup.open()
        if self.audio is not None:
            self.audio.play_music_sequence(("audit_1", "audit_2"), fade_ms=700)

    def on_exit(self) -> None:
        self.calculator.close()
        self.pause_menu.close()
        self.credential_note.clear_hover()
        self.item_inspector.close()
        self.database_search.close()
        self.signature_pad.close()

    def custom_cursor_active(self, position: tuple[int, int] | None) -> bool:
        return self.os_cursor.is_active(
            position,
            blocked=self.item_inspector.is_open,
        )

    def handle_escape(self) -> bool:
        if self.captcha_overlay.is_open or self.timeout_time > 0:
            return True  # no escaping from the human test
        if self.story_intro.is_open:
            self.story_intro.advance()
            return True
        if self.setup.is_open:
            self._leave_to_menu()
            return True
        if self.conclusion_panel.is_open:
            self.conclusion_panel.close()
            self._play_sound("back", 0.65)
            return True
        if self.pause_menu.is_open:
            return self.pause_menu.handle_escape()
        if self.newspaper_transition is not None:
            return True
        if self.newspaper.is_open:
            return True
        if self.item_inspector.is_open:
            self.item_inspector.close()
            self._play_sound("back", 0.65)
            return True
        if self.signature_pad.is_open:
            self.signature_pad.close()
            self._play_sound("back", 0.65)
            return True
        if self.database_search.is_open:
            self.database_search.close()
            self._play_sound("back", 0.65)
            return True
        if self.case_hint.is_open:
            self.case_hint.close()
            self._play_sound("back", 0.65)
            return True
        if self.case_dialog.is_open:
            handled = self.case_dialog.handle_escape()
            if handled:
                self._play_sound("back", 0.65)
            return handled
        if self.protocol_panel.is_popup_open:
            self.protocol_panel.close_popup()
            self._play_sound("back", 0.65)
            return True
        if self.side_view.is_open:
            self.side_view.close()
            self._play_sound("back", 0.65)
            return True
        if self.document_inspector.is_open:
            self.document_inspector.close()
            self._play_sound("back", 0.65)
            return True
        if self.ai_decision_panel.popup_open:
            self.ai_decision_panel.close()
            self._play_sound("back", 0.65)
            return True
        if self.calculator.is_open:
            self.calculator.close()
            self._play_sound("back", 0.65)
            return True
        self._stop_desk_pan()
        self.head_offset = (0, 0)
        self.pause_menu.open()
        return True

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.story_intro.is_open and not self.setup.is_open:
            if event.type == pygame.KEYDOWN:
                if self.story_intro.handle_key(event):
                    self._play_sound("forward", 0.6)
                return
            if event.type != pygame.MOUSEBUTTONDOWN:
                return
        if self.captcha_overlay.is_open:
            monitor = self.scene_to_monitor(self.input_manager.mouse_position)
            if event.type == pygame.MOUSEMOTION:
                self.captcha_overlay.handle_mouse_move(monitor)
                return
            if event.type == pygame.MOUSEBUTTONUP and monitor is not None:
                self.captcha_overlay.handle_mouse_up(monitor)
                return
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self.captcha_overlay.handle_key(event)
                return
            if event.type != pygame.MOUSEBUTTONDOWN:
                return
        if self.timeout_time > 0:
            return
        if self.setup.is_open:
            if event.type == pygame.KEYDOWN:
                action = self.setup.handle_key(event)
                if action == "start":
                    self._start_from_setup()
                elif action == "select":
                    self._play_sound("click", 0.5)
                return
            if event.type != pygame.MOUSEBUTTONDOWN:
                return
        if self.pause_menu.is_open:
            action = self.pause_menu.handle_event(event, self.input_manager.mouse_position)
            if action == "menu":
                self._leave_to_menu()
            elif action == "help":
                self.case_dialog.reopen()
            return
        if self.newspaper_transition is not None:
            return
        if self.item_inspector.is_open:
            action = self.item_inspector.handle_event(
                event,
                self.input_manager.mouse_position,
            )
            if action == "close":
                self._play_sound("back", 0.65)
            elif action == "zoom":
                self._play_sound("scroll", 0.45)
            return
        if self.signature_pad.is_open:
            result = self.signature_pad.handle_event(
                event,
                self.scene_to_monitor(self.input_manager.mouse_position),
            )
            if result is not None and result[0] == "confirm" and result[1] is not None:
                self._get_document("final").sign(result[1])
                self._play_sound("confirm")
            elif result is not None and result[0] == "clear":
                self._play_sound("paper", 0.55)
            elif result is not None and result[0] == "cancel":
                self._play_sound("back", 0.7)
            return
        if self.database_search.is_open:
            self.database_search.handle_event(
                event,
                self.scene_to_monitor(self.input_manager.mouse_position),
            )
            return
        if event.type == pygame.MOUSEWHEEL and self.document_inspector.is_open:
            self.document_inspector.handle_wheel(
                event.y,
                self.scene_to_monitor(self.input_manager.mouse_position),
            )
            self._play_sound("scroll", 0.7)
            return

        if event.type == pygame.MOUSEWHEEL and not self._is_modal_open():
            monitor_position = self.scene_to_monitor(self.input_manager.mouse_position)
            if self.ai_decision_panel.handle_wheel(event.y, monitor_position):
                self._play_sound("scroll", 0.7)
                return
            if monitor_position is not None and DOCUMENT_WORKSPACE.collidepoint(monitor_position):
                self._change_desk_zoom(1 if event.y > 0 else -1)
                self._play_sound("scroll", 0.7)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self._start_desk_pan()
            return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self._stop_desk_pan()
            return

        if event.type == pygame.KEYDOWN:
            if self.newspaper.is_open:
                previous_page = self.newspaper.page_index
                if self.newspaper.handle_key_down(event.key):
                    if self.newspaper.page_index < previous_page:
                        self._play_sound("back", 0.65)
                    elif self.newspaper.page_index > previous_page:
                        self._play_sound("forward", 0.65)
                return
            if (
                event.key == pygame.K_f
                and getattr(event, "mod", 0) & pygame.KMOD_CTRL
                and not self._is_modal_open()
            ):
                if self.database_search.open():
                    self._play_sound("forward", 0.7)
                return
            if not self._is_modal_open():
                if self.calculator.handle_key(event):
                    return
                self.protocol_panel.handle_key_down(event.key)
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_down(getattr(event, "clicks", 1))
            return

        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion()
            return

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._handle_mouse_up()

    def update(self, dt: float) -> None:
        self.toast.update(dt)
        self.story_intro.update(dt)
        self._update_captcha_overlay(dt)
        self._update_timeout(dt)
        if self.pause_menu.is_open:
            self.head_offset = (0, 0)
            self.pause_menu.update(dt)
            return
        if self.newspaper_transition is not None:
            self._update_newspaper_transition(dt)
            return
        if self.item_inspector.is_open:
            self.head_offset = (0, 0)
            self.item_inspector.update_hover(self.input_manager.mouse_position)
            return
        self.head_motion_time += dt
        self._update_clock(dt)
        self.popups.update(dt)
        self.protocol_panel.update(dt)
        flash_id, flash_left = self.document_flash
        if flash_id is not None:
            self.document_flash = (flash_id if flash_left > dt else None, max(0.0, flash_left - dt))
        self.head_offset = (
            round(math.sin(self.head_motion_time * 0.72) * HEAD_SWAY_X),
            round(math.sin(self.head_motion_time * 0.51 + 1.1) * HEAD_SWAY_Y),
        )
        scene_position = self.input_manager.mouse_position
        self.credential_note.update_note_hover(
            self._corrected_scene_position(scene_position),
            enabled=not self._is_modal_open(),
        )
        monitor_position = self.scene_to_monitor(scene_position)

        self.protocol_panel.update_hover(monitor_position)
        self.ai_decision_panel.update_hover(monitor_position)
        self.case_dialog.update_hover(monitor_position)
        self.case_hint.update_hover(monitor_position)
        self.database_search.update_hover(monitor_position)
        self.newspaper.update_hover(monitor_position)
        self.setup.update_hover(monitor_position)
        self.story_intro.update_hover(monitor_position)
        self.conclusion_panel.update_hover(monitor_position)
        self.calculator.update_hover(monitor_position)
        self.comparison_card.update_hover(monitor_position)
        self._update_desk_controls_hover(monitor_position)
        self.story_hovered = bool(
            not self._is_modal_open()
            and monitor_position is not None
            and CASE_STORY_RECT.collidepoint(monitor_position)
        )
        self.calculator_hovered = bool(
            not self._is_modal_open()
            and monitor_position is not None
            and CALCULATOR_BUTTON_RECT.collidepoint(monitor_position)
        )
        self.compare_hovered = bool(
            not self._is_modal_open()
            and monitor_position is not None
            and COMPARE_BUTTON_RECT.collidepoint(monitor_position)
        )
        self.side_view.update_hover(monitor_position)
        self.submit_hovered = bool(
            self.case_completed
            and self._get_document("final").is_signed
            and not self._is_modal_open()
            and monitor_position is not None
            and CASE_SUBMIT_RECT.collidepoint(monitor_position)
        )
        if self.document_inspector.is_open:
            self.document_inspector.handle_mouse_motion(monitor_position)

        self._update_stamp_hover(None if self._is_modal_open() else scene_position)
        target_active = (
            self.selected_stamp_id is not None
            and not self.case_completed
            and not self._is_modal_open()
        )
        for document in self.documents:
            document.set_stamp_target_active(
                target_active and document.document_id == "final"
            )
            document.set_signature_target_active(
                self.case_completed
                and not self._get_document("final").is_signed
                and not self._is_modal_open()
                and document.document_id == "final"
            )

    def render(self, surface: pygame.Surface) -> None:
        self._render_scene(surface, draw_cursor=True)

    def _leave_to_menu(self) -> None:
        """Abandon the shift so the next player always starts from the tutorial."""
        self._restart_turn()
        # the next person at the computer starts from the defaults: 5 cases, with training
        self.setup.count = SHIFT_SIZE
        self.setup.with_tutorial = True
        self.setup.with_clock = True
        self.manager.switch_to("main_menu")

    def _render_scene(self, surface: pygame.Surface, draw_cursor: bool) -> None:
        surface.fill(SCREEN_BASE_COLOR)
        self._render_monitor_content(surface)
        surface.blit(self.terminal_overlay, (0, 0))
        self.credential_note.render_note_highlight(surface)
        self._render_status_led(surface)
        if DEBUG_UI and DEBUG_LAYOUT_RECTS:
            self._draw_layout_rects(surface)
        self._render_active_popup(surface)
        self._render_newspaper_transition(surface)
        self._render_timeout_banner(surface)
        self._render_stamp_buttons(surface)
        self._render_tutorial_focus(surface)
        self._draw_stamp_status(surface)
        if DEBUG_UI:
            self._draw_debug_text(surface)
        self.item_inspector.render(surface)
        if self.pause_menu.is_open:
            self.pause_menu.render(surface)
        if draw_cursor:
            self.os_cursor.render(
                surface,
                self.input_manager.mouse_position,
                blocked=self.item_inspector.is_open,
            )

    def _render_status_led(self, surface: pygame.Surface) -> None:
        pulse = (math.sin(self.head_motion_time * 2.4) + 1.0) * 0.5
        glow = pygame.Surface((52, 52), pygame.SRCALPHA)
        center = (26, 26)
        for radius, alpha in ((20, 8), (15, 14), (11, 25)):
            pygame.draw.circle(glow, (104, 221, 57, round(alpha + pulse * alpha)), center, radius)
        surface.blit(glow, (STATUS_LED_CENTER[0] - 26, STATUS_LED_CENTER[1] - 26))

        core = (105 + round(pulse * 55), 185 + round(pulse * 45), 42 + round(pulse * 20))
        pygame.draw.rect(surface, core, pygame.Rect(1383, 1008, 10, 10))
        pygame.draw.rect(surface, (207, 247, 126), pygame.Rect(1385, 1010, 4, 3))

    def scene_to_monitor(self, position: tuple[int, int] | None) -> tuple[int, int] | None:
        if position is None or not MONITOR_SCREEN_RECT.collidepoint(position):
            return None
        head_offset = self._effective_head_offset()
        return (
            position[0] - MONITOR_SCREEN_RECT.x - head_offset[0],
            position[1] - MONITOR_SCREEN_RECT.y - head_offset[1],
        )

    def _corrected_scene_position(
        self,
        position: tuple[int, int] | None,
    ) -> tuple[int, int] | None:
        if position is None:
            return None
        head_offset = self._effective_head_offset()
        return position[0] - head_offset[0], position[1] - head_offset[1]

    def _effective_head_offset(self) -> tuple[int, int]:
        """Match input coordinates to the integer shift used after scaling."""
        scale = self.input_manager.viewport.scale
        if scale <= 0:
            return self.head_offset
        return tuple(
            round(round(value * scale) / scale)
            for value in self.head_offset
        )

    def _create_documents(self) -> list[CaseDocument]:
        portrait = (
            self.assets.load_image(self.case.portrait_asset)
            if self.case.portrait_asset is not None
            else None
        )
        rendered_documents = self.document_renderer.render_case(self.case, portrait, self.assets.load_image)
        documents = [
            CaseDocument(rendered, FINAL_SHEET_POSITION)
            for rendered in rendered_documents
        ]
        number = 0
        for document in documents:
            document.set_visible(True)
            if document.document_id != "final":
                number += 1
                document.order_number = number
        final = next(d for d in documents if d.document_id == "final")
        final.set_visible(False)  # the audit sheet is opened from the side panel
        documents.remove(final)
        return [final, *documents]  # the audit sheet sits under the papers

    def _apply_case_layout(self) -> None:
        """Put the case documents side by side so their data can be compared at a glance."""
        sources = [document for document in self.documents if document.document_id != "final"]
        zoom = ZOOM_BY_DOCUMENT_COUNT.get(len(sources), 0.75)
        self.desk_zoom = zoom
        size = (round(PREVIEW_SIZE[0] * zoom), round(PREVIEW_SIZE[1] * zoom))
        count = max(1, len(sources))
        spare = DOCUMENT_WORKSPACE.width - 24 - count * size[0]
        gap = min(30, spare // (count - 1)) if count > 1 else 0
        total = count * size[0] + (count - 1) * gap
        x = DOCUMENT_WORKSPACE.x + (DOCUMENT_WORKSPACE.width - total) // 2
        for document in sources:
            document.rect = pygame.Rect((x, DOCUMENT_ROW_TOP), size)
            document.position = document.rect.topleft
            x += size[0] + gap
        final = self._get_document("final")
        final.rect = pygame.Rect(
            (DOCUMENT_WORKSPACE.centerx - size[0] // 2, DOCUMENT_ROW_TOP + size[1] + 16),
            size,
        )
        final.position = final.rect.topleft
        self.final_parked = True
        self.read_document_ids = set()
        self.document_flash = (None, 0.0)

    def _present_final_sheet(self) -> None:
        """Bring the audit sheet from its parking spot to the middle of the desk."""
        final = self._get_document("final")
        final.rect.topleft = (
            DOCUMENT_WORKSPACE.centerx - final.rect.width // 2,
            DOCUMENT_ROW_TOP + 8,
        )
        final.position = final.rect.topleft
        final.set_visible(True)
        self.final_parked = False
        self.read_document_ids.add("final")
        self._bring_document_to_front(final)

    def _focus_on_document(self, document_id: str) -> None:
        """Panel row clicked: show that paper on top and flash it so it is easy to find."""
        if document_id == "final":
            self._present_final_sheet()
        document = self._get_document(document_id)
        self._bring_document_to_front(document)
        self.read_document_ids.add(document_id)
        self.document_flash = (document_id, 0.9)

    def _play_sound(self, name: str, volume: float = 1.0) -> None:
        if self.audio is not None:
            self.audio.play(name, volume)

    def _create_stamp_buttons(self) -> list[StampButton]:
        return [
            StampButton(stamp_id, self.assets.load_image(asset_path), center)
            for stamp_id, asset_path, center in STAMP_LAYOUT
        ]

    def _start_desk_pan(self) -> None:
        if self._is_modal_open():
            return
        scene_position = self.input_manager.mouse_position
        monitor_position = self.scene_to_monitor(scene_position)
        if monitor_position is None or not DOCUMENT_WORKSPACE.collidepoint(monitor_position):
            return
        self.desk_panning = True
        self.last_desk_pan_position = (
            scene_position[0] - MONITOR_SCREEN_RECT.x,
            scene_position[1] - MONITOR_SCREEN_RECT.y,
        )

    def _stop_desk_pan(self) -> None:
        self.desk_panning = False
        self.last_desk_pan_position = None

    def _pan_documents(self, delta: tuple[int, int]) -> None:
        if not delta or not self.documents:
            return

        visible_documents = [document for document in self.documents if document.visible]
        if not visible_documents:
            return
        left = min(document.rect.left for document in visible_documents)
        top = min(document.rect.top for document in visible_documents)
        right = max(document.rect.right for document in visible_documents)
        bottom = max(document.rect.bottom for document in visible_documents)
        document_bounds = pygame.Rect(left, top, right - left, bottom - top)
        proposed = document_bounds.move(delta)
        adjusted_x, adjusted_y = delta

        # The pile of papers may go anywhere as long as a good part of it stays over the workspace.
        # (Keeping it fully inside a box got stuck once zoomed papers were wider than the box.)
        keep_x, keep_y = 220, 160
        if proposed.right < DOCUMENT_WORKSPACE.left + keep_x:
            adjusted_x += DOCUMENT_WORKSPACE.left + keep_x - proposed.right
        elif proposed.left > DOCUMENT_WORKSPACE.right - keep_x:
            adjusted_x -= proposed.left - (DOCUMENT_WORKSPACE.right - keep_x)

        if proposed.bottom < DOCUMENT_WORKSPACE.top + keep_y:
            adjusted_y += DOCUMENT_WORKSPACE.top + keep_y - proposed.bottom
        elif proposed.top > DOCUMENT_WORKSPACE.bottom - keep_y:
            adjusted_y -= proposed.top - (DOCUMENT_WORKSPACE.bottom - keep_y)

        if not adjusted_x and not adjusted_y:
            return
        for document in visible_documents:
            document.rect.move_ip(adjusted_x, adjusted_y)
            document.position = document.rect.topleft

    def _load_stamp_marks(self) -> dict[str, pygame.Surface]:
        return {
            stamp_id: self.assets.load_image(f"stamp_marks/{stamp_id}.png")
            for stamp_id in ("approve", "deny", "review", "violation")
        }

    def _load_protocol_portraits(self) -> dict[str, pygame.Surface]:
        portrait_slugs = (
            "grace_hopper",
            "katherine_johnson",
            "ada_lovelace",
            "radia_perlman",
            "fei_fei_li",
            "margaret_hamilton",
        )
        return {
            slug: self.assets.load_image(f"protocols/{slug}.png")
            for slug in portrait_slugs
        }

    def _load_newspaper_images(self) -> dict[str, pygame.Surface]:
        image_paths = {
            article.image_asset
            for case in CASES
            for article in (case.newspaper_correct, case.newspaper_incorrect)
        }
        images: dict[str, pygame.Surface] = {}
        for path in image_paths:
            try:
                images[path] = self.assets.load_image(path)
            except (FileNotFoundError, pygame.error):
                # The case has its own picture on order (see prompts_jornal.md); until it
                # arrives, a placeholder keeps the newspaper working instead of crashing.
                images[path] = document_art.draw_newsroom_placeholder(HERO_IMAGE_RECT.size, path)
        return images

    def _handle_mouse_down(self, click_count: int) -> None:
        scene_position = self.input_manager.mouse_position
        if scene_position is None:
            return
        monitor_position = self.scene_to_monitor(scene_position)
        if not self._tutorial_click_allowed(scene_position):
            self._play_sound("error", 0.35)
            return

        if self.story_intro.is_open and not self.setup.is_open:
            if monitor_position is not None and self.story_intro.handle_mouse_down(monitor_position):
                self._play_sound("forward", 0.6)
            return
        if self.timeout_time > 0:
            return
        if self.captcha_overlay.is_open:
            if monitor_position is not None:
                self.captcha_overlay.handle_mouse_down(monitor_position)
            return

        if self.setup.is_open:
            action = self.setup.handle_mouse_down(monitor_position) if monitor_position is not None else None
            if action == "start":
                self._start_from_setup()
            elif action == "select":
                self._play_sound("click", 0.5)
            return

        if self.conclusion_panel.is_open:
            action = self.conclusion_panel.handle_mouse_down(monitor_position) if monitor_position is not None else None
            if action == "toggle":
                self._play_sound("toggle", 0.6)
            elif action == "confirm":
                self.conclusion_answers = self.conclusion_panel.score()
                self.conclusion_done = True
                self.conclusion_panel.close()
                self._play_sound("forward", 0.7)
                if self.selected_stamp_id is not None:
                    self.case_dialog.request_confirmation(self.selected_stamp_id)
            return

        if self.newspaper.is_open:
            if monitor_position is not None:
                previous_page = self.newspaper.page_index
                action = self.newspaper.handle_mouse_down(monitor_position)
                if action == "restart":
                    self._play_sound("forward", 0.7)
                    self._restart_turn()
                elif action == "previous" and self.newspaper.page_index < previous_page:
                    self._play_sound("back", 0.65)
                elif action == "next" and self.newspaper.page_index > previous_page:
                    self._play_sound("forward", 0.65)
                elif action == "menu":
                    self._play_sound("back", 0.65)
                    self._leave_to_menu()
                elif action == "explain":
                    self._play_sound("paper", 0.6)
            return

        if self.case_hint.is_open:
            if monitor_position is not None:
                action = self.case_hint.handle_mouse_down(monitor_position)
                if action == "open_protocol":
                    self._play_sound("forward", 0.65)
                    self.protocol_panel.open_protocol(self.case.protocol_focus)
                elif action == "close":
                    self._play_sound("back", 0.65)
            return

        if self.case_dialog.is_open:
            if monitor_position is not None:
                action = self.case_dialog.handle_mouse_down(monitor_position)
                if action == "start":
                    self._play_sound("forward", 0.7)
                elif action == "cancel":
                    self._play_sound("back", 0.7)
                self._handle_case_dialog_action(action)
            return

        if self.protocol_panel.is_popup_open:
            if monitor_position is not None:
                if self.protocol_panel.handle_mouse_down(monitor_position):
                    self._play_sound("click")
            return

        if self.side_view.is_open:
            if monitor_position is not None:
                self._handle_side_view_click(monitor_position)
            return

        if self.document_inspector.is_open:
            if monitor_position is not None:
                handled = self.document_inspector.handle_mouse_down(
                    monitor_position,
                    self.evidence_notes,
                )
                if handled:
                    self._play_sound("paper", 0.7)
            return

        if self.ai_decision_panel.popup_open:
            if monitor_position is not None:
                if self.ai_decision_panel.handle_popup_mouse_down(
                    monitor_position,
                    self.evidence_notes,
                ):
                    self._play_sound("click")
            return

        if monitor_position is not None:
            popup_result = self.popups.handle_mouse_down(monitor_position)
            if popup_result == "close":
                self._play_sound("click", 0.6)
                return
            if popup_result == "decoy":
                self._play_sound("error", 0.6)
                self.toast.show("Ops. Aquele botão era mentira. Agora são mais!", "happy")
                return
            if popup_result == "consume":
                return

        calculator_sound = (
            self.calculator.handle_mouse_down(monitor_position)
            if monitor_position is not None
            else None
        )
        if calculator_sound is not None:
            if calculator_sound != "consume":
                self._play_sound(calculator_sound, 0.5)
            return

        if (
            self.comparison_result is not None
            and monitor_position is not None
            and self.comparison_card.contains(monitor_position)
        ):
            if self.comparison_card.is_close_hit(monitor_position):
                self.comparison_result = None
                self._play_sound("back", 0.5)
            elif (
                self.comparison_card.is_protocol_hit(monitor_position)
                and self.comparison_result[2].kind != "none"
            ):
                self.protocol_panel.open_protocol(self.case.protocol_focus)
                self._play_sound("forward", 0.65)
            return

        if self.credential_note.contains_note(
            self._corrected_scene_position(scene_position)
        ):
            self._stop_desk_pan()
            self.head_offset = (0, 0)
            self.item_inspector.open()
            self._play_sound("paper", 0.55)
            return

        if monitor_position is not None:
            if CASE_STORY_RECT.collidepoint(monitor_position):
                self.case_dialog.reopen()
                self._play_sound("forward", 0.6)
                return
            if COMPARE_BUTTON_RECT.collidepoint(monitor_position):
                if len(self.documents) > 2:
                    self.side_view.open(self.documents)
                    self._play_sound("forward", 0.6)
                return
            if CALCULATOR_BUTTON_RECT.collidepoint(monitor_position):
                self.calculator.toggle()
                self._play_sound("forward" if self.calculator.is_open else "back", 0.6)
                return
            if self.database_search.handle_launcher_click(monitor_position):
                self._play_sound("forward", 0.7)
                return
            hint_action = self.case_hint.handle_mouse_down(monitor_position)
            if hint_action is not None:
                if hint_action == "open":
                    self._play_sound("hint")
                elif hint_action == "close":
                    self._play_sound("back", 0.65)
                else:
                    self._play_sound("forward", 0.65)
                return

        if monitor_position is not None and self._handle_desk_control(monitor_position):
            self._play_sound("click", 0.7)
            return

        if (
            self.case_completed
            and self._get_document("final").is_signed
            and monitor_position is not None
            and CASE_SUBMIT_RECT.collidepoint(monitor_position)
        ):
            self._advance_case_or_show_newspaper()
            return

        if (
            monitor_position is not None
            and PROTOCOL_RECT.collidepoint(monitor_position)
            and self.protocol_panel.handle_mouse_down(monitor_position)
        ):
            self._play_sound("click")
            return

        clicked_stamp = self._get_clicked_stamp(scene_position)
        if clicked_stamp is not None:
            self._select_stamp(clicked_stamp)
            self._play_sound("toggle", 0.6)
            return

        if monitor_position is None:
            return

        ai_action = self.ai_decision_panel.handle_panel_mouse_down(monitor_position)
        if ai_action is not None:
            action, document_id = ai_action
            if action == "toggle" and document_id is not None:
                self._focus_on_document(document_id)
                self._play_sound("toggle", 0.6)
            elif action == "open":
                self.ai_report_seen = True
                self._play_sound("forward", 0.7)
            elif action == "scroll":
                self._play_sound("scroll", 0.7)
            return

        for document in reversed(self.documents):
            if not document.contains_point(monitor_position):
                continue
            self._bring_document_to_front(document)
            if document.document_id != "final":
                self.read_document_ids.add(document.document_id)

            if (
                document.document_id == "final"
                and document.contains_signature_target(monitor_position)
            ):
                self.signature_pad.open(document.signature_image)
                self._play_sound("paper", 0.7)
                return

            if (
                self.selected_stamp_id is not None
                and document.contains_stamp_target(monitor_position)
            ):
                if not self.case_completed:
                    self._request_stamp(self.selected_stamp_id)
                return

            evidence = document.evidence_at_monitor(monitor_position)
            if evidence is not None and click_count < 2:
                self._handle_evidence_comparison(document, evidence)
                return

            if document.contains_inspect_button(monitor_position) or click_count >= 2:
                self.document_inspector.open(document)
                self.inspected_document_ids.add(document.document_id)
                self._play_sound("document", 0.62)
                return

            document.start_drag(monitor_position)
            self._play_sound("document", 0.42)
            self.active_document = document
            return

    def _handle_mouse_motion(self) -> None:
        scene_position = self.input_manager.mouse_position
        monitor_position = self.scene_to_monitor(scene_position)
        self.calculator.handle_mouse_motion(monitor_position)
        self.popups.handle_mouse_move(monitor_position)
        self.protocol_panel.update_hover(monitor_position)
        self.ai_decision_panel.update_hover(monitor_position)
        self.ai_decision_panel.handle_mouse_motion(monitor_position)
        self.case_dialog.update_hover(monitor_position)
        self.case_hint.update_hover(monitor_position)
        self.hovered_evidence = self._find_evidence_at(monitor_position)

        if self.document_inspector.is_open:
            self.document_inspector.handle_mouse_motion(monitor_position)
            return
        if self.desk_panning:
            self.hovered_evidence = None
            if (
                scene_position is not None
                and MONITOR_SCREEN_RECT.collidepoint(scene_position)
                and self.last_desk_pan_position is not None
            ):
                pan_position = (
                    scene_position[0] - MONITOR_SCREEN_RECT.x,
                    scene_position[1] - MONITOR_SCREEN_RECT.y,
                )
                delta = (
                    pan_position[0] - self.last_desk_pan_position[0],
                    pan_position[1] - self.last_desk_pan_position[1],
                )
                self._pan_documents(delta)
                self.last_desk_pan_position = pan_position
            return
        if self._is_modal_open() or self.active_document is None:
            return
        if monitor_position is not None:
            self.active_document.drag(monitor_position, DESK_CONTENT_BOUNDS)

    def _handle_mouse_up(self) -> None:
        self.calculator.handle_mouse_up()
        self.popups.handle_mouse_up()
        self.ai_decision_panel.handle_mouse_up()
        if self.document_inspector.is_open:
            self.document_inspector.handle_mouse_up()
        if self.active_document is not None:
            self.active_document.stop_drag()
            self.active_document = None

    def _handle_case_dialog_action(self, action: str | None) -> None:
        if action is None or action in ("consume", "cancel", "start", "back"):
            return
        if action == "restart":
            self._restart_turn()
            return
        if action.startswith("confirm:"):
            self._commit_stamp(action.split(":", maxsplit=1)[1])

    def _request_stamp(self, stamp_id: str) -> None:
        """Before the confirmation, the player writes down what they concluded."""
        if self.case.conclusions and not self.conclusion_done:
            self.conclusion_panel.open(self.case)
            self._play_sound("paper", 0.6)
            return
        self.case_dialog.request_confirmation(stamp_id)

    def _commit_stamp(self, stamp_id: str) -> None:
        final_document = self._get_document("final")
        final_document.place_stamp(stamp_id, self.stamp_marks[stamp_id])
        self._play_sound("stamp")
        self.case_completed = True
        self.popups.clear()
        self.side_view.close()
        self._bring_document_to_front(final_document)
        self._clear_stamp_selection()
        self.case_dialog.pending_stamp_id = None
        self.case_dialog.mode = None
        if not self.tutorial_active:
            self.case_results.append(
                CaseResult(
                    case=self.case,
                    selected_stamp=stamp_id,
                    correct=stamp_id == self.case.correct_stamp,
                    conclusions_correct=self.conclusion_answers[0],
                    conclusions_total=self.conclusion_answers[1],
                )
            )

    def _reset_case(self) -> None:
        if not self.tutorial_active and self.case_results and self.case_results[-1].case.case_id == self.case.case_id:
            self.case_results.pop()
        self._load_case(self.case_index, tutorial=self.tutorial_active)

    def _load_case(self, case_index: int, *, tutorial: bool = False) -> None:
        self.tutorial_active = tutorial
        self.case_index = -1 if tutorial else case_index
        self.case = TUTORIAL_CASE if tutorial else self.shift_cases[self.case_index]
        self.completed_pairs.clear()
        self.conclusion_done = False
        self.conclusion_answers = (0, 0)
        self.conclusion_panel.close()
        self._stop_desk_pan()
        self.evidence_notes.clear()
        self.comparison_anchor = None
        self.comparison_result = None
        self.hovered_evidence = None
        self.active_document = None
        self.documents = self._create_documents()
        self._apply_case_layout()
        self.case_completed = False
        self.ai_report_seen = False
        self.inspected_document_ids.clear()
        self.document_inspector = DocumentInspector(self.case.evidence_summary)
        self.ai_decision_panel = AIDecisionPanel(self.case)
        self.case_dialog = CaseDialog(self.case)
        self.case_hint = CaseHint(self.case)
        self.database_search.set_case(self.case)
        self.signature_pad.close()
        self.protocol_panel.close_popup()
        self._clear_stamp_selection()
        self.hovered_desk_control = None
        self.submit_hovered = False
        self._reset_clock()

    def _advance_case_or_show_newspaper(self) -> None:
        if self.tutorial_active:
            self._load_case(0)
            self._play_sound("forward", 0.7)
            return
        if self.case_index >= len(self.shift_cases) - 1:
            self._play_sound("forward", 0.75)
            self.newspaper_transition = "shutdown"
            self.newspaper_transition_time = 0.0
            return
        self._load_case(self.case_index + 1)
        self._play_sound("forward", 0.7)

    def _restart_turn(self) -> None:
        """Back to the 'how many cases?' screen, with a clean desk behind it."""
        self.newspaper.close()
        self.newspaper_transition = None
        self.newspaper_transition_time = 0.0
        self.case_results.clear()
        self.calculator.close()
        self.story_intro.close()
        self.clock_enabled = False
        self._load_case(-1, tutorial=True)
        self.needs_setup = True
        self.setup.open()

    def _start_from_setup(self) -> None:
        self.begin_shift(self.setup.count, self.setup.with_tutorial, self.setup.with_clock)
        self._play_sound("forward", 0.7)

    def begin_shift(self, count: int = SHIFT_SIZE, with_tutorial: bool = True, with_clock: bool = False) -> None:
        """Draw `count` cases from the bank and start (optionally with the training)."""
        self.setup.close()
        self.story_intro.close()
        self.needs_setup = False
        self.case_results.clear()
        self.clock_enabled = with_clock
        self.captchas_solved = 0
        self.captchas_shown = 0
        self.director = ComplicationDirector()
        self.shift_cases = pick_shift(self.seen_case_ids, count=count)
        if with_tutorial:
            self._load_case(-1, tutorial=True)
        else:
            self._load_case(0)
        if with_clock:
            self.story_intro.open()

    def _update_newspaper_transition(self, dt: float) -> None:
        self.newspaper_transition_time += dt
        if (
            self.newspaper_transition == "shutdown"
            and self.newspaper_transition_time >= NEWS_SHUTDOWN_DURATION
        ):
            self.newspaper.captchas_solved = self.captchas_solved
            self.newspaper.captchas_shown = self.captchas_shown
            self.newspaper.open(self.case_results)
            self.newspaper_transition = "reveal"
            self.newspaper_transition_time = 0.0
        elif (
            self.newspaper_transition == "reveal"
            and self.newspaper_transition_time >= NEWS_REVEAL_DURATION
        ):
            self.newspaper_transition = None
            self.newspaper_transition_time = 0.0

    def _render_newspaper_transition(self, surface: pygame.Surface) -> None:
        if self.newspaper_transition is None:
            return

        overlay = pygame.Surface(MONITOR_SCREEN_RECT.size, pygame.SRCALPHA)
        if self.newspaper_transition == "reveal":
            progress = min(1.0, self.newspaper_transition_time / NEWS_REVEAL_DURATION)
            overlay.fill((0, 0, 0, round(255 * (1.0 - progress))))
            surface.blit(overlay, MONITOR_SCREEN_RECT.topleft)
            return

        time = self.newspaper_transition_time
        overlay.fill((0, 0, 0, round(255 * min(1.0, time / 0.55))))
        if 0.55 <= time < 1.05:
            collapse = (time - 0.55) / 0.5
            line_width = max(0, round(MONITOR_SCREEN_RECT.width * (1.0 - collapse)))
            line_rect = pygame.Rect(0, 0, line_width, max(2, round(8 * (1.0 - collapse))))
            line_rect.center = overlay.get_rect().center
            pygame.draw.rect(overlay, (213, 222, 154), line_rect)
        elif time >= 1.05:
            title_alpha = min(255, round(255 * (time - 1.05) / 0.35))
            title = self.transition_title_font.render("NOTICIÁRIO DO DIA", False, (230, 218, 169))
            title.set_alpha(title_alpha)
            overlay.blit(title, title.get_rect(center=(overlay.get_width() // 2, 302)))
            subtitle = self.transition_body_font.render(
                "AS CONSEQUÊNCIAS DO TURNO",
                False,
                (139, 145, 91),
            )
            subtitle.set_alpha(title_alpha)
            overlay.blit(subtitle, subtitle.get_rect(center=(overlay.get_width() // 2, 355)))
        surface.blit(overlay, MONITOR_SCREEN_RECT.topleft)

    def _render_monitor_content(self, surface: pygame.Surface) -> None:
        self._render_monitor_background(self.monitor_surface)
        self.protocol_panel.render_menu(self.monitor_surface)
        self.ai_decision_panel.render_panel(
            self.monitor_surface,
            self.read_document_ids,
        )
        previous_clip = self.monitor_surface.get_clip()
        self.monitor_surface.set_clip(DOCUMENT_WORKSPACE)
        for document in self.documents:
            document.render(self.monitor_surface)
        self._render_document_flash(self.monitor_surface)
        self._render_evidence_comparison(self.monitor_surface)
        self.monitor_surface.set_clip(previous_clip)
        self._render_case_guidance(self.monitor_surface)
        self._render_clock(self.monitor_surface)
        self._render_case_progress(self.monitor_surface)
        self._render_story_button(self.monitor_surface)
        self._render_calculator_button(self.monitor_surface)
        self._render_compare_button(self.monitor_surface)
        self.database_search.render_launcher(self.monitor_surface)
        self.case_hint.render_button(self.monitor_surface)
        self._render_desk_zoom_controls(self.monitor_surface)
        if self.case_completed and self._get_document("final").is_signed:
            self._render_submit_button(self.monitor_surface)
        self._render_comparison_card(self.monitor_surface)
        self.calculator.render(self.monitor_surface)
        self.popups.render(self.monitor_surface)
        self.toast.render(self.monitor_surface)
        self.monitor_surface.blit(self.monitor_glass, (0, 0))
        surface.blit(self.monitor_surface, MONITOR_SCREEN_RECT.topleft)

    def _render_monitor_background(self, surface: pygame.Surface) -> None:
        surface.fill(MONITOR_BASE_COLOR)
        pygame.draw.rect(surface, WORKSPACE_SCREEN_COLOR, DOCUMENT_WORKSPACE)
        for y in range(DOCUMENT_WORKSPACE.top + 3, DOCUMENT_WORKSPACE.bottom, 6):
            pygame.draw.line(
                surface,
                (8, 25, 20),
                (DOCUMENT_WORKSPACE.left, y),
                (DOCUMENT_WORKSPACE.right - 1, y),
            )
        for x in range(DOCUMENT_WORKSPACE.left + 15, DOCUMENT_WORKSPACE.right, 48):
            pygame.draw.line(
                surface,
                (7, 21, 18),
                (x, DOCUMENT_WORKSPACE.top),
                (x, DOCUMENT_WORKSPACE.bottom - 1),
            )
        pygame.draw.rect(surface, (36, 55, 39), DOCUMENT_WORKSPACE, 2)

    @staticmethod
    def _build_monitor_glass() -> pygame.Surface:
        glass = pygame.Surface(MONITOR_SCREEN_RECT.size, pygame.SRCALPHA)
        width, height = glass.get_size()
        for y in range(1, height, 4):
            pygame.draw.line(glass, (124, 158, 110, 7), (0, y), (width - 1, y))
        for y in range(11, height, 29):
            for x in range((y * 17) % 31, width, 67):
                glass.set_at((x, y), (177, 198, 139, 10))
        return glass

    def _render_active_popup(self, surface: pygame.Surface) -> None:
        if self.item_inspector.is_open or not self._is_modal_open():
            return
        self.popup_surface.fill((0, 0, 0, 0))
        if self.story_intro.is_open and not self.setup.is_open:
            self.story_intro.render(self.popup_surface)
        elif self.captcha_overlay.is_open:
            self.captcha_overlay.render(self.popup_surface)
        elif self.setup.is_open:
            self.setup.render(self.popup_surface)
        elif self.conclusion_panel.is_open:
            self.conclusion_panel.render(self.popup_surface)
        elif self.newspaper.is_open:
            self.newspaper.render(self.popup_surface)
        elif self.signature_pad.is_open:
            self.signature_pad.render(self.popup_surface)
        elif self.database_search.is_open:
            self.database_search.render(self.popup_surface)
        elif self.case_hint.is_open:
            self.case_hint.render_popup(self.popup_surface)
        elif self.case_dialog.is_open:
            self.case_dialog.render(self.popup_surface)
        elif self.protocol_panel.is_popup_open:
            self.protocol_panel.render_popup(self.popup_surface)
        elif self.side_view.is_open:
            self.side_view.render(self.popup_surface)
            self._render_comparison_card(self.popup_surface, force=True)
        elif self.document_inspector.is_open:
            self.document_inspector.render(self.popup_surface, self.evidence_notes)
        elif self.ai_decision_panel.popup_open:
            self.ai_decision_panel.render_popup(self.popup_surface, self.evidence_notes)
        surface.blit(self.popup_surface, MONITOR_SCREEN_RECT.topleft)

    def _render_stamp_buttons(self, surface: pygame.Surface) -> None:
        for stamp_button in self.stamp_buttons:
            stamp_button.render(surface)

    def _render_tutorial_focus(self, surface: pygame.Surface) -> None:
        focus = self._tutorial_focus_rect()
        if focus is None:
            return
        focus = focus.clip(surface.get_rect())
        if focus.width <= 0 or focus.height <= 0:
            return

        spotlight = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        spotlight.fill((0, 0, 0, 46))
        pygame.draw.rect(spotlight, (0, 0, 0, 0), focus.inflate(16, 16))
        surface.blit(spotlight, (0, 0))

        pulse = (math.sin(self.head_motion_time * 5.2) + 1.0) * 0.5
        expansion = 5 + round(pulse * 7)
        color = (250, 220, 92)
        glow_rect = focus.inflate(expansion * 2, expansion * 2)
        glow = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color, 32 + round(pulse * 28)), glow.get_rect(), 5)
        surface.blit(glow, glow_rect.topleft)
        pygame.draw.rect(surface, color, focus.inflate(6, 6), 3)

        bob = round(pulse * 7)
        if focus.left >= 55:
            tip = (focus.left - 8, focus.centery)
            base_x = focus.left - 31 - bob
            arrow = ((tip[0], tip[1]), (base_x, tip[1] - 11), (base_x, tip[1] + 11))
        else:
            tip = (focus.right + 8, focus.centery)
            base_x = focus.right + 31 + bob
            arrow = ((tip[0], tip[1]), (base_x, tip[1] - 11), (base_x, tip[1] + 11))
        pygame.draw.polygon(surface, (20, 23, 16), tuple((x + 3, y + 3) for x, y in arrow))
        pygame.draw.polygon(surface, color, arrow)

    def _tutorial_focus_rect(self) -> pygame.Rect | None:
        if (
            not self.tutorial_active
            or self.setup.is_open
            or self.story_intro.is_open
            or self.pause_menu.is_open
            or self.newspaper_transition is not None
            or self.newspaper.is_open
            or self.item_inspector.is_open
            or self.database_search.is_open
            or self.case_hint.is_open
            or self.protocol_panel.is_popup_open
            or self.side_view.is_open
            or self.document_inspector.is_open
        ):
            return None
        if self.signature_pad.is_open:
            target = SIGNATURE_CONFIRM_RECT if self.signature_pad.has_ink else SIGNATURE_DRAW_RECT
            return self._monitor_rect_to_scene(target)
        if self.conclusion_panel.is_open:
            return self._monitor_rect_to_scene(self.conclusion_panel.tutorial_target())
        if self.case_dialog.mode == "briefing":
            return self._monitor_rect_to_scene(BRIEFING_START_RECT)
        if self.case_dialog.mode == "confirm":
            return self._monitor_rect_to_scene(CONFIRM_YES_RECT)
        if self.ai_decision_panel.popup_open:
            return self._monitor_rect_to_scene(AI_REPORT_CLOSE_RECT)
        if not self.ai_report_seen:
            return self._monitor_rect_to_scene(AI_REPORT_OPEN_RECT)

        pair_target = self._tutorial_pair_target()
        if pair_target is not None:
            return self._monitor_rect_to_scene(pair_target)

        final_document = self._get_document("final")
        if not self.case_completed and not final_document.visible:
            row = self.ai_decision_panel.row_rect_for_document("final")
            return self._monitor_rect_to_scene(row) if row is not None else None
        if not self.case_completed:
            if self.selected_stamp_id is None:
                correct_stamp = next(
                    (button for button in self.stamp_buttons if button.stamp_id == self.case.correct_stamp),
                    None,
                )
                return correct_stamp.rect if correct_stamp is not None else None
            if final_document.stamp_target is not None:
                return self._monitor_rect_to_scene(final_document.evidence_preview_rect_for_source(final_document.stamp_target))
        if not final_document.is_signed and final_document.signature_target is not None:
            return self._monitor_rect_to_scene(final_document.evidence_preview_rect_for_source(final_document.signature_target))
        if final_document.is_signed:
            return self._monitor_rect_to_scene(CASE_SUBMIT_RECT)
        return None

    def _tutorial_pair_target(self) -> pygame.Rect | None:
        """Next data to click in the scripted training: first of a pair, then its partner."""
        remaining = [
            pair for pair in self.case.tutorial_pairs
            if frozenset(pair) not in self.completed_pairs
        ]
        if not remaining:
            return None
        target_key = remaining[0][0]
        if self.comparison_anchor is not None:
            for first, second in remaining:
                if self.comparison_anchor.key in (first, second):
                    target_key = second if self.comparison_anchor.key == first else first
                    break
        for document in self.documents:
            for region in document.evidence_regions:
                if region.key == target_key and document.visible:
                    return document.evidence_preview_rect(region)
        return None

    def _tutorial_click_allowed(self, scene_position: tuple[int, int]) -> bool:
        if not self.tutorial_active or self.setup.is_open or self.story_intro.is_open:
            return True
        story_click = self.scene_to_monitor(scene_position)
        if (
            story_click is not None
            and CASE_STORY_RECT.collidepoint(story_click)
            and not self.case_dialog.is_open
        ):
            return True  # rereading the case is always allowed
        if self.signature_pad.is_open:
            monitor_position = self.scene_to_monitor(scene_position)
            return bool(
                monitor_position is not None
                and (
                    SIGNATURE_DRAW_RECT.collidepoint(monitor_position)
                    or (
                        self.signature_pad.has_ink
                        and SIGNATURE_CONFIRM_RECT.collidepoint(monitor_position)
                    )
                )
            )
        focus = self._tutorial_focus_rect()
        return focus is None or focus.inflate(10, 10).collidepoint(scene_position)

    def _render_case_progress(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (13, 18, 16), CASE_PROGRESS_RECT)
        pygame.draw.rect(surface, (84, 94, 58), CASE_PROGRESS_RECT, 2)
        text = (
            "TUTORIAL"
            if self.tutorial_active
            else f"CASO {self.case_index + 1}/{len(self.shift_cases)}"
        )
        rendered = self.small_font.render(text, False, (213, 218, 130))
        surface.blit(rendered, rendered.get_rect(center=CASE_PROGRESS_RECT.center))

    def _render_story_button(self, surface: pygame.Surface) -> None:
        hovered = self.story_hovered
        background = (25, 34, 26) if hovered else (5, 11, 9)
        border = (231, 210, 116) if hovered else (176, 148, 74)
        ink = (247, 239, 159) if hovered else (226, 205, 122)
        pygame.draw.rect(surface, background, CASE_STORY_RECT)
        pygame.draw.rect(surface, border, CASE_STORY_RECT, 2)
        page = pygame.Rect(CASE_STORY_RECT.x + 9, CASE_STORY_RECT.y + 6, 17, 22)
        pygame.draw.rect(surface, border, page, 2)
        for line in range(3):
            pygame.draw.line(surface, ink, (page.x + 4, page.y + 6 + line * 5), (page.right - 5, page.y + 6 + line * 5))
        label = self.small_font.render("LER O CASO", False, ink)
        surface.blit(label, label.get_rect(midleft=(CASE_STORY_RECT.x + 34, CASE_STORY_RECT.centery)))

    def _render_compare_button(self, surface: pygame.Surface) -> None:
        background = (25, 34, 26) if self.compare_hovered else (5, 11, 9)
        border = (231, 210, 116) if self.compare_hovered else (76, 89, 57)
        ink = (247, 239, 159) if self.compare_hovered else (213, 218, 130)
        rect = COMPARE_BUTTON_RECT
        pygame.draw.rect(surface, background, rect)
        pygame.draw.rect(surface, border, rect, 2)
        for offset in (0, 13):  # two little pages side by side
            pygame.draw.rect(surface, border, (rect.x + 9 + offset, rect.y + 7, 11, 20), 2)
            pygame.draw.line(surface, ink, (rect.x + 12 + offset, rect.y + 13), (rect.x + 17 + offset, rect.y + 13), 2)
            pygame.draw.line(surface, ink, (rect.x + 12 + offset, rect.y + 18), (rect.x + 17 + offset, rect.y + 18), 2)
        label = self.small_font.render("COMPARAR", False, ink)
        surface.blit(label, label.get_rect(midleft=(rect.x + 44, rect.centery)))

    def _render_calculator_button(self, surface: pygame.Surface) -> None:
        background = (25, 34, 26) if self.calculator_hovered else (5, 11, 9)
        border = (231, 210, 116) if self.calculator_hovered else (76, 89, 57)
        ink = (247, 239, 159) if self.calculator_hovered else (213, 218, 130)
        pygame.draw.rect(surface, background, CALCULATOR_BUTTON_RECT)
        pygame.draw.rect(surface, border, CALCULATOR_BUTTON_RECT, 2)

        icon = pygame.Rect(
            CALCULATOR_BUTTON_RECT.x + 9,
            CALCULATOR_BUTTON_RECT.y + 6,
            20,
            22,
        )
        pygame.draw.rect(surface, border, icon, 2)
        pygame.draw.rect(surface, ink, (icon.x + 4, icon.y + 4, 12, 4))
        for row in range(2):
            for column in range(3):
                pygame.draw.rect(
                    surface,
                    ink,
                    (icon.x + 4 + column * 5, icon.y + 11 + row * 5, 3, 3),
                )

        label = self.small_font.render("CALCULADORA", False, ink)
        surface.blit(
            label,
            label.get_rect(
                midleft=(CALCULATOR_BUTTON_RECT.x + 38, CALCULATOR_BUTTON_RECT.centery)
            ),
        )

    def _render_case_guidance(self, surface: pygame.Surface) -> None:
        final_document = self._get_document("final")
        required_keys = set(self.case.evidence_summary.required_keys)
        found_keys = required_keys.intersection(self.evidence_notes)

        if self.case_completed:
            step = 4
            instruction = (
                "PRONTO! CLIQUE EM 'ENVIAR' PARA IR AO PRÓXIMO CASO"
                if final_document.is_signed
                else "ASSINE: CLIQUE NO CAMPO 'ASSINATURA DO AUDITOR' DA FOLHA"
            )
        elif not self.ai_report_seen:
            step = 1
            instruction = "CLIQUE EM 'ABRIR DECISÃO' PARA LER O QUE A IA DECIDIU"
        elif (
            found_keys != required_keys
            if self.tutorial_active
            else len(found_keys) < min(2, len(required_keys))
        ):
            step = 2
            if self.tutorial_active:
                instruction = (
                    "SELECIONE O OUTRO DADO DESTACADO PARA COMPARAR"
                    if self.comparison_anchor is not None
                    else f"COMPARE OS DADOS DESTACADOS: {len(found_keys)}/{len(required_keys)} ENCONTRADOS"
                )
            else:
                instruction = (
                    "AGORA CLIQUE NO DADO QUE QUER COMPARAR COM ELE"
                    if self.comparison_anchor is not None
                    else "LEIA OS PAPÉIS 1, 2, 3... E COMPARE DOIS DADOS AMARELOS"
                )
        else:
            step = 3
            if not final_document.visible:
                instruction = "ABRA A 'FOLHA DE AUDITORIA' NO PAINEL DA DIREITA E ESCOLHA UM CARIMBO"
            elif self.selected_stamp_id is not None:
                instruction = "AGORA CLIQUE NA ÁREA AMARELA DA FOLHA PARA CARIMBAR"
            else:
                instruction = "DECIDA: ESCOLHA UM CARIMBO NA BANCADA, LÁ EMBAIXO"

        pygame.draw.rect(surface, (5, 11, 9), CASE_GUIDANCE_RECT)
        pygame.draw.rect(surface, (76, 89, 57), CASE_GUIDANCE_RECT, 2)
        badge = pygame.Rect(
            CASE_GUIDANCE_RECT.x + 2,
            CASE_GUIDANCE_RECT.y + 2,
            112,
            CASE_GUIDANCE_RECT.height - 4,
        )
        pygame.draw.rect(surface, (47, 54, 37), badge)
        badge_text = self.small_font.render(f"PASSO {step}/4", False, (237, 193, 91))
        surface.blit(badge_text, badge_text.get_rect(center=badge.center))
        question_text = self.guide_font.render(
            self._fit_line(f"PERGUNTA: {self.case.review_question.upper()}", self._guidance_width()),
            False,
            (237, 236, 183),
        )
        surface.blit(question_text, (badge.right + 15, CASE_GUIDANCE_RECT.y + 8))
        instruction_text = self.guide_font.render(self._fit_line(instruction, self._guidance_width()), False, (159, 169, 108))
        surface.blit(
            instruction_text,
            (badge.right + 15, CASE_GUIDANCE_RECT.y + 36),
        )

    # -- work clock and complications -----------------------------------
    def _timed_case(self) -> bool:
        return self.clock_enabled and not self.tutorial_active and self.clock_limit > 0

    def _guidance_width(self) -> int:
        return 585 if self._timed_case() else 700

    def _reset_clock(self) -> None:
        self.popups.clear()
        self.side_view.close()
        self.captcha_overlay.close()
        self.toast.clear()
        self.timeout_time = 0.0
        self.clock_elapsed = 0.0
        self.time_flash = ("", 0.0)
        if self.clock_enabled and not self.tutorial_active:
            turn = self.case.turn or 3
            self.clock_limit = float(case_time_limit(turn))
            self.clock_left = self.clock_limit
            self.clock_plan = self.director.plan(self.clock_limit, turn)
        else:
            self.clock_limit = self.clock_left = 0.0
            self.clock_plan = []
        self.clock_plan_index = 0

    def _clock_running(self) -> bool:
        return (
            self._timed_case()
            and not self.case_completed
            and self.timeout_time <= 0
            and not self.setup.is_open
            and not self.story_intro.is_open
            and (self.captcha_overlay.is_open or not self._is_modal_open())
        )

    def _update_clock(self, dt: float) -> None:
        self.time_flash = (self.time_flash[0], max(0.0, self.time_flash[1] - dt))
        if not self._clock_running():
            return
        self.clock_left -= dt
        self.clock_elapsed += dt
        if self.clock_left <= 0:
            self._handle_timeout()
            return
        if self.captcha_overlay.is_open:
            return
        if self.clock_plan_index < len(self.clock_plan) and self.clock_elapsed >= self.clock_plan[self.clock_plan_index].at:
            self._trigger(self.clock_plan[self.clock_plan_index])
            self.clock_plan_index += 1

    def _trigger(self, event) -> None:
        self._stop_desk_pan()
        if self.active_document is not None:
            self.active_document.stop_drag()
            self.active_document = None
        if event.kind == "popups":
            self.popups.spawn(int(event.detail))
            self.toast.show(random.choice(POPUP_QUOTES), "suspicious")
            self._play_sound("error", 0.5)
            return
        kind = self.director.pick_captcha(event.detail)
        captcha = create_captcha(kind, random.Random(), self.assets.assets_root)
        self.captchas_shown += 1
        self.captcha_overlay.open(captcha, self.captchas_shown)
        self.toast.clear()
        self._play_sound("hint", 0.7)

    def _flash_time(self, text: str) -> None:
        self.time_flash = (text, 1.4)

    def _update_captcha_overlay(self, dt: float) -> None:
        self.captcha_overlay.update(dt)
        for name, value in self.captcha_overlay.pop_events():
            if name == "sound":
                self._play_sound(str(value), 0.5)
            elif name == "penalty":
                self.clock_left -= WRONG_ANSWER_PENALTY
                self._flash_time(f"-{WRONG_ANSWER_PENALTY}s")
                self.toast.show(random.choice(FAILED_QUOTES), "angry")
            elif name == "solved":
                self.captchas_solved += 1
                self.clock_left += TIME_BONUS_SECONDS
                self._flash_time(f"+{TIME_BONUS_SECONDS}s")
                self.toast.show(random.choice(SOLVED_QUOTES), "happy")
            elif name == "skipped":
                self.clock_left -= SKIP_PENALTY
                self._flash_time(f"-{SKIP_PENALTY}s")
                self.toast.show(SKIPPED_QUOTE, "angry")

    def _handle_timeout(self) -> None:
        """The quota ran out: the case leaves the desk with no decision."""
        self.clock_left = 0.0
        self.popups.clear()
        self.side_view.close()
        self.captcha_overlay.close()
        self.calculator.close()
        self.database_search.close()
        self.case_completed = True
        self.case_results.append(CaseResult(case=self.case, selected_stamp="timeout", correct=False))
        self.timeout_time = 2.4
        self._play_sound("error", 0.8)
        self.toast.show(TIMEOUT_QUOTE, "angry")

    def _update_timeout(self, dt: float) -> None:
        if self.timeout_time <= 0:
            return
        self.timeout_time -= dt
        if self.timeout_time <= 0:
            self.timeout_time = 0.0
            self.toast.clear()
            self._advance_case_or_show_newspaper()

    def _render_timeout_banner(self, surface: pygame.Surface) -> None:
        if self.timeout_time <= 0:
            return
        overlay = pygame.Surface(MONITOR_SCREEN_RECT.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        banner = pygame.Rect(0, 0, 760, 150)
        banner.center = overlay.get_rect().center
        pygame.draw.rect(overlay, (24, 8, 8), banner)
        pygame.draw.rect(overlay, (224, 82, 67), banner, 5)
        title = self.transition_title_font.render("TEMPO ESGOTADO", False, (240, 120, 100))
        overlay.blit(title, title.get_rect(center=(banner.centerx, banner.centery - 22)))
        note = self.transition_body_font.render("O CASO SAIU DA SUA MESA SEM DECISÃO", False, (230, 196, 170))
        overlay.blit(note, note.get_rect(center=(banner.centerx, banner.centery + 38)))
        surface.blit(overlay, MONITOR_SCREEN_RECT.topleft)

    def _render_clock(self, surface: pygame.Surface) -> None:
        if not self._timed_case():
            return
        left = max(0.0, self.clock_left)
        ratio = left / self.clock_limit
        running = self._clock_running()
        if ratio > 0.4:
            color = (170, 226, 120)
        elif ratio > 0.15:
            color = (237, 193, 91)
        else:
            color = (224, 82, 67) if int(self.head_motion_time * 4) % 2 == 0 else (255, 150, 130)
        pygame.draw.rect(surface, (5, 11, 9), CLOCK_RECT)
        pygame.draw.rect(surface, color, CLOCK_RECT, 2)
        label = "COTA" if running or self.case_completed else "PAUSADO"
        surface.blit(self.guide_font.render(label, False, (159, 169, 108)), (CLOCK_RECT.x + 8, CLOCK_RECT.y + 4))
        minutes, seconds = divmod(int(math.ceil(left)), 60)
        text = self.status_font.render(f"{minutes:02d}:{seconds:02d}", False, color)
        surface.blit(text, text.get_rect(midright=(CLOCK_RECT.right - 8, CLOCK_RECT.y + 30)))
        bar = pygame.Rect(CLOCK_RECT.x + 6, CLOCK_RECT.bottom - 9, CLOCK_RECT.width - 12, 5)
        pygame.draw.rect(surface, (30, 38, 30), bar)
        pygame.draw.rect(surface, color, (bar.x, bar.y, round(bar.width * ratio), bar.height))
        flash_text, flash_left = self.time_flash
        if flash_text and flash_left > 0:
            good = flash_text.startswith("+")
            flash = self.status_font.render(flash_text, False, (120, 240, 130) if good else (255, 110, 90))
            surface.blit(flash, flash.get_rect(midright=(CLOCK_RECT.x - 10, CLOCK_RECT.centery - round((1.4 - flash_left) * 14))))

    def _fit_line(self, text: str, width: int) -> str:
        while self.guide_font.size(text)[0] > width and len(text) > 4:
            text = text[:-2].rstrip() + "…"
        return text

    def _render_desk_zoom_controls(self, surface: pygame.Surface) -> None:
        controls = (
            ("zoom_out", DESK_ZOOM_OUT_RECT, "−"),
            ("zoom_in", DESK_ZOOM_IN_RECT, "+"),
        )
        for control_id, rect, label in controls:
            hovered = self.hovered_desk_control == control_id
            pygame.draw.rect(surface, (28, 35, 29) if hovered else (13, 18, 16), rect)
            pygame.draw.rect(surface, (244, 236, 157) if hovered else (84, 94, 58), rect, 2)
            rendered = self.status_font.render(label, False, (244, 236, 157))
            surface.blit(rendered, rendered.get_rect(center=rect.center))

        hovered = self.hovered_desk_control == "zoom_reset"
        pygame.draw.rect(surface, (28, 35, 29) if hovered else (13, 18, 16), DESK_ZOOM_LABEL_RECT)
        pygame.draw.rect(surface, (244, 236, 157) if hovered else (84, 94, 58), DESK_ZOOM_LABEL_RECT, 2)
        rendered = self.small_font.render(f"{round(self.desk_zoom * 100)}%", False, (213, 218, 130))
        surface.blit(rendered, rendered.get_rect(center=DESK_ZOOM_LABEL_RECT.center))

    def _render_submit_button(self, surface: pygame.Surface) -> None:
        label = (
            "FINALIZAR TREINAMENTO"
            if self.tutorial_active
            else "CONCLUIR TURNO"
            if self.case_index == len(self.shift_cases) - 1
            else "ENVIAR / PRÓXIMO CASO"
        )
        fill = (51, 58, 43) if self.submit_hovered else (22, 29, 24)
        border = (246, 238, 159) if self.submit_hovered else (173, 145, 83)
        pygame.draw.rect(surface, (5, 9, 8), CASE_SUBMIT_RECT.move(4, 4))
        pygame.draw.rect(surface, fill, CASE_SUBMIT_RECT)
        pygame.draw.rect(surface, border, CASE_SUBMIT_RECT, 3)
        rendered = self.status_font.render(label, False, (246, 238, 159))
        surface.blit(rendered, rendered.get_rect(center=CASE_SUBMIT_RECT.center))

    def _draw_stamp_status(self, surface: pygame.Surface) -> None:
        if self.newspaper_transition is not None or self.newspaper.is_open:
            return
        if self.case_completed:
            if self._get_document("final").is_signed:
                text = "FOLHA ASSINADA — ENVIE A DECISÃO"
            else:
                text = "DECISÃO CARIMBADA — ASSINE O CAMPO DO AUDITOR"
            color = (184, 176, 104)
        elif self.selected_stamp_id is not None:
            label = STAMP_LABELS.get(self.selected_stamp_id, self.selected_stamp_id.upper())
            text = f"CARIMBO: {label} — APLIQUE NA FOLHA DE AUDITORIA"
            color = (242, 226, 118)
        else:
            return
        rendered = self.status_font.render(text, False, color)
        surface.blit(rendered, rendered.get_rect(midtop=STAMP_STATUS_POSITION))

    def _get_clicked_stamp(self, position: tuple[int, int]) -> StampButton | None:
        if self.case_completed:
            return None
        for stamp_button in self.stamp_buttons:
            if stamp_button.handle_click(position):
                return stamp_button
        return None

    def _select_stamp(self, selected_stamp: StampButton) -> None:
        self.selected_stamp_id = selected_stamp.stamp_id
        self.comparison_result = None
        for stamp_button in self.stamp_buttons:
            stamp_button.set_selected(stamp_button is selected_stamp)
        self._present_final_sheet()

    def _clear_stamp_selection(self) -> None:
        self.selected_stamp_id = None
        for stamp_button in self.stamp_buttons:
            stamp_button.set_selected(False)

    def _update_stamp_hover(self, position: tuple[int, int] | None) -> None:
        for stamp_button in self.stamp_buttons:
            stamp_button.update_hover(position)

    def _update_desk_controls_hover(
        self,
        monitor_position: tuple[int, int] | None,
    ) -> None:
        self.hovered_desk_control = None
        if self._is_modal_open() or monitor_position is None:
            return
        if DESK_ZOOM_OUT_RECT.collidepoint(monitor_position):
            self.hovered_desk_control = "zoom_out"
        elif DESK_ZOOM_LABEL_RECT.collidepoint(monitor_position):
            self.hovered_desk_control = "zoom_reset"
        elif DESK_ZOOM_IN_RECT.collidepoint(monitor_position):
            self.hovered_desk_control = "zoom_in"

    def _handle_desk_control(self, monitor_position: tuple[int, int]) -> bool:
        if DESK_ZOOM_OUT_RECT.collidepoint(monitor_position):
            self._change_desk_zoom(-1)
            return True
        if DESK_ZOOM_LABEL_RECT.collidepoint(monitor_position):
            self._set_desk_zoom(1.0)
            return True
        if DESK_ZOOM_IN_RECT.collidepoint(monitor_position):
            self._change_desk_zoom(1)
            return True
        return False

    def _change_desk_zoom(self, direction: int) -> None:
        current_index = min(
            range(len(DESK_ZOOM_LEVELS)),
            key=lambda index: abs(DESK_ZOOM_LEVELS[index] - self.desk_zoom),
        )
        next_index = max(0, min(len(DESK_ZOOM_LEVELS) - 1, current_index + direction))
        self._set_desk_zoom(DESK_ZOOM_LEVELS[next_index])

    def _set_desk_zoom(self, zoom: float) -> None:
        if zoom == self.desk_zoom:
            return
        old_zoom = self.desk_zoom
        self.desk_zoom = zoom
        for document in self.documents:
            document.rescale_preview(old_zoom, zoom, DESK_CONTENT_BOUNDS)

    def _bring_document_to_front(self, document: CaseDocument) -> None:
        self.documents.remove(document)
        self.documents.append(document)

    def _handle_side_view_click(self, monitor_position: tuple[int, int]) -> None:
        if (
            self.comparison_result is not None
            and self.comparison_card.contains(monitor_position)
        ):
            if self.comparison_card.is_close_hit(monitor_position):
                self.comparison_result = None
                self._play_sound("back", 0.5)
            elif (
                self.comparison_card.is_protocol_hit(monitor_position)
                and self.comparison_result[2].kind != "none"
            ):
                self.side_view.close()
                self.protocol_panel.open_protocol(self.case.protocol_focus)
                self._play_sound("forward", 0.65)
            return
        result = self.side_view.handle_mouse_down(monitor_position)
        if result == "close":
            self.side_view.close()
            self._play_sound("back", 0.6)
        elif result == "chip":
            self._play_sound("click", 0.5)
        elif isinstance(result, tuple):
            _, document, source = result
            evidence = document.evidence_at(source)
            if evidence is not None:
                self._handle_evidence_comparison(document, evidence)

    def _handle_evidence_comparison(
        self,
        document: CaseDocument,
        evidence: EvidenceRegion,
    ) -> None:
        selection = EvidenceSelection(
            document.document_id,
            evidence.key,
            evidence.value,
            evidence.note,
        )
        if self.comparison_anchor is None:
            self.comparison_anchor = selection
            self.comparison_result = None
            self._play_sound("toggle_on", 0.45)
            return
        if self.comparison_anchor == selection:
            self.comparison_anchor = None
            self._play_sound("toggle_off", 0.4)
            return

        first = self.comparison_anchor
        link = find_link(self.case, first.key, selection.key)
        self.comparison_result = (first, selection, link)
        self.comparison_anchor = None
        if link.kind == "none":
            self._play_sound("toggle_off", 0.5)
            return
        self.completed_pairs.add(frozenset((first.key, selection.key)))
        if len(set(self.evidence_notes) | {first.key, selection.key}) >= min(2, len(self.case.evidence_summary.required_keys)):
            self.ai_decision_panel.scroll_to_end()
        for chosen in (first, selection):
            self.evidence_notes[chosen.key] = chosen.note
            self._get_document(chosen.document_id).set_evidence_marked(chosen.key, True)
        self._play_sound(
            {"equal": "success", "different": "error"}.get(link.kind, "toggle_on"),
            0.55,
        )

    def _find_evidence_at(
        self,
        monitor_position: tuple[int, int] | None,
    ) -> EvidenceSelection | None:
        if monitor_position is None or not DOCUMENT_WORKSPACE.collidepoint(monitor_position):
            return None
        for document in reversed(self.documents):
            evidence = document.evidence_at_monitor(monitor_position)
            if evidence is not None:
                return EvidenceSelection(document.document_id, evidence.key, evidence.value, evidence.note)
        return None

    def _render_document_flash(self, surface: pygame.Surface) -> None:
        document_id, remaining = self.document_flash
        if document_id is None or remaining <= 0:
            return
        document = self._get_document(document_id)
        pulse = 0.5 + 0.5 * math.sin(remaining * 18)
        rect = document.rect.inflate(round(8 + pulse * 10), round(8 + pulse * 10))
        pygame.draw.rect(surface, (255, 236, 130), rect, 4)

    def _render_evidence_markers(self, surface: pygame.Surface) -> None:
        """Pulse a small marker on every field the player is allowed to compare."""
        pulse = (math.sin(self.head_motion_time * 4.0) + 1.0) * 0.5
        radius = 5 + round(pulse * 2)
        for index, document in enumerate(self.documents):
            if not document.visible:
                continue
            covering = [other for other in self.documents[index + 1:] if other.visible]
            for region in document.evidence_regions:
                if region.key in document.marked_evidence:
                    continue
                rect = document.evidence_preview_rect(region)
                center = (rect.right - 9, rect.centery)
                if not DOCUMENT_WORKSPACE.collidepoint(center):
                    continue
                if any(other.rect.collidepoint(center) for other in covering):
                    continue
                points = (
                    (center[0], center[1] - radius),
                    (center[0] + radius, center[1]),
                    (center[0], center[1] + radius),
                    (center[0] - radius, center[1]),
                )
                pygame.draw.polygon(surface, (24, 20, 8), tuple((x + 1, y + 1) for x, y in points))
                pygame.draw.polygon(surface, COMPARE_PENDING, points)
                pygame.draw.polygon(surface, (255, 246, 190), points, 1)

    def _render_comparison_card(self, surface: pygame.Surface, force: bool = False) -> None:
        if self.comparison_result is None or (self._is_modal_open() and not force):
            return
        first, second, link = self.comparison_result
        protocol = self._case_protocol()
        self.comparison_card.render(
            surface,
            (self._selection_caption(first), self._card_value(first)),
            (self._selection_caption(second), self._card_value(second)),
            link.kind,
            link.text,
            None if link.kind == "none" or protocol is None else (protocol.number, protocol.scientist, protocol.title),
        )

    @staticmethod
    def _card_value(selection: EvidenceSelection) -> str:
        return selection.value if len(selection.value) <= 26 else selection.note

    def _case_protocol(self):
        return next((p for p in PROTOCOLS if p.slug == self.case.protocol_focus), None)

    def _selection_caption(self, selection: EvidenceSelection) -> str:
        """'Document · field' so the player knows what each value is."""
        for document in self.case.documents:
            if document.document_id != selection.document_id:
                continue
            for field in document.fields:
                if field.evidence_key == selection.key:
                    return f"{document.title} · {field.label}"
            return document.title
        return selection.document_id

    def _render_evidence_comparison(self, surface: pygame.Surface) -> None:
        self._render_evidence_markers(surface)
        hovered = self.hovered_evidence
        if hovered is not None and self.comparison_result is None:
            hovered_rect = self._selection_rect(hovered)
            if hovered_rect is not None:
                pygame.draw.rect(surface, (242, 235, 171), hovered_rect.inflate(4, 4), 2)

        if self.comparison_anchor is not None:
            anchor_rect = self._selection_rect(self.comparison_anchor)
            if anchor_rect is None:
                return
            pygame.draw.rect(surface, COMPARE_PENDING, anchor_rect.inflate(5, 5), 3)
            pointer = self.scene_to_monitor(self.input_manager.mouse_position)
            if pointer is not None and DOCUMENT_WORKSPACE.collidepoint(pointer):
                self._draw_dashed_line(surface, anchor_rect.center, pointer, COMPARE_PENDING)
            label = self.guide_font.render("SELECIONE OUTRO DADO", False, (255, 244, 178))
            label_rect = label.get_rect(midbottom=(anchor_rect.centerx, anchor_rect.y - 7))
            label_rect.clamp_ip(DOCUMENT_WORKSPACE.inflate(-8, -8))
            pygame.draw.rect(surface, (9, 14, 12), label_rect.inflate(12, 7))
            surface.blit(label, label_rect)
            return

        if self.comparison_result is None:
            return
        first, second, link = self.comparison_result
        first_rect = self._selection_rect(first)
        second_rect = self._selection_rect(second)
        if first_rect is None or second_rect is None:
            return
        color = LINK_COLORS.get(link.kind, COMPARE_NONE)
        pygame.draw.line(surface, (8, 12, 10), first_rect.center, second_rect.center, 8)
        pygame.draw.line(surface, color, first_rect.center, second_rect.center, 4)
        for rect in (first_rect, second_rect):
            pygame.draw.rect(surface, color, rect.inflate(5, 5), 3)
            pygame.draw.circle(surface, color, rect.center, 5)


    def _selection_rect(self, selection: EvidenceSelection) -> pygame.Rect | None:
        try:
            document = self._get_document(selection.document_id)
        except KeyError:
            return None
        if not document.visible:
            return None
        evidence = next(
            (region for region in document.evidence_regions if region.key == selection.key),
            None,
        )
        return document.evidence_preview_rect(evidence) if evidence is not None else None

    @staticmethod
    def _normalize_comparison_value(value: str) -> str:
        normalized = unicodedata.normalize("NFKC", value).casefold().strip()
        return " ".join(normalized.split())

    @staticmethod
    def _draw_dashed_line(
        surface: pygame.Surface,
        start: tuple[int, int],
        end: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        delta = pygame.Vector2(end) - pygame.Vector2(start)
        length = delta.length()
        if length <= 0:
            return
        direction = delta.normalize()
        distance = 0.0
        while distance < length:
            segment_start = pygame.Vector2(start) + direction * distance
            segment_end = pygame.Vector2(start) + direction * min(distance + 9, length)
            pygame.draw.line(surface, color, segment_start, segment_end, 2)
            distance += 16

    def _get_document(self, document_id: str) -> CaseDocument:
        for document in self.documents:
            if document.document_id == document_id:
                return document
        raise KeyError(f"Unknown case document: {document_id}")

    def _is_modal_open(self) -> bool:
        return (
            self.setup.is_open
            or self.story_intro.is_open
            or self.captcha_overlay.is_open
            or self.timeout_time > 0
            or self.conclusion_panel.is_open
            or self.newspaper_transition is not None
            or self.newspaper.is_open
            or self.item_inspector.is_open
            or self.signature_pad.is_open
            or self.database_search.is_open
            or self.case_hint.is_open
            or self.case_dialog.is_open
            or self.protocol_panel.is_popup_open
            or self.side_view.is_open
            or self.document_inspector.is_open
            or self.ai_decision_panel.popup_open
        )

    def _draw_layout_rects(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 232, 64), MONITOR_SCREEN_RECT, 2)
        pygame.draw.rect(surface, (107, 207, 255), self._monitor_rect_to_scene(DOCUMENT_WORKSPACE), 2)
        pygame.draw.rect(surface, (161, 255, 146), self._monitor_rect_to_scene(PROTOCOL_RECT), 2)
        pygame.draw.rect(surface, (255, 146, 146), self._monitor_rect_to_scene(AI_DECISION_RECT), 2)
        pygame.draw.rect(surface, (255, 181, 96), self._monitor_rect_to_scene(AI_DATA_RECT), 2)

    def _monitor_rect_to_scene(self, rect: pygame.Rect) -> pygame.Rect:
        return rect.move(MONITOR_SCREEN_RECT.topleft)

    def _draw_debug_text(self, surface: pygame.Surface) -> None:
        monitor_position = self.scene_to_monitor(self.input_manager.mouse_position)
        active_name = self.active_document.name if self.active_document is not None else "nenhum"
        selected = self.selected_stamp_id.upper() if self.selected_stamp_id is not None else "NENHUM"
        text = (
            f"Monitor: {monitor_position} | Documento: {active_name} | "
            f"Carimbo: {selected} | Evidências: {len(self.evidence_notes)}"
        )
        surface.blit(self.small_font.render(text, False, (245, 229, 115)), DEBUG_TEXT_POSITION)
