"""The normalized Frame model that every encoding parses into."""

import datetime
from dataclasses import dataclass, field


@dataclass
class Frame:
    elements: dict
    encoding: str
    location: str = None
    extras: dict = field(default_factory=dict)


def _plain(value):
    """YAML parsers turn 2026-09-07 into a date object; the model keeps RFC 3339 text."""
    if isinstance(value, (datetime.date, datetime.datetime)):
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
            value = [v.strip("\n") if isinstance(v, str) else v for v in value]
        out[name] = value
    return out
