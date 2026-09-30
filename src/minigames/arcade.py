"""ARENA VERIFY-9: a short story campaign of 'prove you are human' captchas with a boss fight.

Unlike the audit's `ComplicationDirector` (which sprinkles captchas between case work),
this mode *is* the captchas: VERIFY-9 throws one verification after another until the
player reaches the final confrontation. It has a beginning, a middle and an end instead
of being an endless grind:

- The 5 regular waves draw from a per-run shuffled queue (`_build_campaign_queue`)
  instead of an independent random pick each time: every "dynamic" verification is
  guaranteed to show up exactly once somewhere in those 5 waves, in a random order, so a
  short run never skips the content it is actually about while still feeling random.
- Score is driven mainly by speed: `score_for_solve` weighs how much time was left over
  the time limit far more than the wave number, so "quanto mais rápido, mais pontos" is
  true at every stage, not just a late-game bonus.
- The combo multiplier only grows from clean, uninterrupted streaks and only resets on
  an actual timeout, so score growth tracks skill and consistency.
- The overclock meter is filled by the same clean streaks and pays out an extra life
  instead of points, turning "play well" into "survive longer" instead of a second,
  disconnected currency.
- Wave `FINAL_WAVE` is a real boss fight, not just a harder wave: VERIFY-9 draws 2
  distinct verifications from its "signature" pool plus the visual-memory grid (always
  last) into one fixed 3-task gauntlet, run against a single shared `BOSS_TIME_LIMIT`
  clock instead of a per-task timer. Running out of time costs a life and resets the
  attempt (fresh tasks, fresh clock) instead of ending the run outright, as long as a
  life remains.
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
BOSS_CAPTCHAS = 3  # a fixed 3-task gauntlet, not "however many the pool deals"
FINAL_WAVE = 6  # this wave IS the VERIFY-9 boss fight; clearing it wins the run
BOSS_TIME_LIMIT = 120.0  # one shared clock for all 3 boss tasks, not a per-task timer

# A skilled player has to be able to go from the briefing to the boss gate in a few
# minutes - 5 intro/escalation waves (5*CAPTCHAS_PER_WAVE = 15 verifications) is short
# enough for that, then the boss fight is its own ~2-minute set piece on top.
BASE_TIME_LIMIT = 24.0
TIME_LIMIT_FLOOR = 8.0
TIME_LIMIT_DECAY = 0.82

# Some verifications are inherently slower to read/execute than others (typing several
# guesses, following a multi-step deduction). Rather than distort the shared wave curve
# for everyone, they get a flat multiplier on top of it. (Irrelevant during the boss
# fight itself, which runs on BOSS_TIME_LIMIT instead of a per-task timer.)
KIND_TIME_MULTIPLIER = {
    "termo": 3.2,
    "cofre": 2.6,
    "padrao": 2.4,
    "wires": 1.8,
    "radio": 1.7,
    "conectar_fios": 1.65,
    "instrumentos": 1.6,
    "labirinto": 1.4,
}

# The 6 classic "prove you're human" captchas (distorted text, click-the-cats, traffic
# grid, rotate-the-photo, tile swaps) are the most tedious part of the mode, so the
# 5 regular waves never schedule them at all - they exist for flavor/completeness but a
# short campaign has no room for filler. Every OTHER verification is "the point" of the
# arena, so all of them are guaranteed to appear, once each, spread across the 5 waves.
BORING_KINDS: tuple[str, ...] = ("wobbly", "cats", "traffic", "rotate", "puzzle", "puzzle9")
REGULAR_DYNAMIC_KINDS: tuple[str, ...] = (
    "simon", "chimp", "whackabot", "invaders", "memory", "memory6",
    "termo", "wires", "cofre", "botao", "labirinto", "instrumentos", "radio",
    "conectar_fios", "padrao",
)
# The boss fight draws 2 DISTINCT verifications from this "signature" pool (a sample,
# not an independent coin flip per slot, so the same one can never show up twice in one
# attempt) and always closes with the visual-memory grid - a fixed-length, guaranteed
# variety gauntlet instead of a wider random pool like the regular waves use.
BOSS_SIGNATURE_KINDS: tuple[str, ...] = (
    "termo", "wires", "cofre", "botao", "labirinto", "instrumentos", "radio", "conectar_fios",
)
BOSS_FINALE_KIND = "padrao"

BASE_SCORE = 120
WAVE_SCORE_STEP = 14
COMBO_STEPS = (1.0, 1.2, 1.5, 1.8, 2.2, 2.6, 3.0)

INTERNAL_FAIL_PENALTY = 2.0
OVERCLOCK_MAX = 100.0
OVERCLOCK_CLEAN_FILL = 18.0
OVERCLOCK_DIRTY_FILL = 8.0

SOLVE_CELEBRATION_SECONDS = 0.9
TIMEOUT_PAUSE_SECONDS = 1.1
WAVE_BANNER_SECONDS = 1.1

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
    "wires": "CORTAR O FIO",
    "puzzle9": "QUEBRA-CABEÇA 3X3",
    "termo": "TERMO",
    "cofre": "ABRIR O COFRE",
    "botao": "SEGURE E SOLTE",
    "labirinto": "LABIRINTO OCULTO",
    "memory6": "MEMÓRIA AVANÇADA",
    "invaders": "INVASORES",
    "instrumentos": "PAINEL DE INSTRUMENTOS",
    "radio": "RÁDIO DA TORRE",
    "padrao": "MEMÓRIA VISUAL",
    "conectar_fios": "CONECTAR OS FIOS",
}

RANKS: tuple[tuple[int, str], ...] = (
    (0, "ESTAGIÁRIO(A) DE TI"),
    (15, "AUDITOR(A) JÚNIOR"),
    (40, "AUDITOR(A) PLENO(A)"),
    (80, "AUDITOR(A) SÊNIOR"),
    (150, "CAÇADOR(A) DE BOTS"),
    (300, "LENDA ANTI-VERIFY-9"),
)


def time_limit_for_wave(wave: int) -> float:
    return TIME_LIMIT_FLOOR + (BASE_TIME_LIMIT - TIME_LIMIT_FLOOR) * (TIME_LIMIT_DECAY ** (wave - 1))


def time_limit_for(wave: int, kind: str) -> float:
    return time_limit_for_wave(wave) * KIND_TIME_MULTIPLIER.get(kind, 1.0)


def build_campaign_queue(rng: random.Random) -> list[str]:
    """A shuffled order for the 5 regular waves covering every REGULAR_DYNAMIC_KINDS
    verification exactly once - "random, but never skips the content" instead of an
    independent draw per slot, which could (and did) leave some kinds never played in
    a single short run."""
    queue = list(REGULAR_DYNAMIC_KINDS)
    rng.shuffle(queue)
    return queue


def draw_boss_tasks(rng: random.Random) -> list[str]:
    """2 distinct verifications sampled (not drawn independently, so they can never
    repeat within one attempt) from the signature pool, plus the visual-memory grid
    fixed as the third and final task."""
    return [*rng.sample(BOSS_SIGNATURE_KINDS, 2), BOSS_FINALE_KIND]


def wave_slice(queue: list[str], wave: int) -> tuple[str, ...]:
    """The chunk of the campaign queue a given regular wave plays, for the wave-up
    banner to preview ("novo teste liberado: ...") before the player gets there."""
    start = (wave - 1) * CAPTCHAS_PER_WAVE
    return tuple(queue[start : start + CAPTCHAS_PER_WAVE])


def captchas_required_for(wave: int) -> int:
    """How many solves clear this wave - the boss fight demands more than a normal one."""
    return BOSS_CAPTCHAS if wave == FINAL_WAVE else CAPTCHAS_PER_WAVE


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
    # Speed is now the main lever (0.5x for a last-second solve, up to 2.0x for an
    # almost-instant one) instead of a small bonus on top of the wave number, since
    # the campaign scores "quanto mais rápido, mais pontos" above everything else.
    speed_bonus = 0.5 + 1.5 * speed_ratio
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
    total_victories: int = 0

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
                total_victories=int(payload.get("total_victories", 0)),
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
    victory: bool = False


class ArcadeRun:
    """One playthrough of the arena: owns the live captcha and the wave/score state."""

    def __init__(self, assets_root: Path, stats: ArcadeStats, rng: random.Random | None = None) -> None:
        self.assets_root = Path(assets_root)
        self.stats = stats
        self.rng = rng or random.Random()
        self._events: list[ArcadeEvent] = []
        self.game_over = False
        self.summary: RunSummary | None = None
        self.campaign_queue: list[str] = build_campaign_queue(self.rng)
        self.boss_tasks: list[str] = []
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
        self.victory = False
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

    def _start_boss(self) -> None:
        """(Re)starts the boss encounter: a fresh 3-task lineup and a fresh shared
        clock. Called both when the boss wave is first reached and whenever the
        shared clock runs out with a life still left, so a failed attempt resets
        instead of ending the run."""
        self.boss_tasks = draw_boss_tasks(self.rng)
        self.cleared_in_wave = 0
        self.time_limit = BOSS_TIME_LIMIT
        self.time_left = BOSS_TIME_LIMIT

    def _spawn_captcha(self) -> None:
        if self.wave == FINAL_WAVE:
            # The boss runs on one shared clock across all 3 tasks: time_limit/time_left
            # are set once in _start_boss() and deliberately left untouched here, so the
            # countdown keeps running straight through the task-to-task transitions.
            kind = self.boss_tasks[self.cleared_in_wave]
        else:
            # captchas_cleared is a running total across the whole run and hasn't been
            # touched by the boss yet at this point, so it doubles as the campaign
            # queue's position: 0 on the very first captcha, 14 on the last regular one.
            kind = self.campaign_queue[self.captchas_cleared]
            self.time_limit = time_limit_for(self.wave, kind)
            self.time_left = self.time_limit
        self.captcha = create_captcha(kind, random.Random(self.rng.randrange(1 << 30)), self.assets_root)
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

    @property
    def ready_to_resume(self) -> bool:
        """True once the minimum pause for the current non-active phase has elapsed.

        Spawning the next captcha is NOT automatic: the presentation layer calls
        `resume()` once it is done showing whatever it wants for this pause (a
        banner, a celebration beat...), so gameplay never starts underneath a
        still-visible notice.
        """
        return not self.game_over and self.phase != "active" and self.phase_timer <= 0

    def resume(self) -> None:
        if self.game_over or self.phase == "active":
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

        if self.cleared_in_wave >= captchas_required_for(self.wave):
            self.cleared_in_wave = 0
            self.wave += 1
            if self.wave > FINAL_WAVE:
                self._end_run(victory=True)
                return
            self._events.append(ArcadeEvent("wave", self.wave))
            if self.wave == FINAL_WAVE:
                self._start_boss()
                upcoming = tuple(self.boss_tasks)
            else:
                upcoming = wave_slice(self.campaign_queue, self.wave)
            for kind in upcoming:
                self._events.append(ArcadeEvent("unlock", kind))
            self.phase = "wave_banner"
            self.phase_timer = WAVE_BANNER_SECONDS + (0.5 if upcoming else 0.0)

    def _handle_timeout(self) -> None:
        self.lives -= 1
        self.combo = 0
        self._events.append(ArcadeEvent("timeout", None))
        if self.lives <= 0:
            self._end_run()
            return
        if self.wave == FINAL_WAVE:
            # The boss fight's shared clock ran out: reset the attempt (fresh tasks,
            # fresh clock) instead of ending the run, as long as a life remains.
            self._start_boss()
            self._events.append(ArcadeEvent("boss_reset", None))
        self.phase = "hit"
        self.phase_timer = TIMEOUT_PAUSE_SECONDS

    def _end_run(self, victory: bool = False) -> None:
        self.game_over = True
        self.victory = victory
        self.phase = "active"
        self.captcha = None
        self.stats.total_runs += 1
        self.stats.total_cleared += self.captchas_cleared
        self.stats.total_score += self.score
        if victory:
            self.stats.total_victories += 1
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
            victory=victory,
        )
        self._events.append(ArcadeEvent("gameover", self.summary))
