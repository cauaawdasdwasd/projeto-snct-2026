p = "src/gameplay/document_blocks.py"
s = open(p, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, count)


sub("        self.regions: list[tuple[DocumentField, pygame.Rect]] = []\n", "        self.regions: list[tuple[DocumentField, pygame.Rect]] = []\n        self.pad = 0  # extra air per row, grown by the renderer when a paper has spare room\n")

# table
sub("        return 12 + 18 * lines\n", "        return 12 + 18 * lines + self.pad\n")
sub("self.text(surface, line, font, color, (x + 7, y + 6 + line_index * 18))", "self.text(surface, line, font, color, (x + 7, y + 6 + self.pad // 2 + line_index * 18))")

# chat
sub("return self.title_height(block) + sum(24 + 18 * len(self._bubble_lines(m)) + 8 for m in block[\"messages\"])",
    "return self.title_height(block) + sum(24 + 18 * len(self._bubble_lines(m)) + 8 + self.pad for m in block[\"messages\"])")
sub("            height = 24 + 18 * len(lines)\n            width = 410", "            height = 24 + 18 * len(lines) + self.pad // 2\n            width = 410")
sub("(x + 10, y + 5))\n            value, field = self.resolve(body)", "(x + 10, y + 5 + self.pad // 4))\n            value, field = self.resolve(body)")
sub("(x + 10, y + 22 + index * 18))", "(x + 10, y + 22 + self.pad // 4 + index * 18))")
sub("self.mark(surface, field, pygame.Rect(x + 6, y + 20, width - 12, 4 + 18 * len(lines)))", "self.mark(surface, field, pygame.Rect(x + 6, y + 20 + self.pad // 4, width - 12, 4 + 18 * len(lines)))")
sub("            y += height + 8\n\n    # --- timeline", "            y += height + 8 + self.pad // 2\n\n    # --- timeline")

# timeline
sub("return self.title_height(block) + sum(14 + 18 * len(self._tl_lines(e)) for e in block[\"entries\"]) + 4",
    "return self.title_height(block) + sum(14 + 18 * len(self._tl_lines(e)) + self.pad for e in block[\"entries\"]) + 4")
sub("        total = sum(14 + 18 * len(self._tl_lines(e)) for e in block[\"entries\"])", "        total = sum(14 + 18 * len(self._tl_lines(e)) + self.pad for e in block[\"entries\"])")
sub("            y += 14 + 18 * len(lines)\n\n    # --- checklist", "            y += 14 + 18 * len(lines) + self.pad\n\n    # --- checklist")

# checklist
sub("return self.title_height(block) + 30 * len(block[\"items\"]) + 4", "return self.title_height(block) + (30 + self.pad) * len(block[\"items\"]) + 4")
sub("            y += 30\n\n    # --- bars", "            y += 30 + self.pad\n\n    # --- bars")

# bars
sub("return self.title_height(block) + 32 * len(block[\"bars\"]) + 4", "return self.title_height(block) + (32 + self.pad) * len(block[\"bars\"]) + 4")
sub("            y += 32\n\n    # --- terminal", "            y += 32 + self.pad\n\n    # --- terminal")

# para
sub("return self.title_height(block) + sum(10 + 19 * len(lines) for lines, _ in self._para_items(block)) + 2", "return self.title_height(block) + sum(10 + 19 * len(lines) + self.pad for lines, _ in self._para_items(block)) + 2")
sub("            height = 10 + 19 * len(lines)\n            if block.get(\"numbered\", True):", "            height = 10 + 19 * len(lines) + self.pad\n            if block.get(\"numbered\", True):")

# receipt
sub("return self.title_height(block) + 26 * len(block[\"items\"]) + 30 * len(block.get(\"totals\", [])) + 12", "return self.title_height(block) + (26 + self.pad // 2) * len(block[\"items\"]) + (30 + self.pad // 2) * len(block.get(\"totals\", [])) + 12")
sub("            self._receipt_row(surface, y, name, qty, price, False)\n            y += 26", "            self._receipt_row(surface, y, name, qty, price, False)\n            y += 26 + self.pad // 2")
sub("            self._receipt_row(surface, y, name, qty, price, True)\n            y += 30", "            self._receipt_row(surface, y, name, qty, price, True)\n            y += 30 + self.pad // 2")
open(p, "w", encoding="utf-8").write(s)

p = "src/gameplay/document_renderer.py"
s = open(p, encoding="utf-8").read()
old = """            y = info_top + (4 if loose else 0)
            for block in document.blocks:
                height = painter.height(block)
                if y + height > body_top - 8:
                    raise ValueError(f"Document {document.document_id} has too much content ({block['type']})")
                painter.draw(surface, block, y)
                y += height + 10
"""
new = """            y = info_top + (4 if loose else 0)
            room = body_top - 8 - y
            painter.pad = 0
            for candidate in range(16, -1, -2):  # spread out (more air per row) when the paper is sparse
                painter.pad = candidate
                used = sum(painter.height(block) + 10 for block in document.blocks) - 10
                if used <= room - 26 or candidate == 0:
                    break
            for block in document.blocks:
                height = painter.height(block)
                if y + height > body_top - 8:
                    raise ValueError(f"Document {document.document_id} has too much content ({block['type']})")
                painter.draw(surface, block, y)
                y += height + 10
"""
assert old in s
s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
