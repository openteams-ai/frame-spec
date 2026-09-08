"""Check a conformance profile (draft section 7, Appendix C) for completeness and consistency."""

from .compose import ALL_REPEATABLE
from .findings import Finding

REQUIRED_KEYS = ("implementation", "version", "specification", "encodings_read", "encodings_written",
                 "resolves_composition", "reference_forms", "rule6_narrowings", "non_repeatable",
                 "additionally_required", "identifier_minting", "visibility")
ENCODINGS = {"markdown", "yaml", "json"}
RESOLUTION = {"none", "non-transitive", "transitive"}
FORMS = {"pinned-ref", "qualified-ref", "uri-ref", "path-ref", "name-ref"}
NARROWING_KEYS = {"dedup", "replace_by_key"}


def _safe_name(value):
    """A value made safe to compare against a vocabulary set or a dict's keys.

    A string passes through unchanged, since it may legitimately be a name in the
    vocabulary being checked. Anything else becomes its own repr. This is the single
    place that decision is made: every vocabulary comparison in this module tests set
    or dict-key membership, which raises for an unhashable value (a list, a set, a
    dict) rather than producing a finding, so nothing may reach one of those
    comparisons except a string, and _as_list() and _as_name() both build on this
    function rather than each deciding it on its own.
    """
    return value if isinstance(value, str) else repr(value)


def _as_list(value):
    """A field's value as a list of names.

    A shape that cannot be a list of names becomes one unusable name (via
    _safe_name()), so the caller's own vocabulary check reports it as an ordinary
    finding. A bare scalar is the shorthand framespec.compose._names() already accepts
    for non_repeatable and the two rule6_narrowings keys: a string is one name, not an
    iterable of characters, so it is wrapped rather than iterated. A non-string element
    buried inside an already-list-shaped value (reference_forms: [[pinned-ref]], a
    block list item that is itself a flow list, an easy YAML slip) is made safe the
    same way, one element at a time, rather than passed through as an unhashable list.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return [_safe_name(v) for v in value]
    return [_safe_name(value)]


def _as_name(value):
    """A scalar field's value made safe to compare against a vocabulary, or None.

    Mirrors _as_list()'s guarantee for a field that takes one value rather than a list
    of them. resolves_composition is the one such field this module checks against a
    vocabulary; resolves_composition: [transitive] is an easy mistake for a field that
    sits among several list-shaped ones, and without this it reached `not in
    RESOLUTION` as a raw, unhashable list and crashed rather than producing a finding.
    None passes through unchanged, so a missing value is still reported as
    profile-missing-key elsewhere, not miscast here as a bad one.
    """
    return value if value is None else _safe_name(value)


def check_profile(data, profile, where=None):
    findings = []
    for key in REQUIRED_KEYS:
        if key not in data:
            findings.append(Finding("error", "profile-missing-key", f"conformance profile lacks '{key}'", where))
    for key in ("encodings_read", "encodings_written"):
        for enc in _as_list(data.get(key)):
            if enc not in ENCODINGS:
                findings.append(Finding("error", "profile-bad-encoding", f"{key} lists unknown encoding {enc!r}", where))
    resolution = _as_name(data.get("resolves_composition"))
    if resolution is not None and resolution not in RESOLUTION:
        findings.append(Finding("error", "profile-bad-resolution",
                                f"resolves_composition must be one of {sorted(RESOLUTION)}, got {resolution!r}", where))
    forms = _as_list(data.get("reference_forms"))
    for form in forms:
        if form not in FORMS:
            findings.append(Finding("error", "profile-bad-reference-form", f"unknown reference form {form!r}", where))
    content = set(profile.content_elements())
    non_repeatable = set(_as_list(data.get("non_repeatable")))
    for name in non_repeatable:
        if name not in content:
            # Not "content elements and guards": rule 5 makes guards accumulate
            # unconditionally, so declaring guards non-repeatable is not a narrowing
            # a profile may make. framespec.compose ignores such a declaration.
            findings.append(Finding("error", "profile-narrowing-not-content",
                                    f"only guidance and its refinements may be narrowed to non-repeatable, not {name!r}", where))
    for name in _as_list(data.get("additionally_required")):
        if name not in profile.elements:
            findings.append(Finding("error", "profile-unknown-element", f"additionally_required names unknown element {name!r}", where))
    narrowings = data.get("rule6_narrowings") or {}
    if not isinstance(narrowings, dict):
        # Blocked at the shipped tool: load_conformance() already validates
        # rule6_narrowings is a mapping before check_profile() ever sees it, so this is
        # reachable only by calling check_profile() directly. Fixed anyway, in the same
        # discipline as _as_list()/_as_name(): a wrong shape becomes a finding here
        # rather than an unhandled TypeError a few lines down, where `for key in
        # narrowings` or `set(narrowings)` would raise on a value that is not iterable
        # at all, or is iterable but not of hashable elements.
        findings.append(Finding("error", "profile-bad-narrowing-key",
                                f"rule6_narrowings must be a mapping of narrowing names to their values, "
                                f"got {narrowings!r}", where))
        narrowings = {}
    for key in narrowings:
        if key not in NARROWING_KEYS:
            findings.append(Finding("error", "profile-bad-narrowing-key", f"rule6_narrowings has unknown key {key!r}", where))
    for key in NARROWING_KEYS & set(narrowings):
        names = _as_list(narrowings[key])
        if key == "dedup":
            # The token that names every repeatable element at once, in whichever form
            # the profile wrote it. It is meaningful only for dedup; replace-by-key has
            # no such token, so one written there falls through to the check below and
            # is reported like any other name that is not a real, still-repeatable
            # element.
            names = [n for n in names if n != ALL_REPEATABLE]
        for name in names:
            if name not in profile.elements:
                # Distinct from "not repeatable": this name is not one of the model's
                # elements at all, so "names non-repeatable element" would misdescribe a
                # name that does not exist as one that exists but does not qualify.
                # additionally_required already gets this distinction right; this makes
                # rule6_narrowings consistent with it.
                findings.append(Finding("error", "profile-unknown-element",
                                        f"rule6_narrowings.{key} names unknown element {name!r}", where))
            elif not profile.is_repeatable(name):
                findings.append(Finding("error", "profile-narrowing-not-content",
                                        f"rule6_narrowings.{key} names non-repeatable element {name!r}", where))
            elif name in non_repeatable:
                # Self-contradictory within this one profile: non_repeatable already
                # sends this element through rule 6's replace branch, where dedup and
                # replace-by-key do not apply. framespec.compose resolves it with
                # _highest_present() alone, so this narrowing names a merge step the
                # profile's own composition never performs.
                findings.append(Finding("error", "profile-narrowing-not-content",
                                        f"rule6_narrowings.{key} names {name!r}, which non_repeatable also "
                                        "narrows: the two declarations cannot both apply to the same element", where))
    if resolution == "none":
        # Rule 9 (reference forms) and rule 6 (narrowings) both describe behavior that
        # only matters when composition is actually resolved. Declaring either while
        # resolves_composition is "none" is the same shape of leftover, unexercised
        # declaration, so both earn the same warning by the same reasoning.
        if forms:
            findings.append(Finding("warning", "profile-forms-without-resolution",
                                    "reference_forms are listed but resolves_composition is 'none'", where))
        if non_repeatable or narrowings:
            findings.append(Finding("warning", "profile-forms-without-resolution",
                                    "non_repeatable or rule6_narrowings are declared but resolves_composition "
                                    "is 'none': rule 6 narrows how composition merges values, and this profile "
                                    "never resolves any composition to merge", where))
    if "visibility" in data and "not an access control" not in str(data["visibility"]):
        findings.append(Finding("warning", "profile-visibility-wording",
                                "visibility should state that it is not used as an access control", where))
    if not findings:
        findings.append(Finding("info", "profile-ok", f"conformance profile for {data.get('implementation')!r} is complete", where))
    return findings
