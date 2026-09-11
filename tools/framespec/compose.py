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
    spec/profile/frame-core.csv. Rule 5 defines the composing side positively, as
    `guidance`, the elements that refine it, and `guards`; everything else belongs
    to the declaring Frame. That remainder is the metadata elements, `composition`
    itself, and any unknown or `x-` element, none of which appear in a list here
    yet none of which may vanish.
    """
    names = list(profile.content_elements())
    if GUARDS not in names:
        names.append(GUARDS)
    return tuple(names)


def load_conformance(path):
    """A conformance profile as a mapping, from YAML (PyYAML) or JSON by suffix.

    The narrowings are parsed here as well as in compose(), so a profile whose
    declarations cannot be read fails when the file is read and names the file, rather
    than resolving a composed set as though the profile had declared nothing.
    """
    text = Path(path).read_text(encoding="utf-8")
    if str(path).lower().endswith(".json"):
        data = json.loads(text)
    else:
        import yaml
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as error:
            # A ValueError like the JSON leg's, so a caller need not import yaml to
            # catch a syntax error in a profile.
            raise ValueError(f"{path}: {error}") from error
    if not isinstance(data, dict):
        # Say what is wrong with the file rather than raising AttributeError on the
        # first .get() of a profile that turned out to be a list or a bare string.
        raise ValueError(f"{path}: a conformance profile must be a mapping of keys to values")
    _narrowings(data, where=path)
    return data


def compose(frames, profile, conformance=None):
    """Resolve one composed set into a single Frame.

    frames are ordered lowest precedence first, so the last is the declaring Frame and
    has the highest precedence (rules 2 and 3). conformance is a loaded conformance
    profile; the keys read here are `non_repeatable` and `rule6_narrowings`, each of
    which a profile may write as one name or as a list of names.
    """
    if not frames:
        raise ValueError("compose() needs at least one Frame: the declaring Frame")
    non_repeatable, dedup_all, dedup_names, replace_by_key = _narrowings(conformance or {})
    # Rule 6 narrows content elements only, so a non-repeatable declaration that names
    # guards is ignored: rule 5 accumulates guards without qualification, and taking one
    # Frame's value in place of the others would drop a Guard the composed set declares,
    # which is the compliance failure rule 5 exists to prevent. Deduplication may still
    # reach guards, since collapsing two identical references drops no Guard.
    non_repeatable &= set(profile.content_elements())
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
            values = _dedup_keep_first(values)
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
            # force declares non-repeatable does not conform to that profile; rule 6
            # does not say which of its values a reader takes. Either choice conforms;
            # this keeps the first, the same choice _dedup_keep_first makes below, so
            # the module is consistent about it rather than picking oppositely in two
            # places for input that is already non-conforming.
            return value[0]
        # Present with no values at all: there is nothing to replace the lower-precedence
        # values with, so precedence passes down.
    return _ABSENT


def _narrowings(conformance, where=None):
    """A conformance profile's declarations, as (non_repeatable, dedup_all, dedup, replace).

    The three declarations are read the same way, by one helper, because a profile writes
    each of them in the same three forms and getting one of them right is no use.
    """
    if not isinstance(conformance, dict):
        raise ValueError(_bad_narrowing("a conformance profile", conformance, where,
                                        "a mapping of keys to values"))
    non_repeatable = _names(conformance.get("non_repeatable"), "non_repeatable", where)
    declared = conformance.get("rule6_narrowings") or {}
    if not isinstance(declared, dict):
        raise ValueError(_bad_narrowing("rule6_narrowings", declared, where,
                                        "a mapping of narrowing names to their values"))
    dedup = _names(declared.get("dedup"), "rule6_narrowings.dedup", where)
    replace_by_key = _names(declared.get("replace_by_key"), "rule6_narrowings.replace_by_key", where)
    # "all-repeatable" is a token rather than an element name, in whichever of the forms
    # the profile wrote it, and what remains is the elements the narrowing names.
    return non_repeatable, ALL_REPEATABLE in dedup, dedup - {ALL_REPEATABLE}, replace_by_key


def _names(value, key, where=None):
    """The element names a narrowing declares: a list of names, one bare name, or nothing.

    YAML's natural form for a single value is a scalar, so `non_repeatable: style` names
    the one element, exactly as `non_repeatable: [style]` does. Iterating the string
    instead would take it apart into letters, and since no letter is an element name the
    narrowing would be dropped and the resolved Frame would contradict the profile it
    was resolved under, with nothing said and an exit code of 0.
    """
    if value is None:
        return set()
    if isinstance(value, str):
        return {value}
    if isinstance(value, (list, tuple, set)) and all(isinstance(v, str) for v in value):
        return set(value)
    raise ValueError(_bad_narrowing(key, value, where, "an element name or a list of element names"))


def _bad_narrowing(key, value, where, expected):
    at = f"{where}: " if where else ""
    return f"{at}{key} must be {expected}, not {value!r}"


def _stable_key(value):
    """A comparison key that only identical values share.

    json.dumps tells 1 from "1", which str() would not, and rule 6 forbids dropping
    values that are not identical.
    """
    try:
        return json.dumps(value, sort_keys=True)
    except TypeError:
        return repr((type(value).__name__, value))


def _dedup_keep_first(values):
    """Identical values collapse to their first occurrence in the concatenation.

    Rule 6 keeps the first occurrence, not the highest-precedence one, and it is not a
    precedence question at all: rule 3 decides which content wins when Frames conflict,
    but identical values do not conflict, so rule 3 has nothing to say about which of
    them a dedup narrowing keeps. What rule 6 asks for instead is that the result stay a
    subsequence of the concatenation, so a narrowing removes values rather than
    reordering them. Keeping the first occurrence is what makes that true; keeping the
    last would reorder a repeated value forward to wherever its highest-precedence
    occurrence sits, which is a reordering rather than a removal.
    """
    seen = set()
    out = []
    for value in values:
        key = _stable_key(value)
        if key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out


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
