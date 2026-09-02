import os
import unittest
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.rendering.screen_effect import ScreenEffect


class FakeAssets:
    assets_root = Path("missing-assets")


class ScreenEffectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_effect_changes_only_requested_display_area(self) -> None:
        surface = pygame.Surface((80, 60)).convert()
        surface.fill((220, 220, 220))
        effect = ScreenEffect(FakeAssets())

        effect.apply(surface, "crt", pygame.Rect(10, 10, 50, 30))

        self.assertEqual(surface.get_at((2, 2))[:3], (220, 220, 220))
        self.assertNotEqual(surface.get_at((12, 14))[:3], (220, 220, 220))


if __name__ == "__main__":
    unittest.main()
