"""The normalized Frame model that every encoding parses into."""

import datetime
from dataclasses import dataclass, field


@dataclass
class Frame:
    elements: dict
    encoding: str
    location: str | None = None
    extras: dict = field(default_factory=dict)


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
