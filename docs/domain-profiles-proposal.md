# Domain Profiles Proposal Sketch

> Status note: still exploratory. "Profile" here means a domain profile. The v0.3 working draft uses "conformance profile" (its Section 7) for an implementation's declaration of optional behaviors, which is a different thing; the draft's optional content refinements (its Section 4.4) cover part of what a domain profile might have specified.

This note is exploratory.

It is not an adopted part of the Frame spec.

Its purpose is to sketch one possible direction for handling domain-specific specialization without overloading the core Frame spec.

## Problem

Different domains appear likely to want different kinds of Frame structure.

Examples:

- investor-facing context packs
- public sector proposal support
- healthcare compliance guidance
- software engineering project context

The project should avoid jumping from one strong use case directly to new core-spec requirements unless those requirements generalize well.

## Working Idea

Keep the core Frame spec small.

Allow richer specialization through optional domain profiles.

A domain profile would define additional expectations such as:

- expected sections
- suggested metadata
- interpretation conventions
- review expectations
- optional validation rules

The key idea is:

- every profile is still a Frame
- not every Frame needs a profile
- profile support should extend the core spec, not replace it

## Benefits

- avoids overfitting the core spec to one workflow
- creates room for serious domain-specific structure
- helps tooling behave more intelligently when a known profile is present
- lets multiple domains evolve at different speeds

## Risks

- fragmentation if profiles proliferate without discipline
- confusion if profiles feel mandatory
- accidental leakage of runtime behavior into profile definitions

## Constraint

If profiles are pursued later, a Frame without profile-aware tooling should still degrade gracefully as human-readable context.

That means profile use should not destroy the basic portability of Frames.

## Possible Future Shape

Examples of lightweight markers that could later be explored:

```yaml
type: frame
profile: public-sector-proposal
```

or

```yaml
type: frame
profiles:
  - investor-relations
  - recipient-tailored-export
```

These are examples only, not recommendations for adoption yet.

## Likely Next Question

If the repo wants to explore this seriously, the next step is not adding profile fields to the spec immediately.

The next step is deciding whether "domain profiles" should become an active enhancement proposal with:

- motivation
- non-goals
- semantics
- compatibility expectations
- example profiles
