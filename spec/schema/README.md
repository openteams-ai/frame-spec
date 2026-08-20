# Schemas

Machine-readable schemas for the two serializations defined by the [working draft](../frame-spec.md).

Both describe the **same Frame shape** — metadata plus a body. They differ only in where the body lives: in the Markdown serialization it is the text after the frontmatter, so the schema covers the frontmatter alone; in the JSON serialization it is a member of the object, so the schema covers it too.

| File | Validates | Body |
| --- | --- | --- |
| [frame-frontmatter.schema.json](frame-frontmatter.schema.json) | the parsed YAML frontmatter of a Markdown Frame | not covered — it is the text after the closing `---` |
| [frame.schema.json](frame.schema.json) | a JSON Frame object | covered, as the optional `body` string |

Both are JSON Schema draft 2020-12.

## Fields

| Field | Type | Status | Constraint |
| --- | --- | --- | --- |
| `type` | string | **required** | `frame`, or `frame [<major>.<minor>]` |
| `name` | string | **required** | non-empty |
| `description` | string | **required** | non-empty |
| `visibility` | string | **required** | non-empty; `private` / `internal` / `shared` / `public` are suggested, not enforced |
| `version` | string | recommended | non-empty; no scheme enforced |
| `scope` | string | recommended | non-empty; no grammar enforced |
| `maintainer` | string | recommended | non-empty |
| `inherits` | string, or array of non-empty unique strings | recommended | at least one entry if an array |
| `body` | string | optional | JSON serialization only; unconstrained content |
| anything else | any | optional | permitted and not validated |

Three deliberate choices in these schemas:

- **`visibility` is not an `enum`.** The spec suggests four values but does not close the set, so the schema lists them as `examples`. A schema that rejected a fifth value would be stricter than the spec.
- **`version` has no pattern.** The spec says a Frame tracks its own revisions and deliberately does not mandate a versioning scheme. `0.1.0`, `1.2.0`, and `2026-08-20` all validate.
- **`additionalProperties` is `true`.** Extension fields are permitted by the spec — several examples in this repository use them. A conforming implementation ignores fields it does not understand rather than rejecting the Frame.

The schemas do not constrain the body's structure, because the spec defines no required sections, no expected sections, and no section taxonomy. Any schema that required sections would be describing a house style, not the spec.

## Applies To Which Version

`frame-frontmatter.schema.json` also validates released [`v0.2`](../v0.2.md) Frames: the required fields, recommended fields, and `type` grammar are unchanged by the draft, and `v0.2` required exactly this serialization.

`frame.schema.json` describes a serialization that `v0.2` did not define. A JSON Frame declaring a spec version should declare `frame [0.3]` or later.

## Validating

Neither schema needs special tooling to be useful — `tools/validate_frames.py` in this repository applies the same rules with the standard library alone, for both serializations:

```bash
python tools/validate_frames.py examples
```

To validate against the schemas themselves, use any JSON Schema validator. With [check-jsonschema](https://github.com/python-jsonschema/check-jsonschema):

```bash
pipx run check-jsonschema --schemafile spec/schema/frame.schema.json examples/json-serialization/frame.json
```

Validating a Markdown Frame means parsing its frontmatter first, since the schema describes the parsed mapping rather than the file:

```python
import json, jsonschema, yaml, pathlib

text = pathlib.Path("examples/minimal/frame.md").read_text()
_, frontmatter, _ = text.split("---", 2)

jsonschema.validate(
    yaml.safe_load(frontmatter),
    json.loads(pathlib.Path("spec/schema/frame-frontmatter.schema.json").read_text()),
)
```

## Scope

These schemas check shape, not quality. A Frame can validate perfectly and still be useless — vague, stale, or too long to read. Validation is a preflight check, not a review.
