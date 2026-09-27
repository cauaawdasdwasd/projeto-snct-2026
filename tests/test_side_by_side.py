import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.app import Application
from src.gameplay import cases as C
from src.scenes import audit as A
from src.ui import side_by_side as S


def _scene(monkeypatch, case_id):
    app = Application()
    app.scene_manager.switch_to("audit")
    scene = app.scene_manager.current_scene
    case = next(c for c in C.CASE_BANK if c.case_id == case_id)
    monkeypatch.setattr(A, "pick_shift", lambda seen, rng=None, count=5: [case])
    scene.begin_shift(1, False, False)
    scene.story_intro.close()
    scene.case_dialog.mode = None
    return scene


def _click(scene, monitor_pos):
    scene._handle_side_view_click(monitor_pos)


def test_side_by_side_compares_evidence_from_two_papers(monkeypatch) -> None:
    scene = _scene(monkeypatch, "case_11")
    assert len(scene.documents) == 4  # final sheet + three papers
    scene.side_view.open(scene.documents)
    assert scene.side_view.is_open and scene._is_modal_open()
    left_doc = scene.side_view.documents[scene.side_view.picks[0]]
    right_doc = scene.side_view.documents[scene.side_view.picks[1]]
    assert left_doc is not right_doc

    def click_evidence(side, document):
        pane = scene.side_view.pane_rect(side)
        region = document.evidence_regions[0]
        pos = (pane.x + region.rect.centerx * pane.width // 620, pane.y + region.rect.centery * pane.height // 800)
        _click(scene, pos)

    click_evidence(0, left_doc)
    assert scene.comparison_anchor is not None
    click_evidence(1, right_doc)
    assert scene.comparison_result is not None  # two clicks in two different papers = a comparison

    surface = pygame.Surface(A.MONITOR_SCREEN_RECT.size, pygame.SRCALPHA)
    scene.side_view.render(surface)
    scene._render_comparison_card(surface, force=True)


def test_chips_swap_papers_and_close_button(monkeypatch) -> None:
    scene = _scene(monkeypatch, "case_11")
    view = scene.side_view
    view.open(scene.documents)
    left, right = view.picks
    chips = view.chip_rects(0)
    _click(scene, chips[right].center)  # picking what the other side shows swaps them
    assert view.picks == [right, left]
    _click(scene, S.CLOSE_RECT.center)
    assert not view.is_open and not scene._is_modal_open()
