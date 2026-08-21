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
python validate_frames.py path/to/frame.yaml
python validate_frames.py path/to/frame.json
python validate_frames.py examples
```

It checks that a Frame has the required fields (`type`, `name`, `description`, `visibility`) and that its metadata is present and readable. All three serializations are covered: Markdown with YAML frontmatter, YAML, and JSON. A Markdown file with no frontmatter, or a YAML or JSON file whose `type` does not claim to be a Frame, is skipped rather than failed — so a package manifest or a CI config in the tree does not break the run. It exits with a non-zero status if any Frame fails, so it can run in CI.

### Scope

The scope of this validator is limited to lightweight Frame metadata checks for authoring and repository example hygiene. It does not:

- validate full YAML
- model YAML's type coercion
- check anything about body content
- certify Frame quality or correctness
- define runtime behavior
- enforce Collab, registry, or deployment behavior
- replace human review

## Schema Check

Use [schema_check.py](schema_check.py) for the fuller check: a real JSON Schema validator and a real YAML parser, run against the schemas in [../spec/schema/](../spec/schema/README.md).

```
python -m pip install jsonschema pyyaml
python schema_check.py ../examples
```

It picks the schema by serialization — frontmatter for Markdown Frames, the document schema for YAML and JSON — and it also confirms the schemas themselves are valid draft 2020-12, so a typo in a schema fails loudly rather than passing everything.

The two checks are complementary, which is why CI runs both:

| | `validate_frames.py` | `schema_check.py` |
| --- | --- | --- |
| Dependencies | none | `jsonschema`, `pyyaml` |
| Missing or empty required field | caught | caught |
| Malformed `type` token | caught | caught |
| YAML coercion, e.g. `version: 1.2` | missed — it reads text | caught |
| Malformed YAML | mostly missed | caught |
| Wrong shape, e.g. `inherits: [4]` | missed | caught |

Neither one certifies that a Frame is any good. A Frame can validate perfectly and still be vague, stale, or too long to read.

