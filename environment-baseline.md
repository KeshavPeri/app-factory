# Environment baseline — Task 1.6

**Checked:** 9 August 2026

| Item | Value |
|---|---|
| Plan tier | Claude Pro account (confirmed via `/status` → Login method) |
| Claude Code version | 2.1.226 — current latest as of 8 Aug 2026 release (verified against changelog) |
| GitHub CLI account | KeshavPeri, logged in to github.com, protocol https, token scopes: gist, read:org, repo, workflow |
| Stray `ANTHROPIC_API_KEY` in shell | None found (`env | grep -i anthropic` returned empty) |
| Shell | zsh (`/bin/zsh`) |

**Known quirk, not urgent:** two Claude Code installations exist on this Mac — an old native install at `~/.local/bin` (not on PATH) and the active npm-global install under nvm Node v24.16.0 (`~/.nvm/versions/node/v24.16.0/bin/claude`, the one actually running, version 2.1.226). They could drift out of sync if the npm one is ever removed and the shell falls back to the stale native one. Fix later: either delete `~/.local/bin/claude` or add it to PATH and keep both updated — not blocking, revisit if `claude --version` ever looks wrong.

---

## Routines / cloud-session baseline — Task 5.5

**Checked:** 9 August 2026

| Item | Value |
|---|---|
| Daily routine run cap | **Not surfaced.** No figure appears at claude.ai/code/routines or claude.ai/settings/usage on a Pro account as of this date. The docs say the cap exists and is shown live; it isn't. Treat it as unknown and detect it by hitting it — a rejected run is the signal. Task 5.5 is closed as "checked, not available", not as a number. |
| Repository attached | `KeshavPeri/fpl-advisor`, confirmed on the routine detail page (task 5.4) |
| `claude/` branch restriction | Confirmed as designed, not relaxed. Platform behaviour, no setting to toggle. Our `claude/ticket-<n>-<slug>` convention sits inside the always-accepted case |
| Trigger picker options (observed in the live form) | Once / Hourly / Daily / Weekdays / Weekly / **Custom (cron)** — custom cron is available in the browser, no CLI needed. **Cron is evaluated in UTC**; the summary line above the field renders local time |
| Usage credits / metered overage | Off — keep it off (§2: no API billing) |
| Routine name | `FPL Advisor overnight pipeline` |
| Routine model | Sonnet 5 |
| Schedule | Daily, 02:00 SGT (departs from §6 — see `deltas.md` D2) |
| Cloud environment | `App Factory` — Custom network, default allowlist plus `fantasy.premierleague.com`, `*.vercel.app`, `vercel.com`, `*.supabase.co` |
| Environment setup script | `apt update && apt install -y gh \|\| true` |
| Connectors attached to the routine | None (all removed) |
| Cloud VM | Ubuntu 24.04 x86_64, 4 vCPU / 16 GB RAM / 30 GB disk, Node 22 on PATH |

**Known gaps in the cloud image, as of this date:** `gh` is not pre-installed (hence the setup
script), and the Trusted network allowlist covers GitHub and package registries but not Vercel,
Supabase or the FPL API (hence the Custom policy).

---

**This is what to compare against if something breaks in week three.**
