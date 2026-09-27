import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.ui.calculator_popup import CalculatorPopup


class CalculatorPopupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.font.init()

    def press(self, calc: CalculatorPopup, keys: str) -> None:
        for key in keys:
            calc.press({"*": "×", "/": "÷"}.get(key, key))

    def test_basic_operations(self) -> None:
        calc = CalculatorPopup()
        self.press(calc, "48*450/9*0.8=")
        self.assertEqual(calc.display, "1920")

    def test_division_by_zero_shows_error_until_cleared(self) -> None:
        calc = CalculatorPopup()
        self.press(calc, "5/0=")
        self.assertEqual(calc.display, "Erro")
        self.press(calc, "7")
        self.assertEqual(calc.display, "Erro")
        calc.press("C")
        self.assertEqual(calc.display, "0")

    def test_keyboard_accepts_equals_and_enter(self) -> None:
        calc = CalculatorPopup()
        calc.open()
        for char in "12*3=":
            calc.handle_key(pygame.event.Event(pygame.KEYDOWN, key=ord(char), unicode=char))
        self.assertEqual(calc.display, "36")

    def test_closed_calculator_ignores_keys(self) -> None:
        calc = CalculatorPopup()
        handled = calc.handle_key(pygame.event.Event(pygame.KEYDOWN, key=ord("1"), unicode="1"))
        self.assertFalse(handled)

    def test_title_bar_drag_stays_on_screen(self) -> None:
        calc = CalculatorPopup()
        calc.open()
        start = (calc.rect.x + 20, calc.rect.y + 10)
        self.assertEqual(calc.handle_mouse_down(start), "consume")
        calc.handle_mouse_motion((5000, 5000))
        calc.handle_mouse_up()
        self.assertLessEqual(calc.rect.right, 1554)
        self.assertLessEqual(calc.rect.bottom, 696)


if __name__ == "__main__":
    unittest.main()
