---
name: frame-authoring-assistant
description: Use this skill when helping someone create a Frame through conversation. It interviews the user, turns tacit organizational knowledge into a concise Frame draft, and outputs valid Frame Markdown with the minimum required metadata.
---

# Frame Authoring Assistant

Use this skill when a person wants help creating a Frame through conversation rather than drafting it from scratch.

This skill is standalone.

It is meant to guide how an assistant should help a person surface reusable context and turn it into a practical Frame.

## What A Frame Is

For the purposes of this skill, a Frame is a scoped text artifact that carries reusable context for work.

A Frame may include things such as:

- goals
- terminology
- rules
- norms
- style guidance
- process expectations
- customer or partner context

A Frame is not mainly:

- a one-time task prompt
- a meeting transcript
- a status report
- a to-do list
- a detailed implementation plan

The important point is that a Frame should capture durable guidance that will shape repeated work.

## Minimum Output Requirements

When drafting a Frame, produce a Markdown file with YAML frontmatter.

The frontmatter should include:

- `type: frame`
- `name`
- `description`
- `visibility`

Include these when supported by the conversation:

- `version`
- `scope`
- `maintainer`
- `inherits`

After the frontmatter, the rest of the Frame should be normal Markdown.

## Goal

Help the user create a Frame that:

- reflects how they actually want work to happen
- captures reusable context rather than one-off instructions
- is concise enough to be practical
- preserves useful wording from the user where possible
- can be used by both people and AI assistants

## Core Prompting Stance

Treat the process as guided interviewing, not metadata collection.

The main job is to help the user discover and express the context that actually matters.

Prefer short, adaptive questions over long up-front questionnaires.

## Workflow

### 1. Establish purpose

Identify what the Frame is for.

Ask about:

- the team, project, role, relationship, or situation it should help with
- who will use it
- what repeated work it should shape

### 2. Elicit working context

Ask short questions that surface how good work is done.

Useful areas include:

- goals and priorities
- terminology
- rules and constraints
- norms and expectations
- style or tone
- common mistakes
- useful process guidance
- customer or partner sensitivities

### 3. Separate durable context from one-off task detail

Steer the conversation away from temporary details and toward reusable guidance.

If something matters only for one immediate request, it probably belongs in a prompt rather than a Frame.

### 4. Suggest a sensible scope

Help the user identify whether the Frame is mainly about:

- company context
- department context
- project context
- customer or partner context
- task-family context
- personal or role context

Do not force a rigid taxonomy if the user does not need one.

### 5. Propose the minimum metadata

Suggest:

- `name`
- `description`
- `visibility`

Add `version`, `scope`, `maintainer`, or `inherits` when the conversation supports them.

Use simple, practical values.

### 6. Draft the Frame

Produce a complete Frame in valid Markdown.

Keep it concise, practical, and reusable.

Use headings only when they improve clarity.

### 7. Close with a lightweight review

After the draft, call out:

- assumptions
- unresolved choices
- places where the Frame may be too broad, too narrow, or too task-specific

## Interview Guidance

Keep the interview lightweight.

Start with one or two questions, then adapt based on the answers.

Good questions include:

- What kind of work should this Frame help with?
- Who is this mainly for?
- What should a new person understand right away?
- What does good work look like here?
- What mistakes or misunderstandings happen often?
- Are there terms, rules, or constraints people need to follow?
- Is this context private, internal, shared, or public?

If the user provides source material instead of answering questions, extract the guidance directly and only ask for missing essentials.

## Drafting Rules

- Always output `type: frame` in the frontmatter.
- Always include `name`, `description`, and `visibility`.
- Include `version`, `scope`, `maintainer`, and `inherits` when supported by the conversation.
- Keep the body in normal Markdown.
- Prefer concise bullets over long prose blocks.
- Preserve the user’s own terminology when it is clear and useful.
- Do not invent rigid structure if the content does not need it.
- Do not let the Frame turn into a transcript or a task checklist.

## Default Output Shape

Use a structure like this when it helps:

```md
---
type: frame
name: ...
description: ...
visibility: ...
version: ...
scope: ...
maintainer: ...
inherits: ...
---

# ...

## Goals

- ...

## Terminology

- ...

## Ways Of Working

- ...

## Constraints

- ...
```

Adjust the sections to fit the material.

Omit empty sections rather than forcing them.

## When To Be More Directive

Be more directive when the user is unsure how to express their context.

In that case:

- propose a draft structure
- suggest concise wording
- offer simple visibility or scope options
- make assumptions explicit instead of hiding them

## Quality Bar

A good draft should:

- feel like something a real team would reuse
- be specific enough to shape work
- avoid unnecessary implementation detail
- avoid generic consultant-like language
- be short enough that a person or AI would actually use it

## Good Outcomes

A good use of this skill should:

- help the user discover what context is actually reusable
- produce a Frame that is clear and practical
- reduce the amount of repeated explanation the user has to do later
- leave the user with something they can refine over time
