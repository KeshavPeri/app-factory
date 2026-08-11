# Handoff — App Factory build session #2 (Phase 4 only)

**For:** a fresh Cowork chat, run on Claude Fable 5 (deliberately — see §5)
**From:** the Phases 0–3 build session, 9 August 2026
**Owner:** Keshav (Singapore)
**Scope of this session:** Phase 4 only — the agent and skill definitions. **Stop when Phase 4
is done.** Do not configure the routine (Phase 5) or run the smoke test (Phase 6) — write a
fresh handoff note for those instead, in the same style as this document, once Phase 4 is
verified complete.

---

## 1. What actually got built in Phases 0–3

All 37 Setup-track tasks are marked Done in `app-factory-workplan-v2.xlsx`.

**Factory repo** — `github.com/KeshavPeri/app-factory` (private):
- `app-factory-system-design-v2.md`, workplan, this handoff, `routines-verification.md`,
  `deltas.md`, `environment-baseline.md`
- `assets/` — all four v0.1 assets, each headed `v0.1 — provisional, revised at Phase 8`:
  `product-brief-template.md`, `ticket-template.md`, `design-reference.md`,
  `agents/analyst.md`, `agents/builder.md`, `agents/qa.md`, `orchestrator-prompt.md`
  **— these four agent/prompt files are the actual material this session reviews, rewrites,
  and refines. They are drafts, not finished work.**

**App repo** — `github.com/KeshavPeri/fpl-advisor` (private):
- README, `CLAUDE.md` (stub only — this session writes the real one, task 4.5), `decisions.md`
  (HIGH-IMPACT / ROUTINE sections, several real entries already logged from Phase 3 work)
- `.github/ISSUE_TEMPLATE/ticket.md`, live and selectable in the New Issue picker
- GitHub Project board "FPL Advisor Pipeline," linked to the repo, five columns: Ready, In
  Progress, For Review, Done, Blocked
- PWA scaffold: Vite + React + TypeScript + `vite-plugin-pwa`, builds clean, installs to iPhone
  home screen and opens standalone
- Vercel: connected, auto-deploys `main` to production
  (`https://fpl-advisor-wine.vercel.app`), verified PR preview URLs work
- Supabase: project created (Asia-Pacific region, Data API on, auto-expose-new-tables off,
  automatic RLS on), keys wired into Vercel env vars — **note the key name is
  `VITE_SUPABASE_PUBLISHABLE_KEY`, not `VITE_SUPABASE_ANON_KEY`, per §3 below.** Live
  connectivity verified in the deployed app (no key committed to the repo).
- Design skills installed: `impeccable` (v4.0.4) and the `emilkowalski/skills` collection
  (`emil-design-eng` + 8 siblings), both under `.claude/skills/`. No Taste Skill variant
  present. Design hook left **off** for both, per §5.4 of the system design — heavy design
  tooling stays confined to future polish tickets, not every edit. `PRODUCT.md` and
  `DESIGN.md` exist, both explicitly seeded/provisional (no real feature built yet).

## 2. Routines deltas found in task 0.2 (checked 9 Aug 2026)

No delta that breaks a design assumption. Full detail in `routines-verification.md` and
`deltas.md`. Two things to carry forward:

- The exact daily routine-run cap is **not published in the docs** — it's account-specific,
  visible only on Keshav's own dashboard (`claude.ai/code/routines`). A later phase (5.5) needs
  him to check and record it — not this session's problem, just don't be surprised it's absent.
- One-off scheduled runs don't count against the daily cap.

## 3. Things that turned out harder than the estimate (or just different)

- **Claude Code wasn't actually runnable at session start** — installed previously but orphaned
  by an nvm Node version switch. Fixed with `npm install -g @anthropic-ai/claude-code`.
- **Vercel and Supabase dashboards have both been redesigned recently.** Vercel folded the
  dedicated "Environment Variables" sidebar item into its Environments page. Supabase is
  mid-migration from legacy `anon`/`service_role` JWT keys to new `sb_publishable_...`/
  `sb_secret_...` keys — **if this session's `CLAUDE.md` or any agent definition references
  Supabase key names, use `VITE_SUPABASE_PUBLISHABLE_KEY`, matching what's actually deployed.**
- **The public Vercel subdomain `fpl-advisor.vercel.app` was already taken** by an unrelated
  third party. Production URL is `fpl-advisor-wine.vercel.app` — Vercel's auto-generated
  fallback, not a mistake, just not the "clean" URL.
- **Impeccable's installer initially installed for the wrong provider** (GitHub Copilot instead
  of Claude Code) and left duplicate files under `.github/skills/`; this has since been cleaned
  up. `.claude/skills/impeccable` is the one real install.
- **PWA home-screen caching**: the installed icon doesn't always show the newest deployment on
  reopen. Expected service-worker behaviour, not a bug — irrelevant to this session but worth
  knowing if screenshots come up during dry-runs.

## 4. Decisions that departed from the design/workplan docs

None structural. All departures were execution-level, driven by the platform changes in §3 —
nothing that required reopening a design decision from `app-factory-system-design-v2.md`. All
logged inline in `fpl-advisor/decisions.md` as they happened, per §4.6's "log at decision time"
rule — read that file before starting, several real entries already exist there.

## 5. What this session does — Phase 4 only

Per `app-factory-system-design-v2.md` §10 and workplan tasks 4.1–4.7. This phase writes the
agent and skill definitions that every future ticket, every future app, runs through — treat
the four v0.1 drafts in `app-factory/assets/` as a first pass to be genuinely reviewed and
improved, not just copy-pasted into place. That's why this session is deliberately running on
**Claude Fable 5** rather than Sonnet: the v0.1 drafts already exist (written in Phase 2 by
Sonnet 5), so the job here is critical review, rewriting, and hardening of the highest-leverage
prompts in the system — not first-draft generation.

**Task 4.1** — Create `.claude/agents/` in the `fpl-advisor` repo.

**Task 4.2** — Commit the Analyst definition to `.claude/agents/analyst.md`. Done means the
escalation tiers in it match system design §4.5 **word for word**. Review the v0.1 draft in
`app-factory/assets/agents/analyst.md` critically — don't just copy it in.

**Task 4.3** — Commit the Builder definition to `.claude/agents/builder.md`. Done means it names
the `claude/ticket-<n>-<slug>` branch convention and the baseline-design-only rule (§5.4:
normal tickets use `frontend-design` + `design-reference.md` only; Impeccable/emil-design-eng
confined to polish tickets).

**Task 4.4** — Commit the QA definition to `.claude/agents/qa.md`. Done means its PR-packet
section lists all five items from §4.8, in order, preview URL first.

**Task 4.5** — Write the **full** `CLAUDE.md` for `fpl-advisor` (replacing the current stub).
Done means it states: the branch convention, the five board column names, where `decisions.md`
lives, and the design-pass rule. This is the file every fresh routine session reads first for
context — it needs to be complete and unambiguous, since no run can ask a human mid-session.

**Task 4.6** — Extract a shared `escalation.md` (all three tiers plus Rules A and B, verbatim
from §4.5) and have all three agent files reference it rather than each repeating the tiers
inline. One copy, referenced — not three copies that can drift apart.

**Task 4.7** — Dry-run each of Analyst, Builder, and QA once interactively inside Claude Code
and confirm each produces sane output. Log the results in `decisions.md`. This is explicitly
meant to catch a broken definition now, cheaply, rather than at 3am during a real run.

**When done:** update `app-factory-workplan-v2.xlsx` (Setup sheet, tasks 4.1–4.7) to Done, then
write a new handoff note — `HANDOFF-phase-5-to-6.md` in the app-factory repo — covering what
Phase 4 actually produced, anything that departed from this brief, and what Phase 5/6 needs to
know. Follow the structure of this document as the template.

**Do not, in this session:** configure the routine (Phase 5), run any smoke test (Phase 6), or
start writing FPL app features (Phase 7). Re-verify anything platform-specific (Vercel/Supabase/
Claude Code Routines UI) at the time of this session rather than trusting §3's screenshots — as
that section shows, these products moved underneath us mid-session already once.
