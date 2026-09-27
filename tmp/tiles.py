import os
os.environ["SDL_VIDEODRIVER"]="dummy"
import pygame; pygame.init(); pygame.display.set_mode((64,64))
from pathlib import Path
from src.minigames.common import load_folder
imgs=load_folder(Path("assets"),"captcha/tiles")
sh=pygame.Surface((8*140,2*140))
for i,im in enumerate(imgs): sh.blit(pygame.transform.smoothscale(im,(136,136)),((i%8)*140,(i//8)*140))
pygame.image.save(sh,"tmp/tiles.png")
