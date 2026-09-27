p = "src/scenes/audit.py"
s = open(p, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, count)


sub("from src.ui.comparison_card import ComparisonCard\n", "from src.ui.comparison_card import ComparisonCard\nfrom src.ui.side_by_side import SideBySide\n")
sub("CALCULATOR_BUTTON_RECT = pygame.Rect(570, 72, 165, 34)\n", "CALCULATOR_BUTTON_RECT = pygame.Rect(570, 72, 165, 34)\nCOMPARE_BUTTON_RECT = pygame.Rect(743, 72, 172, 34)\n")
sub("        self.calculator_hovered = False\n", "        self.calculator_hovered = False\n        self.compare_hovered = False\n        self.side_view = SideBySide()\n")
sub("        self.comparison_card = ComparisonCard()\n", "        self.comparison_card = ComparisonCard()\n")

# escape
sub("""        if self.document_inspector.is_open:
            self.document_inspector.close()
            self._play_sound("back", 0.65)
            return True
""", """        if self.side_view.is_open:
            self.side_view.close()
            self._play_sound("back", 0.65)
            return True
        if self.document_inspector.is_open:
            self.document_inspector.close()
            self._play_sound("back", 0.65)
            return True
""")

# hover
sub("""        self.calculator_hovered = bool(
            not self._is_modal_open()
            and monitor_position is not None
            and CALCULATOR_BUTTON_RECT.collidepoint(monitor_position)
        )
""", """        self.calculator_hovered = bool(
            not self._is_modal_open()
            and monitor_position is not None
            and CALCULATOR_BUTTON_RECT.collidepoint(monitor_position)
        )
        self.compare_hovered = bool(
            not self._is_modal_open()
            and monitor_position is not None
            and COMPARE_BUTTON_RECT.collidepoint(monitor_position)
        )
        self.side_view.update_hover(monitor_position)
""")

# modal mouse handling (before the inspector branch)
sub("""        if self.document_inspector.is_open:
            if monitor_position is not None:
                handled = self.document_inspector.handle_mouse_down(""", """        if self.side_view.is_open:
            if monitor_position is not None:
                self._handle_side_view_click(monitor_position)
            return

        if self.document_inspector.is_open:
            if monitor_position is not None:
                handled = self.document_inspector.handle_mouse_down(""")

# button click
sub("""            if CALCULATOR_BUTTON_RECT.collidepoint(monitor_position):
                self.calculator.toggle()""", """            if COMPARE_BUTTON_RECT.collidepoint(monitor_position):
                if len(self.documents) > 2:
                    self.side_view.open(self.documents)
                    self._play_sound("forward", 0.6)
                return
            if CALCULATOR_BUTTON_RECT.collidepoint(monitor_position):
                self.calculator.toggle()""")

# render button
sub("        self._render_calculator_button(self.monitor_surface)\n", "        self._render_calculator_button(self.monitor_surface)\n        self._render_compare_button(self.monitor_surface)\n")
sub("    def _render_calculator_button(self, surface: pygame.Surface) -> None:", '''    def _render_compare_button(self, surface: pygame.Surface) -> None:
        background = (25, 34, 26) if self.compare_hovered else (5, 11, 9)
        border = (231, 210, 116) if self.compare_hovered else (76, 89, 57)
        ink = (247, 239, 159) if self.compare_hovered else (213, 218, 130)
        rect = COMPARE_BUTTON_RECT
        pygame.draw.rect(surface, background, rect)
        pygame.draw.rect(surface, border, rect, 2)
        for offset in (0, 13):  # two little pages side by side
            pygame.draw.rect(surface, border, (rect.x + 9 + offset, rect.y + 7, 11, 20), 2)
            pygame.draw.line(surface, ink, (rect.x + 12 + offset, rect.y + 13), (rect.x + 17 + offset, rect.y + 13), 2)
            pygame.draw.line(surface, ink, (rect.x + 12 + offset, rect.y + 18), (rect.x + 17 + offset, rect.y + 18), 2)
        label = self.small_font.render("LADO A LADO", False, ink)
        surface.blit(label, label.get_rect(midleft=(rect.x + 44, rect.centery)))

    def _render_calculator_button(self, surface: pygame.Surface) -> None:''')

# popup render
sub("""        elif self.document_inspector.is_open:
            self.document_inspector.render(self.popup_surface, self.evidence_notes)
        elif self.ai_decision_panel.popup_open:""", """        elif self.side_view.is_open:
            self.side_view.render(self.popup_surface)
            self._render_comparison_card(self.popup_surface, force=True)
        elif self.document_inspector.is_open:
            self.document_inspector.render(self.popup_surface, self.evidence_notes)
        elif self.ai_decision_panel.popup_open:""")
sub("""    def _render_comparison_card(self, surface: pygame.Surface) -> None:
        if self.comparison_result is None or self._is_modal_open():
            return""", """    def _render_comparison_card(self, surface: pygame.Surface, force: bool = False) -> None:
        if self.comparison_result is None or (self._is_modal_open() and not force):
            return""")

# modal flag + tutorial guard
sub("            or self.document_inspector.is_open\n            or self.ai_decision_panel.popup_open\n        )", "            or self.side_view.is_open\n            or self.document_inspector.is_open\n            or self.ai_decision_panel.popup_open\n        )")
sub("            or self.protocol_panel.is_popup_open\n            or self.document_inspector.is_open\n        ):\n            return None", "            or self.protocol_panel.is_popup_open\n            or self.side_view.is_open\n            or self.document_inspector.is_open\n        ):\n            return None")

# clear on restarts
s = s.replace("        self.popups.clear()\n", "        self.popups.clear()\n        self.side_view.close()\n")

# handler method
sub("    def _handle_evidence_comparison(", '''    def _handle_side_view_click(self, monitor_position: tuple[int, int]) -> None:
        if (
            self.comparison_result is not None
            and self.comparison_card.contains(monitor_position)
        ):
            if self.comparison_card.is_close_hit(monitor_position):
                self.comparison_result = None
                self._play_sound("back", 0.5)
            elif (
                self.comparison_card.is_protocol_hit(monitor_position)
                and self.comparison_result[2].kind != "none"
            ):
                self.side_view.close()
                self.protocol_panel.open_protocol(self.case.protocol_focus)
                self._play_sound("forward", 0.65)
            return
        result = self.side_view.handle_mouse_down(monitor_position)
        if result == "close":
            self.side_view.close()
            self._play_sound("back", 0.6)
        elif result == "chip":
            self._play_sound("click", 0.5)
        elif isinstance(result, tuple):
            _, document, source = result
            evidence = document.evidence_at(source)
            if evidence is not None:
                self._handle_evidence_comparison(document, evidence)
            elif document.toggle_annotation(source):
                self._play_sound("paper", 0.5)

    def _handle_evidence_comparison(''')
open(p, "w", encoding="utf-8").write(s)
