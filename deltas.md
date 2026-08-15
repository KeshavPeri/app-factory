# Routines deltas since 9 Aug 2026 — Task 0.3

Checked 9 August 2026 against https://code.claude.com/docs/en/routines. See `routines-verification.md` for the full fact table.

**No deltas that break a design assumption.** All three facts checked in Task 0.2 (minimum interval, daily run cap, `claude/` branch restriction) match or are stricter/looser in ways that don't affect §4 of the design:

- Minimum interval and the `claude/`-branch default both confirmed as designed.
- The daily run cap is real but its exact number isn't in the public docs — it's per-account and visible only on the live dashboard. Not a delta, just a number Keshav needs to pull himself (Task 5.5).
- One extra fact worth carrying forward: **one-off scheduled runs don't count against the daily cap.** Not used by the current design (which uses a recurring 2–3/week schedule) but worth knowing if the smoke test (Phase 6) wants a one-off run without spending daily-cap budget.

No action required before Phase 4.

---

# Second pass — 9 August 2026, before Phase 5

Re-read of https://code.claude.com/docs/en/routines **and** https://code.claude.com/docs/en/cloud-environments.
The first pass only read the Routines page; the environments page is where most of the
following lives, and it materially affects Phase 5. **Five deltas, one of them structural.**

## D1 — The GitHub proxy blocks GraphQL. Projects v2 has a REST path out.

> ## SETTLED BY EXPERIMENT, 9 Aug 2026 — the board is unreachable, labels adopted
>
> Two probe runs answered this conclusively. **Every path is closed:**
>
> | Path | Result |
> |---|---|
> | GraphQL API (Projects v2's native API) | 403, explicit deny. Tested via `curl` *and* `gh` |
> | REST, user/org-scoped `projectsV2` | 403 — *"sessions are bound to their configured repositories"* |
> | REST, repo-scoped `projectsV2` | The proxy's own suggested fallback. **GitHub publishes no such endpoint** |
> | Built-in GitHub MCP tools | Issues, labels, comments, PRs. No projects tools at all |
> | MCP connector bypass (routes via Anthropic's servers, not the session proxy) | No GitHub connector exists in the registry. Checked 9 Aug 2026 |
>
> The only remaining route was a GitHub Actions workflow doing the GraphQL outside the proxy.
> **Rejected** — it needs a classic PAT with `project` scope as a repo secret, and it adds a
> second unproven moving part during the phase whose job is to prove the first one works. Same
> shape as the Telegram dispatch §7 already rejected.
>
> **Adopted: issue labels as machine state, Done as issue-closed.** Rationale, for the record:
> labels live *outside* the run's success path, so a run can die at any point without losing a
> transition — which is what §2's crash-tolerance constraint actually demands. A blocked issue
> also notifies Keshav's phone, which Rule B depends on and a file cannot do. Ordering is
> ascending issue number; that is the whole priority mechanism.
>
> **Also proven along the way:** the custom network allowlist works (`fpl=200 vercel=200`), and
> `gh`/`curl` are useless against this repo's API paths from a cloud run — only the built-in
> GitHub tools authenticate through the proxy.
>
> Two consequences worth carrying: the routine **cannot push to `main`**, so `decisions.md`
> entries ride the ticket branch and land at merge — a blocked ticket's decisions must go in the
> issue comment instead; and `issue_write` **replaces the whole label set**, so every state
> change must read-modify-write the full array or it destroys non-status labels.
>
> ---
>
> **Corrected the same day, before anything was built on it.** The first version of this entry
> called the board unreachable. That was written from the Routines/environments docs alone and was
> too pessimistic: GitHub now ships **REST endpoints for Projects v2** (live in API version
> `2026-03-10`, covering projects, fields, items, views, and item updates for both org- and
> user-owned boards). REST doesn't touch the proxy's GraphQL restriction. The likely outcome is
> that `gh project ...` fails and `gh api /users/KeshavPeri/projectsV2/...` works. The probe now
> tests both paths; the original analysis is kept below because the failure mode it describes is
> still live if the REST path turns out to be blocked by token type.
>
> One caveat the probe must settle: GitHub documents the **user-owned** project endpoints as not
> working with GitHub App tokens or fine-grained PATs. If the routine's proxy authenticates as a
> GitHub App, the user-scoped endpoints may 401/403 even though the org-scoped ones would work.
> That is why the probe reports which token mode is in play alongside every project call.


### The original analysis, kept for the failure case

Cloud sessions reach GitHub through a dedicated proxy. Per *Cloud environments → GitHub proxy*:
the proxy "serves only a pinned set of GraphQL operations for pull-request workflows," rejects
everything else on the GraphQL endpoint with a 403, and **names Projects v2 as unreachable**.
The restriction applies regardless of credentials — a `GH_TOKEN` you supply yourself gets the
same 403.

**Why this matters:** the entire design routes on the orchestrator reading the GitHub project
board and moving cards (§4.3, §4.4). GitHub Projects *is* Projects v2. If the doc is accurate as
written, the orchestrator cannot read the board or move a card at 3am — the board can still be
the source of truth for *Keshav*, but not for the routine.

**Not resolved by reading.** Owner decision, 9 Aug 2026: probe before redesigning. Task 5.6's
manual trigger is repurposed into a diagnostic run (`assets/routine-probe-prompt.md`) that tries
the Projects v2 calls for real and reports what actually happens. Only if the probe confirms the
block do we move to the fallback below.

**Fallback if confirmed (not adopted yet):** issue **labels** become the machine-readable state —
`status:ready`, `status:in-progress`, `status:for-review`, `status:blocked`, Done = issue closed.
Labels are REST, which the built-in GitHub tools reach without GraphQL. The Projects board stays
as a human-readable view. This preserves §4.3's four-columns-plus-Blocked semantics and the
board-as-single-source-of-truth principle; only the storage mechanism changes. It is not a
reversal of a §7 decision.

## D2 — Schedule presets, and the cron field is UTC

> **Corrected 9 Aug 2026 from the live form, which is more current than the docs.** The web
> trigger picker offers **Once / Hourly / Daily / Weekdays / Weekly / Custom**, and **Custom takes
> a cron expression directly in the browser**. The docs' claim that custom intervals need
> `/schedule update` from the CLI is out of date. 2–3 fixed nights a week is therefore available
> without touching a terminal whenever we want it.
>
> **The cron field is interpreted in UTC**, while the summary line above it renders local time.
> Observed: `0 1 * * *` displayed as "Runs daily at 9:00 AM SGT" — the +8 offset. Trust the summary
> line, not the expression. Consequence for day-of-week crons: 02:00 SGT is 18:00 UTC *the previous
> day*, so Tue/Thu/Sun nights SGT are `0 18 * * 1,3,6`, not `2,4,0`. Getting this wrong shifts every
> run by a day, silently.

The docs' version of this delta, now superseded:

The web form offers **hourly / daily / weekdays / weekly** only. A specific set of nights needs a
cron expression set from the CLI (`/schedule update`), which conflicts with Phase 5's
"no CLI needed" framing.

**Owner decision, 9 Aug 2026: run the `daily` preset for now**, departing from §6's 2–3 runs/week.
*Because* the cheap-exit (§4.4 1a) makes an empty-board night nearly free, so real throughput is
governed by what Keshav queues, not by the schedule; and `daily` avoids the CLI step entirely.
Revisit if the daily run cap or quota is actually hit — that is the observation §6 asks for,
just measured from the other direction.

## D3 — `gh` CLI is not pre-installed in cloud sessions

Cloud VMs ship git, jq, ripgrep, Node 20/21/22, Python, Docker, Postgres — but **not `gh`**.
Built-in GitHub tools cover reading issues, listing PRs, fetching diffs and posting comments.
Anything beyond that (and any Projects command) needs `gh` installed via the environment's
**setup script**: `apt update && apt install -y gh`. The result is cached, so it doesn't re-run
every session.

## D4 — Vercel and the FPL API are not on the Trusted allowlist

The **Default** environment uses **Trusted** network access. The published allowlist includes
GitHub, npm, PyPI, Docker Hub and the usual registries — it does **not** include `*.vercel.app`,
`vercel.com`, `*.supabase.co`, or `fantasy.premierleague.com`. Requests to unlisted hosts fail
with `403` and `x-deny-reason: host_not_allowed`.

Consequences: QA cannot fetch the Vercel preview URL to test against it, and (Phase 7) the
Builder cannot call the FPL API. Fix is a **Custom** network policy with those domains added and
"include default list" checked. Handled in the Phase 5 runbook by creating a dedicated
**App Factory** environment rather than mutating **Default**.

## D5 — Smaller facts worth carrying

- **A model selector sits on the routine prompt** and applies to every run. Owner decision,
  9 Aug 2026: **Sonnet 5** — all three Phase 4 subagent dry-runs passed first time on Sonnet, and
  §2 makes quota the binding constraint.
- **All connected MCP connectors are included in a new routine by default**, with full write
  access and no prompts. Remove every one the pipeline doesn't need.
- **A green run status means the session exited without an infrastructure error — not that the
  task succeeded.** Relevant to task 6.4: read the transcript, don't trust the dot.
- **Repos are cloned fresh from the default branch every run.** `.claude/agents/`, `CLAUDE.md`,
  `escalation.md`, `design-reference.md` and `.claude/settings.json` all arrive with the clone —
  which is why Phase 4 committing them to `fpl-advisor` was load-bearing.
- Since v2.1.214 the routine's saved prompt reaches the session **as its assigned task**, not as
  untrusted background content. Baseline is 2.1.226, so this is fine — but any text typed into
  **Run now** arrives wrapped as untrusted data and is ignored unless the saved prompt asks for it.
- Setup scripts must exit zero and finish inside ~5 minutes, and the cache rebuilds when the
  script or the allowed-domain list changes, or after ~7 days.



---

# D6 — Two concurrency bugs, observed on the first real 2-ticket run (11 Aug 2026)

Tickets #8 and #9, one run. Both bugs are the same failure category at different layers:
concurrent actors assuming exclusive access to shared mutable state.

## D6a — Two Builders, one working tree

The orchestrator dispatched both Builders in parallel into `/home/user/fpl-advisor` — one
checkout, one `.git`, one `HEAD`, no `isolation: 'worktree'`. Ticket #9's `git checkout -b`
interleaved with ticket #8's checkout→commit sequence, and #8's first commit (`98989d0`, the
Geist packages) landed on `main` **and** on `claude/ticket-9-supabase-reference-schema`, not
only on its own branch.

Self-healed before any push: local `main` force-reset to `origin/main`, #9's branch reset to its
pre-contamination tip, #8's Builder moved itself into a hand-made worktree. Verified clean
afterwards by `git merge-base`, `git fsck --full` and a diff against `origin/main`.

**The precise gap.** The orchestrator prompt already said "one writer per branch, always" — and
that rule was *satisfied*. It is the wrong invariant. **One writer per working tree** is the one
that matters, and nothing stated it. Detection was luck: one Builder happened to read its own
`git log`. There was no designed check.

**Fixed 11 Aug 2026:** orchestrator prompt §4 now mandates `isolation: 'worktree'` on every
Builder dispatch in a multi-ticket batch, with sequential dispatch as the fallback when
isolation is unavailable. `builder.md` now requires a `git branch --show-current` check before
the first commit and before handback; `qa.md` now requires a branch-containment check as its
first mechanical step. Detection is no longer accidental.

## D6b — One global counter in `decisions.md`

`decisions.md`'s ROUTINE section used a flat, file-global counter (`#0, #1, #2...`). Both ticket
branches forked from the same `main` tip (`21758b0`), whose file ended at `#4`, so both
independently continued from `#5` and both inserted at the identical point. Conflict on the
second merge.

**Deterministic, not a fluke.** Batch limit 2 + decisions committed on the ticket branch (forced:
the routine cannot push to `main`) + one shared insertion point = a conflict on every 2-ticket
run, which is the normal batch size.

**The fix that was proposed and rejected.** Ticket-scoped entry keys (`#8.1`, `#9.1`), mirroring
what HIGH-IMPACT already does. This does **not** work: git conflicts on *position*, not on
content. Two branches inserting different lines at the same point in the same file still
conflict. HIGH-IMPACT escaped this run by positional luck, not by its numbering scheme — it
would collide under the same conditions.

**Fixed 11 Aug 2026:** one file per ticket, `decisions/ticket-<number>.md`. Two branches touching
two different files merge cleanly by construction. `decisions.md` in the repo root becomes a
read-only archive of everything logged before the split. Orchestrator prompt §7, `CLAUDE.md` and
`decisions/README.md` all updated.

**Carry-forward for any new app:** create `decisions/` at scaffold time. Do not start a shared
append-only log in a pipeline that runs branches concurrently.


---

# D7 — Two open unknowns resolved on the 11 Aug wave-B run (#10, #15)

**The GitHub App CAN push `.github/workflows/`.** Ticket #10 added
`.github/workflows/scheduled-jobs.yml` on a `claude/` branch and the push was accepted. The
`workflows` permission is present. This was flagged as the most likely failure mode for #10 and
for every future workflow ticket; it is now a closed question. Stop carrying the caveat.

**Both D6 fixes held on their first real run.** Two Builders, two tickets, no branch
contamination in the log, and `decisions/ticket-10.md` and `decisions/ticket-15.md` were created
as separate files with root `decisions.md` untouched — so the re-pasted orchestrator prompt took
effect and the per-ticket split works as designed. No merge conflict on either PR.

**Carry-forward, unresolved.** The `decisions.md` collision class is fixed, but the *shape* of it
recurs for any file two tickets in one batch both append to. Wave C (#11 and #12) both add a step
to `.github/workflows/scheduled-jobs.yml` and will collide the same way. Ticket #12 now carries an
explicit DoD item requiring both steps to survive the merge. **When scoping a batch, check whether
the two tickets append to the same file** — not just whether they depend on each other.


---

# D8 — Supabase RLS and GRANTs are two gates, and the schema tickets only closed one

Observed 11 Aug 2026, first `workflow_dispatch` run of the fpl-advisor heartbeat:

```
heartbeat: insert into job_runs failed: permission denied for table job_runs
```

Both schema migrations (#9 reference tables, #10 `job_runs`) created tables, enabled Row Level
Security and added a `SELECT` policy for `anon` — and issued **no `GRANT` at all**. The tickets
asked for RLS and got RLS; nobody asked for grants.

**The distinction.** A query must pass both gates. GRANTs decide whether a role may touch the
table at all; RLS decides which rows once it is inside. The secret key's `service_role`
**bypasses RLS but not GRANTs**, so it was refused at the outer gate while the policy sat there
looking correct.

Read the error text to tell them apart:

| Message | Gate that closed |
|---|---|
| `permission denied for table X` | missing **GRANT** |
| `new row violates row-level security policy` | missing or wrong **POLICY** |

**Why the tickets missed it.** "Enable RLS with a read-only policy for anon" reads like a
complete permissions specification and isn't. Neither the Analyst lint nor QA caught it, because
both migrations applied cleanly against local Postgres — where the test ran as a superuser, for
whom grants are irrelevant. **The local-Postgres DoD is blind to this entire class of bug.**

**Fixed** by a follow-up migration granting `SELECT` to `anon` and `SELECT, INSERT, UPDATE` to
`service_role`, plus `ALTER DEFAULT PRIVILEGES` for future tables. `DELETE` deliberately
withheld, so "no deletion of existing rows" becomes a database guarantee rather than a promise
in a ticket.

**Carry-forward for every new app.** Any ticket that creates a Supabase table must require
`GRANT`s in the same migration file, as a definition-of-done item, not as an assumption. Added
to `assets/new-app-kickoff.md` Part 3.


---

# D9 — Cross-season id instability is not just a player problem. It repeats at every level.

Found 15 Aug 2026 while linting the feature-list item 10 ticket, before anything read the affected
column. Not observed as a failure — observed by reading the code and then checking the source data.

**The finding.** `scripts/ingest-core-insights.ts` upserted full team rows into `public.teams` with
`onConflict: 'id'`, from the **2025-2026** season file. FPL team ids are re-assigned every season
along with the promoted and relegated clubs. Fetching both season files from the source and diffing
them:

```
https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data/2025-2026/teams.csv
https://raw.githubusercontent.com/olbauday/FPL-Core-Insights/main/data/2026-2027/teams.csv
```

**Only 5 of 20 team ids referred to the same club in both seasons.** Id 3 was Burnley, is now
Bournemouth. Id 12 was Liverpool, is now Ipswich Town. Id 13 was Man City, is now Leeds. `teams.code`
is stable: all 17 clubs present in both files carry the same `code` *and* the same `elo` in both.

**Why it stayed silent.** `scripts/ingest-fpl.ts` runs after the core-insights job in the same
workflow and upserts the same table on the same key, so `name`, `short_name` and the `strength_*`
columns ended up correct — the FPL ingest overwrote them last. But `elo` is written *only* by the
core-insights job and is never overwritten, because `bootstrap-static/` has no elo field. So the
live table carried the right names against the wrong ratings for roughly fifteen clubs, and no
consumer existed yet to notice.

**The generalisation, and the actual lesson.** #12 and #22 established "FPL element ids are not
stable across seasons; `code` is." That finding was then applied to **players and only to players**.
The identical property holds for teams, and would hold for any other entity a per-season source
re-keys. Fixing the instance is not the same as fixing the class.

**Carry-forward for every new app.** When a source is per-season, per-year, or per-any-epoch:

- **Enumerate every entity it keys**, not just the one that produced a visible bug, and check each
  for a stable identifier before writing an upsert conflict target.
- **A silent column is the dangerous one.** The corruption here survived precisely because a second
  job repaired every column *except* the one nothing read yet. A column with no consumer has no
  error path — it is wrong until the first consumer is built, and then it is wrong in production.
- **One writer per table column-set.** The root cause was two jobs upserting the same table on the
  same key with different notions of what the key means. Team identity now belongs to
  `scripts/ingest-fpl.ts` alone; the historical-season job contributes `elo` and nothing else,
  matched on `code`.

**Also worth carrying:** the FPL-Core-Insights **2026-2027** directory now exists (it 404'd when
ticket #12 was written, which is why that job treats a missing season directory as a normal state).
Do not switch the ingest to it — that season has no played matches, and `player_match_stats` needs a
played season for the defcon and xG-rate estimators to have anything to estimate from. The
historical season is the point, and the season identifier being configurable is what makes both
true at once.


---

# D10 — An enumerated file-scope list becomes a contradiction the first time a ticket crosses a module boundary

Observed 15 Aug 2026 on the fpl-advisor run that built issues #32 and #33.

**What happened.** Ticket #33 (the baseline projection model) carried both of these, as written:

- a DoD item requiring the job to **import** the pure defcon estimator from `src/lib/projection/`
  rather than reimplement it, and
- a scope constraint enumerating the exact files that may change — which did not include
  `tsconfig.scripts.json`.

`src/lib/` uses `.ts`-extension imports, so `tsc -b` fails the moment a `scripts/*.ts` job imports
from it unless `allowImportingTsExtensions` is `true`. This was the first job in the repo to make
that crossing. **No implementation could satisfy both items.** The only literal-scope-compliant
option — duplicating the logic — was explicitly forbidden by the same ticket.

**The pipeline handled it correctly, and that is the reassuring half.** The Builder flipped the one
line, flagged the deviation rather than burying it, and proved by revert experiment that the build
genuinely fails without it. QA reproduced the experiment independently. The orchestrator declined to
rule on it and routed it to the Analyst, which classified it Tier 2 — decide, proceed, log loudly —
and it was logged with a full *because* in `decisions/ticket-33.md` and surfaced at the top of the
PR body. Total human cost: one paragraph to read.

**The fault was in the ticket, not the run.** This is the same shape as the four specification
defects in `LEARNINGS-first-build-wave.md` §2 — a DoD no correct implementation can fully meet —
but a new instance of it, and one that is easy to reproduce because the scope-constraint pattern is
otherwise the single most useful thing in a ticket (§8 ranks it second only to grep-checkable DoD
items).

**Carry-forward for every new app.**

- **A scope constraint that enumerates files is a claim about the build, not just about the diff.**
  Before writing one, ask: is this ticket the first to import across a module boundary, add a
  dependency, change a compilation target, or touch anything the build reads? If so, name the
  config file in the scope list, or the constraint and the DoD will contradict each other.
- **Prefer "nothing outside X changes, except build configuration required by this ticket's own
  imports, which must be logged as a decision"** over a bare file list, on any ticket that is the
  first of its kind.
- **Do not treat a flagged scope deviation as a red flag on the code.** A Builder that changes a
  file outside the list *and says so loudly* is the mechanism working. The thing to fear is the one
  that silently duplicates logic to stay inside the lines — which produces a clean-looking diff and
  a second copy of a rule that will drift.

**Second-order effect worth catching.** Once the boundary is crossed, any existing comment stating
the old convention becomes actively misleading — `scripts/sync-squad.ts` carried a paragraph
explaining why `scripts/` duplicates rather than imports. Left alone it would have taught the next
Builder to copy. Corrected in the same pass, with the new rule written into `CLAUDE.md`.
