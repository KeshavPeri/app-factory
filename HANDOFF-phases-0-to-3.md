# Handoff — App Factory build session #1 (Phases 0 → 3)

**For:** a fresh Cowork chat
**From:** the workplan-drafting session, 9 August 2026
**Owner:** Keshav (Singapore)
**Scope of this session:** Phases 0, 1, 2 and 3 only. Stop at the end of Phase 3.

---

## 1. Your job in this session

Walk Keshav through Phases 0–3 of the App Factory workplan, one task at a time, in order.
That is 37 tasks and roughly 17 hours of his time. It will take several sittings — this
chat is expected to span days, not one afternoon.

**You are not building an app.** You are building the factory that builds apps. No
application code gets written in this session beyond a PWA scaffold.

**Stop at the end of Phase 3.** Phases 4–6 belong to a separate chat. Do not start writing
agent definitions into the app repo (Phase 4) even if Phase 2 leaves you feeling ready.

---

## 2. Who you are working with

- Beginner-to-intermediate coder. Not a professional developer.
- **Not comfortable in the CLI.** Every terminal command must be spelled out in full,
  copy-pasteable, with a one-line explanation of what it does and what output means success.
  Prefer a web dashboard whenever one exists (GitHub web UI, Vercel, Supabase,
  claude.ai/code/routines).
- Has completed Anthropic's Claude 101, Prompt Engineering, AI Limitations/Capabilities,
  Claude Code 101, and Claude Code in Action.
- Existing environment: Mac, VS Code, Claude Code installed, GitHub CLI authenticated.
  Prior project (Job Sniper) used GitHub Actions + Supabase + Vercel, so that stack is familiar.

**Ask before assuming.** Where the workplan or the design document is silent on something
Keshav will have to live with, ask him rather than picking for him.

---

## 3. Hard constraints — non-negotiable

| Constraint | Detail |
|---|---|
| **Budget** | Claude **Pro** subscription only. No Anthropic API billing, ever. 100 SGD of free credits exist and are **not** to be spent on an API-based workflow. |
| **Quota** | Pro's allowance is shared across Claude chat, Claude Code, Cowork *and this session*. This is the binding constraint on the whole system — not tooling. Be economical. |
| **Devices** | Apps must work on iPhone and Mac laptop. PWA only — no App Store, no Xcode. |
| **Security** | Not a concern for these personal-use apps, **except** the owner's live data, which is protected by Tier 1 (see §5). |
| **Design quality** | Apps must not look like generic AI output. |
| **Resilience** | Crash-tolerance, not resume. Every routine run is a fresh, stateless session; the board is the single source of truth. |

**Risk to check on day one:** if `ANTHROPIC_API_KEY` is set anywhere in the shell
environment, Claude Code silently bills the API instead of the subscription. Task 1.2
exists for this. Do not skip it.

---

## 4. The system in ten lines

- A **Claude Code Routine** (scheduled cloud agent) fires 2–3 nights a week. Laptop stays closed.
- Its top-level session is the **Orchestrator**. It reads a GitHub project board, picks up to
  2 tickets from **Ready**, and dispatches to three subagents.
- **Analyst** holds the product brief and answers or escalates questions. **Builder** writes
  code on a `claude/ticket-<number>-<slug>` branch. **QA** tests it and writes the PR review packet.
- Board columns: **Ready → In progress → For review → Done**, plus **Blocked**.
- QA failure bounces back to Builder, **maximum 2 revisions**, then the ticket goes to Blocked.
- On pass: a **draft PR** opens with a Vercel preview URL. **Merging is always manual.**
- Keshav reviews from his phone in the morning: read one paragraph, tap the preview, poke the
  feature, merge or write a sentence. Target 10–15 minutes.
- Every decision gets appended to `decisions.md` at the moment it is made, with a *because*.
- **Ticket linting happens in an interactive evening session, never inside the routine.**
- First app is an **FPL advisory app**. Second is a fitness planner. Neither is business-critical.

---

## 5. The escalation tiers — you will need these to write the Phase 2 assets

Three tiers. This is the safety mechanism of the whole system.

**Rule A — the tiers classify *decisions*, not just *questions*.** A Builder that never asks
can still make a Tier 1 decision.
**Rule B — a Tier 1 stop blocks the *ticket*, never the run.** The orchestrator moves to the
next Ready ticket.

**TIER 1 — STOP, move the ticket to Blocked, wait for Keshav.**

- **Real money** moving to or from any account, payment credentials, paid tiers.
  *In-game money (FPL budgets, prices, "bank") is Tier 3.*
- **Personal data** — storing, transmitting or newly collecting his personal information,
  including health, body and location data.
- **Accounts and credentials** — anything needing a new account, sign-up, API key, secret or
  credential, **regardless of whether it is free**. Account creation is owner-only.
- **Destructive operations on live data** — anything deleting or irreversibly transforming
  data in the live Supabase instance. (Deleting code, test fixtures or seed data is Tier 2.)

**TIER 2 — decide, proceed, flag as HIGH-IMPACT in the decisions log.**
Test question: *"Would this be expensive to reverse after ten more tickets are built on top
of it?"* Examples: data structure, deleting code or seed data, committing to an outside
service, **framework and major-library choices**.

**TIER 3 — decide, proceed, log normally.** Conventions, layout, formatting, sensible
defaults, in-game currency display, locale formatting the brief already specifies.

**Order of operations:** the Analyst checks whether the product brief already answers the
question *before* reasoning or researching.

**Calibration warning:** if Tier 1 fires wrongly twice on the same pattern, fix the **brief**
(state the answer there) before touching the tier definitions. Loosening the tiers leaks into
real cases.

---

## 6. Decisions already made — do not reverse without reading this

Fresh sessions helpfully suggest all of these. Each was considered and rejected.

| Rejected | Why |
|---|---|
| **Agent Teams** | Experimental, ~3–4× the tokens. Wrong economics on Pro. Use subagents. Revisit only on Max. |
| **A separate PM agent** | Same job as the BA in a one-person factory. Merged into the Analyst. |
| **A separate Reviewer subagent** | Duplicated QA's final pass plus the human merge gate at ~1/6th of every ticket's quota. Its one distinct output — the human-readable PR summary — moved to QA. **QA itself is retained and is load-bearing.** |
| **Telegram dispatch** | Routines + the Claude mobile app already solve the trigger problem. |
| **Running the nightly job locally** | Mac sleeps; macOS scheduling is fiddly; silent failures. |
| **A separate orchestrator agent** | The routine's top-level session already is the orchestrator. |
| **Auto-merging PRs** | The manual gate costs ~10 seconds and is the only thing preventing unreviewed code accumulating. |
| **Stacking design skills** | Two opinionated rulebooks conflict. One opinionated layer + one motion framework. |
| **Linting inside the routine** | Adds an Analyst pass per ticket per run and defeats the purpose — Keshav must be awake to answer. |
| **GitHub Pages instead of Vercel** | Static-only hosting has nowhere to hide keys, and per-PR preview URLs are what make phone review work. |

Also settled: board has four working columns plus Blocked (not five working columns);
FPL is first even though it is not the simplest, because the star-ceiling hardware isn't resolved.

---

## 7. What Phase 2 must produce — the four v0.1 assets

Timeboxed to roughly one working session. **Explicitly expected to be wrong in places.**
Phase 8 rewrites all four from evidence. Polishing theory here is a quota burn.

1. **Product brief template** — the document the Analyst holds. Must include: the Tier-3
   declaration for in-game currency, a "what personal data this app may store" section with an
   explicit *none* option, and a "chosen external data source" field marked as a Tier-2
   decision requiring a written *because*.
2. **Ticket template** — shaped to pass linting first time. Includes a definition-of-done field.
3. **Rough `design-reference.md`** — 3–5 references with one line each saying what specifically
   to take from that reference (this one's typography, that one's density, this one's colour
   restraint). Rough is fine; distinctive is Phase 8's job.
4. **Agent definitions** — Analyst, Builder, QA, plus the orchestrator routine prompt.
   - The **orchestrator prompt** must encode four behaviours by name: cheap-exit on an empty
     Ready column; stale-card recovery; Tier-1-blocks-ticket-not-run; inline decisions-log
     appending at decision time.
   - The **QA definition** must encode the five-part PR review packet: (1) Vercel preview URL
     on the first line, (2) what changed in plain language in 3–6 sentences, no file lists,
     (3) high-impact decisions with their *because*, (4) what QA tested and what it did not,
     (5) one line on what to look at specifically.

Two behaviours worth encoding in the orchestrator prompt verbatim:

- **Cheap exit:** if Ready is empty, post a one-line "nothing queued" note and terminate
  immediately. Do not load the brief or repo first.
- **Stale-card recovery:** any card in In progress at run start belongs to a run that died.
  If its branch has commits → move to Blocked with a note asking resume/restart/discard.
  If no commits → delete the branch, return the card to Ready. Never silently rebuild on top
  of unknown partial work.

---

## 8. What Phase 3 must produce

GitHub repo for the FPL app, README + CLAUDE.md, `decisions.md` with its two sections, the
project board with its five columns, an issue template, a PWA scaffold that installs to the
iPhone home screen, Vercel connected with a **verified** PR preview URL, Supabase created with
keys in Vercel environment variables (never in the repo), and two design skills installed —
**Impeccable** (primary, run `/impeccable init`) and **emil-design-eng** (motion polish, from
the official repo `github.com/emilkowalski/skills` only; beware imitations).

**Read every third-party `SKILL.md` before installing it.** These are prompt files that enter
the agent's working context. It is worth thirty seconds.

Note for later: heavy design skills are confined to **polish tickets**. Normal build tickets
run on baseline `frontend-design` plus the design-reference file only. Do not wire Impeccable
into every ticket.

---

## 9. How to work through the tasks

The workbook (`app-factory-workplan-v2.xlsx`) is the source of truth for what to do. Use the
**Setup** sheet. Work in Task ID order: 0.1 → 0.2 → 0.3 → 1.1 → … → 3.16.

For each task:

1. Read the task, the **What "done" looks like** column, and the **Notes** column.
2. Do the work with Keshav, spelling out every command.
3. Check the done criterion literally. It is written to be objectively checkable — he should be
   able to point at something and say yes.
4. Set **Status** to `Done` via the dropdown. Everything else on the Dashboard updates itself.

Some rows carry an "Also needs X, Y finished." line at the front of Notes — those are extra
prerequisites beyond the single ID in the Blocked by column.

**Owner-only actions.** Keshav creates every account himself — GitHub, Vercel, Supabase. You
walk him through it; you do not do it for him. This is Tier 1.

**Quota discipline for this session.** This chat spends from the same pool the factory will
run on. Do not generate long exploratory drafts; do not rewrite an asset three times to
polish it; keep Phase 2 inside its timebox. If something is genuinely uncertain, ask Keshav
rather than researching at length.

---

## 10. Do not do these in this session

- Do not write the Operating guide or the System explainer PDF. Those are Phases 10 and 11 and
  can only be written after the first app has been built through the system.
- Do not write the FPL product brief itself. Phase 2 produces the **template**; Phase 7 fills it.
- Do not configure the routine (Phase 5) or run a smoke test (Phase 6).
- Do not install a Taste Skill variant alongside Impeccable. `stitch-design-taste` is a named
  **later** fallback, and it is a swap, never an addition.
- Do not add a Reviewer subagent.
- Do not put any secret or key in the repo.

---

## 11. Session is complete when

All 37 Setup-track tasks from Phases 0 through 3 show `Done`, which means:

- `/status` reports Pro and no stray API key exists in a fresh terminal.
- A factory repo exists with four labelled v0.1 assets in `/assets`.
- An FPL repo exists with a board, an issue template, a PWA that installs on his phone,
  a working Vercel preview URL on a test PR, Supabase wired through environment variables,
  and both design skills installed and verified.
- On the Dashboard, Setup shows 37 of 60 done and three badges are unlocked:
  **First Light**, **Paper Trail**, **Foundations**.

**Then hand off.** Write a short note for the Phase 4–6 chat covering: what actually got built,
any Routines deltas found in task 0.2, anything that turned out harder than the estimate, and
any decision made that departed from this document. Save the updated workbook.

---

## 12. Reference

Full design and reasoning: `app-factory-system-design-v2.md`. Section numbers referenced in
the workbook's Notes column (§4.5, §4.8, §5.4 and so on) point into that document — read it
when a note cites one.
