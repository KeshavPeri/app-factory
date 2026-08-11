# Handoff — App Factory build session #3 (Phases 5 and 6)

**For:** a fresh Cowork chat. Sonnet is fine for this one — Phases 5/6 are configuration and
verification, not prompt-writing (the Fable pass was spent where it mattered, on Phase 4).
**From:** the Phase 4 build session, 9 August 2026
**Owner:** Keshav (Singapore)
**Scope of this session:** Phase 5 (configure the routine) and Phase 6 (smoke test) only.
**Stop when Phase 6 is done.** Do not start Phase 7 (FPL feature tickets) — write
`HANDOFF-phase-7.md` in the same structure as this document once 6.10 is verified.

---

## 1. What Phase 4 actually produced

All of workplan tasks 4.1–4.7 are Done in `app-factory-workplan-v2.xlsx`.

**In `fpl-advisor` (all on `main`):**
- `escalation.md` (repo root) — the single canonical copy of the §4.5 tiers plus Rules A
  and B. Programmatically verified verbatim: every paragraph is an exact substring of
  `app-factory-system-design-v2.md`. Nothing else in either repo restates the tiers.
- `.claude/agents/analyst.md`, `builder.md`, `qa.md` — v0.2, substantially rewritten from
  the v0.1 drafts. Each now has the YAML frontmatter Claude Code requires to register a
  subagent (the drafts had none and would not have loaded at all). Analyst is restricted to
  read-only + web tools; Builder and QA inherit full tools. All three encode the
  subagent-mediation model (see §3) and required output formats.
- `CLAUDE.md` — full version replacing the stub: branch convention, the five board columns
  with meanings, decisions.md location and rules, design-pass rule, agent list, stack,
  commands, key names, hard rules.
- `design-reference.md` (repo root) — copied from assets; Phase 3 never actually copied it
  into the app repo even though the Builder definition depends on reading it every ticket.
- `.claude/settings.json` — permission allowlist for interactive sessions (see §3).
- `decisions.md` — ROUTINE entry #3 logs the task 4.7 dry-run results.

**In `app-factory`:**
- `assets/agents/*` and `assets/escalation.md` — byte-identical mirrors of what is committed
  in fpl-advisor. Keep them in lockstep or not at all.
- `assets/orchestrator-prompt.md` — v0.2. **This is the text Phase 5 pastes into the
  routine.** New since v0.1: explicit subagent-mediation mechanics, orchestrator counts
  revision rounds, step 6 (orchestrator opens the draft PR, polls for the Vercel preview
  URL, splices it into the packet), step 8 (end-of-run summary note), ticket-number
  prefixes on log entries.
- `CLAUDE.md` — new; factory-repo context for future sessions.
- Workbook: Setup rows 4.1–4.7 → Done (497 formulas recalculated, zero errors).

**Dry-runs (task 4.7):** all three subagents passed on first invocation, run interactively on
Sonnet 5. Analyst returned Tier 3 for in-game currency display and Tier 1 (question only,
unanswered, phone-answerable) for login-cookie storage. Builder produced a clean
`claude/ticket-0-home-footer-version` branch with commits, passing build/lint, and the
structured handback. QA returned per-item verdicts and a five-part packet — and correctly
refused to fabricate a preview URL for an unpushed branch. Full detail:
`fpl-advisor/decisions.md` #3.

## 2. Decisions that departed from the Phase 4 brief (all owner-approved)

- **Tasks 4.2 and 4.6 were done as one pass.** The tiers were never inlined in analyst.md;
  `escalation.md` was written first and referenced from the first commit. 4.2's
  word-for-word criterion is satisfied by escalation.md (verified programmatically), avoiding
  a throwaway commit and a second copy that could drift.
- **The orchestrator, not QA, opens the draft PR.** Design §4.4 step 7 is passive ("draft
  pull request opens"); the v0.1 QA draft claimed it. Resolved: QA returns packet text with a
  `<PREVIEW_URL>` placeholder on line 1; the orchestrator opens the PR, waits for the Vercel
  URL, and splices it in. This also fixes a chicken-and-egg the drafts missed — the preview
  URL doesn't exist until the PR is open.
- **QA gained an honesty protocol**: every DoD item gets VERIFIED / FAILED / CANNOT VERIFY,
  and device-level items ("works on the installed iPhone PWA") are *always* CANNOT VERIFY,
  listed in packet item 4. QA also never edits code, so revision counting stays honest.
- **Assets bumped to v0.2** rather than frozen at v0.1, so the factory copies match what
  actually runs. Phase 8 still rewrites from evidence.

## 3. Things learned that this session should carry

- **The v0.1 agent drafts had no YAML frontmatter** and would never have registered as
  subagents. Any future agent file: frontmatter must be the first bytes of the file.
- **Subagents cannot talk to each other.** Every "Builder asks the Analyst" in the drafts was
  rewritten as return-to-orchestrator → orchestrator dispatches → re-invoke. Watch for the
  old pattern sneaking back into any prompt text you touch.
- **Interactive sessions prompt for command permissions; Routines don't.** The dry-runs
  prompted repeatedly, so `.claude/settings.json` now allowlists the pipeline's command
  families (npm/npx/node/git/gh plus read-only utilities) with `acceptEdits` mode. Overnight
  runs were never affected — §4.1: no mid-run permission prompts. `rm` and other destructive
  utilities are deliberately off the allowlist; an unusual command still prompts once
  interactively, and "always allow" adds it to settings.local.json.
- **Check the "copy design-reference.md into the app repo" step for every future app** —
  Phase 3 silently skipped it for app #1.

## 4. What this session does

**Phase 5 (tasks 5.1–5.6):** configure the routine at `claude.ai/code/routines` (no CLI
needed). The routine prompt is the **full text of `assets/orchestrator-prompt.md` v0.2** —
paste it whole, including steps 6 and 8. Schedule 2–3 fixed nights per week (§6 — nightly is
a Later upgrade). Confirm repo write access and the `claude/` branch-prefix restriction
(5.4). Record the per-account daily run cap in `environment-baseline.md` with the date —
task 0.2 confirmed it is not in the docs, only on Keshav's own dashboard (5.5). Trigger one
manual run with an empty board to confirm the trigger fires (5.6) — one-off runs don't count
against the daily cap.

**Phase 6 (tasks 6.1–6.10):** one throwaway smoke ticket end to end — write it with the
issue template, lint it in an evening interactive session (never inside the routine), queue
it, read the morning-after log, verify the draft PR and all five packet items (preview URL
first line). Then the two failure-path tests: cheap-exit on an empty Ready column (6.8 —
confirm it did *not* load the brief or repo first) and the Tier-1 block test (6.9 — queue a
harmless second ticket so you can watch the run continue past the blocked one). Anything
wrong gets fixed in the agent definitions and re-run — never by hand-editing a one-off
output (6.10). If you fix a definition in `fpl-advisor`, update the byte-identical mirror in
`app-factory/assets/` in the same sitting.

## 5. Open items and warnings

- **Board column casing is unverified against the live GitHub board.** CLAUDE.md and the
  orchestrator prompt say "In progress" / "For review" (design-doc casing); the Phase 0–3
  handoff wrote "In Progress" / "For Review". Look at the actual board before creating the
  routine and make the prompt text match the board exactly — the orchestrator matches
  columns by name at 3am.
- **`product-brief.md` does not exist until task 7.1.** The Analyst is written to treat
  brief-dependent questions as unanswerable rather than guessing — expected behaviour in the
  smoke test, not a bug.
- **The orchestrator's Vercel-URL polling (step 6) is untested** until 6.5/6.6 exercise it.
  If the preview URL reliably fails to appear in the PR in time, that's a definition fix in
  orchestrator-prompt.md, and the routine's prompt must be updated to match.
- Re-verify anything platform-specific (Routines dashboard, Vercel, Supabase) at the time of
  this session — these products moved underneath both prior sessions mid-work. Routines is
  still a research preview (§9 risk #9).
