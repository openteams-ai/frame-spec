"""Check a normalized Frame against the profile. Nothing here rejects for content."""

import re

from . import refs
from .findings import Finding
from .profile import CONTENT_ROOT

RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[Tt ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2}))?$")
# xsd:integer's lexical space: an optional sign and one or more digits.
INTEGER_RE = re.compile(r"^[+-]?\d+$")


def _is_integer(value):
    """True when a value is in xsd:integer's lexical space.

    JSON and YAML both give a plain 42 as a Python int, and a quoted "42" as a string
    that is still lexically an integer, so both are accepted. A boolean is not: YAML's
    true is an int subclass in Python, but it is xsd:boolean and not an integer.
    """
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    return bool(INTEGER_RE.match(str(value).strip()))


def _all_null(value):
    """True when an element is present and every value it carries is null.

    normalize() wraps a repeatable element's value in a list, so a null guidance
    arrives here as [None] rather than as None. An element present with no values at
    all is empty, not null, and is not this function's business.
    """
    items = value if isinstance(value, list) else [value]
    return bool(items) and all(item is None for item in items)


def check(frame, profile):
    findings = []
    where = frame.location
    present = frame.elements
    for name in profile.mandatory():
        if name not in present:
            findings.append(Finding("error", "missing-mandatory", f"'{name}' is mandatory", where))
    if CONTENT_ROOT in present and _all_null(present[CONTENT_ROOT]):
        # Section 4.2.2 makes guidance MUST be present and MAY be empty, and the
        # mandatory test above is a test of presence, so an explicit null satisfies it.
        # Whether a null is empty is not something the draft says. This tool takes the
        # permissive reading, that it is, and reports the reading rather than applying
        # it silently: the question is open on a MUST, an implementation that read it
        # the other way would conform too, and tools/README.md records which reading
        # this one takes.
        findings.append(Finding("info", "guidance-null",
                                f"'{CONTENT_ROOT}' is present with a null value, read here as empty; the draft "
                                "does not say whether a null is empty", where))
    for name, value in present.items():
        element = profile.elements.get(name)
        if element is None:
            code = "extension-preserved" if name.startswith("x-") else "unknown-preserved"
            findings.append(Finding("info", code, f"'{name}' is not a registered element; preserved", where))
            continue
        values = value if isinstance(value, list) else [value]
        if not element.repeatable and isinstance(value, list) and len(value) > 1:
            findings.append(Finding("error", "not-repeatable",
                                    f"'{name}' is not repeatable but carries {len(value)} values", where))
        for item in values:
            if element.picklist and item not in element.picklist:
                findings.append(Finding("warning", "unregistered-value",
                                        f"'{name}' value {item!r} is not a registered value; preserved", where))
            if element.is_reference:
                try:
                    form = refs.classify(str(item))
                    findings.append(Finding("info", "reference-form", f"'{name}' reference {item!r} is a {form}", where))
                except ValueError:
                    findings.append(Finding("warning", "empty-reference", f"'{name}' contains an empty reference", where))
            if element.data_type == "xsd:dateTime" and not RFC3339_RE.match(str(item)):
                findings.append(Finding("warning", "not-rfc3339",
                                        f"'{name}' value {item!r} is not an RFC 3339 date or date-time", where))
            # The profile's second datatype, at the same level as the date above, since
            # the draft's preserve-rather-than-reject rules apply to both. Its third,
            # xsd:string, needs no check: every value a document can carry has a string
            # form, so there is no lexical mistake left to report.
            if element.data_type == "xsd:integer" and not _is_integer(item):
                findings.append(Finding("warning", "not-an-integer",
                                        f"'{name}' value {item!r} is not an integer", where))
    return findings
