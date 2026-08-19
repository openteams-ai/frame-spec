# Examples

These examples show what Frames look like in practice. They fall into three groups.

## Canonical v0.2 Examples

These use only what the released [v0.2 spec](../spec/v0.2.md) defines. Start here.

- [minimal/](minimal/) — the smallest valid Frame, using only the required fields.
- [complete/](complete/) — a fuller Frame that also uses the suggested fields, including `inherits`.
- [minimal-self-frame/](minimal-self-frame/) — a self-referential Frame that uses the minimum spec to describe the spec itself.
- [spec-stewardship-frame/](spec-stewardship-frame/) — a Frame capturing stewardship guidance for this spec.

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

Check any Frame against the required v0.2 fields with:

```bash
python tools/validate_frames.py examples
```
