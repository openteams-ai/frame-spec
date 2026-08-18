# Frame Spec V1 Gap Analysis

This document is future-facing.

It is meant to inform later versions of the spec after `v0.2`, not to define the minimum adopt-now format.

## Purpose

This note translates the alignment review against revision 5 of the [Intelligence Hub whitepaper](https://github.com/openteams-ai/inthub-whitepaper) into a concrete spec-focused gap list for `frame-spec v1`.

(For definitions of Cogs, Ops, Collab, and Nebi, see [ecosystem.md](ecosystem.md).)

The `v5` whitepaper sharpens several assumptions that were only implicit in `v4`, especially around organizational memory, policy-governed access to shared context, and reviewable selective sharing. Those additions increase the importance of identity, governance, and composition work for later versions, but they do not require a conceptual reset of the current Frame spec direction.

The current repository already aligns strongly with the whitepaper's core definition of a Frame:

- a scoped artifact for organizational context
- readable by humans
- usable by Cogs
- inheritable and shareable
- distinct from Cogs, Ops, Collab, and Nebi

What the whitepaper adds is not a replacement of the current direction, but a stronger set of product and ecosystem assumptions that the spec will eventually need to support.

## Alignment Summary

The repository and whitepaper are already aligned on:

- Frames as first-class artifacts
- Frames as a separate layer from Cogs and Ops
- open spec plus text-first artifact shape
- inheritance across organizational scopes
- selective sharing across boundaries
- Nebi as packaging and distribution infrastructure
- Collab as a consumer and management surface rather than the source of truth

This means the spec does not need a conceptual reset.

It does need a sharper `v1` contract.

## Main Gaps

The whitepaper assumes several capabilities that the current repository only hints at or leaves open.

### 1. Composition is underdefined

The current draft talks clearly about inheritance, but the whitepaper assumes active composition of multiple Frames in a single work session:

- company
- department
- project
- partner
- regulatory
- personal or ad-hoc

Current docs describe inheritance well enough for a hierarchy, but they do not yet define:

- how multiple sibling Frames are combined
- whether composition is ordered or graph-based
- how conflicts are resolved
- how temporary or session-local layers behave

This is the largest spec gap.

### 2. Sharing is too coarse-grained

The current sketch has document/package visibility states such as `private`, `internal`, `shared`, and `public`.

The whitepaper assumes finer control:

- selective external sharing
- field-level or section-level redaction
- reviewed subsets for partner or vendor use

Document-level visibility alone is not enough for the sharing model described in the whitepaper.

### 3. Local memory is not modeled

The whitepaper introduces a local-first Collab behavior in which a user's active context is composed from:

- inherited organizational Frames
- installed external Frames
- authored personal Frames
- temporary or session-specific Frames

The current spec draft avoids application-specific objects, which is good, but it still needs a way to represent the provenance and lifecycle of:

- local-only context
- promoted context
- imported context
- shared derived context

Without that, local memory becomes an application feature with no portable representation.

### 4. Publication and discovery metadata are incomplete

The current draft treats discoverability as a goal, but the package manifest does not yet define enough metadata for the whitepaper's marketplace and library model.

Missing or weak areas include:

- audience and publication target
- discoverability controls
- topic/domain classification
- trust and stewardship metadata
- compatibility with Hub, Cog, or Op expectations

### 5. Review and governance semantics are too light

The current draft includes `status`, `owners`, `reviewers`, `source_refs`, and `decision_refs`.

The whitepaper expects more operational governance:

- accountable authors
- suggested changes
- review workflows
- scoring or structured feedback
- publishability gates
- auditability for how a Frame was applied

The spec does not need to encode a full workflow engine, but it should expose enough state for multiple tools to implement one consistently.

### 6. Scope taxonomy is too narrow for the whitepaper

The current scope examples cover company, department, team, project, partner, and vendor.

The whitepaper also implies:

- user or personal scope
- role-based scope
- community or consortium scope
- temporary ad-hoc session scope

These do not all need equal weight in `v1`, but the spec should stop acting as if organizational hierarchy alone is sufficient.

### 7. The relationship to Cogs and Ops needs a stronger contract

The current repo correctly keeps Frames separate from Cogs and Ops.

The whitepaper goes further and assumes:

- Cogs declare or receive applicable Frames
- Ops declare required or recommended Frames
- a Hub can apply local Frames during install or execution

The Frame spec does not need to absorb Cog or Op semantics, but it should define the minimum interoperable contract those systems rely on.

### 8. Nebi packaging is still too ambiguous for v1

The current docs intentionally leave room for `nebi.toml`, `pixi.toml`, or another wrapper.

That flexibility is reasonable for a sketch, but the whitepaper assumes Nebi-backed installation and lifecycle management are concrete enough to support marketplace exchange.

For `v1`, the spec should choose one minimal packaging integration pattern, even if it remains explicitly provisional.

### 9. Canonical identity and official-source semantics are missing

The current draft has package and document identifiers, but it does not yet define how a consumer distinguishes between:

- the authoritative published version of a Frame
- a local copy
- a reviewed export
- a fork
- a derived variant

The whitepaper's marketplace, sharing, and local-memory model all become much harder to govern without a portable notion of canonical identity and authoritative source.

This is not only a marketplace issue.

It also affects:

- cache invalidation
- update detection
- provenance
- trust and stewardship
- duplicate detection across Hubs
- promotion of local or derived Frames back into shared libraries

Without an explicit canonical-source concept, different systems will invent their own ideas of what "official" means, usually based on storage location. That would make the spec less portable and less trustworthy.

See [canonical-identity-proposal.md](canonical-identity-proposal.md) for a more exact field-level proposal.

## Recommended V1 Additions

The following additions would move the current draft closer to the whitepaper's implied requirements without collapsing the spec into application-specific behavior.

### A. Add explicit composition metadata

Add a document-level section for how a Frame participates in composition.

Suggested fields:

```yaml
composition:
  combine_mode: "merge"
  precedence: 300
  compatible_with:
    - "scope-type:project"
    - "scope-type:regulatory"
  conflicts_with:
    - "frame:deprecated-brand-voice"
  conflict_resolution:
    terminology: "replace"
    rules: "exception-only"
    style: "extend"
```

Intent:

- `combine_mode` defines whether the Frame is normally merged, layered, or used as an exclusive substitute
- `precedence` provides a deterministic ordering rule
- `compatible_with` and `conflicts_with` help tooling avoid incoherent combinations
- `conflict_resolution` allows section-specific rules without forcing every consumer to invent its own merge logic

This should complement inheritance, not replace it.

### B. Add shareability controls below whole-document visibility

Add section-level policy and export metadata.

Suggested fields:

```yaml
sharing:
  visibility: "internal"
  export_policy: "reviewed-subset-only"
  allowed_audiences:
    - "partner"
    - "vendor"
  section_policies:
    terminology: "shareable"
    goals: "shareable"
    rules: "conditional"
    architecture: "internal-only"
  export_profiles:
    - id: "partner-safe"
      include_sections:
        - "terminology"
        - "goals"
        - "style"
    - id: "vendor-compliance"
      include_sections:
        - "rules"
        - "business_process"
```

Intent:

- preserve coarse visibility for humans
- add machine-readable export behavior for partner and marketplace flows
- support the whitepaper's selective sharing model

### C. Add provenance for local, imported, and promoted Frames

Introduce optional provenance fields that let local-first tools remain portable.

Suggested fields:

```yaml
provenance:
  origin: "local"
  derived_from:
    - "frame:acme.company.core@1.2.0"
  imported_via:
    kind: "marketplace"
    source: "acme"
  promotion:
    promotable: true
    target_classes:
      - "user-library"
      - "team-library"
```

Suggested `origin` values:

- `local`
- `hub`
- `marketplace`
- `partner`
- `community`
- `derived`

This keeps the spec text-based while supporting the whitepaper's local memory and promotion story.

### D. Expand publication and discovery metadata

Strengthen package metadata for libraries and marketplaces.

Suggested package fields:

```yaml
publication:
  discoverability: "listed"
  audiences:
    - "internal"
    - "community"
  channels:
    - "hub-library"
    - "marketplace"
  maintainers:
    - "marketing-ops"
  tags:
    - "brand"
    - "sales"
    - "compliance"
  domain:
    - "healthcare"
  maturity: "stable"
  trust_signals:
    reviewed: true
    publisher_verified: true
```

This helps bridge the gap between a package manifest and a real discovery surface.

### E. Strengthen review and governance fields

Add enough structure to support auditable review and feedback across tools.

Suggested fields:

```yaml
governance:
  accountable_authors:
    - "legal-ops"
  review_policy:
    required_for:
      - "external-sharing"
      - "marketplace-publication"
  feedback_channels:
    suggestions: true
    scoring: true
  scoring_model:
    scale:
      - -10
      - -1
      - 0
      - 1
      - 10
```

Suggested document history entry shape:

```yaml
review_log:
  - at: "2026-05-22"
    actor: "product-lead"
    action: "approved"
    notes: "Approved for internal use and partner-safe export profile."
```

This does not make the spec workflow-heavy, but it does make it governable.

### F. Expand scope support

Keep the existing `scope` identifier model, but broaden the recommended scope types in the spec.

Suggested additions:

- `user`
- `role`
- `community`
- `consortium`
- `session`

Example:

```text
user:acme/alex
role:acme/legal-reviewer
community:nebari/contributors
session:acme/demo/onboarding
```

This matters because the whitepaper explicitly assumes personal Frames, community Frames, and temporary active composition.

### G. Define a minimal interoperability contract for Cogs and Ops

The Frame spec should state what an external system can rely on.

Suggested interoperable concepts:

- a Frame exposes `scope`
- a Frame exposes `status`
- a Frame exposes `sharing` policy
- a Frame exposes composition semantics
- a Frame exposes provenance and review metadata

Suggested non-goals:

- defining Cog manifests
- defining Op execution logic
- defining UI state for Collab

This boundary should be made explicit in the spec.

### H. Choose a provisional Nebi wrapper pattern for v1

The spec should not let packaging define meaning, but `v1` should standardize one reference packaging path so examples, validators, and marketplace tooling do not drift.

Recommended near-term choice:

- keep `frame/package.yaml` and `frame/*.yaml` as the semantic source
- define one official Nebi integration example for `v1`
- treat any alternative wrapper as out of scope until `v1.1`

The exact wrapper can still be marked provisional, but the repo should stop demonstrating multiple top-level directions as peers.

### I. Add canonical identity and authoritative-source fields

The spec should define how a Frame carries its stable identity and how it points to the artifact or publication record that should be treated as authoritative.

Suggested fields:

```yaml
identity:
  frame_id: "acme.brand.voice"
  version: "1.2.0"
  publisher: "acme"
  canonical_source:
    uri: "nebi://acme/frames/brand-voice"
    digest: "sha256:abcd1234"
  authority:
    status: "official"
    maintained_by:
      - "marketing-ops"
  derived_from:
    - "acme.brand.voice@1.1.0"
```

Suggested `authority.status` values:

- `official`
- `community`
- `partner`
- `fork`
- `local`
- `deprecated`

Intent:

- `frame_id` gives a stable identifier across copies and exports
- `version` allows update and compatibility comparison
- `canonical_source` identifies the authoritative publication source without forcing a single storage system
- `digest` supports immutability and integrity checks
- `authority` gives consumers a portable trust hint
- `derived_from` clarifies lineage when a Frame has been forked, localized, or adapted

This should be defined as spec metadata, while resolution and enforcement remain implementation choices.

## Proposed Minimum V1 Contract

At minimum, `v1` should require:

1. A package manifest.
2. One or more Frame documents.
3. Explicit `scope`.
4. Explicit `inherits_from`.
5. Explicit `status`.
6. Explicit document or section sharing policy.
7. Explicit provenance references.
8. Deterministic composition behavior.
9. Stable identity and canonical-source metadata.

That is the smallest useful jump from the current draft to something that matches the whitepaper's assumptions.

## Suggested New Spec Sections

The current docs would benefit from adding these formal sections when the spec is written:

1. Composition Model
2. Sharing and Export Model
3. Provenance and Promotion Model
4. Publication and Discovery Metadata
5. Review and Governance Semantics
6. Canonical Identity and Authority
7. Scope Taxonomy
8. Interoperability Contract for Cogs, Ops, and Hub Consumers
9. Official Nebi Packaging Profile

## Suggested Examples To Add

The next examples in this repo should test the hard parts directly.

### Example 1: Layered active session

Show composition of:

- company Frame
- department Frame
- project Frame
- partner-safe Frame
- user personal Frame

This should demonstrate precedence and conflict behavior.

### Example 2: Selective external sharing

Show one internal Frame with:

- internal-only architecture
- shareable terminology
- review-gated partner export profile

This should demonstrate how one source Frame can produce a safe external view.

### Example 3: Community Frame

Show a community or consortium-published Frame with:

- public discoverability
- steward metadata
- recommended scope applicability

This would align well with the whitepaper's ecosystem claims.

### Example 4: Promoted local Frame

Show a user-authored local Frame that is later promoted to a team library with provenance intact.

This would test the whitepaper's local-memory story without forcing Collab-specific objects into the spec.

### Example 5: Official Frame plus derived fork

Show:

- one official published Frame
- one partner-safe export
- one local derivative
- explicit linkage back to the canonical source

This would test identity, authority, and update behavior directly.

## Prioritized V1 Roadmap

If the spec needs to sequence work, this is the order that best matches the whitepaper while keeping the design tractable.

### Priority 1

- define composition rules
- define section-level sharing and export behavior
- choose one official Nebi packaging profile

### Priority 2

- define provenance and local-to-shared promotion semantics
- expand publication/discovery metadata
- define review and governance fields
- define canonical identity and authoritative-source fields

### Priority 3

- broaden scope taxonomy
- write interoperability notes for Cogs and Ops
- add marketplace-oriented validation fixtures

## Bottom Line

The whitepaper validates the current repository's direction.

It also raises the bar for what `frame-spec v1` must specify.

The key shift is this:

- the current repo defines what a Frame is
- the whitepaper assumes a spec mature enough to support composition, selective sharing, local memory, promotion, discoverability, and auditable governance

That gap is bridgeable without changing the core philosophy of the repo.
