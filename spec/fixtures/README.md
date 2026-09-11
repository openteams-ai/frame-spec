# Fixtures

Test inputs for the v0.3 working draft, each tied to a claim the draft makes.

| Directory | Claim | Check |
|---|---|---|
| [encodings/](encodings/) | The same Frame written as Markdown, YAML, and JSON normalizes to the same element model (Figures 6 to 8 of the draft) | `tools/test_framespec_encodings_fixture.py` |
| [roundtrip/](roundtrip/) | A Frame with all ten refinements, a `guards` reference, and an `x-` extension survives markdown to json to yaml to markdown with every element value intact | `python tools/validate_frame.py --round-trip spec/fixtures/roundtrip/full.frame.md` |
| [composition/](composition/) | The three-Frame chain of section 5.5 resolves to exactly the outputs the rules predict, at the model level and under a profile that narrows `style` | `python tools/validate_frame.py --compose ...` diffed against `expected-model.json` and `expected-style-non-repeatable.json` |
| [composition/](composition/) | Rule 6: a single empty value is present for the replace branch and clears a value the composed Frame would otherwise inherit | `python tools/validate_frame.py --compose ...` on `style-clear-parent.frame.json` and `style-clear-child.frame.json`, diffed against `expected-style-cleared.json` |
| [composition/](composition/) | Rule 6: where a profile deduplicates identical values, the first occurrence in the concatenation is the one kept | `python tools/validate_frame.py --compose ...` on `dedup-parent.frame.json` and `dedup-child.frame.json`, diffed against `expected-dedup.json` |

Fixtures are validated in CI with `python tools/validate_frame.py examples spec/fixtures`.
