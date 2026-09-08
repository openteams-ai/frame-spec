"""Encoding detection, file collection, and parser/writer dispatch."""

from pathlib import Path

from . import markdown, yamljson

PARSERS = {"markdown": markdown.parse, "yaml": yamljson.parse_yaml, "json": yamljson.parse_json}
WRITERS = {"markdown": markdown.write, "yaml": yamljson.write_yaml, "json": yamljson.write_json}
_BY_SUFFIX = {".md": "markdown", ".markdown": "markdown", ".yaml": "yaml", ".yml": "yaml", ".json": "json"}
_SCAN_SUFFIXES = (".md", ".markdown", ".frame.yaml", ".frame.yml", ".frame.json")


def detect_encoding(path, forced="auto"):
    if forced != "auto":
        return forced
    return _BY_SUFFIX.get(Path(path).suffix.lower())


def collect(paths):
    """Files to validate. Directories are scanned for the registered extensions."""
    files = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file() and p.name.lower().endswith(_SCAN_SUFFIXES))
        elif path.is_file():
            files.append(path)
    return sorted(set(files))


def read_frame(path, encoding, profile):
    """Parse one file. (None, None) means the file is not a Frame and was skipped."""
    text = Path(path).read_text(encoding="utf-8")
    if encoding == "markdown":
        first = text.splitlines()[0].strip() if text.strip() else ""
        if first != "---":          # the same rule tools/validate_frames.py applies
            return None, None
    parser = PARSERS.get(encoding)
    if parser is None:
        return None, None
    return parser(text, profile, Path(path).resolve().as_uri())
