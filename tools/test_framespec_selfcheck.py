import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from framespec import selfcheck
from framespec.findings import has_errors
from framespec.profile import DEFAULT_PROFILE_PATH

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent

SNIPPET = """
#### 4.2.1. identifier

- **Label:** Identifier
- **Obligation:** MUST
- **Repeatable:** No
- **Maps to:** `dcterms:identifier` [[DCTERMS]](#ref-DCTERMS)

#### 4.2.2. guidance

- **Label:** Guidance
- **Obligation:** MUST be present; MAY be empty
- **Repeatable:** Yes
- **Maps to:** Frame-native. The nearest terms describe a resource.

### 4.4. Content Refinements

- **rules** (Rules): What is and is not acceptable behavior within the scope.
- **toolSpecs** (Tool Specifications): Specifications of the tools.

### 4.6. Representation-Level Elements

- **mediaType:** The media type of the Representation. Maps to `dcat:mediaType`.
"""

# A spec and a profile that agree on exactly one element. Every comparison in
# self_check() is trivially true here, so a check with no plausibility floor
# reports "1 elements agree between CSV and draft" and exits 0: the false green
# a broken extraction pattern would produce against the real files.
HOLLOW_SPEC = """
#### 4.2.2. guidance

- **Label:** Guidance
- **Obligation:** MUST be present; MAY be empty
- **Repeatable:** Yes
- **Maps to:** Frame-native. The nearest terms describe a resource.
"""

CSV_HEADER = ("propertyID,propertyLabel,mandatory,repeatable,valueNodeType,valueDataType,"
              "valueConstraint,valueConstraintType,mapsTo,refines,note\n")
GUIDANCE_ROW = "guidance,Guidance,true,true,literal,xsd:string,,,,,Frame-native; may be empty\n"


def write(directory, name, text):
    path = Path(directory) / name
    path.write_text(text, encoding="utf-8")
    return path


def csv_with(directory, old_row, new_row):
    """The real profile with one row rewritten, so a mismatch has a real counterpart."""
    text = DEFAULT_PROFILE_PATH.read_text(encoding="utf-8")
    if old_row not in text:
        raise AssertionError(f"row not found in {DEFAULT_PROFILE_PATH}: {old_row!r}")
    return write(directory, "frame-core.csv", text.replace(old_row, new_row))


def run_cli(*args):
    return subprocess.run([sys.executable, str(TOOLS / "validate_frame.py"), *args],
                          capture_output=True, text=True, cwd=REPO)


class ReadSpecTests(unittest.TestCase):
    def test_reads_element_sections_refinements_and_representation_bullets(self):
        found = selfcheck.read_spec_elements(SNIPPET)
        self.assertEqual(found["identifier"]["obligation"], "MUST")
        self.assertFalse(found["identifier"]["repeatable"])
        self.assertFalse(found["identifier"]["native"])
        self.assertTrue(found["guidance"]["repeatable"])
        self.assertTrue(found["guidance"]["native"])
        self.assertEqual(found["rules"]["label"], "Rules")
        self.assertEqual(found["toolSpecs"]["label"], "Tool Specifications")
        self.assertTrue(found["toolSpecs"]["repeatable"])
        self.assertEqual(found["mediaType"]["obligation"], "MAY")

    def test_obligation_is_the_first_requirement_keyword_not_the_first_word(self):
        # The draft qualifies two obligations with a semicolon. Splitting on
        # whitespace keeps the punctuation, so "MUST; ..." reads as "MUST;",
        # which is not equal to "MUST" and would silently agree with a CSV row
        # marked mandatory=false: a real disagreement reported as a clean pass.
        text = SNIPPET.replace("- **Obligation:** MUST\n",
                               "- **Obligation:** MUST; see [Section 3.2](#identity)\n")
        self.assertEqual(selfcheck.read_spec_elements(text)["identifier"]["obligation"], "MUST")
        text = SNIPPET.replace("- **Obligation:** MUST\n",
                               "- **Obligation:** MAY; MUST be present when [Section 3.2](#identity) requires it\n")
        self.assertEqual(selfcheck.read_spec_elements(text)["identifier"]["obligation"], "MAY")

    def test_a_refinement_is_frame_native_only_because_guidance_is(self):
        # Section 4.4 defines each refinement as a subproperty of `guidance`, and
        # Appendix A names "the Frame-native terms (`guidance`, the ten refinements,
        # and `composition`)". So a refinement's rationale is guidance's rationale,
        # and it has to be read from the draft rather than assumed: hard-coding it
        # would make native-without-rationale unable to fire for ten of the thirty.
        self.assertTrue(selfcheck.read_spec_elements(SNIPPET)["rules"]["native"])
        text = SNIPPET.replace("- **Maps to:** Frame-native. The nearest terms describe a resource.",
                               "- **Maps to:** `schema:text` [[SCHEMA-ORG]](#ref-SCHEMA-ORG)")
        self.assertFalse(selfcheck.read_spec_elements(text)["rules"]["native"])

    def test_the_real_draft_yields_seventeen_sections_ten_refinements_and_three_bullets(self):
        # The three shapes are read by three patterns. Counting them separately is
        # what makes a pattern that stops matching visible instead of quiet.
        found = selfcheck.read_spec_elements(selfcheck.DEFAULT_SPEC_PATH.read_text(encoding="utf-8"))
        counted = {}
        for facts in found.values():
            counted[facts["source"]] = counted.get(facts["source"], 0) + 1
        self.assertEqual(counted, {selfcheck.SECTION: 17, selfcheck.REFINEMENT: 10, selfcheck.REPRESENTATION: 3})
        self.assertEqual(len(found), 30)


class SelfCheckTests(unittest.TestCase):
    def codes(self, old_row, new_row):
        """Finding codes from checking the real draft against the profile with one row rewritten."""
        with tempfile.TemporaryDirectory() as tmp:
            findings = selfcheck.self_check(profile_path=csv_with(tmp, old_row, new_row))
        return [f.code for f in findings]

    def edited_draft_codes(self, old, new):
        """Finding codes from checking the real profile against the draft with one edit."""
        text = selfcheck.DEFAULT_SPEC_PATH.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"text not found in {selfcheck.DEFAULT_SPEC_PATH}: {old!r}")
        with tempfile.TemporaryDirectory() as tmp:
            findings = selfcheck.self_check(spec_path=write(tmp, "frame-spec.md", text.replace(old, new, 1)))
        return [f.code for f in findings]

    def test_the_real_spec_and_csv_agree(self):
        findings = selfcheck.self_check()
        self.assertFalse(has_errors(findings), [str(f) for f in findings if f.level == "error"])

    def test_a_near_empty_extraction_is_reported_rather_than_passing(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = write(tmp, "frame-spec.md", HOLLOW_SPEC)
            profile = write(tmp, "frame-core.csv", CSV_HEADER + GUIDANCE_ROW)
            findings = selfcheck.self_check(spec_path=spec, profile_path=profile)
        self.assertTrue(has_errors(findings), [str(f) for f in findings])
        self.assertIn("spec-extraction-too-small", [f.code for f in findings])
        self.assertNotIn("self-check-ok", [f.code for f in findings])

    def test_an_obligation_disagreement_is_reported(self):
        self.assertIn("obligation-mismatch", self.codes(
            "identifier,Identifier,true,false,literal,xsd:string,,,dcterms:identifier,,",
            "identifier,Identifier,false,false,literal,xsd:string,,,dcterms:identifier,,"))

    def test_a_repeatability_disagreement_is_reported(self):
        self.assertIn("repeatable-mismatch", self.codes(
            "guards,Guards,false,true,literal,xsd:string,frame-ref,pattern,dcterms:requires,,",
            "guards,Guards,false,false,literal,xsd:string,frame-ref,pattern,dcterms:requires,,"))

    def test_a_label_disagreement_is_reported(self):
        self.assertIn("label-mismatch", self.codes(
            "toolSpecs,Tool Specifications,false,true,", "toolSpecs,Tool Specs,false,true,"))

    def test_a_section_that_lost_its_label_bullet_is_reported_not_skipped(self):
        # Comparing labels only when the draft's label came out non-empty would
        # turn a Label bullet the extraction stopped reading into a silent pass.
        self.assertIn("label-mismatch", self.edited_draft_codes("- **Label:** Identifier\n", ""))

    def test_an_element_the_csv_dropped_is_reported(self):
        self.assertIn("csv-missing-element", self.codes(
            "checksum,Checksum,false,false,literal,xsd:string,,,spdx:checksum,,Representation level\n", ""))

    def test_an_element_with_no_crosswalk_term_and_no_native_rationale_is_reported(self):
        # Journey 2: no element is invented without justification. The draft's
        # Maps-to for `title` names dcterms:title, so a CSV row that dropped the
        # term leaves the element with neither a crosswalk nor a stated rationale.
        self.assertIn("native-without-rationale", self.codes(
            "title,Title,false,false,literal,xsd:string,,,dcterms:title,,",
            "title,Title,false,false,literal,xsd:string,,,,,"))

    def test_a_crosswalk_term_the_draft_does_not_state_is_reported(self):
        self.assertIn("maps-to-mismatch", self.codes(
            "identifier,Identifier,true,false,literal,xsd:string,,,dcterms:identifier,,",
            "identifier,Identifier,true,false,literal,xsd:string,,,dcterms:creator,,"))

    def test_a_truncated_crosswalk_term_is_reported_rather_than_matching_as_a_substring(self):
        # "dcterms:ident" appears inside the draft's `dcterms:identifier`, so a
        # comparison against the Maps-to line's text rather than against whole
        # backticked terms would call a truncated term agreement.
        self.assertIn("maps-to-mismatch", self.codes(
            "identifier,Identifier,true,false,literal,xsd:string,,,dcterms:identifier,,",
            "identifier,Identifier,true,false,literal,xsd:string,,,dcterms:ident,,"))


class CliTests(unittest.TestCase):
    def test_self_check_takes_no_paths_and_exits_zero(self):
        # The branch has to come before the no-paths guard, which prints help
        # and returns 2; this mode checks the specification, not a Frame.
        result = run_cli("--self-check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("self-check-ok", result.stdout)
        self.assertIn("30 elements agree", result.stdout)

    def test_self_check_refuses_paths_rather_than_ignoring_them(self):
        # Accepting and dropping a path would leave a file the user asked about
        # unchecked while the exit code reported success.
        result = run_cli("--self-check", "examples/minimal/frame.md")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("takes no paths", result.stderr)

    def test_self_check_exits_one_when_the_profile_disagrees_with_the_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            profile = csv_with(tmp, "guards,Guards,false,true,", "guards,Guards,true,true,")
            result = run_cli("--self-check", "--profile", str(profile))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("obligation-mismatch", result.stdout)


if __name__ == "__main__":
    unittest.main()
