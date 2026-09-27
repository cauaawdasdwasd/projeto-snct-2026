import os, random
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.display.set_mode((100,100))
from src.minigames.popups import PopupSwarm
swarm = PopupSwarm(pygame.Rect(20,20,800,400), random.Random(3))
swarm.spawn(4)
for p in swarm.popups: p.age = 1.0; p.corner = 1  # bottom-left corner: where decoy used to cover the X
surface = pygame.Surface((900, 500)); surface.fill((20,26,22))
swarm.render(surface)
pygame.image.save(surface, "tmp/popups.png")
