---
type: frame [0.2]
version: 0.1.0
name: SOW Review — Software Engineer / Tech Lead Lens
description: Reviews a SOW for technical scope, feasibility constraints, tooling assumptions, and work that is harder than the contract implies.
visibility: public
scope: team:project-delivery
maintainer: example
status: stable
document_id: example.sow-review.software-engineer
inherits:
  - frame://example/sow-review/context
---

@frames/sow-review/sow-review-context.frame.md

# Software Engineer / Technical Lead

Reads for technical scope, feasibility constraints, tooling assumptions, and work that is
harder than the contract implies.

**Watch for:**
- Scope items that are vague, placeholder, or marked TBD — blanks or "to be determined"
  entries that could expand the technical surface later
- Hour allocations relative to the actual technical scope — check whether the budgeted hours
  are realistic given what's being asked
- Work that depends on external parties (upstream OSS maintainers, third-party vendors, open
  source communities) whose timelines are outside the vendor's control
- System access requirements at the client — enterprise access provisioning takes 2–4 weeks
  after background checks clear; factor this into when technical work can realistically start
- Tooling named in the SOW — does it actually work inside the client's environment? Enterprise
  clients (especially financial institutions) often restrict specific tools
- Desired outcomes written as aspirational goals rather than measurable acceptance criteria —
  if it can't be measured, it can't be accepted or invoiced
- CI/CD and deployment assumptions that may conflict with the client's internal toolchain (most
  large enterprises have custom pipelines, not standard GitHub Actions)
- Security or compliance requirements that imply specialized expertise — check whether that
  expertise exists on the team or needs to be sourced
- Whether AI tools are permitted for development workflows — not just as a deliverable, but for
  internal use. Enterprise clients in regulated industries sometimes prohibit AI coding
  assistants, automated tooling, or LLM use entirely
