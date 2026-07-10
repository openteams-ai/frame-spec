# Risk Identification Norms — Input Guide

This README describes what task material to provide alongside the Risk Identification Norms
Frame so an AI assistant can produce a risk register with minimal back-and-forth. Package the
selected material as a single input (or a few clearly labeled sections) so the assistant receives
it alongside the active Frame. The Frame is passive guidance — it doesn't retrieve or process
anything on its own; the assistant does the reading, using the Frame to know what to look for.

## Data handling

This frame works with sensitive material — client communications, contract values, personnel
details, invoices, calendars, and security findings. Before sending any of it:

- **Use only data you're authorized to share.** Confirm the engagement or client contract
  permits this material being reviewed this way.
- **Use an approved AI environment.** Send this material only to an AI environment your
  organization has approved for data at this sensitivity level.
- **Send the minimum necessary.** Include the excerpts that carry the signal, not entire
  mailboxes, repositories, or document stores.
- **Redact before sending.** Strip credentials, API keys, and other secrets, and remove
  personal information that isn't needed to assess the risk.

## Required inputs

Without these, the AI assistant can still flag communication or delivery issues while applying
the Frame, but it cannot assess probability or impact with any real grounding.

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
- Needed for the AI assistant to assess margin erosion or overallocation with any precision
- Without this, the output should say "margin risk could not be assessed" rather than guess

## Situational (include only if relevant to this specific project)

**7. Calendar data** — meeting decline/no-show patterns, if not already obvious from notes
**8. Invoice/payment records** — only if payment timing is a live concern
**9. Prior QA/security findings** — if the project has open findings from testing,
unresolved ones are a direct technical risk input, not just a delivery one

## How to package it

Simplest version: one document per project with clearly labeled sections matching the list
above (even if some sections say "none available"). Tell the AI assistant explicitly when a
category is missing rather than leaving it to guess — this is what lets the closing summary
correctly say "X could not be assessed" instead of silently skipping it.

---

## Other information worth pairing with the frame

A few kinds of information that add real risk signal if you include them alongside the core
inputs above. The Frame won't pull these in on its own — the AI assistant only sees what you
provide alongside it — but if you have them on hand, even a sentence or two is worth adding:

- **Contract/master agreement terms** — payment terms (net 60/90/120), liability caps,
  termination clauses. These live outside the SOW itself and are easy to overlook, but define
  how much exposure your organization actually has if things go bad.
- **Public news about the client organization** — layoffs, leadership changes, funding/earnings
  news, M&A activity. A client-side reorg is one of the strongest external leading indicators of
  project risk and isn't visible in your internal comms at all.
- **Verified changes in a key contact's role** — if you can confirm through an attributed,
  reliable source (a company announcement, a direct notification, an org-chart update) that a
  client sponsor has changed roles or left, that's a strong early warning of champion turnover.
  Rely on confirmed, attributable changes rather than reading intent into someone's personal
  profile activity.
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
