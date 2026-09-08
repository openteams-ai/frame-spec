"""The YAML (draft section 6.3) and JSON (section 6.4) encodings."""

import json

from . import markdown
from .findings import Finding
from .model import Frame, normalize

EXTRA_KEYS = ("type", "@context", "@type")


def parse_json(text, profile, location=None):
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return None, [Finding("error", "json-syntax", str(error), location)]
    if not isinstance(data, dict):
        return None, [Finding("error", "not-an-object", "the JSON encoding requires a single object", location)]
    return _from_mapping(data, "json", profile, location)


def parse_yaml(text, profile, location=None):
    try:
        import yaml
    except ImportError:
        return None, [Finding("error", "pyyaml-required",
                              "the YAML encoding cannot be read without PyYAML (pip install pyyaml)", location)]
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as error:
        return None, [Finding("error", "yaml-syntax", str(error), location)]
    if not isinstance(data, dict):
        return None, [Finding("error", "not-a-mapping", "the YAML encoding requires a single mapping", location)]
    return _from_mapping(data, "yaml", profile, location)


def _from_mapping(data, encoding, profile, location):
    findings, elements, extras = [], {}, {}
    for key, value in data.items():
        if key in EXTRA_KEYS:
            extras[key] = value
            findings.append(Finding("info", "encoding-key-preserved", f"{key!r} is an encoding-level key; preserved", location))
            continue
        elements[key] = value
    if "identifier" not in elements and location:
        elements["identifier"] = location
        extras[markdown.DEFAULTED] = True    # derived, not stated: writers must not emit it
        findings.append(Finding("info", "identifier-default", "identifier defaulted to the retrieval location", location))
    # Mandatory elements are not checked here: framespec.check owns that, driven by
    # the profile, so one absence is reported once rather than by every layer that notices.
    return Frame(normalize(elements, profile), encoding, location, extras), findings


def _to_mapping(frame, profile):
    # Reuse EXTRA_KEYS, the same set _from_mapping used to pull these out of the
    # elements, so an encoding-level key that was preserved into extras (an
    # optional "type" token, section 6.3, included) is actually written back
    # rather than dropped.
    out = {k: v for k, v in frame.extras.items() if k in EXTRA_KEYS}
    skip = {"identifier"} if frame.extras.get(markdown.DEFAULTED) else set()
    for name in profile.order:
        if name in frame.elements and name not in skip:
            out[name] = _compact(name, frame.elements[name])
    for name, value in frame.elements.items():
        if name not in out and name not in skip:
            out[name] = value
    return out


def _compact(name, value):
    if name == "guidance" and isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


def write_json(frame, profile):
    return json.dumps(_to_mapping(frame, profile), indent=2, ensure_ascii=False) + "\n"


def write_yaml(frame, profile):
    import yaml
    return yaml.safe_dump(_to_mapping(frame, profile), sort_keys=False, allow_unicode=True, default_flow_style=False)
