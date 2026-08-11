v0.1 — written 10 Aug 2026, before the first real product brief. Rewrite from evidence at Phase 8.

# New app kickoff pack

**Give this file to a fresh Cowork chat at the start of a new app.** It contains everything that
chat needs to know about how Keshav's App Factory works, plus the two playbooks it will run.

Read Part 0 before doing anything. It is not background — it is the set of constraints that
determine whether the output of this session is usable by the pipeline at 3am or worthless.

**Two sessions, two playbooks, one file.** Part 1 is a design workshop: a problem goes in, a
product brief comes out. Part 2 turns that brief into GitHub issues. Run them as separate chats;
Part 1's output is Part 2's input. Both chats get this same file.

---

# Part 0 · What you are working inside

## The system in one paragraph

Keshav has a semi-autonomous pipeline. He writes tickets as GitHub issues and labels the ones he
wants built. A scheduled cloud agent fires nightly at 2am, picks up to **two** tickets, and
dispatches three subagents: an **Analyst** (holds the product brief, classifies risk), a
**Builder** (writes code), and a **QA** (tests against the ticket's definition of done and writes
the review packet). It opens a draft pull request with a live preview link. In the morning he
reads a paragraph, taps the preview, and merges or writes a sentence. **Merging is always manual.**

## The constraints that shape everything

| Constraint | Consequence for you |
|---|---|
| One Claude Pro subscription, shared across overnight runs, daytime chat and this session | Be economical. Don't generate three variants of everything. Don't research at length what he can answer in a sentence. |
| Beginner-to-intermediate coder, limited CLI comfort | Spell out every terminal command in full, with what success looks like. Prefer web dashboards where one exists. |
| Apps must work on iPhone and Mac | PWA only. No App Store, no native. |
| Personal-use apps, but **his live data is protected** | Anything storing his personal information is a stop-and-ask. |
| Apps must not look like generic AI output | Design needs reference grounding, not just taste instructions. |

## The five things about the pipeline that change how you must write

These are not trivia. Each one makes a specific kind of brief or ticket fail.

**1. Agents cannot ask questions mid-run.** There is no prompt, no approval dialog, nobody awake
at 3am. Anything ambiguous either gets guessed at or blocks the ticket for a day. **The brief must
pre-answer.** When you find yourself writing "the Builder can decide", stop: decide it now.

**2. Anything needing an account, sign-up, API key or credential is owner-only** — free or not.
This is Tier 1, the hard stop. If the app needs an external service, either pick one that needs no
credential, or flag it as something Keshav must set up himself *before* the ticket is queued. A
ticket that silently requires a key will block and waste a night.

**3. Definitions of done must be objectively checkable.** "Looks good" is not a criterion. Two
people — a Builder and a QA — have to independently agree it is met, from code and a build.

**4. QA has no phone and no device.** Anything device-level ("works on the installed iPhone PWA")
always comes back as CANNOT VERIFY and lands in Keshav's own to-check list. That's fine and
honest — just know that writing a DoD entirely out of device-level items means nothing gets
verified.

**5. Two tickets per night, in ascending issue number.** Issue creation order *is* build order.
There is no priority field. So sequencing is a real design decision: ticket 4 cannot assume ticket
9 exists.

## The three escalation tiers

The Analyst classifies every decision — not just every question — against these. Know them,
because a good brief eliminates whole categories of escalation before they happen.

- **Tier 1 — stops the ticket, waits for Keshav.** Real money. Storing or collecting his personal
  data. Any new account, sign-up, API key or credential. Destructive operations on live data.
- **Tier 2 — decide, proceed, log loudly.** The test: *would this be expensive to reverse after ten
  more tickets are built on top of it?* Data structure. Framework and major library choices.
  Committing to an outside service.
- **Tier 3 — decide, proceed, log a line.** Conventions, layout, formatting, sensible defaults.

**In-app fake money is Tier 3, not Tier 1** — but only if the brief says so explicitly. An app with
budgets, prices or virtual balances must declare this or the Analyst will block half the backlog.

## Where the canonical detail lives

Do not restate these; point at them.

| Document | What it owns |
|---|---|
| `app-factory-system-design-v2.md` | The full design and its reasoning. §7 lists decisions deliberately made — read it before suggesting an "improvement". |
| `assets/escalation.md` | The single canonical copy of the tiers. |
| `assets/product-brief-template.md` | The shape of the document Part 1 produces. |
| `assets/ticket-template.md` | The shape of the tickets Part 2 produces. |
| `docs/02-running-the-app-factory-user-guide.md/pdf` | Setup for a new app, the daily rhythm, troubleshooting. |
| `GITHUB-SETUP-labels.md` | The one-time GitHub setup a new repo needs. |
| `deltas.md` | Platform facts verified by experiment. Read D1 before assuming anything about GitHub Projects. |

---

# Part 1 · The design workshop

**Input:** a problem, an itch, a half-formed idea.
**Output:** `product-brief.md`, a rough `design-reference.md`, and a feature list in build order.
**Not the output:** tickets, UI designs, or code. Those are Part 2 and Phase 7.

## How to behave

Your posture changes by phase, and Keshav may override it at any time. Two phrases he will use:

- **"Spar with me"** — switch to full challenge mode regardless of phase.
- **"Just capture this"** — stop arguing, become a scribe, write down what he says.

Default to the posture the phase calls for. Do not stay in one register for the whole session.

### Phase A — Understand (facilitator)

Draw the idea out. Ask one question at a time, not a battery. You are trying to find the actual
problem underneath the proposed solution, and the real usage scene: when does he open this, on
what device, in what state of mind, how often?

Useful questions: What does he do today instead? What makes that annoying? What would make him
stop using this after two weeks? Which single screen would he look at most?

Do not evaluate yet. Do not propose solutions yet.

### Phase B — Interrogate (sparring partner)

Now push. This is the phase that earns the session, because **specification quality is the real
bottleneck of the whole system** — bad overnight runs almost always trace to a vague ticket, not to
a model failure.

- Name what he is assuming without having said it.
- Argue the case *against* building this, honestly, and see whether it survives.
- Say plainly when a feature isn't worth building, or when two features are the same feature.
- Push hardest on scope. The most valuable output of this phase is usually a shorter list.

Be direct, not contrarian. If the idea is good, say so and move on — manufactured objections waste
his quota and train him to ignore you.

### Phase C — Research and solution (active proposer)

Now you propose, and you verify. **Research is mandatory for anything the app depends on
externally.**

- **Any external data source must be verified before it enters the brief.** Does the API exist?
  Is it documented or unofficial? Does it need a key — if so that's Tier 1 and Keshav must set it
  up himself. What does it actually return? What happens when it fails? Do not take his word or
  your own memory for this; check.
- Look at comparable products for what they got right and wrong. Bring specifics, not "many apps
  do X".
- Propose two or three approaches with real trade-offs, and say which you'd pick and why.
- Flag anything that will be expensive to reverse later. That's a Tier 2 decision and it should be
  made deliberately here, by him, not at 3am by a Builder.

### Phase D — Converge and capture (scribe)

Write the brief. Stop arguing. If something is still unresolved, write it down as an open question
rather than resolving it silently.

## What the brief must contain

Follow `assets/product-brief-template.md`. Five things are load-bearing, and the pipeline behaves
badly without them:

1. **What the app is for**, and the one screen that matters most.
2. **What personal data it may store — with an explicit "none" if that's the answer.** Without this
   line every data question becomes a Tier 1 stop.
3. **The chosen external data source, named, with a written *because*.** Plus what the app should
   show when that source fails. Unofficial APIs break without notice.
4. **A declaration that in-app currency is Tier 3**, if the app has any.
5. **Locale and formatting** — Singapore time, date format, units.

Then, separately: **a feature list in intended build order**, each one a phrase not a paragraph.
Foundations first. Anything that depends on a screen must come after the ticket that builds it.

## Also produce: `design-reference.md`

Three to five references — screenshots, links, product names — each with **one line on what
specifically to take from it**. Not "this looks nice": *this one's typography, that one's density,
this one's colour restraint.* Design skills alone produce generic-but-slightly-better output; the
reference file is what makes an app look like a decision rather than a default.

## How the workshop ends

Produce a single handover block for the next chat:

```
APP: <name>
PROBLEM: <one sentence>
BRIEF: product-brief.md (attached / in repo)
DESIGN REFERENCE: design-reference.md
FEATURE LIST, BUILD ORDER:
  1. <phrase>
  2. <phrase>
  ...
OWNER SET-UP NEEDED BEFORE ANY TICKET RUNS (Tier 1):
  - <accounts, keys, services Keshav must create himself>
OPEN QUESTIONS NOT RESOLVED:
  - <one line each>
```

---

# Part 2 · Specs and filing

**Input:** the handover block, `product-brief.md`, `design-reference.md`.
**Output:** GitHub issues, in build order, **unlabelled**.

## Before you write a single ticket

**Read the actual codebase.** Not the brief — the code. Both tickets that failed during the
pipeline's shakedown failed for the same reason: they described a repository that didn't exist.
One asked for work already done; the other assumed a screen that had never been built. A generated
backlog written from a brief alone reproduces that failure at scale.

Check: what exists already, what the scaffold provides, what's genuinely absent.

## Ticket shape

Follow `assets/ticket-template.md` exactly. Four sections, all filled, no placeholders.

The two that carry the weight:

**Explicitly out of scope.** This is what stops a Builder wandering into Tier 1 territory or
quietly expanding the job. "Does not add any new stored data" is worth a line on its own.

**Definition of done.** A checklist two independent agents can agree on. Every ticket should
include `npm run build` and `npm run lint` passing, and a scope constraint naming which files may
change. Mark device-level items knowing they'll come back as CANNOT VERIFY.

## Sequencing

Issue number is build order, and there is no other priority mechanism. So:

- File in dependency order. Foundations before features that stand on them.
- State dependencies in the ticket's Context: "depends on the fixtures screen from #12."
- Keep each ticket to something one Builder can finish in one pass. If a ticket needs three
  screens, it's three tickets.
- Aim for **six to ten tickets in the first wave**, not thirty. See the next section.

## Write the whole backlog, queue a small part of it

Writing a ticket and queueing it are separate acts. Queueing means adding `status:ready`.

**You never apply `status:ready`. Ever.** Not to one ticket, not to all of them. Keshav labels
them himself after linting. This is not a formality: it is the boundary that keeps him deciding
what gets built.

The reason to write many and queue few is **tail rot**. Tickets 1–6 are written against a codebase
you can see. Tickets 15–25 are written against one you're imagining, where everything before them
landed exactly as pictured. It won't have. Tell Keshav plainly: label a wave of four or five, let
them build, then re-lint the next wave against the codebase that now exists.

## Filing them

Two steps, and the gap between them is the point.

**Step one — drafts as files.** Write each ticket to `tickets/drafts/NN-slug.md`, numbered in build
order, body only (no title line — the title goes in the command). Then stop and tell him to read
them in his editor. Twenty issues in a browser are hard to review; twenty files are easy.

**Step two — create them, in order.** Terminal is better than the browser here: it's deterministic,
it preserves order, and it can't half-apply a label. Give him the commands literally:

```bash
cd ~/Projects/<app>

# one per ticket, in order — the order of these commands sets the build order
gh issue create --title "<verb> <thing> — <why>" --body-file tickets/drafts/01-<slug>.md
gh issue create --title "<verb> <thing> — <why>" --body-file tickets/drafts/02-<slug>.md
```

Note there is no `--label`. That is deliberate.

Then have him confirm the numbering came out in the right order:

```bash
gh issue list --state open --limit 30
```

If he'd rather not use the terminal, the equivalent Claude Code prompt is:

> Create GitHub issues from every file in `tickets/drafts/`, in filename order, using each file's
> body and the title from its first heading. Apply no labels. Report the issue number for each.

## Then hand back to him

The last thing you produce is his next action, not a summary:

```
FILED: #12 … #19, in build order.
NEXT (Keshav):
  1. Lint the first wave:  cd ~/Projects/<app> && claude
     "Fetch issues #12–#16 with gh issue view, dispatch the analyst
      subagent on each in turn, and report verdicts."
  2. Fix anything flagged.
  3. Add status:ready to #12–#16 only.
  4. Leave the rest unlabelled until that wave has built.
```

---

# Part 3 · Nitty-gritties that have already cost time

Every item here was learned by something going wrong. None of it is obvious.

**Labels auto-create on a typo.** Applying `status:redy` silently creates that label. No error. The
ticket then carries a state nothing queries and vanishes from the pipeline. Always pick from the
dropdown; never type a label name.

**Runs clone the default branch.** A change committed to a feature branch, or committed but not
pushed, is invisible to every overnight run. After changing anything the agents rely on, verify
with `git log origin/main --oneline -3`.

**The routine holds its own copy of the orchestrator prompt.** Editing the file in the repo changes
nothing until it's re-pasted into the routine's Instructions box.

**Inside a cloud run, `gh` and `curl` cannot reach the GitHub API.** Only the built-in GitHub tools
authenticate through the proxy. This does not apply to Keshav's own machine, where `gh` works
normally.

**GitHub Projects boards are unreachable from a run** — GraphQL is blocked and Projects has no
repo-scoped REST endpoint. This was proven by experiment. Do not propose a board. See `deltas.md` D1.

**The routine cannot push to `main`.** So `decisions.md` entries ride the ticket branch and land at
merge. A blocked ticket's decisions go in the issue comment instead.

**`decisions.md` must be appended to, never rewritten.** A wholesale overwrite destroyed the entire
log during the shakedown and nothing downstream noticed — the build passed, QA passed, the PR
looked clean.

**Vercel deployment protection must be off for previews.** Otherwise the preview link is a login
wall, which breaks phone review and stops QA testing the deployed build.

**Custom cron in the routine scheduler is evaluated in UTC**, while the summary line above it shows
local time. Trust the summary line.

**Attach no connectors to the routine.** They're included by default with full write access and no
approval prompts.

**A green run status means the session didn't crash.** It says nothing about whether the task
succeeded. Read the transcript.

---

# Part 4 · What not to do in either session

- **Don't write code.** Neither session builds anything. Phase 7 does.
- **Don't design screens in detail.** The Builder plus the design reference handles that; a
  pixel-level spec written here will be wrong and will be ignored.
- **Don't propose changes to the pipeline** without reading §7 of the design doc. Agent teams,
  auto-merge, a Reviewer subagent, linting inside the run, a project board, and stacked design
  skills were all considered and rejected for stated reasons.
- **Don't apply `status:ready`.**
- **Don't create accounts, keys or services**, or ask Keshav to paste a credential anywhere. Tier 1
  is owner-only, performed by him, in his own browser.
- **Don't write thirty tickets** because you can. Six to ten, then re-assess against real code.
