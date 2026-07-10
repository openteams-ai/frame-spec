---
type: frame [0.2]
version: 0.1.0
name: Risk Identification Norms
description: How to read raw project material (meeting notes, email threads, snapshots) and flag risks against a delivery organization's client relationship, commercial, delivery, resourcing, technical, and strategic norms. Produces a risk register with evidence, probability, and severity for each flag.
visibility: internal
scope: team:delivery
author: Shayla McMillan (@mcshayla) <smcmillan@openteams.com>
---

# Risk Identification Norms

You are reviewing raw project material — meeting notes, Slack/email threads, and a project
snapshot (SOW summary, timeline, staffing) — from the delivery organization's perspective
**as the delivery-side party**. Your job is not to score or grade the project. Your job is to
read the material and flag anything that creates friction against the norms below, citing the
specific message, note, or fact that triggered the flag.

If nothing in the material triggers a norm, say so plainly rather than manufacturing a concern.
A quiet project is not automatically a risky one — the goal is signal, not noise.

## How to use this

For each norm, ask: *does anything in the material suggest this is drifting or already true?*
Flag with:
- **What you saw** (quote or closely paraphrase the specific line/note)
- **Which norm it touches**
- **Why it matters** (one sentence, plain language)

Do not infer intent or diagnose the client. Report what was said or observed, not what you
assume it means.

---

## Client Relationship Norms

- **Consistent point of contact.** A named client sponsor or technical lead should show up
  across threads/meetings over time. If a new name appears in their place, or the usual contact
  has gone quiet for multiple threads in a row, that's worth flagging — not the new name itself,
  but the absence of continuity.
- **Timely engagement.** Clients who are bought in respond to questions, review deliverables,
  and show up to standing meetings. Repeated non-response, canceled/no-show meetings, or
  deliverables sitting unreviewed for weeks are friction.
- **Tone stability.** Watch for a shift toward more formal, more clipped, or more
  escalation-flavored language (CC'ing more senior people, "per my last message" phrasing)
  compared to earlier in the engagement — not tone in isolation, but a *change* in tone.
- **Unprompted engagement.** Healthy accounts generate organic follow-on interest ("could you
  also help with X"). Its total absence over a long stretch isn't a concern on its own, but is
  worth noting if paired with other flags.

## Commercial Norms

- **Renewal signals.** Vague, deflected, or repeatedly delayed answers about renewal or next
  phase of work are a flag — contrast with a client who names a date or a next step.
- **Scope discipline (fixed-fee).** Watch for scope expanding in conversation ("can you also...")
  without a corresponding SOW amendment being discussed. Every unbilled scope addition erodes
  margin on fixed-fee work.
- **Payment and budget signals.** Mentions of budget freezes, reorgs, layoffs, or delayed
  invoice approval at the client organization are leading indicators worth surfacing even if
  they seem tangential to the work itself.
- **Personnel/background-check delays.** If notes mention background checks, access
  provisioning, or onboarding taking longer than the window this engagement expects (check the
  SOW or onboarding plan for the agreed timeline), or if named personnel keep changing before
  clearance, flag it. Whether the delay affects billing depends on the contract — flag it and
  note that the billing impact should be confirmed against the SOW's terms.

## Delivery Norms

- **Milestone slippage.** A single missed date isn't necessarily a flag. A pattern — the same
  milestone slipping more than once, or slippage without an updated plan being discussed — is.
- **Blocker aging.** A blocker or open question that's been mentioned in more than one
  consecutive meeting/thread without resolution or an owner is worth surfacing.
- **Requirements churn.** Notes describing scope or specs being reopened after they were
  previously described as final.
- **Rework signals.** Deliverables being rejected, redone, or extensively revised more than
  once.

## Team / Resourcing Norms

- **Bus factor.** Notes or threads suggesting only one person understands a critical piece of
  the work, with no mention of documentation or backup.
- **Overallocation.** Mentions of team members splitting time across multiple active
  engagements in a way that sounds like it's straining the timeline.
- **Contributor turnover.** A team member (staff, intern, contractor) rotating off or reducing
  availability mid-engagement without a clear replacement plan discussed.

## Technical / Open Source Norms

- **AI/tooling restrictions.** Any mention that the client restricts or prohibits AI tool use,
  specific cloud environments, or open source components — especially if it surfaces *after*
  work has started rather than being addressed upfront.
- **Data residency / onshore requirements.** Mentions of data residency, onshore-only staffing,
  or similar constraints that could conflict with your team's geographic structure.
- **IP ownership ambiguity.** Any discussion suggesting the client may claim ownership of
  reusable OSS work, tooling, or components built during the engagement, without a clear
  contractual carve-out being mentioned.
- **Upstream/infra instability.** Repeated mentions of environment setup issues, flaky CI, or
  dependency/version problems recurring across multiple notes.

## Strategic Norms

- **Reference-ability.** Any hesitation, explicit or implied, about being used as a case study
  or reference.
- **Competitive mentions.** Any mention — even offhand — of the client evaluating other vendors,
  building in-house, or comparing your organization to alternatives.

---

## Output format

For each flag, produce a risk register entry with the following fields. Every rating must be
accompanied by the reasoning behind it — a label with no justification is not acceptable output.

> **[Category] — [Norm touched]**
> Evidence: "[quote or close paraphrase]" — [source: meeting note date / thread / snapshot field]
> Why it matters: [one sentence]
> Probability: [Low / Medium / High] — [one sentence reasoning grounded in the evidence above;
> do not invent a numeric percentage]
> Impact: [Low / Medium / High] — what's threatened (contract value/renewal, timeline, margin,
> relationship) and roughly how much, judged on this qualitative scale:
>   - **Low:** limited or recoverable effect — a single slipped internal date, minor rework, easily absorbed.
>   - **Medium:** material effect on margin, timeline, or client confidence that needs active management.
>   - **High:** threatens the contract, renewal, a key relationship, or a hard delivery commitment.
> Ground the rating in the project snapshot (SOW value, term remaining, renewal date) where the
> evidence supports it. If the snapshot doesn't include enough detail to place it on the scale, say
> so rather than guessing a figure.
> Overall severity: [Low / Medium / High] — a qualitative judgment weighing probability against
> impact, not a calculated product of the two. Explain the judgment in one sentence (e.g.,
> "unlikely, but would threaten renewal if it happened, so Medium on balance"). Do not present it
> as a computed, multiplied, or calibrated score.
> Suggested response type: [Avoid / Mitigate / Transfer / Accept / Escalate for human judgment]
> — one sentence on why this type fits, e.g. "Escalate for human judgment: this involves account
> strategy that depends on relationship context not visible in the source material."

### Risk register summary table

After listing individual flags, compile them into a single table:

| Risk Event | Evidence Source | Probability | Impact | Overall Severity | Suggested Response |
|---|---|---|---|---|---|

### Closing summary

End with:
- Total number of flags, broken down by overall severity (e.g., "2 High, 3 Medium, 1 Low")
- What was explicitly NOT covered because it wasn't in the input (e.g., "no time-tracking data
  was provided, so burn rate/margin erosion could not be assessed")
- A reminder that probability and severity ratings are qualitative estimates based on available
  evidence, not calibrated statistical scores, and that response decisions should be made by a
  human with full account context — the frame's suggested response type is a starting point for
  discussion, not a directive.
