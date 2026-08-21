# Schemas

Machine-readable schemas for the serializations defined by the [working draft](../frame-spec.md).

The draft defines three serializations and this directory holds two schemas, because a schema validates a *parsed data model* rather than a file. YAML and JSON parse into the same model, so one schema covers both. What separates the two files is where the body lives.

| File | Validates | Body |
| --- | --- | --- |
| [frame-frontmatter.schema.json](frame-frontmatter.schema.json) | the parsed YAML frontmatter of a Markdown Frame | not covered — it is the text after the closing `---` |
| [frame-document.schema.json](frame-document.schema.json) | a parsed YAML or JSON Frame document | covered, as the optional `body` string |

Both are JSON Schema draft 2020-12.

One document schema rather than two near-identical ones is deliberate: duplicated files that must be kept in step will drift, and drift in a normative artifact is a conformance bug. If a future serialization needs constraints YAML and JSON do not share, that is the moment to split it.

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
| `body` | string | optional | document serializations only; unconstrained content |
| anything else | any | optional | permitted and not validated |

Three deliberate choices in these schemas:

- **`visibility` is not an `enum`.** The spec suggests four values but does not close the set, so the schema lists them as `examples`. A schema that rejected a fifth value would be stricter than the spec.
- **`version` has no pattern.** The spec says a Frame tracks its own revisions and deliberately does not mandate a versioning scheme. `0.1.0`, `1.2.0`, and `2026-08-20` all validate.
- **`additionalProperties` is `true`.** Extension fields are permitted by the spec — several examples in this repository use them. A conforming implementation ignores fields it does not understand rather than rejecting the Frame.

The schemas do not constrain the body's structure, because the spec defines no required sections, no expected sections, and no section taxonomy. Any schema that required sections would be describing a house style, not the spec.

## Where The String Constraints Earn Their Keep

`"type": "string"` on every field looks like boilerplate until the serialization is YAML — and both frontmatter and the YAML document form are YAML.

YAML coerces unquoted scalars by type:

```yaml
version: 1.2          # a number, not "1.2"
visibility: yes       # a boolean in YAML 1.1 parsers, not "yes"
maintainer: 2026-08-20  # a date in some parsers
```

All three fail validation, which is the intended behavior. Quote them:

```yaml
version: "1.2"
visibility: "yes"
maintainer: "2026-08-20"
```

An implementation should reject a field that arrives as the wrong type rather than stringifying it, so that a Frame means the same thing everywhere it is read.

## Applies To Which Version

`frame-frontmatter.schema.json` also validates released [`v0.2`](../v0.2.md) Frames: the required fields, recommended fields, and `type` grammar are unchanged by the draft, and `v0.2` required exactly this serialization.

`frame-document.schema.json` describes serializations `v0.2` did not define. A YAML or JSON Frame declaring a spec version should declare `frame [0.3]` or later.

## Validating

Two checks live in [../../tools/](../../tools/README.md), and CI runs both:

```bash
python tools/validate_frames.py examples        # standard library only, all three serializations
python tools/schema_check.py                   # the schemas themselves, and every example against them
```

`validate_frames.py` needs nothing installed and does a lightweight structural check. `schema_check.py` is the real thing — it needs `jsonschema` and `pyyaml`:

```bash
python -m pip install jsonschema pyyaml
```

Or point any JSON Schema validator at a Frame directly. With [check-jsonschema](https://github.com/python-jsonschema/check-jsonschema), which reads YAML and JSON alike:

```bash
pipx run check-jsonschema --schemafile spec/schema/frame-document.schema.json \
  examples/yaml-serialization/frame.yaml examples/json-serialization/frame.json
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
