import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from src.core.settings import ASSETS_DIR
from src.minigames.captchas import (
    CANVAS,
    TIERS,
    CatGridCaptcha,
    InvadersCaptcha,
    MemoryCaptcha,
    RotateCaptcha,
    SwapPuzzleCaptcha,
    WobblyTextCaptcha,
    create_captcha,
)
from src.minigames.director import ComplicationDirector, case_time_limit
from src.minigames.popups import MAX_POPUPS, PopupSwarm
from src.minigames.verify9 import MOODS, Verify9
from src.ui.captcha_overlay import CANVAS_ORIGIN, SKIP_AFTER_SECONDS, SKIP_RECT, CaptchaOverlay


@pytest.fixture(scope="module", autouse=True)
def pygame_ready():
    pygame.init()
    pygame.display.set_mode((100, 100))
    yield


def rng(seed: int = 1) -> random.Random:
    return random.Random(seed)


def overlay_point(local):
    return (CANVAS_ORIGIN[0] + local[0], CANVAS_ORIGIN[1] + local[1])


def test_wobbly_text_accepts_the_right_answer_and_punishes_a_wrong_one() -> None:
    game = WobblyTextCaptcha(rng(), ASSETS_DIR)
    game.entry = "XXXXX" if game.text != "XXXXX" else "YYYYY"
    game.on_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""))
    assert not game.solved and game.failures == 1 and "error" in game.take_events()
    assert len(game.text) == 5
    for char in game.text:
        game.on_key(pygame.event.Event(pygame.KEYDOWN, key=ord(char.lower()), unicode=char.lower()))
    game.on_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""))
    assert game.solved
    assert game.image.get_size() == (520, 130)


def test_cat_grid_needs_exactly_the_cats() -> None:
    game = CatGridCaptcha(rng(2), ASSETS_DIR)
    cats = game.cat_indices()
    assert 3 <= len(cats) <= 5
    game.on_mouse_down(game.tile_rect(next(i for i in range(9) if i not in cats)).center)
    game.on_mouse_down(CatGridCaptcha.VERIFY.center)
    assert game.failures == 1 and not game.solved
    for index in game.cat_indices():
        game.on_mouse_down(game.tile_rect(index).center)
    game.on_mouse_down(CatGridCaptcha.VERIFY.center)
    assert game.solved


def test_rotate_captcha_needs_an_upright_photo() -> None:
    game = RotateCaptcha(rng(3), ASSETS_DIR)
    assert not game.upright()
    game.on_mouse_down(RotateCaptcha.VERIFY.center)
    assert game.failures == 1
    game.angle = 5
    assert game.upright()
    game.on_mouse_down(RotateCaptcha.VERIFY.center)
    assert game.solved
    other = RotateCaptcha(rng(4), ASSETS_DIR)
    before = other.angle
    other.on_mouse_down(RotateCaptcha.RIGHT.center)
    assert other.angle == before + 15


@pytest.mark.parametrize("columns,rows", [(3, 2), (3, 3)])
def test_swap_puzzle_can_be_solved_with_swaps(columns, rows) -> None:
    game = SwapPuzzleCaptcha(rng(5), ASSETS_DIR, columns, rows)
    assert not game.is_complete()
    for slot in range(len(game.slots)):
        target = game.slots.index(slot)
        if target != slot:
            game.on_mouse_down(game.slot_rect(slot).center)
            game.on_mouse_down(game.slot_rect(target).center)
    assert game.is_complete() and game.solved


@pytest.mark.parametrize("pairs", [4, 6])
def test_memory_pairs(pairs) -> None:
    game = MemoryCaptcha(rng(6), ASSETS_DIR, pairs)
    first = 0
    wrong = next(i for i in range(len(game.cards)) if game.cards[i] != game.cards[first])
    game.on_mouse_down(game.card_rect(first).center)
    game.on_mouse_down(game.card_rect(wrong).center)
    assert game.wait > 0 and not game.matched
    game.on_mouse_down(game.card_rect(1).center)  # ignored while the wrong pair is showing
    game.update(1.0)
    assert not game.up
    for value in range(pairs):
        for index in [i for i, card in enumerate(game.cards) if card == value]:
            game.on_mouse_down(game.card_rect(index).center)
    assert game.solved


def test_invaders_can_be_won_and_lost() -> None:
    game = InvadersCaptcha(rng(7), ASSETS_DIR)
    for _ in range(6000):
        if game.solved:
            break
        target = max(game.enemies, key=lambda e: e["pos"].y)["pos"].x + 23
        game.on_mouse_move((int(target), 300))
        game.update(1 / 60)
        game.on_mouse_down((0, 0))
    assert game.solved and not game.enemies
    lost = InvadersCaptcha(rng(8), ASSETS_DIR)
    for _ in range(4000):
        lost.update(1 / 30)
        if lost.failures:
            break
    assert lost.failures == 1 and len(lost.enemies) == 15 and not lost.solved


def test_every_tier_builds_and_renders() -> None:
    surface = pygame.Surface(CANVAS)
    for kinds in TIERS.values():
        for kind in kinds:
            game = create_captcha(kind, rng(9), ASSETS_DIR)
            game.render(surface)
            game.update(0.1)
            assert game.instruction


def test_popups_close_decoys_multiply_and_are_capped() -> None:
    swarm = PopupSwarm(pygame.Rect(300, 100, 800, 500), rng(10))
    swarm.spawn(4)
    assert swarm.active == 4
    popup = swarm.popups[-1]
    assert swarm.handle_mouse_down(popup.close_rect.center) == "close"
    assert swarm.active == 3
    decoy = swarm.popups[0]
    decoy.decoy = True
    decoy.rect.topleft = (300, 100)
    for other in swarm.popups[1:]:
        other.rect.topleft = (900, 500)
    before = swarm.active
    assert swarm.handle_mouse_down(decoy.decoy_rect.center) == "decoy"
    assert swarm.active == before + 2
    swarm.spawn(50)
    assert swarm.active == MAX_POPUPS
    swarm.clear()
    assert swarm.active == 0 and swarm.handle_mouse_down((5, 5)) is None


def test_runaway_close_button_hops_away_from_the_cursor() -> None:
    swarm = PopupSwarm(pygame.Rect(300, 100, 800, 500), rng(11))
    swarm.spawn(1, decoys=False)
    popup = swarm.popups[0]
    popup.runaway, popup.corner = True, 0
    swarm.handle_mouse_move(popup.close_rect.center)
    assert popup.corner != 0 and popup.hops == 1


def test_director_plans_more_trouble_for_harder_cases() -> None:
    limits = [case_time_limit(turn) for turn in range(1, 6)]
    assert limits == sorted(limits) and 200 <= limits[0] and limits[-1] <= 290
    director = ComplicationDirector(rng(12))
    counts = []
    for turn in range(1, 6):
        plan = director.plan(case_time_limit(turn), turn)
        counts.append(len([event for event in plan if event.kind == "captcha"]))
        assert [e.at for e in plan] == sorted(e.at for e in plan)
        assert plan[-1].kind == "captcha" and plan[-1].at < case_time_limit(turn)
        assert plan[0].at > 0
    assert counts == [2, 3, 3, 4, 4]
    kinds = {director.pick_captcha("easy") for _ in range(30)}
    assert kinds <= set(TIERS["easy"]) and len(kinds) > 1


def test_overlay_reports_solves_penalties_and_skip() -> None:
    overlay = CaptchaOverlay(Verify9(ASSETS_DIR))
    game = RotateCaptcha(rng(13), ASSETS_DIR)
    overlay.open(game, 1)
    game.angle = 90
    overlay.handle_mouse_down(overlay_point(RotateCaptcha.VERIFY.center))
    overlay.update(0.1)
    events = overlay.pop_events()
    assert ("penalty", None) in events and overlay.failures == 1
    assert not overlay.can_skip
    overlay.update(SKIP_AFTER_SECONDS)
    assert overlay.can_skip
    overlay.handle_mouse_down(SKIP_RECT.center)
    assert ("skipped", None) in overlay.pop_events() and not overlay.is_open

    game = RotateCaptcha(rng(14), ASSETS_DIR)
    overlay.open(game, 2)
    game.angle = 0
    overlay.handle_mouse_down(overlay_point(RotateCaptcha.VERIFY.center))
    overlay.update(0.1)
    assert overlay.celebration > 0
    overlay.update(2.0)
    kinds = [name for name, _ in overlay.pop_events()]
    assert "solved" in kinds and not overlay.is_open


def test_verify9_draws_every_mood_without_art() -> None:
    surface = pygame.Surface((120, 120))
    avatar = Verify9(ASSETS_DIR)
    for mood in MOODS:
        avatar.draw(surface, (60, 60), 100, mood, 1.0)


def test_popups_can_be_dragged_like_windows() -> None:
    swarm = PopupSwarm(pygame.Rect(300, 100, 800, 500), rng(12), limits=pygame.Rect(0, 0, 1554, 696))
    swarm.spawn(1, decoys=False)
    popup = swarm.popups[0]
    popup.runaway = False
    grab = (popup.rect.x + 60, popup.rect.y + 12)  # the title bar, far from the X
    assert swarm.handle_mouse_down(grab) == "consume" and swarm.dragging
    swarm.handle_mouse_move((grab[0] + 100, grab[1] + 50))
    assert popup.rect.topleft == (grab[0] + 100 - 60, grab[1] + 50 - 12)
    swarm.handle_mouse_up()
    swarm.handle_mouse_move((0, 0))
    assert not swarm.dragging and popup.rect.x > 0  # dropped: it no longer follows the mouse
    swarm.handle_mouse_down(popup.rect.center)
    swarm.handle_mouse_move((-500, -500))
    assert swarm.limits.contains(popup.rect)  # cannot be thrown off the screen


def test_every_popup_has_an_icon_and_short_lines() -> None:
    from src.minigames.popups import CONTENT, draw_icon

    for title, lines, _accent, icon in CONTENT:
        assert len(lines) <= 3 and all(len(line) <= 30 for line in lines), title
        assert draw_icon(icon, 64).get_bounding_rect().width > 10, icon
