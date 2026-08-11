v0.1 — provisional, revised at Phase 8

# App Factory — v0.1 assets

Provisional assets for the Analyst/Builder/QA pipeline. Drafted in Phase 2, explicitly rough,
revised from evidence in Phase 8. Every file in this folder carries a
`v0.1 — provisional, revised at Phase 8` header line (Task 2.12).

## The four assets

1. **`product-brief-template.md`** — the document the Analyst holds for each app. Includes the
   Tier-3 in-game-currency declaration, the personal-data section (with an explicit *none*
   option), and the chosen-external-data-source field (Tier-2, requires a written *because*).
2. **`ticket-template.md`** — shaped to pass linting first time. Includes a definition-of-done
   field and a worked example.
3. **`design-reference.md`** — 3–5 references, each with one line on what specifically to take
   from it. Rough on purpose; distinctive is Phase 8's job.
4. **`agents/`** — the Analyst, Builder and QA subagent definitions, plus the orchestrator
   routine prompt (`orchestrator-prompt.md`). Hardened to v0.2 in Phase 4 and committed to
   `fpl-advisor`; the copies here are byte-identical mirrors of what runs. `escalation.md`
   (the single canonical copy of the §4.5 tiers, extracted at task 4.6) sits alongside them.

## Starting a new app

- **`new-app-kickoff.md`** — the file to hand a fresh Cowork chat when beginning a new app. Part 0
  is a context primer on how the pipeline works and the five properties that change how a brief
  must be written; Part 1 is a design-workshop playbook (problem → `product-brief.md`); Part 2
  turns that brief into GitHub issues and files them. Parts 3 and 4 carry the hard-won gotchas and
  the refusals. Run Parts 1 and 2 as **separate chats**, both given this same file.

## Phase 5/6 working files (throwaway, not part of the four)

- **`routine-probe-prompt.md`** — one-off diagnostic prompt for task 5.6. Answers whether a cloud
  routine can actually read and write the GitHub project board (see `../deltas.md` D1). Delete or
  overwrite once it has run.
- **`smoke-test-tickets.md`** — the three Phase 6 test tickets: the smoke ticket (6.1), the
  deliberate Tier-1 ticket and its harmless companion (6.9).

Neither is revised at Phase 8; both are scaffolding.

## Reference

Full reasoning: `../app-factory-system-design-v2.md`. Section numbers (§4.5, §4.8, etc.) in
each asset point into that document.
