---
type: frame [0.2]
version: 0.1.0
name: Meeting Notes — Persona 1
description: Child frame. Outputs only a GitHub Issues section derived from the meeting. Run it alone for just issues, or alongside the parent Meeting Notes frame to get notes + issues with no duplication.
visibility: internal
scope: user:persona1
maintainer: smcmillan@openteams.com
inherits: ./meeting-notes.frame.md
---

# Meeting Notes — Persona 1 (Issues)

**Output only the GitHub Issues section below** — do not reproduce the meeting
notes. This frame is additive: run it **alone** to get just the issues, or
**together with the parent Meeting Notes frame** to get notes + issues, each
printed exactly once.

## GitHub Issues

Convert the meeting's work into issues ready to add to a GitHub project board.
Format it so it is ready to add to GitHub manually or to pass to an issue-creation assistant or workflow.

### What becomes an issue
- One issue per **discrete deliverable or task** — usually each action item,
  but split a broad action into multiple issues, and merge trivially related ones.
- Only for **work to be done** — not discussion, FYIs, or finished items.

### Sub-issues
When one task is a **more specific instance or component of another**, make it
a **sub-issue** of that other one. Mark it with a `Parent: <exact Parent Title>`
line first in its block.

### Format
Each issue is a block in exactly this shape, separated by `---`:

```
### Title: <concise title, Title Case>
Parent: <exact Parent Title>   ← only on sub-issues; omit for top-level

<optional 1–2 lines of context/notes>

# DOD
- [ ] <specific, checkable completion criterion>
```

Rules:
- **Title** is a short noun phrase, not a sentence.
- **`Parent:`** appears only on sub-issues; its value must match the parent
  issue's Title exactly.
- **Notes are optional** and come before the Definition of Done (DOD). Keep them brief.
- **`# DOD` is required** on every issue — concrete, verifiable bullets
  describing the done state, not steps. Derive them from what was discussed.
