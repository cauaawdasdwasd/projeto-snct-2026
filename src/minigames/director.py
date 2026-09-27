"""Decides when, during a case, the desk gets interrupted and by what."""

from __future__ import annotations

import random
from dataclasses import dataclass

from src.minigames.captchas import TIERS

# One more captcha per turn than the earlier cut, so the interruptions carry the pace of the shift.
TIER_PLAN = {
    1: ("easy", "easy"),
    2: ("easy", "medium", "easy"),
    3: ("easy", "medium", "medium"),
    4: ("easy", "medium", "hard", "medium"),
    5: ("medium", "hard", "hard", "medium"),
}
TIME_BONUS_SECONDS = 6
WRONG_ANSWER_PENALTY = 3
SKIP_PENALTY = 15
BASE_LIMIT_SECONDS = 195
LIMIT_PER_TURN_SECONDS = 15


@dataclass(frozen=True)
class Complication:
    at: float  # seconds of real work since the case started
    kind: str  # "popups" or "captcha"
    detail: str  # popup count or difficulty tier


def case_time_limit(turn: int) -> int:
    """3:30 for the easiest turn up to 4:30 for the hardest."""
    return BASE_LIMIT_SECONDS + LIMIT_PER_TURN_SECONDS * max(1, min(5, turn))


class ComplicationDirector:
    def __init__(self, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.recent: list[str] = []

    def plan(self, limit: float, turn: int) -> list[Complication]:
        tiers = TIER_PLAN[max(1, min(5, turn))]
        count = len(tiers)
        popup_count = min(5, 2 + turn // 2)
        events: list[Complication] = []
        for index, tier in enumerate(tiers):
            fraction = (index + 1) / (count + 1) + self.rng.uniform(-0.025, 0.025)
            captcha_at = fraction * limit
            events.append(Complication(captcha_at - 0.11 * limit, "popups", str(popup_count)))
            events.append(Complication(captcha_at, "captcha", tier))
        return sorted(events, key=lambda event: event.at)

    def pick_captcha(self, tier: str) -> str:
        options = [kind for kind in TIERS[tier] if kind not in self.recent[-2:]] or list(TIERS[tier])
        choice = self.rng.choice(options)
        self.recent.append(choice)
        return choice
