# Conformance profiles

Section 7 of the working draft requires every implementation to publish a
conformance profile: a short declaration of which optional behaviors it
performs. Appendix C gives the human-readable template. The files here are
the same declarations in YAML so that `tools/validate_frame.py --check-profile`
can verify them and `--compose --conformance-profile` can apply them.

A profile is a description of an implementation's behavior, not an
endorsement of it. Where a profile records behavior observed from outside
rather than declared by the implementation's maintainers, its `notes` say so.

| File | Implementation |
|---|---|
| [nebari-frames.yaml](nebari-frames.yaml) | Nebari Frames registry |
| [collab.yaml](collab.yaml) | Collab desktop application (observed behavior) |
