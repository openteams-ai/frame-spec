# Frame Spec

**Current release: [v0.2.0](https://github.com/openteams-ai/frame-spec/releases/tag/v0.2.0)** — frozen snapshot at [spec/v0.2.md](spec/v0.2.md), changes tracked in the [changelog](CHANGELOG.md).

Frames are scoped, text-based artifacts that carry the cultural and operational context within which work happens.

They are intended to be:

- readable by humans
- applied by Cogs (specialized, self-contained AI workers that perform discrete tasks, oriented by the Frames that apply to them)
- shareable across organizational boundaries when appropriate
- inheritable across scopes such as company, department, team, project, partner, or vendor
- first-class artifacts that can be authored, discovered, sold, and shared independently

This repository seed is a standalone starting point for the Frame spec as its own project.

## Start Here

If you want to use Frames in day-to-day AI work:

- Read [USING-FRAMES.md](USING-FRAMES.md) first.
- Review [examples/minimal/README.md](examples/minimal/README.md) and [examples/minimal/frame.md](examples/minimal/frame.md) for the smallest concrete example.
- Review [examples/complete/README.md](examples/complete/README.md) and [examples/complete/frame.md](examples/complete/frame.md) for a fuller example with suggested metadata.

If you want to create, validate, or evolve Frames:

- Read [spec/frame-spec.md](spec/frame-spec.md) for the current minimum adopt-now spec.
- Open [tools/frame-builder.html](tools/frame-builder.html) for a simple offline builder that generates valid Frame Markdown.

If you want background or future discussion:

- Read [docs/overview.md](docs/overview.md) for the concept and working definition.
- Read [docs/future-directions.md](docs/future-directions.md) for the map of future and discussion documents.

## Author Or Adopt Frames

This is the fuller toolkit for people who are actively writing Frames. It expands on the "create, validate, or evolve Frames" path above.

- Read [spec/frame-spec.md](spec/frame-spec.md) for the current minimum adopt-now spec.
- Review [examples/minimal/README.md](examples/minimal/README.md) for a concrete minimal example.
- Review [examples/complete/README.md](examples/complete/README.md) for a fuller example that includes suggested fields.
- Review [examples/minimal-self-frame/README.md](examples/minimal-self-frame/README.md) for a self-referential example that uses the minimal spec to describe the spec itself.
- Open [tools/frame-builder.html](tools/frame-builder.html) for a simple offline builder that generates valid Frame Markdown.
- Use [tools/frame-authoring-assistant-prompt.md](tools/frame-authoring-assistant-prompt.md) when someone would rather create a Frame through an AI-guided conversation.
- Use [tools/customer-shared-frame-prompt.md](tools/customer-shared-frame-prompt.md) when creating a shared Frame for customer work between OpenTeams and an external organization.
- Use [share/frame-builder-kit/README.md](share/frame-builder-kit/README.md) for the Slack/email-friendly distribution copy of the builder.

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

## Discussion And Future Work

- Read [docs/future-directions.md](docs/future-directions.md) for the map of future and discussion documents.
- Read [docs/spec-enhancement-process.md](docs/spec-enhancement-process.md) for a proposed lightweight process that separates exploratory ideas from active spec proposals.
- Read [docs/spec-and-implementation.md](docs/spec-and-implementation.md) for the boundary between the Frame spec and the systems that realize Frames.
- Read [references/Intelligence Hub Whitepaper - v6.md](references/Intelligence%20Hub%20Whitepaper%20-%20v6.md) for the repository copy of the latest whitepaper that informed the later spec alignment notes.
- Review [examples/self-frame/README.md](examples/self-frame/README.md) and [examples/nebi-frame-package/README.md](examples/nebi-frame-package/README.md) for richer future-oriented examples.

## Repository Layout

```text
docs/
  overview.md
  design-note.md
  how-to-use-frames.md
  tools-and-aids.md
  spec-and-implementation.md
  future-directions.md
  spec-sketch.md
  nebi-integration.md
  desktop-sharing.md
  v1-gap-analysis.md
  canonical-identity-proposal.md
USING-FRAMES.md
CHANGELOG.md
tools/
  README.md
  frame-builder.html
  frame-authoring-assistant-prompt.md
  customer-shared-frame-prompt.md
  frame-authoring-assistant/
  frame-reader/
share/
  frame-builder-kit/
spec/
  README.md
  frame-spec.md
  v0.2.md
examples/
  minimal/
  complete/
  minimal-self-frame/
  OT-FIR-program.md
  self-frame/
  nebi-frame-package/
references/
  Intelligence Hub Whitepaper - v4.md
  Intelligence Hub Whitepaper - v5.md
  Intelligence Hub Whitepaper - v6.md
  travis-definition.md
```

## Current Status

The spec is early but released: `v0.2.0` is the first official release and is safe to adopt now.

What exists now:

- a working concept and definition for Frames
- a small released spec that can be adopted immediately (`v0.2.0`, frozen at [spec/v0.2.md](spec/v0.2.md))
- a design note describing the problem and direction
- future-oriented spec discussion documents
- a Nebi integration illustration
- concrete example Frame packages

What is intentionally not required for the current spec:

- a finalized schema
- a finalized Nebi contract
- a built-in Desktop sharing implementation
- settled governance for publication and discovery
- a standardized management or layering system

## Working Position On Nebi

Nebi is treated here as a potential mechanism, not as the semantic definition of a Frame.

The intended boundary is:

- Frames are the semantic artifacts
- Nebi may package, version, and distribute Frames
- Desktop may become a discovery, import, export, and sharing surface for Frames
