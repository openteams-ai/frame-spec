---
type: frame [0.2]
version: 0.1.0
name: SOW Review — QA / Security Engineer Lens
description: Reviews a SOW for testing scope, compliance framework requirements, and whether validation deliverables are achievable within the budget allocated per phase.
visibility: public
scope: team:project-delivery
maintainer: example
status: stable
document_id: example.sow-review.qa-security
inherits:
  - frame://example/sow-review/context
---

@frames/sow-review/sow-review-context.frame.md

# QA / Security Engineer

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
