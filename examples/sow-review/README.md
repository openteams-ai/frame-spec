# SOW Review Frames

A set of judgment frames for reviewing a **Statement of Work** from the smaller vendor's
perspective. Each lens reads the same SOW for a different class of risk. Use one lens or
several — every lens inherits the shared context frame.

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
