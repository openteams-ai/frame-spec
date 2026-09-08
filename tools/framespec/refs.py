"""Classify a reference by form (draft section 5.3). Classification never fails."""

import re

PINNED = "pinned-ref"
QUALIFIED = "qualified-ref"
URI = "uri-ref"
PATH = "path-ref"
NAME = "name-ref"

_QUALIFIED = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
_PATH_PREFIXES = ("./", "../", "/")


def classify(ref):
    """Return the form of ref: path first, then pinned, qualified, URI, and name.

    Paths are tested first because "." is a legal character in a qualified-ref
    segment, so "./x.frame.md" would otherwise match the qualified form. Any
    non-empty string is at least a name-ref, so the only error is an empty
    reference.
    """
    text = ref.strip()
    if not text:
        raise ValueError("empty reference")
    if text.startswith(_PATH_PREFIXES):
        return PATH
    if "@" in text:
        left, _, version = text.rpartition("@")
        if version and " " not in version and _QUALIFIED.match(left):
            return PINNED
    if _QUALIFIED.match(text):
        return QUALIFIED
    if _SCHEME.match(text):
        return URI
    return NAME
