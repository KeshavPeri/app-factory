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

**This is what to compare against if something breaks in week three.**
