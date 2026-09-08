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

    def test_missing_guidance_is_an_error_and_object_required(self):
        frame, findings = yamljson.parse_json('{"identifier": "a/b"}', self.p, None)
        self.assertIn("missing-mandatory", [f.code for f in findings])
        frame, findings = yamljson.parse_json('[1, 2]', self.p, None)
        self.assertIsNone(frame)

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


def open_spec_example():
    from test_framespec_markdown import SPEC_EXAMPLE
    return SPEC_EXAMPLE


if __name__ == "__main__":
    unittest.main()
