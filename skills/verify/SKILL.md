---
name: verify
description: Prove a change or a measurement is real by running it. Use before claiming work is done, when setting up a project's end-to-end check, and before reporting any speed, cost or accuracy number.
---

# Verify

Compiling and passing mocks are not proof.

## Run the real thing
1. **Start** it from a clean scratch directory or free port.
2. **Check** it is the right build and ready.
3. **Drive** the user's actual path, including one failure case.
4. **Save** the output outside the scratch directory.
5. **Clean up** only what you started, then confirm the evidence still exists.

Prove a new check can fail by running it against deliberately broken code.
If the project has no such script, write one and keep it in the repo.

## Check any number
- Did the work actually happen (not a cache hit, early exit or empty data)?
- What physically limits it, and is the number plausible?
- What is the error rate?
- How many runs, and how much spread?
- Same conditions for before and after?
- Does it matter to the user?

Label what you report: measured, inferred or guess.
