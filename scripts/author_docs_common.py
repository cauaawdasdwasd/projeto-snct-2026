"""Short constructors used by scripts/author_docs_*.py to describe the layout of each paper."""


def T(title, cols, rows, widths=None):
    block = {"type": "table", "title": title, "cols": cols, "rows": rows}
    if widths:
        block["widths"] = widths
    return block


def C(title, messages):
    return {"type": "chat", "title": title, "messages": messages}


def TL(title, entries):
    return {"type": "timeline", "title": title, "entries": entries}


def CL(title, items):
    return {"type": "checklist", "title": title, "items": items}


def BR(title, bars):
    return {"type": "bars", "title": title, "bars": bars}


def TM(title, lines):
    return {"type": "terminal", "title": title, "lines": lines}


def N(text, side="R", tilt=1.5):
    return {"type": "note", "text": text, "side": side, "tilt": tilt}


def LT(title, headers, text=""):
    return {"type": "letter", "title": title, "headers": headers, "text": text}


def P(title, items, numbered=True):
    return {"type": "para", "title": title, "items": items, "numbered": numbered}


def RC(title, items, totals):
    return {"type": "receipt", "title": title, "items": items, "totals": totals}


def SL(text, side="R", tilt=-4):
    return {"type": "seal", "text": text, "side": side, "tilt": tilt}
