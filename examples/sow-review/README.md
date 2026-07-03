# SOW Review Frames

A set of judgment frames for reviewing a **Statement of Work** from the smaller vendor's
perspective. Each lens reads the same SOW for a different class of risk. Use one lens or
several — every lens inherits the shared context frame.

## Why frames for SOW review

A script can extract dates, dollar amounts, and named roles from a SOW. That's the
deterministic layer — and frames don't help there.

SOW review is an interpretation task. The model needs to read a contract and decide what
counts as a risk — which requires vocabulary, norms, and output discipline that a generic
prompt doesn't provide. Without a frame, the output tends to be complete but generic: it
surfaces the same five concerns regardless of what the SOW actually says, and it can't
distinguish a termination clause that's standard from one that's a deal-breaker for a small
vendor on a fixed-fee engagement.

The frames here don't compute anything. They tell the model **how to read**, **what to look
for**, and **how to express what it found**:

- The context frame establishes the vendor's specific realities — size, fee structure, team
  location, background check timelines — so every lens evaluates the contract against *this*
  vendor's constraints, not a generic vendor
- Each role lens brings a different reading posture: what a Contract Reviewer flags as a
  payment risk looks different from what a Delivery Manager flags as an invoicing blocker,
  even when they're reading the same clause
- The output discipline is built into the frame: flag critical issues to resolve before
  signing, items to watch during execution, and strengths worth noting — not a freeform
  summary the model decides to structure on its own

The result is something auditable: findings tied to specific clauses, risks named with enough
precision to act on, and explicit acknowledgment when something couldn't be assessed rather
than a review that silently skips it.

## What to send

**Required:**
- The SOW itself

**Strongly recommended:**
- The master agreement or MSA — payment terms (net 30/60/90/120), IP ownership, liability
  caps, and indemnification clauses are almost never in the SOW; if you omit this, the frame
  cannot assess where the real financial and legal risk actually sits
- Any referenced attachments or exhibits — scope assumptions are frequently deferred to
  appendices that appear in the SOW by name but aren't included in the document

**Helpful context to include in your prompt:**
- Team location and whether any members are outside the client's country
- Whether the engagement is fixed-fee, T&M, or contingent
- Known constraints (e.g., no cleared personnel available, fully remote team, AI tooling
  is part of your standard workflow)

**What the frame should say when something is missing:**

The frame should name what it couldn't assess rather than silently skipping those sections.
If you don't provide the master agreement, a good review will say something like: *"Master
agreement not provided — payment terms, IP ownership, and indemnification clauses could not
be assessed. Review these before signing."* If you don't provide company context, findings
should note which recommendations assume a small, remote, fixed-fee vendor and flag where
that assumption matters.

Generic output that reads as complete when it isn't is worse than an explicit gap.

## Layering

```
sow-review-context.frame.md      ← small-vendor context; the shared parent
    ├── contract-reviewer.frame.md   → legal exposure, payment risk, missing terms
    ├── program-manager.frame.md     → schedule, resource gaps, governance
    ├── software-engineer.frame.md   → technical feasibility, tooling restrictions
    ├── delivery-manager.frame.md    → sprint governance, acceptance gates
    ├── business-owner.frame.md      → revenue risk, cash flow, IP rights
    ├── qa-security.frame.md         → testing scope, compliance frameworks
    └── technical-writer.frame.md   → documentation scope, format, acceptance

sow-review-all-lenses.frame.md   ← all seven lenses + context in one file
```

## How to use

Two ways, depending on how broad a review you want:

- **Full review, one frame:** activate `sow-review-all-lenses.frame.md` — it bundles the
  context plus all seven lenses in a single file.
- **Focused or custom review:** activate `sow-review-context.frame.md` plus whichever
  individual lens frames you want (e.g. just Contract Reviewer for a quick legal-risk read).

Then provide the SOW and ask: *"Review this SOW through the active lenses. For each, flag
critical issues to resolve before signing, items to watch during execution, and strengths
worth noting."*

## Frames

| File | Lens | Reads for |
|---|---|---|
| `sow-review-all-lenses.frame.md` | **All seven (single file)** | Full multi-lens contract review in one frame |
| `sow-review-context.frame.md` | Context (parent) | Small-vendor realities every lens checks against |
| `contract-reviewer.frame.md` | Contract Reviewer | Legal exposure, payment risk, missing/deferred terms |
| `program-manager.frame.md` | Program Manager | Schedule risk, resource constraints, governance gaps |
| `software-engineer.frame.md` | Software Engineer / TL | Technical scope, feasibility, tooling assumptions |
| `delivery-manager.frame.md` | Delivery Manager / Scrum Master | Sprint governance, unnamed roles, acceptance/invoicing blockers |
| `business-owner.frame.md` | Business Owner | Revenue risk, staffing, reputational exposure, commercial terms |
| `qa-security.frame.md` | QA / Security Engineer | Testing scope, compliance frameworks, validation budget |
| `technical-writer.frame.md` | Technical Writer | Documentation scope, format, summary-vs-detail consistency |
