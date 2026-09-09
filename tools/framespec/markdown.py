"""The Markdown encoding (draft section 6.2): v0.2's file format, read into the model."""

import re

from . import frontmatter
from .findings import Finding
from .model import Frame, default_identifier, derived_names, normalize

REQUIRED_KEYS = ("type",)
RECOMMENDED_KEYS = ("name", "description", "visibility")
ALIASES = {"name": "title", "inherits": "composition"}
REVERSE_ALIASES = {v: k for k, v in ALIASES.items()}
TYPE_RE = re.compile(r"^frame(?: \[\d+\.\d+\])?$")
TYPE_SENTINEL_RE = re.compile(r"^frame\b")
HEADING_RE = re.compile(r"^## (.+?)\s*$")
BULLET_RE = re.compile(r"^- (.*)$")
TERM_RE = re.compile(r"^- \*\*(.+?)\*\*:\s*(.*)$")


def parse(text, profile, location=None):
    """Parse a Markdown Frame. Returns (Frame or None, findings)."""
    findings = []
    try:
        fm_text, body = frontmatter.split(text)
    except ValueError as error:
        return None, [Finding("error", "front-matter", str(error), location)]
    try:
        fm, fallback = frontmatter.load_mapping(fm_text)
    except ValueError as error:
        return None, [Finding("error", "front-matter", str(error), location)]
    if fallback:
        findings.append(Finding("info", "yaml-fallback",
                                "PyYAML is not installed; front matter parsed with the line-based v0.2 parser",
                                location))
    for key in REQUIRED_KEYS:
        if fm.get(key) in (None, ""):
            findings.append(Finding("error", "missing-required-key",
                                    f"the Markdown encoding requires front matter key '{key}'", location))
    for key in RECOMMENDED_KEYS:
        if fm.get(key) in (None, ""):
            findings.append(Finding("warning", "missing-recommended-key",
                                    f"front matter key '{key}' is recommended but not present; "
                                    "the document is still a Frame", location))
    type_token = str(fm.get("type", "")).strip()
    if type_token and not TYPE_SENTINEL_RE.match(type_token):
        findings.append(Finding("error", "bad-type-token",
                                f"type must begin with the word 'frame', got {type_token!r}", location))
    elif type_token and not TYPE_RE.match(type_token):
        findings.append(Finding("warning", "nonstandard-type-version",
                                f"type {type_token!r} has a version token that is not '[<major>.<minor>]'; "
                                "accepted as a Frame", location))
    extras = {"type": type_token} if type_token else {}
    elements = {ALIASES.get(k, k): v for k, v in fm.items() if k != "type"}
    defaulted = default_identifier(elements, extras, location)
    if defaulted:
        findings.append(defaulted)
    guidance, sections = _split_body(body, profile)
    elements["guidance"] = guidance
    for name, values in sections.items():
        existing = elements.get(name)
        if existing is None:
            elements[name] = values
        else:
            elements[name] = (existing if isinstance(existing, list) else [existing]) + values
    return Frame(normalize(elements, profile), "markdown", location, extras), findings


def _split_body(body, profile):
    """One guidance string plus a values list per recognized refinement section."""
    labels = profile.labels()
    guidance_lines, sections, current, in_fence = [], {}, None, False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else HEADING_RE.match(line)
        if match:
            label = match.group(1).strip().lower()
            if label in labels:
                current = labels[label]
                sections.setdefault(current, [])
                continue
            current = None
        (sections[current] if current else guidance_lines).append(line)
    guidance = "\n".join(guidance_lines).strip("\n")
    return guidance, {name: _items(name, lines) for name, lines in sections.items()}


def _items(name, lines):
    """Top-level bullets are values; other paragraphs are values; terminology bullets may be concepts."""
    values, paragraph, in_fence = [], [], False

    def flush():
        if paragraph:
            values.append("\n".join(paragraph).strip())
            paragraph.clear()

    for line in lines:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            paragraph.append(line)
            continue
        if in_fence:                      # a bullet inside a fence is code, not a value
            paragraph.append(line)
            continue
        bullet = BULLET_RE.match(line)
        if bullet:
            flush()
            concept = TERM_RE.match(line)
            if name == "terminology" and concept:
                values.append({"term": concept.group(1), "definition": concept.group(2)})
            else:
                values.append(bullet.group(1).strip())
        elif line.strip() == "":
            flush()
        else:
            paragraph.append(line)
    flush()
    return values


def write(frame, profile, spec_version="0.3"):
    """Render a Frame in the Markdown encoding, v0.2-compatible front matter first."""
    content = set(profile.content_elements())
    fm = {"type": frame.extras.get("type") or f"frame [{spec_version}]"}
    skip = derived_names(frame)
    for name in profile.order:
        if name in content or name not in frame.elements or name in skip:
            continue
        fm[REVERSE_ALIASES.get(name, name)] = frame.elements[name]
    for name, value in frame.elements.items():
        if name not in profile.elements and name not in content:
            fm[name] = value
    parts = [f"---\n{frontmatter.dump_mapping(fm)}---\n"]
    guidance = frame.elements.get("guidance") or [""]
    parts.append("\n" + "\n\n".join(g for g in guidance if g) + "\n")
    for element in profile.refinements():
        values = frame.elements.get(element.name)
        if not values:
            continue
        parts.append(f"\n## {element.label}\n\n")
        for value in values:
            if isinstance(value, dict):
                parts.append(_concept(value))
            elif isinstance(value, str) and "\n" in value:
                parts.append(f"{value}\n\n")
            else:
                parts.append(f"- {value}\n")
    return "".join(parts)


def _concept(value):
    """One terminology bullet. Section 6.2.3 has no syntax for alternative labels,
    so section 4.4.1's dumb-down rule applies: keep the content, lose the structure."""
    line = f"- **{value.get('term', '')}**: {value.get('definition', '')}"
    extra = {k: v for k, v in value.items() if k not in ("term", "definition")}
    if extra:
        kept = "; ".join(f"{k}: {_flat(v)}" for k, v in sorted(extra.items()))
        line += f" ({kept})"
    return line + "\n"


def _flat(value):
    return ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)
