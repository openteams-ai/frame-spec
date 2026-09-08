"""Validation findings. Only 'error' affects the exit code."""

from dataclasses import dataclass

LEVELS = ("error", "warning", "info")


@dataclass
class Finding:
    level: str
    code: str
    message: str
    location: str = None

    def __str__(self):
        where = f" ({self.location})" if self.location else ""
        return f"{self.level.upper():7} {self.code}: {self.message}{where}"


def has_errors(findings):
    return any(f.level == "error" for f in findings)
