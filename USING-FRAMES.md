# Using Frames

This guide is for people who want to use Frames in everyday AI work.

It is intentionally practical.

It does not require any special infrastructure.

## What A Frame Is

A Frame is a small document that carries context for work.

In everyday use that means a Markdown file with a few fields at the top — `type`, `name`, `description`, and `visibility` — and the context itself written below. That is the form this guide uses throughout, and the form to send when you share a Frame with someone else.

The spec itself defines the fields and the body rather than the file format, so a tool may also hold a Frame as JSON or as a record in its own storage. That matters if you are building something; it does not change how you write one. Write the Markdown file.

That context might include:

- goals
- terminology
- rules
- norms
- style guidance
- process expectations
- customer or partner context

Include only what applies to you. The spec requires four fields and nothing more, so there are no sections you have to fill in and no minimum length. One clear rule in the body is a perfectly good Frame.

Think of a Frame as a reusable context document that helps an AI tool work in the right way for your team, company, customer, or project.

## What Frames Are Good For

Use a Frame when you want the AI to work with context that should be reused across many tasks.

Examples:

- how your department works
- how the company talks about itself
- how to work with a specific customer
- what counts as compliant or acceptable in a proposal
- what terminology or reporting style should be used

If the context is durable and should shape repeated work, it is a good candidate for a Frame.

## What Frames Are Not

- **Not organizational memory.** A frame is not a wiki, knowledge base, or repository of everything the org knows. It carries a specific slice — intent, meaning, purpose, judgment — not a complete record.
- **Not the full context for a model or prompt.** The task-specific context — the request itself, attachments, tool output, app state — still arrives separately from the frame. A frame travels alongside that context, not in place of it.
- **Not a Cog or Op.** A frame doesn't execute anything. It orients the Cog that does (a Cog is an AI worker; an Op is a workflow that coordinates Cogs and humans). Frames carry context; Cogs consume it; Ops coordinate the work.
- **Not a one-off prompt.** If it only applies to one task, it belongs in the prompt. A frame earns its place when the same intent, norms, or judgment needs to travel across multiple tasks, tools, or agents.
- **Not a substitute for deterministic computation.** If the output can be produced by a formula or a script, use the formula or the script. A frame can guide how the result is interpreted, framed, or reported, but it should not replace the calculation itself.

## Common Frame Patterns

Many teams will likely end up using more than one Frame.

Common patterns include:

- a company-wide Frame
- a department Frame
- a project or campaign Frame
- a customer or partner Frame
- a task-family Frame, such as pricing or past performance

You do not need to force everything into one large Frame.

Often it is better to keep reusable context in a few scoped Frames than in one giant document.

## When To Use One Frame

Use one Frame when:

- one clear source of context is enough
- the task is specific to one team, one customer, or one scope
- there is no important interaction between different contexts

Examples:

- drafting copy using only the company brand Frame
- answering a customer question using only that customer's Frame

## When To Use Multiple Frames

Use multiple Frames when the task depends on more than one layer of context.

Examples:

- company brand Frame plus marketing department Frame
- customer success department Frame plus customer-specific Frame
- company Frame plus public sector proposal Frame plus pricing Frame

As a working rule:

- broader Frames provide defaults
- narrower Frames refine the task

If multiple Frames are active, tell the AI what the task is and which Frames matter most.

## Suggested Way To Provide Frames To An AI Tool

When using Claude, ChatGPT, Gemini, Codex, or another AI tool:

1. Attach or paste the relevant Frame files.
2. Briefly explain the task.
3. State which Frames should be treated as active.
4. If more than one Frame is attached, say which one is more specific.
5. Ask the AI to use the Frames before answering.

Example:

```text
I am attaching three Frames:

- the company brand Frame
- the marketing department Frame
- the customer Frame for Acme

Please use all three, with the customer Frame as the most specific context for this task.

The task is to draft a follow-up email after a discovery meeting.

If the Frames conflict or leave something unclear, tell me before drafting.
```
## A Note On Sensitive Data

Frames are pasted into external AI tools, so treat them like any other data you share with an outside service. Before using a Frame that contains customer, partner, or other confidential information, follow your organization's data-handling rules. Do not paste sensitive or restricted content into an external AI tool unless your organization permits it.

## Suggested Prompt Pattern

If you are not using a dedicated Frame-reading skill yet, this lightweight pattern is usually enough:

```text
Please read the attached Frame files first.

For this task:
- identify what each Frame governs
- apply the most relevant and most specific guidance
- tell me if the Frames conflict
- tell me if the Frames do not provide enough context

Task: ...
```

## How To Think About Specificity

When more than one Frame applies, the more specific Frame usually matters more for the immediate task.

Typical order:

- company
- department
- project or campaign
- customer, partner, or proposal

This is a working guideline, not a formal spec rule.

If there is a real conflict, it is better for the AI to flag it than to silently guess.

## Examples By Team

### Marketing

Likely Frame set:

- company brand Frame
- marketing department Frame
- campaign or audience Frame when needed

Example tasks:

- website copy
- campaign messaging
- partner-facing collateral

### Customer Success

Likely Frame set:

- customer success department Frame
- customer-specific Frame
- customer-segment Frame when multiple customers share a common pattern

Example tasks:

- account planning
- response drafting
- renewal preparation

### Public Sector / Proposals

Likely Frame set:

- department Frame
- pricing Frame
- past-performance Frame
- customer, opportunity, or proposal Frame

Example tasks:

- compliance analysis
- pricing preparation
- proposal drafting

## What To Put In A Frame Versus In A Prompt

Put it in a Frame when:

- it should be reused often
- it reflects durable team or organizational context
- it should remain available across many tasks

Keep it in the task prompt when:

- it only matters for this one request
- it is a one-off instruction
- it is about the immediate deliverable rather than durable context

Examples:

- "Our team always separates confirmed facts from assumptions." -> Frame
- "Write this as a 150-word email." -> task prompt

## What To Avoid

- Do not attach every Frame you have if only one or two are relevant.
- Do not assume the AI will know which Frame matters most unless you say so.
- Do not mix stale context with active context without clarifying which is current.
- Do not bury critical rules in a giant Frame if they really belong in a more specific scoped Frame.

## If The AI Seems To Use A Frame Poorly

Try these steps:

1. Reduce the number of active Frames.
2. Tell the AI which Frame is most specific.
3. Ask it to summarize the Frames before doing the task.
4. Separate durable context from one-off task instructions.
5. Revise the Frame if the context itself is unclear or overly broad.

## Related Aids

- Use [tools/frame-authoring-assistant-prompt.md](tools/frame-authoring-assistant-prompt.md) to help create new Frames.
- Use [tools/frame-authoring-assistant/SKILL.md](tools/frame-authoring-assistant/SKILL.md) for AI-guided Frame authoring.
- Use [tools/frame-reader/SKILL.md](tools/frame-reader/SKILL.md) when your AI tool supports reusable skills and you want more consistent Frame consumption.
- Use `tools/validate_frames.py` as a lightweight preflight check that a Frame has the required fields.
