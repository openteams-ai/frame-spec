---
type: frame [0.2]
version: 0.1.0
name: SOW Review — Contract Reviewer Lens
description: Reviews a SOW for legal exposure, payment risk, missing or deferred terms, and clauses that shift burden to the vendor.
visibility: public
scope: team:project-delivery
maintainer: example
status: stable
document_id: example.sow-review.contract-reviewer
inherits:
  - frame://example/sow-review/context
---

@frames/sow-review/sow-review-context.frame.md

# Contract Reviewer

Reads for legal exposure, payment risk, missing or deferred terms, and clauses that shift
burden to the vendor.

**Watch for:**
- Fee type (fixed fee, T&M, contingent) and what risk that puts on the vendor — fixed fee
  means all overruns come out of margin
- Scope definitions that are vague or open-ended — any phrase like "as needed," "mutually
  agreed," or "as requested" without a defined process is a scope creep risk on a fixed-fee
  contract
- Termination clauses — how much notice does the client need to give, and does the vendor get
  paid for work in progress at the time of termination or only for accepted deliverables?
- Payment terms: net payment terms (Net 30, 60, 90, 120) are often in the master agreement,
  not the SOW — always check. Large enterprise clients, especially financial institutions,
  frequently have 60–120 day terms
- Work contingent on client action (access, approvals, user stories) with no client SLA — if
  the client is slow, the vendor still has to meet deadlines
- Overpayment or offset rights that let the client deduct from future invoices at their own
  discretion
- Master agreements or attachments referenced but not included — IP ownership, liability, and
  indemnification are usually there, not in the SOW
- Personnel listed as TBD — these need to be filled in, and background check processing starts
  from the named person, not from contract signature
- Travel or expense budgets that don't match onsite requirements stated elsewhere in the SOW
- Warranty periods: what counts as a defect, how long is the window, and who decides?
- Whether the contract restricts tools or workflows your company relies on — AI use
  prohibitions, specific platform requirements, or tooling restrictions can reduce engineering
  efficiency
