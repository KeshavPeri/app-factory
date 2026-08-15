v1.0 — written 11 Aug 2026, after twelve tickets built and merged through the pipeline in a single
day. Source material for rewriting `docs/01-the-app-factory-system-explainer` and
`docs/02-running-the-app-factory-user-guide`. Platform facts proven by experiment live in
`deltas.md`; this file is the wider set of lessons, including the ones about how to *use* the
system.

# What the first real build wave taught us

Twelve tickets: #8 through #15, plus #22, #26, #28 and #29. Feature-list items 1–9 shipped. Two
genuine near-misses, one guaranteed-recurring bug, and a number of assumptions that turned out to be
wrong in ways worth writing down.

---

## 1. The system worked. That is the headline.

An overnight pipeline written by a beginner-to-intermediate coder built a design system, a database
schema, two ingest jobs, a scheduled Action, a router, a form screen, a scoring module with 33
passing tests, and a solver smoke test — in one day, reviewed from a phone. Nothing was merged
without a human deciding to.

The parts that carried the most weight were, in order: **the definition of done**, **the "explicitly
out of scope" section**, and **the QA packet's honesty about what it could not verify**. All three
are cheap to write and were the difference between usable output and plausible output.

---

## 2. Specification quality is the bottleneck, exactly as designed

Every bad outcome traced to a ticket, not to a model.

- A DoD item required *"the database rejects a squad with other than 15 picks — enforced by a
  constraint or unique index."* That is not possible with an index; counting across fifteen rows
  needs a deferred constraint trigger. The ticket asked for substantial machinery while sounding
  like a one-liner.
- A DoD item required *"the numbers 10 and 12 appear nowhere in `src/lib/projection/`"* — while the
  same ticket specified tests using ten matches and a hundred matches. No correct implementation
  could pass.
- A DoD item required an estimate *"within 0.02 of 0.40"* from a shrinkage formula that yields
  0.4286 at one end of its input range. Arithmetically impossible.
- A ticket asserted the solver's repository ships a sample data file. It never has, on any branch.

**Lesson for the user guide: lint your own arithmetic.** If a DoD item states a number, compute it
before writing it. If it says "enforced by a constraint", name the constraint. If it asserts a third
party ships a file, check.

**The counter-lesson, and it is the important one:** in all four cases the pipeline behaved well.
Two were caught by the Analyst before the run. One was caught by the Builder mid-run, which narrowed
its own scope and said so rather than faking a fixture. One was caught by reading the code. **A
wrong ticket is recoverable; a wrong ticket plus an agent that papers over it is not.** The
instruction to report rather than improvise is doing real work.

---

## 3. Two concurrency bugs, one root cause (see `deltas.md` D6)

Both were the same failure at different layers: concurrent actors assuming exclusive access to
shared mutable state.

**Two Builders, one working directory.** The orchestrator dispatched both in parallel into a single
checkout. One ticket's commit landed on the other's branch *and* on local `main`. It self-healed
before any push, but only because a Builder happened to read its own `git log`.

The rule that failed was *"one writer per branch, always"* — and it was **satisfied** the whole
time. It is the wrong invariant. **One writer per working tree** is the one that matters. Fixed by
mandating `isolation: 'worktree'` on every Builder dispatch in a multi-ticket batch, plus a
`git branch --show-current` check in `builder.md` and a branch-containment check in `qa.md`.

**One global counter in `decisions.md`.** Both branches forked from the same `main`, both appended
at the same point, and the second merge always conflicted. Deterministic on every 2-ticket run,
which is the normal batch size.

**The fix that was proposed and rejected is instructive:** ticket-scoped entry numbers (`#8.1`,
`#9.1`). That does not work — **git conflicts on position, not content.** Two branches inserting
different lines at the same point still conflict. Only separate files fix it. Now
`decisions/ticket-<number>.md`, one per ticket, with root `decisions.md` as a read-only archive.

**Generalised lesson for the docs:** when scoping a batch, ask not only *do these tickets depend on
each other* but *do they append to the same file*. Wave 3 hit this again — #11 and #12 both added a
step to `scheduled-jobs.yml` and conflicted exactly as predicted. The fix in #29 was to create a
*separate workflow file* rather than share one.

---

## 4. RLS and GRANTs are two gates, and the local test is blind to one (see `deltas.md` D8)

The first real workflow run failed with `permission denied for table job_runs`. Both schema
migrations enabled Row Level Security with a policy and issued **no GRANT at all**.

- `permission denied for table X` → missing **GRANT**
- `new row violates row-level security policy` → missing or wrong **POLICY**

The secret key's `service_role` bypasses RLS but not GRANTs.

**Why nobody caught it:** the DoD said the migration must apply cleanly against a local Postgres. It
did — as a superuser, for whom grants are irrelevant. **A local-Postgres substitute is blind to this
entire class of bug.** Neither the Analyst lint nor QA was at fault; both passed honestly.

**Lesson: "it worked against a local substitute" is weaker evidence than it reads.** It happened
twice — the second time a REST shim stood in for Supabase and could not cover Supabase-specific
behaviour. QA disclosed both, which is the system working. But tickets should say plainly which
class of failure a substitute cannot detect.

---

## 5. External facts decay, and the brief is not self-correcting

Three assumptions in the Phase 1 brief were wrong within a day of being written:

- FPL-Core-Insights refreshes at **07:30 and 17:30 UTC**, not 05:00 and 17:00.
- The 2026/27 season directory did not exist at all when the ingest ticket was written — then
  appeared mid-wave, which changed what "empty" meant for a ticket already in flight.
- The solver's repository has never shipped the sample file the ticket assumed.

And one the brief could not have known:

- **FPL element ids are not stable across seasons.** 453 of 458 players changed id. `code` is the
  stable key. This invalidated a foreign key, orphaned freshly-ingested historical data until a
  follow-up ticket added `player_code`, and would have silently produced a model trained on almost
  nothing.

**Lesson: verify every external claim at ticket-writing time, not at brief-writing time**, and put
the verification date in the ticket. When the ticket and the brief disagree on a fact, **fix the
brief** — `escalation.md`'s own calibration warning says the same thing about tiers. An Analyst that
mechanically prefers the brief will propagate a stale fact into code.

---

## 6. The hidden human step in the dependency chain

Migrations are written by agents and applied by hand — correctly, since touching live data is
Tier 1. But that puts a **human step inside the dependency chain**, and it broke things twice:

- The squad screen showed "no gameweeks loaded" because the ingest had never run against live.
- The heartbeat failed because a merged migration had not been applied.

**A migration file on `main` does not mean it has been applied.** That sentence is now in
`supabase/README.md`, along with a table tracking what is actually live. By the end of the wave that
table had drifted anyway — 3 of 7 migrations listed.

**Lesson for the user guide:** the daily rhythm is not "review, merge, done." It is **review →
merge → apply migration → update the applied table → trigger the job → verify data landed.** Any
ticket whose migration is unapplied will fail in a way that looks like a code bug.

**Related:** apply a migration from an open PR *before* merging when you want the preview to be
testable. Migrations are additive and idempotent, so this is safe, and it turns "the preview looked
fine" into "I used it."

---

## 7. Things that cost time and are pure mechanics

- **`git diff` opens a pager.** Pasting a multi-line block where one line is `git diff` means `less`
  swallows the rest as keystrokes. Recommend `git config --global core.pager cat` early.
- **Trailing `# comments` on pasted git commands become arguments.** `git status # check things`
  reports on files named `#`, `check`, `things` — and prints "working tree clean" for a dirty repo.
  Never put trailing comments in a command block a beginner will paste whole.
- **Relative `--body-file` paths fail from the wrong directory.** Always prefix with `cd`.
- **Push rejected after an overnight run** is normal — `main` moved. `git pull --rebase` then push.
  Worth wrapping in a shell function.
- **A stale `.git/index.lock`** blocks everything with an unhelpful error.
- **The PWA service worker caches CSS on iOS.** A UI change can look absent on the phone while being
  correct. Test in a private tab before diagnosing a defect.
- **Each PR has its own preview URL.** Appending a route to *last* ticket's preview shows the old
  build. The correct URL is line 1 of the QA packet, deliberately.

Two shell helpers now exist in `~/.zshrc` — `ship "message"` and `sync` — which fold most of the
above into two commands. **Worth shipping with the system for the next app.**

---

## 8. What proved genuinely load-bearing in a ticket

Ranked by how often it prevented a bad outcome:

1. **Grep-checkable DoD items.** "The strings `#aa3bff`, `#4ade80`, `system-ui` appear nowhere in
   `src/`" is worth ten sentences of design intent. Two agents can agree on it from code alone.
2. **A scope constraint naming exact file paths.** It is what makes parallel tickets safe, and it is
   what QA checks first now.
3. **Pre-answering ambiguities in the ticket body, not in a comment.** The orchestrator dispatches
   the Builder with the ticket's title, scope and DoD — **comments are not in that payload.** If a
   rebuild is needed, edit the ticket body; a comment may never be read.
4. **Naming the wrong implementation explicitly.** "`background-attachment: fixed` is ignored on iOS
   Safari — use a fixed-position element" pre-empts the single most likely mistake, and greps for it.
5. **Stating which failures a test substitute cannot catch.**

---

## 9. Gaps in the system design still unresolved

- **There is no defined path for "the human rejects a draft PR."** Five states exist — ready,
  in-progress, for-review, blocked, closed — and a 2-revision cap *within* a run. Nothing covers
  Keshav reviewing a draft PR and rejecting it. Current practice: close the PR, delete the branch,
  **edit the ticket body**, relabel `status:ready`. This should be written into §4 properly.
- **Two tickets in one batch can generate colliding migration timestamps.** Two share
  `20260811180000`. Harmless by luck this time.
- **A stray `claude/<random>` branch** appeared from an interactive lint session that made a small
  commit. Linting is supposed to write nothing. Worth deciding whether that is acceptable.
- **Merged branches accumulate.** Enable "Automatically delete head branches" in repo settings;
  nothing in the pipeline depends on a merged branch existing.

---

## 10. For the "about the system" document

The framing that best survived contact with reality:

> The pipeline does not remove the human. It moves the human from *writing code* to *writing
> specifications and making the decisions that are expensive to reverse* — and it makes those two
> jobs the only ones that matter.

Everything that went wrong in this wave went wrong at specification time or at a human gate
(applying a migration, merging, setting a secret). Nothing went wrong because a model could not
write the code. That is worth saying plainly to anyone deciding whether to build one of these.
