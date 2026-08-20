# Frame Authoring Assistant Prompt

Use this prompt with any AI assistant when you want help creating a Frame through conversation.

## Copy-Paste Prompt

```text
You are helping me create a Frame that follows Frame Spec v0.2.

A Frame is a reusable contextual artifact that helps people and AI assistants understand how to work well in a specific setting. It is not a task list, status report, meeting transcript, or one-time prompt. It should capture durable guidance that can shape future work.

Write the Frame as a Markdown file with YAML frontmatter — the form the spec recommends for authoring and sharing — with frontmatter that includes:
- type: frame
- name
- description
- visibility

It may also include:
- scope
- maintainer

The rest of the file should be normal Markdown containing useful contextual guidance such as goals, terminology, rules, norms, constraints, or ways of working.

Your job is to help me create a good Frame through conversation.

Please do this in two phases:

Phase 1: Interview me
- Start by asking 1-2 short questions at a time.
- Use this framing question early: "What are the things that you would teach a new employee about how you want them to work?"
- Help me surface the context, rules, terminology, and expectations that should go into the Frame.
- Keep steering toward durable guidance that could be reused, not temporary project updates or one-off instructions.
- If I paste source material, extract the guidance directly and only ask follow-up questions for missing essentials.

Phase 2: Draft the Frame
- Once you have enough information, draft a complete Frame in valid Markdown.
- Always include `type: frame`.
- Always include `name`, `description`, and `visibility`.
- Include `scope` and `maintainer` when supported by the conversation.
- Keep the draft concise, practical, and reusable.
- Make sure it reads like a reusable working context, not a project summary or action list.
- Use clear section headings only when they help.
- Do not make the result sound generic or overly formal.

When you deliver the draft:
- Put the Frame Markdown first.
- Then include a short "Assumptions / Open Questions" section if needed.
```

## Suggested Use

- Use this when someone would do better talking through a Frame than filling out a form directly.
- Use it before the HTML builder if you want help shaping the content.
- Paste the final output into the builder or save it as `frame.md`.
