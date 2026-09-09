import json
import unittest
from pathlib import Path
from unittest import mock

from framespec import io as frame_io
from framespec import markdown, roundtrip
from framespec.findings import has_errors
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

    def test_a_leg_that_writes_an_unreadable_document_does_not_report_a_clean_trip(self):
        """The findings of each leg's own re-read are part of the result.

        A Frame carrying only the two elements section 4.2 makes mandatory has no
        valid Markdown form, because section 6.2.1 makes four front matter keys
        REQUIRED in that encoding. The element values still survive the trip, so
        comparing them alone reports OK for a trip that wrote a document with three
        errors in it. That is the false green this asserts against: the diffs are
        empty and the markdown leg's findings are not.
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
        self.assertEqual(codes["markdown"], ["missing-required-key"] * 3)


if __name__ == "__main__":
    unittest.main()
