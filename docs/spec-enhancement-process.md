# Spec Enhancement Process

This note proposes a lightweight process for evolving the Frame spec without blurring the line between:

- ideas worth exploring
- proposals under active consideration
- changes that are actually on track for inclusion
- changes that are already part of the adopted spec

The goal is to make the repository easier to navigate and to reduce pressure to treat every good idea as an imminent spec requirement.

## Why This Process Exists

The repository is intentionally early.

That is a strength, but it creates a predictable risk:

- strong use cases can generate strong suggestions
- strong suggestions can look like default future direction
- future direction can start to feel like implied commitment

This process is meant to slow that down in a healthy way.

It allows the project to:

- learn from real usage
- record possible enhancements
- advance selected proposals deliberately
- avoid overfitting the spec to one domain or one workflow too early

## Guiding Principle

The current adopted spec should remain small and explicit.

Potential enhancements should be easy to discuss without being mistaken for planned inclusion.

Anything moving toward inclusion should be clearly marked as such.

## Repository States

The repository should distinguish four different states.

### 1. Adopted Spec

Meaning:

- this is part of the current spec
- implementers may rely on it
- examples and tools should treat it as normative

Location:

- `spec/`

Examples:

- `spec/v0.2.md`

### 2. Active Proposal

Meaning:

- this idea is being seriously shaped toward possible spec inclusion
- it has a concrete problem statement and proposal shape
- it is still not part of the spec

Location:

- a future `enhancements/` directory

Examples:

- a proposal for canonical identity
- a proposal for composition semantics
- a proposal for domain profile support

### 3. Exploration

Meaning:

- this is a design direction, idea, sketch, or open question
- it may inform future work
- it is not yet being advanced as a defined proposal

Location:

- `docs/`

Examples:

- whitepaper alignment notes
- packaging explorations
- boundary notes
- domain use-case writeups

### 4. Reference

Meaning:

- contextual material that informs the work
- not itself a spec proposal

Location:

- links from `docs/` to externally published material

Examples:

- the [Intelligence Hub whitepaper](https://github.com/openteams-ai/inthub-whitepaper), maintained in its own repository
- historical framing notes

## Proposed Repository Structure

The simplest structure that supports this distinction is:

```text
spec/
  README.md
  v0.2.md

enhancements/
  README.md
  template.md
  0001-domain-profiles.md
  0002-canonical-identity.md

docs/
  future-directions.md
  design-note.md
  spec-and-implementation.md
  ...
```

Interpretation:

- `spec/` contains only adopted spec artifacts
- `enhancements/` contains active spec proposals
- `docs/` contains exploratory notes, framing discussions, and supporting analysis

This keeps "interesting" separate from "in process."

## Proposal Lifecycle

This process is intentionally lighter than a full standards body, but it follows a PEP-like shape.

### Idea

An idea starts as a note, issue, conversation, or exploratory document.

Characteristics:

- problem may be clear
- solution is still open
- no implication of inclusion

Typical home:

- discussion
- `docs/`

### Draft Proposal

A draft proposal exists when the project wants to examine a possible spec enhancement in a structured way.

Characteristics:

- named proposal
- clear motivation
- explicit non-goals
- rough proposed semantics
- open questions still allowed

Typical home:

- `enhancements/`

### Active Review

A proposal enters active review when it is being seriously considered for a future version.

Characteristics:

- concrete enough for real feedback
- examples or experiments exist
- tradeoffs are documented
- maintainers are actively deciding whether to advance it

Typical home:

- `enhancements/`

### Accepted For Future Version

Meaning:

- the project intends to include the proposal in a future spec version
- exact wording may still evolve
- it is not yet adopted in the current spec

This state should be used sparingly.

### Rejected

Meaning:

- the proposal will not move forward in its current form

This is still valuable because it preserves reasoning and prevents repeated confusion.

### Deferred

Meaning:

- the idea may be good, but the project is not ready to advance it

This is especially useful for:

- domain-specific needs
- implementation-coupled ideas
- proposals that need more examples first

### Superseded

Meaning:

- a newer proposal replaces the old one

## Proposal Metadata

Each active proposal should carry a small header so its state is obvious.

Suggested fields:

```yaml
id: 0001
title: Domain Profiles
status: draft
type: standards-track
target_version: null
created: 2026-05-28
updated: 2026-05-28
discussion: docs/future-directions.md
```

Suggested `status` values:

- `draft`
- `review`
- `accepted`
- `deferred`
- `rejected`
- `superseded`

Suggested `type` values:

- `standards-track`
- `process`
- `informational`

## Proposal Template

Each enhancement proposal should answer these sections:

1. Summary
2. Motivation
3. Non-Goals
4. Proposed Semantics
5. Examples
6. Backward Compatibility
7. Alternatives Considered
8. Open Questions
9. Recommendation

This is enough structure to make proposals comparable without turning the repo into ceremony.

## Domain Profiles As A Proposal Class

Domain-specific Frame types or profiles should be treated as proposals, not as assumptions.

That means:

- the core Frame spec remains general unless changed explicitly
- domain-specific conventions can be proposed separately
- multiple domains can evolve profiles without forcing immediate core-spec changes

Examples of possible profile proposals:

- public sector proposal profile
- investor relations profile
- healthcare compliance profile
- software engineering project profile

This is a good fit for the current uncertainty because it allows specialization without prematurely standardizing it.

## Admission Rule For The Core Spec

A feature should move into the core Frame spec only when at least one of these is true:

- every Frame consumer needs it
- multiple domains clearly need the same semantic concept
- the absence of the concept causes repeated interoperability failure
- the concept is necessary to preserve portability, reviewability, or governance

Otherwise, it should stay:

- outside the spec
- in an enhancement proposal
- or in a domain profile

## Recommended Near-Term Use In This Repo

Near term, the repo can adopt this process without a large restructure.

Recommended first step:

1. Keep `spec/` for adopted spec only.
2. Keep `docs/` for exploratory and background material.
3. Add `enhancements/` for active proposals.
4. Move only the proposals that are truly under active consideration into `enhancements/`.
5. Leave broader sketches and idea notes in `docs/`.

This allows the repository to become clearer incrementally.

## Suggested Immediate Candidates

If the project adopts an `enhancements/` track, good initial candidates might include:

- canonical identity and authoritative-source metadata
- composition semantics
- sharing and export semantics
- domain profiles

By contrast, these likely remain better as exploratory notes for now:

- broad packaging direction
- Collab-facing behavior
- full Cog or Op implications
- domain-specific use-case narratives without a concrete proposal

## Working Heuristic

If a document mainly says:

- "here is a possibility"

it belongs in `docs/`.

If it mainly says:

- "here is a concrete change we are evaluating for future inclusion"

it belongs in `enhancements/`.

If it mainly says:

- "this is the current contract implementers should rely on"

it belongs in `spec/`.
