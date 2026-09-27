import os, random
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.display.set_mode((100,100))
from pathlib import Path
from src.minigames.captchas import RotateCaptcha
root=Path("assets")
sheet=pygame.Surface((720*4,360*3))
seen=set()
i=0
seed=0
while len(seen)<12 and seed<200:
    c=RotateCaptcha(random.Random(seed),root)
    seed+=1
    if c.instruction in seen: continue
    seen.add(c.instruction)
    c.angle=25
    s=pygame.Surface((720,360)); s.fill((17,23,20)); c.render(s)
    sheet.blit(s,((i%4)*720,(i//4)*360))
    i+=1
pygame.image.save(sheet,"tmp/rotate_all.png")
print(sorted(seen))
