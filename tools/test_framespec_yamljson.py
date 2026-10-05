import json
import unittest
from framespec import yamljson, markdown
from framespec.findings import has_errors
from framespec.profile import Profile

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

JSON_EXAMPLE = json.dumps({
    "@context": "https://frames.example.org/context/v0.3",
    "@type": "Frame",
    "identifier": "acme/brand-voice",
    "title": "Brand Voice",
    "description": "How Acme sounds in public writing.",
    "visibility": "internal",
    "version": "1.2.0",
    "status": "approved",
    "maintainer": ["marketing"],
    "license": "CC-BY-4.0",
    "composition": ["acme/company-core@2.0.0"],
    "guards": ["acme/pii-guard"],
    "guidance": "Be plain and direct. Prefer short sentences.\n\n## Things We Avoid\n\n- The word \"revolutionary\".",
    "rules": ["No performance claims without a cited benchmark."],
    "terminology": [
        {"term": "customer", "definition": "an organization that has deployed an Acme Hub."},
        "Prefer \"Hub\" over \"instance\"."
    ]
})

YAML_EXAMPLE = """identifier: acme/brand-voice
title: Brand Voice
description: How Acme sounds in public writing.
visibility: internal
version: 1.2.0
status: approved
maintainer: [marketing]
license: CC-BY-4.0
composition:
  - acme/company-core@2.0.0
guards:
  - acme/pii-guard
guidance: |
  Be plain and direct. Prefer short sentences.

  ## Things We Avoid

  - The word "revolutionary".
rules:
  - No performance claims without a cited benchmark.
terminology:
  - term: customer
    definition: an organization that has deployed an Acme Hub.
  - Prefer "Hub" over "instance".
"""


class JsonTests(unittest.TestCase):
    def setUp(self):
        self.p = Profile.load()

    def test_jsonld_keys_go_to_extras_and_elements_match_markdown(self):
        frame, findings = yamljson.parse_json(JSON_EXAMPLE, self.p, "file:///x/b.frame.json")
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(frame.extras["@type"], "Frame")
        self.assertNotIn("@context", frame.elements)
        md, _ = markdown.parse(open_spec_example(), self.p, "file:///x/b.frame.md")
        self.assertEqual(frame.elements, md.elements)

    def test_missing_guidance_is_reported_once_by_the_checker(self):
        """The parser does not duplicate the mandatory check; framespec.check owns it."""
        from framespec.check import check
        frame, findings = yamljson.parse_json('{"identifier": "a/b"}', self.p, None)
        self.assertEqual([f.code for f in findings if f.code == "missing-mandatory"], [])
        codes = [f.code for f in check(frame, self.p)]
        self.assertEqual(codes.count("missing-mandatory"), 1)

    def test_a_json_document_must_be_an_object(self):
        frame, findings = yamljson.parse_json('[1, 2]', self.p, None)
        self.assertIsNone(frame)
        self.assertEqual(findings[0].code, "not-an-object")

    def test_write_json_round_trips(self):
        frame, _ = yamljson.parse_json(JSON_EXAMPLE, self.p, "file:///x/b.frame.json")
        again, findings = yamljson.parse_json(yamljson.write_json(frame, self.p), self.p, "file:///x/b.frame.json")
        self.assertEqual(again.elements, frame.elements)
        self.assertEqual(again.extras, frame.extras)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class YamlTests(unittest.TestCase):
    def setUp(self):
        self.p = Profile.load()

    def test_yaml_matches_json_and_markdown(self):
        y, findings = yamljson.parse_yaml(YAML_EXAMPLE, self.p, "file:///x/b.frame.yaml")
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        j, _ = yamljson.parse_json(JSON_EXAMPLE, self.p, "file:///x/b.frame.json")
        self.assertEqual(y.elements, j.elements)

    def test_write_yaml_round_trips(self):
        y, _ = yamljson.parse_yaml(YAML_EXAMPLE, self.p, "file:///x/b.frame.yaml")
        again, _ = yamljson.parse_yaml(yamljson.write_yaml(y, self.p), self.p, "file:///x/b.frame.yaml")
        self.assertEqual(again.elements, y.elements)


class DefectRegressionTests(unittest.TestCase):
    """One test per defect found while implementing this task, plus tests for
    the cross-encoding behavior the task brief calls out as the one this task
    must get right, none of which the tests above exercise."""

    def setUp(self):
        self.p = Profile.load()

    def test_an_optional_type_key_round_trips_through_json(self):
        """_to_mapping copied only '@context' and '@type' out of extras when
        building the output, so a 'type' key (section 6.3: MAY be present, MUST
        NOT be required) was parsed with a finding claiming it was preserved
        and then silently dropped by the writer. Fixed by reusing EXTRA_KEYS,
        the same set _from_mapping used to pull it out, instead of a second,
        incomplete copy of that tuple."""
        frame, findings = yamljson.parse_json(
            '{"type": "frame [0.3]", "identifier": "a/b", "guidance": ""}', self.p, None)
        self.assertEqual(frame.extras["type"], "frame [0.3]")
        text = yamljson.write_json(frame, self.p)
        self.assertIn('"type"', text)
        again, _ = yamljson.parse_json(text, self.p, None)
        self.assertEqual(again.extras, frame.extras)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_a_defaulted_identifier_survives_a_json_to_yaml_round_trip(self):
        """The identifier is derived from the retrieval location (section 6.1),
        not stated by the document, so no writer may emit it as though it were:
        that would bake one machine's filesystem path into a shared artifact
        as its identity. Both parsers set model.DEFAULTED and both writers
        skip on it, so the marker must survive a change of encoding too."""
        location = "file:///srv/frames/minimal/frame.json"
        frame, _ = yamljson.parse_json('{"guidance": ""}', self.p, location)
        self.assertEqual(frame.elements["identifier"], location)
        as_yaml = yamljson.write_yaml(frame, self.p)
        self.assertNotIn("identifier:", as_yaml)
        again, _ = yamljson.parse_yaml(as_yaml, self.p, location)
        self.assertEqual(again.elements, frame.elements)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_cross_encoding_round_trip_preserves_every_element(self):
        """Section 6.1: converting a document from one encoding to another and
        back must preserve the value of every element. The tests above
        round-trip JSON to JSON and YAML to YAML but never cross the two, so
        this exercises the actual requirement the task exists to prove."""
        y, findings = yamljson.parse_yaml(YAML_EXAMPLE, self.p, "file:///x/b.frame.yaml")
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        as_json = yamljson.write_json(y, self.p)
        via_json, findings = yamljson.parse_json(as_json, self.p, "file:///x/b.frame.yaml")
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(via_json.elements, y.elements)
        back_to_yaml = yamljson.write_yaml(via_json, self.p)
        final, findings = yamljson.parse_yaml(back_to_yaml, self.p, "file:///x/b.frame.yaml")
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        self.assertEqual(final.elements, y.elements)


def open_spec_example():
    from test_framespec_markdown import SPEC_EXAMPLE
    return SPEC_EXAMPLE


if __name__ == "__main__":
    unittest.main()
