# Frame-To-Cog Contract

This note is future-facing.

It is written from the Frame side.

It is not a Cog specification, and it should not be read as if the repository has already defined what a Cog is in full.

Its purpose is narrower:

- describe the minimum contract the Frame spec will likely need to expose for future Cogs to consume Frames reliably
- clarify what the Frame spec should define without trying to define Cog internals prematurely

This note builds on [frame-cog-op-boundary.md](frame-cog-op-boundary.md) and the architectural distinction between Frames, Cogs, and Ops described in the [Intelligence Hub whitepaper](https://github.com/openteams-ai/inthub-whitepaper).

## Framing Assumption

The current repository is defining Frames first.

That means the most useful near-term question is not:

"What is the full Cog spec?"

It is:

"What must a Frame expose so that a future Cog can consume it in a portable, governable, implementation-agnostic way?"

This note answers that second question.

## What This Note Does Not Try To Define

This note does not define:

- how a Cog is packaged
- how a Cog declares its tools
- how a Cog runs
- how a Cog is permissioned
- how a Cog performs retrieval or action
- how a Cog reports execution state
- how an Op orchestrates one or more Cogs

Those belong to later Cog and Op work.

## The Frame-Side Contract

From the Frame side, a future Cog will likely need to rely on a small set of portable concepts.

### 1. Scope

A Cog needs to know where a Frame applies.

A Frame should expose:

- the scope it governs
- enough structure to distinguish company, department, project, partner, user, session, or other scope classes

Why this matters:

- a Cog should not apply company context as if it were project-specific override context
- a Cog should be able to reason about whether multiple Frames are relevant at once

### 2. Status and Review State

A Cog needs to know whether a Frame is approved, draft, deprecated, or otherwise limited in trust.

A Frame should expose:

- status
- review state when relevant
- possibly effective date or similar temporal metadata

Why this matters:

- a Cog should not treat unreviewed draft context as interchangeable with approved organizational guidance
- a Cog may need to warn, refuse, or downgrade confidence when the active Frame is not in an approved state

### 3. Sharing and Visibility Policy

A Cog needs to know whether a Frame or part of a Frame is safe to use in a given collaboration context.

A Frame should expose:

- visibility or sharing policy
- export constraints if later specs support them
- section-level shareability if later specs support that detail

Why this matters:

- a Cog serving a partner-safe workflow should not silently pull in internal-only content
- a Cog should be able to preserve organizational boundaries in mixed internal/external use cases

### 4. Composition Semantics

A Cog needs to know how multiple active Frames relate.

A Frame should expose:

- how it composes with others
- how precedence works
- how conflicts or overrides should be understood

Why this matters:

- the whitepaper assumes active composition of multiple Frames
- a Cog should not be forced to invent its own meaning when company, project, partner, and personal context all appear together

### 5. Provenance and Authority

A Cog needs to know what this Frame claims to be.

A Frame should expose:

- stable identity
- version
- publisher or steward
- canonical-source metadata when available
- lineage or derivation metadata when relevant

Why this matters:

- a Cog may need to distinguish official context from a local adaptation, export, fork, or outdated copy
- auditability becomes much stronger when the active context is identifiable across copies and versions

### 6. Interpretation Guidance

A Cog needs to know how to read and apply the Frame, not just what text it contains.

A Frame should expose or allow:

- interpretation guidance
- reading priorities
- confidence-handling expectations
- citation or attribution expectations

Why this matters:

- two workers can misapply the same Frame differently if the interpretation layer is implicit
- many real use cases depend not just on what the context says, but on how the worker is expected to treat it

### 7. Normative Versus Descriptive Content

A Cog needs to know whether a statement is:

- required
- preferred
- forbidden
- background only

A Frame should expose enough structure that this distinction is visible.

Why this matters:

- a Cog should not treat a bit of background explanation as if it were a hard rule
- a Cog should be able to escalate when required constraints conflict with user requests

## The Minimum Practical Contract

If the repository wants the smallest useful Frame-side contract for future Cogs, the current best candidate is:

- explicit scope
- explicit status or review state
- explicit sharing or visibility metadata
- explicit composition semantics
- explicit provenance or identity metadata
- explicit interpretation guidance
- explicit normative strength where relevant

This is still a Frame contract.

It says what context is available and what claims that context can carry.

It does not say how a Cog must internally implement consumption of that context.

## What A Future Cog Could Reasonably Assume

Without defining the Cog spec, it is still helpful to name what a future Cog should be able to count on from a Frame.

A future Cog should be able to assume that a Frame can answer questions like:

- What scope do you apply to?
- Are you approved, draft, deprecated, or otherwise limited?
- Are you safe to use in this collaboration context?
- How do you combine with other active Frames?
- What source should be treated as authoritative?
- How should your contents be interpreted?
- Which parts are requirements versus preferences versus background?

That is enough to make a Frame portable and machine-usable without prematurely standardizing Cog internals.

## What A Frame Should Not Need To Know About Cogs

To preserve separation of concerns, the Frame spec should avoid depending on future Cog details such as:

- concrete model families
- runtime memory layout
- token-budget strategies
- tool invocation mechanics
- retriever design
- UI presentation details
- internal planning loops

Those are implementation concerns or future Cog-spec concerns.

The Frame should remain meaningful even if different Cogs consume it in different ways.

## Example: Pricing

From the Frame side, the pricing Frame should expose things like:

- scope: public sector pricing
- status: approved
- visibility: internal
- composition: proposal-specific context overrides general pricing defaults
- authority: maintained by finance and proposal leadership
- interpretation: preserve assumption labels and cite source files
- normative content: margin floor is required; preferred language is advisory

That still does not define:

- how a pricing Cog retrieves comparable awards
- how it models competitor pricing
- how it sequences tool use

Those remain future Cog concerns.

## Example: Past Performance

From the Frame side, the past-performance Frame should expose things like:

- scope: public sector proposals
- status: approved
- sharing: internal-only source details, partner-safe summaries if exported
- composition: proposal-specific RFP context can narrow which examples matter
- provenance: official internal source and version
- interpretation: distinguish confirmed evidence from inferred fit
- normative content: do not claim relevance that cannot be supported

Again, that does not define the retrieval or ranking logic of a future past-performance Cog.

## Why This Matters

If the Frame spec exposes too little, every Cog implementation will invent its own rules for:

- what context counts
- what trust level applies
- how conflicts are resolved
- what is safe to share
- how to interpret the text

That would weaken portability and make the ecosystem less coherent.

If the Frame spec exposes too much execution detail, it will start collapsing into a Cog spec before that work is ready.

The goal is to define the smallest portable context contract that future Cogs can depend on.

## Working Heuristic

When deciding whether something belongs in the Frame-side contract, ask:

"Is this a claim about the context that any future Cog should be able to rely on, regardless of how that Cog is implemented?"

If yes, it probably belongs here.

If it is really a claim about worker behavior, runtime mechanics, or execution strategy, it probably belongs in future Cog or Op work instead.
