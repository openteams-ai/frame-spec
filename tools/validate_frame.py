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
import csv
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
    parser.add_argument("--encoding", default="auto", choices=["auto", "markdown", "yaml", "json"],
                        help="how to read each path; auto reads it from the file extension")
    parser.add_argument("--profile", default=str(DEFAULT_PROFILE_PATH), help="path to frame-core.csv")
    parser.add_argument("--quiet", action="store_true", help="print only failures and the summary")
    parser.add_argument("--conformance-profile",
                        help="YAML or JSON conformance profile to apply while composing")
    # The modes are mutually exclusive, and argparse refuses a combination rather than
    # letting one silently override another: --round-trip --self-check ran the
    # self-check, --round-trip --compose ran compose, and --round-trip --check-profile
    # ran check-profile, each with the other flag doing nothing. The reason is the one
    # the --conformance-profile guard in main() gives, and it applies the same way
    # here: a flag that quietly did nothing would leave the user believing the run had
    # done what they asked when another mode ran instead. Plain validation is the fifth
    # mode and is what naming none of these does.
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--round-trip", action="store_true",
                       help="re-encode each Frame through json, yaml, and markdown and report differing elements")
    modes.add_argument("--self-check", action="store_true",
                       help="check spec/profile/frame-core.csv against the element definitions in "
                            "spec/frame-spec.md, and the draft's prose against the invariants of "
                            "framespec.speclint")
    modes.add_argument("--compose", action="store_true",
                       help="resolve composition over PATHS given lowest precedence first; print the result as JSON")
    modes.add_argument("--check-profile", action="store_true",
                       help="check the PATHS as conformance profiles (YAML or JSON) against Appendix C")
    return parser


def where_of(path):
    """The one location shape every finding in this tool reports: a file URI.

    framespec.io already reports a Frame's findings against Path.resolve().as_uri(),
    which is also the identifier a document that states none is given (draft section
    6.1). The modes whose findings are about a file rather than about a Frame use this
    too, so that one run does not spell the same file three ways: a URI from
    validation, an absolute path from --self-check, and the path as typed from
    --check-profile.
    """
    return Path(path).resolve().as_uri()


def report(status, path, lines, out=sys.stdout):
    """One path's outcome: a status header, then one indented line per finding.

    Every mode reports through here, so a finding sits in the same place in the output
    whichever mode produced it. lines are findings, or, for --round-trip's element
    comparison, the differences it found.
    """
    print(f"{status}  {path}", file=out)
    for line in lines:
        print(f"        - {line}", file=out)


def summarize(subject, checked, failed, skipped=None, out=sys.stdout):
    """The count line a path-scanning mode ends with.

    Without one, a run that scanned nothing looks exactly like a run in which
    everything passed. skipped is left off where no path can be skipped.
    """
    tail = "" if skipped is None else f"   skipped: {skipped}"
    print(f"\n{subject}: {checked}   passed: {checked - failed}   failed: {failed}{tail}", file=out)


def load_profile(path, out=sys.stderr):
    """The element set from a DCTAP CSV, or None with a finding printed.

    --profile was the one input to this tool that still produced a traceback: a path
    that is not there raised FileNotFoundError out of Profile.load(). Every other
    input on this tool reports a finding instead, so this one does too. A CSV whose
    header is missing a column raises KeyError from the row lookup and a binary file
    raises csv.Error; both are the same mistake as a missing path, which is that the
    file given is not the profile.

    Printed on stderr rather than stdout: this is the run's configuration failing
    rather than a finding about one of the paths being scanned, and --compose's stdout
    carries the resolved Frame alone.
    """
    try:
        return Profile.load(path)
    except (OSError, ValueError, KeyError, csv.Error) as error:
        report("FAIL", path,
               [Finding("error", "profile-unreadable", f"{type(error).__name__}: {error}", where_of(path))], out)
        return None


# The --round-trip statuses, padded to one width so the paths line up under each other.
GOOD_TRIP, DIFFERING_TRIP, FAILED_TRIP = "ROUND-TRIP OK     ", "ROUND-TRIP DIFFERS", "ROUND-TRIP FAIL   "


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
        report(label, path,
               [Finding("error", "path-not-found", "no such file or directory", where_of(path))], out)
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
            # Control reaches here only when `bad or not quiet` holds, so every finding
            # prints: the per-finding test this used to repeat filtered nothing. --quiet
            # suppresses a passing Frame's findings by suppressing the whole path, which
            # is what the flag's help text says it does.
            report("FAIL" if bad else "OK  ", path, findings, out)
    summarize("Frames checked", checked, failed, skipped, out)
    return 1 if failed else 0


def round_trip_paths(paths, encoding, profile, out=sys.stdout):
    """Re-encode each Frame through json, yaml, and markdown.

    A path fails when an element value changed on the way round or when any leg wrote
    a document that could not be read back without an error.
    """
    from framespec import roundtrip
    failures = report_missing(paths, FAILED_TRIP, out)
    checked, skipped = failures, 0
    for path in frame_io.collect(paths):
        enc = frame_io.detect_encoding(path, encoding)
        frame, findings = frame_io.read_frame(path, enc, profile) if enc else (None, None)
        if findings is None:
            skipped += 1
            continue          # not a Frame: read_frame already agreed to skip it
        checked += 1
        if frame is None:
            # findings is a non-empty list here: the file could not be read at
            # all (see read_frame's contract). Report it rather than silently
            # continuing, which would otherwise exit 0 having checked nothing.
            failures += 1
            report(FAILED_TRIP, path, findings, out)
            continue
        try:
            final, diffs, legs = roundtrip.round_trip(frame, profile)
        except ImportError as error:
            # The yaml leg needs PyYAML. Say so rather than raising a traceback.
            failures += 1
            report(FAILED_TRIP, path,
                   [Finding("error", "pyyaml-required", str(error), where_of(path))], out)
            continue
        # An error-level finding from any leg fails the trip: that leg wrote a document
        # this tool cannot read back, so the trip produced an invalid document however
        # well the element values compare afterward. The comparison runs on the Frame
        # the failing parse returned, which is why discarding these findings would
        # report OK for a trip whose Markdown leg actually failed. Only errors are
        # reported here; a leg's warnings and information are the same findings plain
        # validation already reports for the document itself, while an error is about
        # the trip.
        #
        # Section 6.2.1 once made four front matter keys REQUIRED in the Markdown
        # encoding while section 4.2 made only `identifier` and `guidance` mandatory at
        # the model layer, so a model-minimal Frame had no valid Markdown form and this
        # leg reported missing-required-key on every trip of one. The amendment that
        # made `name`, `description`, and `visibility` SHOULD rather than REQUIRED
        # closed that gap: only `type` is REQUIRED here now, so a model-minimal Frame
        # round-trips clean, with warnings rather than errors for the three it omits.
        # The check above stays, since a leg can still fail for other reasons.
        leg_errors = [(leg, f) for leg, leg_findings in legs for f in leg_findings if f.level == "error"]
        if leg_errors or diffs:
            failures += 1
            report(FAILED_TRIP if leg_errors else DIFFERING_TRIP, path,
                   [f"the {leg} leg: {finding}" for leg, finding in leg_errors] +
                   [f"{name}: {before!r} -> {after!r}" for name, before, after in diffs], out)
        else:
            report(GOOD_TRIP, path, [], out)
    summarize("Frames round-tripped", checked, failures, skipped, out)
    return 1 if failures else 0


def compose_paths(paths, encoding, profile, conformance_path=None, out=sys.stdout, err=sys.stderr):
    """Resolve composition over PATHS and print the resolved elements as JSON.

    The paths are the composed set in precedence order, lowest first (draft section 5.1
    rules 2 and 3, and section 5.4). This mode resolves no references, so a Frame's own
    composition element is reported rather than followed. stdout carries the resolved
    Frame and nothing else, so that CI can diff it against an expected file; that is
    also why this mode ends with no count line, where every path-scanning mode has one.
    """
    from framespec import compose as compose_mod
    conformance = None
    if conformance_path:
        # Before the Frames are read: a profile that cannot be read is the run failing,
        # and saying so first costs the user nothing.
        try:
            conformance = compose_mod.load_conformance(conformance_path)
        except ImportError as error:
            return _conformance_failure(conformance_path, "pyyaml-required",
                                        "a conformance profile written as YAML cannot be read "
                                        f"without PyYAML ({error})", err)
        except (OSError, ValueError) as error:
            # A missing file, a syntax error, or a declaration that cannot be read is a
            # finding like any other, not a traceback.
            return _conformance_failure(conformance_path, "conformance-profile-unreadable",
                                        str(error), err)
    frames = []
    for raw in paths:
        enc = frame_io.detect_encoding(raw, encoding)
        frame, findings = frame_io.read_frame(raw, enc, profile) if enc else (None, None)
        if frame is None:
            # A path that cannot be read is the whole composed set failing, not one
            # Frame missing from it: resolving the rest would answer a question the
            # user did not ask, with an exit code that said it went well.
            report("COMPOSE FAIL", raw, findings or [_not_a_frame(raw)], err)
            return 1
        frames.append((raw, frame))
    for raw, frame in frames:
        declared = frame.elements.get("composition") or []
        # Rule 7: a reader that resolves composition MUST NOT silently ignore a
        # reference it did not resolve. This mode resolves none.
        unresolved = [Finding("info", "composition-unresolved",
                              f"'composition' reference {reference!r} was not resolved; the composed "
                              "set is the paths given, lowest precedence first", where_of(raw))
                      for reference in (declared if isinstance(declared, list) else [declared])]
        if unresolved:
            report("COMPOSE NOTE", raw, unresolved, err)
    resolved = compose_mod.compose([frame for _, frame in frames], profile, conformance)
    print(json.dumps(resolved.elements, indent=2, sort_keys=True, ensure_ascii=False), file=out)
    return 0


def _conformance_failure(path, code, message, err):
    """Report an unusable conformance profile and fail the run."""
    report("COMPOSE FAIL", path, [Finding("error", code, message, where_of(path))], err)
    return 1


def _not_a_frame(raw):
    """Why a path yielded no Frame, as a finding."""
    path = Path(raw)
    where = where_of(path)
    if not path.exists():
        # The same code report_missing() uses, since it is the same mistake: a path that
        # is not there must not be reported as a file whose contents were the problem.
        return Finding("error", "path-not-found", "no such file or directory", where)
    if path.is_dir():
        return Finding("error", "not-a-frame",
                       "a directory: --compose takes the Frames of the composed set, in order", where)
    return Finding("error", "not-a-frame", "not a Frame, or not an encoding this tool reads", where)


def check_profile_paths(paths, profile, out=sys.stdout):
    """Check each path as a conformance profile (YAML or JSON) against Appendix C.

    Mirrors validate_paths() and round_trip_paths(): report_missing() catches a typo'd
    path before it reaches load_conformance(), and a path that exists but is not a
    readable profile (bad syntax, not a mapping, a narrowing that cannot be read, or a
    YAML profile with no PyYAML installed) is a finding here too, not an unhandled
    exception that would crash the run and print nothing for the paths after it.

    conformance.check_profile() itself is also called under a broad except, as defense
    in depth rather than a substitute for that module routing every value's shape
    through _as_list()/_as_name() before comparing it to a vocabulary: the routing is
    what turns a known bad shape into an accurate, specific finding, and this net
    exists only to catch whatever shape that routing does not yet anticipate, so a
    profile no one has written yet degrades to a finding here instead of a traceback.
    """
    from framespec import conformance
    from framespec.compose import load_conformance
    failures = report_missing(paths, "FAIL", out)
    checked = failures
    for raw in paths:
        path = Path(raw)
        if not (path.is_file() or path.is_dir()):
            continue      # already reported by report_missing above
        checked += 1
        where = where_of(raw)
        try:
            data = load_conformance(raw)
        except ImportError as error:
            failures += 1
            report("FAIL", raw, [Finding("error", "pyyaml-required", str(error), where)], out)
            continue
        except (OSError, ValueError) as error:
            failures += 1
            report("FAIL", raw, [Finding("error", "conformance-profile-unreadable", str(error), where)], out)
            continue
        try:
            findings = conformance.check_profile(data, profile, where)
        except Exception as error:  # noqa: BLE001 - deliberate: see the docstring's "defense in depth"
            failures += 1
            report("FAIL", raw, [Finding("error", "profile-check-failed",
                                         f"{type(error).__name__}: {error}", where)], out)
            continue
        bad = has_errors(findings)
        failures += bad
        report("FAIL" if bad else "OK  ", raw, findings, out)
    # No skipped count: a path here is either a conformance profile that checks or a
    # failure, so there is nothing this mode can skip.
    summarize("Profiles checked", checked, failures, out=out)
    return 1 if failures else 0


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.conformance_profile and not args.compose:
        # Above every mode, since only --compose reads this file: a flag that silently
        # did nothing would leave the user believing a narrowing had been applied to a
        # run that never read it, whichever mode ran instead.
        parser.error("--conformance-profile applies to --compose")
    # Each mode's own requirement about paths, together and before any file is opened,
    # so that a usage error names the mode rather than answering with the whole help
    # text, and so that a path the user asked about is refused rather than dropped,
    # which would leave a file unchecked with the exit code at 0 regardless.
    if args.self_check and args.paths:
        parser.error("--self-check takes no paths: it checks the specification, not a Frame")
    if args.compose and not args.paths:
        parser.error("--compose needs at least one path: the Frames of the composed set, "
                     "lowest precedence first")
    if args.check_profile and not args.paths:
        parser.error("--check-profile needs at least one path: the conformance profiles to check")
    if not args.paths and not args.self_check:
        parser.print_help()
        return 2
    profile = load_profile(args.profile)
    if profile is None:
        return 1
    if args.self_check:
        from framespec import selfcheck, speclint
        # One mode, two subjects: the element set against the profile, and the prose
        # against the invariants two review rounds found it breaking. Both are checks
        # of the specification rather than of a Frame, so both belong behind this flag.
        findings = selfcheck.self_check(profile_path=args.profile) + speclint.lint()
        bad = has_errors(findings)
        # Under a path header with the findings indented under it, like every other
        # mode. No count line: this mode scans no paths, it checks the draft against
        # the profile, and the one thing it would count is the elements the last
        # finding already names.
        report("FAIL" if bad else "OK  ", selfcheck.DEFAULT_SPEC_PATH, findings)
        return 1 if bad else 0
    if args.compose:
        return compose_paths(args.paths, args.encoding, profile, args.conformance_profile)
    if args.check_profile:
        return check_profile_paths(args.paths, profile)
    if args.round_trip:
        return round_trip_paths(args.paths, args.encoding, profile)
    return validate_paths(args.paths, args.encoding, profile, args.quiet)


if __name__ == "__main__":
    sys.exit(main())
