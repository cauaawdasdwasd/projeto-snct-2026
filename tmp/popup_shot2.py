import os, random
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.display.set_mode((100,100))
from src.minigames.popups import PopupSwarm, POPUP_SIZE
swarm = PopupSwarm(pygame.Rect(20,20,40,40))  # force a tiny spawn area -> popup lands near (20,20)
swarm.spawn(1, decoys=False)
p = swarm.popups[0]
p.age = 1.0
p.decoy = True
p.corner = 2  # bottom-left: decoy_rect and close_rect both live at the bottom
surface = pygame.Surface((420, 220)); surface.fill((20,26,22))
swarm.render(surface)
pygame.image.save(surface, "tmp/popup_overlap.png")
