# Frame Spec

This repository holds the specification for **Frames**: scoped, text-based artifacts that carry the cultural and operational context within which work happens. A Frame is written by an organization, read by people, and loaded as context for AI systems, so that the organization does not have to re-explain itself in every interaction.

**Current release: [v0.2.0](https://github.com/openteams-ai/frame-spec/releases/tag/v0.2.0)** (2026-08-18), frozen at [spec/v0.2.md](spec/v0.2.md). It is the normative reference. **Working draft:** [spec/frame-spec.md](spec/frame-spec.md) carries the proposed v0.3, which is not normative until it is released. Changes between releases are tracked in the [changelog](CHANGELOG.md).

## What a Frame is

Every organization has implicit context: brand voice, technical terminology, regulatory constraints, departmental conventions, team norms, project goals, business process. Today that lives in style guides, wikis, chat history, and the heads of senior employees. A Frame makes a slice of it explicit and portable.

A Frame is:

- **scoped**: it applies to a defined scope, such as a company, department, team, project, role, or partner relationship
- **inheritable and composable**: a project Frame can build on a department Frame, which builds on a company Frame; several Frames can also be combined for one piece of work
- **shareable**: within an organization, or selectively with partners, vendors, and customers
- **owned**: each Frame is maintained by, and accountable to, a person or a group of people
- **a first-class artifact**: it exists independently of any tool that reads it, and can be authored, versioned, discovered, and exchanged on its own

The definition comes from the Intelligence Hub whitepaper, linked from [docs/ecosystem.md](docs/ecosystem.md). Everything in this repository is about the artifact. Nothing here requires a particular product to read, store, or distribute one.

## What the specification defines

The specification has two layers.

**The Frame itself (the model).** What a Frame is, independent of how it is written down: the elements it carries and what each one means, which of them are mandatory, how Frames combine, and how a Frame is identified. Exactly two elements are mandatory: an identifier (which Frame is this) and guidance (what it says). Everything else is optional, including a title, description, version, status, maintainer, scope, visibility, license, lineage and Guard references, and ten optional kinds of content that a Frame commonly carries (rules, terminology, goals, style, norms, skills, tool specifications, prompts, architecture, business process). A reader that does not recognize one of those kinds treats it as ordinary guidance and never discards it, so a Frame with no labeled sections and a Frame with all ten are the same kind of thing, read at two levels of detail. Where an element means the same thing as a term already defined by an established vocabulary such as Dublin Core or schema.org, the specification says so instead of inventing a new meaning.

**How a Frame is written down (the encodings).** Three: Markdown, YAML, and JSON. The Markdown encoding is the v0.2 file format, unchanged: a YAML front matter block with four required fields and a free-form Markdown body. Every valid v0.2 Frame is a valid Frame under the working draft.

The smallest Markdown Frame, which is the v0.2 minimal example:

```markdown
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

Under the working draft this same file is a Frame whose identifier is its location, whose guidance is the body, and whose Goals, Terminology, and Style sections are recognized kinds of content. Nothing in the file changes.

## Versions and status

- **Released versions** are frozen snapshots in [spec/](spec/README.md) and never change after release. `v0.2.0` is the current release and the normative reference. It defines the Markdown file format, which the working draft preserves as the Markdown encoding.
- **The working draft**, [spec/frame-spec.md](spec/frame-spec.md), carries the proposed `v0.3`: the model, the YAML and JSON encodings, rules for composition, conformance profiles for implementations, and security considerations. It is written in the structure of an IETF Internet-Draft because that structure forces the sections a specification of this kind needs; it has not been submitted to the IETF or anywhere else. It is not normative until released. Appendix D of the draft lists what it adds relative to v0.2, and [spec/README.md](spec/README.md) summarizes it.
- **The element set as data**: [spec/profile/frame-core.csv](spec/profile/frame-core.csv) lists every element with its obligation, repeatability, and vocabulary correspondence, in the DCTAP tabular-profile format, so validators do not have to hard-code the element set.
- **Declaring a version.** A Markdown Frame states the specification version it was written to with `type: frame [<major>.<minor>]`, for example `frame [0.2]`; the YAML and JSON encodings may carry the same token but do not require it. Specification releases are three-part (`v0.2.0`); patch releases clarify wording without changing requirements, so the patch component never appears in the token.

## Start here

If you want to use Frames in day-to-day AI work:

- Read [USING-FRAMES.md](USING-FRAMES.md) first.
- Browse [examples/](examples/README.md), starting with [examples/minimal/](examples/minimal/README.md).

If you want to implement or adopt the specification:

- Read [spec/frame-spec.md](spec/frame-spec.md), the working draft. Sections 3, 4, and 5 are the model, the elements, and composition; section 6 is the three encodings; section 7 describes the conformance profile every implementation publishes to state which optional behaviors it performs.
- Read [spec/v0.2.md](spec/v0.2.md) for the released requirements of the Markdown encoding.
- Run [tools/validate_frames.py](tools/validate_frames.py) to check that a Markdown Frame carries the required v0.2 fields. A validator for the working draft, covering all three encodings, is planned.

If you want background or future discussion:

- Read [docs/overview.md](docs/overview.md) for the concept and working definition.
- Read [docs/ecosystem.md](docs/ecosystem.md) for one-line definitions of the surrounding projects named in the discussion documents.
- Read [docs/future-directions.md](docs/future-directions.md) for the map of future and discussion documents.

## Author or adopt Frames

- Browse [examples/README.md](examples/README.md) for an index of all examples, grouped by whether they are canonical, illustrative, or future-facing.
- Open [tools/frame-builder.html](tools/frame-builder.html) for a simple offline builder that generates valid Frame Markdown.
- Use [tools/frame-authoring-assistant-prompt.md](tools/frame-authoring-assistant-prompt.md) to create a Frame through an AI-guided conversation.
- Use [tools/customer-shared-frame-prompt.md](tools/customer-shared-frame-prompt.md) to create a shared Frame between your organization and an external partner or customer.
- Use [share/frame-builder-kit/README.md](share/frame-builder-kit/README.md) for the standalone distribution copy of the builder.

These aids help people create or verify Frames. They do not define a runtime or a management system for Frames; see [docs/tools-and-aids.md](docs/tools-and-aids.md) for that boundary.

## Discussion and future work

- Read [docs/design-note.md](docs/design-note.md) for the original problem framing and open questions.
- Read [docs/spec-and-implementation.md](docs/spec-and-implementation.md) for the boundary between the specification and the systems that realize Frames.
- Read [docs/spec-enhancement-process.md](docs/spec-enhancement-process.md) for a proposed lightweight process that separates exploratory ideas from active spec proposals.
- Read the Intelligence Hub whitepaper, published in its own repository and linked from [docs/ecosystem.md](docs/ecosystem.md), for the broader architecture the specification serves.
- Review [examples/self-frame/README.md](examples/self-frame/README.md) and [examples/nebi-frame-package/README.md](examples/nebi-frame-package/README.md) for richer, future-oriented examples.

## Repository layout

```text
spec/
  README.md
  frame-spec.md          # working draft (proposed v0.3; not normative until released)
  v0.2.md                # released v0.2.0 snapshot (normative)
  profile/
    frame-core.csv       # element set as a machine-readable profile
CHANGELOG.md
LICENSE
USING-FRAMES.md
examples/
  README.md              # index of all examples
  minimal/
  code-review-norms/
  with-suggested-fields/
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
  test_validate_frames.py
  frame-authoring-assistant-prompt.md
  customer-shared-frame-prompt.md
  frame-authoring-assistant/
  frame-reader/
share/
  frame-builder-kit/
.github/
  workflows/
    validate-frames.yml  # CI: validator tests and example validation
```

## Relationship to implementations and distribution

The specification defines the artifact. Systems that store, distribute, or apply Frames are implementations of it: a registry that hosts Frames for an organization, a package manager that carries them between systems, a desktop or web application that applies them to AI work. Each such system declares in a conformance profile which of the specification's optional behaviors it performs, so that an author knows how a layered set of Frames will behave in a given tool. None of them defines what a Frame means.

Two projects are referred to in the discussion documents as likely mechanisms: Nebi, an open-source environment management tool that may package and distribute Frames as its scope grows beyond computational environments, and Collab, a desktop application that applies Frames and may become a discovery, import, and sharing surface for them. See [docs/ecosystem.md](docs/ecosystem.md) for definitions and links.

## Contributing

Issues and pull requests are welcome. Editorial fixes to the working draft can go straight to a pull request. Substantive changes to what the specification requires should start as an issue, so that the change can be discussed before its wording is. [docs/spec-enhancement-process.md](docs/spec-enhancement-process.md) proposes a lightweight process for carrying an idea from exploration to an active proposal to inclusion.

## License

This repository is licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).
