from __future__ import annotations

from dataclasses import dataclass

from src.gameplay.cases import AuditCase


@dataclass(frozen=True)
class Link:
    """What the player learns by putting two pieces of evidence side by side.

    kind: "equal" and "different" are direct value checks, "related" means the
    two data belong to the same calculation or rule, "none" means unrelated.
    """

    kind: str
    text: str


NO_LINK = Link("none", "Não falam da mesma coisa. Procure dois dados que se cruzem.")

MAX_TEXT_LENGTH = 100


def find_link(case: AuditCase, key_a: str, key_b: str) -> Link:
    """Return the meaning of comparing two evidence keys, or NO_LINK."""
    pair = {key_a, key_b}
    for link in case.links:
        if {link.key_a, link.key_b} == pair:
            return Link(link.kind, link.text)
    return NO_LINK
