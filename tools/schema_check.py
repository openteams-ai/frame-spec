#!/usr/bin/env python3
"""Validate Frames against the JSON Schemas in `spec/schema/`.

This is the fuller counterpart to `validate_frames.py`. That script uses only
the standard library and does a lightweight structural check; this one runs a
real JSON Schema validator against a real YAML parser, so it catches what the
lightweight check cannot:

  * YAML type coercion. An unquoted `version: 1.2` is a number to a real
    parser, and every field the spec defines is a string.
  * Malformed YAML anywhere in a frontmatter block or document.
  * Field shapes beyond presence — an `inherits` list of the wrong item type,
    a `body` that is not a string.

It also checks that the schemas themselves are valid JSON Schema draft
2020-12, so a typo in a schema fails here rather than silently passing
everything.

Which schema applies is decided by serialization:

  * `.md` / `.markdown` — frontmatter is parsed and checked against
    `frame-frontmatter.schema.json`. The body is not covered, because the
    spec places no structural requirement on it.
  * `.yaml` / `.yml` / `.json` — the whole document is parsed and checked
    against `frame-document.schema.json`, which covers both because YAML and
    JSON parse into the same data model.

Requires two packages:

    python -m pip install jsonschema pyyaml

Usage:

    python tools/schema_check.py                 # checks ./examples
    python tools/schema_check.py path/to/dir     # checks a directory
    python tools/schema_check.py a.md b.yaml     # checks specific files

Exit code is 0 if everything passes and 1 if anything fails, so CI can call
it directly.
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import jsonschema
    import yaml
except ImportError as error:  # pragma: no cover - environment problem, not a Frame problem
    sys.stderr.write(
        f"error: {error.name} is required.\n"
        "       Install both dependencies with: python -m pip install jsonschema pyyaml\n"
    )
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO_ROOT / "spec" / "schema"
FRONTMATTER_SCHEMA = SCHEMA_DIR / "frame-frontmatter.schema.json"
DOCUMENT_SCHEMA = SCHEMA_DIR / "frame-document.schema.json"

DEFAULT_TARGET = REPO_ROOT / "examples"

MARKDOWN_SUFFIXES = {".md", ".markdown"}
YAML_SUFFIXES = {".yaml", ".yml"}
JSON_SUFFIXES = {".json"}


def load_schemas():
    """Load both schemas and confirm they are valid draft 2020-12."""
    schemas = {}
    for label, path in (("frontmatter", FRONTMATTER_SCHEMA), ("document", DOCUMENT_SCHEMA)):
        schema = json.loads(path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        schemas[label] = schema
    return schemas


def frontmatter_of(text):
    """Return the frontmatter block of a Markdown Frame, or None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index])
    return None


def claims_to_be_a_frame(value):
    return isinstance(value, str) and value.strip().lower().startswith("frame")


def parsed_frame(path):
    """Return (schema_label, data, error).

    `data` is None when the file does not claim to be a Frame and should be
    skipped. `error` is a string when the file claims Frame-hood but cannot be
    parsed at all.
    """
    suffix = path.suffix.lower()
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return None, None, f"could not read file: {error}"

    if suffix in MARKDOWN_SUFFIXES:
        block = frontmatter_of(text)
        if block is None:
            return None, None, None
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as error:
            return "frontmatter", None, f"frontmatter is not valid YAML: {error}"
        if not isinstance(data, dict):
            return "frontmatter", None, "frontmatter is not a mapping"
        return "frontmatter", data, None

    if suffix in YAML_SUFFIXES or suffix in JSON_SUFFIXES:
        loader = yaml.safe_load if suffix in YAML_SUFFIXES else json.loads
        try:
            data = loader(text)
        except (yaml.YAMLError, json.JSONDecodeError) as error:
            # Only complain if it looks like it was meant to be a Frame.
            if "type" in text and "frame" in text:
                return "document", None, f"could not parse: {error}"
            return None, None, None
        if not isinstance(data, dict) or not claims_to_be_a_frame(data.get("type")):
            return None, None, None
        return "document", data, None

    return None, None, None


def collect_files(targets):
    suffixes = MARKDOWN_SUFFIXES | YAML_SUFFIXES | JSON_SUFFIXES
    files = []
    for target in targets:
        path = Path(target)
        if path.is_dir():
            files.extend(
                p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in suffixes
            )
        elif path.is_file():
            files.append(path)
        else:
            sys.stderr.write(f"warning: path not found, skipping: {target}\n")
    return sorted(set(files))


def display_path(path):
    """Show a repo-relative path when the file is inside the repo, whether the
    caller passed a relative or an absolute path."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT)
    except ValueError:
        return path


def problems_for(schema, data):
    validator = jsonschema.Draft202012Validator(schema)
    problems = []
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        where = "/".join(str(part) for part in error.path) or "(root)"
        problems.append(f"{where}: {error.message}")
    return problems


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate Frames against the JSON Schemas in spec/schema/."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help=f"Files or directories to check (default: {DEFAULT_TARGET}).",
    )
    args = parser.parse_args(argv)

    schemas = load_schemas()
    print("Both schemas are valid JSON Schema draft 2020-12.\n")

    files = collect_files(args.paths or [DEFAULT_TARGET])
    checked = 0
    failed = 0
    skipped = 0

    for path in files:
        label, data, error = parsed_frame(path)
        shown = display_path(path)

        if label is None and error is None:
            skipped += 1
            continue

        checked += 1
        problems = [error] if error else problems_for(schemas[label], data)

        if problems:
            failed += 1
            print(f"FAIL  {shown}  [{label}]")
            for problem in problems:
                print(f"        - {problem}")
        else:
            print(f"OK    {shown}  [{label}]")

    print()
    print(
        f"Frames checked: {checked}   passed: {checked - failed}   "
        f"failed: {failed}   non-Frame files skipped: {skipped}"
    )

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
