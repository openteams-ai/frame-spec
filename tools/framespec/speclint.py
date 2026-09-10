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
DISPOSITION = re.compile(r"preserv\w+|MUST NOT reject|warn\w*|report\w*|error", re.I)
VALUE_RULE = re.compile(r"The value MUST\b|value MUST be\b")

# Section 3.3's promise. A reader rejects a document for these two reasons only, so
# any other sentence that says a reader rejects, refuses or fails on a document is
# either a third path or needs rewording.
REJECTION_RE = re.compile(r"MUST (?:reject|refuse|fail)", re.I)

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z`\[])")
SECTION_CITE = re.compile(r"\[(?:Section|Appendix) [^\]]+\]\(#")
SIMILARITY = 0.86
IDENTICAL = 0.97
HEAD_WORDS = 4
MIN_SENTENCE = 60


def _sections(text):
    """(number, title, body) per numbered heading, so a finding can name where it is."""
    heads = [(m.start(), m.group(1), m.group(2))
             for m in re.finditer(r"^#{2,4} ((?:\d+\.)+|Appendix [A-Z]\.) (.+)$", text, re.M)]
    out = []
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
                subject = SENTENCE_RE.split(line[:match.start()])[-1].strip()
                if PRONOUN_SUBJECT.match(subject):
                    continue
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
                if number == "3.3":
                    continue
                findings.append(Finding(
                    "error", "undeclared-rejection-path",
                    f"section {number}: '{match.group(0)}' outside section 3.3, which enumerates "
                    f"the error conditions: {line.strip()[:90]!r}", where))
    return findings


def check_restatements(text, where):
    """A rule restated in another section must cite the section that defines it (B6, W2).

    Section 10 is exempt. Its media-type registrations and registry requests are
    template-shaped by design, so three registries that each open "IANA is requested
    to create a registry named" are parallel structure rather than drift.
    """
    findings, seen = [], []
    for number, title, body in _sections(text):
        if number.startswith("10"):
            continue
        for line in _prose_lines(body):
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
                low, high = len(bare) * SIMILARITY, len(bare) / SIMILARITY
                for other_number, other in seen:
                    if other_number == number or not low <= len(other) <= high:
                        continue
                    matcher = SequenceMatcher(None, bare, other)
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
CLASSIFICATION = re.compile(
    r"Sections (\d+) through (\d+) and Appendices ([A-Z](?:, [A-Z])*,? and [A-Z]) are normative")


def normative_sections(text):
    """(section numbers, appendix letters) declared normative by section 2.1."""
    m = CLASSIFICATION.search(text)
    if not m:
        return None
    first, last = int(m.group(1)), int(m.group(2))
    letters = set(re.findall(r"\b([A-Z])\b", m.group(3)))
    return set(range(first, last + 1)), letters


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
        if number.startswith("Appendix"):
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


CHECKS = (check_parties, check_dispositions, check_rejection_paths, check_restatements,
          check_normative_scope)


def lint(spec_path=DEFAULT_SPEC_PATH):
    """Findings for every prose invariant the draft breaks."""
    text = Path(spec_path).read_text(encoding="utf-8")
    where = Path(spec_path).resolve().as_uri()
    findings = [f for check in CHECKS for f in check(text, where)]
    if not findings:
        findings.append(Finding("info", "spec-lint-ok",
                                f"{len(CHECKS)} prose invariants hold", where))
    return findings
