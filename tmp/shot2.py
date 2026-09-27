import os, random
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.display.set_mode((100,100))
from pathlib import Path
from src.minigames.captchas import create_captcha
root=Path("assets")
sheet=pygame.Surface((1440,720))
for i in range(4):
    c=create_captcha("rotate",random.Random(i),root)
    c.angle=(30*i)+20
    s=pygame.Surface((720,360)); s.fill((17,23,20)); c.render(s)
    sheet.blit(s,((i%2)*720,(i//2)*360))
pygame.image.save(sheet,"tmp/caps.png")
