import os
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.font.init(); pygame.display.set_mode((100,100))
from pathlib import Path
from src.gameplay.cases import CASE_BANK, CaseResult
from src.core.assets import AssetManager
from src.ui.newspaper import FinalNewspaper

assets = AssetManager(Path("assets"))
case = next(c for c in CASE_BANK if c.case_id == "case_32")
images = {case.newspaper_correct.image_asset: assets.load_image(case.newspaper_correct.image_asset)}
paper = FinalNewspaper(images)
paper.open([CaseResult(case, "approve", False)])
surface = pygame.Surface((1600, 720)); surface.fill((10,10,10))
paper.render(surface)
pygame.image.save(surface, "tmp/news_real.png")
