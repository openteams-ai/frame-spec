import sys
import unittest
from unittest import mock

from framespec import frontmatter, markdown
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


def document_codes(findings):
    """Finding codes about the document, dropping the fallback's configuration notice.

    Without PyYAML every parse also reports `yaml-fallback`, which says how the front
    matter was read rather than anything about the front matter. Tests that assert the
    exact set of findings must be independent of that, or the suite fails in the
    PyYAML-absent configuration tools/README.md advertises as supported.
    """
    return [f.code for f in findings if f.code != "yaml-fallback"]


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

    def test_a_refinement_in_front_matter_precedes_its_body_section(self):
        # Section 6.2.2 (amended): a refinement MAY appear as a front matter key, and
        # where it appears both in front matter and as a body section, its front
        # matter values precede its body values.
        text = ("---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n"
                "rules:\n  - a front matter rule\n---\n\n"
                "## Rules\n\n- a body rule\n")
        frame, findings = markdown.parse(text, self.p, None)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(frame.elements["rules"], ["a front matter rule", "a body rule"])

    def test_missing_type_is_an_error(self):
        text = "---\nname: N\ndescription: D\nvisibility: internal\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        self.assertEqual(document_codes(findings), ["missing-required-key"])
        self.assertTrue(has_errors(findings))

    def test_missing_recommended_keys_are_warnings_and_the_document_is_accepted(self):
        # Section 6.2.1 (amended): only `type` is REQUIRED in the Markdown encoding.
        # `name`, `description`, and `visibility` are SHOULD, so a reader MUST NOT
        # reject a document for omitting one; this is a bare-minimum document, missing
        # all three, and it still parses with no error.
        text = "---\ntype: frame [0.3]\n---\nbody\n"
        frame, findings = markdown.parse(text, self.p, None)
        self.assertIsNotNone(frame)
        self.assertEqual(document_codes(findings), ["missing-recommended-key"] * 3)
        self.assertTrue(all(f.level == "warning" for f in findings
                            if f.code != "yaml-fallback"))
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


def _section(label, lines):
    return ("---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n---\n\n"
            f"## {label}\n\n" + "\n".join(lines) + "\n")


class ListMarkerTests(unittest.TestCase):
    """Section 6.2.2 (amended): a list item may begin with any of five markers, and the
    marker is not part of the value. Section 6.2.3 (amended): a numbered item carries a
    concept exactly as a bulleted one does."""

    def setUp(self):
        self.p = Profile.load()

    def test_a_numbered_list_yields_one_value_per_item(self):
        text = _section("Rules", ["1. First rule.", "2. Second rule.", "3. Third rule."])
        frame, findings = markdown.parse(text, self.p, None)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(frame.elements["rules"], ["First rule.", "Second rule.", "Third rule."])

    def test_each_of_the_five_markers_is_recognized_and_the_marker_is_not_in_the_value(self):
        for marker in ("-", "*", "+", "1.", "1)"):
            with self.subTest(marker=marker):
                text = _section("Rules", [f"{marker} an item."])
                frame, findings = markdown.parse(text, self.p, None)
                self.assertFalse(has_errors(findings), [str(f) for f in findings])
                self.assertEqual(frame.elements["rules"], ["an item."])

    def test_a_numbered_terminology_item_produces_a_concept(self):
        text = _section("Terminology",
                        ["1. **customer**: an organization that has deployed an Acme Hub."])
        frame, findings = markdown.parse(text, self.p, None)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(frame.elements["terminology"],
                         [{"term": "customer", "definition": "an organization that has deployed an Acme Hub."}])

    def test_a_hyphen_bulleted_list_behaves_exactly_as_before(self):
        # Pins the pre-amendment shape: recognizing four new markers must not change
        # what a hyphen bullet, plain or a concept, yields.
        text = _section("Rules", ["- No performance claims without a cited benchmark."]) + (
            "\n## Terminology\n\n"
            "- **customer**: an organization that has deployed an Acme Hub.\n"
            '- Prefer "Hub" over "instance".\n')
        frame, findings = markdown.parse(text, self.p, None)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(frame.elements["rules"], ["No performance claims without a cited benchmark."])
        self.assertEqual(frame.elements["terminology"], [
            {"term": "customer", "definition": "an organization that has deployed an Acme Hub."},
            'Prefer "Hub" over "instance".'])


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

    def test_a_mapping_under_a_refinement_without_a_structured_form_is_written_as_text(self):
        # Section 4.4 gives only `terminology` a structured form. A mapping under any
        # other refinement used to be shaped like a concept, emitting `- ****:  (a: 1)`.
        frame, _ = markdown.parse(SPEC_EXAMPLE, self.p, None)
        frame.elements["rules"] = [{"b": 2, "a": 1}]
        text = markdown.write(frame, self.p)
        self.assertIn("- a: 1; b: 2\n", text)
        self.assertNotIn("****", text)
        again, findings = markdown.parse(text, self.p, None)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(again.elements["rules"], ["a: 1; b: 2"])
        # terminology keeps its concept shape in the same document
        self.assertIn("- **customer**:", text)

    def test_a_fenced_block_does_not_end_a_refinement_section(self):
        text = ("---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n---\n\n"
                "## Rules\n\n- real bullet\n\n```\n## Not A Heading\n- not a bullet\n```\n")
        frame, findings = markdown.parse(text, self.p, None)
        self.assertEqual(frame.elements["guidance"], [""])
        self.assertEqual(frame.elements["rules"][0], "real bullet")
        self.assertIn("## Not A Heading", frame.elements["rules"][1])


class FallbackParserTests(unittest.TestCase):
    """The line-based parser used when PyYAML is absent (section 6.2.1's preserve rule).

    Handed an indented block it cannot model, that parser used to drop the block's
    own lines and reattribute any `- ` item inside it to the preceding key, so a
    nested `terminology` came back as its altTerms list: a fabricated value, with
    the parser's complaints discarded. It must preserve instead.
    """

    def setUp(self):
        self.p = Profile.load()

    def test_lift_nested_separates_only_what_the_parser_cannot_model(self):
        cases = [
            ("a scalar", ["maintainer: marketing"], [], None),
            ("an empty value", ["maintainer:"], [], None),
            ("a simple sequence", ["inherits:", "  - a/b", "  - c/d"], [], None),
            ("a nested mapping", ["terminology:", "  term: client"], ["terminology"],
             "  term: client"),
            ("a mapping holding a sequence",
             ["terminology:", "  term: client", "  altTerms:", "    - account"],
             ["terminology"], "  term: client\n  altTerms:\n    - account"),
        ]
        for label, lines, nested_keys, block in cases:
            with self.subTest(label):
                kept, nested = frontmatter._lift_nested(lines)
                self.assertEqual(sorted(nested), nested_keys)
                if block is not None:
                    self.assertEqual(nested["terminology"], block)
                else:
                    self.assertEqual(kept, lines)

    def test_a_nested_value_is_preserved_verbatim_and_never_fabricated(self):
        text = ("---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n"
                "terminology:\n  term: client\n  altTerms:\n    - account\n---\n\nBody.\n")
        with mock.patch.dict(sys.modules, {"yaml": None}):
            frame, findings = markdown.parse(text, self.p, None)
        codes = [f.code for f in findings]
        self.assertIn("yaml-fallback", codes)
        self.assertIn("front-matter-not-fully-read", codes)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        # The value is the block's own text. Emphatically not ["account"], which is
        # what the reattribution produced and what nothing would have caught.
        self.assertEqual(frame.elements["terminology"],
                         ["  term: client\n  altTerms:\n    - account"])

    def test_a_v02_shaped_document_is_unaffected_by_the_lift(self):
        # The common shape: scalars plus one simple sequence. Must parse exactly as
        # before, or the fallback has regressed for every real v0.2 Frame.
        text = ("---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n"
                "inherits:\n  - acme/company-core\n  - acme/brand-voice\n---\n\nBody.\n")
        with mock.patch.dict(sys.modules, {"yaml": None}):
            frame, findings = markdown.parse(text, self.p, None)
        self.assertNotIn("front-matter-not-fully-read", [f.code for f in findings])
        self.assertEqual(frame.elements["composition"], ["acme/company-core", "acme/brand-voice"])
        self.assertEqual(frame.elements["title"], "N")


class FrontMatterShapeTests(unittest.TestCase):
    """Section 6.2.1: a front matter value MUST be a scalar or a sequence of scalars."""

    def setUp(self):
        self.p = Profile.load()

    HEAD = "---\ntype: frame\nname: N\ndescription: D\nvisibility: internal\n"

    def test_shape_is_warned_about_but_never_rejected(self):
        cases = [
            ("a scalar", "maintainer: marketing\n", False),
            ("an empty scalar", "maintainer:\n", False),
            ("a sequence of scalars", "maintainer:\n  - marketing\n  - sales\n", False),
            ("a mapping", "terminology:\n  term: client\n  altTerms:\n    - account\n", True),
            ("a sequence holding a mapping", "terminology:\n  - term: client\n", True),
            ("a sequence holding a sequence", "maintainer:\n  - - marketing\n", True),
        ]
        for label, block, want_warning in cases:
            with self.subTest(label):
                if want_warning and not HAVE_YAML:
                    self.skipTest("only a YAML parser produces a nested value")
                frame, findings = markdown.parse(self.HEAD + block + "---\n\nBody.\n",
                                                 self.p, None)
                self.assertFalse(has_errors(findings), [str(f) for f in findings])
                warned = [f for f in findings if f.code == "nested-front-matter-value"]
                self.assertEqual(bool(warned), want_warning, [str(f) for f in findings])
                for finding in warned:
                    self.assertEqual(finding.level, "warning")

    @unittest.skipUnless(HAVE_YAML, "only a YAML parser produces a nested value")
    def test_a_nested_value_is_preserved_and_no_concept_is_extracted(self):
        text = (self.HEAD + "terminology:\n  term: client\n  altTerms:\n    - account\n"
                + "---\n\nBody.\n")
        frame, _ = markdown.parse(text, self.p, None)
        self.assertEqual(frame.elements["terminology"],
                         [{"term": "client", "altTerms": ["account"]}])


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
