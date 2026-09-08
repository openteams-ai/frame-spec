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


def _as_list(value):
    """A field's value as a list of names: a bare scalar, a list, or absent.

    Appendix C's list-shaped fields accept a single name written as a bare scalar, the
    same shorthand framespec.compose._names() accepts for non_repeatable and the two
    rule6_narrowings keys. Without this, a profile that used the shorthand would have
    its one name iterated letter by letter and checked against the element vocabulary,
    turning a valid declaration into a handful of unrelated findings.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def check_profile(data, profile, where=None):
    findings = []
    for key in REQUIRED_KEYS:
        if key not in data:
            findings.append(Finding("error", "profile-missing-key", f"conformance profile lacks '{key}'", where))
    for key in ("encodings_read", "encodings_written"):
        for enc in _as_list(data.get(key)):
            if enc not in ENCODINGS:
                findings.append(Finding("error", "profile-bad-encoding", f"{key} lists unknown encoding {enc!r}", where))
    resolution = data.get("resolves_composition")
    if resolution is not None and resolution not in RESOLUTION:
        findings.append(Finding("error", "profile-bad-resolution",
                                f"resolves_composition must be one of {sorted(RESOLUTION)}, got {resolution!r}", where))
    forms = _as_list(data.get("reference_forms"))
    for form in forms:
        if form not in FORMS:
            findings.append(Finding("error", "profile-bad-reference-form", f"unknown reference form {form!r}", where))
    if resolution == "none" and forms:
        findings.append(Finding("warning", "profile-forms-without-resolution",
                                "reference_forms are listed but resolves_composition is 'none'", where))
    content = set(profile.content_elements())
    non_repeatable = set(_as_list(data.get("non_repeatable")))
    for name in non_repeatable:
        if name not in content:
            # Not "content elements and guards": rule 5 makes guards accumulate
            # unconditionally, so declaring guards non-repeatable is not a narrowing
            # a profile may make. framespec.compose ignores such a declaration.
            findings.append(Finding("error", "profile-narrowing-not-content",
                                    f"only guidance and its refinements may be narrowed to non-repeatable, not '{name}'", where))
    for name in _as_list(data.get("additionally_required")):
        if name not in profile.elements:
            findings.append(Finding("error", "profile-unknown-element", f"additionally_required names unknown element '{name}'", where))
    narrowings = data.get("rule6_narrowings") or {}
    for key in narrowings:
        if key not in NARROWING_KEYS:
            findings.append(Finding("error", "profile-bad-narrowing-key", f"rule6_narrowings has unknown key '{key}'", where))
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
            if not profile.is_repeatable(name):
                findings.append(Finding("error", "profile-narrowing-not-content",
                                        f"rule6_narrowings.{key} names non-repeatable element '{name}'", where))
            elif name in non_repeatable:
                # Self-contradictory within this one profile: non_repeatable already
                # sends this element through rule 6's replace branch, where dedup and
                # replace-by-key do not apply. framespec.compose resolves it with
                # _highest_present() alone, so this narrowing names a merge step the
                # profile's own composition never performs.
                findings.append(Finding("error", "profile-narrowing-not-content",
                                        f"rule6_narrowings.{key} names '{name}', which non_repeatable also "
                                        "narrows: the two declarations cannot both apply to the same element", where))
    if "visibility" in data and "not an access control" not in str(data["visibility"]):
        findings.append(Finding("warning", "profile-visibility-wording",
                                "visibility should state that it is not used as an access control", where))
    if not findings:
        findings.append(Finding("info", "profile-ok", f"conformance profile for {data.get('implementation')!r} is complete", where))
    return findings
