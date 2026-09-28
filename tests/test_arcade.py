import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from src.core.assets import AssetManager
from src.core.input_manager import InputManager
from src.core.scene import Scene
from src.core.scene_manager import SceneManager
from src.core.settings import ASSETS_DIR, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from src.minigames.arcade import (
    BASE_TIME_LIMIT,
    RANKS,
    TIME_LIMIT_FLOOR,
    ArcadeRun,
    ArcadeStats,
    KIND_LABELS,
    Leaderboard,
    newly_unlocked_kinds,
    rank_for,
    score_for_solve,
    time_limit_for_wave,
    unlocked_kinds,
)
from src.minigames.captchas import (
    CANVAS,
    CatGridCaptcha,
    ChimpSequenceCaptcha,
    RotateCaptcha,
    SimonBeepCaptcha,
    SwapPuzzleCaptcha,
    TrafficGridCaptcha,
    WhackABotCaptcha,
    WobblyTextCaptcha,
    create_captcha,
)
from src.scenes.arcade import ArcadeScene


@pytest.fixture(scope="module", autouse=True)
def pygame_ready():
    pygame.init()
    pygame.display.set_mode((100, 100))
    yield


def rng(seed: int = 1) -> random.Random:
    return random.Random(seed)


# ---------------------------------------------------------------------------
# New captcha kinds
# ---------------------------------------------------------------------------
def test_traffic_grid_needs_exactly_the_lights() -> None:
    game = TrafficGridCaptcha(rng(22), ASSETS_DIR)
    targets = game.target_indices()
    assert 3 <= len(targets) <= 5
    other = next(i for i in range(9) if i not in targets)
    game.on_mouse_down(game.tile_rect(other).center)
    game.on_mouse_down(TrafficGridCaptcha.VERIFY.center)
    assert game.failures == 1 and not game.solved
    for index in game.target_indices():
        game.on_mouse_down(game.tile_rect(index).center)
    game.on_mouse_down(TrafficGridCaptcha.VERIFY.center)
    assert game.solved


def test_simon_beep_can_be_solved_and_punishes_a_wrong_pad() -> None:
    game = SimonBeepCaptcha(rng(21), ASSETS_DIR)
    while game.phase == "showing":
        game.update(1.0)
    wrong = (game.sequence[0] + 1) % 4
    game.on_mouse_down(game.pads[wrong].center)
    assert game.failures == 1 and not game.solved
    assert game.phase == "wrong" and game.wrong_pad == wrong  # a wrong click pauses with visible feedback...
    game.update(SimonBeepCaptcha.WRONG_PAUSE_SECONDS + 0.1)
    assert game.phase == "showing"  # ...then restarts the sequence from scratch
    guard = 0
    while not game.solved and guard < 100:
        guard += 1
        while game.phase == "showing":
            game.update(1.0)
        expected = game.sequence[game.input_index]
        game.on_mouse_down(game.pads[expected].center)
    assert game.solved


def test_chimp_sequence_can_be_solved_and_punishes_a_wrong_tile() -> None:
    game = ChimpSequenceCaptcha(rng(24), ASSETS_DIR)
    assert game.phase == "showing"
    game.update(ChimpSequenceCaptcha.REVEAL_SECONDS + 0.1)
    assert game.phase == "waiting"
    first_slot = game.positions[0]
    wrong = next(i for i in range(len(game.slots)) if i != first_slot)
    game.on_mouse_down(game.slots[wrong].center)
    assert game.failures == 1 and not game.solved
    assert game.phase == "wrong" and game.wrong_slot == wrong
    game.update(ChimpSequenceCaptcha.WRONG_PAUSE_SECONDS + 0.1)
    assert game.phase == "showing" and game.count == ChimpSequenceCaptcha.START_COUNT

    guard = 0
    while not game.solved and guard < 100:
        guard += 1
        if game.phase == "showing":
            game.update(ChimpSequenceCaptcha.REVEAL_SECONDS + 0.1)
            continue
        expected = game.positions[game.next_expected]
        game.on_mouse_down(game.slots[expected].center)
    assert game.solved


def test_whackabot_rewards_robots_and_punishes_humans() -> None:
    game = WhackABotCaptcha(rng(23), ASSETS_DIR)
    game.active[0] = {"kind": "robot", "life": 5.0, "grow": 1.0}
    game.on_mouse_down(game.slots[0].center)
    assert game.hits == 1 and 0 not in game.active

    game.hits = 4
    game.active[1] = {"kind": "human", "life": 5.0, "grow": 1.0}
    game.on_mouse_down(game.slots[1].center)
    assert game.hits == 2 and game.failures == 1

    game.hits = game.TARGET_HITS - 1
    game.active[2] = {"kind": "robot", "life": 5.0, "grow": 1.0}
    game.on_mouse_down(game.slots[2].center)
    assert game.solved


def test_new_kinds_build_and_render_through_the_factory() -> None:
    surface = pygame.Surface(CANVAS)
    for kind in ("traffic", "simon", "whackabot"):
        game = create_captcha(kind, rng(9), ASSETS_DIR)
        game.render(surface)
        game.update(0.1)
        assert game.instruction


# ---------------------------------------------------------------------------
# Arcade pure logic: pacing, unlocks, ranks, scoring
# ---------------------------------------------------------------------------
def test_time_limit_shrinks_and_floors() -> None:
    limits = [time_limit_for_wave(wave) for wave in range(1, 40)]
    assert limits[0] == BASE_TIME_LIMIT
    assert limits == sorted(limits, reverse=True)
    assert limits[-1] == TIME_LIMIT_FLOOR


def test_wave_unlocks_are_cumulative_and_only_new_at_their_threshold() -> None:
    assert unlocked_kinds(1) == ("wobbly", "cats")
    assert set(unlocked_kinds(2)) == {"wobbly", "cats", "traffic"}
    assert newly_unlocked_kinds(2) == ("traffic",)
    assert newly_unlocked_kinds(5) == ()
    assert set(unlocked_kinds(10)) == set(KIND_LABELS)


def test_rank_progression_reaches_a_ceiling() -> None:
    title, next_at = rank_for(0)
    assert title == RANKS[0][1] and next_at == RANKS[1][0]
    title, next_at = rank_for(RANKS[2][0])
    assert title == RANKS[2][1]
    title, next_at = rank_for(10_000)
    assert title == RANKS[-1][1] and next_at is None


def test_score_rewards_speed_wave_and_combo() -> None:
    slow = score_for_solve(wave=1, time_left=0.0, time_limit=20.0, combo=0)
    fast = score_for_solve(wave=1, time_left=20.0, time_limit=20.0, combo=0)
    assert fast > slow
    low_combo = score_for_solve(wave=1, time_left=10.0, time_limit=20.0, combo=0)
    high_combo = score_for_solve(wave=1, time_left=10.0, time_limit=20.0, combo=5)
    assert high_combo > low_combo
    later_wave = score_for_solve(wave=6, time_left=10.0, time_limit=20.0, combo=0)
    assert later_wave > low_combo


def test_arcade_stats_round_trip(tmp_path) -> None:
    stats = ArcadeStats(best_score=500, best_wave=6, best_combo=8, total_runs=3, total_cleared=42, total_score=1200)
    path = tmp_path / "stats.json"
    stats.save(path)
    assert ArcadeStats.load(path) == stats


def test_arcade_stats_load_missing_file_returns_defaults(tmp_path) -> None:
    assert ArcadeStats.load(tmp_path / "missing.json") == ArcadeStats()


def test_leaderboard_ranks_by_score_and_caps_at_its_size() -> None:
    board = Leaderboard()
    for score in (100, 500, 300, 700, 200):
        board.add(f"P{score}", score, wave=1)
    assert [entry.score for entry in board.entries] == [700, 500, 300, 200, 100]
    assert board.entries[0].name == "P700"


def test_leaderboard_qualifies_until_full_then_only_for_higher_scores() -> None:
    board = Leaderboard()
    assert board.qualifies(1)  # empty board: anything gets in
    for score in range(10):
        board.add(f"P{score}", score, wave=1)
    assert not board.qualifies(-1)
    assert not board.qualifies(0)  # ties with the lowest entry don't bump it
    assert board.qualifies(10)
    rank = board.add("NEW", 10, wave=1)
    assert rank == 0  # highest score so far lands in first place
    assert len(board.entries) == 10  # the old last place fell off


def test_leaderboard_round_trip(tmp_path) -> None:
    board = Leaderboard()
    board.add("ANA", 900, wave=5)
    board.add("BEA", 400, wave=2)
    path = tmp_path / "leaderboard.json"
    board.save(path)
    loaded = Leaderboard.load(path)
    assert [(entry.name, entry.score, entry.wave) for entry in loaded.entries] == [("ANA", 900, 5), ("BEA", 400, 2)]


def test_leaderboard_load_missing_file_returns_empty(tmp_path) -> None:
    assert Leaderboard.load(tmp_path / "missing.json").entries == []


def test_leaderboard_add_falls_back_to_anonimo_for_blank_names() -> None:
    board = Leaderboard()
    board.add("   ", 50, wave=1)
    assert board.entries[0].name == "ANÔNIMO"


# ---------------------------------------------------------------------------
# ArcadeRun: the actual gauntlet loop
# ---------------------------------------------------------------------------
def _solve_current(run: ArcadeRun) -> None:
    captcha = run.captcha
    if isinstance(captcha, WobblyTextCaptcha):
        for char in captcha.text:
            captcha.on_key(pygame.event.Event(pygame.KEYDOWN, key=ord(char.lower()), unicode=char.lower()))
        captcha.on_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""))
    elif isinstance(captcha, CatGridCaptcha):
        for index in captcha.cat_indices():
            captcha.on_mouse_down(captcha.tile_rect(index).center)
        captcha.on_mouse_down(CatGridCaptcha.VERIFY.center)
    elif isinstance(captcha, TrafficGridCaptcha):
        for index in captcha.target_indices():
            captcha.on_mouse_down(captcha.tile_rect(index).center)
        captcha.on_mouse_down(TrafficGridCaptcha.VERIFY.center)
    elif isinstance(captcha, RotateCaptcha):
        captcha.angle = 0
        captcha.on_mouse_down(RotateCaptcha.VERIFY.center)
    elif isinstance(captcha, SimonBeepCaptcha):
        while not captcha.solved:
            while captcha.phase == "showing":
                captcha.update(1.0)
            expected = captcha.sequence[captcha.input_index]
            captcha.on_mouse_down(captcha.pads[expected].center)
    elif isinstance(captcha, SwapPuzzleCaptcha):
        for slot in range(len(captcha.slots)):
            target = captcha.slots.index(slot)
            if target != slot:
                captcha.on_mouse_down(captcha.slot_rect(slot).center)
                captcha.on_mouse_down(captcha.slot_rect(target).center)
    elif isinstance(captcha, ChimpSequenceCaptcha):
        guard = 0
        while not captcha.solved and guard < 100:
            guard += 1
            if captcha.phase == "showing":
                captcha.update(ChimpSequenceCaptcha.REVEAL_SECONDS + 0.1)
                continue
            expected = captcha.positions[captcha.next_expected]
            captcha.on_mouse_down(captcha.slots[expected].center)
    else:
        raise AssertionError(f"no test solver wired up for {type(captcha).__name__}")


def _fast_forward_past_pause(run: ArcadeRun) -> None:
    while run.phase != "active" and not run.game_over:
        run.update(run.phase_timer + 0.01)
        run.pop_events()


def test_arcade_run_scores_advances_waves_and_fires_unlocks() -> None:
    stats = ArcadeStats()
    run = ArcadeRun(ASSETS_DIR, stats, random.Random(42))
    unlocked_seen: list[str] = []
    guard = 0
    while run.wave < 5 and guard < 200:
        guard += 1
        _solve_current(run)
        run.update(0.001)
        for event in run.pop_events():
            if event.kind == "unlock":
                unlocked_seen.append(str(event.value))
        _fast_forward_past_pause(run)
        assert not run.game_over
    assert run.wave >= 5
    assert run.score > 0
    assert run.combo >= 1
    assert "traffic" in unlocked_seen
    assert "puzzle" in unlocked_seen


def test_arcade_run_ends_after_losing_all_lives_and_persists_stats() -> None:
    stats = ArcadeStats()
    run = ArcadeRun(ASSETS_DIR, stats, random.Random(3))
    saved = {"called": False}

    def fake_save(path=None) -> None:
        saved["called"] = True

    run.stats.save = fake_save  # avoid touching the real data/ directory in tests

    guard = 0
    while not run.game_over and guard < 50:
        guard += 1
        if run.phase == "active":
            run.update(run.time_limit + 1.0)
        else:
            run.update(run.phase_timer + 0.01)
        run.pop_events()

    assert run.game_over and run.lives == 0
    assert saved["called"]
    assert stats.total_runs == 1
    assert stats.total_score == run.score
    assert run.summary is not None and run.summary.wave == run.wave


# ---------------------------------------------------------------------------
# ArcadeScene: exercise the whole render pipeline for crashes
# ---------------------------------------------------------------------------
class _DummyScene(Scene):
    def handle_event(self, event: pygame.event.Event) -> None:
        return None

    def update(self, dt: float) -> None:
        return None

    def render(self, surface: pygame.Surface) -> None:
        return None


def _make_scene() -> ArcadeScene:
    manager = SceneManager()
    manager.add_scene("main_menu", _DummyScene(manager, None, None))
    assets = AssetManager(ASSETS_DIR)
    input_manager = InputManager((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    scene = ArcadeScene(manager, assets, input_manager, audio=None)
    manager.add_scene("arcade", scene)
    return scene


def test_arcade_scene_runs_a_full_lifecycle_without_crashing() -> None:
    scene = _make_scene()
    surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    scene.on_enter()
    scene.update(0.016)
    scene.render(surface)
    assert scene.view == "briefing"

    scene._start_run()
    assert scene.view == "playing" and scene.run is not None
    scene.run.stats.save = lambda path=None: None  # avoid touching the real data/ directory in tests
    scene.leaderboard.save = lambda path=None: None
    for _ in range(5):
        scene.update(0.016)
        scene.render(surface)

    _solve_current(scene.run)
    scene.update(0.016)
    scene.render(surface)
    while scene.run.phase != "active" and not scene.run.game_over:
        scene.update(scene.run.phase_timer + 0.05)
        scene.render(surface)

    scene.handle_escape()
    assert scene.paused
    scene.render(surface)
    scene.handle_escape()
    assert not scene.paused

    guard = 0
    while not scene.run.game_over and guard < 60:
        guard += 1
        if scene.run.phase == "active":
            scene.update(scene.run.time_limit + 1.0)
        else:
            scene.update(scene.run.phase_timer + 0.05)
        scene.render(surface)

    assert scene.view == "gameover"
    if scene.gameover_phase == "name_entry":  # an empty leaderboard always qualifies
        scene._confirm_name_entry()
        assert scene.gameover_phase == "summary"
    scene.render(surface)
    scene._start_run()
    assert scene.view == "playing"
    scene.render(surface)


def test_arcade_scene_reacts_to_real_click_events() -> None:
    """Exercises the actual event-dispatch path (input_manager -> scene.handle_event),
    not just the direct state-mutating helpers used by the lifecycle test above."""
    scene = _make_scene()
    input_manager = scene.input_manager

    def click(pos: tuple[int, int]) -> None:
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1)
        input_manager.handle_event(event)
        scene.handle_event(event)

    scene.on_enter()
    click(scene.start_rect.center)
    assert scene.view == "playing" and scene.run is not None
    scene.run.stats.save = lambda path=None: None  # avoid touching the real data/ directory in tests
    scene.leaderboard.save = lambda path=None: None

    scene.handle_escape()
    assert scene.paused
    click(scene.pause_rects[1].center)  # REINICIAR
    assert not scene.paused and scene.run is not None and not scene.run.game_over

    surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    guard = 0
    while not scene.run.game_over and guard < 60:
        guard += 1
        if scene.run.phase == "active":
            scene.update(scene.run.time_limit + 1.0)
        else:
            scene.update(scene.run.phase_timer + 0.05)
        scene.render(surface)
    assert scene.view == "gameover"

    if scene.gameover_phase == "name_entry":  # an empty leaderboard always qualifies
        click(scene.name_confirm_rect.center)
        assert scene.gameover_phase == "summary"

    click(scene.retry_rect.center)
    assert scene.view == "playing" and scene.run is not None and not scene.run.game_over
