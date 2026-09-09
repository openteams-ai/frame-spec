import csv
import tempfile
import unittest
from pathlib import Path

from framespec.profile import Profile, DEFAULT_PROFILE_PATH

REFINEMENTS = ["rules", "terminology", "goals", "style", "norms", "skills",
               "toolSpecs", "prompts", "architecture", "businessProcess"]


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
        self.assertEqual(names, REFINEMENTS)
        # The expected pairs written out, not a comprehension over refinements(): that
        # restated the implementation and would have passed just as well if labels()
        # had stopped lower-casing, which is the one thing it does beyond inverting
        # the mapping. The two labels that are not the element name are the ones that
        # matter, and hard-coding is what the assertion above already does.
        self.assertEqual(self.p.labels(), {
            "rules": "rules",
            "terminology": "terminology",
            "goals": "goals",
            "style": "style",
            "norms": "norms",
            "skills": "skills",
            "tool specifications": "toolSpecs",
            "prompts": "prompts",
            "architecture": "architecture",
            "business process": "businessProcess",
        })

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
        # Written out for the same reason: a comprehension over refinements() would
        # pass whatever content_elements() returned, as long as it returned the same
        # thing twice.
        self.assertEqual(self.p.content_elements(), ["guidance"] + REFINEMENTS)

    def test_missing_content_root_raises(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "no-guidance.csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["propertyID", "propertyLabel", "mandatory", "repeatable",
                                 "valueNodeType", "valueDataType", "valueConstraint",
                                 "valueConstraintType", "mapsTo", "refines", "note"])
                writer.writerow(["identifier", "Identifier", "true", "false", "literal",
                                 "xsd:string", "", "", "dcterms:identifier", "", ""])
            with self.assertRaises(ValueError):
                Profile.load(csv_path)


if __name__ == "__main__":
    unittest.main()
