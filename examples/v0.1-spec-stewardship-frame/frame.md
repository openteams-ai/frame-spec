---
type: frame
version: 0.1.0
name: Frame Spec Stewardship
description: Shared guidance for how the Frame spec should be evolved, reviewed, and discussed as a portable open standard.
visibility: internal
scope: project
maintainer: frame-spec-maintainers
---

# Frame Spec Stewardship

## Purpose

- Preserve a small, portable, human-readable core Frame spec.
- Help contributors evaluate enhancement ideas without treating every strong suggestion as an imminent spec change.
- Keep spec evolution grounded in real use, interoperability, and stewardship rather than implementation preference.

## Primary Goals

- Make the current spec easy to understand and adopt.
- Learn from real examples before standardizing richer semantics.
- Keep the boundary clear between semantic definition and product implementation.
- Support future specialization without overloading the core spec prematurely.

## Ways Of Working

- Prefer durable concepts over tool-specific behavior.
- Prefer portable meaning over convenience for one runtime.
- Prefer evidence from repeated real use over speculative completeness.
- Prefer a small adopted core plus explicit future discussion over implied commitments.
- Make it clear whether an idea is exploratory, under active proposal, or part of the adopted spec.

## Proposal Evaluation

- Ask whether a change is needed by nearly every Frame consumer or only by a particular domain or workflow.
- Ask whether the concept preserves portability, reviewability, governance, or interoperability.
- Ask whether the concept belongs in the core spec, a future enhancement proposal, or a domain-specific profile.
- Ask whether the same outcome could be achieved without increasing the minimum complexity of the adopted spec.
- Ask whether the proposal clarifies the meaning of Frames or primarily reflects runtime, tooling, or interface preferences.

## Domain Sensitivity

- Do not assume one strong use case defines the right shape for every Frame.
- Treat domain-specific structure as a valid possibility without forcing it into the core spec too early.
- Allow room for domains to develop richer conventions when those conventions are not universal requirements.
- Treat domain profiles or similar specialization patterns as proposals to evaluate deliberately, not assumptions to adopt implicitly.

## Boundaries

- Do not let implementation details define the semantic meaning of a Frame.
- Do not collapse Frames, Cogs, and Ops into one undifferentiated concept, even when a product surface makes them feel seamless.
- Do not treat repository workflow mechanics as if they were the same thing as Frame semantics.
- Do not expand the minimum spec solely because a feature would be convenient for one tool, one team, or one industry.

## Evidence Standards

- Strong proposals should point to recurring problems, not just interesting possibilities.
- Real examples are better evidence than abstract preference.
- Cross-domain relevance is stronger evidence for core inclusion than single-domain intensity.
- If uncertainty remains high, prefer documenting the idea as exploration or proposal rather than adopting it into the spec.

## Review Norms

- Be explicit about assumptions, tradeoffs, and non-goals.
- Preserve rejected or deferred ideas when the reasoning is useful.
- Distinguish clearly between adopted guidance and future-facing discussion.
- Favor language that a human reviewer and an AI consumer could both interpret consistently.

## Relationship To Process

- This Frame guides how to think about spec evolution.
- The repository's enhancement-process documents define the mechanics of how proposals are recorded, reviewed, and advanced.
- When drafting a proposal, use this Frame to guide judgment and the process documents to guide structure.
