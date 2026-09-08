import unittest

from src.core.audio import AudioManager


class FakeChannel:
    def set_volume(self, volume: float) -> None:
        self.volume = volume


class FakeSound:
    def __init__(self) -> None:
        self.maxtime = None
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True

    def play(self, *, maxtime: int = 0) -> FakeChannel:
        self.maxtime = maxtime
        return FakeChannel()


class AudioManagerTests(unittest.TestCase):
    def test_typing_sound_is_cut_to_a_short_keypress(self) -> None:
        sound = FakeSound()
        manager = AudioManager.__new__(AudioManager)
        manager.enabled = True
        manager.sfx_volume = 1.0
        manager.sounds = {"typing": sound}

        manager.play("typing")

        self.assertTrue(sound.stopped)
        self.assertEqual(sound.maxtime, AudioManager.TYPING_MAXTIME_MS)


if __name__ == "__main__":
    unittest.main()
