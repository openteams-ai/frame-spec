import unittest
from framespec import markdown
from framespec.findings import has_errors
from framespec.profile import Profile

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

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

    def test_missing_type_is_an_error(self):
        text = "---\nname: N\ndescription: D\nvisibility: internal\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        codes = [f.code for f in findings]
        self.assertEqual(codes, ["missing-required-key"])
        self.assertTrue(has_errors(findings))

    def test_missing_recommended_keys_are_warnings_and_the_document_is_accepted(self):
        # Section 6.2.1 (amended): only `type` is REQUIRED in the Markdown encoding.
        # `name`, `description`, and `visibility` are SHOULD, so a reader MUST NOT
        # reject a document for omitting one; this is a bare-minimum document, missing
        # all three, and it still parses with no error.
        text = "---\ntype: frame [0.3]\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        self.assertIsNotNone(frame)
        codes = [f.code for f in findings]
        self.assertEqual(codes, ["missing-recommended-key"] * 3)
        self.assertTrue(all(f.level == "warning" for f in findings))
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(frame.elements["guidance"], ["body"])

    def test_missing_required_key_and_missing_recommended_key_coexist(self):
        text = "---\ndescription: D\nvisibility: internal\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        codes = [f.code for f in findings]
        self.assertIn("missing-required-key", codes)
        self.assertIn("missing-recommended-key", codes)
        required = next(f for f in findings if f.code == "missing-required-key")
        recommended = next(f for f in findings if f.code == "missing-recommended-key")
        self.assertEqual(required.level, "error")
        self.assertEqual(recommended.level, "warning")
        self.assertTrue(has_errors(findings))

    def test_type_not_beginning_with_frame_is_an_error(self):
        text = "---\ntype: framework\nname: N\ndescription: D\nvisibility: internal\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        codes = [f.code for f in findings]
        self.assertIn("bad-type-token", codes)
        self.assertTrue(has_errors(findings))

    def test_three_part_version_token_warns_but_is_accepted(self):
        text = "---\ntype: frame [0.3.0]\nname: N\ndescription: D\nvisibility: internal\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        codes = [f.code for f in findings]
        self.assertIn("nonstandard-type-version", codes)
        self.assertNotIn("bad-type-token", codes)

    def test_bare_frame_type_has_no_type_finding(self):
        text = "---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        codes = [f.code for f in findings]
        self.assertNotIn("bad-type-token", codes)
        self.assertNotIn("nonstandard-type-version", codes)

    def test_ordinary_major_minor_type_has_no_type_finding(self):
        text = "---\ntype: frame [0.3]\nname: N\ndescription: D\nvisibility: internal\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        codes = [f.code for f in findings]
        self.assertNotIn("bad-type-token", codes)
        self.assertNotIn("nonstandard-type-version", codes)

    def test_no_front_matter_is_an_error(self):
        frame, findings = markdown.parse("just text\n", self.p, None)
        self.assertIsNone(frame)
        self.assertEqual(findings[0].code, "front-matter")


class DefectRegressionTests(unittest.TestCase):
    """One test per defect found while implementing this task."""

    def setUp(self):
        self.p = Profile.load()

    @unittest.skipUnless(HAVE_YAML, "only a YAML parser rejects this front matter")
    def test_malformed_yaml_returns_a_finding_rather_than_crashing(self):
        # Requires PyYAML to be the thing that objects. The line-based fallback
        # framespec.frontmatter uses without it reads "name: [unclosed" as the literal
        # string "[unclosed" and parses the document without complaint, so the same
        # file is invalid with PyYAML installed and valid without it. That is a real
        # limitation of the fallback, recorded in tools/README.md rather than hidden
        # behind this skip.
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

    def test_a_defaulted_identifier_is_not_written_into_the_document(self):
        """The identifier is derived from the location, so emitting it would bake
        one machine's file path into a shared artifact as its identity."""
        location = "file:///srv/frames/minimal/frame.md"
        frame, _ = markdown.parse(MINIMAL_V02, self.p, location)
        self.assertEqual(frame.elements["identifier"], location)
        text = markdown.write(frame, self.p)
        self.assertNotIn("identifier:", text)
        again, _ = markdown.parse(text, self.p, location)
        self.assertEqual(again.elements["identifier"], location)

    def test_a_stated_identifier_is_written(self):
        frame, _ = markdown.parse(SPEC_EXAMPLE, self.p, "file:///x/b.frame.md")
        self.assertIn("identifier: acme/brand-voice", markdown.write(frame, self.p))

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
