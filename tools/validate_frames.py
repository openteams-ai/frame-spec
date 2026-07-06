#!/usr/bin/env python3
"""Validate example Frame files against the v0.2 minimum spec.

A Frame is a Markdown file with YAML frontmatter. The v0.2 spec requires
these frontmatter fields:

    type, name, description, visibility

This script checks, for each Frame it finds:

  1. The frontmatter block is present and properly closed.
  2. Each frontmatter line is a recognizable `key: value` pair, list item,
     comment, or blank line (a lightweight structural sanity check).
  3. All required fields are present and non-empty.
  4. The `type` field declares a Frame (it starts with "frame").

It is intended to keep example Frames from drifting out of sync with the
spec, for example when a new required field is added but the examples are
not updated.

This script uses only the Python standard library, so there is nothing to
install. Note the tradeoff: it does a lightweight structural check rather
than full YAML parsing, so it reliably catches missing or empty required
fields, but it will not catch every possible YAML syntax error.

Usage:

    python validate_frames.py                 # checks ./examples
    python validate_frames.py path/to/dir     # checks a directory
    python validate_frames.py a.md b.md        # checks specific files

Exit code is 0 if everything passes and 1 if any Frame fails, so this can
be wired into a GitHub Action later without changes.
"""

import argparse
import sys
from pathlib import Path

# Fields the v0.2 spec lists as required for every Frame.
REQUIRED_FIELDS = ["type", "name", "description", "visibility"]

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


def parse_frontmatter(fm_lines):
    """Parse simple top-level `key: value` frontmatter into a dict.

    Returns (data, problems). This is a lightweight parser, not a full YAML
    parser. It understands top-level scalar keys, list items under a key,
    comments, and blank lines, which covers the shape Frames use.
    """
    data = {}
    problems = []
    last_key = None

    for raw in fm_lines:
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

            data[key] = value if value != "" else None
            continue

        # Anything else is a line we cannot make sense of.
        problems.append(f"could not parse frontmatter line: {line.strip()}")

    return data, problems


def validate_frame(path):
    """Return a list of problem strings for one file. Empty list means valid."""
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

    data, problems = parse_frontmatter(fm_lines)

    for field in REQUIRED_FIELDS:
        if field not in data:
            problems.append(f"missing required field: {field}")
        elif data[field] is None or str(data[field]).strip() == "":
            problems.append(f"required field is empty: {field}")

    type_value = data.get("type")
    if type_value is not None and not str(type_value).strip().startswith("frame"):
        problems.append(
            f"type should declare a Frame (start with 'frame'), got: {type_value!r}"
        )

    return problems


def is_markdown(path):
    return path.suffix.lower() in {".md", ".markdown"}


def has_frontmatter(path):
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            first = handle.readline().strip()
        return first == "---"
    except OSError:
        return False


def collect_files(targets):
    """Turn the given paths (files or directories) into a sorted file list."""
    files = []
    for target in targets:
        path = Path(target)
        if path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file() and is_markdown(p))
        elif path.is_file():
            files.append(path)
        else:
            sys.stderr.write(f"warning: path not found, skipping: {target}\n")
    return sorted(set(files))


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate example Frame files against the v0.2 minimum spec."
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
        print("No Markdown files found to check.")
        return 0

    checked = 0
    failed = 0
    skipped = 0

    print(f"Checking {len(files)} Markdown file(s)...\n")

    for path in files:
        if not has_frontmatter(path):
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
