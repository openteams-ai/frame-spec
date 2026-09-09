import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent

sys.path.insert(0, str(TOOLS))

import validate_frame  # noqa: E402 - needs the sys.path insert above
from framespec.profile import Profile  # noqa: E402 - same reason

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False


def run(*args):
    return subprocess.run([sys.executable, str(TOOLS / "validate_frame.py"), *args],
                          capture_output=True, text=True, cwd=REPO)


class CliTests(unittest.TestCase):
    def test_all_eighteen_examples_pass(self):
        result = run("examples")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Frames checked: 18   passed: 18   failed: 0", result.stdout)

    def test_a_bad_markdown_frame_fails_with_exit_1(self):
        bad = TOOLS / "_cli_bad.frame.md"
        bad.write_text("---\ntype: frame [0.3.0]\ndescription: D\nvisibility: internal\n---\nbody\n", encoding="utf-8")
        try:
            result = run(str(bad))
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing-required-key", result.stdout)
            self.assertIn("bad-type-token", result.stdout)
        finally:
            bad.unlink()

    def test_unregistered_status_is_a_warning_not_a_failure(self):
        result = run("examples/sow-review/business-owner.frame.md")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("unregistered-value", result.stdout)

    def test_directory_scan_ignores_sketch_yaml_and_plain_markdown(self):
        # self-frame holds README.md, references/rationale.md, frame/spec.yaml, frame/package.yaml,
        # nebi.toml: two Markdown files without front matter, no Frame, and no *.frame.yaml.
        result = run("examples/self-frame")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Frames checked: 0   passed: 0   failed: 0   skipped: 2", result.stdout)

    def test_a_path_that_does_not_exist_fails_with_exit_1(self):
        # collect() only recognizes a path as a directory or a file; anything
        # else must not disappear silently, or a typo'd path would leave the
        # exit code at 0 with nothing checked and nothing to show for it.
        result = run("examples/this-path-does-not-exist.frame.md")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("path-not-found", result.stdout)
        self.assertIn("Frames checked: 1   passed: 0   failed: 1   skipped: 0", result.stdout)

    def test_a_missing_path_does_not_hide_a_real_one_in_the_same_run(self):
        result = run("examples/minimal/frame.md", "examples/still-does-not-exist.frame.md")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("path-not-found", result.stdout)
        self.assertIn("Frames checked: 2   passed: 1   failed: 1   skipped: 0", result.stdout)

    def test_an_undecodable_file_reports_a_finding_instead_of_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "undecodable.frame.md"
            bad.write_bytes(b"\xff\xfe\x00\x01not valid utf-8")
            result = run(str(bad))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("file-unreadable", result.stdout)
        self.assertIn("Frames checked: 1   passed: 0   failed: 1   skipped: 0", result.stdout)

    def test_directory_scan_with_an_unreadable_file_still_checks_the_valid_frame(self):
        # Named so the undecodable file sorts before the valid one: before the fix,
        # an unhandled UnicodeDecodeError on the first file would crash the whole
        # process and the second file, along with the summary line, would never
        # be reached at all.
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "aaa-undecodable.frame.md").write_bytes(b"\xff\xfe\x00\x01not valid utf-8")
            (tmp_path / "zzz-good.frame.md").write_text(
                "---\ntype: frame [0.3]\nname: Good\ndescription: D\nvisibility: internal\n---\nbody\n",
                encoding="utf-8",
            )
            result = run(str(tmp_path))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("file-unreadable", result.stdout)
        self.assertIn("Frames checked: 2   passed: 1   failed: 1   skipped: 0", result.stdout)

    def test_round_trip_reports_ok_for_the_full_fixture(self):
        result = run("--round-trip", "spec/fixtures/roundtrip/full.frame.md")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ROUND-TRIP OK", result.stdout)

    @unittest.skipUnless(HAVE_YAML, "the yaml leg needs PyYAML")
    def test_round_trip_fails_when_a_leg_writes_a_document_that_cannot_be_read_back(self):
        # A Frame carrying only the two elements section 4.2 makes mandatory writes a
        # Markdown document that section 6.2.1 rejects, since that encoding makes four
        # front matter keys REQUIRED. The element values survive, so comparing them
        # alone reported ROUND-TRIP OK and exit 0 for a trip that produced an invalid
        # document. The run must fail and name the leg and the finding.
        with tempfile.TemporaryDirectory() as tmp:
            bare = Path(tmp) / "bare.frame.json"
            bare.write_text('{"identifier": "acme/bare", "guidance": "just guidance"}\n', encoding="utf-8")
            result = run("--round-trip", str(bare))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("the markdown leg", result.stdout)
        self.assertEqual(result.stdout.count("missing-required-key"), 3, result.stdout)
        self.assertNotIn("ROUND-TRIP OK", result.stdout)

    def test_round_trip_reports_a_failure_for_an_unreadable_file_instead_of_a_silent_skip(self):
        # round_trip_paths() must tell read_frame()'s two None-returning cases
        # apart: (None, None) is a file that is not a Frame and is skipped on
        # purpose, but (None, [finding]) is a file that could not be read at
        # all. Treating both the same way would let an unreadable file exit 0
        # having checked nothing, the same false-green validate_paths already
        # guards against for its own scan.
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "undecodable.frame.md"
            bad.write_bytes(b"\xff\xfe\x00\x01not valid utf-8")
            result = run("--round-trip", str(bad))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("file-unreadable", result.stdout)
        self.assertIn("ROUND-TRIP FAIL", result.stdout)

    def test_round_trip_reports_path_not_found_for_a_typod_path(self):
        # report_missing() is shared with validate_paths(); --round-trip must
        # get the same false-green protection for a path collect() would
        # otherwise silently drop.
        result = run("--round-trip", "examples/this-path-does-not-exist.frame.md")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("path-not-found", result.stdout)
        self.assertIn("ROUND-TRIP FAIL", result.stdout)

    def test_round_trip_reports_pyyaml_required_instead_of_crashing(self):
        # Simulate PyYAML being absent without uninstalling it: a None
        # sentinel in sys.modules for "yaml" makes Python's import system
        # raise ImportError for any "import yaml" statement, exactly as if
        # the package were not installed, and the patch restores cleanly
        # afterward. This has to run in-process, not through the run()
        # subprocess helper, since the sentinel only exists in the process
        # that sets it.
        profile = Profile.load()
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.frame.md"
            good.write_text(
                "---\ntype: frame [0.3]\nname: Good\ndescription: D\nvisibility: internal\n---\nbody\n",
                encoding="utf-8",
            )
            out = io.StringIO()
            with mock.patch.dict(sys.modules, {"yaml": None}):
                result = validate_frame.round_trip_paths([str(good)], "auto", profile, out=out)
        self.assertEqual(result, 1)
        self.assertIn("pyyaml-required", out.getvalue())
        self.assertIn("ROUND-TRIP FAIL", out.getvalue())


if __name__ == "__main__":
    unittest.main()
