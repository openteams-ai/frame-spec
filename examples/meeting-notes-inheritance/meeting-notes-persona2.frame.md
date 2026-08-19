---
type: frame [0.2]
version: 0.1.0
name: Meeting Notes — Persona 2
description: Child frame. Outputs only a per-participant program-manager briefing. Run it alone for just the briefing, or alongside the parent Meeting Notes frame to get notes + briefing with no duplication.
visibility: internal
scope: user:persona2
maintainer: example
inherits: ./meeting-notes.frame.md
---

# Meeting Notes — Persona 2 (Briefing)

**Output only the Participant Briefing section below** — do not reproduce the meeting
notes. This frame is additive: run it **alone** to get just the briefing, or
**together with the parent Meeting Notes frame** to get notes + briefing, each
printed exactly once.

Reads notes as a **program manager**: where each person left off, what they're
carrying now, and what could slip.

## Participant Briefing

For **each attendee of the current meeting**, one block, program-manager lens:

```
### <Full Name> — <role, if known>

- **Last meeting:** <what they said / committed to / raised last time>
- **Current work:** <one- or two-line memory-jog on what they're working on now>
- **Risks & dependencies:** <slippage risk, blockers, cross-person dependencies — or
  "none surfaced">
```

Rules:
- **One block per current-meeting attendee**, ordered by centrality to the discussion,
  not alphabetically.
- **Last meeting** draws on the previous meeting's notes. No prior meeting, or they
  weren't there → `_No prior meeting found_` / `_Not present last meeting_`. Don't guess.
- **Current work** is a short memory-jog on what they're doing now — it orients the
  reader, it isn't a full status report.
- **Risks & dependencies** surfaces slippage, blockers, and dependencies **supported by
  the notes.** None → "none surfaced"; don't manufacture risk.
- Attribute only what the notes support; correct obvious name-transcription errors from
  context, same as the parent.
