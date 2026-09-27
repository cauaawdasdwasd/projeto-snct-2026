import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from src.gameplay.cases import CASE_BANK
from src.gameplay.document_renderer import DocumentRenderer


@pytest.fixture(scope="module")
def renderer():
    pygame.init()
    pygame.display.set_mode((64, 64))
    yield DocumentRenderer()
    pygame.quit()


def test_every_paper_has_its_own_layout():
    signatures = set()
    for case in CASE_BANK:
        for document in case.documents:
            assert document.blocks, (case.case_id, document.document_id)
            signatures.add(tuple(block["type"] for block in document.blocks))
    assert len(signatures) >= 20  # tables, chats, timelines, terminals, receipts, charts... not one template


def test_layouts_render_without_cut_text_and_keep_all_evidence(renderer):
    for case in CASE_BANK:
        rendered = renderer.render_case(case)
        assert len(rendered) == len(case.documents) + 1
        for document, paper in zip(case.documents, rendered):
            expected = {field.evidence_key for field in document.fields if field.evidence_key}
            found = {region.key for region in paper.evidence_regions}
            assert expected == found, (case.case_id, document.document_id, expected ^ found)
            for region in paper.evidence_regions:
                assert paper.surface.get_rect().contains(region.rect), (case.case_id, region.key)


def test_all_papers_keep_the_warm_beige_of_the_game(renderer):
    case = CASE_BANK[0]
    for paper in renderer.render_case(case)[:-1]:
        red, green, blue, _ = paper.surface.get_at((300, 780))
        assert red > green > blue  # warm paper, never a green or blue sheet


def test_picture_papers_still_render_an_image(renderer):
    case = next(c for c in CASE_BANK if c.case_id == "case_32")
    rendered = renderer.render_case(case)[0]
    assert rendered.image_rect is not None
