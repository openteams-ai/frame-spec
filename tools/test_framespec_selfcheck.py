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
    def test_reads_element_sections_and_refinement_bullets(self):
        found = selfcheck.read_spec_elements(SNIPPET)
        self.assertEqual(found["identifier"]["obligation"], "MUST")
        self.assertFalse(found["identifier"]["repeatable"])
        self.assertFalse(found["identifier"]["native"])
        self.assertTrue(found["guidance"]["repeatable"])
        self.assertTrue(found["guidance"]["native"])
        self.assertEqual(found["rules"]["label"], "Rules")
        self.assertEqual(found["toolSpecs"]["label"], "Tool Specifications")
        self.assertTrue(found["toolSpecs"]["repeatable"])

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
        # would make native-without-rationale unable to fire for ten of the twenty-seven.
        self.assertTrue(selfcheck.read_spec_elements(SNIPPET)["rules"]["native"])
        text = SNIPPET.replace("- **Maps to:** Frame-native. The nearest terms describe a resource.",
                               "- **Maps to:** `schema:text` [[SCHEMA-ORG]](#ref-SCHEMA-ORG)")
        self.assertFalse(selfcheck.read_spec_elements(text)["rules"]["native"])

    def test_the_registered_values_are_read_from_the_sentence_that_registers_them(self):
        # Sections 4.3.5 and 4.3.8 register their values in one sentence of the Comment
        # bullet. The rest of that bullet backticks terms that are not registered
        # values: 4.3.5 names `stable` as a v0.2 value that predates the registry, so
        # reading every backticked term in the section would report a sixth status.
        found = selfcheck.read_spec_elements(selfcheck.DEFAULT_SPEC_PATH.read_text(encoding="utf-8"))
        self.assertEqual(found["status"]["values"],
                         ("draft", "review", "approved", "deprecated", "revoked"))
        self.assertEqual(found["visibility"]["values"], ("private", "internal", "shared", "public"))
        self.assertNotIn("stable", found["status"]["values"])
        self.assertEqual(found["title"]["values"], ())

    def test_the_real_draft_yields_seventeen_sections_and_ten_refinements(self):
        # The two shapes are read by two patterns. Counting them separately is
        # what makes a pattern that stops matching visible instead of quiet.
        found = selfcheck.read_spec_elements(selfcheck.DEFAULT_SPEC_PATH.read_text(encoding="utf-8"))
        counted = {}
        for facts in found.values():
            counted[facts["source"]] = counted.get(facts["source"], 0) + 1
        self.assertEqual(counted, {selfcheck.SECTION: 17, selfcheck.REFINEMENT: 10})
        self.assertEqual(len(found), 27)


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
            "previousVersion,Previous Version,false,false,literal,xsd:string,,,dcat:previousVersion,,\n", ""))

    def test_an_element_with_no_crosswalk_term_and_no_native_rationale_is_reported(self):
        # Journey 2: no element is invented without justification. The draft's
        # Maps-to for `title` names dcterms:title, so a CSV row that dropped the
        # term leaves the element with neither a crosswalk nor a stated rationale.
        self.assertIn("native-without-rationale", self.codes(
            "title,Title,false,false,literal,xsd:string,,,dcterms:title,,",
            "title,Title,false,false,literal,xsd:string,,,,,"))

    def test_the_appendix_copy_of_the_profile_is_the_csv_it_claims_to_be(self):
        # Appendix B republishes the profile and says the companion file "is
        # identical to the block below". Two hand-maintained copies of the
        # normative element set is the drift this module exists to catch.
        text = selfcheck.DEFAULT_SPEC_PATH.read_text(encoding="utf-8")
        block = selfcheck.read_appendix_profile(text)
        self.assertIsNotNone(block)
        # Anchored on the heading, so this is the profile fence and not the
        # Markdown example that follows the phrase "Appendix B" in the contents
        # list, nor the one after section 5.3's citation of RFC 5234's Appendix B.
        self.assertTrue(block.startswith("propertyID,propertyLabel,mandatory,"), block[:60])
        self.assertEqual(len(block.rstrip().split("\n")), 28)      # header plus the twenty-seven elements
        self.assertEqual(block.rstrip(), DEFAULT_PROFILE_PATH.read_text(encoding="utf-8").rstrip())
        codes = [f.code for f in selfcheck.self_check()]
        self.assertNotIn("appendix-mismatch", codes)
        self.assertNotIn("appendix-not-found", codes)

    def test_an_appendix_block_that_drifted_from_the_csv_is_reported(self):
        self.assertIn("appendix-mismatch", self.edited_draft_codes(
            "previousVersion,Previous Version,false,false,literal,xsd:string,,,dcat:previousVersion,,",
            "previousVersion,Previous Version,false,true,literal,xsd:string,,,dcat:previousVersion,,"))

    def test_a_final_newline_is_not_an_appendix_disagreement(self):
        # The comparison is about the element set, not about how either file ends.
        for ending in ("\n\n\n", ""):
            with tempfile.TemporaryDirectory() as tmp:
                text = DEFAULT_PROFILE_PATH.read_text(encoding="utf-8").rstrip("\n") + ending
                findings = selfcheck.self_check(profile_path=write(tmp, "frame-core.csv", text))
            self.assertEqual([f.code for f in findings], ["self-check-ok"], [str(f) for f in findings])

    def test_an_appendix_block_that_cannot_be_found_is_an_error_not_a_pass(self):
        # Both ways it can go missing: the heading renamed, and the block gone
        # from under a heading that is still there. The second must not be
        # answered with the next appendix's fenced template.
        self.assertIn("appendix-not-found", self.edited_draft_codes(
            "## Appendix B. Machine-Readable Profile", "## Appendix B. Profile"))
        self.assertIn("appendix-not-found", self.edited_draft_codes("```csv\n", ""))

    def test_a_value_registered_in_the_draft_and_missing_from_the_csv_is_reported(self):
        # The drift this module exists to catch and did not: registering a sixth status
        # in the prose left --self-check reporting agreement, after which the checker
        # warned unregistered-value on a value the normative text registers.
        self.assertIn("picklist-mismatch", self.edited_draft_codes(
            "the initial values are `draft`, `review`, `approved`, `deprecated`, and `revoked`.",
            "the initial values are `draft`, `review`, `approved`, `deprecated`, `revoked`, and `archived`."))

    def test_a_value_in_the_csv_and_not_in_the_draft_is_reported(self):
        # The same disagreement from the other side, which would make the checker
        # accept a value the normative text does not register.
        self.assertIn("picklist-mismatch", self.codes(
            "visibility,Visibility,false,false,literal,xsd:string,private internal shared public,picklist,",
            "visibility,Visibility,false,false,literal,xsd:string,private internal shared public team,picklist,"))

    def test_a_picklist_the_draft_stopped_registering_is_an_error_not_a_pass(self):
        # Two vocabularies both read as empty agree trivially. The floor makes a
        # pattern that stopped matching an error, as it does for the three element
        # shapes; without it the comparison above would pass having compared nothing.
        codes = self.edited_draft_codes(
            "the initial values are `draft`, `review`, `approved`, `deprecated`, and `revoked`.", "")
        self.assertIn("spec-extraction-too-small", codes)
        self.assertIn("picklist-mismatch", codes)

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
        self.assertIn("27 elements agree", result.stdout)

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
