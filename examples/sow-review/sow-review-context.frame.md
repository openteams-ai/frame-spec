---
type: frame [0.2]
version: 0.1.0
name: SOW Review — Small Vendor Context
description: Shared context for reviewing a Statement of Work from the smaller vendor's perspective. Parent frame for the seven SOW review lenses — activate it alongside any lens frame.
visibility: public
scope: team:project-delivery
maintainer: example
status: stable
document_id: example.sow-review.context
inherits:
  - frame://example/core
---

# SOW Review — Small Vendor Context

Pair with any role-specific SOW review lens (Contract Reviewer, Program Manager,
Software Engineer, Delivery Manager, Business Owner, QA/Security, Technical Writer).
These reviews are from the **smaller vendor's perspective**. For each item below, ask:
*does anything in this SOW create friction with this reality?* If yes, flag it.

- **Size and structure:** Small vendor. Revenue concentration on any single contract is
  real risk. Losing a project mid-engagement hurts.

- **Remote and international team:** Many team members may be outside the client's country.
  Onshore-only or location-specific requirements may exclude most of the available staff.
  Data residency requirements (e.g. US-only storage) can further restrict which team members
  can access project environments.

- **AI-first or OSS-forward work:** Your company may actively use AI tools, OSS, or data
  science infrastructure. Enterprise clients — especially in regulated industries — may
  explicitly prohibit or restrict AI tool use. Check before assuming standard tooling applies.
  Work product created during engagements (OSS modifications, AI tooling, reusable components)
  may be claimed as client-owned — verify the contract defines what your company can retain or
  reuse.

- **Fixed-fee is common:** Small vendors often take fixed-fee engagements. Scope discipline is
  critical — every undocumented scope expansion comes out of margin. Travel expense caps
  embedded in the total fee reduce margin directly; verify whether travel is a pass-through or
  included in the contract value.

- **Enterprise clients move slowly:** Access provisioning, background checks, and approvals at
  large organizations take longer than expected. Build lead time into every early phase.

- **Payment terms at large clients can be long:** Net 60–120 day terms are common and often
  buried in master agreements, not the SOW. Always check.

- **Background checks are required at most enterprise clients:** These take 2–4 weeks.
  Personnel can't bill or access systems until cleared. The clock starts from the named
  individual, not contract signature — start early and name personnel as soon as possible.

- **Subcontractor and non-employee personnel:** If your company uses subcontractors, compliance
  obligations flow up under the prime contract. TBD or unnamed personnel in a SOW is a gap
  that needs resolving before work starts.

---

## How to use these lenses

When given a Statement of Work, review it through one or more of the professional lenses.
For each lens, flag what needs attention — **critical issues to resolve before signing or
kickoff**, **items to watch during execution**, and **strengths worth noting**.

Use specific role names as written. Do not say "as an expert" — just name the role.
