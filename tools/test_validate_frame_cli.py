import os
import subprocess
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent


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


if __name__ == "__main__":
    unittest.main()
