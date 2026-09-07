# Spec And Implementation

> Status note: the v0.3 working draft ([../spec/frame-spec.md](../spec/frame-spec.md)) states this boundary formally in its conformance model (Section 3.3) and conformance profiles (Section 7).

This note clarifies the boundary between the Frame spec and systems that use Frames.

## Spec

The spec should define:

- what a Frame is
- what format it uses
- what metadata or content claims it may carry
- what those claims mean

Examples:

- `type`
- `name`
- `description`
- `visibility`
- optional `scope`

Frame Spec v0.2 defines inheritance. The v0.3 working draft adds identity (`identifier`, `canonicalSource`) and provenance (`derivedFrom`, `previousVersion`).

## Implementation

Implementation should define:

- where Frames are stored
- how they are discovered
- who is allowed to see or install them
- how they are combined at runtime
- how they are trimmed for model context
- how they are indexed, cached, mounted, or versioned in a specific product

Examples:

- RBAC (role-based access control)
- virtual filesystem (VFS) mounting
- registry lookup
- runtime layering
- product-specific activation behavior (for example, in Collab)

## The Important Middle

Some topics touch both sides.

For example, layering may need:

- a small spec surface for portable meaning
- implementation-specific logic for actual runtime realization

That means the spec may define a small amount of relationship or precedence metadata (the v0.3 working draft does, in its Section 5) without trying to define the full management system.

## Current Position

For `v0.2`, the repo prioritizes:

- a tiny adopt-now spec
- manual shareability
- learning from real use

It intentionally does not try to standardize the full management layer yet.
