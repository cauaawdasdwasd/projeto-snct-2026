import pygame

from src.gameplay.cases import CASES, PLAYABLE_CASES, TUTORIAL_CASE
from src.gameplay.document_renderer import EvidenceRegion
from src.scenes.audit import AuditScene


class _ComparisonDocument:
    def __init__(self, document_id: str) -> None:
        self.document_id = document_id
        self.marked: set[str] = set()

    def set_evidence_marked(self, evidence_key: str, marked: bool) -> None:
        if marked:
            self.marked.add(evidence_key)


def test_every_case_has_a_clear_question_and_focused_document_set() -> None:
    for case in CASES:
        document_ids = {document.document_id for document in case.documents}

        assert case.review_question.endswith("?")
        assert 2 <= len(case.key_document_ids) <= 4
        assert set(case.key_document_ids) <= document_ids
        assert len(document_ids - set(case.key_document_ids)) <= 2


def test_required_evidence_is_found_in_key_documents() -> None:
    for case in CASES:
        key_evidence = {
            field.evidence_key
            for document in case.documents
            if document.document_id in case.key_document_ids
            for field in document.fields
            if field.evidence_key is not None
        }

        assert set(case.evidence_summary.required_keys) <= key_evidence


def test_first_case_drops_the_redundant_promotion_request() -> None:
    first_case = CASES[0]

    assert len(first_case.documents) == 3
    assert "promotion" not in {document.document_id for document in first_case.documents}
    assert first_case.evidence_summary.required_keys == ("employee_id", "record_id")
    assert TUTORIAL_CASE is first_case
    assert TUTORIAL_CASE.is_tutorial
    assert TUTORIAL_CASE not in PLAYABLE_CASES
    assert len(PLAYABLE_CASES) == 5


def test_direct_document_comparison_marks_equal_and_different_values() -> None:
    scene = AuditScene.__new__(AuditScene)
    scene.evidence_notes = {}
    scene.comparison_anchor = None
    scene.comparison_result = None
    scene._play_sound = lambda *_args, **_kwargs: None
    first_document = _ComparisonDocument("first")
    second_document = _ComparisonDocument("second")

    scene._handle_evidence_comparison(
        first_document,
        EvidenceRegion("first_id", pygame.Rect(0, 0, 10, 10), "Primeiro ID", "LAB-4827O"),
    )
    scene._handle_evidence_comparison(
        second_document,
        EvidenceRegion("same_id", pygame.Rect(0, 0, 10, 10), "Mesmo ID", " lab-4827o "),
    )
    assert scene.comparison_result is not None
    assert scene.comparison_result[2] is True

    scene._handle_evidence_comparison(
        first_document,
        EvidenceRegion("letter_o", pygame.Rect(0, 0, 10, 10), "Letra O", "LAB-4827O"),
    )
    scene._handle_evidence_comparison(
        second_document,
        EvidenceRegion("number_zero", pygame.Rect(0, 0, 10, 10), "Número zero", "LAB-48270"),
    )
    assert scene.comparison_result is not None
    assert scene.comparison_result[2] is False
    assert set(scene.evidence_notes) >= {"first_id", "same_id", "letter_o", "number_zero"}
