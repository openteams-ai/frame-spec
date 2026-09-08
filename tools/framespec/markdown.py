"""The Markdown encoding (draft section 6.2): v0.2's file format, read into the model."""

import re

from . import frontmatter
from .findings import Finding
from .model import Frame, normalize

REQUIRED_KEYS = ("type", "name", "description", "visibility")
ALIASES = {"name": "title", "inherits": "composition"}
REVERSE_ALIASES = {v: k for k, v in ALIASES.items()}
TYPE_RE = re.compile(r"^frame(?: \[\d+\.\d+\])?$")
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
    type_token = str(fm.get("type", "")).strip()
    if type_token and not TYPE_RE.match(type_token):
        findings.append(Finding("error", "bad-type-token",
                                f"type must be 'frame' or 'frame [<major>.<minor>]', got {type_token!r}", location))
    extras = {"type": type_token} if type_token else {}
    elements = {ALIASES.get(k, k): v for k, v in fm.items() if k != "type"}
    if "identifier" not in elements and location:
        elements["identifier"] = location
        findings.append(Finding("info", "identifier-default", "identifier defaulted to the retrieval location", location))
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
    guidance_lines, sections, current = [], {}, None
    for line in body.splitlines():
        match = HEADING_RE.match(line)
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
    values, paragraph = [], []

    def flush():
        if paragraph:
            values.append("\n".join(paragraph).strip())
            paragraph.clear()

    for line in lines:
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
    for name in profile.order:
        if name in content or name not in frame.elements:
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
                parts.append(f"- **{value.get('term', '')}**: {value.get('definition', '')}\n")
            elif isinstance(value, str) and "\n" in value:
                parts.append(f"{value}\n\n")
            else:
                parts.append(f"- {value}\n")
    return "".join(parts)
