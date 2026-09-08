import unittest

from src.scenes.login import credentials_are_valid


class LoginCredentialsTests(unittest.TestCase):
    def test_primary_credentials_still_work(self) -> None:
        self.assertTrue(credentials_are_valid("sob_analise", "05112002LAB"))

    def test_admin_credentials_work(self) -> None:
        self.assertTrue(credentials_are_valid("admin", "admin"))

    def test_credentials_cannot_be_mixed(self) -> None:
        self.assertFalse(credentials_are_valid("admin", "05112002LAB"))
        self.assertFalse(credentials_are_valid("sob_analise", "admin"))


if __name__ == "__main__":
    unittest.main()
