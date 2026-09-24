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

## Standing rules for the orchestrator — binding from 24 Sept 2026

Copied verbatim from `MODEL-DIAGNOSIS-2026-09-24.md` §16; section references (§1b, §7, §8, §11) point there.

These exist because the project spent ~50 PRs going in circles (§2, §3). They apply to every future
orchestrator session on this app and on the next one. Copy them into `app-factory/CLAUDE.md` so they
survive beyond this file. If a rule gets in the way, say so to Keshav in one line and ask — do not
quietly work around it.

#### A. Before writing any ticket
1. **Research before you design.** For any modelling or data question, first spend up to 30 minutes
   finding how others already solve it (FPL Review docs, OpenFPL, public repos, papers). Name the
   source in the ticket. If nobody does it this way, treat that as a warning, not an opportunity.
2. **Test the idea before you ticket it.** Run it yourself in an interactive session on public CSVs
   (template: `experiments/2026-09-24-gbm/`). Only ticket changes that already showed their gain
   offline, and put that measured gain in the ticket. An untested idea is not a ticket.
3. **Check the premise at its source.** Before a number goes into a ticket or a message, open the report
   it came from and confirm exactly what is compared with what, on which rows. Quote file and line.
   (§1a: "0.354 vs 0.345" was two model versions, not model vs naive.)
4. **Ask the one question.** "Will this change what Keshav sees, or what gets recommended to him, within
   two runs?" If the answer is no, don't write the ticket.
5. **Know a metric's normal value before calling it a defect.** Compute what a decent model scores on it
   (§1b: captain vs best-other-starter is about −5 per GW for any good model).

#### B. Ticket shape
6. **Every model ticket carries an offline gate** the Builder computes itself from public data before
   marking the PR done: the metric, the reference number, the threshold, and "if missed: stop and
   report, do not tune". No gate may depend on Supabase, a GitHub Action, or a human.
7. **Liveness before comparison.** Every gate first checks the new code path actually ran (row count
   > 0). Identical before/after numbers are a FAIL.
8. **Definition of done is offline only.** Anything live goes in "Post-merge owner check (does not
   block this PR)".
9. **One scoreboard.** The §7 primary metric (5-GW Spearman, active players, zeros included) and the
   captain/top-11 decision checks. Do not add, swap or redefine metrics without Keshav's explicit
   approval. Never gate on 1-GW Spearman of players who featured.
10. **File-disjoint and contract-disjoint.** Tickets in one batch must not edit the same file or change a
    function another ticket in the batch imports. Freeze shared signatures in an earlier run.
11. **Short tickets, short code.** Ticket bodies under ~80 lines. Code comments only where the reason
    isn't obvious; decision logs under ~15 lines. No essays in source files.

#### C. What not to write
12. **No instrument-only tickets.** A report section, preflight check, diagnostic or coverage counter is
    allowed only if it names the model or product ticket in the *next* run that it unblocks.
13. **No data-substrate tickets for modelling.** History comes from vaastav + FPL-Core-Insights. No new
    Supabase history tables.
14. **No one-constant tickets.** Never a ticket whose whole change is one fitted constant, slope,
    shrinkage K or multiplier.
15. **Settled questions stay closed** unless there is new evidence from a *different* data source or a
    *different* population: fixture-term tuning, conversion factors, shrinkage K, the minutes window,
    the bonus exponent, the TypeScript learned model, penalty-duty treatments in baseline-v1.

#### D. Budget and stop signals
16. **Two strikes per idea.** An idea gets at most two runs. If it misses its gate twice, park it, write
    two lines in `model/README.md`, and move on. No third attempt, no "instrument to find out why".
17. **Run budget is 7** (§8). Any ticket not in the plan must say which planned item it replaces.
    Adding runs beyond 7 needs Keshav's explicit yes.
18. **Something visible every run from run 3 on.** At least one ticket per run must change what
    Keshav sees or what gets recommended.
19. **Progress check every 3 runs.** Send Keshav five lines: what he can do now that he couldn't before;
    the primary metric now vs last check; runs used vs budget; what's next; anything blocked.
    **If two runs in a row produced no user-visible change and no metric gain, stop writing tickets and
    tell him plainly before doing anything else.**
20. **Time-box surprises.** When a number moves unexpectedly, suspect the measurement first, but spend
    at most one interactive hour on it. Never write a ticket just to investigate.
21. **Scope is frozen to §11.** New feature ideas go on a parking list at the bottom of
    `feature-list.md`, not into tickets, until the budget is spent.

#### E. Reading results
22. Compare baselines only on the same rows in the same run — never across reports.
23. Fewer than ~10 settled gameweeks of live results is noise (the scorecard, captaincy). Don't act on
    it unless the effect is huge and the cause is obvious.
24. A metric that jumps after an unrelated change is a leak until proven otherwise (LEARNINGS §18).

#### F. Talking to Keshav
25. Lead with the answer. Plain, short English. Exact paste-ready commands, no trailing `#` comments.
26. Every headline number states the comparison, the rows and the sample size ("model 0.59 vs naive
    0.45, active players, 2025-26, 13,259 rows"). If unsure, say unsure.
27. When a previous answer or a handoff was wrong, say so in one line and move on.
28. Handoffs separate **measured** (with file and line) from **opinion**. Never pass on a headline you
    haven't re-checked at its source.

#### G. Checklist to answer in every ticket hand-over message (yes/no, one line each)
- Researched how others do this, with a named source?
- Tested offline, and the measured gain is written in the ticket?
- Offline gate with reference number, threshold and stop rule?
- Changes something Keshav sees or gets recommended within two runs?
- File- and contract-disjoint from the rest of the batch?
- Inside the 7-run budget, or replacing a named planned item?

Any "no" means the ticket is not ready. Say which one, and why it should still go ahead, or drop it.
