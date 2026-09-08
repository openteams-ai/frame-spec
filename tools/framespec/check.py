"""Check a normalized Frame against the profile. Nothing here rejects for content."""

import re

from . import refs
from .findings import Finding

RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:[Tt ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2}))?$")


def check(frame, profile):
    findings = []
    where = frame.location
    present = frame.elements
    for name in profile.mandatory():
        if name not in present:
            findings.append(Finding("error", "missing-mandatory", f"'{name}' is mandatory", where))
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
    return findings
