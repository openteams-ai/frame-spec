import unittest
from framespec.findings import Finding, has_errors
from framespec.model import Frame, normalize
from framespec.profile import Profile


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


if __name__ == "__main__":
    unittest.main()
