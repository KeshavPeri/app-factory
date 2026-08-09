# Routines behaviour verification — Task 0.2

**Checked:** 9 August 2026, against https://code.claude.com/docs/en/routines

| Fact | §4.1 claim | Doc says now | Match? |
|---|---|---|---|
| Minimum schedule interval | 1 hour | "The minimum interval is one hour; expressions that run more frequently are rejected." | Yes |
| Per-account daily run cap | Exists, research-preview, moves | A daily cap on runs-started-per-account exists, but the **exact number is not published in the docs** — it's account/plan-specific and shown live at claude.ai/code/routines or claude.ai/settings/usage. One-off runs do **not** count against it. | Confirmed to exist; exact number needs Keshav to check his own dashboard (owner-only login) — feeds into Task 5.5. |
| `claude/` branch push restriction | Default push restriction to `claude/`-prefixed branches | Confirmed: `claude/`-prefixed branches "always accepted." Pushes to other branches are checked and rejected if the branch is protected, someone else has an open PR from it, or it carries commits authored by someone else. | Yes, and slightly more permissive than the design doc implied (non-`claude/` pushes aren't universally blocked, just conditionally). |

**Also confirmed, not previously in doc:** routines run as full autonomous sessions with **no permission-mode picker and no approval prompts mid-run** — directly confirms §4.1's claim that board-based escalation is the only escalation channel, not a design preference.

**Action for Keshav:** log into claude.ai/code/routines once and note the actual daily run cap number shown for your account — needed for Task 5.5, not blocking for Phase 0.
