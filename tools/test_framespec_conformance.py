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

    def test_narrowings_without_resolution_is_a_warning(self):
        # Rule 6's narrowings (non_repeatable and rule6_narrowings) only matter when
        # composition is actually resolved and merged, the same way reference_forms
        # only matters when something is resolved to classify a reference for. Declaring
        # a narrowing while resolves_composition is 'none' is the same shape of leftover,
        # unexercised declaration, so it earns the same warning by the same reasoning.
        # reference_forms is emptied here to isolate this condition from the other one.
        odd = dict(GOOD, resolves_composition="none", reference_forms=[])
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
        # "all-repeatable" is not itself an element, so under replace_by_key (where the
        # token has no meaning) it is reported as an unknown element, not as an element
        # that merely fails to be repeatable.
        bad_key = dict(GOOD, rule6_narrowings={"replace_by_key": "all-repeatable"})
        codes = [f.code for f in conformance.check_profile(bad_key, self.p) if f.level == "error"]
        self.assertIn("profile-unknown-element", codes)
        as_list = dict(GOOD, rule6_narrowings={"dedup": ["all-repeatable"]})
        self.assertFalse(has_errors(conformance.check_profile(as_list, self.p)))

    def test_an_unknown_narrowing_element_is_reported_as_unknown_not_non_repeatable(self):
        # profile.is_repeatable() returns False both for a real element that is simply
        # not repeatable (e.g. 'title') and for a name that is not an element at all.
        # additionally_required already distinguishes the two with profile-unknown-element;
        # rule6_narrowings must say the same thing about a name that does not exist,
        # rather than implying it exists but fails a repeatability test.
        unknown = dict(GOOD, rule6_narrowings={"dedup": ["not-a-real-element"]})
        codes = [f.code for f in conformance.check_profile(unknown, self.p) if f.level == "error"]
        self.assertIn("profile-unknown-element", codes)
        self.assertNotIn("profile-narrowing-not-content", codes)
        # 'title' exists but is not repeatable even at the model level: still the
        # narrowing-not-content code, since the name is real.
        not_repeatable = dict(GOOD, rule6_narrowings={"dedup": ["title"]})
        codes = [f.code for f in conformance.check_profile(not_repeatable, self.p) if f.level == "error"]
        self.assertIn("profile-narrowing-not-content", codes)
        self.assertNotIn("profile-unknown-element", codes)

    def test_a_non_string_scalar_field_value_is_a_finding_not_a_crash(self):
        # Appendix C's template spells "Resolves composition" as <no | yes, ...>. A
        # profile author extending that "no" convention to reference_forms writes
        # "reference_forms: no", which YAML reads as the Python bool False, not a
        # string or a list. _as_list() must wrap a value like this as one bad entry so
        # it reaches the ordinary vocabulary check, instead of crashing on list(False)
        # (TypeError: 'bool' object is not iterable) or, as the brief's draft did for
        # every list-shaped field before _as_list() existed, silently vanishing under
        # a bare `data.get(key) or []`.
        odd = dict(GOOD, reference_forms=False)
        findings = conformance.check_profile(odd, self.p)
        codes = [f.code for f in findings if f.level == "error"]
        self.assertIn("profile-bad-reference-form", codes)

    def test_as_list_wraps_a_non_iterable_scalar_instead_of_raising(self):
        # Every element _as_list() returns must be a string: call sites test set or
        # dict-key membership, which raises on an unhashable value rather than
        # producing a finding. A non-string scalar becomes its repr, a string; a
        # non-string element inside an already-list-shaped value becomes its repr too,
        # rather than passing an unhashable list, set, or dict through unexamined.
        self.assertEqual(conformance._as_list(None), [])
        self.assertEqual(conformance._as_list("style"), ["style"])
        self.assertEqual(conformance._as_list(["a", "b"]), ["a", "b"])
        self.assertEqual(conformance._as_list(False), ["False"])
        self.assertEqual(conformance._as_list(5), ["5"])
        self.assertEqual(conformance._as_list({"style": True}), ["{'style': True}"])
        self.assertEqual(conformance._as_list([["pinned-ref"]]), ["['pinned-ref']"])
        self.assertEqual(conformance._as_list(["pinned-ref", 5, ["nested"]]),
                         ["pinned-ref", "5", "['nested']"])

    def test_a_nested_list_element_is_a_finding_not_a_crash(self):
        # Reproduces the exact shape reported against the shipped --check-profile flag:
        # reference_forms: [[pinned-ref]] is a block list whose one item is itself a
        # flow list, an easy YAML slip. Before this, the inner list reached FORMS's `not
        # in` set-membership test unexamined and crashed with TypeError: cannot use
        # 'list' as a set element (unhashable type: 'list').
        odd = dict(GOOD, reference_forms=[["pinned-ref"]])
        findings = conformance.check_profile(odd, self.p)
        codes = [f.code for f in findings if f.level == "error"]
        self.assertIn("profile-bad-reference-form", codes)

    def test_a_mapping_value_is_a_finding_not_a_silent_decomposition_into_keys(self):
        # Reachable only through the library, calling check_profile() directly with a
        # raw mapping: through the shipped --check-profile flag, load_conformance()
        # validates non_repeatable and rule6_narrowings at load time and refuses
        # {"style": True} before check_profile() ever sees it (a clean
        # conformance-profile-unreadable finding, not a crash and not this test's
        # concern). Called directly, before this fix _as_list()'s bare list(value)
        # decomposed a mapping into its keys (list({"style": True}) == ["style"]),
        # which happened to be a real, repeatable content element and so validated as
        # profile-ok with zero findings: a false green for a value that was never a
        # list of names at all. Now the whole mapping becomes one unusable name.
        odd = dict(GOOD, non_repeatable={"style": True})
        findings = conformance.check_profile(odd, self.p)
        self.assertTrue(has_errors(findings), [str(f) for f in findings])

    def test_every_unguarded_field_reports_a_finding_for_every_bad_shape(self):
        # The matrix the round 2 review named: encodings_read, encodings_written,
        # reference_forms, and additionally_required are the four fields nothing
        # upstream of check_profile() validates (unlike non_repeatable and the two
        # rule6_narrowings keys, which load_conformance() validates at load time), so
        # _as_list() alone is what stands between a hand-authored profile's mistake and
        # a crash for these four. Each of a boolean, an integer, a mapping, and a
        # nested list must produce an ordinary error finding, never an exception.
        fields = ["encodings_read", "encodings_written", "reference_forms", "additionally_required"]
        shapes = {
            "boolean": False,
            "integer": 5,
            "mapping": {"a": 1},
            "nested list": [["x"]],
        }
        for field in fields:
            for shape_name, shape in shapes.items():
                with self.subTest(field=field, shape=shape_name):
                    odd = dict(GOOD, **{field: shape})
                    findings = conformance.check_profile(odd, self.p)
                    self.assertTrue(has_errors(findings), [str(f) for f in findings])

    def test_a_profile_written_entirely_in_scalar_shorthand_is_still_accepted(self):
        # Every list-shaped field written as a bare scalar rather than a one-item list,
        # confirming _as_list()'s new total coercion did not, in closing the crash and
        # false-green holes, also start rejecting the shorthand round 1 added it to
        # accept in the first place.
        shorthand = {
            "implementation": "X", "version": "1", "specification": "draft-mcandrew-frame-spec-00",
            "encodings_read": "markdown", "encodings_written": "json",
            "resolves_composition": "transitive", "reference_forms": "pinned-ref",
            "rule6_narrowings": {"dedup": "all-repeatable", "replace_by_key": "terminology"},
            "non_repeatable": "style", "additionally_required": "version",
            "identifier_minting": "not performed", "visibility": "declared intent only; not an access control",
        }
        findings = conformance.check_profile(shorthand, self.p)
        self.assertFalse(has_errors(findings), [str(f) for f in findings])


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


class NebariFramesProfileCompositionTests(unittest.TestCase):
    # Task 13's continuous integration workflow composes spec/fixtures/composition/
    # under this profile and diffs the result against expected-style-non-repeatable.json
    # byte for byte; that fixture lives entirely outside this task's file list, and so
    # does the workflow that will check it, but nothing stops a change to the profile or
    # to the resolver from being noticed here first, before that CI exists to catch it.
    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_reproduces_the_composition_fixture_byte_for_byte(self):
        order = ["company-core.frame.json", "brand-voice.frame.json", "q4-playbook.frame.json"]
        result = run("--compose", "--conformance-profile", "spec/profiles/nebari-frames.yaml",
                     *[f"spec/fixtures/composition/{name}" for name in order])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        expected = (REPO / "spec" / "fixtures" / "composition" /
                    "expected-style-non-repeatable.json").read_text(encoding="utf-8")
        self.assertEqual(result.stdout, expected)


if __name__ == "__main__":
    unittest.main()
