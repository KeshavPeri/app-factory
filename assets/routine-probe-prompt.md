v0.1 — written 9 Aug 2026 for Task 5.6. Throwaway: delete or overwrite once the probe has run.

# Routine diagnostic probe prompt

**Purpose.** Task 5.6 asks for one manual run that proves the trigger fires. Delta D1 in
`deltas.md` raised a bigger question at the same time — whether a cloud routine can reach the
GitHub project board at all — so the trigger test doubles as a diagnostic. One run, six answers.

**How to use it.** Create the routine (Phase 5 runbook step 3) with the text between the rules
below as its prompt. Click **Run now**. Read the report. Then edit the routine and replace this
prompt with `orchestrator-prompt.md`.

**It is read-only** apart from adding and removing one label on one scratch issue, and posting one
comment. Nothing else is written, no branch is created, no PR is opened.

---

You are running a one-off diagnostic. **Do not build anything, do not create branches, do not
open pull requests, and do not modify any file in the repository.** Your entire job is to run the
checks below, record exactly what happened, and report.

Work through every check even if an earlier one fails. A failure is a result, not a reason to
stop. For each check, record the literal command or tool you used and the literal output or error
(including HTTP status codes and any `x-deny-reason` header). Do not summarise away error text and
do not guess at a cause you did not observe.

## Check 1 — session and repo

- Run `pwd`, `git remote -v`, and `git branch --show-current`.
- Run `ls -la .claude/agents/` and `ls -la escalation.md design-reference.md CLAUDE.md decisions.md`.
- Report which of those files exist. These are what every future run depends on being in the clone.

## Check 2 — GitHub authentication mode

- Run `echo "GH_TOKEN=$GH_TOKEN"` and `echo "GITHUB_TOKEN=$GITHUB_TOKEN"`.
- Report whether each is empty, the literal string `proxy-injected`, or something else.
  **Never print a value that looks like a real token** — if it is neither empty nor
  `proxy-injected`, report only its length and first four characters.
- Run `which gh` and `gh --version`. Report whether `gh` is installed.

## Check 3 — GitHub REST (the fallback path)

- List the open issues in this repository, using the built-in GitHub tools.
- Report the issue numbers, titles, and the labels currently on each.
- List the labels that exist in the repository.

## Check 4a — GitHub GraphQL and Projects v2 via `gh` (the path we expect to be blocked)

Run these in order and report the full result of each, success or failure:

1. `gh api graphql -f query='query { viewer { login } }'`
   — does *any* GraphQL request survive the proxy?
2. `gh project list --owner KeshavPeri`
   — `gh project` is GraphQL-backed, so this is expected to 403.
3. If step 2 returned a project, fetch its items and their Status field values:
   `gh project item-list <NUMBER> --owner KeshavPeri --format json`

If any of these returns a 403, **quote the error message verbatim**, including whether it names a
REST fallback.

## Check 4b — Projects v2 over REST (the path that probably works)

GitHub added REST endpoints for Projects v2; they are live in API version `2026-03-10`. These are
plain REST, so they do not hit the proxy's GraphQL restriction. Run each with
`gh api -H "X-GitHub-Api-Version: 2026-03-10" ...` and report the status and result:

1. `gh api -H "X-GitHub-Api-Version: 2026-03-10" /users/KeshavPeri/projectsV2`
   — list the boards. Report the `number` and `title` of each.
2. Using the number of the board titled **FPL Advisor Pipeline**:
   `gh api -H "X-GitHub-Api-Version: 2026-03-10" /users/KeshavPeri/projectsV2/<NUMBER>/fields`
   — find the **Status** field and report **the exact name of every one of its options, character
   for character, including capitalisation**. This is the single most important line in your
   report.
3. `gh api -H "X-GitHub-Api-Version: 2026-03-10" /users/KeshavPeri/projectsV2/<NUMBER>/items`
   — list the items and their current Status values.
4. **Write test.** Take exactly one item, PATCH its Status to a different option, read it back to
   confirm, then PATCH it straight back to where it was and confirm again. Report whether both
   writes and both read-backs succeeded. If there are no items on the board, say so and skip.

If any of these fails with 401/403, quote the error verbatim and report whether `GH_TOKEN` was
`proxy-injected` (Check 2) — the user-scoped project endpoints are documented as not working with
GitHub App tokens or fine-grained PATs, so *which* token is in play decides the fix.

## Check 5 — can labels carry state instead?

- Pick the lowest-numbered open issue. If there are no open issues, create one titled
  `probe: scratch issue` with an empty body, and say that you created it.
- Add the label `probe-test` to it (create the label if it does not exist), confirm via a fresh
  read that the label is present, then remove the label again and confirm it is gone.
- Report whether the add, the read-back, and the remove each succeeded.

## Check 6 — outbound network

For each URL below run `curl -sS -o /dev/null -w "%{http_code}"` and report the status code, plus
any `x-deny-reason` header if the request was denied (add `-D -` to see headers):

- `https://fantasy.premierleague.com/api/bootstrap-static/`
- `https://fpl-advisor-wine.vercel.app`
- `https://registry.npmjs.org`

## Report

Post your findings as a comment on the scratch issue from Check 5, and also print the same text
in the session transcript. Structure it exactly like this, one line per check:

```
PROBE REPORT — <date>

1. REPO       — PASS/FAIL — <what you found>
2. AUTH       — <GH_TOKEN mode> — gh installed: yes/no
3. REST       — PASS/FAIL — <n> issues readable, <n> labels
4a. GRAPHQL   — PASS/FAIL — viewer query: ... | gh project list: ...
4b. PROJECTS REST — PASS/FAIL — list: ... | fields: ... | items: ... | write+revert: ...
   COLUMNS    — <exact Status option names, or "not readable">
5. LABELS     — PASS/FAIL — add/read/remove
6. NETWORK    — fpl-api: <code> | vercel: <code> | npm: <code>

VERDICT — Can a routine read and write the project board? YES / NO / PARTIAL
BLOCKERS — <one line each, or "none">
```

End with nothing else. No recommendations, no plan, no offer to continue — the report is the
whole deliverable.
