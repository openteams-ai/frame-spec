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

This builder is intentionally simple and generates Frames in the released v0.2 format ([../spec/v0.2.md](../spec/v0.2.md)), which the working draft preserves as its Markdown encoding.

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
python validate_frames.py examples
```

It checks that a Markdown Frame has the required `v0.2` frontmatter fields (`type`, `name`, `description`, `visibility`) and that the frontmatter block is present and readable. It exits with a non-zero status if any Frame fails, so it can run in CI.

### Scope

The scope of this validator is limited to lightweight `v0.2` Frame frontmatter checks for authoring and repository example hygiene. It does not:

- validate full YAML
- certify Frame quality or correctness
- define runtime behavior
- enforce Collab, registry, or deployment behavior
- replace human review

## Validating against the working draft

[validate_frame.py](validate_frame.py) checks Frames against the v0.3 working
draft in all three encodings, driven from
[../spec/profile/frame-core.csv](../spec/profile/frame-core.csv):

```bash
python tools/validate_frame.py examples spec/fixtures          # validate files or directories
python tools/validate_frame.py --round-trip spec/fixtures/roundtrip/full.frame.md
python tools/validate_frame.py --self-check                     # CSV versus the draft's prose
python tools/validate_frame.py --check-profile spec/profiles/*.yaml
python tools/validate_frame.py --compose A.frame.json B.frame.json C.frame.json
```

It never rejects a Frame for an unrecognized element, an unregistered
`status` or `visibility` value, an unrecognized heading, or the form of a
reference; those are warnings or information, as the draft requires. PyYAML
is optional: without it, Markdown front matter is parsed by the same
line-based parser `validate_frames.py` uses, and the YAML encoding cannot be
read. `validate_frames.py` remains the check for the released v0.2 format.
