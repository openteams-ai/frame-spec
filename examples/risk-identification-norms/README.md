# Risk Identification Norms — Input Guide

This README describes what to send the Risk Identification Norms frame so it can produce a
risk register with minimal back-and-forth. Package everything as a single input (or a few
clearly labeled sections) — the frame reads all of it together, not sequentially.

## Required inputs

Without these, the frame can still flag communication/delivery issues but cannot assess
probability or amount at stake with any real grounding.

**1. Project snapshot**
- Client name, project name
- SOW value (total contract value)
- Contract term / remaining duration
- Renewal date (if applicable)
- Fixed-fee or T&M
- Named personnel on the engagement (from your organization)
- Primary client contact(s) on record

**2. Client-facing communications**
- Recent email threads (client-facing) — last 4–8 weeks minimum, more if available
- Recent Slack messages/channels involving the client (if applicable)
- Include sender/recipient and timestamps, not just message text — timing and who's
  participating is half the signal

**3. Meeting notes**
- Client status calls, check-ins, kickoffs — whatever exists
- Attendance (who showed up, who didn't) matters as much as content

**4. Internal team standup notes**
- Your team's own read on the project — blockers, staffing concerns, concerns raised
  internally often surface before they show up anywhere client-facing

## Strongly recommended (adds real signal, not required to run)

**5. GitHub issues/PRs** (if the engagement involves a repo)
- Open issue age, reopened issues, rejected/reworked PRs
- CI status patterns if flaky infra is a recurring theme

**6. Time-tracking data by role**
- Needed for the frame to speak to margin erosion or overallocation with any precision
- Without this, the frame should say "margin risk could not be assessed" rather than guess

## Situational (include only if relevant to this specific project)

**7. Calendar data** — meeting decline/no-show patterns, if not already obvious from notes
**8. Invoice/payment records** — only if payment timing is a live concern
**9. Prior QA/security findings** — if the project has open findings from testing,
unresolved ones are a direct technical risk input, not just a delivery one

## How to package it

Simplest version: one document per project with clearly labeled sections matching the list
above (even if some sections say "none available"). The frame should be told explicitly when
a category is missing rather than left to guess — this is what lets its closing summary
correctly say "X could not be assessed" instead of silently skipping it.

---

## Other information worth pairing with the frame

A few kinds of information that add real risk signal if you include them alongside the core
inputs above. The frame can't go get these itself — but if you have them on hand, even a
sentence or two is worth adding:

- **Contract/master agreement terms** — payment terms (net 60/90/120), liability caps,
  termination clauses. These live outside the SOW itself and are easy to overlook, but define
  how much exposure your organization actually has if things go bad.
- **Public news about the client organization** — layoffs, leadership changes, funding/earnings
  news, M&A activity. A client-side reorg is one of the strongest external leading indicators of
  project risk and isn't visible in your internal comms at all.
- **Key contact's public signals** — a client sponsor updating LinkedIn to "open to work" or
  changing roles is a strong early warning of champion turnover, often before it shows up in any
  email.
- **Support/ticket volume** (if the engagement includes any ongoing support component) — a
  spike in client-reported issues is a leading indicator of dissatisfaction independent of tone
  in conversation.
- **Cross-project comparison** — if the same client has multiple active engagements, risk
  signals on one project (e.g., non-renewal hints) are relevant context for the others, and vice
  versa. Worth including sibling-project snapshots, not just the one project's material.
- **Industry/regulatory shifts** — for regulated-industry clients, upcoming regulatory changes
  affecting AI tool use or data handling can create risk that has nothing to do with how the
  engagement itself is going.
- **Vendor/competitor mentions in the client's own public materials** — e.g., a client's job
  postings suddenly listing in-house ML engineering roles could be a soft signal of insourcing
  intent.

None of these should block an initial run. They're context a person gathers and pastes in —
"client announced layoffs last month," "payment terms are net 90, no liability cap" — not data
the frame connects to. When you include them, label them like any other input section so the
frame can cite them as evidence.
