"""The Markdown encoding (draft section 6.2): v0.2's file format, read into the model."""

import re

from . import frontmatter
from .findings import Finding
from .model import Frame, default_identifier, derived_names, normalize

REQUIRED_KEYS = ("type",)
RECOMMENDED_KEYS = ("name", "description", "visibility")
ALIASES = {"name": "title", "inherits": "composition"}
# The one refinement section 4.4.2 gives a structured form. Named here, not derived
# from the profile, because the profile records the element set and this is a fact
# about one element's definition; the CSV's note says the same in prose. Every other
# refinement's value is plain content, so a mapping under one is rendered as text.
STRUCTURED_FORM = "terminology"
REVERSE_ALIASES = {v: k for k, v in ALIASES.items()}
TYPE_RE = re.compile(r"^frame(?: \[\d+\.\d+\])?$")
TYPE_SENTINEL_RE = re.compile(r"^frame\b")
HEADING_RE = re.compile(r"^## (.+?)\s*$")
# Section 6.2.2: a list item may begin with a bullet marker, `-`, `*` or `+`, or an
# ordered-list marker, a number followed by `.` or `)`; the marker is not part of the
# value. This matches only an unindented marker followed by exactly one space, which is
# enough to serve that rule and to keep every marker's item shaped like the hyphen items
# the fixtures already use; it does not attempt CommonMark's fuller list-item syntax
# (a marker may be indented up to three spaces, and a run of markers of one kind versus
# another starts a new list), neither of which the rule depends on and neither of which
# this parser needs, since every item becomes its own value regardless of which list it
# would belong to under full CommonMark parsing.
BULLET_RE = re.compile(r"^(?:[-*+]|\d+[.)]) (.*)$")
# Section 6.2.3: the concept form is matched on the item's value, after BULLET_RE has
# already removed the marker, so this carries no marker of its own and applies the same
# way regardless of which of the five markers introduced the item.
TERM_RE = re.compile(r"^\*\*(.+?)\*\*:\s*(.*)$")


def parse(text, profile, location=None):
    """Parse a Markdown Frame. Returns (Frame or None, findings)."""
    findings = []
    try:
        fm_text, body = frontmatter.split(text)
    except ValueError as error:
        return None, [Finding("error", "front-matter", str(error), location)]
    try:
        fm, fallback, problems = frontmatter.load_mapping(fm_text)
    except ValueError as error:
        return None, [Finding("error", "front-matter", str(error), location)]
    if fallback:
        findings.append(Finding("info", "yaml-fallback",
                                "PyYAML is not installed; front matter parsed with the line-based v0.2 parser",
                                location))
    # A line the fallback parser could not read is a warning, not silence: without
    # this the parser's own complaints were discarded and the document looked clean.
    for problem in problems:
        findings.append(Finding("warning", "front-matter-not-fully-read", problem, location))
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
    for key, value in fm.items():
        if key != "type" and not _is_flat(value):
            findings.append(Finding("warning", "nested-front-matter-value",
                                    f"front matter key '{key}' carries a value with internal "
                                    "structure; this encoding defines front matter as scalars and "
                                    "sequences of scalars, so the value is preserved and no "
                                    "structured form is extracted from it", location))
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


def _is_flat(value):
    """Section 6.2.1: a front matter value MUST be a scalar or a sequence of scalars."""
    if isinstance(value, dict):
        return False
    if isinstance(value, list):
        return not any(isinstance(item, (dict, list)) for item in value)
    return True


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
    """Top-level list items are values; other paragraphs are values; terminology items may be concepts."""
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
        if in_fence:                      # a list marker inside a fence is code, not a value
            paragraph.append(line)
            continue
        bullet = BULLET_RE.match(line)
        if bullet:
            flush()
            value = bullet.group(1).strip()
            concept = TERM_RE.match(value) if name == "terminology" else None
            if concept:
                values.append({"term": concept.group(1), "definition": concept.group(2)})
            else:
                values.append(value)
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
            # The element name is not enough: nothing validates concept shape at read
            # time, so a `terminology` value may be a mapping with no `term`, and
            # _concept() would render it with empty bold markup, `- ****:  (foo: bar)`.
            if isinstance(value, dict) and element.name == STRUCTURED_FORM and "term" in value:
                parts.append(_concept(value))
            elif isinstance(value, dict):
                parts.append(f"- {_mapping_text(value)}\n")
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


def _mapping_text(value):
    """A mapping under a refinement that has no structured form, rendered as text.

    Section 4.4 gives only `terminology` a structured form, so a mapping here carries
    no term and no definition and must not be shaped like one: doing so emitted empty
    bold markup, `- ****:  (a: 1)`, which is malformed Markdown. The dumb-down rule of
    section 4.4.1 wants the content kept, which this does, and the structure lost.
    """
    return "; ".join(f"{key}: {_flat(item)}" for key, item in sorted(value.items()))


def _flat(value):
    return ", ".join(str(v) for v in value) if isinstance(value, list) else str(value)
