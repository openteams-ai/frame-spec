# Future Directions

This document collects the richer ideas that are intentionally outside the immediate `v0.2` spec.

These notes are useful for discussion and future design, but they are not required in order to start writing and sharing Frames now.

## Current Spec

- [../spec/v0.2.md](../spec/v0.2.md) is the current release and the adopt-now spec.
- [../spec/frame-spec.md](../spec/frame-spec.md) is the working draft, carrying the proposed v0.3. It is not normative until released.

## Background

- [overview.md](overview.md) explains the concept and working definition.
- [design-note.md](design-note.md) describes the problem framing and open questions.
- [ecosystem.md](ecosystem.md) gives one-line definitions of surrounding projects.
- [spec-and-implementation.md](spec-and-implementation.md) describes the boundary between the spec and the systems that realize Frames.
- [how-to-use-frames.md](how-to-use-frames.md) and [tools-and-aids.md](tools-and-aids.md) cover everyday use and the scope of the authoring aids.
- [early-onboarding-adoption-insights.md](early-onboarding-adoption-insights.md) records lessons from early onboarding conversations.

## Future Spec Exploration

- [spec-sketch.md](spec-sketch.md) explores a richer future shape for Frame artifacts and packaging.
- [v1-gap-analysis.md](v1-gap-analysis.md) maps the earlier spec sketch ([spec-sketch.md](spec-sketch.md)) against the [Intelligence Hub whitepaper](ecosystem.md) assumptions; several of its gaps are addressed by the v0.3 working draft.
- [canonical-identity-proposal.md](canonical-identity-proposal.md) proposes richer identity and authoritative-source metadata.
- [frame-cog-op-boundary.md](frame-cog-op-boundary.md) captures a working rubric for the boundary and contract between context, workers, and orchestration.
- [frame-to-cog-contract.md](frame-to-cog-contract.md) describes the minimum future contract Frames may need to expose for Cog (see [ecosystem.md](ecosystem.md)) consumers, explicitly from the Frame side.
- [domain-profiles-proposal.md](domain-profiles-proposal.md) sketches one possible direction for domain-specific specialization without changing the core spec.
- [spec-enhancement-process.md](spec-enhancement-process.md) proposes a lightweight process for separating exploratory ideas from active paths toward spec inclusion.

## Adjacent Considerations

- [nebi-integration.md](nebi-integration.md) explores one possible future packaging and delivery model.
- [collab-sharing.md](collab-sharing.md) captures future Collab-facing sharing requirements and constraints.

## Spec Vs Implementation

For this repository, the rough boundary is:

- the spec defines what a Frame is and what claims it can carry
- implementation defines how a system discovers, installs, layers, mounts, permissions, and activates Frames

Some future topics, especially layering, may touch both sides. That is one reason they remain discussion topics rather than `v0.2` requirements. The v0.3 working draft specifies composition (its Section 5) and leaves the rest to implementations and their conformance profiles.

## Working Principle

Use Frames first.

Learn from real exchange and usage.

Only then harden the richer behaviors into later versions of the spec.
