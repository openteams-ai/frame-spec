# Early Onboarding Adoption Insights

> Note: this document records early internal onboarding conversations at OpenTeams before the first public release of the spec. It is preserved as background for Frame authors and implementers.

This note summarizes lessons from early internal conversations where people were taught what Frames are, how to create them, and how to use them in everyday AI work.

It is not a spec proposal.

Its purpose is to capture adoption and teaching signals that may influence:

- documentation
- examples
- tooling aids
- future spec discussion

without overstating what should immediately become part of the core Frame spec.

## Context

These insights come from several early onboarding conversations across departments and roles, including:

- public sector and proposal-oriented work
- cross-company partner or customer collaboration
- marketing and product-facing conversations
- general internal users learning the concept for the first time

The conversations are useful not because every participant had a fully mature use case, but because they reveal:

- how people first understand the concept
- where they get confused
- what value feels immediate
- what kinds of Frame patterns appear naturally

## High-Level Conclusion

The strongest adoption signal so far is that Frames are being understood less as a technical artifact and more as a way to preserve and reuse context that people are already trying to give AI manually.

The strongest teaching signal is that new users do not automatically understand Frames as "shared contextual artifacts."

They tend to start with simpler interpretations such as:

- rules
- parameters
- prompt setup
- a big reusable pre-prompt

Those are not wrong, but they are incomplete.

This means early adoption depends as much on explanation and workflow as on the spec itself.

## What People Understand Quickly

Several ideas appear to resonate quickly.

### 1. Frames reduce repeated explanation

People immediately understand the value of not having to repeatedly say:

- who they are
- what OpenTeams is
- what their department cares about
- how a customer or contract should be treated

This makes cross-tool portability one of the clearest near-term value propositions.

### 2. Frames are reusable context

Users quickly recognize that if something appears in many prompts, it probably belongs in a Frame.

This is one of the strongest practical heuristics surfaced so far.

### 3. Layered context feels natural

People naturally think in layered scopes such as:

- company
- department
- industry
- project
- customer
- contract or proposal

Even before formal semantics are settled, users already expect broad-to-narrow layering behavior.

### 4. Customer- and relationship-specific context matters

People naturally propose Frames not only for internal teams, but also for:

- customer-specific work
- customer-type or project-type work
- cross-company shared work
- contract or proposal context

This suggests that relationship-boundary Frames are not edge cases.

## Where People Commonly Get Confused

### 1. "Frame = rules"

New users frequently reduce Frames to rules or parameters.

Rules are part of a Frame, but the concept is broader:

- norms
- vocabulary
- expectations
- role- or situation-specific context
- how work should be interpreted

This is a teaching issue more than a spec issue.

### 2. "Where do Frames get loaded?"

Users quickly ask where Frames live and how they are used in real tools.

This is one of the most immediate adoption friction points:

- the concept makes sense
- the loading model is not yet obvious

### 3. Boundary confusion with Cogs, Ops, and Skills

Users understand the difference better with examples, but the boundaries are not obvious by default.

The most common simplifying instincts are:

- a Frame is a rulebook
- a Cog is a worker
- an Op is the thing to be done
- a Skill is "kind of like this too"

That means the distinctions need repeated reinforcement through examples and usage patterns.

### 4. When to create a Frame versus just writing a prompt

Users need a practical rule for deciding whether something deserves to become a Frame.

The clearest current rule is:

- if it is one-off, keep it in the prompt
- if it recurs across tasks, conversations, or tools, put it in a Frame

## Natural Frame Patterns Emerging From Conversations

The conversations suggest a small set of recurring Frame patterns.

### Company Frame

Used for:

- baseline organizational context
- brand language
- shared norms
- how OpenTeams should be understood

### Department Frame

Used for:

- team-specific working norms
- recurring expectations
- shared ways of operating

Examples:

- marketing
- customer success
- project success
- public sector

### Task-Family Frame

Used for:

- pricing
- past performance
- proposal writing
- contract writing
- kickoff standards

These are not just project-specific. They capture reusable context around a recurring class of work.

### Relationship Frame

Used for:

- specific customers
- classes of customers
- partners
- shared third-party collaboration contexts

This category appears especially important for customer success, proposals, and cross-company work.

### Situation-Specific Frame

Used for:

- a proposal
- a contract pursuit
- a campaign
- a kickoff
- a temporary working context

These may be more short-lived, but they still appear naturally in practice.

## What The Conversations Suggest About The Core Spec

These onboarding conversations do not, by themselves, justify major core-spec expansion.

They do support a few things that are already becoming clearer in the repository.

### Strong support for scoped layering

People expect Frames to be combined from broader to narrower scope.

That aligns with the current `v0.2` direction in [../spec/frame-spec.md](../spec/frame-spec.md), which now includes suggested `version` and optional `inherits` support.

### Strong support for keeping the core simple

Users are still learning the basic concept.

That argues against making the core spec much more complex solely because one domain has a sophisticated use case.

### Strong support for domain-sensitive specialization

Different groups appear likely to want different Frame shapes:

- investor or customer briefing
- public sector proposal support
- contract writing
- marketing messaging
- customer success account context

That supports continued exploration of domain profiles as a future specialization mechanism, as discussed in [domain-profiles-proposal.md](domain-profiles-proposal.md), without making them part of the core spec yet.

## What The Conversations Suggest About Tooling And Documentation

The strongest immediate needs are not deeper semantics alone.

They are:

- better teaching
- clearer usage instructions
- easier loading and activation
- lightweight authoring and reading support

Several of those needs are now directly reflected in the repository.

### Practical usage guidance now matters a lot

This need is now addressed more directly by [../USING-FRAMES.md](../USING-FRAMES.md), which gives a practical operational story for:

- when to use one Frame or several
- how to combine company, department, and customer Frames
- what belongs in a Frame versus in a prompt

This guide responds directly to repeated onboarding questions.

### A Frame-reading aid is important for adoption

The conversations repeatedly surfaced the need for AI tools to consume Frames consistently once users have them.

That need is now partially addressed by [../tools/frame-reader/SKILL.md](../tools/frame-reader/SKILL.md), which gives a lightweight model for:

- identifying Frames
- deciding which are active
- applying the most specific relevant guidance
- surfacing conflict or missing context

### Authoring support needs to stay conversational

Users often discover what a Frame should contain only while talking through their work.

That makes the authoring aids important, especially:

- [../tools/frame-authoring-assistant-prompt.md](../tools/frame-authoring-assistant-prompt.md)
- [../tools/frame-authoring-assistant/SKILL.md](../tools/frame-authoring-assistant/SKILL.md)

### Shared external Frames are a real emerging use case

The conversations surfaced a need to create Frames jointly with customers or partners.

That is now reflected in [../tools/customer-shared-frame-prompt.md](../tools/customer-shared-frame-prompt.md), which is a strong sign that collaboration-boundary Frames are becoming a real category of use.

## Teaching Insights

The onboarding calls suggest a few teaching patterns that work especially well.

### Use analogies

People understand the concept faster through analogies such as:

- family norms versus work norms
- project kickoff versus department standards
- a worker role inside a broader process

### Start from repeated manual prompting

One of the easiest ways to explain a Frame is:

"What do you keep re-explaining to AI, over and over, that should instead be saved and reused?"

This is often more intuitive than starting from the spec definition.

### Teach Frame, Cog, and Op together, but lightly

Users do benefit from seeing the distinction, but the simplest useful explanation seems to be:

- Frame = contextual guidance
- Cog = specialized worker
- Op = coordinated work to produce an outcome

That boundary is captured more explicitly in [frame-cog-op-boundary.md](frame-cog-op-boundary.md), but new users usually need only the simplified form first.

### Give users a rule for when not to create a Frame

This is important.

Without it, users may try to turn every instruction into a Frame.

The best current rule is:

- if it is durable and reused, create a Frame
- if it is one-time task detail, keep it in the prompt

## Product And Workflow Implications

The conversations suggest that internal adoption will depend on a few practical workflow expectations.

### 1. People will manage Frames manually at first

That is acceptable in the short term, but only if:

- naming is simple
- usage guidance is clear
- the reading skill is easy to invoke

### 2. People want a folder-based mental model

A simple local folder of Frames is intuitive to users.

That suggests the product should not fight that model too early.

### 3. People expect shared baseline Frames

Many users want a ready-made OpenTeams or department-level starting point.

This suggests that centrally stewarded baseline Frames will accelerate adoption.

### 4. Cross-tool usage is already part of the value proposition

Users want to move between Claude, Gemini, ChatGPT, Codex, and future OpenTeams surfaces without losing context.

That reinforces the importance of Frames as portable artifacts rather than tool-specific settings.

## Relationship To Current Repo Direction

The current repository has already started responding to the adoption signals from these conversations.

Notable examples include:

- `v0.2` in [../spec/frame-spec.md](../spec/frame-spec.md), which strengthens the adopt-now format with suggested `version` and optional `inherits`
- [../USING-FRAMES.md](../USING-FRAMES.md), which gives a direct operational guide for everyday usage
- [../tools/frame-reader/SKILL.md](../tools/frame-reader/SKILL.md), which supports more consistent consumption
- [../tools/customer-shared-frame-prompt.md](../tools/customer-shared-frame-prompt.md), which reflects the emerging cross-organization use case
- [spec-enhancement-process.md](spec-enhancement-process.md), which helps keep exploratory adoption insights separate from active spec commitments
- [domain-profiles-proposal.md](domain-profiles-proposal.md), which provides a home for future specialization discussion without forcing early core-spec changes

This is a positive pattern:

- use real conversations to expose friction
- address immediate adoption needs with guidance and lightweight tools
- only then decide what should harden into spec semantics

## Recommendations

### Near Term

- keep gathering onboarding conversations across multiple departments
- preserve simple explanations and analogies in onboarding material
- refine baseline company and department Frames that others can adopt quickly
- continue improving usage guidance and examples alongside the spec

### Spec Discipline

- do not overfit the core spec to one sophisticated domain use case
- continue treating richer domain structures as future proposals or profiles
- continue distinguishing teaching/usage problems from semantic-spec problems

### Tooling

- keep the authoring and reading aids lightweight and cross-tool friendly
- improve discoverability of baseline Frames and how to invoke them
- keep manual file-based workflows viable until better product support exists

## Bottom Line

The early onboarding conversations validate the core idea of Frames strongly.

They do not mainly say:

"The spec is too small."

They mainly say:

"The concept is useful, but people need simple explanations, practical loading patterns, and reusable baseline context before broader adoption will feel natural."

That is a strong argument for continuing the current path:

- keep the core Frame spec adoptable
- improve usage guidance and example workflows
- learn from multiple domains
- harden richer semantics only after repeated use shows they are truly needed
