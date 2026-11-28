# Does the kitchen beat plain Claude Code?

1. Pick 10 real, already-solved tickets. Write pass criteria before running anything.
2. Run each from the same starting commit, same model, three ways: plain Claude Code,
   commit `8b0a141`, and this version.
3. Have a person grade the diffs without knowing which setup made them.

| Ticket | Setup | Criteria passed | Would merge? | Human fixes | Tokens | Minutes |
| --- | --- | --- | --- | --- | --- | --- |

Keep this version if quality holds with fewer tokens and less time. Then remove one
skill at a time and rerun; delete any whose removal changes nothing.
Ten tickets is a small sample, so repeat close calls.
