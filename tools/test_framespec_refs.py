import unittest
from framespec import refs


class ClassifyTests(unittest.TestCase):
    def test_pinned(self):
        self.assertEqual(refs.classify("acme/brand-voice@1.2.0"), refs.PINNED)
        self.assertEqual(refs.classify("openteams/company-core@2.0.0"), refs.PINNED)

    def test_qualified(self):
        self.assertEqual(refs.classify("acme/brand-voice"), refs.QUALIFIED)

    def test_uri(self):
        self.assertEqual(refs.classify("https://frames.example.com/acme/brand-voice"), refs.URI)
        self.assertEqual(refs.classify("nebi://acme/frames/brand-voice"), refs.URI)

    def test_path(self):
        self.assertEqual(refs.classify("./meeting-notes.frame.md"), refs.PATH)
        self.assertEqual(refs.classify("../parent/frame.md"), refs.PATH)
        self.assertEqual(refs.classify("/abs/frame.md"), refs.PATH)

    def test_name_is_the_catch_all(self):
        self.assertEqual(refs.classify("company-core"), refs.NAME)
        self.assertEqual(refs.classify("Company Core"), refs.NAME)
        self.assertEqual(refs.classify("editorial-style-guide"), refs.NAME)
        self.assertEqual(refs.classify("weird@but not pinned"), refs.NAME)

    def test_surrounding_whitespace_is_trimmed(self):
        self.assertEqual(refs.classify("  acme/brand-voice@1.0.0  "), refs.PINNED)

    def test_empty_is_the_only_error(self):
        with self.assertRaises(ValueError):
            refs.classify("   ")


if __name__ == "__main__":
    unittest.main()
