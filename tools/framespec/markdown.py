"""The Markdown encoding (draft section 6.2): v0.2's file format, read into the model."""

import re

from . import frontmatter
from .findings import Finding
from .model import Frame, default_identifier, derived_names, normalize

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
HEADING_RE = re.compile(r"^(#{1,2}) (.+?)\s*$")
# Section 6.2.2: a list item may begin with a bullet marker, `-`, `*` or `+`, or an
# ordered-list marker, a number followed by `.` or `)`; the marker is not part of the
# value. This matches only an unindented marker followed by exactly one space, which is
# enough to serve that rule and to keep every marker's item shaped like the hyphen items
# the fixtures already use; it does not attempt CommonMark's fuller list-item syntax
# (a marker may be indented up to three spaces, and a run of markers of one kind versus
# another starts a new list), neither of which the rule depends on and neither of which
# this parser needs, since every item becomes its own value regardless of which list it
# would belong to under full CommonMark parsing.
# A marker with no text after it is an empty list item under CommonMark, and rule 6
# of section 5.1 makes an empty value meaningful, so it is a value like any other.
BULLET_RE = re.compile(r"^(?:[-*+]|\d+[.)])(?: (.*))?$")
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
    except frontmatter.NotAMapping:
        # Section 3.3: a file whose front matter is not a YAML mapping is not a
        # document of this encoding. Not a Frame in error, so there is nothing to
        # report; the caller skips it the way it skips a file with no front matter.
        return None, None
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
    # The sentinel decides whether there is a Frame here at all, so it is settled
    # before anything else is judged. Section 3.3 names three ways a file can be
    # someone else's rather than a Frame in error: front matter that is not a mapping,
    # handled above; no `type` key; and a `type` whose value does not begin with the
    # word `frame`. (None, None) is io.read_frame's contract for a file the caller
    # skips. Reporting any of the three as an error is the defect the sentinel exists
    # to prevent: a reader pointed at a directory reported a broken Frame for every
    # Jekyll post and every Skill file in it.
    type_value = fm.get("type")
    type_token = "" if type_value is None else str(type_value).strip()
    if not TYPE_SENTINEL_RE.match(type_token):
        return None, None
    if not TYPE_RE.match(type_token):
        findings.append(Finding("warning", "nonstandard-type-version",
                                f"type {type_token!r} has a version token that is not '[<major>.<minor>]'; "
                                "accepted as a Frame", location))
    for key in RECOMMENDED_KEYS:
        if fm.get(key) in (None, ""):
            findings.append(Finding("warning", "missing-recommended-key",
                                    f"front matter key '{key}' is recommended but not present; "
                                    "the document is still a Frame", location))
    for key, value in fm.items():
        if key != "type" and not _is_flat(value):
            findings.append(Finding("warning", "nested-front-matter-value",
                                    f"front matter key '{key}' carries a value with internal "
                                    "structure; this encoding defines front matter as scalars and "
                                    "sequences of scalars, so the value is preserved and no "
                                    "structured form is extracted from it", location))
    extras = {"type": type_token} if type_token else {}
    # Section 6.2.1: where a document carries both spellings of an aliased key, the
    # aliased spelling is the one that applies. A comprehension let dict insertion
    # order decide instead, so `name` won or `title` won depending on which the
    # author wrote second, and neither reader warned.
    elements, both = {}, []
    for key, value in fm.items():
        if key == "type":
            continue
        name = ALIASES.get(key, key)
        if name in elements:
            both.append(name)
            if key not in ALIASES:              # the non-aliased spelling loses
                continue
        elements[name] = value
    for name in both:
        findings.append(Finding("warning", "both-spellings",
                                f"front matter carries both spellings of '{name}' "
                                f"('{REVERSE_ALIASES[name]}' and '{name}'); the aliased spelling "
                                "applies and the other value is not used", location))
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
            level, label = match.group(1), match.group(2).strip().lower()
            if level == "##" and label in labels:
                current = labels[label]
                sections.setdefault(current, [])
                continue
            # Section 6.2.2: a section extends to the next heading of level 2 or
            # shallower, so a level 1 heading ends one too. Without that, `## Rules`
            # followed by `# Appendix` read the appendix as rules values and the
            # writer re-emitted the appendix as a bullet under Rules.
            current = None
        (sections[current] if current else guidance_lines).append(line)
    guidance = "\n".join(guidance_lines).strip("\n")
    return guidance, {name: _items(name, lines) for name, lines in sections.items()}


def _items(name, lines):
    """Top-level list items are values; other paragraphs are values; terminology items may be concepts.

    A list item's continuation blocks belong to the item. Section 6.2.2 takes its block
    and list terms from CommonMark, where an indented block following a list item is part
    of that item, so

        - First para.

          Second para.

    is one item and therefore one value. Reading the indented block as a separate
    top-level block split it into two, which two independent implementations built from
    the specification both got right and this one got wrong.
    """
    values, paragraph, in_fence = [], [], False
    item, item_blank = None, False        # the open list item, and a pending blank line

    def flush():
        nonlocal item, item_blank
        if item is not None:
            values.append(_value(name, "\n".join(item).strip()))
            item, item_blank = None, False
        if paragraph:
            values.append("\n".join(paragraph).strip())
            paragraph.clear()

    for line in lines:
        indented = line[:1] in (" ", "\t")
        if not in_fence and line.lstrip().startswith("```"):
            # An unindented fence is a new top-level block even after a list item, so
            # the open item ends here. An indented one is the item's own content.
            if item is not None and not indented:
                flush()
            in_fence = True
            if item is not None:
                if item_blank:
                    item.append("")
                    item_blank = False
                item.append(line.strip())
            else:
                paragraph.append(line)
            continue
        if in_fence:                      # a list marker inside a fence is code, not a value
            if line.lstrip().startswith("```"):
                in_fence = False
            (item if item is not None else paragraph).append(
                line.strip() if item is not None else line)
            continue
        bullet = BULLET_RE.match(line)
        if bullet:
            flush()
            item = [bullet.group(1) or ""]
            continue
        if line.strip() == "":
            if item is not None:
                item_blank = True         # may be a loose item; the next line decides
            else:
                flush()
            continue
        if item is not None and line[:1] in (" ", "\t"):
            if item_blank:
                item.append("")
                item_blank = False
            item.append(line.strip())
            continue
        flush()
        paragraph.append(line)
    flush()
    return values


def _value(name, text):
    """A list item's value: a concept where terminology's item form matches, else the text."""
    concept = TERM_RE.match(text) if name == "terminology" else None
    if concept:
        return {"term": concept.group(1), "definition": concept.group(2)}
    return text


def write(frame, profile):
    """Render a Frame in the Markdown encoding, v0.2-compatible front matter first.

    Section 6.3: a writer preserves a version token the source document carried and
    MUST NOT invent one for a document that carried none. This encoding requires the
    `type` key ([Section 6.2.1](#md-structure)), so a source with no token yields the
    bare sentinel, `type: frame`, rather than this specification's own version. Writing
    a version the source never claimed would record the converting tool's version as
    the document's own.
    """
    content = set(profile.content_elements())
    fm = {"type": frame.extras.get("type") or "frame"}
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
            elif isinstance(value, str) and "\n\n" in value:
                # A value of several blocks goes in one list item with its
                # continuation indented, which CommonMark keeps as one item and so
                # one value. Emitted as bare blocks it comes back as several values,
                # which is what this writer used to do and what an independent
                # implementation built from the specification got right.
                blocks = [b.strip() for b in value.split("\n\n") if b.strip()]
                parts.append(f"- {blocks[0]}\n")
                for block in blocks[1:]:
                    body = "\n".join(f"  {line}" for line in block.splitlines())
                    parts.append(f"\n{body}\n")
                parts.append("\n")
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
