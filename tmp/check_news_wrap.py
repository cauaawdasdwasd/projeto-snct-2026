import os
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.font.init(); pygame.display.set_mode((100,100))
from src.gameplay.cases import CASE_BANK
from src.ui.newspaper import FinalNewspaper, HEADLINE... 
