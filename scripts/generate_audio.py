"""Generate the small, dependency-free audio set used by Sob Análise."""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path


SAMPLE_RATE = 44_100
ROOT = Path(__file__).resolve().parents[1]
MUSIC_DIR = ROOT / "assets" / "music"
SFX_DIR = ROOT / "assets" / "sfx"


def write_wav(path: Path, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames = bytearray()
    for sample in samples:
        value = max(-1.0, min(1.0, sample))
        frames.extend(struct.pack("<h", round(value * 32767)))

    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        output.writeframes(frames)


def envelope(time: float, duration: float, attack: float, release: float) -> float:
    if time < attack:
        return time / attack
    if time > duration - release:
        return max(0.0, (duration - time) / release)
    return 1.0


def midi_to_hz(note: int) -> float:
    return 440.0 * 2.0 ** ((note - 69) / 12.0)


def ambient_track() -> list[float]:
    rng = random.Random(7)
    bpm = 84.0
    beat_length = 60.0 / bpm
    bar_length = beat_length * 4.0
    duration = bar_length * 8.0
    chords = (
        (48, (0, 3, 7, 10)),
        (44, (0, 4, 7, 11)),
        (51, (0, 3, 7, 10)),
        (46, (0, 4, 7, 11)),
    )
    melody = (0, 3, 7, None, 10, 7, 3, None, 7, 10, 12, None, 10, 7, 3, None)
    total_samples = round(duration * SAMPLE_RATE)
    output: list[float] = []
    for index in range(total_samples):
        time = index / SAMPLE_RATE
        root_note, chord_intervals = chords[int(time // bar_length) % len(chords)]
        root = midi_to_hz(root_note)
        pad = sum(
            math.sin(math.tau * midi_to_hz(root_note + interval) * time) * amplitude
            for interval, amplitude in zip(chord_intervals, (0.11, 0.075, 0.055, 0.035), strict=True)
        )
        pad += math.sin(math.tau * root * 0.5 * time) * 0.07
        hum = math.sin(math.tau * 54.0 * time) * 0.035

        beat_index = int(time / beat_length)
        beat_time = time - beat_index * beat_length
        kick = 0.0
        snare = 0.0
        if beat_index % 4 in (0, 2):
            kick = math.sin(math.tau * (105.0 - beat_time * 45.0) * beat_time) * math.exp(-beat_time * 19.0) * 0.13
        elif beat_index % 4 in (1, 3):
            snare = (rng.random() * 2.0 - 1.0) * math.exp(-beat_time * 34.0) * 0.045

        half_length = beat_length / 2.0
        half_index = int(time / half_length)
        half_time = time - half_index * half_length
        hat = (rng.random() * 2.0 - 1.0) * math.exp(-half_time * 70.0) * 0.012

        melody_step = int(time / half_length) % len(melody)
        melody_interval = melody[melody_step]
        pluck = 0.0
        if melody_interval is not None:
            melody_frequency = midi_to_hz(root_note + 12 + melody_interval)
            pluck = math.sin(math.tau * melody_frequency * half_time) * math.exp(-half_time * 11.0) * 0.07

        texture = (rng.random() * 2.0 - 1.0) * 0.002
        fade = envelope(time, duration, 0.1, 0.1)
        output.append((pad + hum + kick + snare + hat + pluck + texture) * fade * 0.72)
    return output


def effect(duration: float, frequencies: tuple[float, ...], amplitude: float) -> list[float]:
    total_samples = round(duration * SAMPLE_RATE)
    samples: list[float] = []
    for index in range(total_samples):
        time = index / SAMPLE_RATE
        progress = time / duration
        frequency = frequencies[0] + (frequencies[-1] - frequencies[0]) * progress
        value = math.sin(math.tau * frequency * time) * amplitude
        value += math.sin(math.tau * frequency * 0.5 * time) * amplitude * 0.3
        samples.append(value * envelope(time, duration, 0.006, min(0.12, duration * 0.45)))
    return samples


def paper_flip() -> list[float]:
    rng = random.Random(19)
    duration = 0.18
    output: list[float] = []
    for index in range(round(duration * SAMPLE_RATE)):
        time = index / SAMPLE_RATE
        progress = time / duration
        noise = (rng.random() * 2.0 - 1.0) * (0.34 - progress * 0.2)
        hiss = math.sin(math.tau * (650.0 + progress * 1900.0) * time) * 0.08
        output.append((noise + hiss) * envelope(time, duration, 0.004, 0.08))
    return output


def low_click() -> list[float]:
    duration = 0.11
    output: list[float] = []
    for index in range(round(duration * SAMPLE_RATE)):
        time = index / SAMPLE_RATE
        body = math.sin(math.tau * 170.0 * time) * math.exp(-time * 32.0) * 0.46
        tick = math.sin(math.tau * (620.0 - time * 2200.0) * time) * math.exp(-time * 50.0) * 0.12
        output.append((body + tick) * envelope(time, duration, 0.003, 0.05))
    return output


def scroll_click() -> list[float]:
    duration = 0.09
    output: list[float] = []
    for index in range(round(duration * SAMPLE_RATE)):
        time = index / SAMPLE_RATE
        tone = math.sin(math.tau * (310.0 - time * 900.0) * time) * math.exp(-time * 40.0) * 0.24
        output.append(tone * envelope(time, duration, 0.003, 0.045))
    return output


def stamp() -> list[float]:
    duration = 0.3
    output: list[float] = []
    for index in range(round(duration * SAMPLE_RATE)):
        time = index / SAMPLE_RATE
        thump = math.sin(math.tau * 105.0 * time) * math.exp(-time * 22.0) * 0.72
        click = math.sin(math.tau * 840.0 * time) * math.exp(-time * 52.0) * 0.18
        output.append(thump + click)
    return output


def main() -> None:
    write_wav(MUSIC_DIR / "audit_ambient.wav", ambient_track())
    write_wav(SFX_DIR / "ui_click.wav", low_click())
    write_wav(SFX_DIR / "paper_flip.wav", paper_flip())
    write_wav(SFX_DIR / "stamp.wav", stamp())
    write_wav(SFX_DIR / "hint.wav", effect(0.22, (540.0, 880.0), 0.24))
    write_wav(SFX_DIR / "confirm.wav", effect(0.32, (440.0, 760.0), 0.26))
    write_wav(SFX_DIR / "scroll.wav", scroll_click())
    print("Audio generated in assets/music and assets/sfx")


if __name__ == "__main__":
    main()
