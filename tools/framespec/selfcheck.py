"""Check that spec/profile/frame-core.csv and spec/frame-spec.md describe the same elements.

The element set exists twice: as normative prose in the draft, where each element
carries a Label, an Obligation, a Repeatable flag and a Maps-to crosswalk, and as
the DCTAP profile the validator reads instead of hard-coding the elements. A
disagreement between the two is worse than either alone, since implementers would
build to different element sets while both believing they conformed. This module
is the only one here whose subject is the specification rather than a Frame.
"""

import re
from itertools import zip_longest
from pathlib import Path

from .findings import Finding
from .profile import DEFAULT_PROFILE_PATH, REPO_ROOT, Profile

DEFAULT_SPEC_PATH = REPO_ROOT / "spec" / "frame-spec.md"

SECTION_RE = re.compile(r"^#{3,4} \d+(?:\.\d+)*\. (\S+)\s*$", re.M)
BULLET_RE = re.compile(r"^- \*\*(Label|Obligation|Repeatable|Maps to):\*\* (.*)$", re.M)
REFINEMENT_RE = re.compile(r"^- \*\*([A-Za-z]+)\*\* \(([^)]+)\): (.*)$", re.M)

# An obligation may be qualified: "MUST be present; MAY be empty" (guidance) and
# "MAY; MUST be present when ... requires it" (derivedFrom). The obligation is the
# first requirement keyword, not the first whitespace-separated word, which would
# keep the semicolon and make "MUST;" compare unequal to "MUST".
KEYWORD_RE = re.compile(r"\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY)\b")

# A crosswalk term as the draft writes it: `dcterms:identifier`, in backticks.
TERM_RE = re.compile(r"`([^`]+)`")

# The sentence in which an element's Comment bullet registers its values: "the
# initial values are `draft`, `review`, `approved`, `deprecated`, and `revoked`."
# Bounded at the end of that sentence, because it is the sentence that registers
# them and the rest of the same bullet backticks terms that are not registered
# values: section 4.3.5 goes on to name `stable` as a value that predates the
# registry, which reading the whole section would take for a sixth status.
INITIAL_VALUES_RE = re.compile(r"the initial values are (.*?)\.(?:\s|$)")

# The draft writes elements in two shapes and each is read by its own pattern
# above. A pattern that quietly stopped matching would make every comparison in
# self_check() trivially true: nothing read, nothing compared, a clean report. So
# each shape declares how many elements the draft is known to define, and reading
# fewer is an error rather than a pass. These are floors: adding an element to the
# draft never trips them, and removing one is deliberate and updates them here.
#
# A third shape lived here once: representation-level elements, read out of section
# 4.6's three bullets. The draft dropped mediaType, checksum and byteSize outright,
# and with them the Representation entity's last elements, so the pattern that read
# that shape now matches nothing, in any draft this specification could publish. A
# floor of zero would have kept the shape's name and its place in every dict below
# while protecting nothing, since a pattern that can never match again can never
# fall short of zero either. Removed instead, along with the loop in
# read_spec_elements() that populated it.
SECTION = "section"                     # 4.2 required, 4.3 descriptive, 4.5 relations
REFINEMENT = "refinement"               # 4.4 content refinements
EXPECTED_SHAPES = {SECTION: 17, REFINEMENT: 10}

# The same discipline for the two registered value vocabularies, which the draft
# states in prose (sections 4.3.5 and 4.3.8) and the CSV records as a picklist.
# Comparing two vocabularies that were both read as empty is the same clean report
# for nothing checked, so a shape that reads fewer values than the draft is known
# to register is an error rather than a pass. A floor, like the counts above.
EXPECTED_PICKLISTS = {"status": 5, "visibility": 4}

# Appendix B republishes the profile inside the draft and states that the
# companion frame-core.csv "is identical to the block below", so the element set
# exists a third time. The heading is what anchors the search: the phrase
# "Appendix B" also appears in the table of contents and in section 5.3, which
# cites RFC 5234's own Appendix B, and the first fenced block after either of
# those is some other example entirely.
APPENDIX_HEADING = "## Appendix B. Machine-Readable Profile"
TOP_HEADING_RE = re.compile(r"^## ", re.M)
FENCE_RE = re.compile(r"^```[^\n]*\n(.*?)^```", re.M | re.S)


def _obligation(value):
    """The requirement keyword an Obligation bullet states, or the raw text if it states none."""
    match = KEYWORD_RE.search(value)
    return match.group(1) if match else value.strip()


def _registered_values(body):
    """The values one element's prose registers, in the order the draft writes them."""
    match = INITIAL_VALUES_RE.search(body)
    return tuple(TERM_RE.findall(match.group(1))) if match else ()


def _vocabulary(values):
    """A vocabulary as a message fragment, so an empty one reads as words and not as '()'."""
    return ", ".join(values) if values else "no values"


def read_appendix_profile(text):
    """The fenced block under Appendix B, or None when the heading or the block is absent.

    The search is bounded by the next top-level heading, so a missing block is
    reported as missing rather than quietly answered with Appendix C's template.
    """
    start = text.find(APPENDIX_HEADING)
    if start < 0:
        return None
    body = start + len(APPENDIX_HEADING)
    next_heading = TOP_HEADING_RE.search(text, body)
    end = next_heading.start() if next_heading else len(text)
    match = FENCE_RE.search(text, body, end)
    return match.group(1) if match else None


def _clip(line, width=60):
    """One line of either copy, short enough to sit inside a finding's message."""
    if line is None:
        return "(no such line)"
    return repr(line if len(line) <= width else line[:width] + "...")


def _appendix_findings(text, profile_path, where):
    """Compare the draft's own copy of the profile against the CSV it claims to be identical to."""
    block = read_appendix_profile(text)
    if block is None:
        return [Finding("error", "appendix-not-found",
                        f"no fenced block under '{APPENDIX_HEADING}' in the draft, so the copy of the "
                        "profile it publishes went unchecked", where)]
    with open(profile_path, encoding="utf-8") as handle:
        csv_text = handle.read()
    # Trailing whitespace off each side: a stray final newline in either file is
    # not a disagreement about the element set.
    appendix_lines, csv_lines = block.rstrip().split("\n"), csv_text.rstrip().split("\n")
    if appendix_lines == csv_lines:
        return []
    # Equal lists returned above, so the two differ at some line and next() always finds it.
    pairs = list(zip_longest(appendix_lines, csv_lines))
    line = next(number for number, (a, b) in enumerate(pairs, start=1) if a != b)
    left, right = pairs[line - 1]
    return [Finding("error", "appendix-mismatch",
                    f"the fenced block under '{APPENDIX_HEADING}' and {profile_path} are not identical, "
                    f"though the draft says they are: {len(appendix_lines)} lines in the appendix and "
                    f"{len(csv_lines)} in the CSV, first differing at line {line}, "
                    f"appendix {_clip(left)} against CSV {_clip(right)}", where)]


def read_spec_elements(text):
    """Element facts as written in the draft: sections 4.2, 4.3, 4.5 (per-element) and 4.4 (bullets)."""
    found = {}
    positions = [(m.start(), m.group(1)) for m in SECTION_RE.finditer(text)]
    for index, (start, name) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(text)
        body = text[start:end]
        facts = dict(BULLET_RE.findall(body))
        if "Obligation" not in facts:
            # A numbered heading whose title is one word, such as 4.5 Relations or
            # 5.1 Rules, is not an element definition. An Obligation bullet is what
            # distinguishes one, and the draft carries such a bullet nowhere else.
            continue
        found[name] = {
            "label": facts.get("Label", ""),
            "obligation": _obligation(facts["Obligation"]),
            "repeatable": facts.get("Repeatable", "").lower().startswith("yes"),
            "maps_to": facts.get("Maps to", ""),
            "native": "Frame-native" in facts.get("Maps to", ""),
            "values": _registered_values(body),
            "source": SECTION,
        }
    # Section 4.4 states the ten refinements' shared obligation and repeatability
    # once, in prose, and gives each a name, a label and a definition. It also
    # defines each as a subproperty of `guidance`, which Appendix A counts among
    # "the Frame-native terms (`guidance`, the ten refinements, and `composition`)".
    # So a refinement's Frame-native rationale is guidance's rationale, and it is
    # read from section 4.2.2 rather than assumed here: hard-coding it would leave
    # native-without-rationale unable to fire for ten of the twenty-seven elements.
    guidance_is_native = found.get("guidance", {}).get("native", False)
    for name, label, _definition in REFINEMENT_RE.findall(text):
        found[name] = {"label": label, "obligation": "MAY", "repeatable": True, "maps_to": "",
                       "native": guidance_is_native, "values": (), "source": REFINEMENT}
    return found


def self_check(spec_path=DEFAULT_SPEC_PATH, profile_path=DEFAULT_PROFILE_PATH):
    """Findings for every disagreement between the draft's prose and the profile CSV."""
    with open(spec_path, encoding="utf-8") as handle:
        text = handle.read()
    spec = read_spec_elements(text)
    profile = Profile.load(profile_path)
    findings = []
    # A file URI, the one location shape validate_frame.py reports: this module used
    # to report an absolute path here while validation reported a URI for the same
    # kind of subject.
    where = Path(spec_path).resolve().as_uri()
    read_by_shape = {shape: 0 for shape in EXPECTED_SHAPES}
    for facts in spec.values():
        read_by_shape[facts["source"]] += 1
    for shape, expected in EXPECTED_SHAPES.items():
        if read_by_shape[shape] < expected:
            findings.append(Finding("error", "spec-extraction-too-small",
                                    f"{shape} elements read from the draft: {read_by_shape[shape]}, expected at least "
                                    f"{expected}; either the pattern that reads them no longer matches or the draft "
                                    "dropped elements, so the comparisons that follow have verified less than they appear to",
                                    where))
    for name, expected in EXPECTED_PICKLISTS.items():
        read = len(spec.get(name, {}).get("values", ()))
        if read < expected:
            findings.append(Finding("error", "spec-extraction-too-small",
                                    f"registered values read from the draft for '{name}': {read}, expected at "
                                    f"least {expected}; either the pattern that reads them no longer matches or "
                                    "the draft stopped registering them, so the picklist comparison below has "
                                    "verified less than it appears to", where))
    findings.extend(_appendix_findings(text, profile_path, where))
    for name in profile.order:
        if name not in spec:
            findings.append(Finding("error", "spec-missing-element",
                                    f"CSV element '{name}' has no section or bullet in the draft", where))
    for name in spec:
        if name not in profile.elements:
            findings.append(Finding("error", "csv-missing-element", f"draft element '{name}' is not in frame-core.csv", where))
    compared = [name for name in profile.order if name in spec]
    for name in compared:
        element, facts = profile.elements[name], spec[name]
        if element.mandatory != (facts["obligation"] == "MUST"):
            findings.append(Finding("error", "obligation-mismatch",
                                    f"'{name}': CSV mandatory={element.mandatory} but draft says "
                                    f"{facts['obligation']}", where))
        if element.repeatable != facts["repeatable"]:
            findings.append(Finding("error", "repeatable-mismatch",
                                    f"'{name}': CSV repeatable={element.repeatable} but draft says "
                                    f"{facts['repeatable']}", where))
        # Checked unconditionally: every shape read_spec_elements() produces now
        # carries a label, a section from its Label bullet and a refinement from
        # its parenthetical. That was not always true; section 4.6's Representation
        # bullets had no Label and were exempted here by shape. The exemption went
        # with the shape when the draft dropped it, rather than staying in place to
        # guard against a case that can no longer occur.
        if element.label != facts["label"]:
            findings.append(Finding("error", "label-mismatch",
                                    f"'{name}': CSV label {element.label!r} but draft says {facts['label']!r}", where))
        if not element.maps_to and not facts["native"]:
            findings.append(Finding("error", "native-without-rationale",
                                    f"'{name}' has no crosswalk term and the draft does not call it Frame-native", where))
        # The registered values, which the draft states in prose and the CSV records as
        # a picklist. These two vocabularies are the only ones in the model that drive
        # user-visible output: framespec.check warns 'unregistered-value' against the
        # CSV's picklist, so a value the draft registers and the CSV lacks becomes a
        # warning on a Frame that conforms to the normative text. Compared as sets
        # rather than in order, because what each copy registers is which values are in
        # the vocabulary and neither states that their order is part of it.
        if set(element.picklist) != set(facts["values"]):
            findings.append(Finding("error", "picklist-mismatch",
                                    f"'{name}': the CSV registers {_vocabulary(element.picklist)} but the draft "
                                    f"registers {_vocabulary(facts['values'])}", where))
        # Membership, not equality: a Maps-to line states the term the CSV records
        # and often a secondary term, a reference link and a note on the fit. The
        # comparison is against whole backticked terms rather than the line's text,
        # so a truncated term is caught instead of matching as a substring.
        prose_terms = TERM_RE.findall(facts["maps_to"])
        if element.maps_to and element.maps_to not in prose_terms:
            findings.append(Finding("error", "maps-to-mismatch",
                                    f"'{name}': CSV maps to {element.maps_to!r}, which is not among the terms "
                                    f"the draft's Maps-to states ({', '.join(prose_terms) or 'none'})", where))
    if not findings:
        findings.append(Finding("info", "self-check-ok", f"{len(compared)} elements agree between CSV and draft", where))
    return findings
