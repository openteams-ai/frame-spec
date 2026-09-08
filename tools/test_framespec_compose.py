import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent

sys.path.insert(0, str(TOOLS))

from framespec import compose, io as frame_io  # noqa: E402 - needs the sys.path insert above
from framespec.compose import ALL_REPEATABLE   # noqa: E402 - same reason
from framespec.model import Frame              # noqa: E402 - same reason
from framespec.profile import Profile          # noqa: E402 - same reason

try:
    import yaml                                # noqa: F401 - presence is the point
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

DIR = REPO / "spec" / "fixtures" / "composition"
ORDER = ["company-core.frame.json", "brand-voice.frame.json", "q4-playbook.frame.json"]
NARROWING = DIR / "style-non-repeatable.conformance.yaml"
SPEC = REPO / "spec" / "frame-spec.md"

# Rule 5 enumerates the elements that MUST NOT be inherited. The list is read out of
# the draft rather than copied here, so that the two cannot drift apart unnoticed.
RULE5_RE = re.compile(r"The elements that describe the Frame itself \(([^)]*)\) MUST NOT be inherited")


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
    """The fourteen element names rule 5 says MUST NOT be inherited, from the draft."""
    match = RULE5_RE.search(SPEC.read_text(encoding="utf-8"))
    if match is None:
        raise AssertionError("rule 5's enumeration was not found in spec/frame-spec.md")
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
    def test_none_of_the_fourteen_elements_rule_5_enumerates_composes(self):
        p = Profile.load()
        composing = compose.composing_elements(p)
        named = rule5_elements()
        self.assertEqual(len(named), 14, named)
        for name in named:
            self.assertIn(name, p.elements, f"rule 5 names {name!r}, which the profile does not define")
            self.assertNotIn(name, composing, f"rule 5 says {name!r} MUST NOT be inherited")

    def test_what_does_not_compose_is_the_fourteen_plus_composition_and_the_representation_level(self):
        # The complement is wider than rule 5's list, and deliberately: composition is
        # neither content nor guards, and the section 4.6 elements describe the document
        # rather than its content. Neither may be inherited either.
        p = Profile.load()
        not_composing = set(p.order) - set(compose.composing_elements(p))
        self.assertEqual(not_composing,
                         set(rule5_elements()) | {"composition", "mediaType", "checksum", "byteSize"})

    def test_guidance_its_refinements_and_guards_are_what_composes(self):
        p = Profile.load()
        self.assertEqual(list(compose.composing_elements(p)), p.content_elements() + ["guards"])
        self.assertEqual(len(compose.composing_elements(p)), 12)   # guidance, ten refinements, guards

    def test_composition_and_representation_elements_stay_with_the_declaring_frame(self):
        p, frames = load_frames()
        result = compose.compose(frames, p).elements
        # brand-voice composes acme/company-core; only q4-playbook's own value survives.
        self.assertEqual(result["composition"], ["acme/brand-voice"])
        for name in ("mediaType", "checksum", "byteSize"):
            self.assertNotIn(name, compose.composing_elements(p))

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

    def test_dedup_keeps_the_highest_precedence_position(self):
        # Rule 6 permits deduplication but does not say where a deduplicated value
        # sits. This pins the choice: the highest-precedence occurrence.
        p = Profile.load()
        a = Frame({"identifier": "a", "guidance": [""], "rules": ["x", "y"]}, "json")
        b = Frame({"identifier": "b", "guidance": [""], "rules": ["y", "x"]}, "json")
        result = compose.compose([a, b], p, {"rule6_narrowings": {"dedup": ["rules"]}})
        self.assertEqual(result.elements["rules"], ["y", "x"])

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


class LoadConformanceTests(unittest.TestCase):
    @unittest.skipUnless(HAVE_YAML, "PyYAML needed to read a profile written as YAML")
    def test_yaml_and_json_profiles_load_the_same_way(self):
        loaded = compose.load_conformance(NARROWING)
        self.assertEqual(loaded["non_repeatable"], ["style"])
        as_json = REPO / "tools" / "_compose_conformance.json"
        as_json.write_text(json.dumps(loaded), encoding="utf-8")
        try:
            self.assertEqual(compose.load_conformance(as_json), loaded)
        finally:
            as_json.unlink()

    def test_a_profile_that_is_not_a_mapping_is_refused(self):
        path = REPO / "tools" / "_compose_conformance_bad.json"
        path.write_text('["style"]', encoding="utf-8")
        try:
            with self.assertRaises(ValueError):
                compose.load_conformance(path)
        finally:
            path.unlink()


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

    def test_compose_without_paths_reports_the_usage_error_instead_of_crashing(self):
        result = run("--compose")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("--compose", result.stderr)


if __name__ == "__main__":
    unittest.main()
