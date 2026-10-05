"""The normalized Frame model that every encoding parses into."""

import datetime
from dataclasses import dataclass, field

from .findings import Finding

DEFAULTED = "identifier-defaulted"   # an extras marker, not an element


@dataclass
class Frame:
    elements: dict
    encoding: str
    location: str | None = None
    extras: dict = field(default_factory=dict)


def default_identifier(elements, extras, location):
    """Apply section 6.1: a document that states no identifier is identified by where
    it was retrieved from. Returns the finding to report, or None if nothing was done.

    The rule lives here, beside Frame.extras, because it is a rule about the model
    rather than about any one encoding: all three apply it identically, and the marker
    it leaves in extras records that the value was derived and not stated. Each
    encoding used to implement it and honor it for itself, which had the YAML and JSON
    encoding import the Markdown encoding to reach a model-level marker.
    """
    if "identifier" in elements or not location:
        return None
    elements["identifier"] = location
    extras[DEFAULTED] = True
    return Finding("info", "identifier-default", "identifier defaulted to the retrieval location", location)


def derived_names(frame):
    """The elements a writer must not emit, because the model derived them.

    Emitting a defaulted identifier would bake one machine's retrieval location into
    a shared document as its identity. Only `identifier` can be derived today, and a
    set keeps each writer's `name in skip` test unchanged if another value joins it.
    """
    return {"identifier"} if frame.extras.get(DEFAULTED) else set()


def _plain(value):
    """Render dates as text, recursing through lists and mappings.

    YAML parsers turn an unquoted 2026-09-07 into a date object, which JSON
    cannot serialize, so the model keeps RFC 3339 text instead. datetime is a
    subclass of date, so one test covers both.
    """
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, list):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    return value


def normalize(elements, profile):
    """Lists for repeatable known elements; dates as text; guidance stripped of outer newlines.

    Unknown elements are passed through as parsed (dates aside) so they can be
    preserved on output (draft section 4.7).
    """
    out = {}
    for name, value in elements.items():
        value = _plain(value)
        if profile.is_repeatable(name) and not isinstance(value, list):
            value = [value]
        if name == "guidance":
            # Do not trust the wrap above: defend the branch so normalize() is
            # correct for any profile, not only one that marks guidance repeatable.
            items = value if isinstance(value, list) else [value]
            value = [v.strip("\n") if isinstance(v, str) else v for v in items]
        out[name] = value
    return out
