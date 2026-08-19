# Collab Sharing

One likely product direction is that Frame sharing becomes a built-in feature of [Collab](ecosystem.md), OpenTeams' desktop app and hub.

That suggests a few spec-level requirements.

## Required Qualities

- A Frame should remain a normal text artifact or folder outside the app.
- Collab should discover, import, export, and attach Frames without redefining the spec.
- Review state should remain visible outside the app.
- Provenance should remain visible outside the app.
- Scope and visibility should remain explicit outside the app.

## Likely Collab Behaviors

A Collab client may eventually need to:

- browse available Frames
- inspect Frame metadata before attaching or importing
- show scope, inheritance, review status, and sharing boundaries
- import Frame packages from [Nebi](ecosystem.md)-backed sources
- export reviewed Frames for partner sharing

## Current Recommendation

Design the spec so Collab can be a consumer and sharing surface, not the sole source of truth.
