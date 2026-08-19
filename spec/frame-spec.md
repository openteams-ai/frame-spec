# Frame Spec v0.2

## Purpose

This is the adopt-now definition of a Frame.

The goal of `v0.2` is immediate use with just enough structure to support composition.

If someone can write a Frame today, share it, and layer it with other Frames so that context flows from broad to narrow scope, then `v0.2` is doing its job.

## Definition

A Frame is a scoped, text-based artifact that carries cultural and operational context for work.


In `v0.2`, a Frame should be:

- a Markdown file
- human-readable
- usable by a Cog (a specialized, self-contained AI worker that performs discrete tasks, oriented by the Frames that apply to it) or another AI assistant
- easy to share manually

## Conformance

A file is a valid `v0.2` Frame if it is:

- a Markdown file, and
- its YAML frontmatter carries the four required fields: `type`, `name`, `description`, and `visibility`

Nothing else in this document is required. The recommended fields are optional, and the body is free-form Markdown with no required or expected structure. A Frame with the four required fields and a single paragraph of guidance is a valid Frame.

An implementation conforms to `v0.2` if it can do the four things listed in Expected Agent Handling, below. Resolving `inherits` is recommended but not required.

### Conventions

- **must** marks a requirement. A Frame or implementation that violates it does not conform to `v0.2`.
- **should** marks a strong recommendation that may be set aside with good reason.
- **may** marks something entirely optional.

## File Format

The preferred `v0.2` format is:

- Markdown body
- YAML frontmatter at the top

This intentionally follows the general shape that Skills (reusable instruction files that give an AI assistant task-specific guidance) already use, without requiring the full Skills standard to define what a Frame is.

In `v0.2`, the canonical form is a single Markdown file.

Future versions may also support a directory form with a canonical entry file such as `frame.md` plus optional supporting assets.

That future directory shape is intentionally left open for later, since it is more closely tied to implementation and distribution concerns than to the minimum adopt-now definition.

## Required Fields

Every `v0.2` Frame must have:

- `type`
- `name`
- `description`
- `visibility`

### `type`

This must be:

```yaml
type: frame
```

or, to specify which version of the Frame Spec the Frame conforms to:

```yaml
type: frame [0.2]
```

This is the minimal explicit hook that tells an AI system or surrounding implementation that the file is intended to be handled as a Frame rather than as generic Markdown. The bracketed spec version is optional but recommended.

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

These are not required in `v0.2`, but they are encouraged:

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

`version` is suggested rather than required in `v0.2` so people can start using Frames without first committing to a versioning scheme. When a Frame is expected to be shared, revised, or referenced over time, including `version` is strongly recommended.

### `scope`

A short description of where this Frame applies.

Examples:

- `company`
- `department`
- `project`
- `partner`
- `personal`

`v0.2` does not require a formal scope grammar.

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

After the frontmatter, the rest of the file is normal Markdown.

The body is free-form. `v0.2` defines no required sections, no expected sections, and no section taxonomy at all.

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

```md
---
type: frame [0.2]
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

This example is intentionally minimal. It uses only the fields required by `v0.2`.

## Example With Suggested Fields

```md
---
type: frame [0.2]
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

This example includes several suggested fields from `v0.2`, including `version`, `scope`, `maintainer`, and `inherits`.

## Inheritance Example

In the example above, the engineering documentation Frame inherits the editorial style guide Frame. All parent guidance applies unless the child Frame overrides it. The child Frame narrows broad editorial guidance into conventions for engineering documentation.

## What v0.2 Does Not Try To Define

`v0.2` intentionally does not standardize:

- package manifests
- canonical identity
- provenance
- review workflows
- publication registries
- runtime management

Those may become part of later versions, but they should not block immediate use. 

Note on trust: Because a Frame is loaded as system context, it can influence how an AI assistant behaves. Provenance and source verification are future-facing and are not defined in v0.2. Until they are, implementations and users should only load Frames from trusted sources and should not treat a Frame's contents as verified.

## Sharing

A `v0.2` Frame may be shared in any ordinary way, including:

- email
- chat
- git
- shared folders

No special infrastructure is required.

## Expected Agent Handling

An implementation must be able to:

1. Detect `type: frame` in the frontmatter.
2. Read the remaining frontmatter as lightweight metadata.
3. Read the Markdown body as contextual guidance for work.
4. Apply that guidance when the Frame is made active by a user or system.

That is the whole requirement. An implementation that can do those four things with a single Markdown file conforms to `v0.2`.

Beyond that, an implementation should resolve parent Frames when `inherits` is present, combining their guidance with the child's. This is a strong recommendation rather than a requirement, because resolving parents means locating other files, which depends on how a given tool stores and addresses Frames. Implementations should disclose whether they resolve `inherits`, so authors know whether a layered set of Frames will behave as written.

`v0.2` does not require more advanced behavior such as transitive inheritance resolution, provenance validation, or canonical-source lookup.

## Relationship To Future Work

This document is the current adopt-now spec.

Future ideas such as richer identity, packaging, layering semantics, and application integration are tracked separately in the discussion docs.
