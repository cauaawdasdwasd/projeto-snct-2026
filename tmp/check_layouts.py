import os, sys
os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
import pygame; pygame.init(); pygame.display.set_mode((64, 64))
from src.gameplay.cases import CASE_BANK
from src.gameplay.document_renderer import DocumentRenderer

r = DocumentRenderer()
only = sys.argv[1:]
bad = 0
sheet = []
for case in CASE_BANK:
    if only and case.case_id not in only:
        continue
    for document in case.documents:
        one = type(case)(**{**case.__dict__, "documents": (document, case.documents[0] if document is not case.documents[0] else case.documents[1])}) if False else None
    try:
        rendered = r.render_case(case)
        sheet += [d.surface for d in rendered[:-1]]
    except Exception as exc:
        bad += 1
        print("FAIL", case.case_id, exc)
print("failures:", bad)
if only and sheet:
    out = pygame.Surface((620 * len(sheet), 800))
    for i, s in enumerate(sheet):
        out.blit(s, (i * 620, 0))
    pygame.image.save(out, "tmp/docs.png")
