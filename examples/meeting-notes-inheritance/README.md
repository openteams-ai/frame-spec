# Meeting Notes — Inheritance Example

This example shows a parent/child inheritance pattern for consistent, composable output across different audiences.

## The frames

- `meeting-notes.frame.md` — parent frame. Turns a meeting transcript into house-style notes: action items first, then themed discussion sections.
- `meeting-notes-persona1.frame.md` — child frame. Additive: outputs only a GitHub Issues section derived from the meeting.
- `meeting-notes-persona2.frame.md` — child frame. Additive: outputs only a per-participant program-manager briefing.

## How to use them

Run the parent alone to get clean meeting notes.

Run a child alone to get just that output.

Run the parent and a child together to get both — each printed exactly once, no duplication.

## What this demonstrates

Each child frame declares what it adds and what it does not reproduce. This keeps output consistent and composable without the parent needing to know about its children.

Frames produced shorter, more specific responses than prompting without them — the AI applies the structure consistently instead of inferring it each time.
