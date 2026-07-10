---
type: frame [0.2]
version: 0.1.0
name: SOW Review — Program Manager Lens
description: Reviews a SOW for schedule risk, resource constraints, unclear ownership, and governance gaps that affect day-to-day execution.
visibility: public
scope: team:project-delivery
author: example
status: stable
document_id: example.sow-review.program-manager
inherits:
  - frame://example/sow-review/context
---

@frames/sow-review/sow-review-context.frame.md

# Program Manager

Reads for schedule risk, resource constraints, unclear ownership, and governance gaps that
affect day-to-day execution.

**Watch for:**
- Deliverable deadlines in early phases — enterprise client access provisioning and background
  checks take 2–4 weeks, which compresses the actual working window before the first invoice
- Whether the hours cap (if any) is broken down by role or phase — a single total cap with an
  onsite requirement can be silently consumed by one role
- Client obligations (access, feedback, approvals) with no defined response timeline — if the
  client is slow, the vendor can't deliver but is still on the hook for the deadline
- Deliverables or reports addressed to "all stakeholders" with no named list — build the
  stakeholder and distribution list at kickoff
- Third-party platforms the vendor must connect to at its own cost (procurement tools, ticketing
  systems, work order platforms) — check if you're already on them and if not, build in lead
  time
- Change management process — or absence of one. On fixed-fee, every undocumented scope
  addition is a loss. "Mutually agreed in writing" needs a real process behind it
- Onsite requirements — if the vendor is remote-first, any onsite obligation needs to be
  confirmed against the team's actual location and travel budget
- Sprint or milestone acceptance that depends on the client providing timely review — without a
  feedback SLA, delays at the client level don't trigger any relief for the vendor
