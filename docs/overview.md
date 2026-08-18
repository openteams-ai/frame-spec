# Overview

## Current Working Definition

The following text captures the current working definition that motivated this proposal:

> A Frame is a scoped, text-based artifact — a file or folder of files using an open spec — that carries the cultural and operational context within which work happens. Every organization has implicit context: brand voice, technical terminology, regulatory constraints, departmental conventions, team norms, project goals. Today, this lives in style guides, wikis, Slack history, onboarding documents, and the heads of senior employees. When AI is brought to bear without this context, the organization must re-explain itself in every interaction, and the resulting work suffers — generic, inconsistent, and disconnected from how the organization actually operates.
>
> Frames make this context explicit, portable, inheritable, and shareable. A Frame is read by humans, applied by Cogs, and exchanged across organizational boundaries when appropriate. Frames are first-class artifacts: they live independently of Cogs and Progs and can be authored, discovered, sold, and inherited on their own.
>
> A Frame typically carries a mix of cultural context (the why and what of the work) and the concrete artifacts that operationalize that context (the how and with what):
>
> Rules — what is and is not acceptable behavior within the scope
> Terminology — the words, names, and definitions specific to the organization, function, or project
> Goals — what success looks like; what outcomes are valued
> Style — tone of voice, formatting conventions, brand expression
> Norms — implicit expectations about how work gets done
> Skills — named capabilities the work depends on
> Tool specifications — Nebi spec files that document the tools the Frame expects to be available
> Prompts — reusable prompt fragments to be loaded into Cog context
> Architecture descriptions — relevant software and system context that orients the work
> Business process details — the procedural backbone that the work follows

## Why Frames Matter

Organizations already have cultural and operational context, but it is usually fragmented across:

- style guides
- onboarding documents
- wikis
- informal chat history
- undocumented team habits
- the judgment of senior employees

That creates problems for both humans and Cogs:

- important context is repeatedly re-explained
- outputs become generic or inconsistent
- cross-team or cross-company collaboration loses nuance
- local assumptions remain implicit
- review becomes harder because the governing context is not visible

Frames aim to make that context:

- explicit
- portable
- inheritable
- reviewable
- shareable

## What A Frame Carries

A Frame may include:

- rules
- terminology
- goals
- style
- norms
- skills
- tool specifications
- prompts
- architecture descriptions
- business process details

Not every Frame must include all of these, but the spec should allow them.

## Scope And Hierarchy

Frames are meant to be scoped and inheritable.

Typical scopes include:

- company
- department
- team
- project
- partner relationship
- vendor relationship

The general idea is:

- broader scopes establish defaults
- narrower scopes refine or constrain them
- exported Frames include only what is intentionally shareable

Frames should also remain self-describing when copied or shared.

That implies the spec should carry structured identity metadata for:

- what logical Frame an artifact is
- which version it represents
- who published or stewards it
- what source it claims as authoritative

This helps distinguish an official published Frame from a local copy, reviewed export, or forked derivative without depending on one particular storage system or application.

## Relationship To Cogs And Progs

Frames are not the same thing as Cogs or Progs.

- Frames carry cultural and operational context
- Cogs consume and apply that context
- Progs remain executable or programmatic components that should stay distinct

This separation matters because the Frame should remain inspectable and shareable even when the consuming Cog or Prog changes.

## Current Direction

The current direction is:

- define an open Frame spec first
- keep Frames as normal text artifacts or folders
- use Nebi as a likely packaging and distribution mechanism
- support future Desktop sharing without making the app the definition of the spec

## Reference

The broader architecture this definition emerged from is described in the [Intelligence Hub whitepaper](https://github.com/openteams-ai/inthub-whitepaper).
