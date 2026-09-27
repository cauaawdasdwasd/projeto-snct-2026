import os, sys
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.display.set_mode((100,100))
from src.gameplay.cases import CASE_BANK
from src.gameplay.document_renderer import DocumentRenderer
ids = sys.argv[1:] or ["case_32"]
r = DocumentRenderer()
docs=[]
for cid in ids:
    case = next(c for c in CASE_BANK if c.case_id==cid)
    docs += list(r.render_case(case)[:-1])
sheet = pygame.Surface((620*len(docs)//2+0, 800*1)) if False else pygame.Surface((620*len(docs), 800))
for i,d in enumerate(docs): sheet.blit(d.surface,(i*620,0))
pygame.image.save(sheet,"tmp/docs.png")
print(len(docs))
