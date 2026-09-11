"""Re-encode a Frame through the other encodings and compare element values."""

from . import io as frame_io
from .findings import Finding


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
        read, findings = frame_io.PARSERS[encoding](text, profile, frame.location)
        findings = list(findings or [])
        if read is None:
            # The leg wrote a document its own reader does not take as a Frame, so
            # there is nothing to carry into the next leg. A parse error already says
            # why; a reader that skipped the document says nothing at all, since
            # (None, None) is how it reports someone else's file, so the leg needs a
            # finding of its own. It is returned rather than raised because the caller
            # reports findings and would crash on an exception.
            if not findings:
                findings.append(Finding(
                    "error", "wrote-a-non-frame",
                    f"the {encoding} writer produced a document that its own reader does "
                    "not read as a Frame, so the trip stopped here", frame.location))
            legs.append((encoding, findings))
            return None, [], legs
        current = read
        legs.append((encoding, findings))
    return current, diff_elements(frame.elements, current.elements), legs
