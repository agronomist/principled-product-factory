# Playbook: Off-Menu Special — Dynamic Multi-Course Synthesis (`off-menu-special.md`)

Use this playbook when no standard service playbook fits: a large cross-cutting kitchen remodel, an ambitious multi-course banquet, or an overnight prep shift a human will inspect in the morning.

## Todo List Steps (Copy into Todo Tool First)

1. **Phase A — Frame the Tasting Predicate & Rigor Level**:
   - State the definition of done as a falsifiable tasting check on the real dish (`principle-taste-before-serving`).
   - Quantify scope (courses, blast radius, one-way vs. two-way doors) and run a **Pre-Mortem** (*"It is 6 months from today and this menu change caused a health-code shutdown or negative food-cost margin—what were the top 3 failure modes?"*).
2. **Phase B — Set Up Mise en Place & Order Prep Riskiest-Ingredient-First**:
   - Build or `Station-Check` the live tasting harness *before* cooking feature code ([`../../taste-the-dish/SKILL.md`](../../taste-the-dish/SKILL.md)).
   - Run [`../../mise-en-place/SKILL.md`](../../mise-en-place/SKILL.md) to lay out types, signatures, and containers before implementation.
   - Order all prep steps by **Riskiest-Ingredient-First** ($\frac{\text{EVOI} \times (1 + P_{\text{fail}})}{\text{Cost}}$) so cheap, high-information falsification tastings run before expensive slow-braise steps.
   - For any One-Way Door recipe decision, run [`../../cook-off/SKILL.md`](../../cook-off/SKILL.md) across isolated cutting boards before committing.
3. **Phase C — Cook One Course at a Time (`principle-one-course-at-a-time`)**:
   - Execute one atomic course at a time under Little's Law ticket-rail bounds (`WIP_LIMIT = 5`).
   - Bracket every course: `clean station baseline -> smallest change -> run live tasting harness -> keep if VERIFIED, dump pan if NOT_VERIFIED or INCONCLUSIVE`.
   - Enforce [`../../principle-check-the-oven/SKILL.md`](../../principle-check-the-oven/SKILL.md) after 2 failed tweaks on the same check, and turn off the burner immediately on duplicate SHA-256 burn signatures.
4. **Phase D — Log Every Course in the Prep Log (`prep-log`)**:
   - Log a row to `decisions.tsv` (`scripts/log-decision.sh`) as each course lands or is dumped, using resolvable `file:line`, commit SHA, or proof artifact pointers.
5. **Phase E — Cross-Contamination Check, Health Inspection & Shift Handoff**:
   - Run [`../../cross-contamination/SKILL.md`](../../cross-contamination/SKILL.md) to prove the change doesn't spoil downstream dishes outside the diff.
   - Run [`../../health-inspector/SKILL.md`](../../health-inspector/SKILL.md) to try to break the dish with real repro commands.
   - Run [`../../shift-handoff/SKILL.md`](../../shift-handoff/SKILL.md) and [`../../plain-english-menu/SKILL.md`](../../plain-english-menu/SKILL.md) to hand back the prep log, verified courses, and any items waiting at the pass.
