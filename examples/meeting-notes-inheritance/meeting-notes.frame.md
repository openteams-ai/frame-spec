---
type: frame [0.2]
version: 0.1.0
name: Meeting Notes
description: Turns a raw meeting transcript into house-style notes — action items first, then themed discussion sections — the same way regardless of who runs it. Parent frame for person- and project-specific note variations.
visibility: internal
scope: team
maintainer: example
---

# Meeting Notes

Turn a meeting transcript into clean, shareable notes. Derive the notes from the
transcript itself; use any AI-generated summary only as a cross-check. If no
transcript is given, ask for it.

## Output

**Action Items first**, then **themed discussion sections.**

### Action Items
Checkbox list, **each item on its own line with a blank line between items**
so they render as separate lines: `[ ] Full Name to verb-phrase the task.`
Lead with the owner's full name + a verb. Capture implied tasks, not just
stated ones. If ownership is unclear, write `[ ] [owner?] …` — don't guess.

### Themed Discussion Sections
3–6 sections, each with a short header naming the theme (derived from what
was discussed, not a fixed list). Bullet what happened and why. Fold
decisions into the relevant section, attributed to who made them. Order by
importance.

Correct obvious transcription errors from context. Never assert something
the transcript doesn't support.

## Customization
Parent frame. Child frames keep this structure as the baseline and add to it.
