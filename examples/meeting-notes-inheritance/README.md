# Meeting Notes — Inheritance Example

This example shows a parent/child inheritance pattern for consistent, composable output across different audiences.

## The frames

- `meeting-notes.frame.md` — parent frame. Turns a meeting transcript into house-style notes: action items first, then themed discussion sections.
- `meeting-notes-persona1.frame.md` — child frame. Additive: outputs only a GitHub Issues section derived from the meeting.
- `meeting-notes-persona2.frame.md` — child frame. Additive: outputs only a per-participant program-manager briefing.

## How to use them

Import and activate the parent frame alone in Collab ([openteams.com/collab](https://openteams.com/collab/)), an OpenTeams desktop app that applies Frames, or paste it into another AI chat with your meeting notes, to get clean meeting notes — action items first, then themed discussion sections.

In the tested Collab workflow, import and activate a child frame alone to get just that child output (either formatted notes for GitHub Issues or a per-participant program-manager briefing).

To get combined output in that workflow, import and activate the parent and a child together — each is printed exactly once, with no duplication (the full meeting notes plus the GitHub Issues section, or the full meeting notes plus the program-manager briefing).

In this test, Collab required manual activation of both Frames because it did not automatically resolve the `inherits` reference. In an implementation that supports Frame Spec v0.2 inheritance resolution, activating the child should resolve and load the parent automatically, combining their guidance with the child taking precedence where they conflict.

## What this demonstrates

Each child frame declares what it adds and what it does not reproduce. This keeps output consistent and composable without the parent needing to know about its children.

Frames produced shorter, more specific responses than prompting without them — the AI applies the structure consistently instead of inferring it each time.
