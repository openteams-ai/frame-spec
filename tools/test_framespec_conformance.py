import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from framespec import conformance
from framespec.findings import has_errors
from framespec.profile import Profile

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
DIR = REPO / "spec" / "profiles"

sys.path.insert(0, str(TOOLS))

import validate_frame  # noqa: E402 - needs the sys.path insert above


def run(*args):
    return subprocess.run([sys.executable, str(TOOLS / "validate_frame.py"), *args],
                          capture_output=True, text=True, cwd=REPO)


GOOD = {
    "implementation": "X", "version": "1", "specification": "draft-mcandrew-frame-spec-00",
    "encodings_read": ["markdown"], "encodings_written": ["json"],
    "resolves_composition": "transitive", "reference_forms": ["pinned-ref", "uri-ref"],
    "rule6_narrowings": {"dedup": ["rules"], "replace_by_key": ["terminology"]},
    "non_repeatable": ["style"], "additionally_required": ["version"],
    "identifier_minting": "not performed", "visibility": "declared intent only; not an access control",
}


class ConformanceTests(unittest.TestCase):
    def setUp(self):
        self.p = Profile.load()

    def test_good_profile_has_no_errors(self):
        self.assertFalse(has_errors(conformance.check_profile(GOOD, self.p)))

    def test_missing_key_and_bad_values(self):
        bad = dict(GOOD)
        del bad["identifier_minting"]
        bad["encodings_read"] = ["xml"]
        bad["resolves_composition"] = "sometimes"
        bad["non_repeatable"] = ["title"]
        codes = [f.code for f in conformance.check_profile(bad, self.p) if f.level == "error"]
        self.assertIn("profile-missing-key", codes)
        self.assertIn("profile-bad-encoding", codes)
        self.assertIn("profile-bad-resolution", codes)
        self.assertIn("profile-narrowing-not-content", codes)

    def test_forms_without_resolution_is_a_warning(self):
        odd = dict(GOOD, resolves_composition="none")
        codes = [f.code for f in conformance.check_profile(odd, self.p) if f.level == "warning"]
        self.assertIn("profile-forms-without-resolution", codes)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_both_repository_profiles_validate_and_differ(self):
        from framespec.compose import load_conformance
        nf = load_conformance(DIR / "nebari-frames.yaml")
        cb = load_conformance(DIR / "collab.yaml")
        self.assertFalse(has_errors(conformance.check_profile(nf, self.p)), [str(f) for f in conformance.check_profile(nf, self.p)])
        self.assertFalse(has_errors(conformance.check_profile(cb, self.p)), [str(f) for f in conformance.check_profile(cb, self.p)])
        self.assertNotEqual(nf["resolves_composition"], cb["resolves_composition"])
        self.assertNotEqual(nf["non_repeatable"], cb["non_repeatable"])

    def test_non_repeatable_accepts_the_bare_scalar_shorthand(self):
        # framespec.compose._names() reads non_repeatable: style the same way as
        # non_repeatable: [style] (YAML's natural form for one value is a scalar).
        # Before this was normalized here too, the checker iterated the string
        # character by character and reported five bogus findings ('s', 't', 'y',
        # 'l', 'e') for a profile compose() itself accepts without complaint.
        scalar = dict(GOOD, non_repeatable="style")
        findings = conformance.check_profile(scalar, self.p)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])
        listed = dict(GOOD, non_repeatable=["style"])
        self.assertEqual([f.code for f in conformance.check_profile(scalar, self.p)],
                         [f.code for f in conformance.check_profile(listed, self.p)])

    def test_rule6_narrowing_of_an_element_also_declared_non_repeatable_is_rejected(self):
        # A profile that puts the same element in both non_repeatable and a
        # rule6_narrowings key is internally contradictory: non_repeatable sends the
        # element through rule 6's replace branch (the highest-precedence value wins),
        # where dedup and replace-by-key never run. framespec.compose bears this out:
        # compose()'s non_repeatable branch continues before the concatenate-then-narrow
        # code that would apply either narrowing, so the declaration describes a merge
        # step the profile's own composition can never reach.
        contradictory = dict(GOOD, non_repeatable=["style"], rule6_narrowings={"dedup": ["style"]})
        codes = [f.code for f in conformance.check_profile(contradictory, self.p) if f.level == "error"]
        self.assertIn("profile-narrowing-not-content", codes)

    def test_all_repeatable_token_is_valid_only_for_dedup(self):
        # "all-repeatable" names every repeatable element at once and is meaningful
        # only for the dedup narrowing (draft section 5.1, rule 6); replace-by-key has
        # no such token. The checker must also recognize the token when it is written
        # as a one-item list, since framespec.compose._names() treats dedup: all-repeatable
        # and dedup: [all-repeatable] identically.
        bad_key = dict(GOOD, rule6_narrowings={"replace_by_key": "all-repeatable"})
        codes = [f.code for f in conformance.check_profile(bad_key, self.p) if f.level == "error"]
        self.assertIn("profile-narrowing-not-content", codes)
        as_list = dict(GOOD, rule6_narrowings={"dedup": ["all-repeatable"]})
        self.assertFalse(has_errors(conformance.check_profile(as_list, self.p)))


class CheckProfileCliTests(unittest.TestCase):
    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_both_repository_profiles_pass_with_exit_0(self):
        result = run("--check-profile", "spec/profiles/nebari-frames.yaml", "spec/profiles/collab.yaml")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.count("profile-ok"), 2)

    def test_check_profile_without_paths_reports_the_usage_error_instead_of_crashing(self):
        result = run("--check-profile")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("--check-profile", result.stderr)

    def test_a_path_that_does_not_exist_fails_with_path_not_found_not_a_crash(self):
        result = run("--check-profile", "spec/profiles/does-not-exist.yaml")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("path-not-found", result.stdout)

    def test_a_missing_path_does_not_hide_a_good_one_in_the_same_run(self):
        result = run("--check-profile", "spec/profiles/nebari-frames.yaml", "spec/profiles/does-not-exist.yaml")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("path-not-found", result.stdout)
        self.assertIn("profile-ok", result.stdout)

    def test_a_malformed_profile_is_a_finding_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "profile.json"
            bad.write_text('["not", "a", "mapping"]', encoding="utf-8")
            result = run("--check-profile", str(bad))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("conformance-profile-unreadable", result.stdout)
        self.assertNotIn("Traceback", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_a_directory_is_a_finding_not_a_crash(self):
        # A conformance profile is one file; report_missing() alone would wave a
        # directory through since collect() elsewhere treats directories as valid, so
        # load_conformance()'s own IsADirectoryError is what must be caught here.
        result = run("--check-profile", "spec/profiles")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("conformance-profile-unreadable", result.stdout)
        self.assertNotIn("Traceback", result.stdout)

    def test_a_profile_with_errors_exits_1(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "profile.json"
            bad.write_text('{"implementation": "Y", "resolves_composition": "sometimes"}', encoding="utf-8")
            result = run("--check-profile", str(bad))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("profile-missing-key", result.stdout)
        self.assertIn("profile-bad-resolution", result.stdout)
        self.assertIn("FAIL", result.stdout)

    def test_a_yaml_profile_without_pyyaml_is_a_finding_not_a_traceback(self):
        # The same sentinel technique test_validate_frame_cli.py and
        # test_framespec_compose.py use: a None in sys.modules makes "import yaml"
        # raise ImportError as though PyYAML were not installed. In-process only,
        # since the sentinel lives in this process, not a subprocess.
        out = io.StringIO()
        with mock.patch.dict(sys.modules, {"yaml": None}):
            code = validate_frame.check_profile_paths(["spec/profiles/nebari-frames.yaml"], Profile.load(), out=out)
        self.assertEqual(code, 1)
        self.assertIn("pyyaml-required", out.getvalue())
        self.assertNotIn("Traceback", out.getvalue())


if __name__ == "__main__":
    unittest.main()
