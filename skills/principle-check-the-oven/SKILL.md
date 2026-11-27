---
name: principle-check-the-oven
description: Apply when two recipe tweaks that share one premise fail the same tasting check, or when a retry produces a duplicate SHA-256 burn signature. Stop adding seasoning, write the shared premise down (e.g., 'is the oven pilot light even lit?'), and test it directly; on duplicate burn signatures, turn off the burner immediately and dump the pan.
---

# Principle: Check the Oven (Attack the Premise)

When two or more recipe tweaks that share one assumption fail the same tasting check, suspect the oven, not the seasoning.

- Write down the single sentence every failed tweak assumed.
- Design and run a read-only observation probe that would come out differently if that premise were false **before** firing attempt #3.
- **Duplicate Burn-Signature Halt**: When a station retry produces an identical SHA-256 burn signature (`SHA256(station_id | exception_type | normalized_message)` — *George Costanza parallel parking the same impossible angle twice*), turn off the burner immediately, execute reverse-order Saga dishpit cleanup, and ring the Head Chef bell.
