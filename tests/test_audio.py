import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.core.audio import AudioManager, _generate_tone


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


class SynthesizedSoundTests(unittest.TestCase):
    """The Simon pad tones are generated with numpy instead of shipped as asset files -
    these guard that the synthesis actually produces valid, playable sounds instead of
    silently failing."""

    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(frequency=44_100, size=-16, channels=1, buffer=512)

    def test_generate_tone_returns_a_playable_sound(self) -> None:
        sound = _generate_tone(440.0)
        self.assertIsInstance(sound, pygame.mixer.Sound)
        self.assertGreater(sound.get_length(), 0)

    def test_pad_tones_are_loaded_into_the_audio_manager(self) -> None:
        from src.core.assets import AssetManager
        from src.core.settings import ASSETS_DIR

        manager = AudioManager(AssetManager(ASSETS_DIR))
        for index in range(len(AudioManager.PAD_TONE_FREQUENCIES)):
            self.assertIn(f"pad_{index}", manager.sounds)


if __name__ == "__main__":
    unittest.main()
