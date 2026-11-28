---
name: mise-en-place
description: Sketch types, function signatures, contract preconditions/postconditions, and isolated module containers before writing implementation logic. Use for /mise-en-place, 'architect this', or any work crossing a module boundary where jumping straight to cooking would lock in the wrong dish shape.
---

# Mise en Place — Architecture Before Cooking (`/mise-en-place`)

In a professional kitchen, **mise en place** ("everything in its place") means measuring, portioning, and labeling every container *before* turning on the stove. In software, it means settling data types, function signatures, and module boundaries before writing implementation bodies.

## 1. Lay Out the Containers First (Module Information Hiding)
Before writing business logic:
1. Define the **immutable input and output data schemas** (`frozen=True, extra="forbid"`).
2. State what "secret" each module hides from the rest of the kitchen (vendor wire formats, internal retry counters, SQLite connection handles).
3. Verify topological layering: `products/<line>` may import from `platform/`, never from another `products/<line>`, and `platform/` never imports from `products/`.

## 2. State Contract Preconditions & Postconditions on the Signature
For every public function or station interface:
- **Preconditions**: What must be true of the ingredients before the function starts? (Subtypes must never strengthen preconditions).
- **Postconditions**: What algebraic or structural invariant is guaranteed on the plated return value? (Subtypes must never weaken postconditions).
- Make illegal states unrepresentable in the type system so bad data is rejected at the kitchen door.

## 3. Stay at the Pass While the Line Cook Fills In the Body
- If the design is a contested One-Way Door, run [`../cook-off/SKILL.md`](../cook-off/SKILL.md) over 2–3 competing type sketches before committing.
- Once the types and signatures compile and tell a clear story on their own, hand the skeleton to the Line Cook to fill in the implementation bodies without altering the public container contracts.
