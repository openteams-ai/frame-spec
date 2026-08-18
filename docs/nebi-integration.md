# Nebi Integration

[Nebi](https://nebi.nebari.dev/) is an open-source, multi-user environment management tool led by OpenTeams: "git for environments," built on Pixi. Today Nebi manages computational environments; the plan is to expand it beyond environments, which could make it a natural packaging and distribution layer for Frames. Nebi does not currently define or ship Frame support — this note explores how it could.

## Position

Nebi is a potential mechanism for packaging, versioning, and distributing Frames.

It should not define the meaning of a Frame.

The intended boundary is:

- Frames are the semantic artifacts
- Nebi may carry and distribute them
- [Collab](https://openteams.com/collab/) may surface them for discovery, import, export, and sharing

## Why Nebi Is Attractive

Nebi already gives a useful set of primitives:

- package-like distribution
- versioning
- import and publish flows
- metadata extension points
- a pattern for human-readable spec plus machine-readable validation

That makes it a plausible vehicle for Frame packages.

## Extending Pixi Metadata

One pattern is to extend Nebi metadata through structured fields in `pixi.toml`.

A Frame package could follow a similar approach by declaring Frame metadata under a dedicated namespace.

Illustrative example:

```toml
[workspace]
name = "company-core-frame"
version = "0.1.0"
description = "Company-level Frame package for Acme"
channels = ["conda-forge"]
platforms = ["linux-64", "osx-arm64", "osx-64", "win-64"]

[dependencies]
python = ">=3.11"

[tool.nebi.frame]
spec-version = "0.2"

[tool.nebi.frame.acme.company-core]
name = "Acme Company Core Frame"
description = "Company-level Frame package with cultural and operational context."
author = { name = "Acme", email = "info@example.com" }
tags = ["frame", "company", "culture", "operations"]
root-scope = "company:acme"
default-format = "yaml"
frame-manifest = "frame/package.yaml"
sharing = "internal"
```

This is only an illustration of how Nebi metadata could point to Frame content.

## Suggested Relationship Between Files

```text
frame-package/
  pixi.toml
  frame/
    package.yaml
    company.yaml
  references/
    glossary.md
    rationale.md
```

Interpretation:

- `pixi.toml` carries Nebi-facing package metadata
- `frame/package.yaml` carries Frame package semantics
- `frame/*.yaml` carries scoped Frame documents
- `references/` carries supporting material

## Example Distribution Flow

One possible future flow:

1. Author Frame files in a package directory.
2. Add Nebi metadata in `pixi.toml`.
3. Validate the Frame manifest and documents.
4. Publish the package through Nebi-supported distribution.
5. Import it through Nebi or a Collab sharing flow.

## Caution

The Nebi contract for Frames is not yet settled.

That means:

- metadata field names may change
- a future Frame package might use `pixi.toml`, `nebi.toml`, or another wrapper shape
- examples should illustrate possibilities rather than freeze the contract too early

## Current Recommendation

Use Nebi examples to make the distribution story concrete, but keep the spec definition independent enough that another delivery system could carry the same Frame files later.
