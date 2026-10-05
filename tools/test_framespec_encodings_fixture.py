import re
import unittest
from pathlib import Path
from framespec import io as frame_io
from framespec.findings import has_errors
from framespec.profile import Profile
from framespec.selfcheck import DEFAULT_SPEC_PATH

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

DIR = Path(__file__).resolve().parent.parent / "spec" / "fixtures" / "encodings"

# spec/fixtures/README.md says these three files are Figures 6 to 8 of the draft.
FIGURES = (("Figure 6", "brand-voice.frame.md"),
           ("Figure 7", "brand-voice.frame.yaml"),
           ("Figure 8", "brand-voice.frame.json"))
FENCE_RE = re.compile(r"^```[^\n]*\n(.*?)^```", re.M | re.S)


def figure_block(text, caption):
    """The fenced block a figure's caption labels, or None when there is none.

    Anchored on the caption rather than on a section heading, because the caption is
    what names the figure: the block a caption labels is the last one that ends before
    it. framespec.selfcheck.read_appendix_profile() anchors on a heading for the same
    reason, that being what identifies its block.
    """
    end = text.find(f"*{caption}:")
    if end < 0:
        return None
    blocks = [m.group(1) for m in FENCE_RE.finditer(text) if m.end() <= end]
    return blocks[-1] if blocks else None


class EncodingsFixtureTests(unittest.TestCase):
    def load(self, name):
        p = Profile.load()
        path = DIR / name
        frame, findings = frame_io.read_frame(path, frame_io.detect_encoding(path), p)
        self.assertIsNotNone(frame, name)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        return frame

    def test_markdown_and_json_normalize_identically(self):
        md = self.load("brand-voice.frame.md")
        js = self.load("brand-voice.frame.json")
        self.assertEqual(md.elements, js.elements)
        self.assertEqual(md.elements["identifier"], "acme/brand-voice")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_yaml_normalizes_identically_too(self):
        self.assertEqual(self.load("brand-voice.frame.yaml").elements, self.load("brand-voice.frame.json").elements)


class DraftFigureTests(unittest.TestCase):
    """The fixtures are the draft's own figures, checked rather than kept by hand.

    spec/fixtures/README.md claims these three files are Figures 6 to 8, so a figure
    edited in the draft and not here would leave the fixtures testing a Frame the
    draft no longer shows, with nothing to say so. This is the discipline
    framespec.selfcheck applies to Appendix B's fenced copy of the profile, as a test
    rather than inside that module: the fixtures are test inputs and not a third copy
    of the normative element set, and --self-check must go on working in a checkout
    that has no fixtures.
    """

    def test_each_fixture_is_byte_for_byte_the_figure_it_claims_to_be(self):
        text = DEFAULT_SPEC_PATH.read_text(encoding="utf-8")
        for caption, name in FIGURES:
            with self.subTest(figure=caption):
                block = figure_block(text, caption)
                self.assertIsNotNone(block, f"no fenced block under {caption} in {DEFAULT_SPEC_PATH}")
                # A pattern that stopped matching would otherwise compare two empty
                # strings and pass, which is the failure this test exists to prevent.
                self.assertTrue(block.strip(), f"{caption}'s block came out empty")
                self.assertEqual(block, (DIR / name).read_text(encoding="utf-8"))

    def test_a_figure_that_drifted_from_its_fixture_is_reported(self):
        # The comparison has to be able to fail: proved on an edited copy of the draft
        # rather than by editing the draft itself.
        text = DEFAULT_SPEC_PATH.read_text(encoding="utf-8")
        edited = text.replace("name: Brand Voice", "name: Brand Tone", 1)
        self.assertNotEqual(edited, text)
        block = figure_block(edited, "Figure 6")
        self.assertNotEqual(block, (DIR / "brand-voice.frame.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
