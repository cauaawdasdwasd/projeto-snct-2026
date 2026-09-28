import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from src.gameplay.cases import CASE_BANK
from src.ui.newspaper import ARTICLE_COLUMN_RECT, FinalNewspaper


@pytest.fixture(scope="module")
def paper():
    pygame.init()
    pygame.font.init()
    pygame.display.set_mode((64, 64))
    yield FinalNewspaper({})
    pygame.quit()


def wrapped_line_count(text: str, font: pygame.font.Font, width: int) -> int:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if not current or font.size(candidate)[0] <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return len(lines)


def test_every_headline_and_body_fits_without_being_cut(paper) -> None:
    headline_width = 1368  # pygame.Rect(92, 145, 1368, 104) in _draw_headline
    body_width = ARTICLE_COLUMN_RECT.width
    for case in CASE_BANK:
        for article in (case.newspaper_correct, case.newspaper_incorrect):
            assert wrapped_line_count(article.headline, paper.font_headline, headline_width) <= 3, (case.case_id, article.headline)
            assert wrapped_line_count(article.body, paper.font_body, body_width) <= 7, (case.case_id, article.body)


def test_headlines_and_bodies_are_not_generic_placeholders() -> None:
    # Regression guard: the Letícia cases used to just repeat the dry technical explanation as the body.
    for case in CASE_BANK:
        assert case.newspaper_incorrect.body != case.explanation, case.case_id
        assert "A IA errou e a auditoria deixou passar." not in case.newspaper_incorrect.body, case.case_id
        assert case.newspaper_correct.body != case.newspaper_incorrect.body, case.case_id
        assert case.newspaper_correct.headline != case.newspaper_incorrect.headline, case.case_id
