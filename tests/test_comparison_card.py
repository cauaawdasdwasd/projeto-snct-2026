import unittest

from src.gameplay.comparison_links import NO_LINK, find_link
from src.gameplay.cases import CASE_BANK, TUTORIAL_CASE
from src.ui.comparison_card import diff_segments


class ComparisonDiffTests(unittest.TestCase):
    def test_letter_o_versus_zero_is_a_single_highlighted_character(self) -> None:
        left, right = diff_segments("LAB-4827O", "LAB-48270")
        self.assertEqual(left, [("LAB-4827", False), ("O", True)])
        self.assertEqual(right, [("LAB-4827", False), ("0", True)])


class FindLinkTests(unittest.TestCase):
    def test_link_lookup_ignores_click_order(self) -> None:
        a = find_link(TUTORIAL_CASE, "employee_id", "record_id")
        b = find_link(TUTORIAL_CASE, "record_id", "employee_id")
        self.assertEqual(a, b)
        self.assertEqual(a.kind, "different")

    def test_unknown_pair_is_no_link(self) -> None:
        self.assertIs(find_link(TUTORIAL_CASE, "employee_id", "nothing"), NO_LINK)
        self.assertEqual(NO_LINK.kind, "none")

    def test_every_interactive_pair_of_a_bank_case_has_a_link(self) -> None:
        for case in CASE_BANK:
            keys = [f.evidence_key for d in case.documents for f in d.fields if f.evidence_key]
            for i, a in enumerate(keys):
                for b in keys[i + 1:]:
                    self.assertNotEqual(find_link(case, a, b).kind, "none", (case.case_id, a, b))


if __name__ == "__main__":
    unittest.main()
