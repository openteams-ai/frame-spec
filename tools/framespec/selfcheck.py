"""Check that spec/profile/frame-core.csv and spec/frame-spec.md describe the same elements.

The element set exists twice: as normative prose in the draft, where each element
carries a Label, an Obligation, a Repeatable flag and a Maps-to crosswalk, and as
the DCTAP profile the validator reads instead of hard-coding the elements. A
disagreement between the two is worse than either alone, since implementers would
build to different element sets while both believing they conformed. This module
is the only one here whose subject is the specification rather than a Frame.
"""

import re

from .findings import Finding
from .profile import DEFAULT_PROFILE_PATH, REPO_ROOT, Profile

DEFAULT_SPEC_PATH = REPO_ROOT / "spec" / "frame-spec.md"

SECTION_RE = re.compile(r"^#{3,4} \d+(?:\.\d+)*\. (\S+)\s*$", re.M)
BULLET_RE = re.compile(r"^- \*\*(Label|Obligation|Repeatable|Maps to):\*\* (.*)$", re.M)
REFINEMENT_RE = re.compile(r"^- \*\*([A-Za-z]+)\*\* \(([^)]+)\): (.*)$", re.M)
REPRESENTATION_RE = re.compile(r"^- \*\*(mediaType|checksum|byteSize):\*\* (.*)$", re.M)

# An obligation may be qualified: "MUST be present; MAY be empty" (guidance) and
# "MAY; MUST be present when ... requires it" (derivedFrom). The obligation is the
# first requirement keyword, not the first whitespace-separated word, which would
# keep the semicolon and make "MUST;" compare unequal to "MUST".
KEYWORD_RE = re.compile(r"\b(MUST NOT|MUST|SHOULD NOT|SHOULD|MAY)\b")

# A crosswalk term as the draft writes it: `dcterms:identifier`, in backticks.
TERM_RE = re.compile(r"`([^`]+)`")

# The draft writes elements in three shapes and each is read by its own pattern
# above. A pattern that quietly stopped matching would make every comparison in
# self_check() trivially true: nothing read, nothing compared, a clean report. So
# each shape declares how many elements the draft is known to define, and reading
# fewer is an error rather than a pass. These are floors: adding an element to the
# draft never trips them, and removing one is deliberate and updates them here.
SECTION = "section"                     # 4.2 required, 4.3 descriptive, 4.5 relations
REFINEMENT = "refinement"               # 4.4 content refinements
REPRESENTATION = "representation"       # 4.6 representation-level elements
EXPECTED_SHAPES = {SECTION: 17, REFINEMENT: 10, REPRESENTATION: 3}


def _obligation(value):
    """The requirement keyword an Obligation bullet states, or the raw text if it states none."""
    match = KEYWORD_RE.search(value)
    return match.group(1) if match else value.strip()


def read_spec_elements(text):
    """Element facts as written in the draft: sections 4.2, 4.3, 4.5 (per-element), 4.4, 4.6 (bullets)."""
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
            "source": SECTION,
        }
    # Section 4.4 states the ten refinements' shared obligation and repeatability
    # once, in prose, and gives each a name, a label and a definition. It also
    # defines each as a subproperty of `guidance`, which Appendix A counts among
    # "the Frame-native terms (`guidance`, the ten refinements, and `composition`)".
    # So a refinement's Frame-native rationale is guidance's rationale, and it is
    # read from section 4.2.2 rather than assumed here: hard-coding it would leave
    # native-without-rationale unable to fire for ten of the thirty elements.
    guidance_is_native = found.get("guidance", {}).get("native", False)
    for name, label, _definition in REFINEMENT_RE.findall(text):
        found[name] = {"label": label, "obligation": "MAY", "repeatable": True, "maps_to": "",
                       "native": guidance_is_native, "source": REFINEMENT}
    # Section 4.6 gives the three Representation-level elements one bullet each,
    # with the crosswalk term inline and no label. They are optional at the model
    # layer; section 4.8 records their obligation as "per encoding".
    for name, rest in REPRESENTATION_RE.findall(text):
        found[name] = {"label": "", "obligation": "MAY", "repeatable": False, "maps_to": rest,
                       "native": False, "source": REPRESENTATION}
    return found


def self_check(spec_path=DEFAULT_SPEC_PATH, profile_path=DEFAULT_PROFILE_PATH):
    """Findings for every disagreement between the draft's prose and the profile CSV."""
    with open(spec_path, encoding="utf-8") as handle:
        text = handle.read()
    spec = read_spec_elements(text)
    profile = Profile.load(profile_path)
    findings = []
    where = str(spec_path)
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
        # By shape rather than by "the draft's label came out empty": a section
        # that lost its Label bullet has to be reported, not skipped. Only the
        # three Representation bullets of 4.6 legitimately carry no label.
        if facts["source"] != REPRESENTATION and element.label != facts["label"]:
            findings.append(Finding("error", "label-mismatch",
                                    f"'{name}': CSV label {element.label!r} but draft says {facts['label']!r}", where))
        if not element.maps_to and not facts["native"]:
            findings.append(Finding("error", "native-without-rationale",
                                    f"'{name}' has no crosswalk term and the draft does not call it Frame-native", where))
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
