from __future__ import annotations

import math
from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame

from src.core.preferences import UserPreferences
from src.core.scene import Scene
from src.core.settings import DEBUG_LAYOUT_RECTS, DEBUG_UI
from src.gameplay.cases import CASES, CaseResult
from src.gameplay.document_renderer import DocumentRenderer
from src.ui.ai_decision_panel import AIDecisionPanel
from src.ui.case_dialog import CaseDialog, STAMP_LABELS
from src.ui.case_document import CaseDocument
from src.ui.case_hint import CaseHint
from src.ui.credential_note import CredentialNote
from src.ui.database_search import DatabaseSearch
from src.ui.document_inspector import DocumentInspector
from src.ui.item_inspector import ItemInspector
from src.ui.newspaper import FinalNewspaper
from src.ui.pause_menu import PauseMenu
from src.ui.protocol_panel import ProtocolPanel
from src.ui.signature_pad import SignaturePad
from src.ui.stamp_button import StampButton

if TYPE_CHECKING:
    from src.core.assets import AssetManager
    from src.core.audio import AudioManager
    from src.core.input_manager import InputManager
    from src.core.scene_manager import SceneManager


SCREEN_BASE_COLOR = (4, 7, 6)
MONITOR_BASE_COLOR = (4, 12, 10)
WORKSPACE_SCREEN_COLOR = (6, 18, 15)

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
CASE_PROGRESS_RECT = pygame.Rect(304, 72, 136, 34)
CASE_GUIDANCE_RECT = pygame.Rect(304, 114, 847, 38)
CASE_SUBMIT_RECT = pygame.Rect(786, 579, 370, 51)
DESK_ZOOM_LEVELS = (0.75, 0.9, 1.0, 1.2, 1.4, 1.6, 1.8)
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

DOCUMENT_POSITIONS = (
    (312, 157),
    (455, 253),
    (598, 157),
    (741, 253),
    (564, 207),
)


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
        self.case_index = 0
        self.case_results: list[CaseResult] = []
        self.case = CASES[self.case_index]
        self.desk_zoom = 1.0
        self.desk_panning = False
        self.last_desk_pan_position: tuple[int, int] | None = None
        self.head_motion_time = 0.0
        self.head_offset = (0, 0)
        self.hovered_desk_control: str | None = None
        self.submit_hovered = False
        self.terminal_overlay = self.assets.load_image("backgrounds/novo_sprite_teste.png")
        self.monitor_surface = pygame.Surface(MONITOR_SCREEN_RECT.size, pygame.SRCALPHA)
        self.popup_surface = pygame.Surface(MONITOR_SCREEN_RECT.size, pygame.SRCALPHA)
        self.monitor_glass = self._build_monitor_glass()
        self.small_font = pygame.font.SysFont(("Consolas", "Courier New", "monospace"), 19)
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
        self.stamp_buttons = self._create_stamp_buttons()
        self.protocol_panel = ProtocolPanel(self._load_protocol_portraits())
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
        self.database_search = DatabaseSearch(self.case, audio)
        self.signature_pad = SignaturePad()
        self.newspaper = FinalNewspaper(self._load_newspaper_images())
        self.pause_menu = PauseMenu(
            audio,
            self.preferences_provider,
            apply_preferences,
        )

        self.evidence_notes: dict[str, str] = {}
        self.active_document: CaseDocument | None = None
        self.selected_stamp_id: str | None = None
        self.case_completed = False
        self.ai_report_seen = False
        self.inspected_document_ids: set[str] = set()
        self.newspaper_transition: str | None = None
        self.newspaper_transition_time = 0.0

    def on_enter(self) -> None:
        self.pause_menu.close()
        self.credential_note.clear_hover()
        self.item_inspector.close()
        self.head_offset = (0, 0)
        if self.audio is not None:
            self.audio.play_music_sequence(("audit_1", "audit_2"), fade_ms=700)

    def on_exit(self) -> None:
        self.pause_menu.close()
        self.credential_note.clear_hover()
        self.item_inspector.close()
        self.database_search.close()
        self.signature_pad.close()

    def handle_escape(self) -> bool:
        if self.pause_menu.is_open:
            return self.pause_menu.handle_escape()
        if self.newspaper_transition is not None:
            return True
        if self.newspaper.is_open:
            handled = self.newspaper.handle_escape()
            if handled:
                self._play_sound("back", 0.65)
            return handled
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
        if self.document_inspector.is_open:
            self.document_inspector.close()
            self._play_sound("back", 0.65)
            return True
        if self.ai_decision_panel.popup_open:
            self.ai_decision_panel.close()
            self._play_sound("back", 0.65)
            return True
        self._stop_desk_pan()
        self.head_offset = (0, 0)
        self.pause_menu.open()
        return True

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.pause_menu.is_open:
            action = self.pause_menu.handle_event(event, self.input_manager.mouse_position)
            if action == "desktop":
                self.manager.switch_to("desktop")
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
        self._update_desk_controls_hover(monitor_position)
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
        surface.fill(SCREEN_BASE_COLOR)
        self._render_monitor_content(surface)
        surface.blit(self.terminal_overlay, (0, 0))
        self.credential_note.render_note_highlight(surface)
        self._render_status_led(surface)
        if DEBUG_UI and DEBUG_LAYOUT_RECTS:
            self._draw_layout_rects(surface)
        self._render_active_popup(surface)
        self._render_newspaper_transition(surface)
        self._render_stamp_buttons(surface)
        self._draw_stamp_status(surface)
        if DEBUG_UI:
            self._draw_debug_text(surface)
        self.item_inspector.render(surface)
        if self.pause_menu.is_open:
            self.pause_menu.render(surface)

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
        rendered_documents = self.document_renderer.render_case(self.case, portrait)
        documents = [
            CaseDocument(rendered, position)
            for rendered, position in zip(rendered_documents, DOCUMENT_POSITIONS, strict=True)
        ]
        for document in documents:
            document.set_visible(document.document_id == "final")
        return documents

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

        if proposed.left < DESK_CONTENT_BOUNDS.left:
            adjusted_x += DESK_CONTENT_BOUNDS.left - proposed.left
        elif proposed.right > DESK_CONTENT_BOUNDS.right:
            adjusted_x -= proposed.right - DESK_CONTENT_BOUNDS.right

        if proposed.top < DESK_CONTENT_BOUNDS.top:
            adjusted_y += DESK_CONTENT_BOUNDS.top - proposed.top
        elif proposed.bottom > DESK_CONTENT_BOUNDS.bottom:
            adjusted_y -= proposed.bottom - DESK_CONTENT_BOUNDS.bottom

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
        return {path: self.assets.load_image(path) for path in image_paths}

    def _handle_mouse_down(self, click_count: int) -> None:
        scene_position = self.input_manager.mouse_position
        if scene_position is None:
            return
        monitor_position = self.scene_to_monitor(scene_position)

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
                elif action == "close":
                    self._play_sound("back", 0.65)
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

        if self.credential_note.contains_note(
            self._corrected_scene_position(scene_position)
        ):
            self._stop_desk_pan()
            self.head_offset = (0, 0)
            self.item_inspector.open()
            self._play_sound("paper", 0.55)
            return

        if monitor_position is not None:
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
                self._toggle_document_visibility(document_id)
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
                    self.case_dialog.request_confirmation(self.selected_stamp_id)
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
        self.protocol_panel.update_hover(monitor_position)
        self.ai_decision_panel.update_hover(monitor_position)
        self.ai_decision_panel.handle_mouse_motion(monitor_position)
        self.case_dialog.update_hover(monitor_position)
        self.case_hint.update_hover(monitor_position)

        if self.document_inspector.is_open:
            self.document_inspector.handle_mouse_motion(monitor_position)
            return
        if self.desk_panning:
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

    def _commit_stamp(self, stamp_id: str) -> None:
        final_document = self._get_document("final")
        final_document.place_stamp(stamp_id, self.stamp_marks[stamp_id])
        self._play_sound("stamp")
        self.case_completed = True
        self._bring_document_to_front(final_document)
        self._clear_stamp_selection()
        self.case_dialog.pending_stamp_id = None
        self.case_dialog.mode = None
        self.case_results.append(
            CaseResult(
                case=self.case,
                selected_stamp=stamp_id,
                correct=stamp_id == self.case.correct_stamp,
            )
        )

    def _reset_case(self) -> None:
        if self.case_results and self.case_results[-1].case.case_id == self.case.case_id:
            self.case_results.pop()
        self._load_case(self.case_index)

    def _load_case(self, case_index: int) -> None:
        self.case_index = case_index
        self.case = CASES[self.case_index]
        self.desk_zoom = 1.0
        self._stop_desk_pan()
        self.evidence_notes.clear()
        self.active_document = None
        self.documents = self._create_documents()
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

    def _advance_case_or_show_newspaper(self) -> None:
        if self.case_index >= len(CASES) - 1:
            self._play_sound("forward", 0.75)
            self.newspaper_transition = "shutdown"
            self.newspaper_transition_time = 0.0
            return
        self._load_case(self.case_index + 1)
        self._play_sound("forward", 0.7)

    def _restart_turn(self) -> None:
        self.newspaper.close()
        self.newspaper_transition = None
        self.newspaper_transition_time = 0.0
        self.case_results.clear()
        self._load_case(0)

    def _update_newspaper_transition(self, dt: float) -> None:
        self.newspaper_transition_time += dt
        if (
            self.newspaper_transition == "shutdown"
            and self.newspaper_transition_time >= NEWS_SHUTDOWN_DURATION
        ):
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
            self._visible_document_ids,
        )
        previous_clip = self.monitor_surface.get_clip()
        self.monitor_surface.set_clip(DOCUMENT_WORKSPACE)
        for document in self.documents:
            document.render(self.monitor_surface)
        self.monitor_surface.set_clip(previous_clip)
        self._render_case_guidance(self.monitor_surface)
        self._render_case_progress(self.monitor_surface)
        self.database_search.render_launcher(self.monitor_surface)
        self.case_hint.render_button(self.monitor_surface)
        self._render_desk_zoom_controls(self.monitor_surface)
        if self.case_completed and self._get_document("final").is_signed:
            self._render_submit_button(self.monitor_surface)
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
        if self.newspaper.is_open:
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
        elif self.document_inspector.is_open:
            self.document_inspector.render(self.popup_surface, self.evidence_notes)
        elif self.ai_decision_panel.popup_open:
            self.ai_decision_panel.render_popup(self.popup_surface, self.evidence_notes)
        surface.blit(self.popup_surface, MONITOR_SCREEN_RECT.topleft)

    def _render_stamp_buttons(self, surface: pygame.Surface) -> None:
        for stamp_button in self.stamp_buttons:
            stamp_button.render(surface)

    def _render_case_progress(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (13, 18, 16), CASE_PROGRESS_RECT)
        pygame.draw.rect(surface, (84, 94, 58), CASE_PROGRESS_RECT, 2)
        text = f"CASO {self.case_index + 1}/{len(CASES)}"
        rendered = self.small_font.render(text, False, (213, 218, 130))
        surface.blit(rendered, rendered.get_rect(center=CASE_PROGRESS_RECT.center))

    def _render_case_guidance(self, surface: pygame.Surface) -> None:
        final_document = self._get_document("final")
        visible_sources = {
            source.document_id
            for source in self.case.data_sources
            if self._get_document(source.document_id).visible
        }
        inspected_sources = visible_sources.intersection(self.inspected_document_ids)

        if self.case_completed:
            step = 5
            instruction = (
                "ENVIE A DECISÃO PELO BOTÃO ABAIXO"
                if final_document.is_signed
                else "CLIQUE NO CAMPO DE ASSINATURA DA FOLHA"
            )
        elif not self.ai_report_seen:
            step = 1
            instruction = "ABRA A DECISÃO DA IA E ENTENDA O QUE ELA FEZ"
        elif len(visible_sources) < 2:
            step = 2
            instruction = "COLOQUE PELO MENOS DOIS DOCUMENTOS NA MESA"
        elif not inspected_sources:
            step = 3
            instruction = "USE A LUPA OU DUPLO CLIQUE PARA COMPARAR OS DADOS"
        else:
            step = 4
            instruction = (
                "CLIQUE NA ÁREA AMARELA DA FOLHA PARA CARIMBAR"
                if self.selected_stamp_id is not None
                else "ESCOLHA UM CARIMBO PARA REGISTRAR SUA DECISÃO"
            )

        pygame.draw.rect(surface, (5, 11, 9), CASE_GUIDANCE_RECT)
        pygame.draw.rect(surface, (76, 89, 57), CASE_GUIDANCE_RECT, 2)
        badge = pygame.Rect(
            CASE_GUIDANCE_RECT.x + 2,
            CASE_GUIDANCE_RECT.y + 2,
            112,
            CASE_GUIDANCE_RECT.height - 4,
        )
        pygame.draw.rect(surface, (47, 54, 37), badge)
        badge_text = self.small_font.render(f"PASSO {step}/5", False, (237, 193, 91))
        surface.blit(badge_text, badge_text.get_rect(center=badge.center))
        instruction_text = self.small_font.render(instruction, False, (222, 224, 166))
        surface.blit(
            instruction_text,
            instruction_text.get_rect(
                midleft=(badge.right + 18, CASE_GUIDANCE_RECT.centery)
            ),
        )

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
            "CONCLUIR TURNO"
            if self.case_index == len(CASES) - 1
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
        for stamp_button in self.stamp_buttons:
            stamp_button.set_selected(stamp_button is selected_stamp)

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

    def _focus_document(self, document_id: str) -> None:
        document = self._get_document(document_id)
        document.set_visible(True)
        self._bring_document_to_front(document)

    def _toggle_document_visibility(self, document_id: str) -> None:
        document = self._get_document(document_id)
        if document.document_id == "final":
            return
        document.set_visible(not document.visible)
        if document.visible:
            self._bring_document_to_front(document)
        elif self.active_document is document:
            self.active_document = None

    @property
    def _visible_document_ids(self) -> set[str]:
        return {document.document_id for document in self.documents if document.visible}

    def _get_document(self, document_id: str) -> CaseDocument:
        for document in self.documents:
            if document.document_id == document_id:
                return document
        raise KeyError(f"Unknown case document: {document_id}")

    def _is_modal_open(self) -> bool:
        return (
            self.newspaper_transition is not None
            or self.newspaper.is_open
            or self.item_inspector.is_open
            or self.signature_pad.is_open
            or self.database_search.is_open
            or self.case_hint.is_open
            or self.case_dialog.is_open
            or self.protocol_panel.is_popup_open
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
