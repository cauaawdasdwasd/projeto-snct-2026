import unittest

from src.core.preferences import UserPreferences


class UserPreferencesTests(unittest.TestCase):
    def test_invalid_screen_filter_returns_to_crt(self) -> None:
        preferences = UserPreferences(screen_filter="broken")

        preferences.normalize()

        self.assertEqual(preferences.screen_filter, "crt")


if __name__ == "__main__":
    unittest.main()
