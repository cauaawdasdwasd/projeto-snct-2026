"""Merge the hand-authored paper layouts (scripts/author_docs_*.py) into data/case_docs_extra.json.

Run: python scripts/build_doc_layouts.py
Documents that have a layout drop their old plain "info" table; images/insets are kept.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
PATH = ROOT / "data" / "case_docs_extra.json"


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    authored = 0
    for name in sorted(p.stem for p in Path(__file__).resolve().parent.glob("author_docs_[a-z].py")):
        module = importlib.import_module(name)
        for case_id, docs in module.DOCS.items():
            for doc_id, blocks in docs.items():
                entry = data.setdefault(case_id, {}).setdefault(doc_id, {})
                entry["blocks"] = blocks
                entry.pop("info", None)
                authored += 1
    lines = ["{"]
    cases = list(data.items())
    for case_index, (case_id, docs) in enumerate(cases):
        lines.append(f' "{case_id}": {{')
        for doc_index, (doc_id, body) in enumerate(docs.items()):
            parts = [f'"{key}": ' + json.dumps(value, ensure_ascii=False) for key, value in body.items()]
            lines.append(f'  "{doc_id}": {{' + ", ".join(parts) + "}" + ("," if doc_index < len(docs) - 1 else ""))
        lines.append(" }" + ("," if case_index < len(cases) - 1 else ""))
    lines.append("}")
    PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{authored} papers with their own layout")


if __name__ == "__main__":
    main()
