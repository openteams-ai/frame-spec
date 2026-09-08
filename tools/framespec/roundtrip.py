"""Re-encode a Frame through the other encodings and compare element values."""

from . import io as frame_io


def diff_elements(before, after):
    keys = sorted(set(before) | set(after))
    return [(key, before.get(key), after.get(key)) for key in keys if before.get(key) != after.get(key)]


def round_trip(frame, profile, order=("json", "yaml", "markdown")):
    """Write and re-read through each encoding in order. Returns (final_frame, diffs)."""
    current = frame
    for encoding in order:
        text = frame_io.WRITERS[encoding](current, profile)
        current, _findings = frame_io.PARSERS[encoding](text, profile, frame.location)
        if current is None:
            raise RuntimeError(f"round trip broke while reading the {encoding} encoding")
    return current, diff_elements(frame.elements, current.elements)
