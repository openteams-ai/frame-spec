# Design Note

> Historical note: this design note predates the first released spec (v0.2.0) and is preserved as background.

## Problem

Organizations need a way to preserve and share cultural and operational context so that both humans and Cogs (see [ecosystem.md](ecosystem.md)) can work from a coherent base.

That context is rarely absent. It is usually implicit.

It lives in:

- terminology habits
- brand and tone expectations
- regulatory and policy constraints
- team norms
- project goals
- process expectations
- informal institutional memory

The problem is not creating context from nothing. The problem is making the right context explicit, portable, inheritable, and shareable.

## Why Existing Artifacts Are Not Enough

Existing documents often fail because they are:

- too fragmented
- too informal
- too static
- too local to one team or one tool
- too dependent on people already knowing the surrounding context

Frames are intended to fill the gap between:

- raw institutional memory
- operational documents
- runnable programs
- one-off prompts

## Frame Characteristics

A useful Frame should be:

- scoped
- text-based
- inheritable
- reviewable
- readable by humans
- usable by Cogs
- shareable when appropriate

It should also remain a first-class artifact rather than becoming a hidden attribute of another system.

## What Is Still Open

Important unresolved questions include:

1. What minimum metadata should every Frame require?
2. Which content sections should be standard versus optional?
3. How should inheritance and exceptions work?
4. What review states should be visible to both humans and Cogs?
5. How should source and decision references be represented?
6. What should a built-in Collab sharing workflow require?
7. How much should the first spec optimize for human authoring versus machine validation?

## Current Boundary

The Frame spec should remain distinct from:

- Cogs
- Ops
- application-specific UI objects
- one particular packaging system

The spec may be packaged and distributed through [Nebi](ecosystem.md), but Nebi should not define what a Frame means.

## Product Direction

One likely product direction is that Frame sharing becomes a built-in feature of [Collab](ecosystem.md).

That suggests a few design constraints:

- a Frame should still exist as a normal text artifact or folder outside the app
- Collab should discover, import, export, and attach Frames without redefining the spec
- review state, provenance, and scope should remain visible outside the app

## Recommended Near-Term Path

1. Define a small v0 spec.
2. Create real example Frames.
3. Test inheritance, sharing, and provenance against real use.
4. Use Nebi as a likely packaging and versioning path without overcommitting too early.
5. Add stronger validation only after the basic model feels natural in practice.
