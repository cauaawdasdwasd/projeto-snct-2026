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
    BOSS_CAPTCHAS,
    CAPTCHAS_PER_WAVE,
    FINAL_WAVE,
    RANKS,
    TIME_LIMIT_FLOOR,
    ArcadeRun,
    ArcadeStats,
    KIND_LABELS,
    Leaderboard,
    newly_unlocked_kinds,
    rank_for,
    score_for_solve,
    time_limit_for,
    time_limit_for_wave,
    unlocked_kinds,
)
from src.minigames.captchas import (
    CANVAS,
    CatGridCaptcha,
    ChimpSequenceCaptcha,
    HoldReleaseCaptcha,
    InstrumentsCaptcha,
    InvadersCaptcha,
    MazeCaptcha,
    MemoryCaptcha,
    RadioCaptcha,
    RotateCaptcha,
    SimonBeepCaptcha,
    SwapPuzzleCaptcha,
    TermoCaptcha,
    TrafficGridCaptcha,
    VaultCaptcha,
    WhackABotCaptcha,
    WireCutCaptcha,
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


def test_wire_cut_follows_the_generated_rule_and_resets_on_a_wrong_cut() -> None:
    game = WireCutCaptcha(rng(30), ASSETS_DIR)
    wrong = next(i for i in range(game.WIRE_COUNT) if i != game.correct_index)
    game.on_mouse_down(game.wire_rect(wrong).center)
    assert game.failures == 1 and not game.solved
    assert game.phase == "wrong" and game.round == 0
    game.update(WireCutCaptcha.WRONG_PAUSE_SECONDS + 0.1)
    assert game.phase == "active"  # a fresh wire set and rule, ready to try again

    guard = 0
    while not game.solved and guard < 100:
        guard += 1
        game.on_mouse_down(game.wire_rect(game.correct_index).center)
        if game.phase == "right":
            game.update(WireCutCaptcha.RIGHT_PAUSE_SECONDS + 0.1)
    assert game.solved


def test_wire_condition_helpers_evaluate_correctly() -> None:
    from src.minigames.captchas import (
        _wire_digit_sum_even,
        _wire_has_vowel,
        _wire_last_digit_odd,
        _wire_more_letters_than_digits,
    )

    assert _wire_last_digit_odd("A1B2C3") is True
    assert _wire_last_digit_odd("A1B2C4") is False
    assert _wire_last_digit_odd("ABCDEF") is False  # no digits at all: never odd

    assert _wire_digit_sum_even("A1B2C3") is True  # 1+2+3 = 6
    assert _wire_digit_sum_even("A1B2C4") is False  # 1+2+4 = 7

    assert _wire_has_vowel("BCDFGH") is False
    assert _wire_has_vowel("BCDAGH") is True

    assert _wire_more_letters_than_digits("AABBC1") is True  # 5 letters, 1 digit
    assert _wire_more_letters_than_digits("A11122") is False  # 1 letter, 5 digits


def test_wire_generate_code_always_has_at_least_one_digit() -> None:
    from src.minigames.captchas import WIRE_CODE_DIGITS, _wire_generate_code

    generator = rng(40)
    for _ in range(200):
        code = _wire_generate_code(generator)
        assert len(code) == 6
        assert any(c in WIRE_CODE_DIGITS for c in code)


def test_wire_cut_rule_always_points_at_exactly_one_wire() -> None:
    # Regenerate many times to make sure the rule always resolves to exactly one wire,
    # whatever colors and code happen to be drawn (the part most likely to break under editing).
    game = WireCutCaptcha(rng(31), ASSETS_DIR)
    for _ in range(200):
        game._deal()
        target_color = game.wires[game.correct_index][0]
        occurrences = [i for i, (name, _) in enumerate(game.wires) if name == target_color]
        assert occurrences == [game.correct_index]  # that color appears exactly once
        assert game.code in game.rule_text
        assert target_color in game.rule_text


def _type_termo_letters(game: TermoCaptcha, word: str) -> None:
    for char in word:
        game.on_key(pygame.event.Event(pygame.KEYDOWN, key=ord(char.lower()), unicode=char.lower()))


def _type_termo_word(game: TermoCaptcha, word: str) -> None:
    _type_termo_letters(game, word)
    game.on_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""))


def _press(game: TermoCaptcha, key: int) -> None:
    game.on_key(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=""))


def test_score_termo_guess_handles_duplicate_letters_correctly() -> None:
    from src.minigames.captchas import _score_termo_guess

    # "O" appears once in the target: only the correctly-placed guess letter should
    # score, the other duplicate must not also claim a "present" — the classic
    # Wordle scoring bug this function has to get right.
    assert _score_termo_guess("ROBOS", "BOLHA") == ["absent", "correct", "present", "absent", "absent"]
    assert _score_termo_guess("DADOS", "DADOS") == ["correct"] * 5
    assert _score_termo_guess("SSSSS", "DADOS") == ["absent", "absent", "absent", "absent", "correct"]


def test_termo_word_bank_is_well_formed() -> None:
    from src.minigames.captchas import TERMO_WORDS

    assert len(TERMO_WORDS) >= 30
    assert len(set(TERMO_WORDS)) == len(TERMO_WORDS)  # no accidental duplicates
    for word in TERMO_WORDS:
        assert len(word) == 5 and word.isalpha() and word == word.upper()


def test_termo_can_be_solved_by_typing_the_target_word() -> None:
    game = TermoCaptcha(rng(32), ASSETS_DIR)
    _type_termo_word(game, game.target)
    assert game.phase == "right" and game.guesses == [game.target]
    game.update(TermoCaptcha.RIGHT_PAUSE_SECONDS + 0.1)
    assert game.solved


def test_termo_arrow_keys_move_the_cursor_to_fix_a_letter() -> None:
    game = TermoCaptcha(rng(34), ASSETS_DIR)
    wrong_middle = next(c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if c != game.target[2])
    almost = game.target[:2] + wrong_middle + game.target[3:]

    _type_termo_letters(game, almost)
    assert "".join(game.current_letters) == almost
    assert game.cursor == TermoCaptcha.WORD_LENGTH - 1  # typing alone never needs the arrows

    _press(game, pygame.K_LEFT)
    _press(game, pygame.K_LEFT)
    assert game.cursor == 2  # moved back two slots without touching any letter
    assert game.current_letters[2] == wrong_middle

    _type_termo_letters(game, game.target[2])  # retype just the wrong slot
    assert game.current_letters[2] == game.target[2]
    assert game.cursor == 3  # typing always auto-advances the cursor

    _press(game, pygame.K_LEFT)
    assert game.cursor == 2
    _press(game, pygame.K_RIGHT)  # can also move forward again
    assert game.cursor == 3

    _press(game, pygame.K_RETURN)
    assert game.guesses == [game.target] and game.phase == "right"


def test_termo_fails_and_deals_a_new_word_once_out_of_guesses() -> None:
    from src.minigames.captchas import TERMO_WORDS

    game = TermoCaptcha(rng(33), ASSETS_DIR)
    wrong = next(word for word in TERMO_WORDS if word != game.target)
    for _ in range(TermoCaptcha.MAX_GUESSES):
        _type_termo_word(game, wrong)
    assert game.phase == "wrong" and game.failures == 1 and not game.solved
    game.update(TermoCaptcha.WRONG_PAUSE_SECONDS + 0.1)
    assert game.phase == "active" and not game.guesses  # a fresh word, ready to try again


def test_score_vault_guess_reports_correct_present_and_absent_per_position() -> None:
    # Same per-slot feedback as the letter Termo now, not an aggregate peg count: the
    # player can see WHICH digit is right and WHICH is just misplaced, like the request.
    from src.minigames.captchas import _score_vault_guess

    assert _score_vault_guess("1234", "1234") == ["correct"] * 4
    assert _score_vault_guess("4321", "1234") == ["present"] * 4  # every digit present, none in place
    assert _score_vault_guess("1256", "1234") == ["correct", "correct", "absent", "absent"]
    # code has only one '1': the exact match at position 0 already claims it, so the
    # second, repeated '1' in the guess can't also score as "present" for digit '1'.
    assert _score_vault_guess("1123", "1234") == ["correct", "absent", "present", "present"]


def test_vault_can_be_cracked_by_typing_the_code() -> None:
    game = VaultCaptcha(rng(35), ASSETS_DIR)
    for digit in game.code:
        game.on_key(pygame.event.Event(pygame.KEYDOWN, key=ord(digit), unicode=digit))
    game.on_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""))
    assert game.guesses == [game.code] and game.results[0] == ["correct"] * 4 and game.phase == "right"
    game.update(VaultCaptcha.RIGHT_PAUSE_SECONDS + 0.1)
    assert game.solved


def test_vault_numpad_clicks_also_work_and_it_locks_out_after_nine_attempts() -> None:
    from src.minigames.captchas import VAULT_NUMPAD

    game = VaultCaptcha(rng(36), ASSETS_DIR)
    wrong_digit = next(d for d in "0123456789" if d not in game.code)
    wrong_guess = wrong_digit * VaultCaptcha.CODE_LENGTH
    label_to_pos = {label: (row, column) for row, labels in enumerate(VAULT_NUMPAD) for column, label in enumerate(labels)}

    def click_guess(guess: str) -> None:
        for digit in guess:
            row, column = label_to_pos[digit]
            game.on_mouse_down(game._numpad_rect(row, column).center)
        ok_row, ok_column = label_to_pos["OK"]
        game.on_mouse_down(game._numpad_rect(ok_row, ok_column).center)

    for _ in range(VaultCaptcha.MAX_ATTEMPTS):
        click_guess(wrong_guess)
    assert len(game.guesses) == VaultCaptcha.MAX_ATTEMPTS and game.phase == "wrong" and game.failures == 1
    game.update(VaultCaptcha.WRONG_PAUSE_SECONDS + 0.1)
    assert game.phase == "active" and not game.guesses  # fresh code, ready to try again


def test_hold_release_rewards_holding_long_enough_and_releasing_on_the_rule() -> None:
    game = HoldReleaseCaptcha(rng(37), ASSETS_DIR)
    game.on_mouse_down(game.BUTTON_CENTER)
    assert game.phase == "holding"

    game.on_mouse_up(game.BUTTON_CENTER)  # released instantly: never reached MIN_HOLD_SECONDS
    assert game.phase == "wrong" and game.failures == 1
    game.update(HoldReleaseCaptcha.WRONG_PAUSE_SECONDS + 0.1)
    assert game.phase == "idle" and game.round == 0

    guard = 0
    while not game.solved and guard < 500:
        guard += 1
        game.on_mouse_down(game.BUTTON_CENTER)
        waited = 0.0
        while waited < 6.0 and not (game.hold_time >= game.MIN_HOLD_SECONDS and game.rule_check(game.digit)):
            game.update(0.05)
            waited += 0.05
        assert waited < 6.0  # the rule must actually become satisfiable within a few ticks
        game.on_mouse_up(game.BUTTON_CENTER)
        if game.phase in ("right", "wrong"):
            pause = game.RIGHT_PAUSE_SECONDS if game.phase == "right" else game.WRONG_PAUSE_SECONDS
            game.update(pause + 0.1)
    assert game.solved


def test_hold_release_never_redraws_the_same_digit_twice_in_a_row() -> None:
    # Regression: a naive `randrange(10)` redraw can repeat the previous digit, which
    # makes that one visibly "linger" for two DIGIT_STEP_SECONDS instead of one while
    # every other digit still only gets one step - the "alguns números saem mais rápido
    # que outros" bug. Every step must land on a genuinely different digit.
    game = HoldReleaseCaptcha(rng(41), ASSETS_DIR)
    game.on_mouse_down(game.BUTTON_CENTER)
    previous = game.digit
    for _ in range(300):
        game.update(HoldReleaseCaptcha.DIGIT_STEP_SECONDS + 0.01)
        assert game.digit != previous
        previous = game.digit


def test_maze_generates_a_solvable_path_to_a_distinct_goal() -> None:
    game = MazeCaptcha(rng(38), ASSETS_DIR)
    assert game.goal != game.player  # the farthest cell is never the start itself
    _solve_maze(game)
    assert game.player == game.goal and game.solved


def test_maze_ignores_moves_that_would_cross_a_wall() -> None:
    game = MazeCaptcha(rng(39), ASSETS_DIR)
    start = game.player
    for key in (pygame.K_UP, pygame.K_LEFT):  # off the top-left corner: at least one must be blocked
        game.on_key(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=""))
    assert 0 <= game.player[0] < game.COLUMNS and 0 <= game.player[1] < game.ROWS
    assert game.player != (start[0] - 1, start[1] - 1)  # never both moves at once


def test_instruments_wins_once_both_gauges_hold_inside_the_safe_band() -> None:
    game = InstrumentsCaptcha(rng(42), ASSETS_DIR)
    game.JERK = 0.0  # freeze drift so the test can put the needles exactly on target
    game.velocity = [0.0, 0.0]
    guard = 0
    while not game.solved and guard < 200:
        guard += 1
        game.gauges = list(game.targets)
        game.update(0.1)
    assert game.solved


def test_instruments_resets_the_hold_timer_once_a_gauge_drifts_out_of_band() -> None:
    game = InstrumentsCaptcha(rng(45), ASSETS_DIR)
    game.JERK = 0.0
    game.velocity = [0.0, 0.0]
    game.gauges = list(game.targets)
    game.update(0.1)
    assert game.hold_timer > 0  # both gauges are dead-on: the hold starts counting

    game.gauges[0] = game.GAUGE_MIN if game.targets[0] > 50 else game.GAUGE_MAX  # yank one gauge far out of band
    game.update(0.1)
    assert game.hold_timer == 0 and not game.solved


def _press_radio_code(game: RadioCaptcha, code: str) -> None:
    for char in code:
        game.on_key(pygame.event.Event(pygame.KEYDOWN, key=ord(char.lower()), unicode=char.lower()))
    game.on_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""))


def test_radio_decodes_the_phonetic_alphabet_into_the_matching_code() -> None:
    from src.minigames.captchas import NATO_ALPHABET

    game = RadioCaptcha(rng(43), ASSETS_DIR)
    assert game.words == [NATO_ALPHABET[char] for char in game.code]

    guard = 0
    while not game.solved and guard < 20:
        guard += 1
        _press_radio_code(game, game.code)
        if game.phase in ("right", "wrong"):
            pause = RadioCaptcha.RIGHT_PAUSE_SECONDS if game.phase == "right" else RadioCaptcha.WRONG_PAUSE_SECONDS
            game.update(pause + 0.1)
    assert game.solved


def test_radio_resets_the_round_count_on_a_wrong_callsign() -> None:
    game = RadioCaptcha(rng(44), ASSETS_DIR)
    _press_radio_code(game, game.code)
    game.update(RadioCaptcha.RIGHT_PAUSE_SECONDS + 0.1)
    assert game.round == 1

    wrong_code = "".join("0" if char != "0" else "1" for char in game.code)
    _press_radio_code(game, wrong_code)
    assert game.phase == "wrong" and game.failures == 1
    game.update(RadioCaptcha.WRONG_PAUSE_SECONDS + 0.1)
    assert game.round == 0 and game.phase == "active"


def test_new_kinds_build_and_render_through_the_factory() -> None:
    surface = pygame.Surface(CANVAS)
    for kind in (
        "traffic", "simon", "whackabot", "chimp", "wires", "termo", "cofre", "botao",
        "labirinto", "instrumentos", "radio",
    ):
        game = create_captcha(kind, rng(9), ASSETS_DIR)
        game.render(surface)
        game.update(0.1)
        assert game.instruction


# ---------------------------------------------------------------------------
# Arcade pure logic: pacing, unlocks, ranks, scoring
# ---------------------------------------------------------------------------
def test_time_limit_keeps_easing_toward_the_floor_across_the_whole_run() -> None:
    limits = [time_limit_for_wave(wave) for wave in range(1, FINAL_WAVE + 1)]
    assert limits[0] == BASE_TIME_LIMIT
    assert limits == sorted(limits, reverse=True)
    # never actually flatlines...
    assert all(limit > TIME_LIMIT_FLOOR for limit in limits)
    # ...but by the boss wave it's close to the floor
    assert limits[-1] - TIME_LIMIT_FLOOR < 2.0
    # and the squeeze is felt within this short campaign, not spread so thin across it
    # that a player never perceives the clock actually shrinking
    assert limits[1] - limits[6] > 5.0


def test_slower_verifications_get_more_time_than_the_wave_baseline() -> None:
    for wave in (1, 7, FINAL_WAVE):
        baseline = time_limit_for_wave(wave)
        assert time_limit_for(wave, "wobbly") == pytest.approx(baseline)
        assert time_limit_for(wave, "termo") == pytest.approx(baseline * 3.2)
        assert time_limit_for(wave, "cofre") == pytest.approx(baseline * 2.6)
        assert time_limit_for(wave, "wires") == pytest.approx(baseline * 1.8)
        assert time_limit_for(wave, "radio") == pytest.approx(baseline * 1.7)
        assert time_limit_for(wave, "instrumentos") == pytest.approx(baseline * 1.6)
        assert time_limit_for(wave, "labirinto") == pytest.approx(baseline * 1.4)
        # ordered by how much deduction/typing/navigating each one actually demands
        assert (
            time_limit_for(wave, "termo")
            > time_limit_for(wave, "cofre")
            > time_limit_for(wave, "wires")
            > time_limit_for(wave, "radio")
            > time_limit_for(wave, "instrumentos")
            > time_limit_for(wave, "labirinto")
            > baseline
        )


def test_wave_unlocks_are_cumulative_and_only_new_at_their_threshold() -> None:
    assert unlocked_kinds(1) == ("wobbly", "cats")
    assert set(unlocked_kinds(2)) == {"wobbly", "cats", "traffic"}
    assert newly_unlocked_kinds(2) == ("traffic",)
    assert newly_unlocked_kinds(FINAL_WAVE) == ()  # the boss fight adds no new kind, just raises the stakes
    assert set(unlocked_kinds(FINAL_WAVE - 1)) == set(KIND_LABELS)  # everything is unlocked before the boss


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
def _solve_maze(captcha: MazeCaptcha) -> None:
    """BFS the shortest path from wherever the token currently is to the goal, then
    feed the matching arrow-key presses."""
    from collections import deque as _deque

    key_by_delta = {(0, -1): pygame.K_UP, (0, 1): pygame.K_DOWN, (-1, 0): pygame.K_LEFT, (1, 0): pygame.K_RIGHT}
    start = captcha.player
    parent: dict[tuple[int, int], tuple[tuple[int, int], int] | None] = {start: None}
    queue = _deque([start])
    while queue:
        cell = queue.popleft()
        if cell == captcha.goal:
            break
        for (dx, dy), key in key_by_delta.items():
            neighbor = (cell[0] + dx, cell[1] + dy)
            if (
                0 <= neighbor[0] < captcha.COLUMNS
                and 0 <= neighbor[1] < captcha.ROWS
                and neighbor not in parent
                and frozenset({cell, neighbor}) in captcha.passages
            ):
                parent[neighbor] = (cell, key)
                queue.append(neighbor)

    keys: list[int] = []
    cursor = captcha.goal
    while parent[cursor] is not None:
        previous, key = parent[cursor]
        keys.append(key)
        cursor = previous
    for key in reversed(keys):
        captcha.on_key(pygame.event.Event(pygame.KEYDOWN, key=key, unicode=""))


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
    elif isinstance(captcha, WireCutCaptcha):
        guard = 0
        while not captcha.solved and guard < 100:
            guard += 1
            if captcha.phase in ("right", "wrong"):
                pause = WireCutCaptcha.RIGHT_PAUSE_SECONDS if captcha.phase == "right" else WireCutCaptcha.WRONG_PAUSE_SECONDS
                captcha.update(pause + 0.1)
                continue
            captcha.on_mouse_down(captcha.wire_rect(captcha.correct_index).center)
    elif isinstance(captcha, TermoCaptcha):
        _type_termo_word(captcha, captcha.target)
        captcha.update(TermoCaptcha.RIGHT_PAUSE_SECONDS + 0.1)  # flush the "right" pause into solved=True
    elif isinstance(captcha, VaultCaptcha):
        for digit in captcha.code:
            captcha.on_key(pygame.event.Event(pygame.KEYDOWN, key=ord(digit), unicode=digit))
        captcha.on_key(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode=""))
        captcha.update(VaultCaptcha.RIGHT_PAUSE_SECONDS + 0.1)
    elif isinstance(captcha, HoldReleaseCaptcha):
        guard = 0
        while not captcha.solved and guard < 500:
            guard += 1
            captcha.on_mouse_down(captcha.BUTTON_CENTER)
            waited = 0.0
            while waited < 6.0 and not (captcha.hold_time >= captcha.MIN_HOLD_SECONDS and captcha.rule_check(captcha.digit)):
                captcha.update(0.05)
                waited += 0.05
            captcha.on_mouse_up(captcha.BUTTON_CENTER)
            if captcha.phase in ("right", "wrong"):
                pause = captcha.RIGHT_PAUSE_SECONDS if captcha.phase == "right" else captcha.WRONG_PAUSE_SECONDS
                captcha.update(pause + 0.1)
    elif isinstance(captcha, MazeCaptcha):
        _solve_maze(captcha)
    elif isinstance(captcha, InstrumentsCaptcha):
        captcha.JERK = 0.0
        captcha.velocity = [0.0, 0.0]
        guard = 0
        while not captcha.solved and guard < 200:
            guard += 1
            captcha.gauges = list(captcha.targets)
            captcha.update(0.1)
    elif isinstance(captcha, RadioCaptcha):
        guard = 0
        while not captcha.solved and guard < 20:
            guard += 1
            _press_radio_code(captcha, captcha.code)
            if captcha.phase in ("right", "wrong"):
                pause = RadioCaptcha.RIGHT_PAUSE_SECONDS if captcha.phase == "right" else RadioCaptcha.WRONG_PAUSE_SECONDS
                captcha.update(pause + 0.1)
    elif isinstance(captcha, MemoryCaptcha):
        pairs = len(captcha.cards) // 2
        for value in range(pairs):
            for index in [i for i, card in enumerate(captcha.cards) if card == value]:
                captcha.on_mouse_down(captcha.card_rect(index).center)
    elif isinstance(captcha, WhackABotCaptcha):
        guard = 0
        while not captcha.solved and guard < 3000:
            guard += 1
            captcha.update(0.05)
            for slot, entry in list(captcha.active.items()):
                if entry["kind"] == "robot":
                    captcha.on_mouse_down(captcha.slots[slot].center)
                    break
    elif isinstance(captcha, InvadersCaptcha):
        guard = 0
        while not captcha.solved and guard < 6000:
            guard += 1
            if not captcha.enemies:
                break
            target = max(captcha.enemies, key=lambda enemy: enemy["pos"].y)["pos"].x + 23
            captcha.on_mouse_move((int(target), 300))
            captcha.update(1 / 60)
            captcha.on_mouse_down((0, 0))
    else:
        raise AssertionError(f"no test solver wired up for {type(captcha).__name__}")


def _fast_forward_past_pause(run: ArcadeRun) -> None:
    guard = 0
    while run.phase != "active" and not run.game_over and guard < 200:
        guard += 1
        run.update(0.1)
        run.pop_events()
        if run.ready_to_resume:
            run.resume()


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
    assert "botao" in unlocked_seen  # the dynamic/fun kinds now unlock earlier (wave 4)


def test_arcade_run_ends_after_losing_all_lives_and_persists_stats() -> None:
    stats = ArcadeStats()
    run = ArcadeRun(ASSETS_DIR, stats, random.Random(3))
    saved = {"called": False}

    def fake_save(path=None) -> None:
        saved["called"] = True

    run.stats.save = fake_save  # avoid touching the real data/ directory in tests

    guard = 0
    while not run.game_over and guard < 400:
        guard += 1
        if run.phase == "active":
            run.update(run.time_limit + 1.0)
        else:
            run.update(0.1)
        run.pop_events()
        if run.ready_to_resume:
            run.resume()

    assert run.game_over and run.lives == 0
    assert saved["called"]
    assert stats.total_runs == 1
    assert stats.total_score == run.score
    assert run.summary is not None and run.summary.wave == run.wave


def test_run_waits_for_explicit_resume_before_spawning_the_next_captcha() -> None:
    """The core fix for text/content overlapping during transitions: a solved (or
    failed) captcha must stay on screen, unreplaced, until something explicitly
    calls resume() — the run never silently swaps it out on its own timer."""
    stats = ArcadeStats()
    run = ArcadeRun(ASSETS_DIR, stats, random.Random(50))
    captcha_before = run.captcha
    _solve_current(run)
    run.update(0.001)
    assert run.phase != "active" and run.captcha is captcha_before

    run.update(10.0)  # well past any minimum pause
    assert run.ready_to_resume
    assert run.phase != "active" and run.captcha is captcha_before  # still untouched: nobody called resume()

    run.resume()
    assert run.phase == "active" and run.captcha is not captcha_before


def test_arcade_run_declares_victory_after_surviving_the_final_wave() -> None:
    stats = ArcadeStats()
    run = ArcadeRun(ASSETS_DIR, stats, random.Random(77))
    saved = {"called": False}

    def fake_save(path=None) -> None:
        saved["called"] = True

    run.stats.save = fake_save  # avoid touching the real data/ directory in tests

    guard = 0
    while not run.game_over and guard < 5000:
        guard += 1
        _solve_current(run)
        run.update(0.001)
        run.pop_events()
        _fast_forward_past_pause(run)

    assert run.game_over and run.victory
    assert run.wave == FINAL_WAVE + 1
    assert run.summary is not None and run.summary.victory
    assert saved["called"]
    assert stats.total_victories == 1
    assert stats.total_cleared == (FINAL_WAVE - 1) * CAPTCHAS_PER_WAVE + BOSS_CAPTCHAS


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
    assert scene.view == "name_entry"

    scene.name_buffer = "TESTER"
    scene._confirm_player_name()
    assert scene.view == "briefing" and scene.player_name == "TESTER"
    scene.render(surface)

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
    guard = 0
    while scene.run.phase != "active" and not scene.run.game_over and guard < 400:
        guard += 1
        scene.update(0.1)  # small steps: a wave/unlock banner must fully clear before play resumes
        scene.render(surface)

    scene.handle_escape()
    assert scene.paused
    scene.render(surface)
    scene.handle_escape()
    assert not scene.paused

    guard = 0
    while scene.view != "gameover" and guard < 400:
        guard += 1
        if not scene.run.game_over and scene.run.phase == "active":
            scene.update(scene.run.time_limit + 1.0)
        else:
            scene.update(0.1)  # let any pending banner clear before the view switches
        scene.render(surface)

    assert scene.view == "gameover"  # the run is recorded to the leaderboard automatically, no extra step
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
    assert scene.view == "name_entry"
    for char in "AC E":  # letters and a space; also exercises the allowed-character filter
        scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=ord(char.lower()) if char != " " else pygame.K_SPACE, unicode=char.lower()))
    click(scene.name_confirm_rect.center)
    assert scene.view == "briefing" and scene.player_name == "AC E"

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
    while scene.view != "gameover" and guard < 400:
        guard += 1
        if not scene.run.game_over and scene.run.phase == "active":
            scene.update(scene.run.time_limit + 1.0)
        else:
            scene.update(0.1)  # let any pending banner clear before the view switches
        scene.render(surface)
    assert scene.view == "gameover"  # already recorded to the leaderboard, no extra confirmation step

    click(scene.retry_rect.center)
    assert scene.view == "playing" and scene.run is not None and not scene.run.game_over


def test_scene_blocks_the_next_captcha_while_a_banner_is_still_on_screen() -> None:
    scene = _make_scene()
    scene.on_enter()
    scene.name_buffer = "X"
    scene._confirm_player_name()
    scene._start_run()
    assert scene.run is not None
    scene.run.stats.save = lambda path=None: None
    scene.leaderboard.save = lambda path=None: None

    _solve_current(scene.run)
    scene.run.update(0.001)
    scene.run.update(10.0)  # push well past the run's own minimum pause
    assert scene.run.ready_to_resume and scene.run.phase != "active"

    # Force a banner to still be showing, as if a wave/unlock notice hadn't cleared yet.
    scene.active_banner = {"title": "TESTE", "subtitle": "", "color": (0, 0, 0), "duration": 5.0, "timer": 0.0, "preview": None}
    captcha_before = scene.run.captcha
    scene.update(0.016)
    assert scene.run.phase != "active" and scene.run.captcha is captcha_before  # held back by the banner

    scene.active_banner = None
    scene.banner_queue = []
    scene.update(0.016)
    assert scene.run.phase == "active" and scene.run.captcha is not captcha_before  # now free to proceed


def test_arcade_scene_can_switch_players_from_the_briefing_screen() -> None:
    scene = _make_scene()
    scene.on_enter()
    scene.name_buffer = "PRIMEIRO"
    scene._confirm_player_name()
    assert scene.view == "briefing" and scene.player_name == "PRIMEIRO"

    input_manager = scene.input_manager
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=scene.change_player_rect.center, button=1)
    input_manager.handle_event(event)
    scene.handle_event(event)
    assert scene.view == "name_entry" and scene.name_buffer == "PRIMEIRO"  # prefilled, but editable

    scene.name_buffer = "SEGUNDO"
    scene._confirm_player_name()
    assert scene.view == "briefing" and scene.player_name == "SEGUNDO"
