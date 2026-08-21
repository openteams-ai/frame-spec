# Frame Spec — Working Draft (targets v0.3)

## Status

This is the working draft. It is **not normative**. The normative reference is the released snapshot, [v0.2.md](v0.2.md).

This draft makes one substantive change to `v0.2`: it separates the *shape* of a Frame from the *medium* a Frame is written in. `v0.2` defined a Frame as a Markdown file. This draft defines a Frame as metadata plus a body, and defines Markdown-with-frontmatter as one serialization of that shape — the recommended one — alongside YAML and JSON.

Because that widens what counts as a Frame rather than narrowing it, it is a minor-version change and targets `v0.3`. See [Relationship To v0.2](#relationship-to-v02).

## Purpose

This is the adopt-now definition of a Frame.

The goal is immediate use with just enough structure to support composition.

If someone can write a Frame today, share it, and layer it with other Frames so that context flows from broad to narrow scope, then the spec is doing its job.

## Definition

A Frame is a scoped, text-based artifact that carries cultural and operational context for work.

A Frame is:

- **structured**: a small set of named metadata fields plus a body of guidance
- human-readable
- usable by a Cog (a specialized, self-contained AI worker that performs discrete tasks, oriented by the Frames that apply to it) or another AI assistant
- easy to share manually

A Frame is not defined by its file format. Markdown with YAML frontmatter is the recommended way to write and exchange one, and is what most authors should use, but a Frame is the *shape* — not the medium that carries it.

## Conformance

There are three separate things that can conform.

### A Frame conforms if

- it carries the four required fields — `type`, `name`, `description`, and `visibility` — with non-empty values, and
- it is written in a serialization that satisfies the rules in [Serializations](#serializations)

Nothing else in this document is required. The recommended fields are optional, and the body is free-form with no required or expected structure. A Frame with the four required fields and a single paragraph of guidance is a valid Frame.

### A serialization conforms if

- the four required fields are recoverable by name, with their declared types
- the body is recoverable as text
- the `type` field survives, so the artifact stays self-identifying
- an implementation that knows the serialization can convert to and from the reference serialization without losing required fields or body text

### An implementation conforms if

- it can do the four things listed in [Expected Agent Handling](#expected-agent-handling), for at least one conforming serialization

An implementation must document which serializations it reads. Resolving `inherits` is recommended but not required.

### Conventions

- **must** marks a requirement. A Frame, serialization, or implementation that violates it does not conform.
- **should** marks a strong recommendation that may be set aside with good reason.
- **may** marks something entirely optional.

## Frame Shape

A Frame has exactly two parts:

1. **Metadata** — a map of named fields. Four are required; several more are recommended; authors may add their own.
2. **Body** — free-form text carrying the context the Frame exists to convey.

That is the whole data model. Everything else in this document either describes those fields, or describes how to write that shape down.

| Field | Type | Status | Notes |
| --- | --- | --- | --- |
| `type` | string | **required** | Exactly `frame`, or `frame [<major>.<minor>]` |
| `name` | string | **required** | Short human-readable name |
| `description` | string | **required** | One or two sentences on what it is for |
| `visibility` | string | **required** | Suggested values below; not a closed set |
| `version` | string | recommended | The Frame's own version, not the spec's |
| `scope` | string | recommended | Where the Frame applies |
| `maintainer` | string | recommended | Person, team, or organization |
| `inherits` | string, or array of strings | recommended | One or more parent Frames |
| body | text | optional | Free-form; no required structure |
| anything else | any | optional | Extension fields are permitted and ignored by conforming implementations that do not understand them |

The body is optional in the sense that an empty body still conforms. It is also the part that carries the value, so a Frame with an empty body is valid and pointless.

Machine-readable schemas for the defined serializations are in [schema/](schema/README.md).

## Serializations

A serialization is a way of writing the Frame shape down. This draft defines three, and permits others that meet the serialization conformance rules above.

### Markdown with YAML frontmatter (reference serialization)

- Metadata is a YAML mapping in frontmatter, delimited by `---` at the start of the file and `---` after the last field.
- The body is everything after the closing `---`.
- Conventional file name: `frame.md`. Conventional extension: `.md`.

This intentionally follows the general shape that Skills (reusable instruction files that give an AI assistant task-specific guidance) already use, without requiring the full Skills standard to define what a Frame is.

This is the **reference serialization**: when a Frame crosses a tool or organizational boundary, and nothing else has been agreed, write it this way. It is the form every conforming implementation should be able to read, and the form the rest of this document uses for examples.

### YAML

- Metadata fields are keys of a single top-level YAML mapping.
- The body is the value of the `body` key, a string. Authors should write it as a literal block scalar (`body: |`) so it stays readable and its line breaks are preserved verbatim.
- Conventional file name: `frame.yaml`.

YAML suits the places that already speak YAML — a CI configuration, a Helm value, a package manifest, a tool that reads its whole config as one YAML document. It is also the only defined serialization that carries the body as data *and* keeps it readable, since a block scalar needs no escaping.

One hazard is specific to YAML: an unquoted scalar is coerced by type. `version: 1.2` parses as a number, not the string `"1.2"`; `visibility: yes` parses as a boolean in YAML 1.1 parsers. Every field defined by this spec is a string, so authors should quote any value that YAML would otherwise coerce, and implementations should reject a field that arrives as the wrong type rather than stringifying it. The same hazard applies to frontmatter, which is also YAML.

### JSON

- Metadata fields are members of a single top-level JSON object.
- The body is the value of the `body` member, a string.
- Conventional file name: `frame.json`.

JSON exists for the cases where neither Markdown nor YAML is the right container: an API response, a database column, a Frame generated or consumed programmatically. The cost is the body, which becomes a single escaped string.

### Other serializations

A Frame may also be carried by any other format that satisfies the serialization conformance rules — a TOML file, a row in a table, a field in an existing config file, a record in a content system.

The spec does not enumerate these and does not need to. What it requires is that the required fields and the body survive the trip, and that `type` is among them so that whatever reads the artifact next can still tell it is a Frame.

Authors should not invent a serialization when one of the three defined ones will do. The reason to define the shape independently of the medium is not to encourage variety — it is so that a system which already has a place to put structured text does not have to pretend to be a filesystem in order to hold a Frame.

### Body Text Format

The body is human-readable text. Markdown formatting is conventional and is what implementations should assume when rendering, but no formatting is required and plain text is fine. An implementation must not reject a Frame because its body is not valid Markdown.

### Round-Tripping

Converting a Frame between conforming serializations must preserve the required fields and the body text. Extension fields and comments may be lost. Field order and whitespace may change.

The three defined serializations map onto each other directly: each frontmatter field becomes a key of the YAML mapping or a member of the JSON object, and the Markdown body becomes the `body` string. Only the body's presentation changes — a block scalar in YAML, an escaped string in JSON.

### Directory Form

The canonical form of a Frame is a single artifact.

Future versions may also support a directory form with a canonical entry file such as `frame.md`, `frame.yaml`, or `frame.json` plus optional supporting assets. That future shape is intentionally left open for later, since it is more closely tied to implementation and distribution concerns than to the minimum adopt-now definition.

## Required Fields

Every Frame must have `type`, `name`, `description`, and `visibility`.

### `type`

This must be:

```yaml
type: frame
```

or, to specify which version of the Frame Spec the Frame conforms to:

```yaml
type: frame [0.3]
```

This is the minimal explicit hook that tells an AI system or surrounding implementation that the artifact is intended to be handled as a Frame rather than as generic text. The bracketed spec version is optional but recommended.

These are the only two valid forms: `frame`, or `frame [<major>.<minor>]`.

The bracketed token names the spec conformance family as `major.minor`. Spec releases themselves are identified by three-part version numbers such as `v0.2.0`. Patch releases clarify wording without changing conformance requirements, so the patch component never appears in the `type` token: `frame [0.2]` declares conformance with any `v0.2.x` release, while `frame [0.2.0]` is not a valid value.

### `name`

Short human-readable name for the Frame.

### `description`

One or two sentences describing what the Frame is for and when it should be used.

### `visibility`

Suggested values:

- `private`
- `internal`
- `shared`
- `public`

## Recommended Fields

These are not required, but they are encouraged:

- `version`
- `scope`
- `maintainer`
- `inherits`

### `version`

The current version of this Frame.

```yaml
version: 0.1.0
```

This tracks the Frame's own revision history, not the spec version. Authors should update this when the content of the Frame changes.

`version` is suggested rather than required so people can start using Frames without first committing to a versioning scheme. When a Frame is expected to be shared, revised, or referenced over time, including `version` is strongly recommended.

### `scope`

A short description of where this Frame applies.

Examples:

- `company`
- `department`
- `project`
- `partner`
- `personal`

The spec does not require a formal scope grammar.

### `maintainer`

The person, team, or organization that maintains the Frame.

### `inherits`

One or more parent Frames that this Frame extends. May be a single value or a list.

```yaml
inherits: company-core
```

```yaml
inherits:
  - company-core
  - department-engineering
```

Values should be references that an implementation can resolve — typically a file path, a Frame name, or a URI. The spec does not require a specific resolution mechanism.

## Body Content

The body is free-form. The spec defines no required sections, no expected sections, and no section taxonomy at all.

The body should carry whatever context the Frame exists to convey. In practice that is often terminology, goals, rules, style guidance, norms, relevant skills, or business process notes — but those are examples of what some authors have found useful, not a checklist to work through. Most Frames need only one or two of them, and a Frame that carries a single rule well is a good Frame.

Frames are intended to be loaded as system context for AI assistants, where tokens are at a premium. Authors should keep body content concise: prefer short bullets over long prose, omit boilerplate, and include only the guidance that would actually change how work is done. A Frame that is too long to read quickly is too long to be useful.

## Inheritance

A Frame may declare that it inherits from one or more parent Frames using the `inherits` field.

### Semantics

1. Inheritance must be explicit. A Frame only inherits what it declares.
2. A child Frame extends its parents. All parent guidance applies unless the child overrides it.
3. The child takes precedence. Where parent and child guidance conflict, the child wins.
4. Parents are read in order. When multiple parents are listed, earlier entries have lower precedence than later entries. The child always has highest precedence.
5. Inheritance is not transitive by default. If A inherits B and B inherits C, an implementation may resolve the full chain, but is not required to.
6. Inheritance does not depend on serialization. A Frame may inherit from a parent written in a different serialization.

Because transitive resolution is optional, the same Frame may behave differently across tools. Implementations should disclose whether they resolve inheritance chains transitively, and authors should not rely on transitive resolution unless a specific tool guarantees it.

### What Inheritance Means In Practice

When a Frame with `inherits` is activated, an implementation should:

1. Resolve and load the parent Frame(s).
2. Present the combined guidance to the AI assistant, with the child's content taking precedence on any point of conflict.

The simplest valid implementation is concatenation: parent content first, then child content, with a note that later content overrides earlier content.

### Scope And Inheritance

Inheritance typically flows from broader to narrower scope:

- company → department → team → project

This is a convention, not a requirement. A Frame may inherit from any other Frame regardless of scope.

## Minimal Example

In the reference serialization:

```md
---
type: frame [0.3]
name: Editorial Style Guide
description: Shared guidance for clear, consistent external writing.
visibility: shared
---

# Editorial Style Guide

## Goals

- Be clear, direct, and credible.
- Avoid hype and overclaiming.

## Terminology

- Prefer "Frame" over "alignment file".

## Style

- Use calm, explanatory language.
- Make important assumptions explicit.
```

This example is intentionally minimal. It uses only the required fields.

## The Same Frame In YAML

```yaml
type: frame [0.3]
name: Editorial Style Guide
description: Shared guidance for clear, consistent external writing.
visibility: shared
body: |
  # Editorial Style Guide

  ## Goals

  - Be clear, direct, and credible.
  - Avoid hype and overclaiming.

  ## Terminology

  - Prefer "Frame" over "alignment file".

  ## Style

  - Use calm, explanatory language.
  - Make important assumptions explicit.
```

The same four fields, and a body that is still readable because the block scalar carries it without escaping. What changes from the Markdown form is that the body is now a *value* rather than the remainder of the file, which is what makes it addressable by a tool that reads the whole artifact as one mapping.

## The Same Frame In JSON

```json
{
  "type": "frame [0.3]",
  "name": "Editorial Style Guide",
  "description": "Shared guidance for clear, consistent external writing.",
  "visibility": "shared",
  "body": "# Editorial Style Guide\n\n## Goals\n\n- Be clear, direct, and credible.\n- Avoid hype and overclaiming.\n\n## Terminology\n\n- Prefer \"Frame\" over \"alignment file\".\n\n## Style\n\n- Use calm, explanatory language.\n- Make important assumptions explicit.\n"
}
```

This is the same Frame again. Same fields, same body, same meaning, different container. An implementation that reads more than one serialization must treat them identically.

Note what the JSON form costs: the body is a single escaped string, which is fine for a program and unpleasant for a person. That is why Markdown is the reference serialization and the document forms are alternatives, rather than the other way around.

## Example With Suggested Fields

```md
---
type: frame [0.3]
name: Engineering Documentation Style
description: Writing guidance for engineering documentation that extends a broader editorial style guide.
visibility: internal
version: 0.1.0
scope: department
maintainer: engineering enablement
inherits: editorial-style-guide
---

# Engineering Documentation Style

## Style

- Use precise technical language when writing for engineers.
- Keep the calm, direct tone from the broader editorial guidance.
- Code examples are preferred over abstract descriptions.
```

This example includes several suggested fields, including `version`, `scope`, `maintainer`, and `inherits`.

## Inheritance Example

In the example above, the engineering documentation Frame inherits the editorial style guide Frame. All parent guidance applies unless the child Frame overrides it. The child Frame narrows broad editorial guidance into conventions for engineering documentation.

## Relationship To v0.2

Every valid `v0.2` Frame is a valid Frame under this draft. The required fields are unchanged, the recommended fields are unchanged, the inheritance semantics are unchanged, and the reference serialization is the Markdown-with-frontmatter form that `v0.2` required. Nothing an author has already written needs to be revised, and `type: frame [0.2]` remains a valid declaration.

What changes:

| | `v0.2` | This draft |
| --- | --- | --- |
| What a Frame is | a Markdown file | metadata plus a body |
| Markdown with frontmatter | required | the reference serialization, recommended for interchange |
| YAML and JSON | undefined | defined serializations |
| Other formats | not conformant | conformant if the required fields and body survive |
| Implementation duty | read Markdown Frames | read at least one conforming serialization, and document which |

The practical effect for implementers is narrow: an implementation that reads Markdown Frames and says so already conforms. The effect for authors is that a Frame stored in a system with no filesystem — an app's database, an API payload, a config file — is now a Frame rather than an approximation of one.

## What This Draft Does Not Try To Define

It intentionally does not standardize:

- package manifests
- canonical identity
- provenance
- review workflows
- publication registries
- runtime management
- body structure or section taxonomy

Those may become part of later versions, but they should not block immediate use.

Note on trust: Because a Frame is loaded as system context, it can influence how an AI assistant behaves. Provenance and source verification are future-facing and are not defined here. Until they are, implementations and users should only load Frames from trusted sources and should not treat a Frame's contents as verified.

## Sharing

A Frame may be shared in any ordinary way, including:

- email
- chat
- git
- shared folders
- any system that can hold structured text

No special infrastructure is required. When sharing outside a context where the serialization has been agreed, use the reference serialization.

## Expected Agent Handling

An implementation must be able to:

1. Detect that an artifact is a Frame by reading its `type` field.
2. Read the remaining metadata fields as lightweight metadata.
3. Read the body as contextual guidance for work.
4. Apply that guidance when the Frame is made active by a user or system.

That is the whole requirement. An implementation that can do those four things for at least one conforming serialization, and documents which it reads, conforms.

Beyond that, an implementation should:

- read the reference serialization, since that is what authors reach for by default and what arrives from outside
- resolve parent Frames when `inherits` is present, combining their guidance with the child's

Resolving parents is a strong recommendation rather than a requirement, because it means locating other artifacts, which depends on how a given tool stores and addresses Frames. Implementations should disclose whether they resolve `inherits`, so authors know whether a layered set of Frames will behave as written.

The spec does not require more advanced behavior such as transitive inheritance resolution, provenance validation, or canonical-source lookup.

## Relationship To Future Work

This document is the working draft. The released spec is [v0.2.md](v0.2.md).

Future ideas such as richer identity, packaging, layering semantics, and application integration are tracked separately in the discussion docs.
