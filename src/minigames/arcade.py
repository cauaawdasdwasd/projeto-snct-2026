"""ARENA VERIFY-9: a standalone score-attack gauntlet of 'prove you are human' captchas.

Unlike the audit's `ComplicationDirector` (which sprinkles captchas between case work),
this mode *is* the captchas: VERIFY-9 throws one verification after another and grades
the player on speed, streak and survival. It is built to be grindable rather than a pile
of random rewards:

- Waves are fixed-length (`CAPTCHAS_PER_WAVE` solves each) and only get harder in a
  predictable curve (shorter timers, wider challenge roster), so a player can learn the
  pace instead of being surprised by noise.
- The combo multiplier only grows from clean, uninterrupted streaks and only resets on
  an actual timeout, so score growth tracks skill and consistency.
- The overclock meter is filled by the same clean streaks and pays out an extra life
  instead of points, turning "play well" into "survive longer" instead of a second,
  disconnected currency.
- Lifetime stats persist across runs (`ArcadeStats`) and unlock ranks, giving the mode a
  reason to be replayed beyond a single session's high score.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from src.core.settings import BASE_DIR
from src.minigames.captchas import Captcha, create_captcha

STATS_PATH = BASE_DIR / "data" / "arcade_stats.json"
LEADERBOARD_PATH = BASE_DIR / "data" / "arcade_leaderboard.json"
LEADERBOARD_SIZE = 10
NAME_MAX_LEN = 14

STARTING_LIVES = 3
MAX_LIVES = 5
CAPTCHAS_PER_WAVE = 3

BASE_TIME_LIMIT = 26.0
TIME_LIMIT_FLOOR = 12.0
TIME_LIMIT_STEP = 0.6

BASE_SCORE = 120
WAVE_SCORE_STEP = 18
COMBO_STEPS = (1.0, 1.2, 1.5, 1.8, 2.2, 2.6, 3.0)

INTERNAL_FAIL_PENALTY = 2.0
OVERCLOCK_MAX = 100.0
OVERCLOCK_CLEAN_FILL = 18.0
OVERCLOCK_DIRTY_FILL = 8.0

SOLVE_CELEBRATION_SECONDS = 0.9
TIMEOUT_PAUSE_SECONDS = 1.1
WAVE_BANNER_SECONDS = 1.1

# Cumulative unlock schedule: the roster only grows, so early challenges stay in the mix
# and a player always recognises *something* on the screen, even deep into a run.
KIND_LABELS = {
    "wobbly": "TEXTO TORTO",
    "cats": "ACHE OS GATOS",
    "traffic": "SEMÁFORO",
    "rotate": "GIRAR A FOTO",
    "simon": "SEQUÊNCIA DE CORES",
    "puzzle": "QUEBRA-CABEÇA",
    "chimp": "TESTE DO MACACO",
    "memory": "JOGO DA MEMÓRIA",
    "whackabot": "CAÇA-ROBÔS",
    "puzzle9": "QUEBRA-CABEÇA 3X3",
    "memory6": "MEMÓRIA AVANÇADA",
    "invaders": "INVASORES",
}
WAVE_UNLOCKS: tuple[tuple[int, tuple[str, ...]], ...] = (
    (1, ("wobbly", "cats")),
    (2, ("traffic",)),
    (3, ("rotate", "simon")),
    (4, ("puzzle", "chimp")),
    (6, ("memory", "whackabot")),
    (8, ("puzzle9",)),
    (10, ("memory6", "invaders")),
)

RANKS: tuple[tuple[int, str], ...] = (
    (0, "ESTAGIÁRIO(A) DE TI"),
    (15, "AUDITOR(A) JÚNIOR"),
    (40, "AUDITOR(A) PLENO(A)"),
    (80, "AUDITOR(A) SÊNIOR"),
    (150, "CAÇADOR(A) DE BOTS"),
    (300, "LENDA ANTI-VERIFY-9"),
)


def time_limit_for_wave(wave: int) -> float:
    return max(TIME_LIMIT_FLOOR, BASE_TIME_LIMIT - TIME_LIMIT_STEP * (wave - 1))


def unlocked_kinds(wave: int) -> tuple[str, ...]:
    kinds: list[str] = []
    for threshold, batch in WAVE_UNLOCKS:
        if wave >= threshold:
            for kind in batch:
                if kind not in kinds:
                    kinds.append(kind)
    return tuple(kinds)


def newly_unlocked_kinds(wave: int) -> tuple[str, ...]:
    """Kinds that become available for the first time exactly at this wave."""
    for threshold, batch in WAVE_UNLOCKS:
        if threshold == wave:
            return batch
    return ()


def rank_for(total_cleared: int) -> tuple[str, int | None]:
    """Current rank title and the score needed for the next one (None past the last rank)."""
    current = RANKS[0][1]
    next_threshold: int | None = None
    for threshold, title in RANKS:
        if total_cleared >= threshold:
            current = title
        else:
            next_threshold = threshold
            break
    return current, next_threshold


def score_for_solve(wave: int, time_left: float, time_limit: float, combo: int) -> int:
    base = BASE_SCORE + WAVE_SCORE_STEP * (wave - 1)
    speed_ratio = max(0.0, min(1.0, time_left / time_limit)) if time_limit > 0 else 0.0
    speed_bonus = 1.0 + 0.5 * speed_ratio
    multiplier = COMBO_STEPS[min(combo, len(COMBO_STEPS) - 1)]
    return round(base * speed_bonus * multiplier)


@dataclass
class ArcadeStats:
    """Lifetime progress, persisted between play sessions like `UserPreferences`."""

    best_score: int = 0
    best_wave: int = 1
    best_combo: int = 0
    total_runs: int = 0
    total_cleared: int = 0
    total_score: int = 0

    def rank(self) -> tuple[str, int | None]:
        return rank_for(self.total_cleared)

    def save(self, path: Path = STATS_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path = STATS_PATH) -> ArcadeStats:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            return cls(
                best_score=int(payload.get("best_score", 0)),
                best_wave=int(payload.get("best_wave", 1)),
                best_combo=int(payload.get("best_combo", 0)),
                total_runs=int(payload.get("total_runs", 0)),
                total_cleared=int(payload.get("total_cleared", 0)),
                total_score=int(payload.get("total_score", 0)),
            )
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return cls()


@dataclass
class LeaderboardEntry:
    """One row of the classic arcade high-score table."""

    name: str
    score: int
    wave: int


class Leaderboard:
    """Local top-`LEADERBOARD_SIZE` scores, like the initials table on an arcade cabinet."""

    def __init__(self, entries: list[LeaderboardEntry] | None = None) -> None:
        self.entries: list[LeaderboardEntry] = list(entries or [])

    def qualifies(self, score: int) -> bool:
        return len(self.entries) < LEADERBOARD_SIZE or score > self.entries[-1].score

    def add(self, name: str, score: int, wave: int) -> int:
        """Insert an entry and return its rank (0-indexed), or -1 if it didn't make the cut."""
        entry = LeaderboardEntry(name=(name.strip() or "ANÔNIMO")[:NAME_MAX_LEN], score=score, wave=wave)
        self.entries = sorted([*self.entries, entry], key=lambda item: item.score, reverse=True)[:LEADERBOARD_SIZE]
        for index, placed in enumerate(self.entries):
            if placed is entry:
                return index
        return -1

    def save(self, path: Path = LEADERBOARD_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(entry) for entry in self.entries]
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path = LEADERBOARD_PATH) -> Leaderboard:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            entries = [
                LeaderboardEntry(
                    name=str(item.get("name", "ANÔNIMO"))[:NAME_MAX_LEN],
                    score=int(item.get("score", 0)),
                    wave=int(item.get("wave", 1)),
                )
                for item in payload
            ]
            entries.sort(key=lambda item: item.score, reverse=True)
            return cls(entries[:LEADERBOARD_SIZE])
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return cls()


@dataclass
class ArcadeEvent:
    kind: str
    value: object = None


@dataclass
class RunSummary:
    score: int
    wave: int
    cleared: int
    best_combo: int
    new_record: bool
    rank: str
    next_rank_at: int | None


class ArcadeRun:
    """One playthrough of the arena: owns the live captcha and the wave/score state."""

    def __init__(self, assets_root: Path, stats: ArcadeStats, rng: random.Random | None = None) -> None:
        self.assets_root = Path(assets_root)
        self.stats = stats
        self.rng = rng or random.Random()
        self._events: list[ArcadeEvent] = []
        self.game_over = False
        self.summary: RunSummary | None = None
        self._recent_kinds: list[str] = []
        self._start()

    def _start(self) -> None:
        self.wave = 1
        self.cleared_in_wave = 0
        self.lives = STARTING_LIVES
        self.score = 0
        self.captchas_cleared = 0
        self.combo = 0
        self.best_combo = 0
        self.overclock = 0.0
        self.had_error_this_captcha = False
        self.phase = "active"  # active | celebrate | hit | wave_banner
        self.phase_timer = 0.0
        self.time_left = 0.0
        self.time_limit = 0.0
        self.captcha: Captcha | None = None
        self._spawn_captcha()

    # -- lifecycle ---------------------------------------------------------
    def pop_events(self) -> list[ArcadeEvent]:
        events, self._events = self._events, []
        return events

    def _spawn_captcha(self) -> None:
        pool = unlocked_kinds(self.wave)
        choices = [kind for kind in pool if kind not in self._recent_kinds[-2:]] or list(pool)
        kind = self.rng.choice(choices)
        self._recent_kinds.append(kind)
        self.captcha = create_captcha(kind, random.Random(self.rng.randrange(1 << 30)), self.assets_root)
        self.time_limit = time_limit_for_wave(self.wave)
        self.time_left = self.time_limit
        self.had_error_this_captcha = False
        self.phase = "active"

    # -- input passthrough (only valid while a captcha is actually live) ---
    @property
    def accepting_input(self) -> bool:
        return self.phase == "active" and self.captcha is not None and not self.game_over

    def handle_mouse_down(self, pos: tuple[int, int]) -> None:
        if self.accepting_input:
            self.captcha.on_mouse_down(pos)

    def handle_mouse_up(self, pos: tuple[int, int]) -> None:
        if self.accepting_input:
            self.captcha.on_mouse_up(pos)

    def handle_mouse_move(self, pos: tuple[int, int] | None) -> None:
        if self.accepting_input and pos is not None:
            self.captcha.on_mouse_move(pos)

    def handle_key(self, event) -> None:
        if self.accepting_input:
            self.captcha.on_key(event)

    # -- update --------------------------------------------------------
    def update(self, dt: float) -> None:
        if self.game_over:
            return
        if self.phase == "active":
            self._update_active(dt)
        else:
            self.phase_timer -= dt
            if self.phase_timer <= 0:
                if self.game_over:
                    return
                self._spawn_captcha()

    def _update_active(self, dt: float) -> None:
        assert self.captcha is not None
        self.time_left -= dt
        self.captcha.update(dt)
        for name in self.captcha.take_events():
            self._events.append(ArcadeEvent("sound", name))
            if name == "error":
                self.had_error_this_captcha = True
                self.time_left -= INTERNAL_FAIL_PENALTY
                self._events.append(ArcadeEvent("mistake", None))
        if self.captcha.solved:
            self._handle_solved()
            return
        if self.time_left <= 0:
            self._handle_timeout()

    def _handle_solved(self) -> None:
        assert self.captcha is not None
        points = score_for_solve(self.wave, max(0.0, self.time_left), self.time_limit, self.combo)
        self.score += points
        self.captchas_cleared += 1
        self.cleared_in_wave += 1
        self.combo += 1
        self.best_combo = max(self.best_combo, self.combo)
        fill = OVERCLOCK_DIRTY_FILL if self.had_error_this_captcha else OVERCLOCK_CLEAN_FILL
        self.overclock = min(OVERCLOCK_MAX + fill, self.overclock + fill)
        self._events.append(ArcadeEvent("solved", points))
        overclocked = False
        if self.overclock >= OVERCLOCK_MAX and self.lives < MAX_LIVES:
            self.lives = min(MAX_LIVES, self.lives + 1)
            self.overclock -= OVERCLOCK_MAX
            overclocked = True
            self._events.append(ArcadeEvent("overclock", None))
        elif self.overclock >= OVERCLOCK_MAX:
            self.overclock = OVERCLOCK_MAX

        self.phase = "celebrate"
        self.phase_timer = SOLVE_CELEBRATION_SECONDS + (0.5 if overclocked else 0.0)

        if self.cleared_in_wave >= CAPTCHAS_PER_WAVE:
            self.cleared_in_wave = 0
            self.wave += 1
            unlocked = newly_unlocked_kinds(self.wave)
            self._events.append(ArcadeEvent("wave", self.wave))
            for kind in unlocked:
                self._events.append(ArcadeEvent("unlock", kind))
            self.phase = "wave_banner"
            self.phase_timer = WAVE_BANNER_SECONDS + (0.5 if unlocked else 0.0)

    def _handle_timeout(self) -> None:
        self.lives -= 1
        self.combo = 0
        self._events.append(ArcadeEvent("timeout", None))
        if self.lives <= 0:
            self._end_run()
            return
        self.phase = "hit"
        self.phase_timer = TIMEOUT_PAUSE_SECONDS

    def _end_run(self) -> None:
        self.game_over = True
        self.phase = "active"
        self.captcha = None
        self.stats.total_runs += 1
        self.stats.total_cleared += self.captchas_cleared
        self.stats.total_score += self.score
        new_record = self.score > self.stats.best_score
        self.stats.best_score = max(self.stats.best_score, self.score)
        self.stats.best_wave = max(self.stats.best_wave, self.wave)
        self.stats.best_combo = max(self.stats.best_combo, self.best_combo)
        try:
            self.stats.save()
        except OSError:
            pass
        rank, next_at = self.stats.rank()
        self.summary = RunSummary(
            score=self.score,
            wave=self.wave,
            cleared=self.captchas_cleared,
            best_combo=self.best_combo,
            new_record=new_record,
            rank=rank,
            next_rank_at=next_at,
        )
        self._events.append(ArcadeEvent("gameover", self.summary))
