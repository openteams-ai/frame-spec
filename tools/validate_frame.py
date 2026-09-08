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
import json
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
    parser.add_argument("--self-check", action="store_true",
                        help="check spec/profile/frame-core.csv against the element definitions in spec/frame-spec.md")
    parser.add_argument("--compose", action="store_true",
                        help="resolve composition over PATHS given lowest precedence first; print the result as JSON")
    parser.add_argument("--conformance-profile",
                        help="YAML or JSON conformance profile to apply while composing")
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


def compose_paths(paths, encoding, profile, conformance_path=None, out=sys.stdout, err=sys.stderr):
    """Resolve composition over PATHS and print the resolved elements as JSON.

    The paths are the composed set in precedence order, lowest first (draft section 5.1
    rules 2 and 3, and section 5.4). This mode resolves no references, so a Frame's own
    composition element is reported rather than followed. stdout carries the resolved
    Frame and nothing else, so that CI can diff it against an expected file.
    """
    from framespec import compose as compose_mod
    frames = []
    for raw in paths:
        enc = frame_io.detect_encoding(raw, encoding)
        frame, findings = frame_io.read_frame(raw, enc, profile) if enc else (None, None)
        if frame is None:
            # A path that cannot be read is the whole composed set failing, not one
            # Frame missing from it: resolving the rest would answer a question the
            # user did not ask, with an exit code that said it went well.
            print(f"COMPOSE FAIL  {raw}", file=err)
            for finding in findings or []:
                print(f"        - {finding}", file=err)
            if not findings:
                print(f"        - {_not_a_frame(raw)}", file=err)
            return 1
        frames.append((raw, frame))
    for raw, frame in frames:
        declared = frame.elements.get("composition") or []
        for reference in (declared if isinstance(declared, list) else [declared]):
            # Rule 7: a reader that resolves composition MUST NOT silently ignore a
            # reference it did not resolve. This mode resolves none.
            print(Finding("info", "composition-unresolved",
                          f"'composition' reference {reference!r} was not resolved; the composed "
                          "set is the paths given, lowest precedence first", str(raw)), file=err)
    conformance = compose_mod.load_conformance(conformance_path) if conformance_path else None
    resolved = compose_mod.compose([frame for _, frame in frames], profile, conformance)
    print(json.dumps(resolved.elements, indent=2, sort_keys=True, ensure_ascii=False), file=out)
    return 0


def _not_a_frame(raw):
    """Why a path that exists yielded no Frame, as a finding."""
    where = Path(raw).resolve().as_uri()
    if Path(raw).is_dir():
        return Finding("error", "not-a-frame",
                       "a directory: --compose takes the Frames of the composed set, in order", where)
    return Finding("error", "not-a-frame", "not a Frame, or not an encoding this tool reads", where)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_check:
        # Before the paths guard: this mode checks the specification itself and takes no paths.
        # Paths given anyway are refused rather than dropped, which would leave a
        # file the user asked about unchecked and the exit code at 0 regardless.
        if args.paths:
            parser.error("--self-check takes no paths: it checks the specification, not a Frame")
        from framespec import selfcheck
        findings = selfcheck.self_check(profile_path=args.profile)
        for finding in findings:
            print(finding)
        return 1 if has_errors(findings) else 0
    profile = Profile.load(args.profile)
    if args.conformance_profile and not args.compose:
        # A flag that silently did nothing would leave the user believing a narrowing
        # had been applied to a run that never read it.
        parser.error("--conformance-profile applies to --compose")
    if args.compose:
        # With the other modes, before the paths guard below, so that the usage error
        # names this mode rather than answering with the whole help text.
        if not args.paths:
            parser.error("--compose needs at least one path: the Frames of the composed set, "
                         "lowest precedence first")
        return compose_paths(args.paths, args.encoding, profile, args.conformance_profile)
    if not args.paths:
        parser.print_help()
        return 2
    if args.round_trip:
        return round_trip_paths(args.paths, args.encoding, profile)
    return validate_paths(args.paths, args.encoding, profile, args.quiet)


if __name__ == "__main__":
    sys.exit(main())
