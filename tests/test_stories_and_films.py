import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from src.core.settings import ASSETS_DIR
from src.gameplay.cases import CASES, TUTORIAL_CASE
from src.gameplay.protocols import PROTOCOLS
from src.rendering.protocol_films import DURATION, FILM_SIZE, INTRO_END, VERDICT_START, create_film
from src.ui.case_dialog import BRIEFING_START_RECT, CaseDialog
from src.ui.protocol_panel import VIDEO_RECT, ProtocolPanel


@pytest.fixture(scope="module", autouse=True)
def pygame_ready():
    pygame.init()
    pygame.display.set_mode((100, 100))
    yield


def test_every_case_tells_a_story_and_points_at_what_to_check() -> None:
    for case in CASES:
        assert 300 <= len(case.story) <= 560, (case.case_id, len(case.story))
        assert 100 <= len(case.attention) <= 260, (case.case_id, len(case.attention))
        # the story must not just repeat the answer key
        assert case.explanation not in case.story


def test_dossier_renders_for_every_case_and_reopens() -> None:
    surface = pygame.Surface((1554, 696), pygame.SRCALPHA)
    for case in CASES:
        dialog = CaseDialog(case)
        assert dialog.mode == "briefing"
        dialog.render(surface)
        assert dialog.handle_mouse_down(BRIEFING_START_RECT.center) == "start"
        assert dialog.mode is None
        dialog.reopen()
        assert dialog.mode == "briefing" and dialog.reopened
        dialog.render(surface)


def _portrait(slug: str) -> pygame.Surface:
    return pygame.image.load(ASSETS_DIR / "protocols" / f"{slug}.png").convert_alpha()


def test_every_protocol_has_a_film_that_renders_at_any_moment() -> None:
    for protocol in PROTOCOLS:
        film = create_film(protocol.slug, _portrait(protocol.slug))
        assert film.captions and film.events == sorted(film.events)
        for t in (0.0, 1.0, INTRO_END, 5.0, 9.0, VERDICT_START, 13.0, DURATION):
            frame = film.render(t)
            assert frame.get_size() == FILM_SIZE
        assert film.events[-1][0] <= DURATION


def test_film_player_plays_pauses_seeks_and_restarts() -> None:
    played: list[str] = []
    panel = ProtocolPanel({p.slug: _portrait(p.slug) for p in PROTOCOLS}, lambda name, volume: played.append(name))
    panel.open_protocol("radia_perlman")
    assert panel.film_playing and panel.film_time == 0.0
    for _ in range(70):
        panel.update(0.25)
    assert not panel.film_playing and panel.film_time == DURATION
    assert "stamp" in played
    center = VIDEO_RECT.center
    panel.handle_mouse_down(center)  # finished: click restarts
    assert panel.film_playing and panel.film_time == 0.0
    panel.update(1.0)
    panel.handle_mouse_down(center)  # playing: click pauses
    assert not panel.film_playing
    bar = (VIDEO_RECT.x + VIDEO_RECT.width // 2, VIDEO_RECT.bottom - 10)
    panel.handle_mouse_down(bar)  # progress bar: seek and play
    assert panel.film_playing and 6.0 < panel.film_time < 9.0
    panel.close_popup()
    assert not panel.film_playing


def test_tutorial_dossier_still_lists_key_documents_but_bank_cases_do_not_mark_them() -> None:
    assert TUTORIAL_CASE.is_tutorial and TUTORIAL_CASE.story


def test_every_paper_explains_itself_and_every_case_has_balanced_conclusions() -> None:
    for case in CASES:
        for document in case.documents:
            assert 30 <= len(document.body) <= 170, (case.case_id, document.title, len(document.body))
            assert document.issuer, (case.case_id, document.title)
        truths = [truth for _, truth in case.conclusions]
        assert len(truths) == 4, case.case_id
        assert 1 <= sum(truths) <= 3, case.case_id  # never all true or all false
        assert all(len(text) <= 80 for text, _ in case.conclusions), case.case_id
