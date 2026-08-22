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
