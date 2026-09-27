"""Builds data/case_bank.json from the two design documents.

    python scripts/build_case_bank.py

Sources:
  - Casos (Mariah)/casos mariah.md          -> case_07 .. case_31
  - Casos-Leticia/25 Casos - ... .md         -> case_32 .. case_56

Rules applied here (see README, "Banco de casos"):
  * every document that reaches the desk carries at least one field that matters;
    papers without an "Evidência" are dropped;
  * only fields that matter for the case are interactive (they get an evidence key);
  * every pair of interactive fields from different documents is a real link, so
    the player never compares data that have nothing to do with each other;
  * difficult words are replaced by simple ones (TITLE_SIMPLIFICATIONS).
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from newspaper_content import NEWS  # noqa: E402  (each case's own headline + body, see that file)

ROOT = Path(__file__).resolve().parents[1]
MARIAH = ROOT / "Casos (Mariah)" / "casos mariah.md"
LETICIA = ROOT / "Casos-Leticia" / "25 Casos - Letícia - Sob Análise.md"
OUTPUT = ROOT / "data" / "case_bank.json"
STORIES = ROOT / "data" / "case_stories.json"
DOCS = ROOT / "data" / "case_docs.json"
CONCLUSIONS = ROOT / "data" / "case_conclusions.json"

# Used only to fill in a temporary image while parsing; finish_case() always overwrites it
# afterward with the case's own picture (newspaper/<case_id>.png, see newspaper_content.py).
IMAGES = {
    "grace_hopper": ("newspaper/identity_correct_v2.png", "newspaper/identity_wrong_v2.png"),
    "katherine_johnson": ("newspaper/cargo_correct.png", "newspaper/cargo_wrong.png"),
    "ada_lovelace": ("newspaper/criteria_correct.png", "newspaper/criteria_wrong.png"),
    "radia_perlman": ("newspaper/privacy_correct.png", "newspaper/privacy_wrong.png"),
    "fei_fei_li": ("newspaper/bias_correct.png", "newspaper/bias_wrong.png"),
    "margaret_hamilton": ("newspaper/cargo_correct.png", "newspaper/cargo_wrong.png"),
}

HINTS = {
    "grace_hopper": "Confirme se os dados pertencem mesmo à pessoa, ao objeto ou ao código certo.",
    "katherine_johnson": "Refaça a conta com os números dos papéis e veja se o resultado bate.",
    "ada_lovelace": "Veja se o critério usado pela IA é permitido e tem a ver com a decisão.",
    "radia_perlman": "Veja para que o dado foi autorizado e para que ele foi usado.",
    "fei_fei_li": "Compare situações parecidas: alguém foi tratado diferente sem motivo?",
    "margaret_hamilton": "Pergunte se a IA tinha informação suficiente para decidir sem uma pessoa.",
}

# Simple words for the player. Applied to document titles and field labels.
TITLE_SIMPLIFICATIONS = (
    (r"^Logs (de|do|da|das|dos) ", r"Histórico  "),
    (r"^Log de ", "Histórico de "),
    (r"^Log do ", "Histórico do "),
    (r"^Log da ", "Histórico da "),
    (r"^Log ", "Histórico "),
    (r"\bLog\b", "Histórico"),
    (r"^Matriz de ", "Lista de "),
    (r"^Manifesto do Fabricante", "Lista do fabricante"),
    (r"^Manifesto de Carga", "Lista de carga"),
    (r"^Manifesto do Navio", "Lista do navio"),
    (r"^Convenção Coletiva \(Trecho\)", "Regras do sindicato"),
    (r"\(Trecho\)", ""),
    (r"^Rastreamento TI", "Rastro do sistema"),
    (r"^IP Histórico", "Histórico de acesso"),
    (r"^Relatório IA$", "Relatório da IA"),
    (r"^Ordem de Varredura", "Ordem de bloqueio"),
    (r"^Regimento da Empresa", "Regras da empresa"),
    (r"^Termos de Uso da SmartTV", "Termos de uso da TV"),
    (r"^Cadastro Original do Fundo", "Cadastro antigo"),
    (r"^Certidão de Casamento Anexada", "Certidão de casamento"),
    (r"^Licença ANAC \(CMA\)", "Licença do piloto"),
    (r"^Regra da Aviação Civil", "Regra da aviação"),
    (r"^Protocolo de Aviação Civil", "Regra da aviação"),
)

SMALL_WORDS = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "no", "na", "nos", "nas", "em", "com", "para", "por", "um", "uma"}
STOP_WORDS = SMALL_WORDS | {"que", "se", "ao", "aos", "sem", "mais", "mas", "ser", "foi", "sua", "seu", "pelo", "pela"}

# Fields where the interactive value is not the last one written in the draft.
FIELD_OVERRIDES: dict[tuple[str, int], str] = {
    ("case_15", 1): "Processo",
    ("case_16", 1): "Nome",
    ("case_16", 2): "Nome",
    ("case_42", 1): "Histórico de Atrasos",
    ("case_43", 3): "Destino",
    ("case_51", 2): "Cálculo",
    ("case_54", 2): "Notas Manuais",
    ("case_56", 2): "Faturado",
}

# Extra fields that also matter (the draft marked only one field per paper).
EXTRA_KEYS: dict[tuple[str, int, str], str] = {
    ("case_08", 2, "Item A"): "Item A: 200 rolos",
    ("case_16", 1, "Endereço"): "Mesmo endereço",
    ("case_16", 2, "Endereço"): "Mesmo endereço",
    ("case_25", 1, "ID"): "ID do crachá",
    ("case_32", 1, "Placa Lida"): "Placa lida pela IA",
    ("case_38", 1, "CPF"): "CPF do pedido",
    ("case_38", 2, "Nome"): "Nome no cadastro antigo",
    ("case_22", 2, "Horário"): "Acesso às 23:15",
    ("case_45", 1, "Receita Total"): "Receita total",
    ("case_51", 1, "Valor"): "Valor da fatura",
}

# (case, label of the field) -> better note; (case, document number) -> better title
NOTE_OVERRIDES = {
    ("case_22", "Credencial"): "Credencial: Token 88",
    ("case_32", "Placa"): "Placa do carro autuado",
}
TITLE_OVERRIDES = {
    ("case_20", 1): "Contrato: cláusula 4",
    ("case_20", 2): "Contrato: cláusula 5",
}
NOTE_WORDS = (("Trigger", "Gatilho"), ("Override", "Comando manual"), ("SLA", "prazo"))

LABEL_SIMPLIFICATIONS = {
    "Trigger": "Gatilho",
    "Override Humano": "Comando do piloto",
    "Override": "Ordem",
    "Score Serasa": "Nota de crédito",
    "Score Cultural": "Nota cultural",
    "Pedido de Unsubscribe": "Pedido de cancelamento",
    "Cálculo Real": "Conta certa",
    "Ação às 18:05": "Ação às 18:05",
}
ACRONYMS = {"tv": "TV", "cep": "CEP", "ia": "IA"}
TEXT_FIXES = {"Cégo": "Cego"}

# Questions from the drafts that gave the answer away, reworded neutrally.
QUESTION_OVERRIDES = {
    "case_34": "O motivo usado pela IA tem a ver com pagar o aluguel?",
    "case_35": "A TV podia usar esse áudio para vender anúncios?",
    "case_36": "A IA tratou igualmente candidatos com lacunas parecidas?",
    "case_38": "A IA podia considerar que é a mesma cliente?",
    "case_39": "O peso da carga passa mesmo do limite do navio?",
    "case_40": "O motivo dado pela IA é um critério válido para promover alguém?",
    "case_41": "A seguradora podia usar esses dados de atividade física?",
    "case_42": "É justo reduzir o limite pelo endereço do cliente?",
    "case_44": "O alerta da câmera aponta a pessoa certa?",
    "case_45": "A conta da IA está correta?",
    "case_46": "O motivo da IA se apoia em algo que a empresa realmente mede?",
    "case_47": "O usuário deu permissão válida para receber esses e-mails?",
    "case_48": "A nota da IA mede bem o trabalho desses atendentes?",
    "case_49": "A IA podia ignorar o comando do piloto?",
    "case_50": "A IA leu o número de série com segurança?",
    "case_51": "O valor cobrado é mesmo um preço abusivo?",
    "case_52": "O piloto tem os documentos em dia para voar hoje?",
    "case_53": "A empresa respeitou o pedido de saída do cliente a tempo?",
    "case_54": "A decisão da IA foi justa com a fundadora?",
    "case_55": "A IA podia trancar as saídas nessa situação?",
    "case_56": "A cobrança do fornecedor está correta?",
}

CASE_OVERRIDES: dict[str, dict] = {
    "case_08": {
        "briefing": "A Têxtil FioBom teve a entrega de matéria-prima aprovada por uma IA. Veja se os números da carga batem.",
        "ai": {
            "verdict": "Entrega Aprovada",
            "confidence": "92%",
            "reason": "Volume coerente",
            "evidence_label": "Total lido",
            "evidence_value": "500 rolos",
        },
        "explanation": "A nota fiscal fala em 500 rolos, mas os itens do manifesto somam só 450 (200 + 250). A IA errou a soma.",
    },
    # Casos 32-56 (Letícia) vinham com uma dica genérica por protocolo (só 6 frases para 25 casos).
    # Aqui cada um ganha uma dica que diz exatamente quais dois dados comparar ou que conta refazer.
    "case_32": {"hint": "Compare a placa que a câmera realmente fotografou com a placa que a IA leu e com a placa do carro multado."},
    "case_33": {"hint": "Use a calculadora: confira se o valor pago bate com a regra do sindicato para o feriado."},
    "case_34": {"hint": "Veja se o motivo que a IA usou para negar o crédito tem alguma relação com pagar aluguel."},
    "case_35": {"hint": "Compare para que o áudio podia ser usado com o motivo real que gerou o anúncio."},
    "case_36": {"hint": "Compare as duas lacunas do currículo e veja se a IA tratou os dois candidatos do mesmo jeito."},
    "case_37": {"hint": "Compare o horário em que os comandos do operador pararam com o horário em que os dados do sensor ficaram corrompidos."},
    "case_38": {"hint": "Confira se o CPF e a certidão de casamento provam que é a mesma cliente, mesmo com o nome diferente."},
    "case_39": {"hint": "Use a calculadora: confira se as duas unidades de peso (libras e quilos) foram convertidas direito."},
    "case_40": {"hint": "Veja se o critério que a IA usou aparece nos critérios oficiais de promoção da empresa."},
    "case_41": {"hint": "Compare para que os dados do aplicativo podiam ser usados com o que a seguradora realmente fez com eles."},
    "case_42": {"hint": "Compare o histórico de pagamento do cliente com o motivo que a IA realmente usou para reduzir o limite."},
    "case_43": {"hint": "Veja se a IA tinha como saber que o galpão de destino não existe mais."},
    "case_44": {"hint": "Compare as duas fotos dos funcionários: elas são mesmo da mesma pessoa?"},
    "case_45": {"hint": "Use a calculadora: confira se a porcentagem de gasto em P&D bate com a regra da lei."},
    "case_46": {"hint": "Veja se a métrica que a IA usou é uma das que o manual de avaliação realmente permite."},
    "case_47": {"hint": "Leia com atenção o que o clique do usuário realmente autorizava."},
    "case_48": {"hint": "Compare a nota humana com a nota da IA e veja de onde vem a diferença."},
    "case_49": {"hint": "Veja, na regra da aviação, se a IA podia ignorar o comando do piloto."},
    "case_50": {"hint": "Compare o número de série borrado com os números de série realmente válidos do lote."},
    "case_51": {"hint": "Confira a moeda: o valor da fatura está em dólar ou na moeda do país do fornecedor?"},
    "case_52": {"hint": "Veja se a licença do piloto está mesmo válida para hoje, sem se deixar impressionar pelo currículo dele."},
    "case_53": {"hint": "Confira quantas horas se passaram entre o pedido de cancelamento e o envio da oferta."},
    "case_54": {"hint": "Compare as notas do gerente com o motivo que a IA usou para ignorá-las."},
    "case_55": {"hint": "Veja se a regra de emergência permite trancar as saídas com pessoas lá dentro."},
    "case_56": {"hint": "Use a calculadora: confira se o valor faturado bate com o preço fixo vezes a quantidade."},
}


# ---------------------------------------------------------------- helpers
def strip_accents(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", strip_accents(text).lower()) if len(w) >= 3 and w not in STOP_WORDS}


def simplify_title(title: str) -> str:
    title = title.strip()
    for pattern, replacement in TITLE_SIMPLIFICATIONS:
        title = re.sub(pattern, replacement, title)
    title = re.sub(r"\s+", " ", title).strip()
    return title[:1].upper() + title[1:]


def join_titles(titles: list[str]) -> str:
    titles = [simplify_title(t) for t in titles]
    return titles[0] if len(titles) == 1 else ", ".join(titles[:-1]) + " e " + titles[-1]


def nice_title(text: str) -> str:
    result = []
    for index, word in enumerate(text.lower().split()):
        word = TEXT_FIXES.get(word.capitalize(), word)
        if word in ACRONYMS:
            result.append(ACRONYMS[word])
        else:
            result.append(word if index and word in SMALL_WORDS else word[:1].upper() + word[1:])
    return " ".join(result)


def unquote(text: str) -> str:
    return text.strip().strip('"“”').strip()


def clip(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit]
    sentence_end = max(cut.rfind(". "), cut.rfind("! "), cut.rfind("? "))
    if sentence_end > limit * 0.5:
        return cut[: sentence_end + 1]
    return cut[: cut.rfind(" ")].rstrip(",;:") + "…"


def normalise_value(value: str) -> str:
    return " ".join(strip_accents(value).casefold().split())


def link_kind(value_a: str, value_b: str) -> str:
    a, b = normalise_value(value_a), normalise_value(value_b)
    if len(a) > 32 or len(b) > 32:
        return "related"
    if a == b or a in b or b in a:
        return "equal"
    from difflib import SequenceMatcher

    return "different" if SequenceMatcher(a=a, b=b).ratio() >= 0.6 else "related"


def build_links(documents: list[dict]) -> list[list[str]]:
    keyed = [
        (index, field)
        for index, document in enumerate(documents)
        for field in document["fields"]
        if field.get("key")
    ]
    links: list[list[str]] = []
    for i, (doc_a, field_a) in enumerate(keyed):
        for doc_b, field_b in keyed[i + 1:]:
            text = clip(f"{field_a['note']} · {field_b['note']}", 100)
            links.append([field_a["key"], field_b["key"], link_kind(field_a["value"], field_b["value"]), text])
    return links


def relocate_key(document: dict) -> None:
    """The drafts hang the key on the last field; move it where the note points."""
    keyed = next((f for f in document["fields"] if f["key"]), None)
    if keyed is None or len(document["fields"]) < 2:
        return
    note = words(keyed["note"])
    own = len(note & words(f"{keyed['label']} {keyed['value']}"))
    best = max(document["fields"], key=lambda f: len(note & words(f"{f['label']} {f['value']}")))
    if best is not keyed and len(note & words(f"{best['label']} {best['value']}")) > own:
        best["key"], best["note"] = keyed["key"], keyed["note"]
        keyed["key"], keyed["note"] = None, None


def apply_overrides(case: dict) -> None:
    for number, document in enumerate(case["documents"], start=1):
        label = FIELD_OVERRIDES.get((case["id"], number))
        if label:
            keyed = next((f for f in document["fields"] if f["key"]), None)
            target = next((f for f in document["fields"] if f["label"] == label), None)
            if keyed and target and keyed is not target:
                target["key"], target["note"] = keyed["key"], keyed["note"]
                keyed["key"], keyed["note"] = None, None
        else:
            relocate_key(document)
        for (case_id, doc_number, extra_label), note in EXTRA_KEYS.items():
            if case_id == case["id"] and doc_number == number:
                target = next(f for f in document["fields"] if f["label"] == extra_label)
                target["key"], target["note"] = f"{case['id']}_x{number}{extra_label[:2].lower()}", note
        if (case["id"], number) in TITLE_OVERRIDES:
            document["title"] = TITLE_OVERRIDES[(case["id"], number)]
        for field in document["fields"]:
            field["label"] = LABEL_SIMPLIFICATIONS.get(field["label"], field["label"])
            if field["key"]:
                field["note"] = NOTE_OVERRIDES.get((case["id"], field["label"]), field["note"])
                for old, new in NOTE_WORDS:
                    field["note"] = field["note"].replace(old, new)


def finish_case(case: dict) -> dict:
    """Common post-processing: links, evidence summary, defaults."""
    apply_overrides(case)
    case["documents"] = [d for d in case["documents"] if any(f["key"] for f in d["fields"])]
    documents = case["documents"]
    keyed = [field for document in documents for field in document["fields"] if field.get("key")]
    case["links"] = build_links(documents)
    case["required_keys"] = [field["key"] for field in keyed]
    case["evidence_lines"] = [clip(field["note"], 44) for field in keyed[:3]]
    case["key_documents"] = [document["id"] for document in documents]
    for document in documents:
        document["title"] = simplify_title(document["title"])
    stories = json.loads(STORIES.read_text(encoding="utf-8"))
    entry = stories[case["id"]]
    case["story"], case["attention"] = entry["story"], entry["attention"]
    if case["id"] in QUESTION_OVERRIDES:
        case["question"] = QUESTION_OVERRIDES[case["id"]]
    guides = json.loads(DOCS.read_text(encoding="utf-8"))[case["id"]]
    if len(guides) != len(case["documents"]):
        raise ValueError(f"{case['id']}: {len(guides)} guides for {len(case['documents'])} documents")
    for document, guide in zip(case["documents"], guides):
        document["guide"] = guide
    case["conclusions"] = json.loads(CONCLUSIONS.read_text(encoding="utf-8"))[case["id"]]
    override = CASE_OVERRIDES.get(case["id"], {})
    for key, value in override.items():
        if key == "ai":
            case["ai"].update(value)
        else:
            case[key] = value
    # Every case gets its own newsroom picture (instead of 10 shared by protocol) and its own
    # two-sided tabloid story (instead of the dry technical explanation repeated as the body).
    news = NEWS[case["id"]]
    image = f"newspaper/{case['id']}.png"
    correct_headline, correct_body = news["correct"]
    wrong_headline, wrong_body = news["wrong"]
    case["news_correct"] = {"headline": correct_headline.upper(), "body": correct_body, "image": image}
    case["news_wrong"] = {"headline": wrong_headline.upper(), "body": wrong_body, "image": image}
    return case


# ------------------------------------------------------------ Mariah file
def parse_mariah() -> list[dict]:
    text = MARIAH.read_text(encoding="utf-8")
    blocks = re.split(r"^### (case_\d+) — (.*)$", text, flags=re.M)[1:]
    cases = []
    for case_id, title, body in zip(blocks[0::3], blocks[1::3], blocks[2::3]):
        cases.append(finish_case(parse_mariah_case(case_id, title.strip(), body)))
    return cases


def field_after(pattern: str, body: str) -> str:
    match = re.search(pattern, body, flags=re.M)
    if match is None:
        raise ValueError(f"missing {pattern!r}")
    return match.group(1).strip()


def parse_mariah_case(case_id: str, title: str, body: str) -> dict:
    meta = re.search(r"\*\*Sequência.*?\*\* (\d+), turno: (\d+), dificuldade: (\d+), protocol_focus: (\w+)", body)
    subject = re.search(r"\*\*Sujeito.*?\*\* (.*?), subject_name: (.*?), decision_object: (.*?), newspaper_section: (.*)", body)
    decision = re.search(r'\*\*Decisão:\*\* (.*?); (\d+%); "(.*?)"[;,] (.*?); (Doc[^;]*); (.*)', body)
    if not (meta and subject and decision):
        raise ValueError(f"{case_id}: header not understood")
    evidence_label, evidence_value, evidence_key, evidence_note = [p.strip() for p in decision.group(6).rstrip(". ").split(", ", 3)]

    documents = []
    for line in re.findall(r"^- \*\*doc_(\d+)\*\* (.*)$", body, flags=re.M):
        number, rest = line
        head = re.match(r"\((.*?)\): (.*?), (blue|olive|amber|red)\. (.*)$", rest)
        if head is None:
            raise ValueError(f"{case_id}: doc line not understood: {rest[:60]}")
        doc_title, organization, accent, fields_text = head.groups()
        fields_text = re.sub(r"\s*Destaque: (sim|não)\.?\s*$", "", fields_text).rstrip(". ")
        fields = []
        for segment in re.split(r"label: ", fields_text)[1:]:
            segment = segment.strip().rstrip(",").strip()
            m = re.match(r"(.*?), value: (.*?)(?:, evidence_key: (.*?), evidence_note: (.*?))?\.?$", segment)
            if m is None:
                raise ValueError(f"{case_id}: field not understood: {segment[:60]}")
            label, value, key, note = m.groups()
            fields.append({"label": label.strip(), "value": value.strip().rstrip("."), "key": key, "note": note.strip().rstrip(".") if note else None})
        documents.append({"id": f"doc_{number}", "title": doc_title.strip(), "org": organization.strip(), "accent": accent, "fields": fields})
    synthesis = re.search(r"\*\*Síntese:\*\* required_keys: [\w, ]+?\. (.*)", body)
    explanation = clip(synthesis.group(1), 250) if synthesis else ""
    news = re.findall(r'\*\*Resultado:\*\* "(.*?)"; "(.*?)"; Imagem: (.*?)\.', body)
    correct_image, wrong_image = IMAGES[meta.group(4)]
    stamp = field_after(r"\*\*Carimbo correto:\*\* (\w+)", body)
    return {
        "id": case_id,
        "sequence": int(meta.group(1)),
        "turn": int(meta.group(2)),
        "difficulty": int(meta.group(3)),
        "protocol": meta.group(4),
        "title": title,
        "briefing": field_after(r"\*\*Briefing:\*\* (.*)", body),
        "hint": field_after(r"\*\*Dica:\*\* (.*)", body),
        "question": field_after(r"\*\*Pergunta de revisão:\*\* (.*)", body),
        "subject_label": subject.group(1).strip(),
        "subject_name": subject.group(2).strip(),
        "decision_object": subject.group(3).strip(),
        "section": subject.group(4).strip(),
        "documents": documents,
        "ai": {
            "verdict": decision.group(1).strip(),
            "confidence": decision.group(2),
            "reason": decision.group(3).strip(),
            "model": decision.group(4).strip(),
            "source": join_titles([d["title"] for d in documents]),
            "evidence_label": evidence_label,
            "evidence_value": evidence_value,
            "evidence_key": evidence_key,
            "evidence_note": evidence_note.rstrip("."),
        },
        "correct_stamp": stamp,
        "explanation": explanation,
        "feedback_correct": field_after(r"\*\*Feedback ao acertar:\*\* (.*)", body),
        "feedback_wrong": field_after(r"\*\*Feedback ao errar:\*\* (.*)", body),
        "news_correct": {"headline": news[0][0].upper(), "body": news[0][1], "image": correct_image},
        "news_wrong": {"headline": news[1][0].upper(), "body": news[1][1], "image": wrong_image},
        "search": [],
    }


# ----------------------------------------------------------- Leticia file
def split_top_level(text: str) -> list[str]:
    """Split on ', ' and '. ' that are outside parentheses and quotes."""
    items, current, depth, in_quote = [], "", 0, False
    i = 0
    while i < len(text):
        char = text[i]
        if char == '"':
            in_quote = not in_quote
        elif not in_quote and char == "(":
            depth += 1
        elif not in_quote and char == ")":
            depth -= 1
        if depth == 0 and not in_quote and char in ",." and text[i + 1: i + 2] == " ":
            items.append(current.strip())
            current = ""
            i += 2
            continue
        current += char
        i += 1
    items.append(current.strip().rstrip("."))
    return [item for item in items if item]


def parse_fields(campos: str) -> list[dict]:
    fields = []
    for item in split_top_level(campos):
        m = re.match(r"^(.+?) \((.*)\)$", item)
        if m:
            label, value = m.group(1), unquote(m.group(2))
        elif re.match(r"^Obs: ", item):
            label, value = "Observação", item[5:]
        elif ": " in item and len(item.split(": ")[0]) < 24:
            label, value = item.split(": ", 1)
        else:
            label, value = "Observação", item
        value = unquote(value).replace('", "', "; ").replace('"', "").rstrip(".")
        fields.append({"label": label.strip(), "value": value, "key": None, "note": None})
    return fields


def pick_evidence_field(fields: list[dict], evidence: str) -> dict:
    target = words(evidence)
    scored = [(len(target & words(f"{f['label']} {f['value']}")), index, f) for index, f in enumerate(fields)]
    best = max(scored, key=lambda item: (item[0], -item[1]))
    return best[2]


def parse_leticia() -> list[dict]:
    text = LETICIA.read_text(encoding="utf-8")
    table = {}
    for row in re.findall(r"^\| `(case_\d+)` \| (\d+) \| (\d+) \| (\w+) \| `(\w+)` \| `(\w+)` \| (.*?) \| (.*?) \|", text, flags=re.M):
        table[row[0]] = {"turn": int(row[2]), "difficulty": row[3], "protocol": row[4], "stamp": row[5], "sector": row[6], "affected": row[7]}
    blocks = re.split(r"^#### Caso (\d+) — (.*)$", text, flags=re.M)[1:]
    cases = []
    for number, title, body in zip(blocks[0::3], blocks[1::3], blocks[2::3]):
        cases.append(finish_case(parse_leticia_case(f"case_{number}", title.strip(), body, table[f"case_{number}"])))
    return cases


def parse_leticia_case(case_id: str, title: str, body: str, meta: dict) -> dict:
    decision_text = field_after(r"\*\*Decisão que chegou à mesa:\*\* (.*)", body)
    m = re.match(r"(.*?)\. Confiança: (\d+%)\. Modelo: (.*?)\. Razão: (.*)$", decision_text)
    if m is None:
        raise ValueError(f"{case_id}: decision not understood: {decision_text[:80]}")
    verdict, confidence, model, reason = m.groups()
    source = None
    if " Fonte: " in reason:
        reason, source = reason.split(" Fonte: ", 1)
    reason = unquote(reason.rstrip(".")).replace('"', "")

    documents = []
    for index, (doc_title, emitter, campos, evidence) in enumerate(
        re.findall(r"^- (.*?): \[Emissor: (.*?)\] Campos: (.*?) Evidência: (.*)$", body, flags=re.M), start=1
    ):
        fields = parse_fields(campos)
        chosen = pick_evidence_field(fields, evidence)
        chosen["key"] = f"{case_id}_d{index}"
        chosen["note"] = evidence.strip().rstrip(".")
        accent = ("olive", "blue", "amber", "red")[(index - 1) % 4]
        documents.append({"id": f"doc_{index}", "title": doc_title.strip(), "org": emitter.strip(), "accent": accent, "fields": fields})

    cross = field_after(r"\*\*Cruzamento decisivo:\*\* (.*)", body)
    news = re.findall(r"^- \*\*(Acerto|Erro):\*\* (.*?) \(Pixel art: .*\)\.?$", body, flags=re.M)
    news_map = {kind: headline for kind, headline in news}
    base = re.search(r'\*\*Base Interna:\*\* (?:Busca|Pesquisa) (.+?) -> (?:Retorna )?"(.+?)"', body)
    search = []
    if base:
        query, result = base.group(1).strip(), base.group(2).strip()
        search.append({
            "title": result,
            "source": "Base interna",
            "snippet": f"Você buscou por {query}: {result}.",
            "keywords": sorted(words(query) | {query.lower()}),
        })
    correct_image, wrong_image = IMAGES[meta["protocol"]]
    explanation = clip(cross, 250)
    return {
        "id": case_id,
        "sequence": int(case_id.split("_")[1]),
        "turn": meta["turn"],
        "difficulty": {"Baixa": 1, "Média": 2, "Alta": 4, "Extrema": 5}.get(meta["difficulty"], 3),
        "protocol": meta["protocol"],
        "title": nice_title(title),
        "briefing": field_after(r"\*\*Chamado da Sob Análise:\*\* (.*)", body),
        "hint": HINTS[meta["protocol"]],
        "question": field_after(r"\*\*Pergunta que Ana deixa aberta:\*\* (.*)", body).split("?")[0] + "?",
        "subject_label": "AFETADO",
        "subject_name": meta["affected"],
        "decision_object": verdict,
        "section": meta["sector"].upper(),
        "documents": [d for d in documents],
        "ai": {
            "verdict": verdict,
            "confidence": confidence,
            "reason": reason,
            "model": model.strip(),
            "source": source.rstrip(".") if source else join_titles([d["title"] for d in documents]),
            "evidence_label": "MOTIVO DA IA",
            "evidence_value": clip(reason, 34),
            "evidence_key": f"{case_id}_ai",
            "evidence_note": clip(reason, 60),
        },
        "correct_stamp": meta["stamp"],
        "explanation": explanation,
        "feedback_correct": explanation,
        "feedback_wrong": explanation,
        "news_correct": {"headline": news_map["Acerto"].upper(), "body": explanation, "image": correct_image},
        "news_wrong": {
            "headline": news_map["Erro"].upper(),
            "body": clip("A IA errou e a auditoria deixou passar. " + cross, 260),
            "image": wrong_image,
        },
        "search": search,
    }


def main() -> None:
    cases = parse_mariah() + parse_leticia()
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps({"cases": cases}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(cases)} casos gravados em {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
