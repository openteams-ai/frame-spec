import datetime
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent

sys.path.insert(0, str(TOOLS))

import validate_frame                          # noqa: E402 - needs the sys.path insert above
from framespec import compose, io as frame_io  # noqa: E402 - same reason
from framespec.compose import ALL_REPEATABLE   # noqa: E402 - same reason
from framespec.model import Frame              # noqa: E402 - same reason
from framespec.profile import CONTENT_ROOT, Profile  # noqa: E402 - same reason

try:
    import yaml                                # noqa: F401 - presence is the point
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

DIR = REPO / "spec" / "fixtures" / "composition"
ORDER = ["company-core.frame.json", "brand-voice.frame.json", "q4-playbook.frame.json"]
NARROWING = DIR / "style-non-repeatable.conformance.yaml"
SPEC = REPO / "spec" / "frame-spec.md"

# Rule 5 no longer enumerates every element that MUST NOT be inherited: a spec
# amendment replaced the list with a derivation (the complement of "content elements
# and guards") plus three named examples, identifier and maintainer, then composition
# on its own. The examples are read out of the draft rather than copied here, so
# prose and code cannot drift apart unnoticed the way the old two-statement rule did.
RULE5_RE = re.compile(r"MUST NOT be inherited from a composed Frame: ([^.]*\.)")


def run(*args):
    return subprocess.run([sys.executable, str(TOOLS / "validate_frame.py"), *args],
                          capture_output=True, text=True, cwd=REPO)


def load_frames(names=ORDER):
    """The fixture Frames, lowest precedence first."""
    profile = Profile.load()
    frames = []
    for name in names:
        frame, findings = frame_io.read_frame(DIR / name, "json", profile)
        if frame is None:
            raise AssertionError(f"fixture {name} did not parse: {[str(f) for f in (findings or [])]}")
        frames.append(frame)
    return profile, frames


def rule5_elements():
    """The element names rule 5 gives as examples of what MUST NOT be inherited, from the draft."""
    match = RULE5_RE.search(SPEC.read_text(encoding="utf-8"))
    if match is None:
        raise AssertionError("rule 5's named examples were not found in spec/frame-spec.md")
    return re.findall(r"`([A-Za-z]+)`", match.group(1))


class ComposeTests(unittest.TestCase):
    def test_model_level_matches_expected(self):
        p, frames = load_frames()
        result = compose.compose(frames, p)
        expected = json.loads((DIR / "expected-model.json").read_text(encoding="utf-8"))
        self.assertEqual(result.elements, expected)

    def test_description_is_not_inherited(self):
        p, frames = load_frames()
        self.assertNotIn("description", compose.compose(frames, p).elements)

    def test_profile_narrowing_style_non_repeatable(self):
        p, frames = load_frames()
        result = compose.compose(frames, p, {"non_repeatable": ["style"]})
        expected = json.loads((DIR / "expected-style-non-repeatable.json").read_text(encoding="utf-8"))
        self.assertEqual(result.elements, expected)

    def test_dedup_and_replace_by_key(self):
        p = Profile.load()
        a = Frame({"identifier": "a", "guidance": ["x"], "rules": ["r1", "r2"],
                   "terminology": [{"term": "Hub", "definition": "old"}]}, "json")
        b = Frame({"identifier": "b", "guidance": ["y"], "rules": ["r2", "r3"],
                   "terminology": [{"term": "Hub", "definition": "new"}]}, "json")
        result = compose.compose([a, b], p, {"rule6_narrowings": {"dedup": "all-repeatable",
                                                                  "replace_by_key": ["terminology"]}})
        self.assertEqual(result.elements["rules"], ["r1", "r2", "r3"])
        self.assertEqual(result.elements["terminology"], [{"term": "Hub", "definition": "new"}])


class PrecedenceDirectionTests(unittest.TestCase):
    """Rules 2 and 3: the last Frame given is the highest precedence."""

    def test_reversing_the_order_reverses_the_concatenation(self):
        p, frames = load_frames()
        forward = compose.compose(frames, p).elements["rules"]
        backward = compose.compose(list(reversed(frames)), p).elements["rules"]
        self.assertEqual(forward, ["cite sources", "no hype", "lead with impact"])
        self.assertEqual(backward, ["lead with impact", "no hype", "cite sources"])

    def test_reversing_the_order_changes_which_value_the_replace_branch_takes(self):
        p, frames = load_frames()
        narrowing = {"non_repeatable": ["style"]}
        self.assertEqual(compose.compose(frames, p, narrowing).elements["style"], "plain")
        # Reversed, company-core is highest and no longer loses to brand-voice.
        self.assertEqual(compose.compose(list(reversed(frames)), p, narrowing).elements["style"], "formal")

    def test_the_declaring_frame_is_the_last_one_given(self):
        p, frames = load_frames()
        self.assertEqual(compose.compose(frames, p).elements["identifier"], "acme/q4-playbook")
        self.assertEqual(compose.compose(list(reversed(frames)), p).elements["identifier"],
                         "acme/company-core")


class Rule5Tests(unittest.TestCase):
    def test_the_examples_rule_5_names_do_not_compose(self):
        # Rule 5 used to enumerate every element that MUST NOT be inherited; a spec
        # amendment replaced that with a derivation and three named examples instead,
        # since restating the complement in prose was a second statement of the same
        # fact and the two could drift. The three examples must still land on the
        # non-composing side of whatever the derivation produces.
        p = Profile.load()
        composing = compose.composing_elements(p)
        named = rule5_elements()
        self.assertEqual(set(named), {"identifier", "maintainer", "composition"}, named)
        for name in named:
            self.assertIn(name, p.elements, f"rule 5 names {name!r}, which the profile does not define")
            self.assertNotIn(name, composing, f"rule 5 says {name!r} MUST NOT be inherited")

    def test_what_does_not_compose_is_every_element_outside_content_and_guards(self):
        # Rule 5's own words for the complement, now that it states the derivation
        # instead of listing it: every element that neither refines guidance nor is
        # guards. Computed here straight from the profile's refines column, rather
        # than by calling compose.composing_elements() and comparing it to itself, so
        # this is a check on that function and not a restatement of it. The three
        # elements rule 5 names as examples must fall on the non-composing side.
        p = Profile.load()
        composing = set(compose.composing_elements(p))
        expected_composing = {CONTENT_ROOT, compose.GUARDS} | {
            name for name in p.order if p.elements[name].refines == CONTENT_ROOT
        }
        self.assertEqual(composing, expected_composing)
        not_composing = set(p.order) - composing
        for name in ("identifier", "maintainer", "composition"):
            self.assertIn(name, not_composing)

    def test_guidance_its_refinements_and_guards_are_what_composes(self):
        p = Profile.load()
        self.assertEqual(list(compose.composing_elements(p)), p.content_elements() + ["guards"])
        self.assertEqual(len(compose.composing_elements(p)), 12)   # guidance, ten refinements, guards

    def test_composition_stays_with_the_declaring_frame(self):
        p, frames = load_frames()
        result = compose.compose(frames, p).elements
        # brand-voice composes acme/company-core; only q4-playbook's own value survives.
        self.assertEqual(result["composition"], ["acme/brand-voice"])

    def test_unknown_and_extension_elements_are_not_inherited_but_are_kept(self):
        p = Profile.load()
        parent = Frame({"identifier": "a", "guidance": ["x"], "x-parent": "p", "unknown": "u"}, "json")
        child = Frame({"identifier": "b", "guidance": ["y"], "x-child": "c"}, "json")
        result = compose.compose([parent, child], p).elements
        self.assertEqual(result["x-child"], "c")
        self.assertNotIn("x-parent", result)
        self.assertNotIn("unknown", result)

    def test_guards_accumulate_even_when_a_profile_declares_them_non_repeatable(self):
        # Rule 5 makes guards accumulate without qualification, and rule 6's narrowings
        # are for content elements. A profile cannot drop a Guard by declaring guards
        # non-repeatable, which is the failure the compliance case in rule 5 rules out.
        p = Profile.load()
        frames = [Frame({"identifier": "a", "guidance": [""], "guards": ["acme/pii-guard"]}, "json"),
                  Frame({"identifier": "b", "guidance": [""], "guards": ["acme/legal-guard"]}, "json")]
        result = compose.compose(frames, p, {"non_repeatable": ["guards"]})
        self.assertEqual(result.elements["guards"], ["acme/pii-guard", "acme/legal-guard"])


class Rule6Tests(unittest.TestCase):
    def test_the_replace_branch_takes_the_highest_precedence_present_value_even_when_empty(self):
        # q4-playbook declares guidance as "". Section 4.2.2 makes an empty guidance a
        # present value that "carries nothing", so under a profile that declares
        # guidance non-repeatable it replaces the values below it. Skipping it would
        # hand the result to a lower-precedence Frame, which rule 6 does not allow.
        p, frames = load_frames()
        result = compose.compose(frames, p, {"non_repeatable": ["guidance"]})
        self.assertEqual(result.elements["guidance"], "")

    def test_the_replace_branch_skips_a_frame_that_does_not_have_the_element(self):
        p, frames = load_frames()
        result = compose.compose(frames, p, {"non_repeatable": ["style"]})
        self.assertEqual(result.elements["style"], "plain")

    def test_the_concatenate_branch_leaves_out_an_empty_value(self):
        p, frames = load_frames()
        self.assertEqual(compose.compose(frames, p).elements["guidance"],
                         ["Company-wide guidance.", "Sound like us."])

    def test_dedup_keeps_the_first_occurrence_in_the_concatenation(self):
        # Rule 6 keeps the first occurrence, not the highest-precedence one: identical
        # values do not conflict, so rule 3's precedence has no say in this, and keeping
        # the first is what makes the deduplicated result a subsequence of the
        # concatenation rather than a reordering of it.
        p = Profile.load()
        a = Frame({"identifier": "a", "guidance": [""], "rules": ["x", "y"]}, "json")
        b = Frame({"identifier": "b", "guidance": [""], "rules": ["y", "x"]}, "json")
        result = compose.compose([a, b], p, {"rule6_narrowings": {"dedup": ["rules"]}})
        self.assertEqual(result.elements["rules"], ["x", "y"])

    def test_a_dedup_narrowing_written_as_one_name_narrows_that_element_only(self):
        p = Profile.load()
        a = Frame({"identifier": "a", "guidance": [""], "rules": ["x"], "style": ["s"]}, "json")
        b = Frame({"identifier": "b", "guidance": [""], "rules": ["x"], "style": ["s"]}, "json")
        result = compose.compose([a, b], p, {"rule6_narrowings": {"dedup": "rules"}})
        self.assertEqual(result.elements["rules"], ["x"])
        self.assertEqual(result.elements["style"], ["s", "s"])

    def test_a_non_repeatable_declaration_takes_precedence_over_the_narrowings(self):
        # Both narrowings are defined "within a repeatable element", so an element the
        # profile declares non-repeatable goes through the replace branch and neither
        # narrowing applies to it.
        p = Profile.load()
        a = Frame({"identifier": "a", "guidance": [""],
                   "terminology": [{"term": "Hub", "definition": "old"}]}, "json")
        b = Frame({"identifier": "b", "guidance": [""],
                   "terminology": [{"term": "Cog", "definition": "new"}]}, "json")
        result = compose.compose([a, b], p, {"non_repeatable": ["terminology"],
                                             "rule6_narrowings": {"dedup": ALL_REPEATABLE,
                                                                  "replace_by_key": ["terminology"]}})
        self.assertEqual(result.elements["terminology"], {"term": "Cog", "definition": "new"})

    def test_replace_by_key_leaves_unstructured_terminology_alone(self):
        # Section 4.4.2 allows terminology content that is not in the structured form;
        # such a value carries no key, so replacement by key must not touch it.
        p = Profile.load()
        a = Frame({"identifier": "a", "guidance": [""],
                   "terminology": ["Prefer Hub over instance.", {"term": "Hub", "definition": "old"}]}, "json")
        b = Frame({"identifier": "b", "guidance": [""],
                   "terminology": [{"term": "Hub", "definition": "new"}]}, "json")
        result = compose.compose([a, b], p, {"rule6_narrowings": {"replace_by_key": ["terminology"]}})
        self.assertEqual(result.elements["terminology"],
                         ["Prefer Hub over instance.", {"term": "Hub", "definition": "new"}])

    def test_guidance_is_present_even_when_every_frame_leaves_it_empty(self):
        p = Profile.load()
        frames = [Frame({"identifier": "a", "guidance": [""]}, "json"),
                  Frame({"identifier": "b", "guidance": [""]}, "json")]
        self.assertEqual(compose.compose(frames, p).elements["guidance"], [""])
        self.assertEqual(compose.compose(frames, p, {"non_repeatable": ["guidance"]}).elements["guidance"], "")

    def test_composing_no_frames_is_an_error_rather_than_a_crash(self):
        with self.assertRaises(ValueError):
            compose.compose([], Profile.load())


class NarrowingFormTests(unittest.TestCase):
    """A profile writes a narrowing as one name or as a list, and both must be read."""

    def test_a_non_repeatable_narrowing_written_as_one_name_is_honored(self):
        # non_repeatable: style is YAML's natural form for a single value. Iterating the
        # string would take it apart into letters, and the resolved Frame would
        # contradict the profile it was resolved under.
        p, frames = load_frames()
        self.assertEqual(compose.compose(frames, p, {"non_repeatable": "style"}).elements["style"],
                         "plain")
        self.assertEqual(compose.compose(frames, p, {"non_repeatable": ["style"]}).elements["style"],
                         "plain")

    def test_a_replace_by_key_narrowing_written_as_one_name_is_honored(self):
        p = Profile.load()
        a = Frame({"identifier": "a", "guidance": [""],
                   "terminology": [{"term": "Hub", "definition": "old"}]}, "json")
        b = Frame({"identifier": "b", "guidance": [""],
                   "terminology": [{"term": "Hub", "definition": "new"}]}, "json")
        for declared in ("terminology", ["terminology"]):
            with self.subTest(declared=declared):
                result = compose.compose([a, b], p, {"rule6_narrowings": {"replace_by_key": declared}})
                self.assertEqual(result.elements["terminology"], [{"term": "Hub", "definition": "new"}])

    def test_the_dedup_token_is_read_in_either_form(self):
        p = Profile.load()
        a = Frame({"identifier": "a", "guidance": [""], "rules": ["x"]}, "json")
        b = Frame({"identifier": "b", "guidance": [""], "rules": ["x"]}, "json")
        for declared in (ALL_REPEATABLE, [ALL_REPEATABLE]):
            with self.subTest(declared=declared):
                result = compose.compose([a, b], p, {"rule6_narrowings": {"dedup": declared}})
                self.assertEqual(result.elements["rules"], ["x"])

    def test_a_narrowing_that_is_not_element_names_is_an_error_naming_the_key(self):
        # A malformed declaration must not resolve as though the profile had declared
        # nothing, and must not reach the user as a TypeError traceback either.
        p, frames = load_frames()
        cases = [
            ("non_repeatable", {"non_repeatable": 5}),
            ("non_repeatable", {"non_repeatable": ["style", 5]}),
            ("rule6_narrowings.dedup", {"rule6_narrowings": {"dedup": 5}}),
            ("rule6_narrowings.replace_by_key", {"rule6_narrowings": {"replace_by_key": 5}}),
            ("rule6_narrowings", {"rule6_narrowings": 5}),
        ]
        for key, conformance in cases:
            with self.subTest(conformance=conformance):
                with self.assertRaises(ValueError) as caught:
                    compose.compose(frames, p, conformance)
                self.assertIn(key, str(caught.exception))
        with self.assertRaises(ValueError):
            compose.compose(frames, p, ["style"])          # not a mapping at all


class StableKeyTests(unittest.TestCase):
    def test_a_number_and_its_string_are_not_the_same_value(self):
        # Deduplication drops values that share a key, and rule 6 forbids dropping
        # values that are not identical, so 1 and "1" must not share one.
        self.assertNotEqual(compose._stable_key(1), compose._stable_key("1"))
        p = Profile.load()
        a = Frame({"identifier": "a", "guidance": [""], "rules": [1]}, "json")
        b = Frame({"identifier": "b", "guidance": [""], "rules": ["1"]}, "json")
        result = compose.compose([a, b], p, {"rule6_narrowings": {"dedup": ALL_REPEATABLE}})
        self.assertEqual(result.elements["rules"], [1, "1"])

    def test_a_value_json_cannot_serialize_still_gets_a_key(self):
        # normalize() turns dates into text, so this is defensive: the fallback keeps
        # deduplication working on a value json.dumps refuses rather than raising.
        day = datetime.date(2026, 9, 8)
        self.assertEqual(compose._stable_key(day), compose._stable_key(datetime.date(2026, 9, 8)))
        self.assertNotEqual(compose._stable_key(day), compose._stable_key("2026-09-08"))


class LoadConformanceTests(unittest.TestCase):
    @unittest.skipUnless(HAVE_YAML, "PyYAML needed to read a profile written as YAML")
    def test_yaml_and_json_profiles_load_the_same_way(self):
        loaded = compose.load_conformance(NARROWING)
        self.assertEqual(loaded["non_repeatable"], ["style"])
        with tempfile.TemporaryDirectory() as tmp:
            as_json = Path(tmp) / "profile.json"
            as_json.write_text(json.dumps(loaded), encoding="utf-8")
            self.assertEqual(compose.load_conformance(as_json), loaded)

    def test_a_profile_that_is_not_a_mapping_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profile.json"
            path.write_text('["style"]', encoding="utf-8")
            with self.assertRaises(ValueError):
                compose.load_conformance(path)

    def test_a_profile_whose_narrowing_cannot_be_read_is_refused_by_name(self):
        # Reading the file is where the file's name is known, so the check belongs here
        # as well as in compose(), rather than resolving a set under a profile whose
        # declarations were dropped.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profile.json"
            path.write_text('{"non_repeatable": 5}', encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                compose.load_conformance(path)
            self.assertIn("non_repeatable", str(caught.exception))
            self.assertIn(str(path), str(caught.exception))


class ComposeCliTests(unittest.TestCase):
    def test_model_level_output_matches_the_expected_fixture_byte_for_byte(self):
        result = run("--compose", *[f"spec/fixtures/composition/{name}" for name in ORDER])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, (DIR / "expected-model.json").read_text(encoding="utf-8"))

    @unittest.skipUnless(HAVE_YAML, "PyYAML needed to read a profile written as YAML")
    def test_output_under_the_conformance_profile_matches_the_expected_fixture(self):
        result = run("--compose", "--conformance-profile", str(NARROWING.relative_to(REPO)),
                     *[f"spec/fixtures/composition/{name}" for name in ORDER])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout,
                         (DIR / "expected-style-non-repeatable.json").read_text(encoding="utf-8"))

    def test_declared_composition_references_are_reported_not_silently_ignored(self):
        # Rule 7: this mode resolves no references, so the references the Frames
        # declare are named on stderr. stdout stays the resolved Frame alone.
        result = run("--compose", *[f"spec/fixtures/composition/{name}" for name in ORDER])
        self.assertIn("composition-unresolved", result.stderr)
        self.assertIn("acme/company-core", result.stderr)
        self.assertNotIn("composition-unresolved", result.stdout)

    def test_a_path_that_does_not_exist_fails_instead_of_composing_the_rest(self):
        result = run("--compose", "spec/fixtures/composition/company-core.frame.json",
                     "spec/fixtures/composition/does-not-exist.frame.json")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("does-not-exist.frame.json", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_a_file_that_is_not_a_frame_fails_rather_than_being_skipped(self):
        result = run("--compose", "README.md")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("not a Frame", result.stderr)

    def test_a_path_that_is_not_there_is_reported_as_missing_not_as_no_frame(self):
        # An unknown suffix reaches the message directly, so the message must not tell
        # a user their nonexistent file is not a Frame.
        result = run("--compose", "spec/fixtures/composition/does-not-exist.txt")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("path-not-found", result.stderr)
        self.assertNotIn("not a Frame", result.stderr)

    def test_compose_without_paths_reports_the_usage_error_instead_of_crashing(self):
        result = run("--compose")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("--compose", result.stderr)

    def test_a_conformance_profile_without_compose_is_a_usage_error_in_every_mode(self):
        # --self-check takes no paths and returned 0 with the flag silently ignored
        # until the guard moved above it.
        profile = str(NARROWING.relative_to(REPO))
        frame = "spec/fixtures/composition/q4-playbook.frame.json"
        cases = [["--self-check", "--conformance-profile", profile],
                 ["--round-trip", "--conformance-profile", profile, frame],
                 ["--conformance-profile", profile, frame]]
        for args in cases:
            with self.subTest(args=args):
                result = run(*args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("--conformance-profile applies to --compose", result.stderr)

    def test_a_conformance_profile_that_is_not_there_is_a_finding_not_a_traceback(self):
        result = run("--compose", "--conformance-profile", "spec/profiles/not-yet-written.yaml",
                     *[f"spec/fixtures/composition/{name}" for name in ORDER])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("conformance-profile-unreadable", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_a_yaml_profile_without_pyyaml_is_a_finding_not_a_traceback(self):
        # The sentinel trick tools/test_validate_frame_cli.py uses: a None in sys.modules
        # makes "import yaml" raise ImportError as though PyYAML were not installed. It
        # has to run in-process, since the sentinel lives only in this process.
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(sys.modules, {"yaml": None}):
            code = validate_frame.compose_paths([str(DIR / name) for name in ORDER], "auto",
                                                Profile.load(), conformance_path=str(NARROWING),
                                                out=out, err=err)
        self.assertEqual(code, 1)
        self.assertIn("pyyaml-required", err.getvalue())
        self.assertEqual(out.getvalue(), "")

    def test_a_conformance_profile_with_a_bad_narrowing_is_a_finding_not_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profile.json"
            path.write_text('{"non_repeatable": 5}', encoding="utf-8")
            result = run("--compose", "--conformance-profile", str(path),
                         *[f"spec/fixtures/composition/{name}" for name in ORDER])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("conformance-profile-unreadable", result.stderr)
        self.assertIn("non_repeatable", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
