from __future__ import annotations

import os
import random
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "assets" / "stamp_marks"

MARKS = {
    "approve": ("APROVADO", (72, 130, 54)),
    "deny": ("NEGADO", (174, 52, 45)),
    "review": ("REVISÃO HUMANA", (169, 112, 24)),
    "violation": ("VIOLAÇÃO", (112, 58, 125)),
}


def generate_mark(label: str, color: tuple[int, int, int], seed: int) -> pygame.Surface:
    surface = pygame.Surface((420, 150), pygame.SRCALPHA)
    font_size = 45 if len(label) < 12 else 34
    font = pygame.font.SysFont(("Consolas", "Courier New", "monospace"), font_size, bold=True)
    ink = (*color, 228)

    pygame.draw.rect(surface, ink, (9, 9, 402, 132), 7)
    pygame.draw.rect(surface, (*color, 150), (18, 18, 384, 114), 3)

    rendered = font.render(label, False, color)
    rendered.set_alpha(224)
    surface.blit(rendered, rendered.get_rect(center=surface.get_rect().center))

    randomizer = random.Random(seed)
    for _ in range(180):
        x = randomizer.randrange(8, 412)
        y = randomizer.randrange(8, 142)
        if randomizer.random() < 0.65:
            pygame.draw.rect(surface, (0, 0, 0, randomizer.randrange(18, 65)), (x, y, 2, 2))
        else:
            pygame.draw.rect(surface, (*color, randomizer.randrange(35, 95)), (x, y, 2, 2))

    return surface


def main() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for index, (stamp_id, (label, color)) in enumerate(MARKS.items(), start=1):
        pygame.image.save(generate_mark(label, color, index * 7919), OUTPUT_DIR / f"{stamp_id}.png")

    pygame.quit()


if __name__ == "__main__":
    main()

