import unittest

import pygame

from src.ui.desktop_window import DesktopWindowManager


class DesktopWindowManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.work_area = pygame.Rect(100, 50, 900, 650)
        self.manager = DesktopWindowManager(self.work_area)

    def test_focus_minimize_and_restore_follow_z_order(self) -> None:
        self.manager.open("first", "First", pygame.Rect(180, 90, 480, 360), (300, 220))
        self.manager.open("second", "Second", pygame.Rect(250, 130, 420, 300), (280, 200))

        self.assertEqual(self.manager.focused_id, "second")
        self.manager.minimize("second")
        self.assertEqual(self.manager.focused_id, "first")
        self.manager.restore("second")
        self.assertEqual(self.manager.focused_id, "second")
        self.manager.focus("first")
        self.assertEqual(self.manager.task_order, ["first", "second"])

    def test_maximize_restores_original_rectangle(self) -> None:
        original = pygame.Rect(250, 130, 420, 300)
        window = self.manager.open("app", "App", original, (280, 200))

        self.manager.toggle_maximize("app")
        self.assertTrue(window.maximized)
        self.assertEqual(window.rect, self.work_area)

        self.manager.toggle_maximize("app")
        self.assertFalse(window.maximized)
        self.assertEqual(window.rect, original)

    def test_corner_resize_respects_work_area(self) -> None:
        window = self.manager.open(
            "app",
            "App",
            pygame.Rect(200, 100, 500, 400),
            (300, 220),
        )
        pointer = window.rect.bottomright
        hit = self.manager.hit_test(pointer)
        self.assertIsNotNone(hit)
        assert hit is not None

        self.manager.begin_interaction(hit, pointer)
        self.manager.update_pointer((1200, 900))
        self.manager.end_interaction((1200, 900))

        self.assertLessEqual(window.rect.right, self.work_area.right)
        self.assertLessEqual(window.rect.bottom, self.work_area.bottom)
        self.assertGreaterEqual(window.rect.width, window.min_size[0])
        self.assertGreaterEqual(window.rect.height, window.min_size[1])


if __name__ == "__main__":
    unittest.main()
