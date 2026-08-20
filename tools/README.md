# Tools

This directory contains lightweight tools and aids for authoring `v0.2` Frames.

## Frame Builder

Open [frame-builder.html](frame-builder.html) in a browser.

The builder helps non-technical users produce:

- valid `type: frame` frontmatter
- the required `v0.2` metadata fields
- a Markdown body using common Frame sections
- many kinds of Frames, not just style or brand guides

The generated output can be:

- copied into another tool
- saved as `frame.md`
- shared by email, chat, or git

This builder is intentionally simple and tracks the current [../spec/frame-spec.md](../spec/frame-spec.md) spec.

It starts in a guided blank state and lets the user load an example on demand.

## AI-Guided Authoring

This directory also includes lightweight AI authoring aids:

- [frame-authoring-assistant-prompt.md](frame-authoring-assistant-prompt.md): a copy-paste prompt for any chat-based AI assistant
- [customer-shared-frame-prompt.md](customer-shared-frame-prompt.md): a copy-paste prompt for creating a shared Frame between your organization and a customer
- [frame-authoring-assistant/SKILL.md](frame-authoring-assistant/SKILL.md): a reusable skill for AI-assisted Frame interviews and drafting

These are meant for people who would rather talk through a Frame than build it from scratch in the form.

## AI-Guided Use

This directory also includes a lightweight usage aid:

- [frame-reader/SKILL.md](frame-reader/SKILL.md): a standalone skill for reading one or more Frames, determining which are active for a task, resolving likely precedence, and applying them consistently

This is meant to help ordinary AI tools use Frames more reliably without requiring a dedicated runtime or access to this repository.

## Frame Validator

Use [validate_frames.py](validate_frames.py) as a lightweight preflight check for `v0.2` Frame frontmatter.

It is dual-purpose:

- Maintainer / CI use: keeps the repository's own example Frames from drifting away from the `v0.2` minimum spec.
- Author use: gives someone writing a Frame a quick preflight check before sharing it or opening a PR.

Run it on a single file or a directory:

```
python validate_frames.py path/to/frame.md
python validate_frames.py path/to/frame.json
python validate_frames.py examples
```

It checks that a Frame has the required fields (`type`, `name`, `description`, `visibility`) and that its metadata is present and readable. Both serializations are covered: Markdown with YAML frontmatter, and JSON. A Markdown file with no frontmatter, or a JSON file whose `type` does not claim to be a Frame, is skipped rather than failed. It exits with a non-zero status if any Frame fails, so it can run in CI.

For the fuller, schema-based check, see [../spec/schema/README.md](../spec/schema/README.md).

### Scope

The scope of this validator is limited to lightweight Frame metadata checks for authoring and repository example hygiene. It does not:

- validate full YAML
- check anything about body content
- certify Frame quality or correctness
- define runtime behavior
- enforce Collab, registry, or deployment behavior
- replace human review

