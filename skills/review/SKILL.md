---
name: review
description: Review a diff by trying to break it and proving each finding with a real command. Use for code review, blast-radius checks, and any change touching auth, tenant data, billing, secrets, personal data or destructive migrations.
---

# Review

A finding counts only if you can show it: a failing command, or an exact file:line
for something that cannot be executed. Do not edit the code under review.

1. State what the change promises, then grade each acceptance criterion pass or fail.
2. Try to break it: bad input, repeats, ordering, timeouts, empty state.
3. **Blast radius.** Name the one fact that makes the change safe and prove it by
   running real code. Look past direct callers: stored data, payloads, env vars.
4. **Sensitive areas.** For auth, tenant isolation, billing, secrets, personal data or
   destructive migrations, run at least two attacks that must be refused (no auth,
   another tenant's data, replay, bad signature) and scan the diff for secrets.
5. **Leftovers.** Debug output, scratch files, conflict markers, disabled checks.

Report: verdict (approve, request changes, reject), verified findings with the command
and output, and anything unproven. "No verified findings" is a valid result.
