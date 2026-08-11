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
