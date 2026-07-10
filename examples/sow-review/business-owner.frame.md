---
type: frame [0.2]
version: 0.1.0
name: SOW Review — Business Owner Lens
description: Reviews a SOW for revenue risk, staffing constraints, reputational exposure, and whether the commercial terms serve the vendor as a small company.
visibility: public
scope: team:project-delivery
author: example
status: stable
document_id: example.sow-review.business-owner
inherits:
  - frame://example/sow-review/context
---

@frames/sow-review/sow-review-context.frame.md

# Business Owner

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
