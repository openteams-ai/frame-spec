# Frame Spec

**Current release: [v0.2.0](https://github.com/openteams-ai/frame-spec/releases/tag/v0.2.0)** — frozen snapshot at [spec/v0.2.md](spec/v0.2.md), changes tracked in the [changelog](CHANGELOG.md).

Frames are scoped, text-based artifacts that carry the cultural and operational context within which work happens.

They are intended to be:

- readable by humans
- applied by any AI assistant, including Cogs (specialized, self-contained AI workers that perform discrete tasks, oriented by the Frames that apply to them — see [docs/ecosystem.md](docs/ecosystem.md))
- shareable across organizational boundaries when appropriate
- inheritable across scopes such as company, department, team, project, partner, or vendor
- first-class artifacts that can be authored, discovered, sold, and shared independently

This repository is the home of the Frame spec as its own standalone project.

## Start Here

If you want to use Frames in day-to-day AI work:

- Read [USING-FRAMES.md](USING-FRAMES.md) first.
- Browse [examples/](examples/README.md), starting with [examples/minimal/](examples/minimal/README.md) for the smallest concrete example.

If you want to implement or adopt the spec:

- Read [spec/v0.2.md](spec/v0.2.md), the released `v0.2.0` snapshot. It is the normative reference. ([spec/frame-spec.md](spec/frame-spec.md) is the working draft, which may drift ahead between releases.)

If you want background or future discussion:

- Read [docs/overview.md](docs/overview.md) for the concept and working definition.
- Read [docs/ecosystem.md](docs/ecosystem.md) for one-line definitions of the surrounding projects named in the discussion docs.
- Read [docs/future-directions.md](docs/future-directions.md) for the map of future and discussion documents.

## Author Or Adopt Frames

This is the fuller toolkit for people who are actively writing Frames.

- Read [spec/v0.2.md](spec/v0.2.md) for the released spec.
- Browse [examples/README.md](examples/README.md) for an index of all examples, grouped by whether they are canonical, illustrative, or future-facing.
- Open [tools/frame-builder.html](tools/frame-builder.html) for a simple offline builder that generates valid Frame Markdown.
- Use [tools/frame-authoring-assistant-prompt.md](tools/frame-authoring-assistant-prompt.md) when someone would rather create a Frame through an AI-guided conversation.
- Use [tools/customer-shared-frame-prompt.md](tools/customer-shared-frame-prompt.md) when creating a shared Frame between your organization and an external partner or customer.
- Use [share/frame-builder-kit/README.md](share/frame-builder-kit/README.md) for the standalone distribution copy of the builder.
- Run [tools/validate_frames.py](tools/validate_frames.py) as a preflight check that a Frame has the required v0.2 fields.

## Tools And Aids

This repo can include lightweight, spec-adjacent aids such as:

- offline builders
- prompt templates
- small authoring or validation skills
- lint and validation tools
- sample authoring workflows

These aids help people create or verify Frames. They do not define the full runtime or management system for Frames.

For the current boundary, read [docs/tools-and-aids.md](docs/tools-and-aids.md).

## Background

- Read [docs/overview.md](docs/overview.md) for the concept and current working definition.
- Read [docs/design-note.md](docs/design-note.md) for the problem framing and open questions.
- Read [docs/ecosystem.md](docs/ecosystem.md) for one-line definitions of the surrounding projects mentioned in the discussion docs (Cogs, Ops, Collab, Nebi, Intelligence Hub).

## Discussion And Future Work

- Read [docs/future-directions.md](docs/future-directions.md) for the map of future and discussion documents.
- Read [docs/spec-enhancement-process.md](docs/spec-enhancement-process.md) for a proposed lightweight process that separates exploratory ideas from active spec proposals.
- Read [docs/spec-and-implementation.md](docs/spec-and-implementation.md) for the boundary between the Frame spec and the systems that realize Frames.
- Read the Intelligence Hub whitepaper — published in its own repository and linked from [docs/ecosystem.md](docs/ecosystem.md) — for the broader architecture vision that informed the later spec alignment notes.
- Review [examples/self-frame/README.md](examples/self-frame/README.md) and [examples/nebi-frame-package/README.md](examples/nebi-frame-package/README.md) for richer future-oriented examples.

## Repository Layout

```text
spec/
  README.md
  frame-spec.md          # working draft
  v0.2.md                # released v0.2.0 snapshot (normative)
CHANGELOG.md
USING-FRAMES.md
examples/
  README.md              # index of all examples
  minimal/
  complete/
  minimal-self-frame/
  spec-stewardship-frame/
  sow-review/
  risk-identification-norms/
  meeting-notes-inheritance/
  self-frame/
  nebi-frame-package/
docs/
  overview.md
  ecosystem.md
  how-to-use-frames.md
  design-note.md
  tools-and-aids.md
  spec-and-implementation.md
  spec-enhancement-process.md
  future-directions.md
  spec-sketch.md
  canonical-identity-proposal.md
  domain-profiles-proposal.md
  frame-cog-op-boundary.md
  frame-to-cog-contract.md
  nebi-integration.md
  collab-sharing.md
  v1-gap-analysis.md
  early-onboarding-adoption-insights.md
tools/
  README.md
  frame-builder.html
  validate_frames.py
  frame-authoring-assistant-prompt.md
  customer-shared-frame-prompt.md
  frame-authoring-assistant/
  frame-reader/
share/
  frame-builder-kit/
```

## Current Status

The spec is early but released: `v0.2.0` is the first official release and is available for adoption now.

What exists now:

- a working concept and definition for Frames
- a small released spec that can be adopted immediately (`v0.2.0`, frozen at [spec/v0.2.md](spec/v0.2.md))
- a design note describing the problem and direction
- future-oriented spec discussion documents
- a packaging and distribution illustration
- concrete example Frame packages

What is intentionally not required for the current spec:

- a finalized schema
- a finalized Nebi packaging contract
- a built-in Collab sharing implementation
- settled governance for publication and discovery
- a standardized management or layering system

## Working Position On Nebi And Collab

Nebi (an open-source environment management tool led by OpenTeams) and Collab (OpenTeams' desktop app for private AI, with a hosted hub) are treated here as potential mechanisms, not as the semantic definition of a Frame. See [docs/ecosystem.md](docs/ecosystem.md) for fuller definitions and links.

The intended boundary is:

- Frames are the semantic artifacts
- Nebi may package, version, and distribute Frames as its scope expands beyond computational environments
- Collab applies Frames on the desktop and may become a discovery, import, export, and sharing surface for them through its hub
