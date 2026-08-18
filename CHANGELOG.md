# Changelog

This changelog tracks released versions of the Frame Spec.

Each released version is frozen as a snapshot in `spec/` (for example, [spec/v0.2.md](spec/v0.2.md)). The working draft between releases is [spec/frame-spec.md](spec/frame-spec.md); it is not normative until it is released.

## v0.2.0 — 2026-08-18

First official release of the Frame Spec.

Frozen snapshot: [spec/v0.2.md](spec/v0.2.md)

### What v0.2 defines

- A Frame is a scoped, text-based artifact that carries cultural and operational context for work: a single Markdown file with YAML frontmatter.
- Required frontmatter fields: `type`, `name`, `description`, `visibility`.
- Recommended frontmatter fields: `version`, `scope`, `maintainer`, `inherits`.
- Inheritance semantics: explicit declaration via `inherits`, child takes precedence over parents, parents read in order, transitive resolution optional (implementations should disclose their behavior).
- Body content guidance: normal Markdown, kept concise, intended to be loaded as system context for AI assistants.
- Minimum expected agent handling: detect `type: frame`, read frontmatter as metadata, apply the body as contextual guidance, resolve declared parents.

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
- **v0.1.1** — added the `version` field and the optional bracketed spec-version syntax in `type` (for example, `type: frame [0.2]`).
- **v0.2** — added inheritance (`inherits` field and semantics), body-conciseness guidance, and the trust note about loading Frames as system context.

These drafts were superseded by `v0.2.0` and were not released as snapshots.
