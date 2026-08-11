# Phase 6 runbook — the smoke test (tasks 6.1–6.10)

**Written:** 9 August 2026. **Do not start this until Phase 5 step 8 is done** — the routine must
be running the real orchestrator prompt, not the diagnostic probe.

Phase 6 spans at least three calendar days: queue in the evening, read in the morning, twice over.
That's the point — you're testing the overnight loop, not simulating it.

**The one rule for the whole phase (task 6.10):** anything that comes out wrong gets fixed in the
**agent definition**, and the ticket is re-run. Never hand-edit a one-off output to make it look
right. A hand-fixed PR description tells you nothing about whether the pipeline works. And if you
change a definition in `fpl-advisor`, update the byte-identical mirror in `app-factory/assets/`
in the same sitting — a drifted mirror is worse than none.

---

## Day 1, evening

### 6.1 — Write the smoke ticket

`assets/smoke-test-tickets.md` **Ticket A** is written and ready. Open a new issue in
`fpl-advisor` using the repo's issue template and paste it in.

✅ *Done when* the issue exists with every template field filled and a checkable definition of
done — no placeholders.

### 6.2 — Lint it in an interactive session

**In an interactive Claude Code session in `fpl-advisor`, never inside the routine** (§4.7 — this
is a settled decision, see §7). Open a session and say:

> Use the analyst subagent to lint issue #N. Return its verdict, its Tier-1 scope check, and its
> DoD verifiability note.

The Analyst returns PASS or NEEDS EDIT with specific problems named, a Rule-A scope check, and a
note on any DoD item QA won't be able to verify from a build/code check.

Ticket A was written to pass cleanly. **If the Analyst flags something anyway, that is a real
finding** — either the ticket has a hole you didn't see, or the Analyst is miscalibrated. Read the
reason before deciding which. Edit the ticket, or explicitly pass it and write down why.

✅ *Done when* the Analyst has read the ticket and it has been edited or explicitly passed.

### 6.3 — Queue it

Add the label **`status:ready`** to the issue. Make sure it's the only open issue carrying that
label — the probe's scratch issue #2 must be closed first, or the run will pick it up as a
ticket. Confirm the next run time on the routines dashboard.

✅ *Done when* exactly one open issue has `status:ready` and you know when the run fires.

---

## Day 2, morning

### 6.4 — Read the session log

Open **https://claude.ai/code/routines** → the routine → the run.

**A green status only means the session exited without an infrastructure error. It does not mean
the run worked.** Read the transcript.

You should be able to point at each of these in the log:

- [ ] The cheap-exit check ran **first**, before `CLAUDE.md`, the brief, or the repo were read
- [ ] Stale-ticket recovery ran (and found nothing — no `status:in-progress` issues)
- [ ] The issue moved `status:ready` → `status:in-progress`, and **no other label was lost**
      in the process
- [ ] A **builder** subagent invocation, working on `claude/ticket-<n>-<slug>`
- [ ] A **qa** subagent invocation, returning per-DoD-item verdicts
- [ ] `decisions.md` entries appended **during** the run, each prefixed with the ticket number —
      not one batch written at the end
- [ ] The orchestrator (not QA) opened the PR and polled for the Vercel URL
- [ ] An end-of-run summary note

Note anything you *can't* point at. That list is the input to 6.10.

Expect one thing that looks like a failure and isn't: `product-brief.md` doesn't exist until task
7.1, so the Analyst treats brief-dependent questions as unanswerable. That's designed behaviour.

✅ *Done when* you've read the whole log and can point at each subagent invocation.

### 6.5 — Verify the draft PR

- [ ] A PR exists, in **draft** state
- [ ] From a branch named `claude/ticket-<number>-<slug>`
- [ ] The issue carries **`status:for-review`**
- [ ] The PR body contains `Closes #<issue-number>` below the packet — that's what makes your
      merge close the issue and land it in Done
- [ ] Nothing was merged

✅ *Done when* all four hold.

### 6.6 — Verify the five-part packet

Check the PR description against §4.8, in order:

1. [ ] **Preview URL on the first line**, formatted `**Preview:** https://…`, and the link opens a
       working build. If it says "Preview: pending", the orchestrator's polling (step 6) needs a
       longer wait or a different signal — that's a definition fix.
2. [ ] **What changed in plain language**, 3–6 sentences, **no file list**
3. [ ] **High-impact decisions with their *because***, or the explicit word "None"
4. [ ] **What QA tested and what it did not**, with every CANNOT VERIFY item named individually —
       "works on the installed iPhone PWA" must be in the *not tested* list, never marked verified
5. [ ] **One line on what to look at specifically**

**Any missing item is a QA-definition bug.** Fix `.claude/agents/qa.md` in `fpl-advisor`, mirror
it to `app-factory/assets/agents/qa.md`, and re-run the ticket. Do not edit the PR description.

✅ *Done when* all five are present, or the definition has been fixed and the re-run passes.

### 6.7 — Merge

Do the real morning review first, the way you'll do it every time: tap the preview, poke the
tagline, read the paragraph. Then merge the PR, confirm **the issue closed by itself** (the
`Closes #N` line), and check **https://fpl-advisor-wine.vercel.app** shows the change.

If the issue didn't auto-close, the orchestrator omitted the `Closes` line — that's a prompt bug
to fix in the routine and mirror to `assets/orchestrator-prompt.md`, not something to close by
hand and forget.

✅ *Done when* it's merged, the issue is closed, and production shows the tagline.
**This is the badge — the first thing the factory built and you shipped.**

---

## Day 2, evening → Day 3, morning

### 6.8 — The empty-board cheap-exit test

Make sure **no open issue carries `status:ready`** and let the next scheduled run fire. (Don't
use **Run now** — you're testing the scheduled trigger path.)

In the log, confirm:

- [ ] A one-line "nothing queued" note
- [ ] Immediate termination
- [ ] **The brief and the repo were not loaded first** — this is the actual test. A run that reads
      `CLAUDE.md` and the board and *then* exits has failed 6.8 even though it exited. Look at the
      order of operations, not just the ending.

If it loaded context first, fix the ordering in the orchestrator prompt (routine → pencil icon →
edit the prompt), mirror the change to `assets/orchestrator-prompt.md`, and re-test.

✅ *Done when* the log shows a clean, early exit.

### 6.9 — The Tier-1 block test

File **Ticket B first, then Ticket C** from `assets/smoke-test-tickets.md`, in that order — B must
get the **lower issue number**, because ascending issue number is the only priority mechanism.
Label both `status:ready`. Lint both through the Analyst first, as in 6.2 — B is *supposed* to be
flagged Tier 1 at the lint stage too, and if the evening lint catches it, that's Rule A working.
Queue it anyway; you want to see the run handle it.

Next morning, confirm:

- [ ] **Ticket B carries `status:blocked`**
- [ ] **A comment on B carries the one-line question** — and you got a notification for it. The
      label is machine state; the comment is the part that reaches you. No comment = broken
      mechanism, even if the label is right
- [ ] No account was created, no API key was requested, nothing was stubbed in to work around it
- [ ] **The run continued to Ticket C** and completed it — a draft PR exists for C
- [ ] The run did **not** halt at B

The last two are the whole point: Rule B says Tier 1 blocks the *ticket*, never the *run*.

Then close B and C and delete their branches. Closing is enough — closed beats labelled, so
there's no label to tidy.

✅ *Done when* B is Blocked with its question and C got built anyway.

---

### 6.10 — Fix what the smoke test exposed

Take everything you noted in 6.4–6.9 and, for each item, do one of exactly two things:

1. **Fix the agent definition** in `fpl-advisor` (`.claude/agents/*.md`, or the routine prompt),
   mirror it to `app-factory/assets/`, and re-run the affected ticket to prove the fix; or
2. **Write it into `decisions.md` as accepted**, with the *because* — a known, deliberate
   limitation you're choosing to live with.

Nothing goes on a mental list. If it isn't fixed-and-retested or written down, it will resurface
at 3am during Phase 7 and you won't remember it was a known issue.

Bump any file you change to **v0.3** in its version line. Phase 8 still rewrites all of them from
evidence — this is repair, not the rewrite.

✅ *Done when* every observation is in one of those two buckets.

---

## Then stop

**Do not start Phase 7.** Write `HANDOFF-phase-7.md` in the same structure as
`HANDOFF-phase-5-to-6.md`: what Phase 5/6 actually produced, what the probe found about the board,
which definitions were changed and why, what turned out harder than estimated, and every decision
that departed from the design doc.

Set Setup-sheet statuses 6.1–6.10 to `Done` as you go, and update the **Current state** line at the
bottom of `app-factory/CLAUDE.md`.
