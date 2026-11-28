---
name: four-tasting-risks
description: Marty Cagan's Four Big Risks Discovery Gate (Value Risk, Usability Risk, Feasibility Risk, and Business Viability Risk) plus High-Integrity Reservations. Ensures the Product Trio (Product, Design, and Sous Chef Tech Lead) de-risks usability, technical feasibility spikes, legal/channel viability, and customer hunger before committing line cooks or promising a hard delivery date to a VIP table. Use for /four-tasting-risks, Cagan discovery checks, or high-integrity commitments.
---

# The Four Tasting Risks & High-Integrity Reservations (`/four-tasting-risks`)

> *"A Feature Factory only asks 'How long will it take to cook this?' An Empowered Kitchen asks four questions before lighting a single burner: Will diners order it? Can they eat it without a manual? Can our ovens actually cook it during a Saturday rush? And does it survive health code, legal, and food-cost math?"*

## 1. Marty Cagan's Four Big Risks Scorecard

Before any new feature or product bet (`Stage A` or `Stage B`) moves from Discovery into Delivery ([`/kitchen-brigade`](../kitchen-brigade/SKILL.md)), the **Product Trio** must explicitly score and retire all four risks:

| The 4 Big Risks | Kitchen Question | Owner in the Product Trio | Required Discovery Proof Before Firing Line Cooks |
| :--- | :--- | :--- | :--- |
| **1. Value Risk** | *Will the diner actually choose to order this dish and pay for it?* | **Product (Maitre D')** via [`/no-empty-calories`](../no-empty-calories/SKILL.md) | Ulwick JTBD Opportunity Score $\ge 10.0$ + *The Mom Test* skin-in-the-game (`time`, `reputation`, or `financial/pain` commitment). |
| **2. Usability Risk** | *Can the diner figure out how to eat it without a 40-page instruction manual, or did we serve an uncracked lobster with no nutcracker?* | **Design (Plating & Experience Chef)** via [`/plating-and-experience`](../plating-and-experience/SKILL.md) | 5-minute [`/amuse-bouche`](../amuse-bouche/SKILL.md) bite test proving $\le 3$ steps to first value, clear empty state, and fix-naming error messages. |
| **3. Feasibility Risk** | *Can our kitchen actually cook this with our current ovens, latency budgets, context limits, and purveyor APIs during a Friday rush?* | **Tech Lead (Sous Chef)** via [`sous-chef-planner`](../../agents/sous-chef-planner.md) | **Day-0 Feasibility Spike**: Sous Chef inspects the live codebase during discovery (not after!) to verify data availability, latency ceiling, and whether changing 10% of the spec makes it $5\times$ faster to build. |
| **4. Business Viability Risk** | *Does this dish work for our margins, legal/privacy rules, sales channel, and existing menu?* | **Product + Deal Desk** via [`/food-cost-guard`](../food-cost-guard/SKILL.md) & [`/allergy-alert`](../allergy-alert/SKILL.md) | Contribution margin $\ge M_{\min}$, $\text{EVOI} > \text{Cost}$, Purple-Board compliance cleared (PII/Auth/Billing), and zero destructive cannibalization of existing signature dishes. |

### The Hard Discovery Rule
If **any** of the Four Big Risks is scored `UNPROVEN` or `HIGH_RISK`:
- **Do NOT dispatch [`line-cook-implementer`](../../agents/line-cook-implementer.md) to build the full production recipe.**
- Instead, run the **cheapest possible 15-minute discovery spike** that retires that specific risk first (e.g., an [`/amuse-bouche`](../amuse-bouche/SKILL.md) for Usability Risk, a 20-line benchmark script for Feasibility Risk, or a Challenger [`/sommelier-table-pitch`](../sommelier-table-pitch/SKILL.md) Give-Get test for Value Risk).

---

## 2. High-Integrity Reservations (Never Promise the Banquet Before Tasting the Sauce)

Marty Cagan's law on stakeholder & enterprise commitments:
1. **Discovery Bets Have Zero Delivery Date Promises**: While any of the 4 Big Risks is still in Discovery, never give an executive or enterprise prospect a hard ship date.
2. **When a High-Integrity Reservation Is Allowed**: When a VIP table or cross-team dependency genuinely needs a hard date commitment (a *High-Integrity Commitment*), you must **complete Discovery first**—meaning all 4 Big Risks are retired and [`sous-chef-planner`](../../agents/sous-chef-planner.md) has completed a live feasibility spike and sized the exact ingredients. Only then do you stamp a High-Integrity Reservation date on the ticket.
