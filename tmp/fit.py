import os
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.display.set_mode((64,64))
from src.gameplay.cases import CASE_BANK
from src.gameplay.document_renderer import DocumentRenderer
r=DocumentRenderer()
for c in CASE_BANK:
    for d in c.documents:
        if d.image or d.image_art: continue
        n=r.info_rows_that_fit(d)
        if n!=len(d.info): print(c.case_id,d.document_id,n,len(d.info),[ (f.label[:10],len(f.value)) for f in d.fields])
