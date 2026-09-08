"""Resolve composition (draft section 5.1, rules 2, 3, 5 and 6) over an ordered set of Frames.

The order is given, not discovered: this module resolves no references and walks no
graph, so rules 4, 7 and 8 are the caller's concern. That is what section 5.4 permits,
where the order in which a session activated the Frames is the precedence order, and it
is how the composition a registry resolves and the layering an application performs come
under the same rules.
"""

import json
from pathlib import Path

from .model import Frame
from .profile import CONTENT_ROOT

GUARDS = "guards"                       # rule 5: composes by accumulation, alongside the content
ALL_REPEATABLE = "all-repeatable"       # the dedup narrowing that names every repeatable element
TERM_KEY = "term"                       # terminology's natural key (draft sections 6.3 and 6.4)

_ABSENT = object()                      # "no Frame had this element", which None cannot say


def composing_elements(profile):
    """The elements rule 5 lets compose: guidance, its refinements, and guards, in profile order.

    Derived from the profile rather than listed here, so the element set stays in
    spec/profile/frame-core.csv. Rule 5 defines the composing side positively, and
    everything else belongs to the declaring Frame: the fourteen elements rule 5
    enumerates, `composition`, the representation-level elements of section 4.6, and
    any unknown or `x-` element, which appear in no list yet must not vanish.
    """
    names = list(profile.content_elements())
    if GUARDS not in names:
        names.append(GUARDS)
    return tuple(names)


def load_conformance(path):
    """A conformance profile as a mapping, from YAML (PyYAML) or JSON by suffix."""
    text = Path(path).read_text(encoding="utf-8")
    if str(path).lower().endswith(".json"):
        data = json.loads(text)
    else:
        import yaml
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        # Say what is wrong with the file rather than raising AttributeError on the
        # first .get() of a profile that turned out to be a list or a bare string.
        raise ValueError(f"{path}: a conformance profile must be a mapping of keys to values")
    return data


def compose(frames, profile, conformance=None):
    """Resolve one composed set into a single Frame.

    frames are ordered lowest precedence first, so the last is the declaring Frame and
    has the highest precedence (rules 2 and 3). conformance is a loaded conformance
    profile; the keys read here are `non_repeatable` and `rule6_narrowings`.
    """
    if not frames:
        raise ValueError("compose() needs at least one Frame: the declaring Frame")
    conformance = conformance or {}
    content = set(profile.content_elements())
    # Rule 6 narrows content elements only, so a non-repeatable declaration that names
    # guards is ignored: rule 5 accumulates guards without qualification, and taking one
    # Frame's value in place of the others would drop a Guard the composed set declares,
    # which is the compliance failure rule 5 exists to prevent. Deduplication may still
    # reach guards, since collapsing two identical references drops no Guard.
    non_repeatable = {n for n in (conformance.get("non_repeatable") or ()) if n in content}
    narrowings = conformance.get("rule6_narrowings") or {}
    dedup_all, dedup_names = _dedup_narrowing(narrowings.get("dedup"))
    replace_by_key = set(narrowings.get("replace_by_key") or ())
    declaring = frames[-1]
    composing = composing_elements(profile)
    # Rule 5: only content elements and guards compose, so every other element on the
    # result is the declaring Frame's own and none is inherited.
    result = {name: _unshared(value) for name, value in declaring.elements.items()
              if name not in composing}
    for name in composing:
        if name in non_repeatable:
            # Rule 6, replace branch.
            value = _highest_present(frames, name)
            if value is not _ABSENT:
                result[name] = value
            continue
        # Rule 6, concatenate branch, then the two narrowings a profile may declare.
        values = _concatenated(frames, name)
        if name in replace_by_key:
            values = _replace_by_key(values)
        if dedup_all or name in dedup_names:
            values = _dedup_keep_last(values)
        if values:
            result[name] = values
    if CONTENT_ROOT not in result:
        # guidance MUST be present and MAY be empty (section 4.2.2), so a composed set
        # whose Frames all leave it empty still has the element, in the shape the
        # profile in force gives it.
        result[CONTENT_ROOT] = "" if CONTENT_ROOT in non_repeatable else [""]
    return Frame(result, declaring.encoding, declaring.location, dict(declaring.extras))


def _unshared(value):
    """A list value the composed Frame owns, so mutating it cannot reach an input Frame."""
    return list(value) if isinstance(value, list) else value


def _concatenated(frames, name):
    """Every composed Frame's values for one element, in order of increasing precedence.

    An empty string is left out. Section 4.2.2 says a Frame with empty guidance "carries
    nothing", so an empty value adds nothing to a concatenation while a blank entry in
    the middle of the composed content would suggest it did. No value that carries
    content is dropped, which is what rule 6 protects.
    """
    values = []
    for frame in frames:
        value = frame.elements.get(name)
        if value is None:
            continue
        values.extend(v for v in (value if isinstance(value, list) else [value]) if v != "")
    return values


def _highest_present(frames, name):
    """Rule 6's replace branch: the value of the highest-precedence Frame that has the element.

    Presence is the element appearing on the Frame, not its value being non-empty:
    section 4.2.2 defines guidance as "MUST be present; MAY be empty", so a Frame that
    declares an element empty is a Frame in which the element is present, and its empty
    value replaces the values below it. Filtering empty values here would hand the
    result to a lower-precedence Frame, which rule 6 does not allow.
    """
    for frame in reversed(frames):
        if name not in frame.elements:
            continue
        value = frame.elements[name]
        if not isinstance(value, list):
            return value
        if value:
            # The model stores a repeatable element as a list, so a single value arrives
            # wrapped. A Frame carrying several values for an element the profile in
            # force declares non-repeatable does not conform to that profile; the last
            # of its own values is the one kept.
            return value[-1]
        # Present with no values at all: there is nothing to replace the lower-precedence
        # values with, so precedence passes down.
    return _ABSENT


def _dedup_narrowing(dedup):
    """Rule 6's dedup narrowing as (applies to every repeatable element, named elements).

    A profile writes either the token "all-repeatable" or a list of element names. A
    bare string that is not the token names one element; it is never matched as a
    substring, which is what testing `name in dedup` against a string would do.
    """
    if dedup == ALL_REPEATABLE:
        return True, set()
    if isinstance(dedup, str):
        return False, {dedup}
    return False, set(dedup or ())


def _stable_key(value):
    """A comparison key that only identical values share.

    json.dumps tells 1 from "1", which str() would not, and rule 6 forbids dropping
    values that are not identical.
    """
    try:
        return json.dumps(value, sort_keys=True)
    except TypeError:
        return repr((type(value).__name__, value))


def _dedup_keep_last(values):
    """Identical values collapse to their highest-precedence occurrence.

    Rule 6 permits a profile to deduplicate identical values but does not say which
    position a deduplicated value keeps. This keeps the last, so a value sits where the
    highest-precedence Frame that declared it put it and the declaring Frame's own
    ordering survives (rule 3). Only position is at stake: the values are identical.
    """
    last = {_stable_key(v): i for i, v in enumerate(values)}
    return [v for i, v in enumerate(values) if last[_stable_key(v)] == i]


def _replace_by_key(values):
    """A later value with the same natural key replaces an earlier one, in place.

    `terminology` is the standing example and the only element the draft gives a
    structured form, whose key is `term` (sections 4.4.2, 6.3 and 6.4). A value with no
    key, such as the unstructured terminology content section 4.4.2 allows, has nothing
    to be replaced by and is kept.
    """
    out, index = [], {}
    for value in values:
        key = value.get(TERM_KEY) if isinstance(value, dict) else None
        if key is None:
            out.append(value)
            continue
        if key in index:
            out[index[key]] = value
            continue
        index[key] = len(out)
        out.append(value)
    return out
