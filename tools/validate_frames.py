#!/usr/bin/env python3
"""Validate Frame artifacts against the minimum spec.

A Frame is metadata plus a body. The spec requires these metadata fields:

    type, name, description, visibility

This script checks the three serializations the spec defines:

  * Markdown with YAML frontmatter (the reference serialization). Metadata is
    the frontmatter mapping; the body is everything after the closing `---`.
  * YAML. Metadata fields are keys of the top-level mapping; the body is the
    optional `body` key, conventionally a literal block scalar.
  * JSON. Metadata fields are members of the top-level object; the body is the
    optional `body` string.

For each Frame it finds, it checks:

  1. The metadata block is present and readable (frontmatter properly closed,
     or JSON that parses into an object).
  2. Each frontmatter line is a recognizable `key: value` pair, list item,
     comment, or blank line (a lightweight structural sanity check).
  3. All required fields are present and non-empty.
  4. The `type` field is a valid Frame declaration: exactly `frame`, or
     `frame [<major>.<minor>]` (for example `frame [0.2]`).
  5. For JSON Frames, that field values have the right JSON types.

It is intended to keep example Frames from drifting out of sync with the
spec, for example when a new required field is added but the examples are
not updated.

This script uses only the Python standard library, so there is nothing to
install. Note the tradeoff wherever YAML is involved — frontmatter and YAML
Frames alike: it does a lightweight structural check rather than full YAML
parsing, so it reliably catches missing or empty required fields, but it will
not catch every possible YAML syntax error, and it does not model YAML's type
coercion (an unquoted `version: 1.2` is a number to a real parser, and this
script sees text). `tools/schema_check.py` is the fuller check and does catch
those; it validates against the schemas in `spec/schema/` and needs
`jsonschema` and `pyyaml` installed.

Usage:

    python validate_frames.py                     # checks ./examples
    python validate_frames.py path/to/dir         # checks a directory
    python validate_frames.py a.md b.yaml c.json  # checks specific files

Exit code is 0 if everything passes and 1 if any Frame fails, so this can
be wired into a GitHub Action later without changes.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Fields the spec lists as required for every Frame.
REQUIRED_FIELDS = ["type", "name", "description", "visibility"]

# The only valid `type` values: `frame`, or `frame [<major>.<minor>]`.
# The bracketed token is the spec conformance family (major.minor only);
# patch-qualified tokens such as `frame [0.2.0]` are not valid.
TYPE_PATTERN = re.compile(r"^frame(?: \[\d+\.\d+\])?$")

# The default place to look when no path is given.
DEFAULT_TARGET = "examples"


def split_frontmatter(text):
    """Return (frontmatter_lines, error).

    Frontmatter is the block between the first two lines that contain only
    `---`. If the file does not start with `---`, frontmatter_lines is None
    and the caller treats the file as "not a Frame".
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index], None

    return None, "frontmatter opening '---' has no closing '---'"


# YAML block scalar indicators, with optional chomping and indentation hints
# (`|`, `|-`, `>2`, and so on). A Frame body written as `body: |` uses these.
BLOCK_SCALAR = re.compile(r"^[|>][+-]?\d*$|^[|>]\d*[+-]?$")


def parse_mapping(fm_lines):
    """Parse simple top-level `key: value` YAML into a dict.

    Returns (data, problems). This is a lightweight parser, not a full YAML
    parser. It understands top-level scalar keys, list items under a key,
    literal and folded block scalars, comments, and blank lines, which covers
    the shape Frames use — as frontmatter and as a whole YAML document.
    """
    data = {}
    problems = []
    last_key = None
    lines = list(fm_lines)
    index = 0

    while index < len(lines):
        raw = lines[index]
        index += 1
        line = raw.rstrip()

        # Blank lines and comments are fine.
        if line.strip() == "" or line.lstrip().startswith("#"):
            continue

        # A list item belongs to the most recent key (e.g. an `inherits` list).
        if line.lstrip().startswith("- "):
            if last_key is not None:
                existing = data.get(last_key)
                item = line.lstrip()[2:].strip()
                if isinstance(existing, list):
                    existing.append(item)
                else:
                    data[last_key] = [item]
            continue

        # Top-level key: value. Only treat a colon as a separator if the line
        # is not indented (indented lines are nested structure we don't model).
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            last_key = key

            # Light check: a value that opens a quote should also close it.
            for quote in ('"', "'"):
                if value.startswith(quote) and not value.endswith(quote):
                    problems.append(
                        f"value for '{key}' looks like an unterminated string: {value}"
                    )

            # A block scalar (`body: |`) owns every following line that is
            # indented under it. Consume them here so they are not mistaken
            # for unparseable lines, and keep the text as the key's value.
            if BLOCK_SCALAR.match(value):
                folded = value.startswith(">")
                block = []
                while index < len(lines):
                    nxt = lines[index]
                    if nxt.strip() == "":
                        block.append("")
                        index += 1
                        continue
                    if not nxt.startswith((" ", "\t")):
                        break
                    block.append(nxt.strip())
                    index += 1
                data[key] = (" " if folded else "\n").join(block).strip() or None
                continue

            data[key] = value if value != "" else None
            continue

        # Anything else is a line we cannot make sense of.
        problems.append(f"could not parse frontmatter line: {line.strip()}")

    return data, problems


# The frontmatter of a Markdown Frame is the same YAML shape as a whole YAML
# Frame, so both go through parse_mapping. The old name is kept as an alias.
parse_frontmatter = parse_mapping


def check_metadata(data):
    """Check required fields and the `type` grammar. Serialization-independent."""
    problems = []

    for field in REQUIRED_FIELDS:
        if field not in data:
            problems.append(f"missing required field: {field}")
        elif data[field] is None or str(data[field]).strip() == "":
            problems.append(f"required field is empty: {field}")

    type_value = data.get("type")
    if type_value is not None and not TYPE_PATTERN.match(str(type_value).strip()):
        problems.append(
            "type must be 'frame' or 'frame [<major>.<minor>]' "
            f"(for example 'frame [0.2]'), got: {type_value!r}"
        )

    return problems


def check_json_types(data):
    """Check JSON field types. Frontmatter values are always text, so this
    only applies to the JSON serialization, where a field can genuinely be a
    number, object, or something else the spec does not allow."""
    problems = []

    # `type` is left out: a non-string `type` already fails the grammar check
    # in check_metadata, with a more useful message than a type complaint.
    for field in REQUIRED_FIELDS:
        if field == "type":
            continue
        if field in data and not isinstance(data[field], str):
            problems.append(
                f"required field '{field}' must be a string, got "
                f"{type(data[field]).__name__}"
            )

    if "body" in data and not isinstance(data["body"], str):
        problems.append(
            f"'body' must be a string, got {type(data['body']).__name__}"
        )

    inherits = data.get("inherits")
    if inherits is not None:
        if isinstance(inherits, list):
            if not all(isinstance(item, str) and item.strip() for item in inherits):
                problems.append("'inherits' list entries must be non-empty strings")
        elif not isinstance(inherits, str):
            problems.append(
                "'inherits' must be a string or a list of strings, got "
                f"{type(inherits).__name__}"
            )

    return problems


def validate_markdown_frame(path):
    """Validate a Markdown Frame. Empty list means valid."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return [f"could not read file: {error}"]

    fm_lines, fm_error = split_frontmatter(text)

    if fm_error:
        return [fm_error]

    if fm_lines is None:
        # No frontmatter at all. Not a Frame, so nothing to validate.
        return []

    data, problems = parse_mapping(fm_lines)

    return problems + check_metadata(data)


def validate_yaml_frame(path):
    """Validate a whole-document YAML Frame. Empty list means valid."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return [f"could not read file: {error}"]

    lines = text.splitlines()

    # A leading `---` is a legal YAML document start. Skip it so a YAML Frame
    # that opens with one is not read as empty frontmatter.
    if lines and lines[0].strip() == "---":
        lines = lines[1:]

    data, problems = parse_mapping(lines)

    return problems + check_metadata(data)


def validate_json_frame(path):
    """Validate a JSON Frame. Empty list means valid."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return [f"could not read file: {error}"]

    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return [f"could not parse JSON: {error}"]

    if not isinstance(data, dict):
        return [f"a JSON Frame must be an object, got {type(data).__name__}"]

    return check_json_types(data) + check_metadata(data)


def validate_frame(path):
    """Return a list of problem strings for one file. Empty list means valid."""
    if is_json(path):
        return validate_json_frame(path)
    if is_yaml(path):
        return validate_yaml_frame(path)
    return validate_markdown_frame(path)


def is_markdown(path):
    return path.suffix.lower() in {".md", ".markdown"}


def is_json(path):
    return path.suffix.lower() == ".json"


def is_yaml(path):
    return path.suffix.lower() in {".yaml", ".yml"}


def has_frontmatter(path):
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            first = handle.readline().strip()
        return first == "---"
    except OSError:
        return False


def claims_to_be_a_frame(type_value):
    """True if a `type` value claims Frame-hood, well spelled or not.

    A misspelled claim such as 'framework' still counts, so the `type` grammar
    gets a chance to reject it instead of the file being silently skipped.
    """
    return isinstance(type_value, str) and type_value.strip().lower().startswith("frame")


def looks_like_json_frame(path):
    """A JSON file is treated as a Frame if it is an object whose `type` claims
    Frame-hood. Other JSON in the tree (package manifests, config) is skipped
    rather than failed."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False

    if not isinstance(data, dict):
        return False

    return claims_to_be_a_frame(data.get("type"))


def looks_like_yaml_frame(path):
    """A YAML file is treated as a Frame if a top-level `type` key claims
    Frame-hood. Package manifests and CI config are skipped rather than
    failed. This reads only the first few lines, so it stays cheap on a tree
    full of unrelated YAML."""
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            for _ in range(40):
                line = handle.readline()
                if line == "":
                    break
                if line.startswith((" ", "\t", "#")) or line.strip() in {"", "---"}:
                    continue
                key, sep, value = line.partition(":")
                if sep and key.strip() == "type":
                    return claims_to_be_a_frame(value.strip())
    except OSError:
        return False

    return False


def is_frame_candidate(path):
    """True if this file claims to be a Frame and should therefore be checked."""
    if is_markdown(path):
        return has_frontmatter(path)
    if is_json(path):
        return looks_like_json_frame(path)
    if is_yaml(path):
        return looks_like_yaml_frame(path)
    return False


def collect_files(targets):
    """Turn the given paths (files or directories) into a sorted file list."""
    files = []
    for target in targets:
        path = Path(target)
        if path.is_dir():
            files.extend(
                p
                for p in path.rglob("*")
                if p.is_file() and (is_markdown(p) or is_json(p) or is_yaml(p))
            )
        elif path.is_file():
            files.append(path)
        else:
            sys.stderr.write(f"warning: path not found, skipping: {target}\n")
    return sorted(set(files))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate Frame artifacts against the minimum spec."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=[DEFAULT_TARGET],
        help=f"Files or directories to check (default: {DEFAULT_TARGET}).",
    )
    args = parser.parse_args(argv)

    targets = args.paths if args.paths else [DEFAULT_TARGET]
    files = collect_files(targets)

    if not files:
        print("No Markdown, YAML, or JSON files found to check.")
        return 0

    checked = 0
    failed = 0
    skipped = 0

    print(f"Checking {len(files)} file(s)...\n")

    for path in files:
        if not is_frame_candidate(path):
            skipped += 1
            continue

        checked += 1
        problems = validate_frame(path)
        if problems:
            failed += 1
            print(f"FAIL  {path}")
            for problem in problems:
                print(f"        - {problem}")
        else:
            print(f"OK    {path}")

    print()
    print(
        f"Frames checked: {checked}   passed: {checked - failed}   "
        f"failed: {failed}   non-Frame files skipped: {skipped}"
    )

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
