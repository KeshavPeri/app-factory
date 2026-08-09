v0.1 — provisional, revised at Phase 8

# Ticket template

Shaped to pass the evening lint pass (§4.7) first time. The Analyst reads every field below
before a ticket goes into Ready — fill them in, don't leave placeholders, and this ticket won't
bounce back for clarification while Keshav is asleep.

---

## Title

`<verb> <thing> — <one clause on why>`
e.g. "Add gameweek deadline countdown — so the home screen answers 'how long do I have'"

## Context

One or two sentences. What part of the product brief does this ticket serve? Link the section
if the brief has one (e.g. "Core feature #2, product-brief-template.md §2").

## Scope

**In scope:**
- <bullet the concrete, buildable pieces>

**Explicitly out of scope:**
- <anything a Builder might reasonably assume is included but isn't — this line is what stops
  scope creep into Tier-1 territory, e.g. "does not add any new stored user data">

## Definition of done

<A checklist the Builder and QA can both point at and agree is objectively met. Not "looks
good" — concrete and checkable.>
- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] <criterion 3>

## Notes for the Analyst / Builder

<Anything ambiguous that the person queueing this ticket already knows the answer to but hasn't
written above — better here than left for a 3am escalation.>

---

## Worked example

### Title
Add gameweek deadline countdown — so the home screen answers "how long do I have"

### Context
Core feature #1 in the FPL brief: "the home screen must show time remaining to the next
transfer deadline." Nothing exists for this yet.

### Scope
**In scope:**
- A countdown component on the home screen showing time remaining to the next gameweek
  deadline, in Singapore time (per brief's locale setting, Tier 3)
- Deadline data read from the chosen external data source (per brief §6)
- Graceful fallback text ("deadline unavailable") if the data source doesn't return a deadline

**Explicitly out of scope:**
- No push notifications or reminders — that's a separate future ticket
- No new stored data — the deadline is fetched live each page load, nothing persisted

### Definition of done
- [ ] Home screen shows a live countdown to the next gameweek deadline
- [ ] Countdown is displayed in Singapore time
- [ ] If the data source call fails, the fallback text renders instead of a broken UI
- [ ] Works on both the installed iPhone PWA and the laptop browser

### Notes for the Analyst / Builder
The data source's exact deadline field name isn't confirmed yet — if the API response doesn't
have an obvious deadline field, that's a genuine ambiguity, not a Tier-1 issue: ask rather than
guess a field name.
