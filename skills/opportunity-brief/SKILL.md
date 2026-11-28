---
name: opportunity-brief
description: Empowered Opportunity Assessment — turns mercenary feature requests ("Build feature X") into missionary problems to solve ("Move outcome metric Y for diner segment Z"). Strips off the prescribed solution, answers The Product Trio's 4 Opportunity Questions, and pitches 3 competing dish concepts (including a 10-line/zero-code option) before cooking. Use for /opportunity-brief, "unbundle this feature request", or outcome-driven roadmaps.
---

# The Empowered Opportunity Brief (`/opportunity-brief`)

> *"In a Feature Factory, executives hand the kitchen a list of recipes: 'Q2: Build a PDF export button.' In an Empowered Kitchen, leadership hands the brigade a problem to solve: '40% of new tables walk out before their first course arrives—get Time-to-First-Plate under 90 seconds.' Mercenaries cook the button; missionaries solve the walk-out."*

## 1. The Solution-to-Problem Reframe (Stop Cooking Prescribed Tickets Blindly)

Stakeholders, users, and GitHub issues almost always ask for a **prescribed solution** (*"Add a custom webhook retry dashboard"*, *"Add a CSV export button"*).
Before evaluating or building that specific solution, `/opportunity-brief` peels back the order using **The 4 Opportunity Assessment Questions**:

1. **Objective (Which Restaurant Goal Does This Move?)**:
   - What specific business or product outcome is this supposed to improve (activation, retention, food-cost margin, service speed, expansion)?
2. **Key Result & Leading Indicator (`Plated != Eaten`)**:
   - How will we know within 7–30 days that the dish actually worked? Name the exact **leading-indicator metric** (not *"we merged the PR"*, which is an output, not an outcome).
3. **Diner Problem (What Hurts Right Now?)**:
   - What concrete friction, failure, or waste is the user experiencing today, and how are they working around it?
4. **Target Diner Persona (Which Table Are We Cooking For?)**:
   - Who specifically has this hunger (e.g., *first-time developer installing the plugin*, *on-call engineer debugging a failed shift at 2 AM*, *enterprise CFO reviewing token spend*)?

---

## 2. The 3-Recipe Option Rule (Never Bring Only One Dish to the Tasting Table)

Once the underlying **Diner Problem + Leading Indicator** is written down, the Product Trio must sketch **3 competing ways to solve that problem** before picking one to cook:

| Option Tier | What It Looks Like | Typical Food Cost & Build Time |
| :--- | :--- | :--- |
| **Option 1: The Garnish / Knife Twist (Smallest Possible Lever)** | Solve 80% of the problem by changing defaults, improving an error message, adding a 15-line shell flag, or deleting a confusing step ([`/principle-kitchen-muscle-memory`](../principle-kitchen-muscle-memory/SKILL.md)). | $< 30$ minutes, near-zero ongoing maintenance |
| **Option 2: The Bistro Special (Focused 80/20 Feature)** | A clean, single-purpose recipe that solves the core diner pain without new infrastructure or schema bloat. | $1\text{--}2$ shifts, low complexity |
| **Option 3: The Full Tasting-Menu Course (What the Requester Asked For)** | The heavy multi-file architecture originally requested on the ticket. | High token & maintenance cost — only justified if Options 1 and 2 cannot move the Leading Indicator |

### Decision Rule
Always fire **Option 1 or an [`/amuse-bouche`](../amuse-bouche/SKILL.md) of Option 2** first unless there is measured evidence that the lighter dish cannot move the Key Result.

---

## 3. "The Schmeer" (The Unspoken Next Step)

> *"Giving the audience or diner what they asked for is just the bagel. The Schmeer is that unexpected extra riff—one step beyond what they knew to ask for—that makes them sit back and say: 'Wait... how did they know I was going to need that?!'"*

Defensive filters ([`/no-empty-calories`](../no-empty-calories/SKILL.md) and [`/food-cost-guard`](../food-cost-guard/SKILL.md)) protect the kitchen from cooking inedible waste, **but a kitchen that only ever cooks literal customer feature requests becomes a forgettable cafeteria.** Customers only ask for incremental patches to their current broken workflow.

Once you nail the core problem (the bagel), every Opportunity Brief MUST propose **"The Schmeer"** subject to three strict rules so it never degenerates into scope creep:

1. **Earn the Right First**: You cannot put a schmeer on a burned bagel. The core problem must be solved cleanly first.
2. **The Next-30-Seconds Test**: Look at what the user has to do **30 seconds after** your feature finishes running. What is their very next manual copy-paste, terminal command, Excel formula, or awkward explanation to their boss? Eliminate *that* friction right on the plate (e.g., don't just display a failed webhook log—generate the exact pre-filled `curl` replay command and a 1-line root-cause summary right next to it).
3. **Petit-Four Economics ($\le 15\%$ Effort, $10\times$ Hospitality)**: In a Michelin restaurant, sending out warm madeleines at the end of dinner costs 40 cents of butter and flour and creates $10\times$ the memory. A software Schmeer must cost **$\le 15\%$ of the ticket's build effort** and introduce **zero new infrastructure dependencies**.
