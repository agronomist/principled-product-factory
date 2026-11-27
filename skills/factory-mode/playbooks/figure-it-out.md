# Playbook: Figure It Out — Dynamic Workflow Synthesis (`figure-it-out.md`)

Use this playbook when no narrower playbook fits: a large cross-cutting architecture migration, an ambitious multi-part build, or unattended overnight work a human will audit after stepping away.

## Todo List Steps (Copy into Todo Tool First)

1. **Phase A — Frame the Falsifiable Predicate & Rigor Level**:
   - State the definition of done as a falsifiable predicate on the real artifact (`principle-prove-it-works`).
   - Quantify scope (units, blast radius, one-way vs. two-way doors) and run a **Pre-Mortem** (*"It is 6 months from today and this change caused a SEV-1 outage or negative unit margin—what were the top 3 failure modes?"*).
2. **Phase B — Synthesize the Workflow Graph (Harness & Riskiest-Unknown First)**:
   - Build or `Doctor`-check the verification harness *before* writing feature code (`principle-foundational-thinking`).
   - Order all domain tasks by **Riskiest-Unknown-First** ($\frac{\text{EVOI} \times (1 + P_{\text{fail}})}{\text{Cost}}$) so cheap, high-information falsification steps run before expensive buildout steps.
   - For any One-Way Door design decision, run [`../../arena/SKILL.md`](../../arena/SKILL.md) across isolated worktrees before locking in the interface.
3. **Phase C — Run the Scientific Loop (`principle-sequence-verifiable-units`)**:
   - Execute one atomic unit at a time under Little's Law concurrency bounds (`WIP_LIMIT = 5`).
   - Bracket every unit: `known-good state -> smallest change -> run live verification harness -> keep if VERIFIED, hard-revert if NOT_VERIFIED or INCONCLUSIVE`.
   - Enforce [`../../principle-attack-the-premise/SKILL.md`](../../principle-attack-the-premise/SKILL.md) after 2 failed fixes on the same gate, and halt retries immediately on duplicate SHA-256 error signatures.
4. **Phase D — Weave the Append-Only Decision Trail (`show-me-your-work`)**:
   - Log a row to `decisions.tsv` (`scripts/log-decision.sh`) as each unit lands or reverts, using resolvable `file:line`, commit SHA, or proof artifact pointers.
5. **Phase E — Adversarial Interrogation, Structural Ratchet & Hand-Back**:
   - Run [`../../interrogate/SKILL.md`](../../interrogate/SKILL.md) to try to break the result with real repro commands.
   - Run [`../../correct/SKILL.md`](../../correct/SKILL.md) to encode any new mistake class into architecture, types, or a fix-naming lint.
   - Audit `decisions.tsv` against the transcript with a cross-vendor model and return the playbook used, the decision-trail path, verified predicates, and the `Attention` review block.
