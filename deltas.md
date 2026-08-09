# Routines deltas since 9 Aug 2026 — Task 0.3

Checked 9 August 2026 against https://code.claude.com/docs/en/routines. See `routines-verification.md` for the full fact table.

**No deltas that break a design assumption.** All three facts checked in Task 0.2 (minimum interval, daily run cap, `claude/` branch restriction) match or are stricter/looser in ways that don't affect §4 of the design:

- Minimum interval and the `claude/`-branch default both confirmed as designed.
- The daily run cap is real but its exact number isn't in the public docs — it's per-account and visible only on the live dashboard. Not a delta, just a number Keshav needs to pull himself (Task 5.5).
- One extra fact worth carrying forward: **one-off scheduled runs don't count against the daily cap.** Not used by the current design (which uses a recurring 2–3/week schedule) but worth knowing if the smoke test (Phase 6) wants a one-off run without spending daily-cap budget.

No action required before Phase 4.
