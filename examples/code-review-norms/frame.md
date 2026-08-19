---
type: frame [0.2]
name: Code Review Norms
description: How this team reviews pull requests, including what a reviewer blocks on and what is only a suggestion.
visibility: shared
---

# Code Review Norms

Block on correctness, security, and data loss. Everything else is a suggestion the author is free to decline.

Say which one you mean. Prefix blocking comments with "Blocking:" and everything else with "Nit:" so the author can triage a long review at a glance.

Review the change that was made, not the change you would have made. If a different approach is genuinely better, say so once, explain why, and leave the decision with the author.

Approve when the change is safe to merge, not when it is perfect. A follow-up issue costs less than a stalled pull request.

If a thread reaches three round trips without converging, move it to a call and post the outcome back in the thread.
