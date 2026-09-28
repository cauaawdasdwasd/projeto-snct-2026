import os
os.environ["SDL_VIDEODRIVER"]="dummy"; os.environ["SDL_AUDIODRIVER"]="dummy"
import pygame; pygame.init(); pygame.font.init(); pygame.display.set_mode((100,100))
from src.gameplay.cases import CASE_BANK
from src.gameplay.document_renderer import DocumentRenderer

r = DocumentRenderer()
targets = []
for case in CASE_BANK:
    for doc in case.documents:
        if doc.organization.upper() == "RH":
            targets.append((case, doc))
print(len(targets), "docs with org RH")
docs = [r.render_case(case)[[d.document_id for d in case.documents].index(doc.document_id)] for case, doc in targets[:8]]
sheet = pygame.Surface((300*4, 90*2))
for i, rd in enumerate(docs):
    crop = rd.surface.subsurface((300, 640, 300, 90))
    sheet.blit(crop, ((i % 4) * 300, (i // 4) * 90))
pygame.image.save(sheet, "tmp/signatures.png")
