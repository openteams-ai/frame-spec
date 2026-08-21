# Changelog

This changelog tracks released versions of the Frame Spec.

Each released version is frozen as a snapshot in `spec/` (for example, [spec/v0.2.md](spec/v0.2.md)). The working draft between releases is [spec/frame-spec.md](spec/frame-spec.md); it is not normative until it is released.

## Unreleased — working draft toward v0.3

Working draft: [spec/frame-spec.md](spec/frame-spec.md). Not normative. The released spec is still `v0.2.0`.

### Changed

- **A Frame is now defined as metadata plus a body, not as a Markdown file.** `v0.2` defined the medium; the draft defines the shape and treats the medium as a separate question.
- **Markdown with YAML frontmatter is now the reference serialization** rather than the only one: the form to use when a Frame crosses a tool or organizational boundary and nothing else has been agreed.
- **Conformance is split three ways** — a Frame conforms by carrying the required fields in a conforming serialization; a serialization conforms if the required fields and body survive a round trip and `type` stays intact; an implementation conforms if it handles at least one conforming serialization and documents which.
- **Expected Agent Handling is no longer Markdown-specific**: detect a Frame by its `type` field, read the remaining fields as metadata, read the body as guidance, apply it.
- Body text is human-readable text with Markdown as a convention. An implementation must not reject a Frame because its body is not valid Markdown.

### Added

- **A YAML serialization**: metadata as keys of a top-level mapping, the body as the `body` key, conventionally a literal block scalar (`body: |`). The only defined serialization that carries the body as data while keeping it readable, since a block scalar needs no escaping.
- **A JSON serialization**: metadata as members of a top-level object, the body as the `body` string.
- A note on YAML's type coercion, which applies to frontmatter as much as to the YAML document form: every field the spec defines is a string, so authors should quote anything YAML would coerce (`version: "1.2"`, `visibility: "yes"`), and implementations should reject a wrongly typed field rather than stringifying it.
- **Machine-readable schemas** in [spec/schema/](spec/schema/README.md) — `frame-frontmatter.schema.json` for Markdown frontmatter, `frame-document.schema.json` for a whole YAML or JSON document. Two schemas for three serializations, because YAML and JSON parse into the same data model and duplicated normative files drift.
- A round-tripping rule: converting between conforming serializations must preserve the required fields and the body text.
- [examples/yaml-serialization/](examples/yaml-serialization/) and [examples/json-serialization/](examples/json-serialization/) — the `code-review-norms` Frame in each document form, unchanged in shape. Parse either and you get the same object; the YAML body matches the Markdown body character for character.
- `tools/validate_frames.py` now validates YAML and JSON Frames alongside Markdown ones, including block scalars in the lightweight YAML parser and JSON field types. Files whose `type` does not claim Frame-hood are skipped, so package manifests and CI config in the tree do not break the run.
- `tools/schema_check.py` — the fuller check: a real JSON Schema validator and a real YAML parser. Confirms both schemas are valid draft 2020-12 and validates every Frame against the right one. Catches what the lightweight check cannot, such as `version: 1.2` arriving as a number.
- CI gained a second job, `validate-schemas`, which installs `jsonschema` and `pyyaml` and runs the schema check. The existing job stays dependency-free, which keeps the standard-library promise honest.

### Compatibility

Every valid `v0.2` Frame remains valid. Required fields, recommended fields, `type` grammar, and inheritance semantics are unchanged, and the reference serialization is the form `v0.2` required. Nothing already written needs revising, and `type: frame [0.2]` stays a valid declaration. The change widens what counts as a Frame rather than narrowing it, which is why it is a minor version rather than a major one.

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
