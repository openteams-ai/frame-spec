# Spec

This directory contains the released spec, the working draft, and room for more formal spec artifacts over time.

## Released Versions

Each release is frozen as a versioned snapshot that will not change after release:

- [v0.2.md](v0.2.md) — `v0.2.0`, the current release (2026-08-18)

Released snapshots are the normative reference for implementers. Changes between releases are recorded in the [changelog](../CHANGELOG.md).

## Working Draft

- [frame-spec.md](frame-spec.md) is the working draft of the spec.

At the moment of a release the working draft and the newest snapshot are identical. Between releases the working draft may drift ahead; edits to it are not normative until they land in a released snapshot.

The working draft currently carries the proposed **v0.3**. It is written in the structure of an IETF Internet-Draft and adds what v0.2 left undefined: a data model independent of any file format (Frame, Frame Version, Representation), a definition and obligation for every element, rules for how Frames compose, YAML and JSON encodings alongside the existing Markdown one, conformance profiles for implementations, and security considerations. The v0.2 file format is preserved as the Markdown encoding, and every valid v0.2 Frame remains valid. Appendix D of the draft lists the changes. The element set is also published as a machine-readable profile at [profile/frame-core.csv](profile/frame-core.csv).

## Later

As the format stabilizes through real usage, this directory may also hold:

- richer human-readable specs
- a machine-readable schema (a first form is [profile/frame-core.csv](profile/frame-core.csv))
- validation examples

For future-facing discussion, see [../docs/future-directions.md](../docs/future-directions.md).
For a proposed enhancement-track process that separates exploratory ideas from active spec proposals, see [../docs/spec-enhancement-process.md](../docs/spec-enhancement-process.md).

Of the areas identified earlier as important to formalize, the working draft addresses scope and inheritance (composition rules), canonical identity (`identifier`, `canonicalSource`), and provenance (`derivedFrom`, `previousVersion`), and publishes the element set as a profile. Still open after the draft: sharing semantics beyond a declared `visibility`, review workflow beyond a `status` value, validation examples, and a namespace for the Frame-native terms (see the draft's Appendix A).

The released spec intentionally stops short of committing to a final schema; the working draft is where that schema is being worked out.
