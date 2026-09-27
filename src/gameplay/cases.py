from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentField:
    label: str
    value: str
    evidence_key: str | None = None
    evidence_note: str | None = None
    highlight: bool = False


@dataclass(frozen=True)
class CaseDocumentData:
    document_id: str
    title: str
    organization: str
    accent: str
    fields: tuple[DocumentField, ...]
    body_title: str = ""
    body: str = ""
    show_portrait: bool = False
    issuer: str = ""
    theme: str = ""
    info: tuple[tuple[str, str], ...] = ()
    blocks: tuple[dict, ...] = ()
    image: str = ""
    image_caption: str = ""
    image_art: str = ""
    inset: str = ""


@dataclass(frozen=True)
class DataSource:
    label: str
    document_id: str


@dataclass(frozen=True)
class EvidenceSummary:
    required_keys: tuple[str, ...]
    lines: tuple[str, ...]
    conclusion: str


@dataclass(frozen=True)
class AIDecision:
    verdict: str
    confidence: str
    reason: str
    model_name: str
    source_document: str
    evidence_label: str
    evidence_value: str
    evidence_key: str
    evidence_note: str


@dataclass(frozen=True)
class NewspaperArticle:
    headline: str
    body: str
    image_asset: str


@dataclass(frozen=True)
class SearchRecord:
    title: str
    source: str
    snippet: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class CaseLink:
    """Two interactive data that really relate to each other, and what they show."""

    key_a: str
    key_b: str
    kind: str
    text: str


@dataclass(frozen=True)
class AuditCase:
    case_id: str
    sequence: int
    protocol_focus: str
    title: str
    briefing: str
    hint: str
    subject_label: str
    subject_name: str
    decision_object: str
    newspaper_section: str
    portrait_asset: str | None
    documents: tuple[CaseDocumentData, ...]
    data_sources: tuple[DataSource, ...]
    evidence_summary: EvidenceSummary
    ai_decision: AIDecision
    correct_stamp: str
    correct_feedback: str
    incorrect_feedback: str
    newspaper_correct: NewspaperArticle
    newspaper_incorrect: NewspaperArticle
    search_records: tuple[SearchRecord, ...] = ()
    review_question: str = ""
    key_document_ids: tuple[str, ...] = ()
    is_tutorial: bool = False
    links: tuple[CaseLink, ...] = ()
    tutorial_pairs: tuple[tuple[str, str], ...] = ()
    explanation: str = ""
    turn: int = 0
    story: str = ""
    attention: str = ""
    conclusions: tuple[tuple[str, bool], ...] = ()


@dataclass(frozen=True)
class CaseResult:
    case: AuditCase
    selected_stamp: str
    correct: bool
    conclusions_correct: int = 0
    conclusions_total: int = 0


CASE_01 = AuditCase(
    case_id="case_01",
    sequence=1,
    protocol_focus="grace_hopper",
    title="O ou zero?",
    briefing=(
        "A IA aprovou a promoção de Ana porque decidiu que uma ocorrência grave pertence a "
        "outro funcionário. Compare os IDs antes de aceitar."
    ),
    hint="Olhe o último caractere: a letra O e o número 0 parecem iguais, mas não são.",
    subject_label="FUNCIONÁRIA",
    subject_name="Ana Ribeiro",
    decision_object="Promoção bloqueada pela IA",
    newspaper_section="TRABALHO",
    portrait_asset="cases/case_01/ana_ribeiro.png",
    documents=(
        CaseDocumentData(
            "profile",
            "Ficha da Ana",
            "NÚCLEO ORBITAL DE PESQUISA",
            "olive",
            (
                DocumentField("NOME", "Ana Ribeiro"),
                DocumentField("ID FUNCIONAL", "LAB-4827O", "employee_id", "ID da Ana: termina na letra O", True),
                DocumentField("CARGO", "Técnica de Laboratório"),
                DocumentField("SETOR / TURNO", "Controle / Diurno"),
            ),
            "RESUMO PROFISSIONAL",
            "Desempenho 94%, nenhuma falta e nenhuma ocorrência nos últimos 12 meses.",
            show_portrait=True,
            issuer="Núcleo Orbital de Pesquisa",
        ),
        CaseDocumentData(
            "directory",
            "Lista de funcionários",
            "LISTA DE FUNCIONÁRIOS",
            "blue",
            (
                DocumentField("FUNCIONÁRIA", "Ana Ribeiro"),
                DocumentField("ID / TURNO", "LAB-4827O / DIURNO"),
                DocumentField("FUNCIONÁRIO", "Artur Ribeiro"),
                DocumentField("ID / TURNO", "LAB-48270 / NOTURNO", "directory_artur_id", "ID do Artur: termina no número zero", True),
                DocumentField("SETOR DE ANA", "Controle de Qualidade"),
                DocumentField("SETOR DE ARTUR", "Controle de Qualidade"),
            ),
            "DOIS FUNCIONÁRIOS, MESMO SOBRENOME",
            "Lista atualizada em 08/06/2026 às 04:20.",
            issuer="Central de funcionários",
        ),
        CaseDocumentData(
            "disciplinary",
            "Ocorrências",
            "SEGURANÇA DO TRABALHO",
            "red",
            (
                DocumentField("NOME ABREVIADO", "A. Ribeiro"),
                DocumentField("ID DA OCORRÊNCIA", "LAB-48270", "record_id", "A ocorrência é do ID LAB-48270", True),
                DocumentField("TURNO", "Noturno"),
                DocumentField("DATA", "07/06/2026 - 23:40"),
                DocumentField("PROTOCOLO", "RD-0607-118"),
                DocumentField("GRAVIDADE", "Alta"),
            ),
            "O QUE ACONTECEU",
            "Desativação indevida do controle de temperatura durante o turno noturno.",
            issuer="Segurança do trabalho",
        ),
    ),
    data_sources=(
        DataSource("Ficha da Ana", "profile"),
        DataSource("Lista de funcionários", "directory"),
        DataSource("Ocorrências", "disciplinary"),
    ),
    evidence_summary=EvidenceSummary(
        ("employee_id", "record_id", "directory_artur_id"),
        ("ID da Ana: LAB-4827O", "ID da ocorrência: LAB-48270", "Letra O não é número 0"),
        "A IA separou corretamente os dois funcionários. A decisão pode ser aprovada.",
    ),
    ai_decision=AIDecision("APROVAR PROMOÇÃO", "96%", "O ID de Ana termina em O. A ocorrência termina em 0; por isso a IA ignorou a ocorrência.", "ORÁCULO-RH v2.4", "Ficha da Ana e Ocorrências", "IDS COMPARADOS", "LAB-4827O ≠ LAB-48270", "ai_record_id", "A IA tratou os dois códigos como pessoas diferentes."),
    correct_stamp="approve",
    correct_feedback="A IA separou corretamente a letra O do número zero.",
    incorrect_feedback="A promoção foi bloqueada mesmo sem ocorrência no ID de Ana.",
    newspaper_correct=NewspaperArticle("AUDITORIA IMPEDE QUE UM ZERO CUSTE A PROMOÇÃO DE ANA RIBEIRO", "A conferência dos IDs separou dois funcionários com o mesmo sobrenome. A ocorrência voltou ao prontuário correto e a promoção de Ana será reavaliada.", "newspaper/identity_correct_v2.png"),
    newspaper_incorrect=NewspaperArticle("ERRO ENTRE O E ZERO CUSTA PROMOÇÃO A ANA; EMPRESA PAGARÁ R$ 620 MIL", "A companhia confirmou a punição usando a ocorrência de Artur Ribeiro. Ana perdeu salário e progressão por oito meses antes de a troca ser descoberta na Justiça do Trabalho.", "newspaper/identity_wrong_v2.png"),
    search_records=(
        SearchRecord("Ana Ribeiro — LAB-4827O", "Lista de funcionários", "Técnica de laboratório, Controle de Qualidade, turno diurno. Cadastro ativo sem ocorrência.", ("ana", "ribeiro", "lab-4827o", "diurno", "controle")),
        SearchRecord("Artur Ribeiro — LAB-48270", "Lista de funcionários", "Técnico de laboratório, Controle de Qualidade, turno noturno. Há uma ocorrência ligada ao ID.", ("artur", "ribeiro", "lab-48270", "noturno", "controle")),
        SearchRecord("RD-0607-118 — A. Ribeiro", "Segurança do trabalho", "Ocorrência registrada às 23:40 para o ID LAB-48270. Turno noturno.", ("rd-0607-118", "a ribeiro", "lab-48270", "ocorrencia", "23:40")),
        SearchRecord("Amanda Ribeiro — LAB-4827Q", "Lista de funcionários", "Assistente administrativa, setor de Compras. Não trabalha no Núcleo Orbital.", ("amanda", "ribeiro", "lab-4827q", "compras")),
        SearchRecord("PR-204-77 — pedido de promoção", "Comitê de carreira", "Pedido da ID LAB-4827O. Vaga de Analista de Dados Jr., nota 94/100.", ("pr-204-77", "lab-4827o", "promocao", "analista")),
        SearchRecord("LAB-48270 — histórico de acesso", "Controle de temperatura", "Crachá usado no laboratório durante o turno noturno de 07/06/2026.", ("lab-48270", "acesso", "temperatura", "07/06/2026")),
        SearchRecord("LAB-4827O — entrada no sistema", "Portal de pessoas", "Último acesso às 16:12. A letra final do identificador é O.", ("lab-4827o", "autenticacao", "letra o", "16:12")),
    ),
    review_question="A ocorrência pertence mesmo a Ana?",
    key_document_ids=("profile", "disciplinary", "directory"),
    is_tutorial=True,
    links=(
        CaseLink("employee_id", "record_id", "different", "O ID de Ana e o ID da ocorrência não são o mesmo."),
        CaseLink("directory_artur_id", "record_id", "equal", "O ID da ocorrência é o mesmo que o de Artur."),
        CaseLink("employee_id", "directory_artur_id", "different", "Ana e Artur têm IDs diferentes."),
    ),
    tutorial_pairs=(("employee_id", "record_id"), ("directory_artur_id", "record_id")),
    explanation="A IA separou corretamente os dois funcionários. A decisão pode ser aprovada.",
    story=(
        "Você acabou de assumir o turno na Sob Análise. A primeira auditoria é no Núcleo Orbital de Pesquisa: "
        "a IA aprovou a promoção da técnica Ana Ribeiro porque concluiu que uma ocorrência grave, registrada "
        "de madrugada, não era dela. Só que a empresa tem dois funcionários com o mesmo sobrenome no mesmo setor, "
        "um de dia e outro de noite, e os dois têm códigos de identificação quase iguais."
    ),
    attention=(
        "Neste treinamento o jogo aponta cada passo com um brilho amarelo. Leia os códigos devagar: em alguns "
        "tipos de letra, a letra O e o número zero são muito parecidos."
    ),
    conclusions=(
        ("O ID da Ana termina na letra O.", True),
        ("A ocorrência é do mesmo ID que o do Artur.", True),
        ("Para o computador, a letra O e o número 0 são iguais.", False),
        ("A IA misturou os dois funcionários.", False),
    ),
)


TUTORIAL_CASE = CASE_01

SHIFT_SIZE = 5
BANK_PATH = Path(__file__).resolve().parents[2] / "data" / "case_bank.json"


def _load_extras() -> dict:
    path = BANK_PATH.parent / "case_docs_extra.json"
    if not path.is_file():
        return {}
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


DOC_EXTRAS = _load_extras()


def _case_from_json(raw: dict) -> AuditCase:
    extras = DOC_EXTRAS.get(raw["id"], {})
    documents = tuple(
        CaseDocumentData(
            document_id=doc["id"],
            title=doc["title"],
            organization=doc["org"].upper(),
            accent=doc["accent"],
            issuer=doc["org"],
            body_title="O QUE ESTE PAPEL MOSTRA",
            body=doc["guide"],
            theme=extras.get(doc["id"], {}).get("theme", ""),
            info=tuple((label, value) for label, value in extras.get(doc["id"], {}).get("info", ())),
            image=extras.get(doc["id"], {}).get("image", ""),
            image_caption=extras.get(doc["id"], {}).get("caption", ""),
            image_art=extras.get(doc["id"], {}).get("art", ""),
            inset=extras.get(doc["id"], {}).get("inset", ""),
            blocks=tuple(extras.get(doc["id"], {}).get("blocks", ())),
            fields=tuple(
                DocumentField(
                    field["label"].upper(),
                    field["value"],
                    field["key"],
                    field["note"],
                    bool(field["key"]),
                )
                for field in doc["fields"]
            ),
        )
        for doc in raw["documents"]
    )
    ai = raw["ai"]
    return AuditCase(
        case_id=raw["id"],
        sequence=raw["sequence"],
        protocol_focus=raw["protocol"],
        title=raw["title"],
        briefing=raw["briefing"],
        hint=raw["hint"],
        subject_label=raw["subject_label"].upper(),
        subject_name=raw["subject_name"],
        decision_object=raw["decision_object"],
        newspaper_section=raw["section"].upper(),
        portrait_asset=None,
        documents=documents,
        data_sources=tuple(DataSource(doc.title, doc.document_id) for doc in documents),
        evidence_summary=EvidenceSummary(
            tuple(raw["required_keys"]),
            tuple(raw["evidence_lines"]),
            raw["explanation"],
        ),
        ai_decision=AIDecision(
            ai["verdict"].upper(),
            ai["confidence"],
            ai["reason"],
            ai["model"],
            ai["source"],
            ai["evidence_label"].upper(),
            ai["evidence_value"],
            ai["evidence_key"],
            ai["evidence_note"],
        ),
        correct_stamp=raw["correct_stamp"],
        correct_feedback=raw["feedback_correct"],
        incorrect_feedback=raw["feedback_wrong"],
        newspaper_correct=NewspaperArticle(raw["news_correct"]["headline"], raw["news_correct"]["body"], raw["news_correct"]["image"]),
        newspaper_incorrect=NewspaperArticle(raw["news_wrong"]["headline"], raw["news_wrong"]["body"], raw["news_wrong"]["image"]),
        search_records=tuple(
            SearchRecord(r["title"], r["source"], r["snippet"], tuple(r["keywords"]))
            for r in raw["search"]
        ),
        review_question=raw["question"],
        key_document_ids=tuple(raw["key_documents"]),
        links=tuple(CaseLink(*link) for link in raw["links"]),
        explanation=raw["explanation"],
        turn=raw["turn"],
        story=raw["story"],
        attention=raw["attention"],
        conclusions=tuple((text, bool(truth)) for text, truth in raw["conclusions"]),
    )


def load_case_bank(path: Path = BANK_PATH) -> tuple[AuditCase, ...]:
    with path.open(encoding="utf-8") as handle:
        return tuple(_case_from_json(raw) for raw in json.load(handle)["cases"])


CASE_BANK = load_case_bank()
CASES = (TUTORIAL_CASE, *CASE_BANK)


def _turn_plan(count: int, rng) -> list[int]:
    """Which difficulty turn each case of a shift comes from, easiest first."""
    if count >= SHIFT_SIZE:
        return [1 + (index * SHIFT_SIZE) // count for index in range(count)]
    return sorted(rng.sample(range(1, SHIFT_SIZE + 1), count))


def pick_shift(seen: set[str], rng: random.Random | None = None, count: int = SHIFT_SIZE) -> list[AuditCase]:
    """Draw one case per difficulty turn (1..5) so the shift always escalates.

    `seen` holds the cases already played in this session. A turn only repeats a
    case once all ten of its candidates have been played.
    """
    rng = rng or random
    shift: list[AuditCase] = []
    for turn in _turn_plan(count, rng):
        candidates = [case for case in CASE_BANK if case.turn == turn and case not in shift]
        fresh = [case for case in candidates if case.case_id not in seen]
        if not fresh:
            seen.difference_update(case.case_id for case in candidates)
            fresh = candidates
        chosen = rng.choice(fresh)
        seen.add(chosen.case_id)
        shift.append(chosen)
    return shift
