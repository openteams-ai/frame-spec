# Conformance profiles

Section 7 of the working draft requires every implementation to publish a
conformance profile: a short declaration of which optional behaviors it
performs. Appendix C gives the human-readable template. The files here are
the same declarations in YAML so that `tools/validate_frame.py --check-profile`
can verify them and `--compose --conformance-profile` can apply them.

The files here are examples. They illustrate the template and give
`--check-profile` something to run against; they describe no real
implementation. A profile is published by the implementation it describes,
so a real one belongs with that implementation rather than here.

| File | Illustrates |
|---|---|
| [registry.yaml](registry.yaml) | a reader that resolves composition transitively and narrows several elements |
| [desktop.yaml](desktop.yaml) | the minimum a profile must state, from a reader that resolves no composition |
