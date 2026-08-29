from __future__ import annotations

import pygame

from src.gameplay.document_renderer import EvidenceRegion, RenderedDocument


PREVIEW_SIZE = (310, 390)
HIGHLIGHT_COLOR = (244, 216, 65, 78)
TARGET_COLOR = (244, 216, 65, 122)
SIGNATURE_COLOR = (43, 62, 75)


class CaseDocument:
    """High-resolution case document with draggable desk preview and evidence."""

    def __init__(
        self,
        rendered: RenderedDocument,
        position: tuple[int, int],
    ) -> None:
        self.document_id = rendered.document_id
        self.title = rendered.title
        self.name = rendered.document_id
        self.source_image = rendered.surface
        self.evidence_regions = rendered.evidence_regions
        self.stamp_target = rendered.stamp_target
        self.signature_target = rendered.signature_target
        self.rect = pygame.Rect(position, PREVIEW_SIZE)
        self.position = self.rect.topleft
        self.visible = True
        self.dragging = False
        self.drag_offset = pygame.Vector2(0, 0)
        self.marked_evidence: set[str] = set()
        self.applied_stamp_id: str | None = None
        self.applied_stamp_image: pygame.Surface | None = None
        self.stamp_target_active = False
        self.signature_target_active = False
        self.is_signed = False
        self._decorated_cache: pygame.Surface | None = None

    def contains_point(self, position: tuple[int, int]) -> bool:
        return self.visible and self.rect.collidepoint(position)

    def contains_inspect_button(self, position: tuple[int, int]) -> bool:
        return self.inspect_button_rect.collidepoint(position)

    @property
    def inspect_button_rect(self) -> pygame.Rect:
        return pygame.Rect(self.rect.right - 48, self.rect.y + 10, 38, 34)

    def start_drag(self, mouse_position: tuple[int, int]) -> None:
        self.dragging = True
        self.drag_offset.update(
            mouse_position[0] - self.rect.x,
            mouse_position[1] - self.rect.y,
        )

    def drag(self, mouse_position: tuple[int, int], bounds: pygame.Rect | None = None) -> None:
        if not self.dragging:
            return

        self.rect.topleft = (
            int(mouse_position[0] - self.drag_offset.x),
            int(mouse_position[1] - self.drag_offset.y),
        )
        if bounds is not None:
            self._clamp_to_bounds(bounds)
        self.position = self.rect.topleft

    def stop_drag(self) -> None:
        self.dragging = False

    def rescale_preview(
        self,
        old_scale: float,
        new_scale: float,
        bounds: pygame.Rect,
    ) -> None:
        if old_scale <= 0 or new_scale <= 0:
            return
        ratio = new_scale / old_scale
        bounds_center = pygame.Vector2(bounds.center)
        relative_center = pygame.Vector2(self.rect.center) - bounds_center
        self.rect.size = (
            max(1, round(PREVIEW_SIZE[0] * new_scale)),
            max(1, round(PREVIEW_SIZE[1] * new_scale)),
        )
        self.rect.center = bounds_center + relative_center * ratio
        self._clamp_to_bounds(bounds)
        self.position = self.rect.topleft

    def source_position(self, monitor_position: tuple[int, int]) -> tuple[int, int]:
        local_x = monitor_position[0] - self.rect.x
        local_y = monitor_position[1] - self.rect.y
        return (
            int(local_x * self.source_image.get_width() / self.rect.width),
            int(local_y * self.source_image.get_height() / self.rect.height),
        )

    def evidence_at(self, source_position: tuple[int, int]) -> EvidenceRegion | None:
        for evidence in self.evidence_regions:
            if evidence.rect.collidepoint(source_position):
                return evidence
        return None

    def contains_stamp_target(self, monitor_position: tuple[int, int]) -> bool:
        if self.stamp_target is None or not self.contains_point(monitor_position):
            return False
        return self.stamp_target.collidepoint(self.source_position(monitor_position))

    def contains_signature_target(self, monitor_position: tuple[int, int]) -> bool:
        if self.signature_target is None or not self.contains_point(monitor_position):
            return False
        return self.signature_target.collidepoint(self.source_position(monitor_position))

    def set_visible(self, visible: bool) -> None:
        self.visible = visible
        if not visible:
            self.dragging = False

    def set_evidence_marked(self, evidence_key: str, marked: bool) -> None:
        if marked:
            self.marked_evidence.add(evidence_key)
        else:
            self.marked_evidence.discard(evidence_key)
        self._decorated_cache = None

    def set_stamp_target_active(self, active: bool) -> None:
        if self.stamp_target_active == active:
            return
        self.stamp_target_active = active
        self._decorated_cache = None

    def set_signature_target_active(self, active: bool) -> None:
        if self.signature_target_active == active:
            return
        self.signature_target_active = active
        self._decorated_cache = None

    def sign(self) -> None:
        if self.signature_target is None:
            raise ValueError(f"Document {self.document_id} has no signature target")
        self.is_signed = True
        self.signature_target_active = False
        self._decorated_cache = None

    def place_stamp(self, stamp_id: str, stamp_image: pygame.Surface) -> None:
        if self.stamp_target is None:
            raise ValueError(f"Document {self.document_id} has no stamp target")
        self.applied_stamp_id = stamp_id
        self.applied_stamp_image = stamp_image
        self._decorated_cache = None

    def clear_stamp(self) -> None:
        self.applied_stamp_id = None
        self.applied_stamp_image = None
        self._decorated_cache = None

    def composed_surface(self) -> pygame.Surface:
        if self._decorated_cache is None:
            composed = self.source_image.copy()
            overlay = pygame.Surface(composed.get_size(), pygame.SRCALPHA)
            for evidence in self.evidence_regions:
                if evidence.key in self.marked_evidence:
                    pygame.draw.rect(overlay, HIGHLIGHT_COLOR, evidence.rect)
                    pygame.draw.rect(overlay, (190, 151, 25, 220), evidence.rect, 4)

            if self.stamp_target_active and self.stamp_target is not None:
                pygame.draw.rect(overlay, TARGET_COLOR, self.stamp_target)
                pygame.draw.rect(overlay, (241, 218, 76, 240), self.stamp_target, 6)

            if self.signature_target_active and self.signature_target is not None:
                pygame.draw.rect(overlay, (91, 143, 168, 58), self.signature_target)
                pygame.draw.rect(overlay, (70, 116, 139, 220), self.signature_target, 4)

            composed.blit(overlay, (0, 0))
            self._blit_stamp(composed)
            self._blit_signature(composed)
            self._decorated_cache = composed
        return self._decorated_cache

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
        shadow_rect = self.rect.move(8, 8)
        shadow = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 95))
        surface.blit(shadow, shadow_rect)

        # A mild filtered reduction keeps the document readable without the
        # overly hard pixel edges of the surrounding terminal frame.
        preview = pygame.transform.smoothscale(self.composed_surface(), self.rect.size)
        surface.blit(preview, self.rect)
        self._draw_inspect_button(surface)

    def _blit_stamp(self, surface: pygame.Surface) -> None:
        if self.applied_stamp_image is None or self.stamp_target is None:
            return

        available = self.stamp_target.inflate(-30, -24)
        scale = min(
            available.width / self.applied_stamp_image.get_width(),
            available.height / self.applied_stamp_image.get_height(),
        )
        size = (
            max(1, round(self.applied_stamp_image.get_width() * scale)),
            max(1, round(self.applied_stamp_image.get_height() * scale)),
        )
        stamp = pygame.transform.scale(self.applied_stamp_image, size)
        surface.blit(stamp, stamp.get_rect(center=self.stamp_target.center))

    def _blit_signature(self, surface: pygame.Surface) -> None:
        if not self.is_signed or self.signature_target is None:
            return
        font = pygame.font.SysFont(
            ("Courier New", "Consolas", "monospace"),
            27,
            bold=True,
            italic=True,
        )
        signature = font.render("AUDITOR 04", True, SIGNATURE_COLOR)
        signature = pygame.transform.rotate(signature, 3)
        surface.blit(
            signature,
            (self.signature_target.x + 12, self.signature_target.y + 10),
        )

    def _draw_inspect_button(self, surface: pygame.Surface) -> None:
        rect = self.inspect_button_rect
        pygame.draw.rect(surface, (20, 28, 24), rect)
        pygame.draw.rect(surface, (213, 216, 126), rect, 2)
        center = (rect.x + 16, rect.y + 15)
        pygame.draw.circle(surface, (231, 225, 151), center, 7, 2)
        pygame.draw.line(
            surface,
            (231, 225, 151),
            (center[0] + 5, center[1] + 5),
            (center[0] + 11, center[1] + 11),
            3,
        )

    def _clamp_to_bounds(self, bounds: pygame.Rect) -> None:
        if self.rect.width <= bounds.width:
            self.rect.left = max(bounds.left, min(self.rect.left, bounds.right - self.rect.width))
        else:
            self.rect.centerx = bounds.centerx

        if self.rect.height <= bounds.height:
            self.rect.top = max(bounds.top, min(self.rect.top, bounds.bottom - self.rect.height))
        else:
            self.rect.centery = bounds.centery
