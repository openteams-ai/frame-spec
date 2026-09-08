#!/usr/bin/env python3
"""Validate Frames against the v0.3 working draft (spec/frame-spec.md).

Reads the Markdown, YAML, and JSON encodings, normalizes each to the Frame
model, and checks it against spec/profile/frame-core.csv. Findings are
errors (exit 1), warnings, or info; the draft's preserve-rather-than-reject
rules mean most surprises are warnings.

Usage:
    validate_frame.py PATH [PATH ...] [--encoding auto|markdown|yaml|json]
                      [--profile CSV] [--quiet]

Directories are scanned for *.md, *.frame.yaml, *.frame.yml, and *.frame.json.
PyYAML is optional; without it Markdown front matter is parsed by the v0.2
line-based parser and the YAML encoding cannot be read.
"""

import argparse
import sys
from pathlib import Path

from framespec import check as check_mod
from framespec import io as frame_io
from framespec.findings import Finding, has_errors
from framespec.profile import DEFAULT_PROFILE_PATH, Profile


def build_parser():
    parser = argparse.ArgumentParser(description="Validate Frames against the v0.3 working draft.")
    parser.add_argument("paths", nargs="*", help="Frame files or directories")
    parser.add_argument("--encoding", default="auto", choices=["auto", "markdown", "yaml", "json"])
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE_PATH), help="path to frame-core.csv")
    parser.add_argument("--quiet", action="store_true", help="print only failures and the summary")
    parser.add_argument("--round-trip", action="store_true",
                        help="re-encode each Frame through json, yaml, and markdown and report differing elements")
    return parser


def report_missing(paths, label, out=sys.stdout):
    """Print one failure per path that is neither a file nor a directory, and count them.

    collect() drops such a path, so without this a typo would produce no finding
    and exit 0: a false green. Every mode that scans paths needs it.
    """
    missing = 0
    for raw in dict.fromkeys(paths):     # a repeated argument is one path, as collect() treats it
        path = Path(raw)
        if path.is_dir() or path.is_file():
            continue
        missing += 1
        where = path.resolve().as_uri()      # same location shape every other finding uses
        print(f"{label}  {path}", file=out)
        print(f"        - {Finding('error', 'path-not-found', 'no such file or directory', where)}", file=out)
    return missing


def validate_paths(paths, encoding, profile, quiet, out=sys.stdout):
    checked = failed = skipped = 0
    missing = report_missing(paths, "FAIL", out)
    checked += missing
    failed += missing
    for path in frame_io.collect(paths):
        enc = frame_io.detect_encoding(path, encoding)
        frame, findings = frame_io.read_frame(path, enc, profile) if enc else (None, None)
        if findings is None:
            skipped += 1
            continue
        checked += 1
        if frame is not None:
            findings = findings + check_mod.check(frame, profile)
        bad = has_errors(findings)
        failed += bad
        if bad or not quiet:
            print(f"{'FAIL' if bad else 'OK  '}  {path}", file=out)
            for finding in findings:
                if bad or finding.level != "info" or not quiet:
                    print(f"        - {finding}", file=out)
    print(f"\nFrames checked: {checked}   passed: {checked - failed}   failed: {failed}   skipped: {skipped}", file=out)
    return 1 if failed else 0


def round_trip_paths(paths, encoding, profile, out=sys.stdout):
    """Re-encode each Frame through json, yaml, and markdown; report differing elements."""
    from framespec import roundtrip
    failures = report_missing(paths, "ROUND-TRIP FAIL   ", out)
    for path in frame_io.collect(paths):
        enc = frame_io.detect_encoding(path, encoding)
        frame, findings = frame_io.read_frame(path, enc, profile) if enc else (None, None)
        if findings is None:
            continue          # not a Frame: read_frame already agreed to skip it
        if frame is None:
            # findings is a non-empty list here: the file could not be read at
            # all (see read_frame's contract). Report it rather than silently
            # continuing, which would otherwise exit 0 having checked nothing.
            failures += 1
            print(f"ROUND-TRIP FAIL     {path}", file=out)
            for finding in findings:
                print(f"        - {finding}", file=out)
            continue
        try:
            final, diffs = roundtrip.round_trip(frame, profile)
        except ImportError as error:
            # The yaml leg needs PyYAML. Say so rather than raising a traceback.
            failures += 1
            print(f"ROUND-TRIP FAIL     {path}", file=out)
            print(f"        - {Finding('error', 'pyyaml-required', str(error), str(path))}", file=out)
            continue
        if diffs:
            failures += 1
            print(f"ROUND-TRIP DIFFERS  {path}", file=out)
            for name, before, after in diffs:
                print(f"        - {name}: {before!r} -> {after!r}", file=out)
        else:
            print(f"ROUND-TRIP OK       {path}", file=out)
    return 1 if failures else 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    profile = Profile.load(args.profile)
    if not args.paths:
        build_parser().print_help()
        return 2
    if args.round_trip:
        return round_trip_paths(args.paths, args.encoding, profile)
    return validate_paths(args.paths, args.encoding, profile, args.quiet)


if __name__ == "__main__":
    sys.exit(main())
