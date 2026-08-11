# GitHub setup for the label pipeline

One-time, all web UI, about ten minutes. Do this before Phase 5 step 8 (pasting the v0.3
orchestrator prompt into the routine). Until the labels exist, the pipeline has nowhere to put
state.

---

## 1. Create the four status labels

**https://github.com/KeshavPeri/fpl-advisor/labels** → **New label**, four times. Name them
**exactly** as below — copy-paste, don't type. The orchestrator matches them character for
character at 3am, and applying a name that doesn't exist silently *creates* it, so a typo invents
a state no query will ever match and the ticket disappears from the pipeline with no error.

| Name | Suggested colour | Description |
|---|---|---|
| `status:ready` | `#0E8A16` green | Linted and queued for the next run |
| `status:in-progress` | `#FBCA04` yellow | Being worked this run |
| `status:for-review` | `#1D76DB` blue | Draft PR open, awaiting your review |
| `status:blocked` | `#D93F0B` red | Awaiting your decision — read the comment |

Colours are for you, not the machine. Reds and yellows read well on a phone at 8am, which is the
only place these get looked at.

**Why create them by hand when applying auto-creates them?** Because auto-created labels come out
grey and undescribed, and because pre-creating means you'll pick the right one from a dropdown
instead of typing a near-miss.

## 2. Install the Claude GitHub App

**https://github.com/apps/claude** → **Install** → **Only select repositories** → `fpl-advisor`.

The probe found `gh` and `curl` returning *"GitHub access is not enabled for this session. An org
admin must connect the Claude GitHub App."* The pipeline works through the built-in GitHub tools
regardless, but installing this is what gives a run access to PR and deployment data — which is
how step 6 of the orchestrator finds the Vercel preview URL. Without it, expect more
"Preview: pending" packets.

## 3. Close the probe's scratch issue

The first probe run created **issue #2, "probe: scratch issue"**. Close it. If it's left open it's
harmless today, but the moment anything labels it, the run treats it as a real ticket.

Check it isn't carrying a leftover `probe-test` label. Delete that label from the repo entirely
while you're on the labels page — it has no role now.

## 4. Decide what to do with the project board

The **"FPL Advisor Pipeline"** board can't be written by a routine, so it will now sit frozen
showing whatever was last on it. Two honest options:

- **Delete or archive it.** Recommended. A board that shows stale state is worse than no board —
  it's the kind of thing you glance at in month two and believe.
- **Keep it as a manual scratchpad** for your own planning, clearly not pipeline state.

Don't leave it as-is and unlabelled. That's the version that misleads you later.

## 5. Bookmark your review views

These replace the board on your phone. Save them in Safari, or star them on GitHub mobile:

```
https://github.com/KeshavPeri/fpl-advisor/issues?q=is:open+label:"status:blocked"
https://github.com/KeshavPeri/fpl-advisor/issues?q=is:open+label:"status:for-review"
https://github.com/KeshavPeri/fpl-advisor/issues?q=is:open+label:"status:ready"
```

The blocked one is the important bookmark — it's your Rule B channel. You'll also get a
notification on every blocked ticket, since the orchestrator posts the question as a comment.

## 6. Push the rewritten definitions

The v0.3 agent definitions, `CLAUDE.md`, `escalation.md` and the issue template have been
rewritten in your local `fpl-advisor` folder but not committed. A routine clones from the
**default branch**, so until these land on `main`, every run reads the old board-based
instructions and fails in confusing ways. This is the step most likely to bite.

In an interactive Claude Code session in `fpl-advisor`, or in your terminal:

```bash
cd ~/Projects/fpl-advisor
git status
git add CLAUDE.md escalation.md .claude/agents/ .github/ISSUE_TEMPLATE/ticket.md decisions.md
git commit -m "Phase 5: replace project board with issue labels as pipeline state (v0.3)"
git push origin main
```

`git status` first, so you see exactly what's changing before you commit it.

---

## What you are NOT setting up, and why

- **No GitHub Actions workflow.** The tempting move is a workflow syncing labels to the board's
  Status field — Actions runs outside the proxy, so GraphQL works there. It needs a classic PAT
  with `project` scope stored as a repo secret, and it adds a second unproven moving part during
  the phase whose entire job is proving the first one works. Revisit after Phase 6 if you miss
  the columns.
- **No priority labels.** Order is ascending issue number. File tickets in the order you want them
  built. Adding a priority scheme now is a rule you'd have to remember at 11pm while queueing.
- **No `status:done` label.** Done is the issue being closed. Every query filters to open issues,
  so closing is sufficient and nothing needs tidying after a merge.
