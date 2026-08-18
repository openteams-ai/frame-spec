#!/usr/bin/env python3
"""Tests for validate_frames.py, focused on the `type` grammar.

The v0.2 spec allows exactly two `type` forms: `frame`, or
`frame [<major>.<minor>]`. These tests prove that malformed values fail
validation, so the validator cannot certify a Frame that violates the
frozen normative syntax.

Run with:

    python -m unittest discover -s tools
"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_frames import validate_frame


def problems_for(type_value):
    """Validate a minimal Frame with the given `type` value."""
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
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "frame.md"
        path.write_text(text, encoding="utf-8")
        return validate_frame(path)


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
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "frame.md"
            path.write_text(text, encoding="utf-8")
            problems = validate_frame(path)
        self.assertTrue(any("description" in p for p in problems))
        self.assertTrue(any("visibility" in p for p in problems))


if __name__ == "__main__":
    unittest.main()
