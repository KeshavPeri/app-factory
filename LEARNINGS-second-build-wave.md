v1.0 — written 21 Aug 2026, the morning before the GW1 deadline, after the value loop closed.
Companion to `LEARNINGS-first-build-wave.md`, which covers waves 1–3. Platform facts proven by
experiment live in `deltas.md`; this file is the wider set of lessons.

# What closing the value loop taught us

Twenty-four more tickets, taking the app from "items 1–9 shipped" to a working chain: real squad in,
a Telegram message carrying a real recommendation out. **36 pull requests total, 15 migrations,
15 background jobs, 7 workflows.** Built in ten days by a beginner-to-intermediate coder reviewing
from a phone.

---

## 1. The system held at three tickets a night

The batch limit went from 2 to 3 on 16 August after four clean multi-ticket runs. Worktree isolation
held; the per-ticket decision files never collided. Two costs came with it and both are real:
**quota**, since three tickets is roughly half again as many subagent dispatches on one
subscription; and **merge-order coupling**, since three branches all fork from the same `main` and
any two touching one file conflict on the second merge regardless of whether the tickets depend on
each other.

The orchestrator prompt now requires both to be surfaced in the end-of-run note. That was the right
fix: the coupling is invisible at queue time unless somebody deliberately compares the scope lists.

**A drift worth knowing about.** `CLAUDE.md` and the routine's saved prompt each hold a copy of the
batch limit, and the routine's copy only changes when the prompt is re-pasted into its Instructions
box. They drifted within a day. The run found the disagreement, followed `CLAUDE.md`, took two
tickets instead of three, and said so in the note. **That is exactly the right behaviour and it is
worth preserving** — the fix was to make `CLAUDE.md` explicitly the binding copy rather than to
remove the duplication.

---

## 2. Every serious bug was found by reading output, not by testing

This is the headline lesson of the wave. Five defects, none caught by a test, all caught by somebody
looking at a number and finding it implausible:

| What was noticed | What it was |
|---|---|
| A job reported exactly **1,000** rows | Supabase silently caps a query at 1,000. Two thirds of the data was missing. |
| A **38-game season** showed players with **54 matches** | 18% of the match data was cup and European games being counted as league form. |
| A clean-sheet rate of **95%** | Clean sheets were being read from a goalkeeper-only column. |
| A projected score of **280** on a card about one gameweek | A five-gameweek total, mislabelled. |
| A projected score of **101** for one gameweek | Two solver runs' rows summed together. |

**Every one of those numbers was printed by a job that reported success.** Each job only checks its
own step. The tests all passed, because the tests asserted the code did what the code did.

Three practices came out of this and all of them earn their keep:

- **Put counters in `job_runs.details`, always.** Rows read, rows written, rows excluded, rows
  skipped, and *why*. The 1,000-row bug was found because a ticket had asked for those counters and
  one of them was a suspiciously round number. Counters are cheap and they are the only thing
  standing between a silent failure and a visible one.
- **Bounds-check any derived rate that has a known real-world limit.** A clean-sheet rate above 60%
  is impossible; a player cannot exceed 38 league matches. The report that got clean sheets wrong
  was internally consistent, carried its sample sizes, listed three honest caveats, and was still
  wrong, because nothing compared a number against reality.
- **Reconcile counts arithmetically.** 12,754 kept + 2,586 excluded = 15,340 exactly. Three clubs
  × 5 gameweeks = 15 fixtures, but 14 reported — because two of those clubs play each other once.
  When the numbers reconcile you have actually verified something; when they nearly reconcile, the
  gap is the finding.

---

## 3. A measuring instrument can be wrong, and it is the most expensive kind of wrong

A calibration report was built specifically to settle a modelling doubt with a number. Its headline
said defenders were under-projected by 45%. **That conclusion was an artefact of a data gap in the
report itself**, and acting on it would have sent three tickets chasing a problem that did not exist.

The sequence is worth recording because it happened twice in opposite directions:

1. A solver output looked wrong — a defender captained four gameweeks out of five.
2. A report was built to measure it. The report said the opposite of the worry.
3. The report was then found to be measuring the wrong thing.
4. A corrected report is still pending.

**The lesson is not "don't measure".** It is that **an instrument needs its own verification**, and
the cheapest form is a sanity bound on every derived figure. The second lesson is that reporting
"not comparable" is a legitimate and valuable output. A report that says "I cannot measure this" is
trustworthy; one that says "0.30, probably" is not.

---

## 4. Fixing the instance is not fixing the class

Waves 1–3 established that FPL element ids are not stable across seasons and that `code` is the
stable key. That finding was applied to **players, and only to players.**

The identical property holds for **teams** — only 5 of 20 team ids referred to the same club across
the season boundary. The bug sat live for days, attaching Chelsea's, Leeds' and Liverpool's ClubElo
ratings to three newly promoted clubs, because the column had no consumer yet and therefore no error
path. `deltas.md` D9.

**Carry-forward:** when a source is per-season or per-any-epoch, enumerate *every* entity it keys,
not just the one that produced a visible bug. And **a column with no consumer is the dangerous
one** — it is wrong until the first consumer is built, and then it is wrong in production.

---

## 5. The scope constraint is the best tool in a ticket and it contradicts itself twice

`LEARNINGS-first-build-wave.md` §8 ranks a scope constraint naming exact file paths as the second
most load-bearing thing in a ticket. That still holds — it is what makes a three-ticket batch safe.

But it produced the same defect twice, in both directions:

- A ticket required an **import** the scope list did not permit the build config for.
- A ticket's **Notes** asked for a file to be updated that the scope list omitted.

The second is the more insidious, because a Notes instruction reads as advisory: a Builder that
follows it violates a hard constraint, and one that respects the constraint silently drops an
instruction the author thought had been given. Neither is visible without diffing the two sections
by hand.

**The fix is procedural: write the scope constraint last.** After the rest of the ticket exists,
read back over it and collect every file it names *or implies* — the decisions log, a doc it asks to
update, a build config an instructed import requires. Writing it early, while the ticket is still a
sketch, is what produces both instances. `deltas.md` D10.

**The counter-lesson matters more.** Both times, the Builder flagged the contradiction rather than
picking a side, the Analyst classified it, and it was logged with a full *because*. **A Builder that
steps outside the lines and says so loudly is the mechanism working.** The thing to fear is the one
that quietly duplicates logic to stay compliant, producing a clean diff and a second copy of a rule
that will drift.

---

## 6. The human steps in the chain are still where things break

`LEARNINGS-first-build-wave.md` §6 named this and it recurred all wave.

- A migration merged and unapplied caused a workflow failure that looked exactly like a code bug.
- **The applied-migrations table in `supabase/README.md` fell four rows behind**, having already
  fallen behind once in the first wave.
- A DELETE-grant migration was applied to live Supabase but the file never reached the repository —
  so the repo's own migration history was incomplete, and the next reader would have had no way to
  know the grant existed.

**Two responses, both adopted.**

First, the daily rhythm is written down and is not "review, merge, done": it is **review → merge →
apply migration → update the applied table → run the job → verify the counters**. Order matters —
running a projection before the ingest that stamps a new column produces nulls everywhere and looks
like the fix broke something.

Second, and more durably: **a preflight check that asserts the whole chain is healthy in one job.**
Ten assertions across the live database — next gameweek, squad shape, projection coverage,
recommendation freshness, solver status, team ratings, match-data integrity, job freshness,
notification state, configuration. One overall verdict, a non-zero exit on failure, and every
verdict carrying the numbers behind it.

Its first run reported 8 pass, 1 warn, 1 fail, two days before the deadline. **The warn was correct
and expected. The fail was a mis-specified assertion.** Both outcomes were useful, and the ten
assertions collectively answered a question no individual job could: *is this actually going to
work on Friday?*

**Carry-forward for every new app:** build the preflight check early, not late. It is the only thing
that catches the class of failure where every component reports success.

---

## 7. Specification defects, this wave's crop

Continuing §2 of the first-wave file. Each of these was a ticket that no correct implementation could
fully satisfy, or that specified the wrong thing:

- **"None of the projection rows may be all-zero."** Impossible: 15% of a Premier League player list
  is injured, suspended or never plays, and an all-zero projection is the correct output for them.
- **"Show the net projected points"** — without saying over what period. The Builder correctly used
  the stored horizon total; the card was about one gameweek. **A specification that omits a unit is
  a specification that will be read wrong.**
- **"The workflow must be demonstrated by an actual run."** Not possible: a `workflow_dispatch`
  workflow cannot be triggered until its file is on the default branch.
- **"Warn when total expected minutes fall below 100."** The code's fallback is 100; the solver's
  *shipped settings* say 300. Reading a default from source rather than from the shipped
  configuration produced a warning calibrated to the wrong number.

**The pattern across all four: the author knew the domain but stated the requirement loosely.** The
antidote is the one already in the first-wave file — if a definition-of-done item states a number,
compute it; if it asserts a third party ships something, check. Extended by this wave: **if it names
a quantity, name its unit**, and **check the shipped configuration, not just the code's fallback.**

---

## 8. What proved load-bearing, updated

The first-wave ranking still holds. Three additions from this wave, in order of how often they
prevented a bad outcome:

1. **Counters in `job_runs.details`.** Now ranked with grep-checkable DoD items. They found the
   1,000-row cap, the competition contamination, the elo gap and the doubled solver rows.
2. **"What a substitute cannot catch."** Every ticket this wave ended with an explicit statement of
   which class of failure its tests were blind to, and which check was therefore a human one. This
   turned "QA passed" into a claim with a known scope.
3. **Pre-answering a decision with its *because* in the ticket body.** Not just the answer — the
   reason. Several times a Builder hit a case the author had not imagined and reasoned correctly
   from the stated *because* rather than from the stated rule.

---

## 9. For the "about the system" document

The framing from the first wave survived contact and is worth restating, with one addition:

> The pipeline does not remove the human. It moves the human from *writing code* to *writing
> specifications and making the decisions that are expensive to reverse* — and it makes those two
> jobs the only ones that matter.

The addition, learned this wave: **it also moves the human to reading output.** Every serious defect
in this wave was found by a person looking at a number and thinking "that can't be right" — a
1,000, a 54, a 95%, a 280, a 101. No test caught any of them, because tests assert that code does
what code does. **The instinct that a number is implausible is the one thing in this system that
cannot be automated**, and it turned out to be the most valuable input the human provided.

---

## 10. Not every ticket is worth a night — added 29 Aug 2026

The overnight pipeline costs two things that are easy to forget: **a night of latency, and one of
three batch slots.** Both are worth paying when the specification is the hard part. Neither is worth
paying when the change is small, the file is one, and the tests already exist.

**The rule that emerged, stated as a test rather than a list:** *is writing the ticket harder than
making the change?* If yes, use the pipeline — that is exactly what it is for, and §9's framing holds
(the human writes specifications, the machine writes code). If no, fix it directly in an interactive
session and keep the slot for work that needs a spec.

**What "small" actually means here**, from the case that produced this note — a solver-log parser
whose cross-check was reading the wrong solution index:

- One module, and a pure one.
- A defect already diagnosed, with the mechanism written down and the evidence attached.
- Fixtures that exist as captured artefacts, not ones that have to be invented.
- A test suite that already covers the surrounding behaviour, so a regression is visible.

**Write the ticket either way.** The ticket is what makes the fix reviewable and what keeps the
decisions log continuous; it is the *dispatch* that is optional, not the specification. An
interactive fix still branches under `claude/`, still writes `decisions/ticket-<n>.md`, and still
gets read before merge.

**The counter-lesson, and it is the one that stings.** This particular parser took three attempts —
not because the change was hard, but because each ticket was specified against the cases its author
could imagine rather than the ones already captured in an artefact. The first covered only a
chip-enabled log; the second added the chip-free case but asserted only that a *disagreement* fails
and that an *empty* log agrees, never that a *populated* log agrees with itself. **Test the passing
case first. The failing cases are the easy half**, and a check that can never pass looks exactly like
a check that is working.

---

## 11. A batch can be file-disjoint and still break the build — added 29 Aug 2026

`deltas.md` D6b, D7 and §5 above all warn about the same thing: two tickets in one batch touching
one file conflict on the second merge. The scope constraint that names exact file paths is the
defence, and it works.

**It does not defend against a shared *type*.** Two tickets merged the same night: one taught the
solver-log parser to read the sell and buy columns, which meant adding two fields to the
`SolverSolution` type it exports. The other wrote a new job whose tests construct `SolverSolution`
literals. **Different files, no overlap, both branches green, both test suites passing** — and
`tsc -b` failed on `main` the moment the second one merged, with 24 errors in a file neither ticket
had touched together.

**Worse, the ticket had been told to stay away from the file that would have surfaced it.** Its
Notes said, in as many words: *do not edit the parser, even though you depend on its fix.* That
instruction was right about the diff and wrong about the build.

**The rule, generalised.** A scope constraint is a claim about the *diff*. `tsc -b` is a claim about
the *program*. When one ticket in a batch changes an exported type, interface or function signature
that another ticket consumes, they are coupled no matter how disjoint their file lists are.

**What to do at queue time**, and it is cheap:

- For each ticket in the batch, ask **what it exports that another ticket imports** — not what files
  it touches. A ticket that widens a type is a ticket every consumer depends on.
- If two tickets in a batch are on either side of that line, **either sequence them across two
  nights, or put the type change and its consumers in the same ticket.** Do not batch them and hope.
- The tell is a Notes line reading *"depends on the fix in the other ticket"*. That sentence is the
  coupling, written down, and it should stop the batch rather than reassure the reader.

**Cost when it happens: low, and visible immediately** — a red `main` build, a failing Vercel
deploy, and a five-minute test-literal fix. **The danger is not the breakage, it is the delay**: the
production deploy stayed red for four hours before anyone looked, and every PR preview URL in that
window would have been stale. Check `main` is green after a multi-ticket merge, before reading
anything from the deployed app.

---

## 12. The class fix that was only an instance fix, again — added 29 Aug 2026

**§4 said "fixing the instance is not fixing the class". Here is the fourth instance, and it is
the most expensive one so far.**

Ticket #43 was written because a job's own counter read exactly 1,000 — a round number, spotted by
eye. The finding was real: **Supabase silently caps a query at 1,000 rows.** The fix was a shared
helper, `scripts/lib/paginate.ts`, which pages with `.range(from, to)` and then asserts the total
against an independent count query. That helper has been used at roughly 25 call sites since. It
is good code and it was reviewed and it works.

**It solved truncation. It did not solve ordering.**

Postgres gives no stable row order between separate queries without an `ORDER BY`. Paging a
13,000-row table in chunks of 1,000 issues fourteen separate queries. Between any two of them the
server is free to return rows in a different order — so one row comes back on two pages and
another never comes back at all.

**The count assertion passes anyway.** One row duplicated and one row dropped leaves the total
unchanged. The single guard built specifically to catch a bad paginated read is structurally
blind to this failure.

It surfaced as a preflight FAIL saying a player had 39 matches in a 38-match season. The database
had 38. Roughly 18 of the 25 call sites pass no ordering, including the backtest's 19-page read of
`feature_history` and the calibration report's read of `player_match_stats`.

**Every multi-page read in the project has been quietly duplicating and dropping rows, for weeks,
including the reads that produce the numbers used to judge the model.**

**The generalisable lesson, and it is about how the fix was scoped, not about SQL.** The bug found
was "this read was truncated". The class was "reads that exceed one page". Truncation is one
failure mode of that class; **non-determinism is another, and nobody enumerated the class's failure
modes — the fix was written against the symptom that happened to be observed.**

**What to do differently:** when a ticket introduces a shared helper for a class of operation, ask
*what else can go wrong with this class of operation* before the helper ships, and encode the
answers as things the helper **refuses** rather than things each caller must remember. A helper
that accepts a page request with no ordering is a helper that requires 25 authors to independently
remember an invariant. The fix is not 25 `.order()` calls; it is `paginate.ts` rejecting a call
that has none.

**Cost: unknown and unbounded, which is the worst kind.** Every measurement taken since #43 is
approximately right and not reproducible.

---

## 13. A metric without a baseline is not a measurement — added 29 Aug 2026

Ticket #147 added Spearman rank correlation and top-N overlap to the backtest. It shipped
correctly, tested, with sanity bounds. It produced **0.289**.

**Nobody can say whether 0.289 is good.**

The ticket — written by the orchestrator — specified an **absolute** expectation band, "0.3 to
0.6 is what a real, useful, imperfect model looks like", with **no comparator**. That band was
invented from general intuition about regression models, not derived from anything about weekly
FPL scoring. Predicting a single gameweek is largely predicting who scores a goal. The ceiling may
be near 0.3. The number is uninterpretable in either direction.

**The ticket should have required a baseline in the same run**: rank by price, rank by last
season's points per game, rank by a constant. A model that beats a naive benchmark has skill; a
model that does not is decoration. **That comparison costs almost nothing to compute and is the
only thing that makes the primary number mean anything.**

**The rule: any ticket that introduces a new evaluation metric must ship a baseline against which
that metric is read.** An absolute threshold asserted by the ticket author is a guess wearing the
costume of a specification — and because it is written in the definition of done, it is a guess
that the QA agent, the reviewer and the human all treat as established fact.

---

## 14. A sanity bound checked at the aggregate does not protect the breakdown — added 29 Aug 2026

Ticket #147 specified an upper bound as a leak alarm: **top-10 overlap above 90% fails the
report.** The reasoning was sound — a suspiciously good ranking is what lookahead contamination
looks like.

The report it produced contains **"Goalkeeper: 615 of 615 (100.0%)"** and passed.

Two independent defects, both in the same table:

1. **The bound is applied to the season aggregate only.** The by-position breakdown, added in the
   same ticket, is not bounded at all. A guard written to catch exactly this shape did not look
   where the shape appeared.
2. **A top-N metric is meaningless when the population is smaller than N.** There are about 16
   goalkeepers in a gameweek's measured population. "How many of the top 20 are in the top 20"
   over 16 rows is 100% by arithmetic. Forwards' 80.7% is the same artifact at lower resolution.

**The rules:** a sanity bound must be applied at **every level of aggregation the report prints**,
not only the headline — if a number is worth printing it is worth bounding. And **a top-N metric
must cap N at the population**, or refuse to report, exactly as the same ticket already does for
gameweeks with fewer than 50 rows. **That "too small to read" discipline existed in the ticket and
was applied to one axis and not the other.**

---

## 15. Storing data and consuming it are two tickets, and the human check must say so — added 29 Aug 2026

Ticket #146 added three columns to `feature_history` to fix two named defects: a defcon hit rate
that cannot be recovered from cumulative totals, and a 23% backtest exclusion caused by joining to
a live table that only holds the current season's players. The ticket delivered exactly that.
Rebuild verified: 18,246 rows, 100% coverage, implied hit rate 0.195.

**And the backtest run afterwards showed the defcon error unchanged at −0.191 and the exclusion
unchanged at 23%** — because `run-backtest.ts` was explicitly out of scope and still reads neither
column.

That is correct behaviour and a correctly scoped ticket. **The problem is that the ticket's human
check did not say so.** It read: *"apply the migration, rebuild the season, and confirm
element_type is non-null on every row"* — true, checkable, passed — while sitting inside a ticket
whose stated purpose was fixing two visible defects that the check would not move.

The orchestrator caught this in conversation and warned before the run. **It should have been in
the ticket.**

**The rule: when a ticket builds a substrate that a later ticket consumes, the definition of done
must state what will NOT change, and name the follow-up.** Otherwise the human reads the next
report, sees the defect he was told this ticket addresses still sitting there, and reasonably
concludes the build failed. **A ticket that fixes a cause without fixing a symptom must say which
symptom will survive it.**

---

## 16. Where the pipeline itself is structurally blind — added 29 Aug 2026

Written for the "about the system" document. These are not ticket defects; they are properties of
the App Factory as currently designed.

**a. The scope constraint that makes batching safe also guarantees class-level bugs survive.**
This is the sharpest tension in the system. A scope constraint names exact file paths, and that is
precisely what lets three tickets run overnight without colliding (§5, §11). But it also means
**no agent in the loop is ever permitted to ask "does this same mistake exist elsewhere in the
repo?"** — asking would be out of scope, and answering would break the batch. Every fix is local
by construction. §12's pagination bug lived at 18 call sites for weeks with a well-reviewed helper
sitting in the middle of them. **The pipeline cannot produce a class fix unless a human writes a
ticket that asks for one**, which means the orchestrator must periodically go looking for classes.
Consider a standing "audit ticket" slot — one night in five spent on a single question of the form
*"find every place in this repo that does X"* — run alone, since a repo-wide sweep cannot be
scope-constrained.

**b. QA reviews the diff; nothing reviews the program.** §11 recorded the type-collision case.
§12 is the same blindness on a longer timescale. The QA agent sees one ticket's changes against
one ticket's stated scope. **There is no role that reads the whole codebase and no artifact that
accumulates cross-cutting invariants.** `deltas.md` and the learnings files are the closest thing,
and they are read by the orchestrator, not by the agents.

**c. There is no distinct review for measurement code, and there should be.** §3 established that
a wrong instrument is the most expensive kind of wrong. Since then the project has shipped a
calibration report, a backtest harness, a preflight check, a prediction log and a ranking module —
**five instruments, all reviewed exactly like feature code.** §13 and §14 are both instrument
defects that passed QA cleanly. An instrument should have to answer three extra questions before
merge: *what is the baseline, what would a broken version of this look like, and is the guard
checked at every level this thing prints?*

**d. The human checks in a ticket are written by the orchestrator and verified by nobody.** They
are the most trusted lines in the whole ticket — the QA agent cannot evaluate them, the Builder
treats them as out of scope, and the human treats them as authoritative because they arrived in a
specification. **§13's invented 0.3–0.6 band is exactly this failure**: a guess became a fact
because of where it was written. The orchestrator should mark any human check derived from
judgement rather than from the codebase, in the ticket, as a guess.

**e. `feature-list.md` drifts within days and nothing notices.** The v2.0 list was eight days old
at handover and wrong about six items. **This is what caused the human to twice ask "are these
tickets even on the feature list?"** — a fair challenge that the orchestrator could not answer
confidently because the list had stopped tracking reality. **A merged ticket should update the
feature list in the same PR**, the way it already updates `decisions.md` and `supabase/README.md`.
The list is the only artifact that answers "are we building the product or just fixing things",
and it is the one nothing keeps current.

**f. The overnight batch is the wrong shape for a certain size of work, and §10 only half-solved
it.** §10 established that small fixes can go to an interactive session. The other end is also
true: **a repo-wide sweep, a class fix, or an instrument rebuild does not fit in a three-ticket
file-disjoint batch either.** The system is well-tuned for medium work and has no mode for either
extreme.

---

## 17. The pipeline cannot catch a wrong diagnosis, only a wrong implementation — added 3 Sept 2026

**The most expensive ticket of this wave was implemented perfectly.**

Ticket 89 (issue `#192`) asserted that the backtest's five-gameweek quality oracle was
mis-specified in *units* — that it estimated a per-match rate while being scored against a totals
target — and that fixing the units would restore the expected ordering (oracle above model). The
Analyst accepted it, the Builder implemented it faithfully and well (a new
`computeOracleFeaturedRate × computeOracleAppearanceRate` construction, leak-guarded identically to
the existing rate oracle, fully tested), and QA passed it.

The oracle moved from **0.507 to 0.506**.

The real defect was on the model side and had nothing to do with the oracle:
`projectAndReconstructWindowGameweek` keyed **three** point-in-time lookups — the feature-history
row, the team-strength computation, and the position prior — on each *leg's* gameweek `G+i` rather
than the window's start gameweek `G`. The five-gameweek "projection" was five one-week-ahead
projections built with information that did not exist when the app would have planned. A hindsight
oracle scored below the model because the model was reading inside the target window.

**The general failure.** Every gate in this pipeline — Analyst, Builder, QA, the scope constraint,
the definition of done — verifies that the ticket was *implemented as written*. **Nothing checks
whether the ticket's premise was true.** A confidently wrong orchestrator diagnosis converts
directly into a wasted night, and the more precisely the ticket is specified, the more efficiently
the pipeline executes the wrong thing.

**It also propagated.** Ticket 92, batched the same night, wrote the wrong cause into
`docs/projection-model-backlog.md` as G13 — so the mistaken diagnosis was durably recorded in the
project's own institutional memory, by a ticket whose entire purpose was to record settled facts.
**A documentation ticket batched alongside the ticket whose findings it records will faithfully
transcribe that ticket's errors.** Do not batch them together; let the finding land and be read
first.

**Carry-forward — the falsification check.** A ticket whose premise is a *causal claim about a
measured number* should carry, in its definition of done, a figure that **must move if the
diagnosis is right**, and an explicit instruction to **stop and report rather than merge** if it
does not. Ticket 89 had this in spirit — "the oracle must sit above the model at both horizons" —
but it shipped as a runtime assertion inside the harness rather than a build-time stop. The result:
the wrong fix merged cleanly and the nightly job simply began failing. The check was right; its
placement made it a post-merge alarm instead of a pre-merge gate.

---

## 18. Instrument defects have now outnumbered model defects for two consecutive waves — added 3 Sept 2026

§3 established that a measuring instrument can be wrong and that it is the most expensive kind of
wrong. Two waves on, the tally is no longer anecdotal. From the 2–3 September sessions alone:

| Surprising number | Cause | Instrument or model? |
|---|---|---|
| Defcon captured only 27% of actual | harness fed one averaged match, capping own-evidence at 1 against `k=5` | instrument (`#154`) |
| Goalkeeper appearance projected 1.42x | calibration report compared different populations | instrument (`#155`) |
| MID/FWD lost to a naive minutes baseline | harness used a single averaged match, not the live five-match window | instrument |
| Forward assists stuck at 0.70x after three fixes | report compares 2026/27 projections against 2025/26 actuals; the population difference is itself assist-shaped | instrument |
| Model beat its own hindsight oracle | three lookahead lookups in the five-gameweek construction | instrument |
| `attackingMultiplier` twice too steep | genuinely the model | **model** (`#184`) |

**Five to one.** And in every instrument case the first hypothesis raised — by the orchestrator, in
writing — was a model defect.

**Carry-forward.** When a measured number moves in a surprising direction, **the default hypothesis
is that the instrument changed**, and the ticket should be written to test that before proposing a
model change. Concretely: before writing a ticket that tunes a constant, name what changed in the
harness, the report, or the population since the last reading, and say why it is not the cause.
The model review reached this conclusion independently and stated it in its summary; the pipeline
has still not absorbed it into how tickets get written.

**Corollary worth stating separately.** Ticket 89 made the leak *worse* — the five-gameweek Spearman
rose 0.672 → 0.728 — because it fed the harness a genuinely better minutes signal, and minutes
carry roughly 85% of the model's ranking signal. **Improving an input to a leaking construction
makes the leak larger, and the number gets better-looking as the measurement gets more wrong.**
Any metric that improves after an unrelated fidelity improvement deserves suspicion, not
celebration.

---

## 19. Three smaller findings — added 3 Sept 2026

**a. Draft numbers, issue numbers and in-code ticket references have diverged three ways.**
Ticket drafts `89`, `91` and `92` became GitHub issues `#192`, `#191` and `#190` — reversed by
creation order — and the Builder wrote `#187` into the source comments for the oracle work. Three
numbering spaces, none reconciled. Tracing a code comment back to the ticket that caused it now
requires guessing. **Carry-forward: the ticket body should state its own draft number, and the
Builder should be required to cite the GitHub issue number it was dispatched with, not a number of
its own choosing.**

**b. No part of this system can verify an external data format, including the orchestrator.**
Writing a ClubElo ingest ticket required seeing one response. `api.clubelo.com` was unreachable from
the cloud container (egress allowlist), from the device VM (same allowlist), and from WebFetch
(robots.txt), and when the human ran `curl` himself the host returned HTTP 502 on every endpoint —
its own outage. The standing rule from `LEARNINGS-first-build-wave.md` §5 (never assert an external
format you have not seen) held and correctly blocked the ticket. But the consequence is structural:
**any ticket touching a new external source is permanently gated on a human running a command.**
Worth an explicit decision — either accept that gate, or maintain the environment's custom network
allowlist (`deltas.md` D4) proactively for sources the roadmap already names.

**c. A pre-registered acceptance criterion was set aside within a day of being set.** Ticket 91's
definition of done said: if any position's appearance ratio moves *away* from 1.00, revert rather
than tune. Three of four did. The orchestrator recommended deferring the decision until the backtest
— the better instrument for the question — was trustworthy again, and stated openly that this
departed from a rule it had itself pre-registered. **That may well be the right call, and stating
the departure openly is the right way to make it. But this is precisely the move pre-registration
exists to prevent, and a deferred revert becomes a permanent keep by default.** Carry-forward: when
a pre-registered criterion is set aside, the deferral needs a named condition and a named owner for
closing it out, recorded where the next session will find it — not just a sentence in a chat.
