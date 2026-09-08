"""Load the element set from the DCTAP profile (spec/profile/frame-core.csv)."""

import csv
from dataclasses import dataclass
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = TOOLS_DIR.parent
DEFAULT_PROFILE_PATH = REPO_ROOT / "spec" / "profile" / "frame-core.csv"

# The model's content root that the ten refinements refine (draft section 4.4).
CONTENT_ROOT = "guidance"


@dataclass(frozen=True)
class ElementDef:
    name: str
    label: str
    mandatory: bool
    repeatable: bool
    node_type: str
    data_type: str
    constraint: str
    constraint_type: str
    maps_to: str
    refines: str
    note: str

    @property
    def picklist(self):
        """Registered values, when the constraint is a picklist. Recommended, not required."""
        if self.constraint_type == "picklist":
            return tuple(self.constraint.split())
        return ()

    @property
    def is_reference(self):
        """True when values are references classified by the frame-ref grammar."""
        return self.constraint_type == "pattern" and self.constraint == "frame-ref"


def _flag(value):
    return str(value).strip().lower() in ("true", "1", "yes")


class Profile:
    """The element set: one ElementDef per CSV row, in CSV order."""

    def __init__(self, elements):
        self.elements = {e.name: e for e in elements}
        self.order = [e.name for e in elements]
        if CONTENT_ROOT not in self.elements:
            raise ValueError(f"profile is missing the content root element {CONTENT_ROOT!r}")

    @classmethod
    def load(cls, path=DEFAULT_PROFILE_PATH):
        with open(path, newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        return cls([
            ElementDef(
                name=row["propertyID"],
                label=row["propertyLabel"],
                mandatory=_flag(row["mandatory"]),
                repeatable=_flag(row["repeatable"]),
                node_type=row["valueNodeType"],
                data_type=row["valueDataType"],
                constraint=row["valueConstraint"],
                constraint_type=row["valueConstraintType"],
                maps_to=row["mapsTo"],
                refines=row["refines"],
                note=row["note"],
            )
            for row in rows
        ])

    def mandatory(self):
        return [n for n in self.order if self.elements[n].mandatory]

    def refinements(self):
        return [self.elements[n] for n in self.order if self.elements[n].refines == CONTENT_ROOT]

    def labels(self):
        """Lower-cased Markdown heading label to element name, for the ten refinements."""
        return {e.label.lower(): e.name for e in self.refinements()}

    def is_repeatable(self, name):
        element = self.elements.get(name)
        return bool(element and element.repeatable)

    def content_elements(self):
        """guidance and the elements that refine it, in CSV order."""
        return [CONTENT_ROOT] + [e.name for e in self.refinements()]
