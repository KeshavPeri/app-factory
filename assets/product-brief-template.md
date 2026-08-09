v0.1 — provisional, revised at Phase 8

# Product brief — <app name>

This is the document the Analyst holds for every ticket on this app. Order of operations for
any question the Analyst hits: **check whether this brief already answers it before reasoning
or researching.** A silent brief is what pushes decisions onto the Builder at 3am.

## 1. One-liner

<One sentence: what this app does and who it's for. It's for Keshav, personal use, unless
stated otherwise.>

## 2. Core features (v1 scope)

<Bulleted list of what the first working version must do. Keep it small — this is scope, not
a wishlist.>

## 3. Out of scope (for now)

<What you're deliberately not building yet, so the Analyst doesn't accidentally scope-creep a
ticket into it.>

## 4. In-game currency declaration — Tier 3

Per the escalation tiers (§4.5 of the system design), **real money** is Tier 1 (stop and wait
for Keshav) but **in-game or in-app representations of money are Tier 3** (decide, proceed,
log normally) — they are display and formatting concerns, not financial ones.

**Filled example (FPL):** this app's budgets, player prices, and "bank" balance are in-game
numbers with no connection to real payment methods. They are Tier 3. Formatting them (currency
symbol, decimal places, colour for over/under budget) is a routine design decision, not an
escalation.

**For this app:** <name the equivalent in-game/points/budget concept here, and declare it
Tier 3 explicitly, even if the answer is "not applicable, no such concept in this app.">

## 5. What personal data this app may store

Tier 1 territory (§4.5) — storing, transmitting, or newly collecting personal information
(including health, body, and location data) stops the ticket and waits for Keshav. State the
answer here so the Analyst never has to guess.

- [ ] **None** — this app stores no personal data about Keshav or anyone else.
- [ ] The following personal data, and why it's needed: <list each field/type and the reason>

<If any box beyond "None" is checked, each data type listed here is understood as pre-approved
by Keshav via this brief — new personal data fields not listed here still hit Tier 1.>

## 6. Chosen external data source — Tier 2, high-impact

Per §4.5, committing to an outside data source is a Tier-2 decision: proceed, but it must be
made deliberately here, in daylight, with a stated reason — not settled by the Analyst mid-run.

**Source chosen:** <name it — e.g. the unofficial FPL API>
**Because:** <one sentence: why this source, what alternative was considered and rejected, what
the graceful-failure plan is if it changes without notice or goes down>

## 7. Design references

Rough references live in `design-reference.md`. State here if this app needs anything
different from the shared factory defaults (e.g. a lighter/denser register).

## 8. Open questions

<Anything the brief doesn't yet answer. An empty list here is a green flag, not a formality to
skip — if it's genuinely empty, write "None — brief is current" so the Analyst knows it was
checked, not forgotten.>
