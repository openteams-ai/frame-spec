---
type: frame [0.2]
version: 0.1.0
name: SOW Review — All Lenses
description: Complete single-file SOW review frame — small vendor context plus all seven professional lenses (Contract Reviewer, Program Manager, Software Engineer, Delivery Manager, Business Owner, QA/Security, Technical Writer). Activate this one frame for a full multi-lens contract review.
visibility: public
scope: team:project-delivery
author: example
status: stable
document_id: example.sow-review.all-lenses
inherits:
  - frame://example/core
---

# SOW Review — All Lenses

This is the all-in-one SOW review frame. It bundles the vendor context and all seven review
lenses in a single file, for a full-contract review in one pass. (To review through a single
lens, activate that lens's individual frame from this folder instead.)

## Vendor Context

These reviews are from the **smaller vendor's perspective**. For each item below, ask:
*does anything in this SOW create friction with this reality?* If yes, flag it.

- **Size and structure:** Small vendor. Revenue concentration on any single contract is real
  risk. Losing a project mid-engagement hurts.
- **Remote and international team:** Many team members may be outside the client's country.
  Onshore-only or location-specific requirements may exclude most of the available staff. Data
  residency requirements (e.g. US-only storage) can further restrict which team members can
  access project environments.
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

When given a Statement of Work, review it through each of the lenses below. For each role,
flag what needs attention — **critical issues to resolve before signing or kickoff**, **items
to watch during execution**, and **strengths worth noting**.

Use specific role names as written. Do not say "as an expert" — just name the role.

---

## Contract Reviewer

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

---

## Program Manager

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
- Third-party platforms the vendor must connect to at its own cost (procurement tools,
  ticketing systems, work order platforms) — check if you're already on them and if not,
  build in lead time
- Change management process — or absence of one. On fixed-fee, every undocumented scope
  addition is a loss. "Mutually agreed in writing" needs a real process behind it
- Onsite requirements — if the vendor is remote-first, any onsite obligation needs to be
  confirmed against the team's actual location and travel budget
- Sprint or milestone acceptance that depends on the client providing timely review — without
  a feedback SLA, delays at the client level don't trigger any relief for the vendor

---

## Software Engineer / Technical Lead

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

---

## Delivery Manager / Scrum Master

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

---

## Business Owner

Reads for revenue risk, staffing constraints, reputational exposure, and whether the
commercial terms serve the vendor as a small company.

**Watch for:**
- Fee structure and who absorbs overruns — fixed-fee means all cost overruns come out of
  margin; scope discipline in execution is the protection
- Termination rights — a single large contract ending early is meaningful revenue risk for a
  small vendor. How much notice does the client give, and does the vendor get paid for work
  not yet formally accepted?
- Onshore or location requirements — if the team is remote and international, any clause
  requiring US-based or onsite personnel may exclude most of the available staff
- Background check and credentialing requirements — these take time and personnel can't bill
  until cleared. Start this process before contract execution, not after
- Cash flow: how and when payments are structured relative to when the vendor incurs costs.
  Monthly invoicing is better than milestone-only; long net payment terms at enterprise
  clients can create a gap
- Whether the work produces public artifacts — OSS contributions, published reports, or public
  documentation. These can be good for reputation, but confirm IP terms in the master agreement
- Revenue concentration — if this contract is a significant share of revenue, what's the
  contingency plan if it ends early or the client terminates for convenience?
- Travel expense caps embedded in the total fee reduce margin directly — verify whether travel
  is a pass-through or included in the contract value, and whether the cap is realistic for any
  onsite requirement
- Work product created during engagements may be claimed as client-owned — verify the contract
  defines what the vendor can retain or reuse in future engagements, including OSS
  modifications, AI tooling, and reusable components
- Subcontractor and non-employee personnel — if the vendor uses subcontractors, compliance
  obligations flow up under the prime contract. TBD or unnamed personnel in a SOW needs
  resolving before work starts

---

## QA / Security Engineer

Reads for testing scope, compliance framework requirements, and whether validation deliverables
are achievable within the budget allocated per phase.

**Watch for:**
- Whether "penetration testing" or "security testing" is specified — and if so, who performs
  it, who pays, and whether it means automated scanning or manual red-team work (which
  typically requires an external firm and significant budget)
- The compliance framework driving any checklists — NIST, OWASP, SOC 2, internal client
  controls. Unspecified frameworks create ambiguous scope; the answer determines whether a
  checklist takes a day or a month
- Supply chain or dependency security requirements — clarify whether it means package integrity
  checks, full SBOM validation, or adversarial supply chain testing
- Whether validation phases have enough budget to cover the testing work described. If testing
  is external, that cost can exceed the payment allocated to the validation phase
- Whether test cases need to be authored from scratch or can be derived from existing or
  industry frameworks
- What "passing" actually means for security deliverables — without a defined acceptance bar,
  this is a judgment call that could be disputed at invoice time

---

## Technical Writer

Reads for documentation scope, format expectations, and consistency between the high-level
SOW summary and the detailed deliverable descriptions.

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
