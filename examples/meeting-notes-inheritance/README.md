# Meeting Notes — Inheritance Example

This example shows a parent/child inheritance pattern for consistent, composable output across different audiences.

## The frames

- `meeting-notes.frame.md` — parent frame. Turns a meeting transcript into house-style notes: action items first, then themed discussion sections.
- `meeting-notes-persona1.frame.md` — child frame. Additive: outputs only a GitHub Issues section derived from the meeting.
- `meeting-notes-persona2.frame.md` — child frame. Additive: outputs only a per-participant program-manager briefing.

## How to use them

Import and activate the parent frame alone in Collab, or paste it into another AI chat with your meeting notes, to get clean meeting notes — action items first, then themed discussion sections.

Import and activate a child frame alone to get just that output (either formatted notes for GitHub Issues or a per-participant program-manager briefing).

Import and activate the parent and a child together to get both — each printed exactly once, no duplication (the full meeting notes plus the GitHub Issues section, or the full meeting notes plus the program-manager briefing).

## What this demonstrates

Each child frame declares what it adds and what it does not reproduce. This keeps output consistent and composable without the parent needing to know about its children.

Frames produced shorter, more specific responses than prompting without them — the AI applies the structure consistently instead of inferring it each time.
