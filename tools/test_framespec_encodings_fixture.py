import unittest
from pathlib import Path
from framespec import io as frame_io
from framespec.findings import has_errors
from framespec.profile import Profile

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

DIR = Path(__file__).resolve().parent.parent / "spec" / "fixtures" / "encodings"


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


if __name__ == "__main__":
    unittest.main()
