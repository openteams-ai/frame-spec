# Frame, Cog, and Op Boundary

This note is future-facing.

It is not the Frame spec itself.

Its purpose is to help keep the boundary between Frames, Cogs, and Ops clear as the Frame spec matures and later Cog and Op specs are discussed.

The definitions here are grounded in the repository's current direction and the architecture described in the [Intelligence Hub whitepaper](https://github.com/openteams-ai/inthub-whitepaper).

(For one-line definitions of Cogs, Ops, and related projects, see [ecosystem.md](ecosystem.md).)

## Core Distinction

At a high level:

- a Frame carries context
- a Cog performs work
- an Op coordinates work toward an outcome

More specifically:

- a Frame answers: "What context, constraints, language, and expectations should govern this work?"
- a Cog answers: "What AI worker can do this kind of work under those constraints?"
- an Op answers: "What orchestrated process should produce this business outcome?"

This distinction should remain true even when one product surface makes the three layers feel seamless to the user.

## Layer Contract

### Frame

A Frame is the durable, inspectable context layer.

It should define things such as:

- rules
- terminology
- goals
- norms
- style
- trust or confidence guidance
- process expectations
- tool expectations
- prompts or prompt fragments
- interpretation guidance for how the context should be used

A Frame should remain meaningful when read by:

- a human
- a different Cog
- a different Op
- a different product implementation

A Frame should not depend on one particular worker or one particular workflow in order to make sense.

### Cog

A Cog is the worker layer.

It should define things such as:

- the class of task it performs
- the tools or APIs it can use
- the inputs it expects
- the outputs it produces
- the approvals or governance constraints it operates under
- the Frames it requires, accepts, or benefits from

A Cog consumes context from Frames, but the Cog is not itself the source of organizational truth.

A Cog may specialize in one narrow type of work, such as:

- proposal compliance review
- pricing analysis
- competitor research
- past-performance retrieval
- investor-brief synthesis

### Op

An Op is the orchestration layer.

It should define things such as:

- the business outcome being requested
- which Cogs participate
- which Frames apply at the workflow level
- sequencing and parallelization
- checkpoints, validation, and escalation
- the final deliverable shape

An Op is where multiple workers and multiple context sources come together into one supervised unit of work.

## Decision Rubric

When a concept feels ambiguous, these questions usually help place it.

### Put it in a Frame when:

- it should stay true across many tasks, many workers, or many tools
- it expresses policy, language, standards, or operating assumptions
- a human should be able to inspect and approve it as organizational context
- it would still matter even if the current implementation changed completely
- the main question is "what should govern the work?"

Examples:

- "Use these definitions for key public sector terms."
- "Separate confirmed facts from projections and hypotheses."
- "Prefer brutally honest evidence over marketing language."
- "Use approved past-performance language and attribution rules."

### Put it in a Cog when:

- it describes a specialized capability or worker role
- it depends on tool access, retrieval behavior, or action permissions
- the main question is "who or what does this task?"
- swapping it out for a better worker would not change the governing organizational truth

Examples:

- "Search public award databases for comparable contracts."
- "Scrape approved repositories and summarize implementation status."
- "Rank candidate past-performance examples against an RFP."
- "Draft a pricing recommendation from market signals and constraints."

### Put it in an Op when:

- it combines multiple steps into one requested business outcome
- it coordinates more than one Cog or stage of review
- it needs workflow-level checkpoints or human approval
- the main question is "how do we turn this request into a finished result?"

Examples:

- "Produce a proposal-ready pricing package."
- "Generate a first-draft compliance matrix and summary narrative."
- "Prepare an investor briefing package tailored to this recipient."

## Boundary Tests

These are useful tests for cases that sit near the line.

### Test 1: Durability

Ask:

"Should this remain valid if we replace the current worker, model, or interface?"

If yes, it likely belongs in a Frame.

### Test 2: Worker Identity

Ask:

"Is this mainly describing a kind of worker and what it can do?"

If yes, it likely belongs in a Cog.

### Test 3: Outcome Orientation

Ask:

"Is this mainly describing a multi-step business outcome with coordination?"

If yes, it likely belongs in an Op.

### Test 4: Organizational Truth vs Execution Detail

Ask:

"Is this a truth the organization wants to preserve, or an execution detail of how a worker currently operates?"

Organizational truth points toward Frame.

Execution detail points toward Cog or Op.

### Test 5: Portability

Ask:

"Would we want to share this with another team, partner, or future implementation as a context artifact?"

If yes, Frame is more likely.

If it only makes sense as runnable worker behavior, Cog or Op is more likely.

## Common Ambiguities

Some content naturally sits close to the boundary.

### Interpretation Rules

Statements such as:

- "Cite the file and section you used."
- "Preserve confirmed versus projection versus hypothesis."
- "Trust the Frame over recent session drift."

These are best treated as Frame-level interpretation guidance, because they govern how context should be read and applied across workers.

### Retrieval Instructions

Statements such as:

- "Search SAM.gov (the US federal contract award database) for similar awards."
- "Scrape GitHub for current implementation evidence."
- "Look for association events in target geographies."

These are better treated as Cog behavior, because they describe actions taken by a worker.

### Workflow Templates

Statements such as:

- "First gather candidates, then score them, then draft a summary, then escalate for review."

These are generally Op-level, because they describe coordination across steps rather than durable context.

## Relationship Contract Between Layers

The emerging contract between the layers looks like this:

- Frames provide context to Cogs and Ops
- Cogs declare what Frames they require, accept, or recommend
- Ops declare which Frames apply at the workflow level and which Cogs they coordinate
- Cogs should be auditable in terms of which Frames were active when they acted
- Ops should be auditable in terms of which Cogs ran, under which Frames, to produce which outputs

This suggests a future interoperability model where:

- Frame specs define the context surface
- Cog specs define the worker surface
- Op specs define the orchestration surface

without collapsing all three into one artifact type.

## Worked Examples

### Example 1: Pricing

Frame:

- pricing principles
- approved rate-card context
- margin expectations
- terminology
- escalation rules for uncertain assumptions

Cog:

- retrieve historical pricing examples
- gather public comparable contract data
- analyze likely competitor pricing
- produce a pricing recommendation

Op:

- generate a proposal-ready pricing package for a specific opportunity

### Example 2: Past Performance

Frame:

- what counts as relevant past performance
- approved description patterns
- confidence and evidence requirements
- attribution rules

Cog:

- search internal repositories
- rank candidate examples against the proposal
- draft concise summaries

Op:

- produce a first-draft past-performance section with top recommended examples

### Example 3: Investor Context Pack

Frame:

- canonical company narrative
- terminology
- strategic framing
- interpretation rules for how to read the pack
- anti-claims and escalation guidance

Cog:

- gather recipient-specific background
- synthesize relevant angles
- prepare a recipient-tailored briefing or cover note

Op:

- assemble and deliver a tailored investor briefing package

## What This Means For The Frame Spec

The Frame spec does not need to define Cogs or Ops.

It likely does need to expose enough structure that Cogs and Ops can reliably consume Frames.

The minimum future contract probably includes:

- scope
- review or status metadata
- sharing metadata
- composition semantics
- provenance or lineage
- interpretation guidance

Those fields help the context layer stay portable while still being useful to worker and orchestration layers.

## Working Heuristic

If a statement should remain true across many workers and workflows, put it in a Frame.

If it describes a specialized AI worker and what that worker can do, put it in a Cog.

If it coordinates workers and steps toward a deliverable, put it in an Op.
