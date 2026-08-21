# YAML Serialization Example

This is [../code-review-norms/frame.md](../code-review-norms/frame.md) — the same Frame, written as a YAML document instead of Markdown with frontmatter.

The four required fields become keys of the top-level mapping, and the body becomes the `body` key, written as a literal block scalar (`body: |`).

## Why This One Matters

Of the three defined serializations, YAML is the only one that carries the body **as data** while keeping it **readable**. A block scalar needs no escaping, so the body looks the same as it does in the Markdown form — just indented two spaces.

That makes YAML the practical middle ground:

| | Body is addressable data | Body is readable |
| --- | --- | --- |
| Markdown + frontmatter | no — it is the rest of the file | yes |
| YAML | yes | yes |
| JSON | yes | no — one escaped string |

Compare all three side by side: this file, [../code-review-norms/frame.md](../code-review-norms/frame.md), and [../json-serialization/frame.json](../json-serialization/frame.json). Parse the YAML and the JSON and you get the same object, key for key; take the YAML's `body` and it is the Markdown file's body, character for character. That equivalence is what the draft means by defining the shape rather than the medium.

Markdown is still the reference serialization — the form to send when a Frame crosses a boundary and nothing else has been agreed.

## Quote What YAML Would Coerce

Every field the spec defines is a string, and YAML coerces unquoted scalars by type. This Frame has no field at risk, but a fuller one does:

```yaml
version: "1.2"          # unquoted, 1.2 parses as a number
visibility: "shared"    # `yes` and `no` would parse as booleans
maintainer: "2026-08-20"  # some parsers read this as a date
```

The schema enforces this — a coerced value fails the `"type": "string"` constraint rather than being silently stringified. See [../../spec/schema/README.md](../../spec/schema/README.md).

## Draft, Not v0.2

This is **not** a valid `v0.2` Frame. Released `v0.2` requires a Markdown file, so a YAML Frame is a draft-only artifact — which is why `type` declares `frame [0.3]` rather than `frame [0.2]`.

Treat it as illustrating the working draft ([../../spec/frame-spec.md](../../spec/frame-spec.md)), not adopted spec behavior. If you need a Frame that today's tools will accept, write the Markdown form.

## Validating

```bash
python ../../tools/validate_frames.py frame.yaml
```

Or against the schema, from the repository root:

```bash
python tools/schema_check.py
pipx run check-jsonschema --schemafile spec/schema/frame-document.schema.json examples/yaml-serialization/frame.yaml
```
