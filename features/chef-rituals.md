# Feature 4: Daily Chef Rituals (`pre-shift-check.sh`, `audit-date-dots.sh`, `clean-station.sh`)

## What the Diner / Head Chef Observes
1. **4:30 PM Pre-Shift Lineup (`/pre-shift-lineup` -> `pre-shift-check.sh`)**:
   - Inspects base stockpot health (`git status`), active `factory/*` worktrees against Little's Law (`WIP_LIMIT = 5`), walk-in FIFO date dots, and station surface cleanliness in one command.
2. **Green Painter's Tape & FIFO Date Dots (`/fifo-walk-in` -> `audit-date-dots.sh`)**:
   - Scans for `FIFO-DATE-DOT: expires=YYYY-MM-DD` tags. Passes with exit code `0` when all containers are within shelf life; fails loudly with exit code `1` (`SPOILED CONTAINER`) if any tag's `expires` date is earlier than today's UTC date.
3. **"Clean As You Go" & Purple-Board Allergy Scan (`/allergy-alert` -> `clean-station.sh`)**:
   - Scans the cutting board for leftover scratch droppings (`*.bak`, `*.orig`, `*.tmp`, `debug_*`), unresolved conflict markers (`<<<<<<<`), debug crumbs (`pdb.set_trace()`, `breakpoint()`), and hardcoded credentials (`AKIA...`, `BEGIN PRIVATE KEY`). Passes with exit code `0` on a wiped station; fails with exit code `1` on a dirty board.

## Tasting Commands
```bash
bash skills/head-chef-mode/scripts/pre-shift-check.sh
bash skills/head-chef-mode/scripts/audit-date-dots.sh
bash skills/head-chef-mode/scripts/clean-station.sh --allergy
```
