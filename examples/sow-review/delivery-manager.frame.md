---
type: frame [0.2]
version: 0.1.0
name: SOW Review — Delivery Manager / Scrum Master Lens
description: Reviews a SOW for sprint governance, unnamed roles, and anything that could stall delivery or block final acceptance and invoicing.
visibility: public
scope: team:project-delivery
maintainer: example
status: stable
document_id: example.sow-review.delivery-manager
inherits:
  - frame://example/sow-review/context
---

@frames/sow-review/sow-review-context.frame.md

# Delivery Manager / Scrum Master

Reads for sprint governance, unnamed roles, and anything that could stall delivery or block
final acceptance and invoicing.

**Watch for:**
- Roles named in governance sections (Scrum Master, Delivery Manager, etc.) that don't appear
  in the resource roles table — if the vendor has to fill that role, there needs to be budget
  and a named person
- Whether coordination roles are vendor-provided or client-provided — don't assume the client
  will staff this
- Final acceptance criteria and whether there is a deemed-acceptance fallback — without one,
  the final invoice can be held indefinitely while waiting for a client signature
- Feedback timelines for the client — "prompt" or "timely" without a defined window. Sprint
  cadences require predictable client review; delays that have no SLA will quietly derail
  schedules
- Incident notification requirements — know who at the client receives them and what channel
  to use before the first incident happens
- Whether sprint deliverables align with invoice dates — on fixed-fee, accepted work must be
  clearly tied to a specific payment trigger, or delivery and billing drift apart
