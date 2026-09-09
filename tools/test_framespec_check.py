import unittest
from framespec.check import check
from framespec.model import Frame
from framespec.profile import Profile


def codes(findings, level=None):
    return [f.code for f in findings if level is None or f.level == level]


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.p = Profile.load()

    def frame(self, **elements):
        return Frame(elements, "json", "file:///x.frame.json")

    def test_mandatory(self):
        f = self.frame(title="T")
        self.assertEqual(codes(check(f, self.p), "error").count("missing-mandatory"), 2)
        ok = self.frame(identifier="a/b", guidance=[""])
        self.assertEqual(codes(check(ok, self.p), "error"), [])

    def test_unregistered_values_warn_and_never_error(self):
        f = self.frame(identifier="a/b", guidance=["g"], status="stable", visibility="team")
        findings = check(f, self.p)
        self.assertEqual(codes(findings, "error"), [])
        self.assertEqual(codes(findings, "warning").count("unregistered-value"), 2)

    def test_non_repeatable_with_many_values_is_an_error(self):
        f = self.frame(identifier="a/b", guidance=["g"], title=["A", "B"])
        self.assertIn("not-repeatable", codes(check(f, self.p), "error"))

    def test_references_are_classified_not_rejected(self):
        f = self.frame(identifier="a/b", guidance=["g"], composition=["./x.md", "Company Core", "acme/x@1.0"])
        findings = check(f, self.p)
        self.assertEqual(codes(findings, "error"), [])
        forms = [x.message for x in findings if x.code == "reference-form"]
        self.assertEqual(len(forms), 3)
        self.assertTrue(any("path-ref" in m for m in forms))
        self.assertTrue(any("name-ref" in m for m in forms))
        self.assertTrue(any("pinned-ref" in m for m in forms))

    def test_unknown_and_extension_elements_are_preserved_as_info(self):
        f = self.frame(identifier="a/b", guidance=["g"], **{"x-nebari-excludes": ["a/c"], "mystery": 1})
        findings = check(f, self.p)
        self.assertEqual(codes(findings, "error"), [])
        self.assertIn("extension-preserved", codes(findings, "info"))
        self.assertIn("unknown-preserved", codes(findings, "info"))

    def test_issued_date_format(self):
        good = self.frame(identifier="a/b", guidance=["g"], issued="2026-09-07")
        bad = self.frame(identifier="a/b", guidance=["g"], issued="September 7")
        self.assertNotIn("not-rfc3339", codes(check(good, self.p)))
        self.assertIn("not-rfc3339", codes(check(bad, self.p), "warning"))

    def test_non_repeatable_with_a_single_listed_value_is_not_an_error(self):
        """A one-item list is one value, not several: the repeatable check must not be fooled by it."""
        f = self.frame(identifier="a/b", guidance=["g"], title=["A"])
        self.assertEqual(codes(check(f, self.p), "error"), [])

    def test_reference_form_findings_are_info_level(self):
        """The interface designates reference-form as info; checking only the code would miss a level swap."""
        f = self.frame(identifier="a/b", guidance=["g"], composition=["./x.md", "Company Core", "acme/x@1.0"])
        findings = check(f, self.p)
        self.assertEqual(codes(findings, "info").count("reference-form"), 3)

    def test_empty_reference_warns_rather_than_rejecting(self):
        f = self.frame(identifier="a/b", guidance=["g"], composition=["   "])
        findings = check(f, self.p)
        self.assertEqual(codes(findings, "error"), [])
        self.assertIn("empty-reference", codes(findings, "warning"))

    def test_a_null_guidance_is_reported_rather_than_accepted_silently(self):
        """Section 4.2.2 makes guidance MUST be present and MAY be empty and does not
        say whether an explicit null is empty. The mandatory check tests presence, so a
        null passes it. Taking the permissive reading is a position on a MUST, so the
        tool states it: no error, no warning, and an info finding that says so."""
        f = self.frame(identifier="a/b", guidance=[None])
        findings = check(f, self.p)
        self.assertEqual(codes(findings, "error"), [])
        self.assertEqual(codes(findings, "warning"), [])
        self.assertIn("guidance-null", codes(findings, "info"))
        empty = check(self.frame(identifier="a/b", guidance=[""]), self.p)
        self.assertNotIn("guidance-null", codes(empty))

    def test_a_null_guidance_in_a_document_reaches_the_checker_as_present(self):
        """The shape a real document produces, not one assembled by hand: normalize()
        wraps the null, so the finding has to fire on [None] and not on None."""
        from framespec import yamljson
        frame, _ = yamljson.parse_json('{"identifier": "a/b", "guidance": null}', self.p, None)
        self.assertEqual(frame.elements["guidance"], [None])
        found = codes(check(frame, self.p))
        self.assertIn("guidance-null", found)
        self.assertNotIn("missing-mandatory", found)

    def test_extension_and_unknown_codes_attach_to_the_right_element(self):
        """assertIn on codes alone would not catch the two preserved codes being swapped."""
        f = self.frame(identifier="a/b", guidance=["g"], **{"x-nebari-excludes": ["a/c"], "mystery": 1})
        findings = check(f, self.p)
        extension = next(x for x in findings if x.code == "extension-preserved")
        unknown = next(x for x in findings if x.code == "unknown-preserved")
        self.assertIn("x-nebari-excludes", extension.message)
        self.assertIn("mystery", unknown.message)


if __name__ == "__main__":
    unittest.main()
