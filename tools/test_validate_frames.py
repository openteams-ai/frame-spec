#!/usr/bin/env python3
"""Tests for validate_frames.py: the `type` grammar and the two serializations.

The spec allows exactly two `type` forms: `frame`, or
`frame [<major>.<minor>]`. These tests prove that malformed values fail
validation, so the validator cannot certify a Frame that violates the
frozen normative syntax.

They also prove that the same Frame validates identically whether it is
written as Markdown with frontmatter or as JSON, since the spec defines the
shape of a Frame rather than its medium.

Run with:

    python -m unittest discover -s tools
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_frames import is_frame_candidate, validate_frame


def problems_for_file(name, text):
    """Write text to a temp file with the given name and validate it."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        path.write_text(text, encoding="utf-8")
        return validate_frame(path)


def problems_for(type_value):
    """Validate a minimal Markdown Frame with the given `type` value."""
    text = (
        "---\n"
        f"type: {type_value}\n"
        "name: Test Frame\n"
        "description: A Frame used to exercise the validator.\n"
        "visibility: private\n"
        "---\n"
        "\n"
        "Body.\n"
    )
    return problems_for_file("frame.md", text)


def json_problems_for(**overrides):
    """Validate a minimal JSON Frame, with any field overridden or removed.

    Passing None for a field drops it, so tests can check missing fields.
    """
    frame = {
        "type": "frame [0.3]",
        "name": "Test Frame",
        "description": "A Frame used to exercise the validator.",
        "visibility": "private",
        "body": "Body.\n",
    }
    frame.update(overrides)
    frame = {key: value for key, value in frame.items() if value is not None}
    return problems_for_file("frame.json", json.dumps(frame))


class TypeGrammarTests(unittest.TestCase):
    def test_bare_frame_is_valid(self):
        self.assertEqual(problems_for("frame"), [])

    def test_conformance_token_is_valid(self):
        self.assertEqual(problems_for("frame [0.2]"), [])

    def test_prefix_word_is_rejected(self):
        self.assertTrue(problems_for("framework"))

    def test_trailing_words_are_rejected(self):
        self.assertTrue(problems_for("frame nonsense"))

    def test_patch_qualified_token_is_rejected(self):
        self.assertTrue(problems_for("frame [0.2.0]"))

    def test_missing_brackets_are_rejected(self):
        self.assertTrue(problems_for("frame 0.2"))


class RequiredFieldTests(unittest.TestCase):
    def test_missing_required_field_is_rejected(self):
        text = (
            "---\n"
            "type: frame\n"
            "name: Test Frame\n"
            "---\n"
            "\n"
            "Body.\n"
        )
        problems = problems_for_file("frame.md", text)
        self.assertTrue(any("description" in p for p in problems))
        self.assertTrue(any("visibility" in p for p in problems))


class JsonSerializationTests(unittest.TestCase):
    """The JSON serialization carries the same shape, so it gets the same rules."""

    def test_minimal_json_frame_is_valid(self):
        self.assertEqual(json_problems_for(), [])

    def test_json_frame_without_body_is_valid(self):
        self.assertEqual(json_problems_for(body=None), [])

    def test_json_type_grammar_is_enforced(self):
        self.assertTrue(json_problems_for(type="frame [0.3.0]"))
        self.assertTrue(json_problems_for(type="framework"))

    def test_missing_required_field_is_rejected(self):
        problems = json_problems_for(visibility=None)
        self.assertTrue(any("visibility" in p for p in problems))

    def test_empty_required_field_is_rejected(self):
        problems = json_problems_for(name="")
        self.assertTrue(any("name" in p for p in problems))

    def test_non_string_required_field_is_rejected(self):
        problems = json_problems_for(name=42)
        self.assertTrue(any("name" in p and "string" in p for p in problems))

    def test_non_string_body_is_rejected(self):
        problems = json_problems_for(body={"text": "Body."})
        self.assertTrue(any("body" in p and "string" in p for p in problems))

    def test_inherits_accepts_a_string_or_a_list(self):
        self.assertEqual(json_problems_for(inherits="company-core"), [])
        self.assertEqual(
            json_problems_for(inherits=["company-core", "department-engineering"]), []
        )
        self.assertTrue(json_problems_for(inherits=[1, 2]))

    def test_malformed_json_is_rejected(self):
        self.assertTrue(problems_for_file("frame.json", "{not json"))

    def test_json_array_is_rejected(self):
        self.assertTrue(problems_for_file("frame.json", "[]"))


class CandidateDetectionTests(unittest.TestCase):
    """Files that do not claim to be Frames are skipped rather than failed,
    so a package manifest or a plain Markdown note does not break the run."""

    def candidate(self, name, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / name
            path.write_text(text, encoding="utf-8")
            return is_frame_candidate(path)

    def test_markdown_without_frontmatter_is_not_a_candidate(self):
        self.assertFalse(self.candidate("notes.md", "# Notes\n"))

    def test_json_without_a_frame_type_is_not_a_candidate(self):
        self.assertFalse(self.candidate("package.json", '{"name": "thing"}'))

    def test_json_with_a_frame_type_is_a_candidate(self):
        self.assertTrue(self.candidate("frame.json", '{"type": "frame"}'))

    def test_misspelled_frame_type_is_still_a_candidate(self):
        """Otherwise a typo would be silently skipped instead of reported."""
        self.assertTrue(self.candidate("frame.json", '{"type": "framework"}'))


if __name__ == "__main__":
    unittest.main()
