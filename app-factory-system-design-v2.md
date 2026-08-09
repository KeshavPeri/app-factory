# Autonomous App Factory — System Design & Handoff (v2, post-Fable review)

**Owner:** Keshav (Singapore)
**Date:** 9 August 2026
**Status:** Reviewed and revised; ready for workplan drafting
**Purpose:** Carry the full design and its reasoning into subsequent sessions (workplan drafting → Cowork build) without losing context or accidentally reversing deliberate decisions.
**Changes from v1:** see §14 Changelog.

---

## 1. The Objective

Build a system where AI agents work overnight, semi-autonomously, to develop personal-use web apps. The owner writes specifications and approves finished work; agents do requirements clarification, building, testing, design polish and review.

**Target experience on run nights:** wake up, open phone, read a short list of what was built and what decisions were made, tap the preview link, merge what's good, write a sentence about what's wrong. Total involvement: ~10–15 minutes per run night.

*(Changed from "daily": Pro quota funds 2–3 run nights a week, not seven — see §6. Nightly is a Later upgrade, earned by observed headroom, not assumed.)*

---

## 2. Hard Constraints

Non-negotiable. Any proposed change must respect these.

| Constraint | Detail |
|---|---|
| **Budget** | Claude **Pro** subscription only. No Anthropic API billing. 100 SGD of free credits exist but are **not** to be spent on an API-based workflow. |
| **Skill level** | Beginner-to-intermediate coder. Not a professional developer. **Not currently comfortable in the CLI.** Completed Anthropic's Claude 101, Prompt Engineering, AI Limitations/Capabilities, Claude Code 101, Claude Code in Action. CLI steps are acceptable only inside the guided Cowork session (§13), with every command spelled out. |
| **Quota** | Pro's usage allowance is shared across Claude chat, Claude Code and Cowork — including the morning review itself. This is the binding constraint on the whole system — not tooling. |
| **Devices** | Apps must work on iPhone and Mac laptop. |
| **Existing environment** | Mac, VS Code, Claude Code installed, GitHub CLI authenticated. Prior project (Job Sniper) used GitHub Actions + Supabase + Vercel — that stack is familiar. |
| **Resilience** | **Crash-tolerance, not resume.** Routines cannot resume a dead run; each run is a fresh, isolated session. Resilience is achieved by making every run stateless and the board the single source of truth: any run must be able to die at any point and leave a state the next run can recover from. See §4.4 step 2a. |
| **Design quality** | Apps must not look like generic AI-generated output. See §5. |
| **Security** | Not a concern for these personal-use apps. Broad agent autonomy is acceptable. Exception carved out in v2: the owner's **live data** is protected by Tier 1 (§4.5) even though app security in general is not a goal. |

---

## 3. Project Backlog

| Order | App | Nature | Notes |
|---|---|---|---|
| **1st** | **FPL advisory / management app** | Personal | Confirmed first build. Needs an external data feed — see risk note below. |
| 2nd | Personalised fitness planner | Personal | Gym + running + yoga. Needs careful data modelling. Note: workout/body data counts as personal data under Tier 1 — the product brief must state up front what may be stored. |
| 3rd | Star-sky ceiling projection | Personal | **Deferred** — hardware side still being figured out. |
| Later | **Inflo** | **Business** | Do **not** run through this pipeline until it has proven itself on personal apps. |

**Note on FPL as first build:** it was not the simplest option, so expect the pipeline shakedown and the data-source work to overlap. Three specific consequences:

1. Choosing the FPL data source is a **Tier-2 high-impact decision** under §4.5 — decide it deliberately in the product brief rather than letting the Analyst settle it at 3am.
2. The commonly used FPL API is unofficial and undocumented. Expect it to change without notice and build in a graceful failure path.
3. **FPL's own vocabulary is full of fake money** — budgets, prices, "bank." The product brief must state explicitly that in-game currency is Tier 3, or the Analyst will block half the backlog (§4.5, money definition).

---

## 4. The System

### 4.1 Where things run

- **Scheduling & execution:** Claude Code **Routines** — scheduled cloud agents on Anthropic-managed infrastructure, set up via `/schedule` (or the routines dashboard at claude.ai/code/routines, which avoids the CLI entirely). Bills against the claude.ai subscription. Minimum interval one hour; per-account daily run cap during research preview. Verified current as of Aug 2026: runs are fully autonomous with **no permission prompts mid-run** (so board-based escalation is the only escalation channel — the design's stop-and-block mechanism is not a preference but a necessity), and pushes are restricted to **`claude/`-prefixed branches** by default.
- **Laptop stays closed.** Local overnight execution was considered and rejected — see §7.
- **Code hosting:** GitHub, one repo per app. Branch convention: `claude/ticket-<number>-<slug>`, matching the Routines default push restriction rather than fighting it.
- **App hosting:** Vercel free tier (draft PRs get preview URLs — load-bearing for phone review, see §4.8).
- **Data:** Supabase free tier where an app needs storage/auth.
- **App format:** PWA. One codebase, installable to iPhone home screen and usable in the laptop browser. No App Store, no Xcode.

### 4.2 The team

| Role | Type | Job |
|---|---|---|
| **Orchestrator** | Not a subagent — this *is* the routine's top-level session | Cheap-exit check (§4.4 step 1a), stale-card recovery, reads the board, picks tickets, dispatches to subagents, moves cards, **appends decisions-log entries as they occur** |
| **Analyst** (BA + PM merged) | Subagent | Holds the product brief. Lints tickets **in an interactive evening session, not inside the routine** (§4.7). Answers or escalates clarifying questions during the run per §4.5. |
| **Builder** | Subagent | Writes the code |
| **QA** | Subagent | Tests the work; bounces it back on failure up to the revision cap. On pass, writes the **PR review packet** (§4.8) — the plain-language summary, decisions, and preview link that the owner reviews from the phone. |

**V1 is three subagents plus the main session.** The Reviewer role from v1 is cut: its function was almost fully duplicated by QA's final pass plus the mandatory human merge gate, at the cost of roughly one-sixth of every ticket's quota. Its one non-duplicated output — the human-readable summary — moves to QA. **Later:** reinstate a distinct Reviewer only if merged work demonstrably ships problems that QA plus the merge gate miss.

Design skills (§5) are layered onto Builder, invoked only in polish tickets (§5.4).

### 4.3 The board

A GitHub project board with four working columns plus Blocked:

**Ready → In progress → For review → Done**, plus **Blocked** for tickets awaiting a human decision.

*(v1 had separate Building / QA / Review columns. Nobody observes the board mid-run — it runs at night — so intermediate states carry no information anyone acts on. Cards are only ever seen between runs, where four states cover everything: queued, died mid-run, PR open, merged. Fewer transitions also means fewer orchestrator actions per ticket.)*

### 4.4 The run loop

1. Routine fires on schedule
   - **1a. Cheap exit:** if **Ready** is empty, the orchestrator posts a one-line "nothing queued" note and terminates immediately. Do not load the brief or repo first.
2. Orchestrator reads the board
   - **2a. Stale-card recovery:** any card in **In progress** at run start belongs to a previous run that died. Rule: if its branch has commits, move the card to **Blocked** with a note ("previous run died mid-ticket; branch `X` has partial work — resume, restart, or discard?"). If the branch has no commits, delete the branch and return the card to **Ready**. Never silently rebuild on top of unknown partial work.
3. Orchestrator picks up to the batch limit (§6) from the top of **Ready**
4. Builder builds on a `claude/` branch; questions go to the Analyst under §4.5. A Tier 1 hit blocks **that ticket only** — the orchestrator moves to the next Ready ticket.
5. QA tests. On failure → back to Builder, **maximum 2 revisions**
6. On exceeding the revision cap → ticket moves to **Blocked**, human gate
7. On pass → QA writes the PR review packet (§4.8); draft pull request opens; card to **For review**. **Merging is always manual.**
8. Throughout: the orchestrator appends decisions-log entries at the moment each decision is made. *(v1 had a separate end-of-run Analyst pass to write the log — a full extra subagent invocation for work the top-level session can do inline for free.)*

### 4.5 The Analyst's escalation rules

Three tiers. This is the safety mechanism of the whole system. Two structural rules first, both new in v2:

**Rule A — the tiers classify *decisions*, not just *questions*.** A Builder that never asks can still make a Tier 1 decision (adding health-data fields "as a sensible default," signing the app up for a service). Therefore: (i) the Analyst's evening lint pass checks each ticket's *scope* for Tier-1-adjacent territory before the run, and (ii) the decisions log classifies what was actually done, whether or not anyone asked.

**Rule B — a Tier 1 stop blocks the ticket, never the run.** The blocked card carries a one-line question the owner can answer from the phone. The orchestrator continues with the next Ready ticket.

**TIER 1 — STOP and wait for the human.** Ticket moves to Blocked.
- **Real money**: money moving to or from any account, payment credentials, paid tiers of any service. *In-game and in-app representations of money (FPL budgets, prices, "bank") are Tier 3 — see §3 note 3.*
- **Personal data**: storing, transmitting, or newly collecting the owner's personal information — including health, body and location data. Displaying a timezone the brief already specifies is Tier 3.
- **Accounts and credentials**: anything requiring a new account, sign-up, API key, secret, or credential — regardless of whether it is free. Creating accounts is an owner-only action.
- **Destructive operations on live data**: any migration or operation that deletes or irreversibly transforms data in the live Supabase instance. (Deleting code, test fixtures, or seed data is Tier 2.)
- Anything otherwise sensitive.

**TIER 2 — Decide, proceed, but flag as HIGH-IMPACT in the decisions log.**
The test question is primary: *"Would this be expensive to reverse after ten more tickets are built on top of it?"* The list below gives examples of it, not a substitute for it:
- How data is structured
- Deleting code, test data, or seed data
- Committing to an outside service that creates a dependency (where no new credential is needed — otherwise Tier 1)
- **Framework and major-library choices** (charting library, CSS framework, state management) — these read like "conventions" but fail the test question. *(New in v2 — the v1 examples and test question disagreed here.)*

**TIER 3 — Decide, proceed, log normally.**
Everything else: conventions, layout, formatting, sensible defaults, in-game currency display, locale formatting already specified in the brief.

**Order of operations for any question:** the Analyst must first check whether the product brief already answers it. Only if the brief is silent does it reason or research.

**Calibration warning (from the review's scenario tests):** the failure mode of a too-literal Tier 1 is not just annoyance — it is that repeated false alarms pressure the owner into loosening the wording, and the looseness then leaks into real cases. Definitions above are drawn tightly on purpose. If Tier 1 fires wrongly twice on the same pattern, fix the *brief* (state the answer there) before touching the tier definitions.

### 4.6 The decisions log

A `decisions.md` file in each repo, in two sections:

```
HIGH-IMPACT
#14 — Storing workouts as one record per exercise rather than per session,
      because the brief emphasises tracking progression on individual lifts.

ROUTINE
#14 — Sorting the exercise list alphabetically.
#15 — Showing gameweek deadlines in Singapore time.
```

**Mandatory rule:** every high-impact entry must state *why*, not just *what*. "Chose X" is useless at 8am. "Chose X **because** the brief says Y" lets the owner spot a misread brief in three seconds.

**Health signal:** if the high-impact section regularly runs past ~5 items a night, the Analyst has become loose about what counts as high-impact and its rules need tightening.

Entries are appended by the orchestrator at decision time (§4.4 step 8), not compiled afterwards.

### 4.7 Ticket linting

Before any run, the Analyst reads queued tickets and flags what is ambiguous — while the owner is still awake to clarify. This addresses the system's real bottleneck: vague specifications, not model capability.

**Explicitly not part of the routine.** Linting runs in a short interactive session (chat or Claude Code) in the evening, when the owner queues tickets. Putting it inside the routine would add an Analyst pass per ticket per run and remove the whole point — that the owner is awake to answer. In v2 the lint pass also performs the Tier-1 scope check from §4.5 Rule A.

Adopted from Eric Tech's methodology (§8). Highest-value single component.

### 4.8 The PR review packet — what makes phone review real

*(New section. The v1 design routed the entire safety model through the owner reading things on a phone at 8am, but never specified what would be read. Reading raw diffs on GitHub mobile does not survive contact with week three; the realistic decay path is rubber-stamping green ticks. The fix is artifact design, not discipline.)*

Every draft PR description must contain, written by QA:

1. **The Vercel preview URL**, first line. The review is *using the app*, not reading the diff.
2. **What changed, in plain language**, 3–6 sentences. No file lists.
3. **High-impact decisions made on this ticket**, inlined from the decisions log, each with its *because*.
4. **What QA tested and what it did not.**
5. **Anything the owner should look at specifically** — one line.

The morning review is then: read one paragraph, tap the preview, poke the feature, merge or write a sentence. If a PR description is missing any of the five items, that is a QA-definition bug — fix the agent definition, not the process.

---

## 5. The Design Layer

**Requirement:** apps must not look like generic AI output.

### 5.1 The landscape (verified 9 Aug 2026)

| Skill | What it is | Verdict |
|---|---|---|
| **Anthropic `frontend-design`** | Ships with Claude Code. Foundational layout/typography/colour rules. | The floor, not the ceiling. Already present. Runs on every build ticket by default. |
| **Impeccable** (Paul Bakaus) | v1.5.1 (17 Mar 2026), actively maintained. 23 commands, 7 reference pillars, 59 deterministic anti-pattern detector rules, `/impeccable init` setup writing PRODUCT.md/DESIGN.md, brand and **product** modes. | **Confirmed primary.** |
| **Taste Skill** (Leonxlnx) | *Changed since v1:* now a 13-skill collection with a v2 flagship. The flagship remains scoped to landing pages, portfolios and redesigns — but the repo now includes product-UI variants, notably `stitch-design-taste` (editorial product UI, Notion/Linear register, restrained palette). | Still not installed — see §5.2 for the updated reasoning. `stitch-design-taste` is the named **Later** fallback. |
| **emil-design-eng** (Emil Kowalski, official repo `github.com/emilkowalski/skills`) | Confirmed active (updated late Jul 2026). Sub-skills now include `animate`, `review-animations`, `improve-animations`, `find-animation-opportunities`, `animation-vocabulary`, `apple-design`, `pick-ui-library`. | **Confirmed secondary.** Motion polish after a UI exists. Beware third-party imitations under similar names — official repo only. |
| **UI/UX Pro Max** | Searchable design database the agent queries before designing. | Returns text recommendations the model executes blind. Skip. |

### 5.2 Recommendation

**Install two, not three.** (Unchanged conclusion, updated reasoning.)

1. **Impeccable** as the primary design layer. The v1 reasoning ("Taste Skill is landing-page-scoped") is no longer the whole truth — Taste Skill now has product-UI variants. The decision now rests on the stronger ground: **pick exactly one opinionated rulebook**, and Impeccable wins it for product UI on (a) a dedicated product mode, (b) deterministic detector rules that catch anti-patterns mechanically rather than by vibe, and (c) an init flow that encodes the app's audience and register into files the agents re-read each session — which matters more here than usual, because every routine run starts from zero context.
2. **emil-design-eng** as a motion polish pass after a UI exists. Complementary, not competing — it is a decision framework (when to animate, which curve), not a second aesthetic rulebook.

**Do not stack Impeccable and any Taste Skill variant together.** Two opinionated rulebooks means two competing sets of design instructions in context. **Later:** if Impeccable's product-mode output disappoints across app #1, swap it for `stitch-design-taste` — swap, never add.

### 5.3 The limitation nobody mentions up front

A design skill is a set of heuristics, not a source of taste. It moves the model off the exact centre of the distribution, but it supplies no picture of what *your* app should look like.

**The actual fix is reference grounding:** a `design-reference.md` per app — 3–5 screenshots or links, with a line each on what specifically to take from them (this one's typography, that one's density, this one's colour restraint). Reusable asset, drafted rough in Phase 2, made good in Phase 8 (§10).

Skills plus reference grounding works. Skills alone gets you generic-but-slightly-better.

### 5.4 Quota discipline

Design passes cost real tokens. **Do not run a design pass on every ticket.** Make "polish pass" its own ticket type, run at feature milestones. Concretely, in v2: normal build tickets run on the baseline `frontend-design` skill plus the design-reference file only; **Impeccable commands and emil-design-eng are invoked exclusively inside polish tickets.** Installed skills that load reference files into context on every pass are a per-ticket tax — confine the heavy ones to the tickets that use them.

### 5.5 Before installing

Read any third-party `SKILL.md` before installing it. These are prompt files that go into the agent's working context — worth thirty seconds of reading.

---

## 6. Pro-Tier Calibration

The source methodology demos at Max-tier throughput. Starting settings for Pro, revised downward from v1:

- **2–3 runs per week, not nightly.** *(Changed.)* One ticket through Analyst-answer → Build → QA → 2 possible revisions is six-plus full agent passes; two tickets a night, nightly, competes with daytime chat/Cowork use and the morning review from the same pool. Nightly is a Later upgrade, adopted only after two weeks of observed headroom.
- **Batch, don't fragment:** two tickets in one run beats one ticket in two runs. Every fresh session pays a fixed overhead re-reading the board, brief and repo; halve the number of runs, not the batch size.
- **2 tickets per run**, not a full column.
- **Revision cap of 2**, not 3.
- **One app at a time.**
- Design passes as separate polish tickets (§5.4), not per-ticket.
- Raise any of these only after observing that limits aren't being hit.

Cost controls now built into the design rather than hoped for: cheap-exit on empty board (§4.4 1a), Reviewer role cut (§4.2), linting kept out of the routine (§4.7), decisions log written inline by the orchestrator (§4.4 step 8), heavy design skills confined to polish tickets (§5.4), Tier 1 blocking tickets not runs (§4.5 Rule B).

---

## 7. Decisions Deliberately Made — Do Not Reverse Without Reading This

Fresh sessions will helpfully suggest these. Each was considered and rejected for reasons.

| Rejected | Why |
|---|---|
| **Agent Teams** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) | Experimental and token-hungry. A 3-teammate team processes roughly 3–4× the tokens of a single session on the same task. Wrong economics on Pro. Use subagents instead. Revisit only on Max. |
| **A separate PM agent, distinct from the BA** | In a one-person app factory these are the same job. Every extra role costs context-loading quota. Merged into the Analyst. |
| **A separate Reviewer subagent** | *(New in v2.)* Its function was duplicated by QA's final pass plus the mandatory human merge gate; on Pro it cost roughly one-sixth of every ticket for marginal catch-rate. Its one distinct output — the human-readable PR summary — moved to QA (§4.8). Reinstate only if merged work demonstrably ships problems the remaining chain misses. |
| **Telegram dispatch** (used in the source video) | Solves a trigger problem already solved by Routines + the Claude mobile app. Machinery for no gain. |
| **Running the nightly job on the local laptop** | Mac sleeps; macOS scheduling is fiddly; silent failures; needs log plumbing. Everything the agent needs lives in the GitHub repo. Routines is strictly simpler. |
| **A separate orchestrator agent** | The routine's top-level session already is the orchestrator. Nothing to build. |
| **Auto-merging pull requests** | The manual merge gate costs ~10 seconds and is the only thing preventing unreviewed code accumulating. Keep it. In v2 the gate is made real rather than nominal by the PR review packet (§4.8). |
| **Stacking design skills** | Opinionated rulebooks conflict. One opinionated layer plus one motion framework — see §5.2. |
| **Paying for the source creator's gated skill files** | The methodology is fully explained in the free video. Claude Code can generate equivalent skill files from a plain description. |
| **Linting inside the routine** | *(New in v2, promoted from implicit.)* Adds an Analyst pass per ticket per run and defeats the purpose — the owner must be awake to answer. Evening interactive session only. |

### Also deliberately settled

- **GitHub Pages vs Vercel:** Vercel chosen — (a) static-only hosting has nowhere to hide secret keys; (b) per-PR preview URLs are what make phone-based review actually work (§4.8). Switching hosts later is ~3 clicks, so not lock-in.
- **Escalation scope:** an earlier draft stopped for "anything about what the app is for" — rejected as too fuzzy. Replaced with the three-tier model, tightened again in v2 after scenario testing (§4.5).
- **Build order:** star-ceiling was originally recommended first (simplest). Owner chose FPL because the star-ceiling hardware isn't resolved. Accepted — see caveats in §3.
- **Board columns:** *(new in v2)* reduced from five working columns to four — intermediate mid-run states carry no information anyone acts on, since the board is only observed between runs.

---

## 8. Source Methodology

**Eric Tech — "How I Make Claude Code Build Apps Autonomously"** (22 May 2026, 20:53)
https://www.youtube.com/watch?v=nX_bGyIOFM4

Adopted: the board as a state machine, ticket linting before dispatch, capped revision loops, explicit human gates for blocked tickets.
Not adopted: Telegram dispatch, the gated skill-file download, Max-tier throughput assumptions.

Caveat: a small-channel video, under a thousand views. Clearly battle-tested by its author, but one person's rig — not an established standard. Adapt, don't copy reverently.

**Other references:**
- "How to Properly Use Claude Code Agent Teams" — https://www.youtube.com/watch?v=uvs1Igr4u6g
- Owain Lewis, "Agent Loops: Complete Guide" — https://www.youtube.com/watch?v=RVEaDvh6f5A
- Impeccable docs — impeccable.style
- Emil Kowalski skills — https://github.com/emilkowalski/skills and emilkowal.ski/skill
- Taste Skill (for the Later fallback only) — https://github.com/Leonxlnx/taste-skill

---

## 9. Known Risks

1. **Billing change risk.** Anthropic announced in May 2026 that programmatic usage would move to a separate credit pool at API rates; paused 15 June 2026, never took effect. Routines bill against the subscription. If reinstated, the local/scripted path is the exposed one — a further argument for the cloud Routines design. Design so a reversal costs a config change, not a rewrite.
2. **Accidental API billing.** If `ANTHROPIC_API_KEY` is set anywhere in the shell environment, Claude Code silently bills the API instead of the subscription. **Check `/status` before starting and confirm it reports the Pro plan.**
3. **Spec quality is the real bottleneck.** Bad runs will almost always trace to ambiguous tickets, not agent failure.
4. **Invisible assumptions.** Mitigated by the decisions log — and in v2 by §4.5 Rule A, which classifies decisions rather than only questions. If the log stops being read, this risk returns in full.
5. **FPL data source instability.** Unofficial API; expect breakage; build the graceful failure path early.
6. **Design drift.** Skills alone don't produce distinctiveness. Without reference grounding (§5.3) the apps will still look samey.
7. **Review decay.** *(New.)* The realistic week-three failure is rubber-stamping. Mitigated by the PR review packet (§4.8); monitored by a simple tell — if you can't answer "what did I merge yesterday?" the gate has already failed.
8. **Zombie cards.** *(New.)* A run dying mid-ticket strands a card and a partial branch. Mitigated by the stale-card recovery rule (§4.4 2a).
9. **Research-preview instability.** *(New.)* Routines is still a research preview: run caps, trigger behavior, and the `claude/` branch restriction can change. Re-verify the Routines docs at build time, not from this document.

---

## 10. Build Sequence

The reusable playbook and assets are **phases inside the single workplan**, not a parallel document.

**Reviewed question — draft provisional v0.1 assets before the first build, or after?** Verdict: **before, but strictly trimmed.** The alternative (build first, extract assets after) would run the first build with no product brief or ticket template — directly contradicting risk #3, spec quality as the real bottleneck. The genuine danger in the v1 plan was scope: polishing seven theoretical templates in chat is a quota-and-time burn producing documents that Phase 8 will rewrite anyway. So Phase 2 drafts **only the four assets the first run cannot start without**, timeboxed to one session, explicitly rough. Everything else waits for Phase 8, where it can be written from evidence instead of theory.

| Phase | What happens |
|---|---|
| **0** | Fable review of this document — **done; this is the output** |
| **1** | Environment check — `/status` confirms Pro plan, no stray API key |
| **2** | Draft **provisional v0.1 assets — trimmed to four** (see §12): product brief, ticket template, agent definitions, rough design-reference.md. One session, timeboxed. Explicitly expected to be wrong in places. |
| **3** | Infrastructure setup — repo, project board (four columns + Blocked), Vercel, Supabase, design skills installed |
| **4** | Write the agent/skill definitions (three subagents + orchestrator routine prompt, per §4.2) |
| **5** | Configure the routine — dashboard at claude.ai/code/routines (no CLI needed) or `/schedule` in the Cowork session |
| **6** | **Smoke test** — one throwaway ticket end to end. In v2 the smoke test must also exercise the failure path: kill nothing, but verify the cheap-exit (run once with an empty Ready column) and confirm a Tier 1 test ticket lands in Blocked without halting the run. |
| **7** | **Build app #1 (FPL)** using the v0.1 assets, at §6 cadence |
| **8** | **Retrospective and asset revision** — rewrite the four assets from what actually happened, and write the remaining assets (decisions-log conventions, definition-of-done, "starting a new app" checklist, per-project playbook) from evidence |
| **9** | App #2 (fitness planner) using the revised v1.0 assets |

Phase 8 is the point of the whole sequence. The v0.1 assets exist to be used and corrected, not to be right first time.

---

## 11. V1 / Later Ledger

Everything in this document is V1 unless listed here. V1 requires no solo CLI work: the routine can be configured from the web dashboard, the board and PRs live in GitHub's web/mobile UI, and the one-time CLI steps (skill installs, environment check) happen inside the guided Cowork session with commands spelled out.

**Later (each with its trigger):**
- **Nightly cadence** — after two weeks of 2–3 runs/week with no limit collisions
- **Reviewer subagent reinstated** — only if merged work ships problems QA + the merge gate miss
- **`stitch-design-taste` swap** — only if Impeccable product-mode output disappoints across app #1 (swap, never stack)
- **Second app in flight** — after app #1 reaches Done-mostly and cadence headroom is proven
- **GitHub-event-triggered routines** (e.g., run QA on PR events) — a real Routines feature, but machinery V1 doesn't need
- **Agent Teams** — Max tier only
- **Revision cap of 3** — only if good tickets are regularly dying at cap 2

---

## 12. Instructions for the Workplan Session

Produce **one phased workplan** following §10 — not a separate parallel document. Ordered so a working end-to-end loop exists as early as possible. Assumes limited CLI comfort: every command spelled out; prefer the web dashboard where one exists.

Phase 2 deliverables — **four assets only** (provisional v0.1, revised at Phase 8):

- **Product brief template** — the document the Analyst holds. Must include: the Tier-3 declaration for in-game currency (§3 note 3), what personal data (if any) the app may store, and the chosen external data source (§3 note 1).
- **Ticket template** — shaped to pass linting first time; includes a definition-of-done field (folded in from v1's separate template).
- **Rough `design-reference.md`** — 3–5 references with one line each (§5.3). Rough is fine; distinctive is Phase 8's job.
- **Agent definitions** — Analyst, Builder, QA, plus the orchestrator routine prompt. The orchestrator prompt must encode: cheap-exit (§4.4 1a), stale-card recovery (§4.4 2a), Tier-1-blocks-ticket-not-run (§4.5 Rule B), inline decisions-log appending (§4.4 step 8). The QA definition must encode the five-part PR review packet (§4.8).

Phase 8 deliverables (written from evidence, not drafted in Phase 2):

- Revised v1.0 of the four assets above
- **Decisions-log conventions**, **"starting a new app" checklist**, **per-project playbook**

---

## 13. Instructions for the Cowork Session

Execute the workplan phase by phase with the owner following along. Expect to:

- Walk through exact terminal commands rather than assuming familiarity; use web dashboards where they exist (routines dashboard, GitHub, Vercel, Supabase)
- Create the GitHub repo and four-column project board
- Install and verify the two design skills (§5.2), reading each SKILL.md aloud first (§5.5)
- Write the agent/skill files per §12
- Configure Vercel and Supabase
- Set up the routine schedule
- Run the extended smoke test (§10 Phase 6), including the empty-board and Tier-1-block checks
- Support the app #1 build and the Phase 8 retrospective

---

## 14. Changelog (v1 → v2)

**Subtractions**
1. **Reviewer subagent cut** (§4.2, §7). Duplicated QA + the human merge gate at ~1/6th of every ticket's quota. Its PR-summary output moved to QA. Reinstatement trigger defined in §11.
2. **Board reduced from five working columns to four** (§4.3). Mid-run states are never observed; fewer transitions, same glanceability.
3. **End-of-run Analyst decisions-log pass removed** (§4.4). The orchestrator appends entries inline at decision time — same output, one fewer subagent invocation per run.
4. **Phase 2 assets trimmed from seven to four** (§10, §12). Definition-of-done folded into the ticket template; checklist, log conventions and playbook deferred to Phase 8 where they can be written from evidence. Verdict on the reviewed question: draft-before-build stands, but timeboxed and minimal.
5. **UI/UX Pro Max downgraded from "optional" to "skip"** (§5.1).

**Corrections**
6. **"Auto-resume" constraint rewritten as crash-tolerance** (§2, §4.4 2a). Routines cannot resume; fresh session each run. Added the stale-card recovery rule — the largest quiet failure mode in v1 (zombie cards after mid-run quota death) now has an explicit handler.
7. **Cadence cut from nightly to 2–3 runs/week, batched** (§1, §6). Pro-tier arithmetic: 12+ agent passes per 2-ticket night, from the same pool as daytime use. Nightly moved to Later with an observation trigger.
8. **Tier 1 definitions tightened after scenario testing** (§4.5): real-money definition excludes in-game currency (FPL false-alarm scenario); accounts/credentials/API keys made an explicit Tier 1 trigger regardless of cost (API-key-creep scenario); destructive operations split — live data Tier 1, code/test data Tier 2 (live-migration scenario).
9. **Tiers now classify decisions, not just questions** (§4.5 Rule A) — closes the silent-default hole (health-data-by-accretion scenario). Lint pass gains a Tier-1 scope check.
10. **Tier 1 blocks the ticket, not the run** (§4.5 Rule B) — v1 wording was ambiguous; the wrong reading wastes a whole run on one blocked card.
11. **Tier 2 test question made primary over its examples**, and framework/major-library choices added as a named Tier 2 example (§4.5) — the v1 bullets and test question disagreed.
12. **§5 verified against current information** (9 Aug 2026): Impeccable v1.5.1 confirmed current and still primary; emil-design-eng confirmed active with an expanded sub-skill list; **Taste Skill's landscape changed** — now a 13-skill collection including product-UI variants, so the v1 rejection reasoning ("landing-page scope") was updated to the stronger one-opinionated-rulebook argument, with `stitch-design-taste` named as the Later fallback.
13. **Routines behavior verified and folded in** (§4.1): no mid-run permission prompts (board-based escalation is the only channel — confirming the design by necessity); default `claude/` branch-prefix push restriction adopted as the branch convention.

**Additions (each justified against quota)**
14. **Cheap-exit on empty board** (§4.4 1a). Saves the fixed per-run overhead of loading board+brief+repo when nothing is queued; costs one line of prompt.
15. **PR review packet** (§4.8). Costs nothing extra — it replaces the cut Reviewer's pass with a cheaper QA output — and is the difference between a real merge gate and rubber-stamping (new risk #7).
16. **Heavy design skills confined to polish tickets** (§5.4, made concrete). Impeccable's reference files are a per-pass context tax; normal build tickets run on baseline + design-reference only.
17. **Linting explicitly excluded from the routine** (§4.7, §7) — was implicit in v1; made a settled decision so future sessions don't "helpfully" automate it.
18. **Smoke test extended to exercise failure paths** (§10 Phase 6): empty-board exit and Tier-1 block, verified before real work. Costs one extra tiny run.
19. **New risks logged** (§9): review decay, zombie cards, research-preview instability.
20. **V1/Later ledger added** (§11) with explicit triggers for each Later item, replacing scattered "revisit later" notes.
