# CLAUDE.md

This is the **factory repo** for a semi-autonomous overnight app pipeline. It holds the
design, the workplan, and the reusable assets — **no app code lives here.** App code lives in
one repo per app (first: `KeshavPeri/fpl-advisor`). Sessions in this repo are usually doing
one of three things: executing a workplan phase, revising assets, or writing a handoff.

## Owner and constraints

Keshav (Singapore), Claude **Pro** subscription — quota, not tooling, is the binding
constraint on every design decision here. Beginner-to-intermediate coder, limited CLI
comfort: spell out every terminal command; prefer web dashboards where they exist.

## The files

- **`app-factory-system-design-v2.md`** — the single working reference. Every § reference in
  this repo and in the app repos points into it. Read §7 ("Decisions Deliberately Made — Do
  Not Reverse") before helpfully suggesting changes: Agent Teams, a Reviewer subagent,
  auto-merge, nightly cadence and linting-inside-the-routine were all considered and rejected.
- **`app-factory-workplan-v2.xlsx`** — the phased workplan. The **Setup** sheet (phases 0–6)
  is the active track; task statuses are updated there as work completes. Formulas compute
  blocking and queue order — edit only the Status column unless you know the sheet.
- **`HANDOFF-*.md`** — session-to-session handoff notes. Each session's scope is set by the
  latest handoff; **stop at the scope boundary and write the next handoff** in the same
  structure rather than continuing into the next phase.
- **`assets/`** — the reusable pipeline assets: product-brief template, ticket template,
  design reference, `escalation.md`, and `agents/` (analyst, builder, qa + orchestrator
  prompt). **The agent files and escalation.md are byte-identical mirrors of what is
  committed in `fpl-advisor`** (`.claude/agents/`, repo root). Change them in lockstep or
  not at all — a drifted mirror is worse than none. v0.2 as of Phase 4; rewritten from
  evidence at Phase 8.
- **`routines-verification.md`, `deltas.md`, `environment-baseline.md`** — platform facts as
  verified on a given date. Claude Code Routines is a research preview: re-verify against
  current docs at time of use, never trust these files' screenshots-of-the-past.

## Rules that keep biting

- **Escalation tiers live in `assets/escalation.md`** (canonical copy: `fpl-advisor`
  repo root). Never restate them; reference them.
- Supabase key naming: **`VITE_SUPABASE_PUBLISHABLE_KEY`** (current publishable-key format),
  never the legacy `ANON_KEY` name — that's what is actually deployed in Vercel.
- FPL production URL is `https://fpl-advisor-wine.vercel.app` (the clean subdomain was
  taken — not a mistake).
- Merging app PRs is always manual; agents open draft PRs only. No agent ever creates
  accounts, API keys, or service sign-ups (Tier 1, owner-only).
- Decisions get logged **at decision time** in the relevant repo's `decisions.md`
  (HIGH-IMPACT entries state the *because*). For factory-level work, that log is in
  `fpl-advisor` until a factory-level log exists.
- Phase 8 rewrites the assets from evidence. Do not polish assets speculatively before
  then — that's a quota burn the design explicitly rejects (§10).

## Current state (update this line when it changes)

Phases 0–3 complete. Phase 4 files written and committed; task 4.7 (subagent dry-runs) still
to verify, then the workbook update and `HANDOFF-phase-5-to-6.md`. Do not start Phase 5/6
without that handoff.
