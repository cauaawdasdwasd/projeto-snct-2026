import json

path = "data/case_docs_extra.json"
data = json.load(open(path, encoding="utf-8"))


def set_row(case, doc, label, value):
    rows = data[case][doc]["info"]
    for row in rows:
        if row[0] == label:
            row[1] = value
            return
    raise KeyError((case, doc, label))


set_row("case_39", "doc_3", "Observação", "Compara o peso da nota com o limite do porto.")
set_row("case_18", "doc_3", "Observação", "Recalcula a rota quando o mapa é atualizado.")
set_row("case_42", "doc_2", "Observação", "Analisa dados por região e por bairro.")
set_row("case_31", "doc_2", "Observação", "Interface redesenhada para o novo visual.")
set_row("case_13", "doc_2", "Observação", "Quantidades anotadas pelo operador do turno.")
set_row("case_12", "doc_2", "Observação", "Uma cor por sensor, atualizada o tempo todo.")
set_row("case_08", "doc_1", "Observação", "Compra feita por telefone e confirmada por e-mail.")
json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
