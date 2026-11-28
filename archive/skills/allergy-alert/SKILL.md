---
name: allergy-alert
description: The Purple-Board Allergy Protocol for high-blast-radius tickets touching authentication, payments/billing, multi-tenant SQL isolation, secrets/cryptography, PII/PHI, or destructive schema migrations. Forces dedicated utensil isolation, mandatory /health-inspector exploit proofs, and automated allergen diff scanning before plating. Use for /allergy-alert or security/compliance-sensitive tickets.
---

# Purple-Board Allergy Alert (`/allergy-alert`)

> *"When a server rings in `ALLERGY: SHELLFISH / PEANUT — TABLE 12`, the entire kitchen changes protocol. The Head Chef signs the ticket, and the Line Cook pulls out the purple allergy kit—separate pan, separate tongs, fresh gloves, zero shared fryer oil—because a dish that tastes 10/10 still kills the guest if a trace of peanut oil touches the plate."*

## 1. The 6 Kitchen Allergens (Automatic Purple-Board Triggers)

During Station 1 ([`host-triage`](../../agents/host-triage.md)) or Station 2 ([`sous-chef-planner`](../../agents/sous-chef-planner.md)), any ticket touching one or more of these six domains MUST be stamped **`PURPLE_BOARD_ALLERGY: true`**:

1. **Shellfish (Authentication, Session & RBAC/ABAC Boundaries)**: Login flows, JWT/OAuth verification, middleware auth checks, role/permission gates.
2. **Peanuts (Multi-Tenant Isolation & Data Cross-Contamination)**: SQL/ORM queries, cache keys, or vector-store lookups where Tenant A could ever read or mutate Tenant B's rows.
3. **Tree Nuts (Billing, Ledger, Pricing & Quotas)**: Stripe/webhook handlers, credit deduction, food-cost metering, idempotency keys on financial mutations.
4. **Dairy (Secrets, API Keys, Cryptography & Token Handling)**: `.env` loading, KMS/vault calls, webhook HMAC verification, webhook signing.
5. **Gluten (PII / PHI / Regulated Guest Data)**: Logging, analytics payloads, LLM prompt redaction, GDPR/HIPAA export or deletion paths.
6. **Nightshades (Destructive Migrations & Irreversible State Drops)**: `DROP COLUMN`, `TRUNCATE`, queue purge logic, or background backfill scripts.

---

## 2. Purple-Board Station Rules (What Changes When Allergy Alert Is Active)

When `PURPLE_BOARD_ALLERGY: true` is stamped on a ticket:

1. **No Fast-Track Shortcut**:
   - The Expediter is strictly forbidden from routing a purple-board ticket through a single-step `fast_implement`. It must traverse all four brigade stations (`host-triage -> sous-chef-planner -> line-cook-implementer -> pass-inspector`).
2. **Mandatory Negative Allergen Criteria in `sous-chef-planner`**:
   - The Sous Chef must include at least **two negative security/isolation acceptance criteria** (e.g., *"Unauthenticated request returns 401; Tenant A token requesting Tenant B resource returns 403/404; webhook replay with duplicate idempotency key is a no-op"*).
3. **Automated Allergen Scan on the Cutting Board (`clean-station.sh --allergy`)**:
   - Before plating, the Line Cook and Pass Inspector must run:
     ```bash
     bash skills/head-chef-mode/scripts/clean-station.sh --allergy
     ```
   - This scans the branch diff for leaked secret literals, raw private keys, insecure `eval`/`exec` patterns, disabled TLS/verification flags, and debug dumps.
4. **Mandatory Adversarial Exploit Attempt ([`/health-inspector`](../health-inspector/SKILL.md))**:
   - [`pass-inspector`](../../agents/pass-inspector.md) must execute at least one **adversarial negative test command** attempting to trigger the allergen (cross-tenant access, missing signature, replay, or malformed token) and record the command output in `.audit/evidence/`.
