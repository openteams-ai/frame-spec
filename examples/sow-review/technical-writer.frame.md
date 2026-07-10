---
type: frame [0.2]
version: 0.1.0
name: SOW Review — Technical Writer Lens
description: Reviews a SOW for documentation scope, format expectations, and consistency between the high-level summary and the detailed deliverable descriptions.
visibility: public
scope: team:project-delivery
author: example
status: stable
document_id: example.sow-review.technical-writer
inherits:
  - frame://example/sow-review/context
---

@frames/sow-review/sow-review-context.frame.md

# Technical Writer

Reads for documentation scope, format expectations, and consistency between the high-level SOW
summary and the detailed deliverable descriptions.

**Watch for:**
- Conflicts between a general summary of deliverables and the detailed
  installment-by-installment descriptions — the detailed version usually controls, but if they
  contradict each other it will cause disputes at acceptance
- The payment schedule installment descriptions often contain the most precise deliverable
  language in the SOW — treat these as the authoritative spec, not the milestone table
- Knowledge transfer or handoff scope that is underspecified relative to the engagement length
  — a year-long technical engagement produces a lot of institutional knowledge; a vague
  "training session and runbooks" deliverable at the end is often underfunded
- Whether target audiences for documentation are named — client contacts may want different
  formats than the client's internal engineering teams
- Whether format and medium are specified (Confluence, Markdown, PDF, recorded sessions) —
  clients have preferences and sometimes requirements. Confirming this early avoids rework at
  handoff
- Whether documentation effort has its own budget or is folded into implementation hours — if
  it's the latter, it tends to get cut when implementation runs long
- Deliverable descriptions that are specific and detailed enough to repurpose directly as
  documentation specs — when they exist, use them. They also serve as a paper trail supporting
  each invoice
- Recurring reports (sprint, monthly, milestone) are documentation deliverables too — check
  whether format, length, and audience are specified for each, not just the final handoff
  package
- Whether documentation deliverables have their own acceptance criteria or inherit the general
  acceptance clause — a delayed sign-off on documentation can hold the final invoice
