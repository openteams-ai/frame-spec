---
type: frame [0.3]
identifier: acme/full-fixture
name: Full Round-Trip Fixture
description: Every optional element, all ten refinements, a Guard, and an extension element.
visibility: internal
version: 3.1.4
versionNotes:
  - Added the extension element for the round-trip test.
status: approved
maintainer:
  - platform engineering
scope: department
license: Apache-2.0
issued: 2026-09-07
canonicalSource: https://frames.example.org/acme/full-fixture
inherits:
  - acme/company-core@2.0.0
  - ./sibling.frame.md
derivedFrom:
  - contoso/full-fixture
previousVersion: acme/full-fixture@3.1.3
guards:
  - acme/pii-guard
x-nebari-excludes:
  - acme/legacy-tone
---

Guidance that is not under any recognized heading.

## Not A Refinement

This section is guidance too, because its heading matches no registered label.

## Rules

- No performance claims without a cited benchmark.
- Escalate when a local optimization conflicts with stated priorities.

## Terminology

- **Hub**: a deployed instance of the platform.
- Prefer "Hub" over "instance".

## Goals

- Move qualified accounts from evaluation to signed pilot within the quarter.

## Style

- Plain, direct, technically credible. Short sentences.

## Norms

- Flag regulatory uncertainty for review rather than asserting it.

## Skills

- proposal-drafting

## Tool Specifications

- ./tools/pixi.toml

## Prompts

- When summarizing a release, lead with customer impact.

## Architecture

- A registry service fronted by an OIDC-protected gateway.

## Business Process

- Externally facing compliance statements route through the compliance officer before release.
