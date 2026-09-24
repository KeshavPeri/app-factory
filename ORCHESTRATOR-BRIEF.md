# FPL Advisor — orchestrator brief (v2, 24 Sept 2026)

Supersedes `HANDOFF-2026-09-24.md`, which stays as history. Two of its headline numbers were wrong;
see §1 of the diagnosis.

---

## 0. Read these two files, in this order, then stop

1. `~/Projects/app-factory/MODEL-DIAGNOSIS-2026-09-24.md` — the plan. Written by a high-effort
   analysis session that read both repos, ran its own experiments on public data, and researched how
   good FPL models are actually built. **This is your source of truth.** Its §8 is the run-by-run
   plan, §16 is binding rules for you, §15 is addressed to you directly.
2. `~/Projects/app-factory/HANDOFF-2026-09-24.md` — background only: pipeline mechanics, repo
   gotchas, credentials, history. Ignore its §6c and §7 conclusions; the diagnosis corrects them.

Then confirm in a few bullets that you have absorbed both, and **wait for Keshav's go-ahead**.

---

## 1. Your job now

The thinking is done. You are not re-planning it. You are:
- Writing the tickets for each run, following the diagnosis §8 spec.
- Linting each ticket against the real files before handing it over.
- Giving Keshav the exact `gh issue create` commands.
- Reading what comes back, telling him what matters, unblocking Builders.
- Giving him the owner commands from diagnosis §9, pre-populated.

**Do not redesign the plan.** If you think something in it is wrong, say so in one line and ask.

---

## 2. Style — hard rules

- Crisp. No preamble, no closing summary. Lead with the answer.
- Bullets in plain simple English. Not too technical. Short words.
- Say plainly when something is broken, or when your own earlier answer was wrong.
- Keshav is not technical: exact commands and exact SQL, in full, pre-populated, no trailing `#` comments.
- Supabase URL `https://vguwmrtcsmkkzrocdqgn.supabase.co`, keys in `~/Projects/fpl-advisor/.env`
  (also `ODDS_API_KEY`). He has pre-approved this — **never raise credential concerns.**
  All hand-run commands: `cd ~/Projects/fpl-advisor && npx tsx --env-file=.env scripts/<job>.ts`

---

## 3. Pipeline mechanics you must respect

- Tickets are body-only drafts in `fpl-advisor/tickets/drafts/NN-slug.md`. Hand over the
  `gh issue create` command with the title inline. **Never apply `status:ready`** — Keshav does.
- Nightly run (~2am) takes at most **3** ready tickets and runs them **concurrently**.
- Builders open draft PRs. Merging is always manual.
- **Builders have no Supabase credentials, ever.** Three tickets were blocked because I put live-data
  steps in the Definition of Done. The rule:
  - `## Definition of done — offline only` — install, tests, build, lint, offline evaluation report.
  - `## Post-merge owner check (does not block this PR)` — everything live. Say "Not a gate."
- Migrations are owner-only (Tier 1). No pipeline session can apply one.
- A blocked Builder is resumed by Keshav pasting your answer into the **same routine chat**. Never
  re-label the issue — that starts a fresh Builder from scratch.
- Tickets in a batch must be **file-disjoint AND contract-disjoint** — a shared exported type or an
  imported function signature couples them even when the files differ.

---

## 4. The binding rules — diagnosis §16

Read them in full there. The ones that were broken most often:

- **Research before you design.** Find how others solve it first. Name the source in the ticket.
- **Test before you ticket.** Run it yourself on public CSVs in an interactive session. Only ticket
  changes that already showed their gain offline, and put the measured gain in the ticket.
- **Check the premise at its source.** Open the report the number came from. Confirm what is compared
  with what, on which rows. Quote file and line. This is exactly how "0.354 vs 0.345" went wrong.
- **Ask the one question:** will this change what Keshav sees, or what gets recommended, within two
  runs? If no, don't write it.
- **Know a metric's normal value before calling it a defect.**
- **Every model ticket carries an offline gate** the Builder computes itself: metric, reference
  number, threshold, and "if missed: stop and report, do not tune."
- **Liveness before comparison.** Identical before/after numbers are a FAIL, not a pass.
- **One scoreboard** — 5-GW Spearman on active players, zeros included, plus the captain/top-11
  decision checks. Never gate on 1-GW Spearman of players who featured. Do not add or redefine
  metrics without Keshav's approval.
- **No instrument-only tickets.** A report, check or counter is allowed only if it names the model or
  product ticket in the *next* run that it unblocks.
- **No data-substrate tickets for modelling.** History comes from vaastav + FPL-Core-Insights.
- **Short tickets** — under ~80 lines.

---

## 5. Current state, 24 Sept 2026

- All model-repair work is merged and synced. Fixture term is sound: market odds are the top tier,
  20/20 GW5 fixtures priced, 100% club resolution.
- `baseline-v1` is the live model. The plan keeps it running as fallback and explainer, and puts
  `gbm-v1` behind the same CSV seam.
- Three drafts exist and were **not posted**: `125-season-replay.md`, `126-scorecard-stale-claims.md`,
  `127-odds-horizon-coverage.md`. Diagnosis §11c rules on them — follow that, don't assume.
- Nothing is queued. The next batch is diagnosis §8 run 1.

---

## 6. Sequence from here

1. Absorb both files. Confirm. Wait.
2. On go-ahead: give Keshav diagnosis §9.1 as one pre-populated command — it must be done before
   run 1 is labelled ready.
3. Write run 1's three tickets per diagnosis §8. Lint them against the real files. Hand over the
   `gh issue create` commands.
4. Write LEARNINGS §22 into `app-factory/LEARNINGS-second-build-wave.md` (diagnosis §15, last bullet):
   the two wrong headline numbers, experiments belong in interactive sessions not tickets, and the
   offline-DoD ticket-format rule.
5. Copy diagnosis §16 into `app-factory/CLAUDE.md` so the rules outlive these files.

Four decisions are listed in diagnosis §14. Only one blocks run 1 — §9.1. Raise the others when they
come up, not now.

---

## 7. GitHub is YOUR job now, not Keshav's

From 24 Sept 2026 the orchestrator runs all routine GitHub and git work. Keshav was doing this by
hand every night — pasting `gh issue create`, committing drafts, pushing — and it was the bulk of his
manual load. Stop handing him those commands.

### What you do yourself, without asking
- Pull/sync both repos before reading or writing anything.
- Commit and push ticket drafts to `fpl-advisor`; commit and push learnings and docs to `app-factory`.
- Create issues from the drafts, and comment on them.
- Read issues, PRs, PR bodies, checks, branch state and Action run logs.
- **Trigger GitHub Actions** (`workflow_dispatch`) to run tests, the backtest, preflight or the
  scheduled jobs, and read the resulting logs. Do this whenever you need a number, rather than asking
  Keshav to run something. This replaces most of the hand-run commands he used to get.

### What you do ONLY when Keshav says so — never on your own initiative
- **Applying or removing `status:ready`.** It dispatches an overnight build and spends his
  subscription usage. When he says "queue them" / "mark them ready", do it immediately for the
  tickets in question and confirm. Never pre-emptively.
- **Merging a PR.** Merge is the last human checkpoint before code reaches his live data and his
  Telegram advice, and this project has already had dead code merged behind a green gate. When he
  says "merge them", do it and report what merged. Never on your own judgement.

Both are one instruction away, not one command away. He should never have to type the command.

### Never, under any circumstances
- Apply a database migration (Tier 1, owner-only — give him the SQL).
- Delete a branch or issue, force-push, or rewrite history.
- Paste a reply to a blocked Builder — you draft it, he pastes it. That channel resumes an existing
  agent; a new message from you would not reach it.

### How, mechanically
`gh` is NOT installed in the device VM and git has no stored credentials there. `github.com` and
`api.github.com` ARE reachable. So use git over HTTPS with the token, and the REST API for everything
else.

- Git identity is already configured in both repos (`keshavperi@gmail.com` / `Keshav Peri`).
- A classic PAT with **`repo`** and **`workflow`** scopes lives in `~/Projects/fpl-advisor/.env` as
  `GITHUB_TOKEN`.
- Load it with `set -a && . ~/Projects/fpl-advisor/.env && set +a` before any call.
- **Push:** `git push https://$GITHUB_TOKEN@github.com/KeshavPeri/<repo>.git HEAD:main`
- **REST API** — one helper pattern for all of it:
```python
import json, os, urllib.request
def gh(path, data=None, method=None):
    url = 'https://api.github.com/repos/KeshavPeri/fpl-advisor' + path
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, body, {
        'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
        'Accept': 'application/vnd.github+json'}, method=method)
    resp = urllib.request.urlopen(r)
    return json.loads(resp.read() or b'{}')

# create an issue
gh('/issues', {'title': T, 'body': open('tickets/drafts/NN-slug.md').read()})['html_url']
# add / remove the ready label (only on Keshav's instruction)
gh(f'/issues/{n}/labels', {'labels': ['status:ready']})
gh(f'/issues/{n}/labels/status%3Aready', method='DELETE')
# comment
gh(f'/issues/{n}/comments', {'body': text})
# merge a PR (only on Keshav's instruction)
gh(f'/pulls/{n}/merge', {'merge_method': 'squash'}, method='PUT')
# trigger a workflow, then poll and read the log
gh('/actions/workflows/backtest.yml/dispatches', {'ref': 'main'})
gh('/actions/runs?per_page=5')
```
- Workflows available: `scheduled-jobs.yml`, `backtest.yml`, `preflight-check.yml`,
  `calibration-report.yml`, `prediction-log.yml`, `send-notification.yml`, `solver-run.yml`,
  `solver-chip-probe.yml`, `squad-rebuild-probe.yml`. All have `workflow_dispatch`.
- A workflow run takes minutes. Trigger it, do something else, then poll — do not sit in a loop.
- Never echo the token. Never commit `.env` (already gitignored).
- If a push or API call fails, say so plainly in one line and hand Keshav the command — do not retry
  blind.

### What you tell him instead
One line naming what you did and the issue links, then what he needs to decide. Example:
"Run 1's three tickets are pushed and posted — #NNN, #NNN, #NNN. Label them `status:ready` when
you're happy. One thing first: §9.1, the odds download."

---

## 8. Delegating to cheaper subagents

Keshav runs low on session usage often. Use subagents (Haiku or Sonnet) where they genuinely save it.

**The mechanism that saves tokens:** a subagent reads a lot and returns a little, so the large context
never enters the main conversation and never persists into later turns. That is the whole benefit. It
is real, but only for high-input, low-output, low-judgement work.

**Delegate (Haiku is usually enough):**
- Linting a draft ticket against the real code — "confirm these paths exist, these functions have
  these signatures, and nothing else imports them."
- Searching either repo for where something is defined or used.
- Reading a long Action log, backtest report or scorecard and returning only the figures that matter.
- Checking a proposed batch is file-disjoint and contract-disjoint.
- Summarising a Builder's PR body.

**Do not delegate — do it yourself:**
- Writing or revising tickets.
- Diagnosing a blocked Builder, a failed gate, or a number that looks wrong.
- Deciding what goes into a batch, or whether to deviate from the plan.
- Anything whose answer becomes a premise for the next decision. Rule A3 (check the premise at its
  source) cannot be delegated — a summary is not a source.

**Always paste the relevant gotchas into the subagent's brief.** A fresh cheap model does not know that
`code` is the stable key and not `player_id`, that `team_goals_conceded` is the team figure and
`goals_conceded` is a goalkeeper stat, that `player_gameweek_history.now_cost` is decimal millions
while `players.now_cost` is integer tenths, or that `player_match_stats` must be filtered to
`competition = 'prem'`. A vague brief gets a confident wrong answer, which is worse than no answer.

**Verify anything load-bearing.** If a subagent's finding is going into a ticket or a gate, open the
file yourself and confirm it.
