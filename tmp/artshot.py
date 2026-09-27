import os
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.display.set_mode((64,64))
from src.gameplay import document_art as a
kinds=list(a.ARTS)
sheet=pygame.Surface((1100,(len(kinds)+1)//2*138))
for i,k in enumerate(kinds):
    sheet.blit(a.draw_art(k,(544,128),k),((i%2)*550,(i//2)*138))
pygame.image.save(sheet,"tmp/arts.png")
