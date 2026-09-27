import os
import random

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.core.settings import ASSETS_DIR
from src.gameplay.cases import (
    CASE_BANK,
    CASES,
    SHIFT_SIZE,
    TUTORIAL_CASE,
    pick_shift,
)
from src.gameplay.comparison_links import MAX_TEXT_LENGTH
from src.gameplay.document_renderer import DocumentRenderer, EvidenceRegion
from src.gameplay.protocols import PROTOCOLS
from src.scenes.audit import AuditScene

STAMPS = {"approve", "deny", "review", "violation"}
HARD_WORDS = ("disciplinar", "diretório", "manifesto", "matriz", "override", "trigger", "sla", "log ")


def evidence_keys(case) -> set[str]:
    return {
        field.evidence_key
        for document in case.documents
        for field in document.fields
        if field.evidence_key
    }


def test_bank_has_fifty_unique_cases_spread_over_five_turns() -> None:
    assert len(CASE_BANK) == 50
    assert len({case.case_id for case in CASE_BANK}) == 50
    for turn in range(1, 6):
        assert sum(1 for case in CASE_BANK if case.turn == turn) == 10
    assert TUTORIAL_CASE not in CASE_BANK
    assert TUTORIAL_CASE.is_tutorial
    assert not any(case.is_tutorial for case in CASE_BANK)


def test_every_case_is_complete_and_valid() -> None:
    protocol_ids = {protocol.slug for protocol in PROTOCOLS}
    for case in CASES:
        assert case.review_question.endswith("?"), case.case_id
        assert case.correct_stamp in STAMPS, case.case_id
        assert case.ai_decision.verdict and case.ai_decision.reason, case.case_id
        assert case.explanation, case.case_id
        assert 2 <= len(case.documents) <= 4, case.case_id
        assert case.protocol_focus in protocol_ids, case.case_id


def test_every_document_and_every_interactive_field_is_useful() -> None:
    for case in CASES:
        document_ids = {document.document_id for document in case.documents}
        assert {source.document_id for source in case.data_sources} == document_ids, case.case_id
        assert set(case.key_document_ids) == document_ids, case.case_id

        keys = evidence_keys(case)
        linked = {key for link in case.links for key in (link.key_a, link.key_b)}
        for document in case.documents:
            own = {f.evidence_key for f in document.fields if f.evidence_key}
            assert own, f"{case.case_id}: {document.title} has nothing to compare"
        assert keys <= linked, (case.case_id, keys - linked)
        assert set(case.evidence_summary.required_keys) == keys, case.case_id
        for link in case.links:
            assert {link.key_a, link.key_b} <= keys, (case.case_id, link)
            assert link.kind in {"equal", "different", "related"}
            assert len(link.text) <= MAX_TEXT_LENGTH, link.text


def test_names_stay_simple() -> None:
    for case in CASES:
        names = [document.title for document in case.documents]
        names += [field.label for document in case.documents for field in document.fields]
        names += [source.label for source in case.data_sources]
        for name in names:
            assert not any(word in name.lower() for word in HARD_WORDS), (case.case_id, name)


def test_every_case_renders_on_paper() -> None:
    pygame.font.init()
    renderer = DocumentRenderer()
    portrait = pygame.Surface((190, 220))
    for case in CASES:
        rendered = renderer.render_case(case, portrait if case.portrait_asset else None)
        assert len(rendered) == len(case.documents) + 1
        regions = sum(len(document.evidence_regions) for document in rendered)
        assert regions == len(evidence_keys(case)), case.case_id


def test_training_is_scripted_and_uses_all_three_documents() -> None:
    case = TUTORIAL_CASE
    assert [d.document_id for d in case.documents] == ["profile", "directory", "disciplinary"]
    assert {d.title for d in case.documents} == {"Ficha da Ana", "Lista de funcionários", "Ocorrências"}
    link_pairs = {frozenset((link.key_a, link.key_b)) for link in case.links}
    assert case.tutorial_pairs
    for pair in case.tutorial_pairs:
        assert frozenset(pair) in link_pairs


def test_shift_draws_one_case_per_turn_and_avoids_repeats() -> None:
    seen: set[str] = set()
    rng = random.Random(7)
    played: list[str] = []
    for _ in range(10):
        shift = pick_shift(seen, rng)
        assert len(shift) == SHIFT_SIZE
        assert [case.turn for case in shift] == [1, 2, 3, 4, 5]
        played.extend(case.case_id for case in shift)
    # ten games exhaust the ten candidates of every turn exactly once
    assert len(set(played)) == 50
    # the next draw starts over without failing
    assert len(pick_shift(seen, rng)) == SHIFT_SIZE


class _ComparisonDocument:
    def __init__(self, document_id: str) -> None:
        self.document_id = document_id
        self.marked: set[str] = set()

    def set_evidence_marked(self, evidence_key: str, marked: bool) -> None:
        if marked:
            self.marked.add(evidence_key)


def _comparison_scene(case) -> tuple[AuditScene, dict[str, "_ComparisonDocument"]]:
    scene = AuditScene.__new__(AuditScene)
    scene.case = case
    scene.evidence_notes = {}
    scene.completed_pairs = set()
    scene.comparison_anchor = None
    scene.comparison_result = None
    scene._play_sound = lambda *_args, **_kwargs: None
    scene.ai_decision_panel = type("Panel", (), {"scroll_to_end": lambda self: None})()
    documents = {"profile": _ComparisonDocument("profile"), "disciplinary": _ComparisonDocument("disciplinary")}
    scene._get_document = documents.__getitem__
    return scene, documents


def _compare(scene, documents, first, second) -> None:
    for document_id, key, value in (first, second):
        scene._handle_evidence_comparison(
            documents[document_id],
            EvidenceRegion(key, pygame.Rect(0, 0, 10, 10), f"nota {key}", value),
        )


def test_related_comparison_reports_link_and_records_evidence() -> None:
    scene, documents = _comparison_scene(TUTORIAL_CASE)
    _compare(
        scene,
        documents,
        ("profile", "employee_id", "LAB-4827O"),
        ("disciplinary", "record_id", "LAB-48270"),
    )
    assert scene.comparison_result is not None
    assert scene.comparison_result[2].kind == "different"
    assert set(scene.evidence_notes) == {"employee_id", "record_id"}
    assert frozenset(("employee_id", "record_id")) in scene.completed_pairs


def test_unknown_pair_says_no_link_and_does_not_count_as_evidence() -> None:
    scene, documents = _comparison_scene(TUTORIAL_CASE)
    _compare(
        scene,
        documents,
        ("profile", "employee_id", "LAB-4827O"),
        ("disciplinary", "not_a_real_key", "80%"),
    )
    assert scene.comparison_result is not None
    assert scene.comparison_result[2].kind == "none"
    assert scene.evidence_notes == {}
    assert scene.completed_pairs == set()
    assert documents["profile"].marked == set()
