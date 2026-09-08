import unittest
from framespec.profile import Profile, DEFAULT_PROFILE_PATH


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.p = Profile.load(DEFAULT_PROFILE_PATH)

    def test_loads_thirty_elements_in_csv_order(self):
        self.assertEqual(len(self.p.order), 30)
        self.assertEqual(self.p.order[0], "identifier")
        self.assertEqual(self.p.order[-1], "byteSize")

    def test_mandatory_is_identifier_and_guidance(self):
        self.assertEqual(self.p.mandatory(), ["identifier", "guidance"])

    def test_ten_refinements_with_labels(self):
        names = [e.name for e in self.p.refinements()]
        self.assertEqual(names, ["rules", "terminology", "goals", "style", "norms", "skills",
                                 "toolSpecs", "prompts", "architecture", "businessProcess"])
        self.assertEqual(self.p.labels()["tool specifications"], "toolSpecs")
        self.assertEqual(self.p.labels()["business process"], "businessProcess")

    def test_picklists_and_references(self):
        self.assertEqual(self.p.elements["status"].picklist,
                         ("draft", "review", "approved", "deprecated", "revoked"))
        self.assertEqual(self.p.elements["visibility"].picklist,
                         ("private", "internal", "shared", "public"))
        self.assertTrue(self.p.elements["composition"].is_reference)
        self.assertTrue(self.p.elements["guards"].is_reference)
        self.assertFalse(self.p.elements["title"].is_reference)

    def test_repeatability(self):
        self.assertTrue(self.p.is_repeatable("guidance"))
        self.assertTrue(self.p.is_repeatable("maintainer"))
        self.assertFalse(self.p.is_repeatable("title"))
        self.assertFalse(self.p.is_repeatable("nonexistent"))

    def test_content_elements(self):
        self.assertEqual(self.p.content_elements()[0], "guidance")
        self.assertEqual(len(self.p.content_elements()), 11)


if __name__ == "__main__":
    unittest.main()
