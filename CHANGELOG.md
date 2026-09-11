# Changelog

This changelog tracks released versions of the Frame Spec.

Each released version is frozen as a snapshot in `spec/` (for example, [spec/v0.2.md](spec/v0.2.md)). The working draft between releases is [spec/frame-spec.md](spec/frame-spec.md); it is not normative until it is released.

## Unreleased

Working draft only; nothing here is normative until released.

- The working draft [spec/frame-spec.md](spec/frame-spec.md) now carries the proposed v0.3, written in the structure of an IETF Internet-Draft. It adds a data model independent of any encoding, a definition and obligation for every element (two mandatory: `identifier` and `guidance`), ten optional content refinements with a dumb-down rule, composition rules, a reference grammar, identity rules, `status`, `license`, `issued`, `canonicalSource`, `versionNotes`, `derivedFrom`, `previousVersion` and `guards` elements, YAML and JSON encodings, media types, conformance profiles, and security considerations. The v0.2 file format is preserved as the Markdown encoding and every valid v0.2 Frame is a valid v0.3 Frame. Of v0.2's four required front matter fields only `type` is required there, the other three being recommended, so compatibility runs backward and not forward.
- Added [spec/profile/frame-core.csv](spec/profile/frame-core.csv), the element set as a DCTAP-style machine-readable profile.
- Added [LICENSE](LICENSE): the repository is licensed under the Apache License, Version 2.0.

## v0.2.0 — 2026-08-18

First official release of the Frame Spec.

Frozen snapshot: [spec/v0.2.md](spec/v0.2.md)

### What v0.2 defines

- A Frame is a scoped, text-based artifact that carries cultural and operational context for work: a single Markdown file with YAML frontmatter.
- A conformance rule: a valid Frame is a Markdown file whose frontmatter carries the four required fields. Nothing else in the spec is required.
- Required frontmatter fields: `type`, `name`, `description`, `visibility`.
- Valid `type` forms: exactly `frame`, or `frame [<major>.<minor>]`. The bracketed token names the spec conformance family as `major.minor`; spec releases are three-part (for example `v0.2.0`), and patch releases never appear in the token.
- Recommended frontmatter fields: `version`, `scope`, `maintainer`, `inherits`.
- Inheritance semantics: explicit declaration via `inherits`, child takes precedence over parents, parents read in order, transitive resolution optional (implementations should disclose their behavior).
- Body content: free-form Markdown with no required or expected sections, kept concise because it is loaded as system context for AI assistants.
- Minimum expected agent handling: detect `type: frame`, read frontmatter as metadata, and apply the body as contextual guidance. Resolving `inherits` is recommended but not required for conformance, since it depends on how a tool stores and addresses Frames.

### What v0.2 intentionally does not define

- package manifests
- canonical identity
- provenance and source verification
- review workflows
- publication registries
- runtime management

### Pre-release history

Earlier drafts evolved inside this repository before the first release:

- **v0.1** — initial minimal adopt-now spec (Markdown file, YAML frontmatter, required fields).
- **v0.1.1** — added the `version` field and the optional bracketed spec-version syntax in `type` (at the time, `type: frame [0.1.1]`).
- **v0.2** — added inheritance (`inherits` field and semantics), body-conciseness guidance, and the trust note about loading Frames as system context.

These drafts were superseded by `v0.2.0` and were not released as snapshots. No Frames conforming to them were ever published, so implementations do not need to support pre-0.2 `type` tokens such as `frame [0.1.1]`.
