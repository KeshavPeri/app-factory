# Phase 5 runbook — configure the routine (tasks 5.1–5.6)

**Written:** 9 August 2026, from a fresh read of the Routines and Cloud-environments docs.
**All of this is web UI.** No terminal. Roughly 45 minutes, most of it waiting on one run.

Read `deltas.md` § "Second pass" first if you want the *why* behind steps 2, 3 and 7 — they are
not in the original workplan and exist because the platform moved.

**Order matters.** Steps 1–7 create the routine with a *throwaway diagnostic prompt* and run it
once. Step 8 replaces that prompt with the real orchestrator prompt — but only after the probe
tells us whether the project board is reachable at all. Don't skip ahead to step 8.

---

## Step 1 — Open the dashboard *(task 5.1)*

Go to **https://claude.ai/code/routines**.

You should see an empty routine list and a **New routine** button. Somewhere on this page or at
**https://claude.ai/settings/usage** there is a line showing **remaining daily routine runs** —
find it now, you need the number in step 6.

✅ *5.1 is done when* the page loads and you can see `fpl-advisor` offered in a repository picker
(you'll confirm this in step 3).

---

## Step 2 — Create a dedicated cloud environment

*Not in the workplan. Needed because of deltas D3 and D4: `gh` isn't pre-installed in cloud
sessions, and Vercel, Supabase and the FPL API are not on the default network allowlist.*

1. Go to **https://claude.ai/code** (not the routines page).
2. In the row just above the message box, click the **cloud icon** showing `Default`.
3. Click **Add cloud environment**.
4. Fill it in:
   - **Name:** `App Factory`
   - **Network access:** choose **Custom**. In **Allowed domains**, one per line:
     ```
     fantasy.premierleague.com
     *.vercel.app
     vercel.com
     *.supabase.co
     ```
     Then **tick "Also include default list of common package managers"**. If you don't tick it,
     npm and GitHub stop working and every run fails.
   - **Environment variables:** leave empty. Anyone using the environment can read these and
     there is no secrets store — Supabase keys stay in Vercel where Phase 3 put them.
   - **Setup script:**
     ```bash
     #!/bin/bash
     apt update && apt install -y gh || true
     ```
     The `|| true` matters: a setup script that exits non-zero stops the session from starting.
5. Click **Create environment**.

✅ *Done when* `App Factory` appears in the environment list.

> The script runs once, then the filesystem is snapshotted and reused, so it won't slow down
> every run. It re-runs if you edit the script or the domain list, or after about a week.

---

## Step 3 — Create the routine *(task 5.2, first half)*

Back at **https://claude.ai/code/routines** → **New routine**.

| Field | What to put |
|---|---|
| **Name** | `FPL Advisor overnight pipeline` |
| **Prompt** | The probe prompt — see below |
| **Model selector** (inside the prompt box) | **Sonnet 5** |
| **Repositories** | `KeshavPeri/fpl-advisor` — this one only |
| **Environment** | `App Factory` (from step 2) |
| **Trigger** | Schedule — see step 4 |
| **Connectors** | **Remove every one.** They're all included by default with full write access and no prompts. The pipeline needs none of them. |

**The prompt for now is the probe, not the orchestrator.** Open
`assets/routine-probe-prompt.md`, copy everything **below the `---` rule** (start at
"You are running a one-off diagnostic"), and paste it into the Prompt box.

Then click **Create**.

---

## Step 4 — Set the schedule *(task 5.3)*

In **Select a trigger**, choose **Schedule** → preset **Daily**, time **02:00**, your local zone
(Singapore). Times are entered in local time and converted automatically.

**This departs from §6's "2–3 runs per week", deliberately and with your approval.** The reason,
for `decisions.md`: the form has no 2–3-nights preset — that needs a cron expression from the CLI
— and the cheap-exit rule (§4.4 1a) makes an empty-board night nearly free, so what actually
governs quota is how many tickets you queue, not how often the routine fires. If the daily run
cap or your usage limit starts biting, that's the signal §6 wanted; drop to `weekly` or set a
cron then.

Expect runs to start a few minutes after 02:00 — there's a deliberate consistent stagger.

✅ *5.3 is done when* the routine's detail page shows a next run time.

---

## Step 5 — Confirm repo access and the branch restriction *(task 5.4)*

On the routine's detail page, confirm `KeshavPeri/fpl-advisor` is listed under repositories.

The `claude/` restriction is platform behaviour, not a setting you'll find a toggle for. Current
docs: branches prefixed `claude/` are **always accepted**; a push to any other branch is checked
and rejected if the branch is protected, someone else has an open PR from it, or it carries
commits authored by someone else. Also worth knowing: the GitHub proxy only allows `git push`
against the session's current working branch.

Our convention (`claude/ticket-<number>-<slug>`) sits inside the always-accepted case, so there is
nothing to relax.

✅ *5.4 is done when* you've seen the repo listed and written one line in `decisions.md` recording
that the restriction is confirmed-as-designed, not relaxed.

---

## Step 6 — Record the daily run cap *(task 5.5)*

Find the remaining-runs figure at **https://claude.ai/code/routines** or
**https://claude.ai/settings/usage** and write it into `environment-baseline.md` under the
Routines section (a stub is already there), with today's date.

Note while you're there: **one-off scheduled runs don't count against the daily cap**, and if you
turn on usage credits, runs past the cap go to metered overage — leave that **off** unless you
want to spend money, which §2 says you don't.

---

## Step 7 — Fire the probe *(task 5.6)*

On the routine's detail page click **Run now**. Leave the optional text box empty — anything typed
there arrives labelled as untrusted data and the prompt ignores it by design.

Wait for the run, then **click into the run to read the transcript.** A green status only means
the session exited without an infrastructure error — it does not mean the checks passed.

The probe prints a `PROBE REPORT` block and posts the same text as a comment on a scratch issue.
Bring that report back to the next session. The three lines that decide what happens next:

- **`4b. PROJECTS REST`** — whether the routine can read *and write* the project board over REST.
  This is the one that decides the architecture. (`4a. GRAPHQL` failing is expected and fine.)
- **`COLUMNS`** — the exact Status option names, which settles the casing question left open by
  the Phase 4 handoff (§5 of `HANDOFF-phase-5-to-6.md`).
- **`6. NETWORK`** — whether step 2's custom allowlist actually took effect.

✅ *5.6 is done when* a run session exists, terminated cleanly, and you have the report.

---

## Step 8 — Install the real prompt *(task 5.2, second half)*

**The probe verdict was NO** — the board is unreachable by every path (`deltas.md` D1). The
pipeline now runs on issue labels, and all the definitions have been rewritten to match. So this
step is now a straight paste, with no edits needed:

Open the routine → pencil icon → replace the probe prompt with `assets/orchestrator-prompt.md`
**v0.3**, everything **below the `---` rule** (start at "You are the orchestrator"). Save.

Before you do, complete the GitHub-side setup in `GITHUB-SETUP-labels.md` — the labels have to
exist and the smoke ticket has to be queued, or the first real run will cheap-exit correctly and
tell you nothing.

✅ *5.2 is done when* the routine's Instructions box holds the v0.3 orchestrator prompt.

---

## Workplan statuses to set when you finish

Setup sheet, Status column only:

| Task | Set to Done when |
|---|---|
| 5.1 | Step 1 |
| 5.2 | Step 8 (not step 3 — the probe prompt isn't the deliverable) |
| 5.3 | Step 4 |
| 5.4 | Step 5 |
| 5.5 | Step 6 |
| 5.6 | Step 7 |
