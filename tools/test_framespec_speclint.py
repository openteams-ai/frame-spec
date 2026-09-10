import pathlib
import tempfile
import unittest

from framespec import speclint
from framespec.findings import has_errors

SPEC = speclint.DEFAULT_SPEC_PATH

# Each row is a defect a review found in this draft, written back into the draft as
# the text the review quoted. A check that cannot reproduce the finding it exists for
# is a check that will pass anything, which is the failure this module guards against
# and the reason every row names its finding.
MUTATIONS = [
    ("B3 a MUST bound to a role the draft never defines",
     "An implementation that needs to establish whether a Frame is the one it claims to be "
     "MUST rely on a registry",
     "Consumers that need to know whether a Frame is the one it claims to be MUST rely on a registry",
     "keyword-without-a-party"),
    ("B3 a recommendation only a person could satisfy",
     "- **Comment:** One or two sentences are enough for the purpose.",
     "- **Comment:** Authors SHOULD write one or two sentences.",
     "keyword-without-a-party"),
    ("S6 a value rule with no stated disposition",
     "The value MUST be a date or date-time in the format of [[RFC3339]](#ref-RFC3339). A reader "
     "MUST preserve a value that is not in that format and MUST NOT reject a Frame for carrying "
     "one; it SHOULD warn.",
     "The value MUST be a date or date-time in the format of [[RFC3339]](#ref-RFC3339).",
     "value-rule-without-a-disposition"),
    ("S8 a rejection path outside section 3.3",
     "A reader MUST NOT reject a document because its version token names a version",
     "A reader MUST reject a document because its version token names a version",
     "undeclared-rejection-path"),
    ("B6 a restatement that drops the qualification the original carries",
     "The structure is that of the YAML encoding ([Section 6.3](#enc-yaml)), including its one "
     "exception: repeatable elements are arrays and non-repeatable elements are strings, except "
     "`guidance`, which is a string because a document has exactly one `guidance` value.",
     "A repeatable element is always an array and a non-repeatable element is always a string, so "
     "an element's type does not vary between documents.",
     "restatement-drops-a-qualification"),
    ("W2 a requirement stated in a part section 2.1 calls non-normative",
     "A reader that does not implement a refinement it recognizes treats the content as ordinary "
     "guidance and never discards it.",
     "A reader that does not understand a section MUST treat its content as guidance and MUST NOT "
     "discard it.",
     "keyword-in-a-non-normative-part"),
]


class SpecLintTests(unittest.TestCase):
    def setUp(self):
        self.text = SPEC.read_text(encoding="utf-8")

    def lint_with(self, old, new):
        self.assertEqual(self.text.count(old), 1, f"anchor is not unique: {old[:60]!r}")
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "frame-spec.md"
            path.write_text(self.text.replace(old, new), encoding="utf-8")
            return speclint.lint(path)

    def test_the_draft_holds_every_invariant(self):
        findings = speclint.lint()
        self.assertFalse(has_errors(findings), [str(f) for f in findings if f.level == "error"])
        self.assertEqual([f.code for f in findings], ["spec-lint-ok"])

    def test_every_check_reproduces_the_finding_it_exists_for(self):
        for label, old, new, expected in MUTATIONS:
            with self.subTest(label):
                codes = [f.code for f in self.lint_with(old, new)]
                self.assertIn(expected, codes, codes)

    def test_each_check_is_reached_by_at_least_one_mutation(self):
        # A check nothing exercises is a check nobody knows is broken.
        covered = {expected for _, _, _, expected in MUTATIONS}
        self.assertEqual(len(speclint.CHECKS), 5)
        self.assertEqual(len(covered), 5, sorted(covered))

    def test_the_normative_classification_is_read_from_the_draft(self):
        # Hard-coding the section list here would let the draft's own statement drift
        # away from what the check enforces.
        numbers, letters = speclint.normative_sections(self.text)
        self.assertEqual(numbers, set(range(3, 11)))
        self.assertEqual(letters, {"A", "B", "C"})

    def test_an_unreadable_classification_is_an_error_not_a_pass(self):
        findings = self.lint_with(
            "Sections 3 through 10 and Appendices A, B, and C are normative.",
            "Everything here is normative unless it says otherwise.")
        self.assertIn("classification-unreadable", [f.code for f in findings])


if __name__ == "__main__":
    unittest.main()
