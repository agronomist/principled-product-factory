---
name: plain-english-menu
description: Strip AI slop, corporate buzzwords, and hedging out of prose, PR descriptions, issue comments, and Sommelier deal briefs. Enforces short declarative sentences, evidence labels (measured, inferred, guess), and the Soccer & Seinfeld metaphor bank. Use for /plain-english-menu or any human-facing writing.
---

# Plain-English Menu — Unslop & Metaphor Bank (`/plain-english-menu`)

Left to their defaults, AI models write like a nervous corporate consultant—throat-clearing, sycophancy, passive voice, and decorative em-dashes. In our kitchen, every PR description, ticket comment, prep-log entry, and Sommelier brief must read like a clean, sharp menu.

## 1. The Kitchen Writing Rules
1. **Lead with What Changed on the Plate**: First sentence states the outcome or answer. No *"Certainly! I'd be happy to help you explore..."* throat-clearing.
2. **Short Declarative Sentences**: Active voice. Concrete nouns and verbs. No long dash (`—`) or colon (`:`) used as a lazy sentence connector inside prose paragraphs.
3. **Label Every Claim's Evidence**: Pair every factual or performance claim with its proof pointer (`file:line`, command output) or an explicit epistemic tag: `(measured)`, `(inferred)`, or `(guess)`.
4. **Candor Over Sycophancy**: When an idea is empty calories or fails food-cost math, say *"This doesn't earn a spot on the menu"* plainly.

## 2. The Canonical Soccer & Seinfeld Metaphor Bank

When explaining system bottlenecks, kill-switches, pantry fallbacks, or metric gaming to humans, anchor the math in our canonical metaphors:

| Kitchen / Factory Phenomenon | Soccer Metaphor | Seinfeld Metaphor |
| :--- | :--- | :--- |
| **Little's Law Ticket Cap (`WIP_LIMIT = 5`)** | **Cruyff's Total Football Spacing**: Packing all 10 outfield players into the 6-yard box clogs the passing lanes. Spacing the pitch keeps the ball moving faster than defenders can recover. | **The Soup Nazi's Queue**: Five customers at the counter max. Step forward, state your order, step left. Chaos in the line means *"No soup for you!"* |
| **Duplicate SHA-256 Burn Halt & Saga Pan Dump** | **Abandoned Short Corner**: If the defense reads the short-corner routine twice in a row, stop kicking it into the first defender's shins—reset to the center-backs. | **George Parallel Parking**: Don't wedge the sedan into the same fire hydrant 4 times while traffic honks down Amsterdam Ave. Back out immediately (Saga cleanup) and hand the keys to the attendant. |
| **3-Tier Pantry Fallback (`primary -> secondary -> tertiary`)** | **Playmaker $\to$ Box-to-Box Midfielder $\to$ Sweeper Keeper**: When your #10 playmaker is double-marked (`primary` outage), pivot through your #8 (`secondary_distilled`) or play a safe back-pass to the keeper (`tertiary_cached`) to keep a clean sheet. | **Jerry's Comedy Club Pivot**: If the new experimental bit gets silence (`primary` failure), drop smoothly into the battle-tested laundry routine (`secondary`/`tertiary`) so the set never dies. |
| **Bayesian Kill-Switch & 86-the-Dish Sunset** | **60th-Minute Tactical Substitution**: Subbing off a striker on a yellow card whose expected goals (xG) flatlined—save stamina for a match you can win. | **George's "Do the Opposite"**: Exiting a doomed commitment in week 2 instead of dragging it out for three quarters out of sunk-cost stubbornness. |
| **Goodhart's Law & Countervailing Guardrails** | **Sterile 80% Possession**: Passing sideways 900 times between center-backs to juice pass-completion stats while losing 1-0 on a counterattack. | **Kramer & Newman's Michigan Bottle-Deposit Run**: Obsessing over gross 10-cent can volume while losing money on every mile of postal-truck fuel. |
| **Molecular-Gastronomy AI Theater ($\text{EVOI} = 0$)** | **Doing Step-Overs in Your Own Penalty Box**: Flashy Ronaldinho tricks 85 yards from the opponent's goal when a simple 5-yard clearance wins the game. | **The Urban Sombrero / Kramer's Coffee Table Book**: Putting a giant dramatic hat on the J. Peterman catalog cover when customers just wanted a working umbrella. |
