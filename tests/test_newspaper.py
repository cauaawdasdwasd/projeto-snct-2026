import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.gameplay import document_art
from src.gameplay.cases import CASE_BANK, CaseResult
from src.ui.newspaper import EXPLAIN_RECT, HERO_IMAGE_RECT, MENU_RECT, NEXT_RECT, FinalNewspaper


def make_results(correct_flags: list[bool]) -> list[CaseResult]:
    return [
        CaseResult(case, case.correct_stamp if ok else "deny" if case.correct_stamp != "deny" else "approve", ok)
        for case, ok in zip(CASE_BANK[:5], correct_flags)
    ]


class NewspaperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.font.init()

    def test_summary_page_is_added_after_every_decision(self) -> None:
        paper = FinalNewspaper({})
        paper.open(make_results([True] * 5))
        self.assertEqual(paper.page_count, 6)
        self.assertFalse(paper.is_summary)
        paper.page_index = 5
        self.assertTrue(paper.is_summary)

    def test_navigation_cannot_leave_the_page_range(self) -> None:
        paper = FinalNewspaper({})
        paper.open(make_results([True] * 5))
        for _ in range(10):
            paper.handle_mouse_down(NEXT_RECT.center)
        self.assertEqual(paper.page_index, 5)
        paper.handle_key_down(pygame.K_LEFT)
        self.assertEqual(paper.page_index, 4)

    def test_explanation_resets_on_page_change_and_is_unavailable_on_summary(self) -> None:
        paper = FinalNewspaper({})
        paper.open(make_results([True, False, True, True, True]))
        self.assertEqual(paper.handle_mouse_down(EXPLAIN_RECT.center), "explain")
        self.assertTrue(paper.show_explanation)
        paper.handle_key_down(pygame.K_RIGHT)
        self.assertFalse(paper.show_explanation)
        paper.page_index = 5
        paper.show_explanation = False
        self.assertNotEqual(paper.handle_mouse_down(EXPLAIN_RECT.center), "explain")
        self.assertFalse(paper.show_explanation)

    def test_menu_and_close_buttons_leave_the_newspaper(self) -> None:
        paper = FinalNewspaper({})
        paper.open(make_results([True] * 5))
        self.assertEqual(paper.handle_mouse_down(MENU_RECT.center), "menu")

    def test_escape_does_not_dismiss_the_newspaper(self) -> None:
        paper = FinalNewspaper({})
        paper.open(make_results([True] * 5))
        self.assertTrue(paper.handle_escape())
        self.assertTrue(paper.is_open)

    def test_every_case_has_its_own_picture_never_shared_with_another_case(self) -> None:
        # Regression guard: this used to be only 10 pictures reused by protocol across 50 cases.
        for case in CASE_BANK:
            self.assertEqual(case.newspaper_correct.image_asset, case.newspaper_incorrect.image_asset)
            self.assertEqual(case.newspaper_correct.image_asset, f"newspaper/{case.case_id}.png")
        assets = {case.newspaper_correct.image_asset for case in CASE_BANK}
        self.assertEqual(len(assets), len(CASE_BANK))

    def test_newspaper_renders_with_the_placeholder_before_the_real_pictures_arrive(self) -> None:
        # No assets/newspaper/case_XX.png exists yet: the game must still open and draw the paper.
        images = {
            case.newspaper_correct.image_asset: document_art.draw_newsroom_placeholder(
                HERO_IMAGE_RECT.size, case.newspaper_correct.image_asset
            )
            for case in CASE_BANK[:3]
        }
        paper = FinalNewspaper(images)
        paper.open(make_results([True, False, True]))
        surface = pygame.Surface((1600, 900))
        paper.render(surface)  # must not raise looking up a missing image
        paper.page_index = 1
        paper.render(surface)


if __name__ == "__main__":
    unittest.main()
