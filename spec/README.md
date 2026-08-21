# Spec

This directory contains the released spec, the working draft, and room for more formal spec artifacts over time.

## Released Versions

Each release is frozen as a versioned snapshot that will not change after release:

- [v0.2.md](v0.2.md) — `v0.2.0`, the current release (2026-08-18)

Released snapshots are the normative reference for implementers. Changes between releases are recorded in the [changelog](../CHANGELOG.md).

## Working Draft

- [frame-spec.md](frame-spec.md) is the working draft of the spec.

At the moment of a release the working draft and the newest snapshot are identical. Between releases the working draft may drift ahead; edits to it are not normative until they land in a released snapshot.

The draft has now drifted ahead of `v0.2.0` in one substantive way: it defines a Frame as metadata plus a body rather than as a Markdown file, and treats Markdown with YAML frontmatter as the reference serialization alongside YAML and JSON. Because that widens what counts as a Frame instead of narrowing it, every valid `v0.2` Frame is still valid, and the draft targets `v0.3`.

## Schemas

- [schema/](schema/README.md) holds machine-readable schemas for the serializations the draft defines: one for the frontmatter of a Markdown Frame, one for a whole YAML or JSON document. Two schemas for three serializations, because YAML and JSON parse into the same data model.

They describe fields, types, and what is required — not body structure, which the spec deliberately leaves free-form. They are as normative as the draft they describe, which is to say not yet.

## Later

As the format stabilizes through real usage, this directory may also hold:

- richer human-readable specs
- validation examples
- conformance test fixtures

For future-facing discussion, see [../docs/future-directions.md](../docs/future-directions.md).
For a proposed enhancement-track process that separates exploratory ideas from active spec proposals, see [../docs/spec-enhancement-process.md](../docs/spec-enhancement-process.md).

Areas that now look important to formalize include:

- scope and inheritance
- canonical identity and authoritative-source metadata
- sharing and review semantics
- provenance and validation examples

The current spec intentionally stops short of committing to a final content schema because it still needs more real examples. The schemas in [schema/](schema/README.md) pin down the metadata fields only.
