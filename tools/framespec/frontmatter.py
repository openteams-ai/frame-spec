"""Split and parse YAML front matter, with a PyYAML-free fallback."""

import json

# A line width no front matter scalar is expected to reach, so none are folded.
SCALAR_WIDTH = 1 << 20


def split(text):
    """Return (front_matter, body). Raise ValueError if the block is missing or unclosed."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("no front matter: the file does not start with '---'")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1:])
    raise ValueError("front matter opening '---' has no closing '---'")


def _unquote(value):
    if isinstance(value, str) and len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def load_mapping(text):
    """Parse front matter to a dict. Returns (mapping, used_fallback).

    With PyYAML installed this is a real YAML parse. Without it, the
    line-based parser from tools/validate_frames.py is used; it understands
    scalars and simple lists, which is the shape v0.2 Frames use.
    """
    try:
        import yaml
    except ImportError:
        from validate_frames import parse_frontmatter
        data, _problems = parse_frontmatter(text.splitlines())
        return {k: ([_unquote(i) for i in v] if isinstance(v, list) else _unquote(v))
                for k, v in data.items()}, True
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError as error:
        # Callers turn a ValueError into a finding, so a syntax error in the
        # front matter is reported rather than raised out of the parser.
        raise ValueError(f"front matter is not valid YAML: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("front matter is not a mapping")
    return data, False


def dump_mapping(mapping):
    """Serialize a flat mapping (scalars and lists of scalars) as YAML text."""
    try:
        import yaml
        # width keeps long scalars on one line: v0.2's line-based reader, which
        # is also the fallback below, cannot follow a folded continuation line.
        return yaml.safe_dump(mapping, sort_keys=False, allow_unicode=True,
                              default_flow_style=False, width=SCALAR_WIDTH)
    except ImportError:
        pass
    lines = []
    for key, value in mapping.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {_scalar(item)}" for item in value)
        else:
            lines.append(f"{key}: {_scalar(value)}")
    return "\n".join(lines) + "\n"


def _scalar(value):
    text = str(value)
    plain = text and text[0] not in "-?:,[]{}#&*!|>'\"%@`" and ": " not in text and " #" not in text \
        and text.lower() not in ("true", "false", "null", "yes", "no")
    return text if plain else json.dumps(text, ensure_ascii=False)
