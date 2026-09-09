"""Re-encode a Frame through the other encodings and compare element values."""

from . import io as frame_io


def diff_elements(before, after):
    keys = sorted(set(before) | set(after))
    return [(key, before.get(key), after.get(key)) for key in keys if before.get(key) != after.get(key)]


def round_trip(frame, profile, order=("json", "yaml", "markdown")):
    """Write and re-read through each encoding in order. Returns (final_frame, diffs, legs).

    legs is one (encoding, findings) pair per leg, in the order the legs ran, where a
    leg's findings are those of re-reading the document that leg's writer produced.
    They are what says whether the document this tool just wrote is one this tool can
    still read. Discarding them, as this function used to, reports a clean round trip
    for a trip whose own output does not parse: the element values still agree, because
    they are compared after the very parse that produced the findings.
    """
    current = frame
    legs = []
    for encoding in order:
        text = frame_io.WRITERS[encoding](current, profile)
        current, findings = frame_io.PARSERS[encoding](text, profile, frame.location)
        legs.append((encoding, list(findings or [])))
        if current is None:
            raise RuntimeError(f"round trip broke while reading the {encoding} encoding")
    return current, diff_elements(frame.elements, current.elements), legs
