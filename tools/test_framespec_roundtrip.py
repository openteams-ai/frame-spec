import json
import unittest
from pathlib import Path
from unittest import mock

from framespec import io as frame_io
from framespec import markdown, roundtrip, yamljson
from framespec.findings import has_errors
from framespec.model import Frame
from framespec.profile import Profile

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

FIXTURE = Path(__file__).resolve().parent.parent / "spec" / "fixtures" / "roundtrip" / "full.frame.md"


@unittest.skipUnless(HAVE_YAML, "PyYAML needed for the YAML leg")
class RoundTripTests(unittest.TestCase):
    def test_full_fixture_survives_markdown_json_yaml_markdown(self):
        p = Profile.load()
        frame, findings = markdown.parse(FIXTURE.read_text(encoding="utf-8"), p, FIXTURE.as_uri())
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        for name in p.refinements():
            # A key that is merely present but empty would still pass "in", and
            # would make this fixture exercise nothing for that refinement while
            # still looking green. Require actual content.
            self.assertTrue(frame.elements.get(name.name), f"fixture must carry a non-empty {name.name}")
        self.assertEqual(frame.elements["x-nebari-excludes"], ["acme/legacy-tone"])
        self.assertEqual(frame.elements["guards"], ["acme/pii-guard"])
        final, diffs, legs = roundtrip.round_trip(frame, p)
        # A round_trip that forgot to reassign its working value on each pass
        # would hand back the original object and trivially agree with itself.
        # Guard against that specific shortcut, not just against its symptom.
        self.assertIsNot(final, frame, "round_trip must return a freshly re-parsed Frame, not the original")
        self.assertEqual(diffs, [], diffs)
        self.assertEqual(final.elements, frame.elements)
        self.assertEqual([(leg, [str(f) for f in findings if f.level == "error"]) for leg, findings in legs],
                         [("json", []), ("yaml", []), ("markdown", [])])

    def test_a_difference_is_reported(self):
        p = Profile.load()
        frame, _ = markdown.parse(FIXTURE.read_text(encoding="utf-8"), p, FIXTURE.as_uri())
        diffs = roundtrip.diff_elements(frame.elements, dict(frame.elements, title="Changed"))
        self.assertEqual([d[0] for d in diffs], ["title"])

    def test_round_trip_detects_a_dropped_element(self):
        """The comparison must catch a value that a writer actually lost.

        A round trip that only ever compares two Frames derived the same way
        would pass even when an encoding silently drops data. Break the json
        writer on purpose, on a copy of the real output, and confirm the
        difference is reported rather than a clean result.
        """
        p = Profile.load()
        frame, _ = markdown.parse(FIXTURE.read_text(encoding="utf-8"), p, FIXTURE.as_uri())
        real_write_json = frame_io.WRITERS["json"]

        def broken_write_json(fr, profile):
            mapping = json.loads(real_write_json(fr, profile))
            del mapping["guards"]
            return json.dumps(mapping, indent=2, ensure_ascii=False) + "\n"

        with mock.patch.dict(frame_io.WRITERS, {"json": broken_write_json}):
            final, diffs, legs = roundtrip.round_trip(frame, p, order=("json",))
        names = [d[0] for d in diffs]
        self.assertIn("guards", names, "a dropped element must show up as a difference")

    def test_a_model_minimal_frame_now_has_a_valid_markdown_form_with_warnings(self):
        """Section 6.2.1 (amended) makes only `type` REQUIRED in the Markdown encoding.

        A Frame carrying only the two elements section 4.2 makes mandatory, identifier
        and guidance, used to have no valid Markdown form: the encoding made four
        front matter keys REQUIRED, so writing this Frame and reading it back reported
        three missing-required-key errors, a false green for anyone comparing element
        values alone. The amendment downgrades `name`, `description`, and `visibility`
        to SHOULD, so the same Frame's markdown leg now carries three
        missing-recommended-key warnings instead of errors, and the trip is clean.
        """
        p = Profile.load()
        frame, findings = frame_io.PARSERS["json"](
            '{"identifier": "acme/bare", "guidance": "just guidance"}', p, "file:///x/bare.frame.json")
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        final, diffs, legs = roundtrip.round_trip(frame, p)
        self.assertEqual(diffs, [], diffs)
        codes = {leg: [f.code for f in leg_findings if f.level == "error"] for leg, leg_findings in legs}
        self.assertEqual(codes["json"], [])
        self.assertEqual(codes["yaml"], [])
        self.assertEqual(codes["markdown"], [])
        markdown_findings = next(fs for leg, fs in legs if leg == "markdown")
        self.assertEqual([(f.level, f.code) for f in markdown_findings],
                         [("warning", "missing-recommended-key")] * 3)

    def test_an_error_level_leg_finding_still_fails_the_trip(self):
        """The amendment closes the one gap that used to make a leg's re-read error
        on element presence alone, but `type` is still REQUIRED and its value must
        still begin with the word 'frame' (section 6.2.1); a leg can still write a
        document it cannot read back for that reason. Built directly rather than
        parsed, since going through the json and yaml legs first would not preserve
        a `type` extra for the markdown leg to reproduce; `order` targets the leg
        that can still fail on its own.
        """
        p = Profile.load()
        frame = Frame({"identifier": "acme/bad-type", "guidance": ["g"]}, "json", None, {"type": "framework"})
        final, diffs, legs = roundtrip.round_trip(frame, p, order=("markdown",))
        self.assertEqual(diffs, [], diffs)
        codes = {leg: [f.code for f in leg_findings if f.level == "error"] for leg, leg_findings in legs}
        self.assertEqual(codes["markdown"], ["bad-type-token"])



class MarkdownLimitsTests(unittest.TestCase):
    """Section 6.2.4: four structures the Markdown encoding cannot express.

    Section 6.1's round-trip rule carves these out, so losing the structure is
    conforming. This tool still reports the loss, because a validator's job is to
    surface it; the rows below pin what is lost so the behaviour is deliberate
    rather than discovered.
    """

    def setUp(self):
        self.p = Profile.load()

    def test_each_documented_limit_loses_structure_and_is_reported(self):
        cases = [
            ("a refinement value containing a blank line",
             {"identifier": "x/y", "guidance": "G", "rules": ["First para.\n\nSecond para."]},
             "rules", ["First para.", "Second para."]),
            ("guidance holding a heading that matches a refinement label",
             {"identifier": "x/y", "guidance": "Be plain.\n\n## Rules\n\nBe nice."},
             "rules", ["Be nice."]),
        ]
        for label, elements, element, expected in cases:
            with self.subTest(label):
                frame, _ = yamljson.parse_json(json.dumps(elements), self.p, "file:///t.frame.json")
                back, findings = markdown.parse(markdown.write(frame, self.p), self.p,
                                                "file:///t.frame.md")
                self.assertFalse(has_errors(findings), [str(f) for f in findings])
                # The words survive, per section 4.4.1; the structure does not.
                self.assertEqual(back.elements[element], expected)
                self.assertIn("Second para." if element == "rules" and len(expected) == 2
                              else "Be nice.", str(back.elements[element]))

    @unittest.skipUnless(HAVE_YAML, "round_trip passes through the YAML leg")
    def test_the_loss_is_visible_in_round_trip_output(self):
        elements = {"identifier": "x/y", "guidance": "Be plain.\n\n## Rules\n\nBe nice."}
        frame, _ = yamljson.parse_json(json.dumps(elements), self.p, "file:///t.frame.json")
        _final, diffs, _legs = roundtrip.round_trip(frame, self.p)
        self.assertTrue(diffs, "a documented structural loss must not round-trip silently")
        self.assertIn("guidance", [name for name, _before, _after in diffs])


if __name__ == "__main__":
    unittest.main()
