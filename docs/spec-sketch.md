# Spec Sketch

This document is a future-facing sketch, not the current adopt-now spec. The field names and structure below do not correspond to the released v0.2 format; see [../spec/v0.2.md](../spec/v0.2.md) for the current spec.

For immediate use, see [../spec/frame-spec.md](../spec/frame-spec.md).

This document describes a first draft shape for Frame artifacts and the packages that may carry them.

It is a working sketch, not yet a finalized specification.

## Spec Goals

The first version should optimize for:

- human readability
- Cog usability
- explicit scope
- explicit inheritance
- portable identity
- explicit review state
- selective sharing
- diffability in version control

It should not yet optimize for:

- maximum compactness
- full graph semantics
- dynamic remote resolution
- advanced execution behavior

## Conceptual Layers

The spec currently assumes five layers.

### 1. Frame

The Frame is the primary semantic artifact.

It answers:

- what context applies within a scope
- what is normative, preferred, or descriptive
- what humans and Cogs should understand there

### 2. Package

The package is the delivery unit.

It answers:

- what is being distributed
- who published it
- what version it is
- what Frames it contains
- what other packages it depends on

### 3. Document

The document is the concrete file representation of a Frame.

It answers:

- what artifact identity it claims
- what scope it applies to
- what it inherits from
- what is visible or shareable
- what review state it has

### 4. Section

Sections group content into common categories such as:

- vision
- goals
- terminology
- rules
- norms
- skills
- tool specifications
- prompts
- architecture
- business process
- style
- review
- escalation

### 5. Policy

Policies express concrete expectations inside sections such as:

- required behavior
- preferred behavior
- forbidden behavior
- advisory background

## Frame As File Or Folder

A Frame may be represented as:

- a single structured file
- a folder of files with one main manifest

The spec should allow both, though the examples below use a folder of files.

## Suggested Package Layout

```text
frame-package/
  nebi.toml
  frame/
    package.yaml
    company.yaml
    department.research.yaml
    project.alpha.yaml
  references/
    glossary.md
    rationale.md
```

Interpretation:

- `nebi.toml` carries packaging metadata if [Nebi](ecosystem.md) is used
- `frame/package.yaml` is the Frame package manifest
- each `frame/*.yaml` file defines one scoped Frame document
- `references/` holds supporting human-facing material

## Package Manifest Draft

```yaml
spec_version: "1.0-draft"
package_id: "acme.operating-frame"
package_version: "0.1.0"
package_name: "Acme Operating Frame"
publisher: "acme"
summary: "Shared cultural and operational context for Acme internal teams and approved partners."
default_format: "yaml"
root_scope: "company:acme"
frames:
  - "company.yaml"
  - "department.research.yaml"
  - "project.alpha.yaml"
dependencies:
  - package_id: "common.agent-coordination"
    version: "^0.2"
distribution:
  visibility: "internal"
  exportable_scopes:
    - "partner:acme-contoso"
review:
  status: "approved"
  approved_by:
    - "ops-lead"
    - "product-lead"
source_refs:
  - kind: "document"
    uri: "file://references/glossary.md"
    role: "terminology-source"
decision_refs:
  - kind: "decision"
    uri: "file://references/rationale.md"
    role: "package-rationale"
```

## Frame Document Draft

```yaml
identity:
  frame_id: "acme.company.core"
  version: "1.2.0"
  publisher: "acme"
  canonical_source:
    uri: "nebi://acme/frames/company-core"
    digest: "sha256:4d5e6f"
  authority:
    status: "official"
    maintained_by:
      - "leadership"
  lineage:
    derived_from: []
    variant_of: null
document_id: "acme.company.core"
scope: "company:acme"
inherits_from: []
applies_to:
  entity_types:
    - "human"
    - "agent"
visibility: "internal"
status: "approved"
priority: 100
summary: "Core company-wide operating context."
owners:
  - "leadership"
reviewers:
  - "operations"
effective_date: "2026-05-18"
source_refs:
  - kind: "document"
    uri: "file://references/glossary.md"
    role: "terminology-source"
decision_refs:
  - kind: "decision"
    uri: "file://references/rationale.md"
    role: "scope-rationale"
sections:
  vision:
    intent:
      - "Help teams act with long-term clarity rather than short-term local optimization."
  terminology:
    preferred_terms:
      - term: "Frame"
        prefer_over:
          - "memory file"
  goals:
    objectives:
      - "Preserve coherent operating context across sessions and teams."
  rules:
    required:
      - "Escalate when a local optimization conflicts with stated priorities."
    forbidden:
      - "Treat unreviewed exported Frames as approved shared truth."
  style:
    communication:
      - "Be direct, calm, and precise."
  norms:
    expectations:
      - "Make important assumptions explicit when collaboration spans teams."
```

## Canonical Identity And Authority

Frames should remain self-describing even when copied between:

- repositories
- hubs
- local memory
- partner exports
- marketplaces

That means a consumer should be able to tell, from the artifact itself:

- what logical Frame this is
- which version it represents
- who published or stewards it
- where its authoritative published source lives
- whether it should be treated as official, local, partner-provided, or forked
- what lineage it has

The spec should therefore carry a structured identity block with fields such as:

- `frame_id`
- `version`
- `publisher`
- `canonical_source`
- `authority`
- `lineage`

Suggested semantics:

- `frame_id` identifies the logical Frame across copies and versions
- `version` identifies the revision of that logical Frame
- `publisher` identifies the publishing or stewarding entity
- `canonical_source.uri` points to the authoritative published source for that version
- `canonical_source.digest` optionally identifies the expected immutable content
- `authority.status` expresses whether the artifact claims to be `official`, `community`, `partner`, `fork`, `local`, or `deprecated`
- `lineage` preserves derivation when a Frame is exported, adapted, or forked

This should be treated as spec metadata, not as an implementation-specific registry lookup.

External systems may still maintain indexes, caches, and assignment graphs, but those should complement rather than replace artifact-local identity metadata.

## Scope Model

The current draft assumes explicit scope identifiers:

```text
<scope-type>:<scope-id>
```

Examples:

- `company:acme`
- `department:acme/research`
- `team:acme/research/agents`
- `project:acme/research/atlas`
- `partner:acme-contoso`
- `vendor:acme-legal`

## Inheritance Rules

The initial inheritance model should remain simple:

1. Narrower scopes may inherit from broader scopes.
2. Inheritance must be explicit.
3. Narrower scopes may extend or refine broader guidance.
4. Required rules from broader scopes should not disappear silently.
5. Exceptions should be explicit and justified.

Suggested override modes:

- `extend`
- `replace`
- `exception`

## Visibility

Suggested visibility values:

- `private`
- `internal`
- `shared`
- `public`

These should control what can be exported or shared beyond the local working context.

## Review And Trust

Suggested status values:

- `draft`
- `review`
- `approved`
- `deprecated`
- `revoked`

Cogs should not treat these states as interchangeable.

## Provenance

Frames should support lightweight provenance through:

- `source_refs`
- `decision_refs`

Suggested reference fields:

- `kind`
- `uri`
- `role`
- optional `title`
- optional `notes`

The goal is traceability, not a full graph model.

Canonical identity complements provenance:

- provenance explains where claims and decisions came from
- identity explains what artifact this is and what source it claims as authoritative

Both are needed when the same Frame may be copied, exported, forked, mirrored, or installed in multiple places.

## YAML As Current Default

YAML is the current default because it fits the spec's current goals:

- easy human review
- straightforward nesting
- low punctuation overhead
- natural use in version-controlled text artifacts

This remains a default, not yet a permanent decision.

## Minimal V0

The minimal useful version likely needs only:

1. a package manifest
2. one scoped Frame document
3. explicit `frame_id`
4. explicit `version`
5. explicit `scope`
6. explicit `inherits_from`
7. explicit `visibility`
8. explicit `status`
9. a small section taxonomy
10. optional provenance references
11. optional but standard canonical source and authority metadata

## Open Questions

1. Should one package usually contain one Frame tree or many independent scopes?
2. How strict should override validation be in v0?
3. Which sections are required versus merely allowed?
4. What should Collab sharing require from Frame metadata?
5. How should canonical identity behave for reviewed exports, local copies, and forks?
6. How much schema enforcement should exist before more real examples are authored?
