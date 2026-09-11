"""Check the draft against invariants that two review rounds found it breaking.

The element set has had a checker since `selfcheck`; the prose has not. Eleven
blocking defects were found across two reviews of `spec/frame-spec.md`, and nine
of the eleven fell into four classes that a script can decide. Each class below
is one of those, named with the finding that motivated it, so a rule this module
enforces is a rule a reviewer no longer has to rediscover.
"""

import re
from difflib import SequenceMatcher
from pathlib import Path

from .findings import Finding
from .profile import REPO_ROOT

DEFAULT_SPEC_PATH = REPO_ROOT / "spec" / "frame-spec.md"

KEYWORD_RE = re.compile(r"\b(MUST NOT|MUST|SHOULD NOT|SHOULD|REQUIRED|RECOMMENDED)\b")

# Section 2.1: the key words bind implementations, the documents they produce and
# consume, and the registration procedures of section 10. They do not bind a person.
# So the check is on the subject side and it is a denylist: a role this document
# never defines, or a human. Requiring an approved subject instead cannot work, since
# a relative clause carries actor words ("Consumers that need to know whether a
# Frame ... MUST") and many legitimate requirements have an artifact as their subject.
UNDEFINED_PARTIES = re.compile(
    r"\b(consumers?|users?|authors?|clients?|producers?|maintainers?|publishers?|"
    r"persons?|people|humans?|developers?|organizations?|companies|teams?|"
    r"anyone|everyone|somebody|whoever)\b", re.I)

# A sentence may carry its subject as a pronoun, its antecedent being the sentence
# before: "A reader that does not implement a refinement MUST treat ... It MUST NOT
# discard the value." Legitimate prose, so the check looks back one sentence when the
# subject is a pronoun rather than reporting the pronoun as an undefined party.
PRONOUN_SUBJECT = re.compile(r"^(It|Its|They|Their|Such|This|That|These|Those|Both|Neither|Each)\b")

# A value-shape rule states what a value must look like. Section 4.3.10's date format
# was the only one that never said what a reader does with a value that breaks it,
# which made it a third rejection path in a specification that promises two.
DISPOSITION = re.compile(r"MUST NOT reject|MUST NOT fail|MUST preserve|MUST report|"
                         r"(?:MUST|SHOULD|MAY) warn|is (?:an|in) error", re.I)
VALUE_RULE = re.compile(r"The value MUST\b|value MUST be\b|Documents MUST\b|"
                        r"is REQUIRED\b|MUST begin with\b|MUST be a\b|MUST be one of\b")

# Section 3.3's promise. A reader rejects a document for these two reasons only, so
# any other sentence that says a reader rejects, refuses or fails on a document is
# either a third path or needs rewording.
# The negative lookahead matters: "MUST NOT reject" is a prohibition on rejecting,
# the opposite of the thing this check looks for, and the draft states it eight times.
REJECTION_RE = re.compile(
    r"MUST(?! NOT)(?: \w+){0,2} (?:reject|refuse|fail|decline|abort|discard|stop)", re.I)

# Where a rejection may be stated. Section 3.3 defines when a document is in error;
# section 5.1's rules 7 and 8 and section 9.7's limits define when a resolution fails,
# which section 3.3 distinguishes from rejecting a document. Listed rather than left
# to a phrasing accident, so a rejection introduced anywhere else fires.
REJECTION_SECTIONS = {"3.3", "5.1", "9.7"}

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z`\[])")
SECTION_CITE = re.compile(r"\[(?:Section|Appendix) [^\]]+\]\(#")
SIMILARITY = 0.86
IDENTICAL = 0.97
HEAD_WORDS = 4
# The length ratio below which SequenceMatcher cannot reach SIMILARITY at all,
# from ratio = 2*matches/total: a wholly matched shorter string against a longer
# one scores 2*short/(short+long), so short/long must be at least t/(2-t).
LENGTH_FLOOR = SIMILARITY / (2 - SIMILARITY)
MIN_SENTENCE = 60


PREAMBLE = "preamble"


def _sections(text):
    """(number, title, body) per numbered heading, so a finding can name where it is.

    Everything before the first numbered heading is one pseudo-section named
    `preamble`: the title block, Status of This Memo, the Abstract and the contents
    list. Without it that text sits outside every section and so outside every check
    here, and three requirements injected into the Abstract went unreported.
    """
    heads = [(m.start(), m.group(1), m.group(2))
             for m in re.finditer(r"^#{2,4} ((?:\d+\.)+|Appendix [A-Z]\.) (.+)$", text, re.M)]
    out = []
    if heads and heads[0][0] > 0:
        out.append((PREAMBLE, "Front matter", text[:heads[0][0]]))
    for index, (start, number, title) in enumerate(heads):
        end = heads[index + 1][0] if index + 1 < len(heads) else len(text)
        out.append((number.rstrip("."), title.strip(), text[start:end]))
    return out


def _prose_lines(body):
    """Body lines that are prose: not tables, fences, figures or reference entries."""
    lines, in_fence = [], False
    for line in body.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or line.startswith(("|", "#", "*Figure", "*Table")) or line.startswith("**["):
            continue
        if re.match(r"^\s*(?:-|\d+\.)\s+\[", line):      # a contents entry, not prose
            continue
        lines.append(line)
    return lines


def check_parties(text, where):
    """No normative keyword is bound to a person or an undefined role (blocker B3)."""
    findings = []
    for number, title, body in _sections(text):
        if number in ("2.1", "1.2"):            # the BCP 14 boilerplate quotes the keywords
            continue
        for line in _prose_lines(body):
            if "**Obligation:**" in line:       # an obligation cell, not a sentence
                continue
            for match in KEYWORD_RE.finditer(line):
                # The head of the subject: the sentence's first few words. Any wider
                # window picks up a relative clause ("a Frame ... imported into another
                # organization's registry MUST carry") and reports a sentence whose
                # actual subject is fine. A pronoun subject is skipped, since the
                # sentence that gave it its antecedent was scanned on its own.
                pieces = SENTENCE_RE.split(line[:match.start()])
                subject = pieces[-1].strip()
                if PRONOUN_SUBJECT.match(subject):
                    if len(pieces) < 2:
                        continue
                    subject = pieces[-2].strip()
                head = " ".join(subject.split()[:HEAD_WORDS])
                if UNDEFINED_PARTIES.search(head):
                    findings.append(Finding(
                        "error", "keyword-without-a-party",
                        f"section {number}: '{match.group(0)}' bound to a party this "
                        f"specification does not define, or to a person, which section 2.1 says "
                        f"it never does: {head!r}", where))
    return findings


def check_dispositions(text, where):
    """Every value-shape rule says what a reader does with a value that breaks it (S6)."""
    findings = []
    for number, title, body in _sections(text):
        for line in _prose_lines(body):
            if VALUE_RULE.search(line) and not DISPOSITION.search(line):
                findings.append(Finding(
                    "error", "value-rule-without-a-disposition",
                    f"section {number}: a value rule with no stated disposition, so a reader is "
                    f"left to choose whether to reject: {line.strip()[:90]!r}", where))
    return findings


def check_rejection_paths(text, where):
    """Only section 3.3 says a reader rejects a document (S8, and the promise of 4.6)."""
    findings = []
    for number, title, body in _sections(text):
        for line in _prose_lines(body):
            for match in REJECTION_RE.finditer(line):
                if number in REJECTION_SECTIONS:
                    continue
                findings.append(Finding(
                    "error", "undeclared-rejection-path",
                    f"section {number}: '{match.group(0)}' in a section that does not define an "
                    f"error condition or a resolution failure: {line.strip()[:90]!r}", where))
    return findings


def check_restatements(text, where):
    """A rule restated in another section must cite the section that defines it (B6, W2).

    Section 10's registration templates are exempt by shape, not by section: its
    definition-list bullets and its "IANA is requested to create a registry named"
    openings are parallel by design, while free prose inside a registration is
    compared like any other. Exempting the whole section hid a divergence between
    section 10.1.3's heading rule and section 6.2.2's.
    """
    findings, seen = [], []
    for number, title, body in _sections(text):

        for line in _prose_lines(body):
            if number.startswith("10") and (line.startswith("- **")
                                            or line.startswith("IANA is requested")):
                continue
            sentences = [x.strip() for x in SENTENCE_RE.split(line)]
            # Single sentences and adjacent pairs. A restatement that merges two
            # sentences into one, or splits one into two, matches no single sentence,
            # and section 1.2's summary of the dumb-down rule is exactly that shape.
            windows = sentences + [f"{a} {b}" for a, b in zip(sentences, sentences[1:])]
            for sentence in windows:
                if len(sentence) < MIN_SENTENCE:
                    continue
                bare = re.sub(r"\[\[[^\]]+\]\]\(#[^)]+\)|\[Section [^\]]+\]\(#[^)]+\)", "", sentence)
                bare = re.sub(r"\s+", " ", bare).strip()
                # Cheap prefilters before the quadratic comparison: a length band,
                # which SIMILARITY bounds outright, then a character-multiset ratio.
                low, high = len(bare) * LENGTH_FLOOR, len(bare) / LENGTH_FLOOR
                matcher = SequenceMatcher()
                matcher.set_seq2(bare)
                for other_number, other in seen:
                    if other_number == number or not low <= len(other) <= high:
                        continue
                    matcher.set_seq1(other)
                    if matcher.quick_ratio() < SIMILARITY:
                        continue
                    ratio = matcher.ratio()
                    if ratio < SIMILARITY:
                        continue
                    # The citation may sit in a neighbouring sentence of the same
                    # bullet or paragraph, which is close enough to bind the two.
                    if SECTION_CITE.search(line):
                        break
                    if ratio >= IDENTICAL:
                        findings.append(Finding(
                            "info", "duplicate-rule-statement",
                            f"section {number} states the same rule as section {other_number}, "
                            f"word for word: {bare[:70]!r}", where))
                    else:
                        findings.append(Finding(
                            "error", "restatement-drops-a-qualification",
                            f"section {number} restates section {other_number}'s rule with "
                            f"different wording and cites no section, so one of the two carries a "
                            f"qualification the other lacks: {bare[:90]!r}", where))
                    break
                seen.append((number, bare))
    return findings


# Section 2.1 states which parts of the document are normative. Parsed rather than
# hard-coded, so editing that sentence changes what this check enforces, and an
# unparseable sentence is an error rather than a silent pass.
CLASSIFICATION = re.compile(r"\b(Sections? \d[^.]*?) are normative")
RANGE = re.compile(r"\b(\d+) through (\d+)\b")
APPENDICES = re.compile(r"Appendices? ([A-Z](?:[,\s]+(?:and\s+)?[A-Z])*)")


def normative_sections(text):
    """(section numbers, appendix letters) declared normative by section 2.1.

    The sentence names sections as ranges ("3 through 7"), as individual numbers
    ("9 and 10"), or as both. It stopped being one range when section 8 came out of
    the normative set: RFC 7942's implementation status is removed before
    publication, so declaring it normative and declaring it temporary contradicted.
    """
    m = CLASSIFICATION.search(text)
    if not m:
        return None
    clause = m.group(1)
    numbers = set()
    for first, last in RANGE.findall(clause):
        numbers.update(range(int(first), int(last) + 1))
    # Ranges are consumed before the loose numbers are read, so the endpoints of
    # "3 through 7" are not read a second time as sections named on their own. Both
    # readings reach the same set, but only this one leaves "names no range" and
    # "names a range" distinguishable for whoever edits the sentence next.
    numbers.update(int(n) for n in re.findall(r"\b(\d+)\b", RANGE.sub("", clause)))
    appendices = APPENDICES.search(clause)
    letters = set(re.findall(r"\b([A-Z])\b", appendices.group(1))) if appendices else set()
    if not numbers or not letters:
        return None
    return numbers, letters


def check_normative_scope(text, where):
    """No normative keyword appears in a part section 2.1 calls non-normative (W2).

    A summary that restates a rule with a keyword is the defect: section 1.2 carried
    the dumb-down rule as a MUST without section 4.4.1's scope, so a reader following
    the summary and a reader following the rule behaved differently.
    """
    declared = normative_sections(text)
    if declared is None:
        return [Finding("error", "classification-unreadable",
                        "section 2.1's statement of which parts are normative did not parse, so "
                        "nothing checked where the requirements may appear", where)]
    numbers, letters = declared
    findings = []
    for number, title, body in _sections(text):
        if number == "2.1":                     # quotes the key words to define them
            continue
        if number == PREAMBLE:
            normative = False
        elif number.startswith("Appendix"):
            normative = number.split()[-1] in letters
        else:
            normative = int(number.split(".")[0]) in numbers
        if normative:
            continue
        for line in _prose_lines(body):
            for match in KEYWORD_RE.finditer(line):
                findings.append(Finding(
                    "error", "keyword-in-a-non-normative-part",
                    f"section {number} is not normative by section 2.1's own statement, and "
                    f"carries '{match.group(0)}': {line.strip()[:80]!r}", where))
    return findings


DECLARATION_RE = re.compile(r"^(\d+)\. (.+)$", re.M)
TEMPLATE_LABEL_RE = re.compile(r"^([A-Z][A-Za-z0-9 -]*?):\s+", re.M)
PLACEHOLDER_RE = re.compile(r"<[^>]+>")

# Appendix C's template has one free-text field that declares nothing, and three of
# its fields are covered by a section 7 item that asks for two things at once: item 1
# asks which encodings an implementation reads and writes, item 5 asks which elements
# it narrows and which it additionally requires, and item 10 asks for the
# specification version and the implementation's own version. Both numbers are
# deliberate: a legitimate change to either side updates them here, and any change to
# one side alone fires the check.
TEMPLATE_NON_DECLARATIONS = 1       # Notes
TEMPLATE_FIELDS_PAIRED = 3          # items 1, 5 and 10 each cover two fields


def _fenced_blocks(body):
    blocks, current, in_fence = [], [], False
    for line in body.splitlines():
        if line.startswith("```"):
            if in_fence:
                blocks.append("\n".join(current))
                current = []
            in_fence = not in_fence
            continue
        if in_fence:
            current.append(line)
    return blocks


def check_profile_template(text, where):
    """Section 7's declarations, Appendix C's template and Figure 11 stay in step.

    A requirement about conformance profiles lives in five places: section 7's list,
    Appendix C's template, Figure 11's worked example, the published profiles, and the
    checker's required keys. Three defects of that shape have been found by review:
    section 7 gained two declarations while the checker gained one, Figure 11 omitted
    two fields its own template requires, and section 7's list omits a declaration
    section 5.2's argument depends on. `conformance.REQUIRED_KEYS` is compared against
    the template in tools/test_framespec_conformance.py, which holds the label-to-key
    mapping; this check covers the three parts that need no mapping.
    """
    findings = []
    sections = dict((number, body) for number, _title, body in _sections(text))
    seven = sections.get("7")
    appendix = sections.get("Appendix C")
    if seven is None or appendix is None:
        return [Finding("error", "profile-sections-not-found",
                        "section 7 or Appendix C did not parse, so nothing compared the "
                        "declarations against the template", where)]
    declarations = DECLARATION_RE.findall(seven)
    blocks = _fenced_blocks(appendix)
    if len(blocks) < 2:
        return [Finding("error", "profile-template-not-found",
                        f"Appendix C holds {len(blocks)} fenced blocks; the template and the "
                        "worked example are both needed", where)]
    template, example = blocks[0], blocks[1]
    template_labels = TEMPLATE_LABEL_RE.findall(template)
    example_labels = TEMPLATE_LABEL_RE.findall(example)
    if not declarations or not template_labels:
        return [Finding("error", "profile-template-unreadable",
                        f"read {len(declarations)} declarations and {len(template_labels)} template "
                        "fields; one of the two patterns no longer matches", where)]
    missing = sorted(set(template_labels) - set(example_labels))
    if missing:
        findings.append(Finding("error", "example-profile-incomplete",
                                f"Figure 11 omits {', '.join(missing)}, which Appendix C's template "
                                "requires of a profile", where))
    left = PLACEHOLDER_RE.findall(example)
    if left:
        findings.append(Finding("error", "example-profile-unfilled",
                                f"Figure 11 leaves a placeholder unfilled: {', '.join(left)}", where))
    expected = len(template_labels) - TEMPLATE_NON_DECLARATIONS - TEMPLATE_FIELDS_PAIRED
    if len(declarations) != expected:
        findings.append(Finding(
            "error", "declarations-and-template-disagree",
            f"section 7 lists {len(declarations)} declarations; Appendix C's template has "
            f"{len(template_labels)} fields, of which {TEMPLATE_NON_DECLARATIONS} declare nothing "
            f"and {TEMPLATE_FIELDS_PAIRED} are the second half of a paired declaration, leaving "
            f"{expected}; one side gained a requirement the other did not", where))
    return findings


CHECKS = (check_parties, check_dispositions, check_rejection_paths, check_restatements,
          check_normative_scope, check_profile_template)


def lint(spec_path=DEFAULT_SPEC_PATH):
    """Findings for every prose invariant the draft breaks."""
    text = Path(spec_path).read_text(encoding="utf-8")
    where = Path(spec_path).resolve().as_uri()
    findings = [f for check in CHECKS for f in check(text, where)]
    if not findings:
        findings.append(Finding("info", "spec-lint-ok",
                                f"{len(CHECKS)} prose invariants hold", where))
    return findings
