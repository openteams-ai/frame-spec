# JSON Serialization Example

This is [../code-review-norms/frame.md](../code-review-norms/frame.md), byte-for-byte the same Frame, written in the JSON serialization instead of Markdown with frontmatter.

Same four required fields, same body text, same meaning. The only difference is the container: the frontmatter mapping became the top-level object, and the Markdown body became the `body` string.

## Why This Example Exists

To make the draft's central point concrete: a Frame is metadata plus a body, not a file format. Compare the two files side by side and the shape is identical — which is the argument for defining the shape rather than the medium.

It also shows the tradeoff honestly. The body here is one escaped string with `\n` for every line break. That is fine for a program reading it out of an API response or a database column, and unpleasant for a person editing it by hand. Markdown remains the reference serialization for exactly that reason.

## Draft, Not v0.2

This is **not** a valid `v0.2` Frame. Released `v0.2` requires a Markdown file, so a JSON Frame is a draft-only artifact — which is why `type` declares `frame [0.3]` rather than `frame [0.2]`.

Treat it as illustrating the working draft ([../../spec/frame-spec.md](../../spec/frame-spec.md)), not adopted spec behavior. If you need a Frame that today's tools will accept, write the Markdown form.

## Validating

```bash
python ../../tools/validate_frames.py frame.json
```

Or against the schema directly, from the repository root:

```bash
pipx run check-jsonschema --schemafile spec/schema/frame.schema.json examples/json-serialization/frame.json
```

See [../../spec/schema/README.md](../../spec/schema/README.md) for both schemas.
