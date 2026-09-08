import unittest
from framespec import markdown
from framespec.findings import has_errors
from framespec.profile import Profile

SPEC_EXAMPLE = """---
type: frame [0.3]
identifier: acme/brand-voice
name: Brand Voice
description: How Acme sounds in public writing.
visibility: internal
version: 1.2.0
status: approved
maintainer: marketing
license: CC-BY-4.0
inherits:
  - acme/company-core@2.0.0
guards:
  - acme/pii-guard
---

Be plain and direct. Prefer short sentences.

## Rules

- No performance claims without a cited benchmark.

## Terminology

- **customer**: an organization that has deployed an Acme Hub.
- Prefer "Hub" over "instance".

## Things We Avoid

- The word "revolutionary".
"""

MINIMAL_V02 = """---
type: frame [0.2]
name: Editorial Style Guide
description: Shared guidance for clear, consistent external writing.
visibility: shared
---

# Editorial Style Guide

## Goals

- Be clear, direct, and credible.

## Terminology

- Prefer "Frame" over "alignment file".
"""


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.p = Profile.load()

    def test_spec_example_normalizes_as_figures_6_to_8_describe(self):
        frame, findings = markdown.parse(SPEC_EXAMPLE, self.p, "file:///x/brand-voice.frame.md")
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        e = frame.elements
        self.assertEqual(e["identifier"], "acme/brand-voice")
        self.assertEqual(e["title"], "Brand Voice")
        self.assertEqual(e["composition"], ["acme/company-core@2.0.0"])
        self.assertEqual(e["guards"], ["acme/pii-guard"])
        self.assertEqual(e["maintainer"], ["marketing"])
        self.assertEqual(e["rules"], ["No performance claims without a cited benchmark."])
        self.assertEqual(e["terminology"], [
            {"term": "customer", "definition": "an organization that has deployed an Acme Hub."},
            'Prefer "Hub" over "instance".'])
        self.assertEqual(e["guidance"], [
            'Be plain and direct. Prefer short sentences.\n\n## Things We Avoid\n\n- The word "revolutionary".'])
        self.assertNotIn("type", e)
        self.assertEqual(frame.extras["type"], "frame [0.3]")

    def test_identifier_defaults_to_location_and_unstructured_terminology_is_kept(self):
        frame, findings = markdown.parse(MINIMAL_V02, self.p, "file:///x/minimal/frame.md")
        self.assertFalse(has_errors(findings))
        self.assertEqual(frame.elements["identifier"], "file:///x/minimal/frame.md")
        self.assertEqual(frame.elements["terminology"], ['Prefer "Frame" over "alignment file".'])
        self.assertEqual(frame.elements["goals"], ["Be clear, direct, and credible."])
        self.assertEqual(frame.elements["guidance"], ["# Editorial Style Guide"])
        self.assertIn("identifier-default", [f.code for f in findings])

    def test_qualified_heading_is_guidance_and_subheadings_stay_in_section(self):
        text = "---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n---\n\n## Review Norms\n\n- a\n\n## Rules\n\n### Hard rules\n\n- b\n"
        frame, findings = markdown.parse(text, self.p, None)
        self.assertEqual(frame.elements["guidance"], ["## Review Norms\n\n- a"])
        self.assertEqual(frame.elements["rules"], ["### Hard rules", "b"])

    def test_missing_required_key_and_bad_type_are_errors(self):
        text = "---\ntype: frame [0.3.0]\ndescription: D\nvisibility: internal\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        codes = [f.code for f in findings]
        self.assertIn("missing-required-key", codes)
        self.assertIn("bad-type-token", codes)
        self.assertTrue(has_errors(findings))

    def test_no_front_matter_is_an_error(self):
        frame, findings = markdown.parse("just text\n", self.p, None)
        self.assertIsNone(frame)
        self.assertEqual(findings[0].code, "front-matter")


class DefectRegressionTests(unittest.TestCase):
    """One test per defect found while implementing this task."""

    def setUp(self):
        self.p = Profile.load()

    def test_malformed_yaml_returns_a_finding_rather_than_crashing(self):
        frame, findings = markdown.parse("---\nname: [unclosed\n---\nbody\n", self.p, None)
        self.assertIsNone(frame)
        self.assertEqual(findings[0].code, "front-matter")

    def test_a_long_description_is_not_folded_by_the_writer(self):
        long = "A description long enough that PyYAML would fold it at column eighty by default."
        frame, _ = markdown.parse(MINIMAL_V02, self.p, None)
        frame.elements["description"] = long
        text = markdown.write(frame, self.p)
        self.assertIn(f"description: {long}", text)
        again, findings = markdown.parse(text, self.p, None)
        self.assertEqual(again.elements["description"], long)

    def test_a_non_string_refinement_value_does_not_crash_the_writer(self):
        frame, _ = markdown.parse(MINIMAL_V02, self.p, None)
        frame.elements["rules"] = [5]
        self.assertIn("- 5", markdown.write(frame, self.p))

    def test_alternative_labels_survive_the_markdown_writer(self):
        frame, _ = markdown.parse(MINIMAL_V02, self.p, None)
        frame.elements["terminology"] = [
            {"term": "Hub", "definition": "a deployed instance.", "altTerms": ["instance", "deployment"]}]
        text = markdown.write(frame, self.p)
        self.assertIn("instance, deployment", text)
        again, _ = markdown.parse(text, self.p, None)
        self.assertIn("instance, deployment", again.elements["terminology"][0]["definition"])

    def test_a_fenced_block_does_not_end_a_refinement_section(self):
        text = ("---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n---\n\n"
                "## Rules\n\n- real bullet\n\n```\n## Not A Heading\n- not a bullet\n```\n")
        frame, findings = markdown.parse(text, self.p, None)
        self.assertEqual(frame.elements["guidance"], [""])
        self.assertEqual(frame.elements["rules"][0], "real bullet")
        self.assertIn("## Not A Heading", frame.elements["rules"][1])


class WriteTests(unittest.TestCase):
    def test_write_then_parse_preserves_element_values(self):
        p = Profile.load()
        frame, _ = markdown.parse(SPEC_EXAMPLE, p, "file:///x/brand-voice.frame.md")
        text = markdown.write(frame, p)
        again, findings = markdown.parse(text, p, "file:///x/brand-voice.frame.md")
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(again.elements, frame.elements)
        self.assertIn("name: Brand Voice", text)
        self.assertIn("inherits:", text)


if __name__ == "__main__":
    unittest.main()
