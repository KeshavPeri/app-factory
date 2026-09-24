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
  not at all — a drifted mirror is worse than none. v0.3 as of Phase 5 (labels replaced the
  project board); rewritten from evidence at Phase 8.
- **`GITHUB-SETUP-labels.md`** — the one-time GitHub-side setup the label pipeline needs.

**Two drift traps this repo has already fallen into once each.** (a) The live routine holds its
*own copy* of `assets/orchestrator-prompt.md` — editing the file changes nothing until it is
re-pasted into the routine's Instructions box, so every edit to that file ends with a re-paste
or it is not real. (b) A cloud run clones the app repo's **default branch**, so definition
changes that sit on a feature branch, or unpushed, are invisible to every run: after changing
anything in `fpl-advisor`, confirm with `git log origin/main --oneline -3` before assuming it
took effect.
- **`routines-verification.md`, `deltas.md`, `environment-baseline.md`** — platform facts as
  verified on a given date. Claude Code Routines is a research preview: re-verify against
  current docs at time of use, never trust these files' screenshots-of-the-past. `deltas.md`'s
  second pass (9 Aug, pre-Phase-5) carries the **Projects v2 / GraphQL-proxy** question — read
  D1 before touching anything that assumes the routine can move a board card.
- **`PHASE-5-RUNBOOK.md`, `PHASE-6-RUNBOOK.md`** — click-by-click execution notes for the
  current phase. Written from the docs as of 9 Aug 2026; if a dashboard screen doesn't match,
  the platform moved and the runbook is the thing that's wrong.

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

Phases 0–4 complete. Phase 5 tasks 5.1 and 5.3–5.6 complete (9 Aug 2026); 5.2 pending the
GitHub-side setup. **The GitHub project board is out of the design** — a routine cannot reach
Projects v2 by any path, proven by two probe runs; state is now `status:` labels on open issues,
Done = closed. Agent definitions, orchestrator prompt and escalation mirrors are at v0.3.
Next: `GITHUB-SETUP-labels.md`, then Phase 5 step 8, then Phase 6 per `PHASE-6-RUNBOOK.md`.
Do not start Phase 7 before that session writes `HANDOFF-phase-7.md`.

---

## Orchestrator responsibilities — added 24 Sept 2026

The orchestrator session runs all routine GitHub and git work for this system. The owner does not
hand-run `git commit`, `git push` or issue creation any more. See `ORCHESTRATOR-BRIEF.md` §7 for the
exact mechanics and `LEARNINGS-second-build-wave.md` §22d for why.

**Orchestrator does, unprompted:** pull/sync both repos; commit and push ticket drafts, learnings and
docs; create and comment on issues; read issues, PRs, checks, branch state and Action logs; trigger
GitHub Actions (`workflow_dispatch`) to run tests, backtests, preflight or the scheduled jobs, and read
the results. Running an Action replaces most of the hand-run commands the owner used to be given.

**Orchestrator does, but only on the owner's explicit instruction:** applying or removing
`status:ready` (it dispatches an overnight build and spends his usage); merging a PR (the last human
checkpoint before code reaches live data). One instruction away, not one command away — he should never
have to type these, but he must always choose them.

**Never the orchestrator:** applying a database migration (Tier 1 — hand over the SQL); deleting,
force-pushing or rewriting history; pasting a reply to a blocked Builder (drafted by the orchestrator,
pasted by the owner, because that channel resumes an existing agent).

**Mechanics:** `gh` is not installed in the device VM and git has no stored credentials there, but
`github.com` and `api.github.com` are reachable. Git identity is configured in both repos. A classic
PAT with `repo` and `workflow` scopes lives in `fpl-advisor/.env` as `GITHUB_TOKEN`; push via
`https://$GITHUB_TOKEN@github.com/...` and do everything else through the REST API. Never echo the
token.

Standing rules for writing tickets are in `MODEL-DIAGNOSIS-2026-09-24.md` §16 — research before you
design, test before you ticket, check every premise at its source, offline-only Definition of Done,
one scoreboard, no instrument-only tickets.
