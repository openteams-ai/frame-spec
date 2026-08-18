# Future Directions

This document collects the richer ideas that are intentionally outside the immediate `v0.2` spec.

These notes are useful for discussion and future design, but they are not required in order to start writing and sharing Frames now.

## Current Spec

- [../spec/frame-spec.md](../spec/frame-spec.md) is the current adopt-now spec.

## Background

- [overview.md](overview.md) explains the concept and working definition.
- [design-note.md](design-note.md) describes the problem framing and open questions.
- [ecosystem.md](ecosystem.md) gives one-line definitions of surrounding projects.

## Future Spec Exploration

- [spec-sketch.md](spec-sketch.md) explores a richer future shape for Frame artifacts and packaging.
- [v1-gap-analysis.md](v1-gap-analysis.md) maps the current draft against the [Intelligence Hub whitepaper](https://github.com/openteams-ai/inthub-whitepaper) assumptions.
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

Some future topics, especially layering, may touch both sides. That is one reason they remain discussion topics rather than `v0.2` requirements.

## Working Principle

Use Frames first.

Learn from real exchange and usage.

Only then harden the richer behaviors into later versions of the spec.
