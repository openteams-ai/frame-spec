import unittest
from framespec import markdown, yamljson
from framespec.findings import Finding, has_errors
from framespec.model import DEFAULTED, Frame, default_identifier, derived_names, normalize
from framespec.profile import Profile

MINIMAL_MD = "---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n---\nbody\n"


class FindingsTests(unittest.TestCase):
    def test_has_errors(self):
        self.assertFalse(has_errors([Finding("info", "x", "m"), Finding("warning", "y", "m")]))
        self.assertTrue(has_errors([Finding("error", "z", "m")]))

    def test_an_unknown_level_is_rejected_at_construction(self):
        """A typo such as "eror" would be invisible to has_errors."""
        with self.assertRaises(ValueError):
            Finding("eror", "x", "m")


class NormalizeTests(unittest.TestCase):
    def setUp(self):
        self.p = Profile.load()

    def test_repeatable_scalars_become_lists(self):
        out = normalize({"maintainer": "marketing", "rules": ["a"], "title": "T"}, self.p)
        self.assertEqual(out["maintainer"], ["marketing"])
        self.assertEqual(out["rules"], ["a"])
        self.assertEqual(out["title"], "T")

    def test_guidance_is_listed_and_stripped_of_newlines(self):
        out = normalize({"guidance": "Be plain.\n\n## Avoid\n\n- hype\n"}, self.p)
        self.assertEqual(out["guidance"], ["Be plain.\n\n## Avoid\n\n- hype"])

    def test_unknown_elements_pass_through_untouched(self):
        out = normalize({"x-nebari-excludes": ["a/b"], "mystery": {"k": 1}}, self.p)
        self.assertEqual(out["x-nebari-excludes"], ["a/b"])
        self.assertEqual(out["mystery"], {"k": 1})

    def test_dates_become_rfc3339_text(self):
        import datetime
        out = normalize({"issued": datetime.date(2026, 9, 7), "x-when": [datetime.date(2026, 1, 2)]}, self.p)
        self.assertEqual(out["issued"], "2026-09-07")
        self.assertEqual(out["x-when"], ["2026-01-02"])

    def test_frame_defaults(self):
        f = Frame({"identifier": "a/b", "guidance": [""]}, "json")
        self.assertIsNone(f.location)
        self.assertEqual(f.extras, {})

    def test_guidance_branch_survives_a_non_repeatable_profile(self):
        """A string must never be iterated character by character."""
        class NotRepeatable:
            def is_repeatable(self, name):
                return False
        out = normalize({"guidance": "Be plain.\n"}, NotRepeatable())
        self.assertEqual(out["guidance"], ["Be plain."])


class IdentifierDefaultTests(unittest.TestCase):
    """Section 6.1's identifier default, in one place.

    The rule was implemented four times: derived in the Markdown encoding and again in
    the YAML and JSON encoding, honored by each of their writers, with the YAML and
    JSON encoding importing the Markdown encoding to reach a model-level marker. It
    belongs beside Frame.extras, which is where the marker it sets lives.
    """

    def test_a_document_that_states_no_identifier_is_identified_by_its_location(self):
        elements, extras = {"guidance": ""}, {}
        finding = default_identifier(elements, extras, "file:///srv/frames/x.frame.json")
        self.assertEqual(elements["identifier"], "file:///srv/frames/x.frame.json")
        self.assertIs(extras[DEFAULTED], True)
        self.assertEqual((finding.level, finding.code), ("info", "identifier-default"))
        # Derived, so no writer may emit it as though the document had stated it.
        self.assertEqual(derived_names(Frame(elements, "json", None, extras)), {"identifier"})

    def test_a_stated_identifier_is_left_alone_and_nothing_is_marked(self):
        elements, extras = {"identifier": "acme/x", "guidance": ""}, {}
        self.assertIsNone(default_identifier(elements, extras, "file:///srv/frames/x.frame.json"))
        self.assertEqual(elements["identifier"], "acme/x")
        self.assertEqual(extras, {})
        self.assertEqual(derived_names(Frame(elements, "json", None, extras)), set())

    def test_with_no_retrieval_location_there_is_nothing_to_default_to(self):
        elements, extras = {"guidance": ""}, {}
        self.assertIsNone(default_identifier(elements, extras, None))
        self.assertNotIn("identifier", elements)
        self.assertEqual(extras, {})

    def test_every_encoding_applies_the_one_rule_and_honors_the_one_marker(self):
        p = Profile.load()
        location = "file:///srv/frames/minimal/frame.md"
        md, md_findings = markdown.parse(MINIMAL_MD, p, location)
        js, js_findings = yamljson.parse_json('{"guidance": "body"}', p, location)
        for frame, findings in ((md, md_findings), (js, js_findings)):
            self.assertEqual(frame.elements["identifier"], location)
            self.assertIs(frame.extras[DEFAULTED], True)
            self.assertIn("identifier-default", [f.code for f in findings])
        self.assertNotIn("identifier:", markdown.write(md, p))
        self.assertNotIn('"identifier"', yamljson.write_json(js, p))


if __name__ == "__main__":
    unittest.main()
