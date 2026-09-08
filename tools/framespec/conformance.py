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
    """A field's value as a list of names.

    A shape that cannot be a list of names becomes one unusable name, so the caller's
    own vocabulary check reports it as an ordinary finding. Nothing here may return a
    value that is not a string: every call site tests membership against a set or a
    dict's keys, and an unhashable value (a list, a set, a dict) would crash there
    rather than produce a finding, whether it arrives as the field's own value
    (reference_forms: no, which YAML reads as the bool False, extending Appendix C's
    own "Resolves composition: no" wording to a list field) or buried inside an
    already-list-shaped one (reference_forms: [[pinned-ref]], a block list item that is
    itself a flow list). A bare scalar remains the shorthand framespec.compose._names()
    already accepts for non_repeatable and the two rule6_narrowings keys; a string is
    one name, not an iterable of characters, so it is wrapped rather than iterated.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return [v if isinstance(v, str) else repr(v) for v in value]
    return [repr(value)]


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
            if name not in profile.elements:
                # Distinct from "not repeatable": this name is not one of the model's
                # elements at all, so "names non-repeatable element" would misdescribe a
                # name that does not exist as one that exists but does not qualify.
                # additionally_required already gets this distinction right; this makes
                # rule6_narrowings consistent with it.
                findings.append(Finding("error", "profile-unknown-element",
                                        f"rule6_narrowings.{key} names unknown element '{name}'", where))
            elif not profile.is_repeatable(name):
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
