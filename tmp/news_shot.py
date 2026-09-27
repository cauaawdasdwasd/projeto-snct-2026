import os
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.font.init(); pygame.display.set_mode((100,100))
from src.gameplay.cases import CASE_BANK, CaseResult
from src.gameplay import document_art
from src.ui.newspaper import FinalNewspaper, HERO_IMAGE_RECT

case = next(c for c in CASE_BANK if c.case_id == "case_32")
images = {
    case.newspaper_correct.image_asset: document_art.draw_newsroom_placeholder(HERO_IMAGE_RECT.size, case.newspaper_correct.image_asset),
}
paper = FinalNewspaper(images)
paper.open([CaseResult(case, "approve", False)])
surface = pygame.Surface((1600, 720))
surface.fill((10, 10, 10))
paper.render(surface)
pygame.image.save(surface, "tmp/news_wrong.png")

paper.open([CaseResult(case, case.correct_stamp, True)])
surface2 = pygame.Surface((1600, 720))
surface2.fill((10, 10, 10))
paper.render(surface2)
pygame.image.save(surface2, "tmp/news_correct.png")
