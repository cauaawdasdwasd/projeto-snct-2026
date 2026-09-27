"""Exports the six protocol films to assets/videos/<slug>.mp4 (needs ffmpeg).

    python scripts/render_protocol_videos.py [slug ...]

The game itself does not need these files: it draws the same films live. The MP4s
are for sharing, slides and the school presentation.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pygame  # noqa: E402

from src.rendering.protocol_films import DURATION, FILM_CLASSES, FILM_SIZE, create_film  # noqa: E402

FPS = 30
SCALE = 2


def render(slug: str, ffmpeg: str) -> Path:
    portrait = pygame.image.load(ROOT / "assets" / "protocols" / f"{slug}.png").convert_alpha()
    film = create_film(slug, portrait)
    target = ROOT / "assets" / "videos" / f"{slug}.mp4"
    width, height = FILM_SIZE[0] * SCALE, FILM_SIZE[1] * SCALE
    command = [
        ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{width}x{height}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", str(target),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    assert process.stdin is not None
    for frame in range(int(DURATION * FPS) + 1):
        surface = film.render(frame / FPS)
        scaled = pygame.transform.scale(surface, (width, height))
        process.stdin.write(pygame.image.tobytes(scaled, "RGB"))
    process.stdin.close()
    process.wait()
    return target


def main() -> None:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise SystemExit("ffmpeg não encontrado. Instale-o para exportar os MP4.")
    pygame.init()
    pygame.display.set_mode((100, 100))
    slugs = sys.argv[1:] or list(FILM_CLASSES)
    for slug in slugs:
        print(render(slug, ffmpeg).relative_to(ROOT))


if __name__ == "__main__":
    main()
