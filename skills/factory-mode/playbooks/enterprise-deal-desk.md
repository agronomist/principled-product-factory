# Playbook: Enterprise Challenger Deal Desk & JOLT Pipeline (`enterprise-deal-desk.md`)

Use this playbook when structuring an enterprise B2B sales pitch, handling a prospect's demand for a custom feature or price discount, or rescuing a stalled deal from "No Decision".

## Todo List Steps (Copy into Todo Tool First)

1. **Validate the 6-Step Commercial Teaching Choreography (`challenger-deal-desk`)**:
   - Open [`../../challenger-deal-desk/SKILL.md`](../../challenger-deal-desk/SKILL.md).
   - Verify the pitch follows the strict 6-step Challenger sequence:
     1. **Warmer**: Lead with benchmarked industry observations (never ask the lazy *"What keeps you up at night?"* cliché).
     2. **Reframe**: Expose a counter-intuitive structural blind spot the buyer thought was a normal cost of doing business.
     3. **Rational Drowning**: Quantify their exact annual **Cost of Inaction ($\text{COI}$)**—requiring $\text{COI} \ge 3.0\times \text{ACV}$ ($\le 4$-month payback on status-quo bleed).
     4. **Emotional Impact**: Connect the failure mode to their team's day-to-day operational pain.
     5. **A New Way**: Define the vendor-agnostic architectural capabilities required to fix the reframe—**before** pitching product SKU names.
     6. **Our Solution Map**: Prove how our unique platform invariants are the only way to deliver Step 5.
2. **Tailor for Resonance Across the Buying Committee (`challenger-deal-desk`)**:
   - Generate tailored briefs for all 4 stakeholders:
     - `ECONOMIC_BUYER_CFO` (monthly Cost-of-Delay bleed, ROIC, CAC payback, contribution margin floor).
     - `TECHNICAL_ARCHITECT_VP_ENG` (3-tier SRE fallback clean sheet, zero single-vendor lock-in, Liskov/Parnas boundaries).
     - `MOBILIZER_CHAMPION` (*Go-Getters, Teachers, Skeptics*—never passive *Talkers*: 14-day Stage A proof with a cross-vendor audited `decisions.tsv` trail).
     - `END_USER_OPERATOR` (Axis 1 Workflow Elimination $\ge 0.85$ with zero popup drudgery).
3. **Hold Constructive Tension Against Build-Trap & Margin Demands (`escape-the-build-trap` + `margin-guard`)**:
   - **Never act like a "Relationship Builder" rep** who caves to bespoke roadmap demands or untraded discounts:
     - If the prospect demands a custom feature, run it through [`../../escape-the-build-trap/SKILL.md`](../../escape-the-build-trap/SKILL.md). If it is a one-off ($N=1$) or fails Ulwick's JTBD Opportunity Score ($< 10.0$), **push back with Constructive Tension** and log the signal in [`../../customer-flywheel/SKILL.md`](../../customer-flywheel/SKILL.md) (so it is quarantined at $N=1$ but automatically promotes to Stage A if $N=3$ independent accounts ask for it).
     - If the prospect requests a discount, verify [`../../margin-guard/SKILL.md`](../../margin-guard/SKILL.md) at the discounted price AND require a concrete **Give-Get concession** (24-month commitment, annual upfront billing, and public case study).
4. **Apply the JOLT Effect Playbook to Overcome FOMU (`challenger-deal-desk`)**:
   - Diagnose **FOMU (Fear of Messing Up)** across Option Overload, Endless POC Creep, and Outcome Fear:
     - **J**udge the indecision level.
     - **O**ffer a bold personal recommendation (eliminate confusing multi-tier menus).
     - **L**imit the exploration (bound POCs to 14 days on our golden eval set + 1 live harness journey).
     - **T**ake risk off the table (3-tier SRE fallback SLA + 6-month re-pricing retro-audit + Stage A Bayesian exit ramp).
