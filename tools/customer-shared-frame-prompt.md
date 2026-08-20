# Customer Shared Frame Prompt

Use this prompt with any AI assistant when you want help creating a Frame for shared work between your organization and a customer.

This is meant for situations where the Frame should capture how both sides want the engagement to work, not just your organization's internal preferences.

## Copy-Paste Prompt

```text
You are helping me create a shared Frame that follows Frame Spec v0.2.

A Frame is a reusable contextual artifact that helps people and AI assistants understand how to work well in a specific setting. It is not a task list, status report, meeting transcript, or one-time prompt. It should capture durable guidance that can shape future work.

This Frame is for work between my organization and a customer, so it should capture the shared context that will help both people and AI assistants work well across the engagement.

Write the Frame as a Markdown file with YAML frontmatter — the form the spec recommends for authoring and sharing — with frontmatter that includes:
- type: frame
- name
- description
- visibility

It may also include:
- scope
- maintainer

The rest of the file should be normal Markdown containing useful contextual guidance.

Your job is to help me create a practical shared-customer Frame through conversation.

Please do this in two phases.

Phase 1: Interview me
- Ask 1-2 short questions at a time.
- Use this framing question early: "If a new team member from my organization and a new customer team member were starting this work together next week, what would you want them both to understand about how the engagement should work?"
- Help me surface the shared goals, ways of working, terminology, constraints, success criteria, and communication expectations that should go into the Frame.
- Keep steering toward reusable engagement guidance, not temporary project updates or one-off instructions.
- If I paste source material such as statements of work, onboarding docs, discovery notes, meeting notes, or email summaries, extract the guidance directly and only ask follow-up questions for missing essentials.

As you interview me, look for:
- what the customer is trying to achieve
- how my organization is expected to help
- what success looks like
- who the main participants are
- preferred communication and decision-making patterns
- known constraints, sensitivities, or non-goals
- important terminology, domain language, or business context
- boundaries around confidentiality, approvals, or escalation

Phase 2: Draft the Frame
- Once you have enough information, draft a complete Frame in valid Markdown.
- Always include `type: frame`.
- Always include `name`, `description`, and `visibility`.
- Prefer `visibility: shared` unless the conversation clearly points to another value.
- Include `scope` and `maintainer` when supported by the conversation.
- Keep the draft concise, practical, and reusable.
- Make sure it reads like a reusable shared working context, not a project summary or action list.
- Write it so it can be shared with both my organization and the customer.
- Avoid internal-only language, private assumptions, or implementation details that should not be in a shared artifact.
- Use clear section headings only when they help.

Good shared Frame sections often include:
- Goals
- Shared Context
- Terminology
- Ways Of Working
- Constraints
- Communication
- Success Criteria
- Escalation

When you deliver the draft:
- Put the Frame Markdown first.
- Then include a short "Assumptions / Open Questions" section if needed.
- If you see anything that feels too internal for a shared Frame, call it out explicitly.
```

## Suggested Use

- Use this when your organization and a customer need a shared working context for a project, onboarding effort, delivery engagement, or ongoing collaboration.
- Use it when someone has source material but needs help turning it into a reusable shared Frame.
- Paste the final output into the HTML builder or save it directly as `frame.md`.

## What Makes This Different

This prompt is more specific than the general Frame authoring prompt.

It is designed to produce a Frame that:

- can be shared across organizational boundaries
- reflects both provider and customer concerns
- avoids internal-only assumptions
- clarifies how the engagement should work in practice
