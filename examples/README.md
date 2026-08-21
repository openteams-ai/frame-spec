# Examples

These examples show what Frames look like in practice. They fall into three groups.

## Canonical v0.2 Examples

These use only what the released [v0.2 spec](../spec/v0.2.md) defines. Start here.

A reminder as you read them: `v0.2` requires four frontmatter fields and nothing else. The body is free-form, and none of these examples' section headings are required by the spec.

- [minimal/](minimal/) — the smallest valid Frame, using only the required fields.
- [code-review-norms/](code-review-norms/) — a Frame with only the four required fields and a genuinely useful body, showing that the value lives in the body rather than the metadata.
- [with-suggested-fields/](with-suggested-fields/) — a fuller Frame that also uses the suggested fields, including `inherits`.
- [minimal-self-frame/](minimal-self-frame/) — a self-referential Frame that uses the minimum spec to describe the spec itself.
- [spec-stewardship-frame/](spec-stewardship-frame/) — a Frame capturing stewardship guidance for this spec.

## Working-Draft Examples

These follow the [working draft](../spec/frame-spec.md) rather than released `v0.2`. The draft defines a Frame as metadata plus a body instead of as a Markdown file, so it permits serializations `v0.2` did not.

Both are the same Frame as [code-review-norms/](code-review-norms/), field for field. Read the three together — that equivalence *is* the change.

- [yaml-serialization/](yaml-serialization/) — as a YAML document, with the body as a literal block scalar. The only defined form that carries the body as data and keeps it readable.
- [json-serialization/](json-serialization/) — as JSON, with the body as an escaped string. Machine-friendly, and unpleasant to hand-edit.

## Illustrative Working Examples

Real-world-shaped Frames contributed from practice. They are valid v0.2 Frames and may also use extra fields that the spec permits but does not define.

- [sow-review/](sow-review/) — a set of review-lens Frames for evaluating a Statement of Work.
- [risk-identification-norms/](risk-identification-norms/) — norms a delivery organization uses to spot engagement risk.
- [meeting-notes-inheritance/](meeting-notes-inheritance/) — a parent Frame with per-participant children, including notes on how one tool handled `inherits`.

## Future-Facing Sketches

These explore ideas beyond v0.2, such as packaging and distribution. They are illustrative only and do not describe adopted spec behavior.

- [self-frame/](self-frame/) — a richer, future-oriented spec sketch in package form.
- [nebi-frame-package/](nebi-frame-package/) — how a Frame package could carry packaging metadata. See [../docs/ecosystem.md](../docs/ecosystem.md) for what Nebi is.

## Validating

Check any Frame against the required fields — in any of the three serializations — with:

```bash
python tools/validate_frames.py examples
```

That needs nothing installed. For the fuller check against the schemas, which also catches YAML type coercion:

```bash
python -m pip install jsonschema pyyaml
python tools/schema_check.py examples
```

CI runs both. For the field-by-field schemas, see [../spec/schema/README.md](../spec/schema/README.md).
