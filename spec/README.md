# Spec

This directory contains the released spec, the working draft, and room for more formal spec artifacts over time.

## Released Versions

Each release is frozen as a versioned snapshot that will not change after release:

- [v0.2.md](v0.2.md) — `v0.2.0`, the current release (2026-08-18)

Released snapshots are the normative reference for implementers. Changes between releases are recorded in the [changelog](../CHANGELOG.md).

## Working Draft

- [frame-spec.md](frame-spec.md) is the working draft of the spec.

At the moment of a release the working draft and the newest snapshot are identical. Between releases the working draft may drift ahead; edits to it are not normative until they land in a released snapshot.

## Later

As the format stabilizes through real usage, this directory may also hold:

- richer human-readable specs
- a machine-readable schema
- validation examples

For future-facing discussion, see [../docs/future-directions.md](../docs/future-directions.md).
For a proposed enhancement-track process that separates exploratory ideas from active spec proposals, see [../docs/spec-enhancement-process.md](../docs/spec-enhancement-process.md).

Areas that now look important to formalize include:

- scope and inheritance
- canonical identity and authoritative-source metadata
- sharing and review semantics
- provenance and validation examples

The current spec intentionally stops short of committing to a final schema because it still needs more real examples.
