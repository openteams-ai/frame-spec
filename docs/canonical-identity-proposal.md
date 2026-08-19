# Canonical Identity Proposal

This document is a future proposal for later spec versions.

It is not part of the minimum `v0.2` definition.

## Purpose

This note proposes an exact `v1` shape for canonical identity and authoritative-source metadata in the Frame spec.

The goal is to let a consumer answer these questions consistently:

- Is this Frame the authoritative published version, a copy, an export, or a fork?
- What other copies of this Frame are semantically the same artifact?
- Where should a system look for updates?
- What lineage does this Frame have?
- What trust signal, if any, comes with this Frame?

This proposal is intentionally limited to spec metadata.

It does not define:

- how a Hub resolves remote references
- how a marketplace indexes Frames
- how signatures are verified
- how trust policies are enforced

## Design Goals

The model should be:

- portable across files, packages, hubs, and marketplaces
- self-describing when copied out of its original environment
- precise enough for tooling
- simple enough for human authors to understand
- neutral about storage and transport systems

## Proposed Metadata Shape

Suggested top-level section:

```yaml
identity:
  frame_id: "acme.brand.voice"
  version: "1.2.0"
  publisher: "acme"
  canonical_source:
    uri: "nebi://acme/frames/brand-voice"
    digest: "sha256:3b7e4c..."
  authority:
    status: "official"
    maintained_by:
      - "marketing-ops"
  lineage:
    derived_from:
      - "acme.brand.voice@1.1.0"
    variant_of: null
```

## Field Definitions

### `identity.frame_id`

Stable identifier for the semantic Frame across copies, exports, and mirrored publications.

Requirements:

- required
- string
- stable across versions of the same logical Frame
- assigned by the publishing authority

Examples:

- `acme.brand.voice`
- `nebari.community.contribution-guide`
- `health-consortium.hipaa.compliance`

Meaning:

- two artifacts with the same `frame_id` and different `version` values are different versions of the same logical Frame
- two artifacts with different `frame_id` values are different logical Frames, even if their content overlaps

### `identity.version`

Version of this artifact instance.

Requirements:

- required
- string
- must compare deterministically under the versioning rules the spec adopts

Recommendation:

- use semver-style strings in `v1`

Meaning:

- identifies which released revision of a Frame this artifact represents
- allows update checks and compatibility reasoning

### `identity.publisher`

Human-meaningful identifier for the entity claiming authorship or stewardship.

Requirements:

- required
- string

Examples:

- `acme`
- `nebari-community`
- `contoso-legal`

Meaning:

- helps disambiguate authority and namespace ownership
- is not by itself proof of authenticity

### `identity.canonical_source`

Reference to the authoritative publication source for this version of the Frame.

Suggested fields:

```yaml
canonical_source:
  uri: "nebi://acme/frames/brand-voice"
  digest: "sha256:3b7e4c..."
```

Requirements:

- `uri` required
- `digest` optional but strongly recommended

Meaning:

- `uri` identifies where the authoritative record for this Frame version is published
- `digest` identifies the exact content instance expected for this artifact

Notes:

- the spec should not require a single URI scheme
- `nebi://` (a hypothetical scheme for [Nebi](ecosystem.md), an environment management tool from OpenTeams) is a good reference example, not the only possible form
- an OCI registry reference (for example `quay.io/acme/frames/brand-voice:1.2.0`) is another plausible concrete form, since Nebi already publishes to OCI registries
- the `uri` may point to a package publication, registry entry, or stable manifest path

### `identity.authority`

Portable trust and stewardship hint carried with the Frame.

Suggested fields:

```yaml
authority:
  status: "official"
  maintained_by:
    - "marketing-ops"
```

Suggested `status` values:

- `official`
- `community`
- `partner`
- `fork`
- `local`
- `deprecated`

Semantics:

- `official`: published by the steward intended to be treated as canonical
- `community`: broadly shared artifact without a single organizational owner
- `partner`: shared by a partner for joint or limited use
- `fork`: intentionally diverged from another published Frame
- `local`: local or user-managed artifact without broader publication authority
- `deprecated`: retained for history or compatibility but no longer preferred

Notes:

- this is a hint, not an enforcement mechanism
- consumers may combine it with signatures, ACLs, registry trust, or local policy

### `identity.lineage`

Lineage metadata for derivation and adaptation.

Suggested fields:

```yaml
lineage:
  derived_from:
    - "acme.brand.voice@1.1.0"
  variant_of: null
```

Definitions:

- `derived_from`: one or more prior Frames this artifact was adapted from
- `variant_of`: a stable parent identity when this artifact is a named branch or localized variant rather than a new independent Frame

When to use:

- use `derived_from` for exports, revisions, forks, and local adaptations
- use `variant_of` when the artifact remains clearly subordinate to a canonical parent

Example:

```yaml
identity:
  frame_id: "contoso.partner-safe.brand.voice"
  version: "1.0.0"
  publisher: "contoso"
  canonical_source:
    uri: "nebi://contoso/frames/partner-safe-brand-voice"
  authority:
    status: "partner"
  lineage:
    derived_from:
      - "contoso.brand.voice@2.3.0"
    variant_of: "contoso.brand.voice"
```

## Normative Interpretation Rules

These are the core semantics recommended for `v1`.

### Rule 1

`frame_id` identifies the logical Frame, not the physical file.

### Rule 2

`frame_id + version + publisher` should uniquely identify a published Frame version within the spec.

### Rule 3

`canonical_source.uri` identifies the authoritative publication location for that version, not necessarily the current file location of a copy.

### Rule 4

If `canonical_source.digest` is present, consumers may use it to determine whether a copied artifact matches the authoritative published content.

### Rule 5

`authority.status` is descriptive spec metadata and must not by itself be treated as cryptographic proof.

### Rule 6

Derived or exported Frames should preserve lineage to their source when practical, even if they receive a new `frame_id`.

### Rule 7

A local copy of an official Frame should normally preserve the original `frame_id`, `version`, and `canonical_source`, while a true fork or adapted derivative should declare lineage and may receive a new `frame_id`.

## Recommended Behaviors

These are not strict spec requirements, but they are the behaviors the model is designed to support.

### Official published Frame

- retains its stable `frame_id`
- publishes a canonical source URI
- carries `authority.status: official`

### Mirrored copy

- preserves the same `frame_id`
- preserves the same `version`
- preserves the same `canonical_source`
- may add local provenance elsewhere in the document

### Reviewed export

- may preserve the same `frame_id` if it is a byte-equivalent or semantically equivalent published export
- should receive a new `frame_id` if it materially changes content or scope
- should always preserve lineage to the source

### Local adaptation

- should declare `derived_from`
- may use `authority.status: local`
- may keep `variant_of` pointing to the parent canonical Frame

### Intentional fork

- should receive a new `frame_id`
- should declare `derived_from`
- should normally use `authority.status: fork`

## Examples

### Example 1: Official company Frame

```yaml
identity:
  frame_id: "acme.brand.voice"
  version: "1.2.0"
  publisher: "acme"
  canonical_source:
    uri: "nebi://acme/frames/brand-voice"
    digest: "sha256:3b7e4c..."
  authority:
    status: "official"
    maintained_by:
      - "marketing-ops"
  lineage:
    derived_from: []
    variant_of: null
```

### Example 2: Local installed copy

```yaml
identity:
  frame_id: "acme.brand.voice"
  version: "1.2.0"
  publisher: "acme"
  canonical_source:
    uri: "nebi://acme/frames/brand-voice"
    digest: "sha256:3b7e4c..."
  authority:
    status: "official"
    maintained_by:
      - "marketing-ops"
  lineage:
    derived_from: []
    variant_of: null
```

This artifact would differ from the canonical publication through separate provenance metadata, not through a changed identity block.

### Example 3: Partner-safe derivative

```yaml
identity:
  frame_id: "acme.partner-safe.brand.voice"
  version: "1.0.0"
  publisher: "acme"
  canonical_source:
    uri: "nebi://acme/frames/partner-safe-brand-voice"
    digest: "sha256:91aa22..."
  authority:
    status: "official"
    maintained_by:
      - "marketing-ops"
  lineage:
    derived_from:
      - "acme.brand.voice@1.2.0"
    variant_of: "acme.brand.voice"
```

### Example 4: Customer-local fork

```yaml
identity:
  frame_id: "contoso.local.brand.voice"
  version: "0.1.0"
  publisher: "contoso"
  canonical_source:
    uri: "hub://contoso/local-frames/brand-voice"
  authority:
    status: "local"
    maintained_by:
      - "contoso-marketing"
  lineage:
    derived_from:
      - "acme.brand.voice@1.2.0"
    variant_of: "acme.brand.voice"
```

## Open Questions

These are the main design choices still worth debating:

1. Should `version` be mandatory on every draft, or only on published artifacts?
2. Should `frame_id` be globally unique by convention, or formally namespaced by publisher?
3. Should `variant_of` accept only a `frame_id`, or a fully qualified `frame_id@version`?
4. Should `canonical_source` permit multiple URIs for mirrored authorities, or exactly one primary URI?
5. Should the spec require a signature field in `v1`, or leave signatures to packaging and registry layers?

## Recommendation

For `v1`, the recommendation is:

1. Make `frame_id`, `version`, `publisher`, and `canonical_source.uri` required for published Frames.
2. Strongly recommend `canonical_source.digest`.
3. Include `authority.status` and `lineage` as optional but standard fields.
4. Keep signatures and trust enforcement out of the core Frame document spec unless the maintainers decide they are essential for that release.

That gives the spec a clean notion of "official version" without tying it to any single implementation.
