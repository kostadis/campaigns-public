# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **public, generated mirror** of selected material from the private `kostadis/campaigns` repo. It holds content, not code: D&D session summaries, NPC dossiers, and the `gm-assistant` Claude Code skill family. There is no build, lint, or test.

Everything committed here is public. Review `git status` / `git diff` before every commit.

## Syncing from upstream

```bash
scripts/sync-from-campaigns.sh [branch]   # default branch: main
```

It makes a fresh shallow, sparse clone of `kostadis/campaigns` from GitHub (override with `CAMPAIGNS_REPO=...`) — it never reads a local working copy such as `~/src/campaigns`. Commit messages for syncs record the upstream short SHA ("Synced from campaigns @ <sha>"); the script prints it at the end.

## Publishing to Google Drive (for NotebookLM)

```bash
scripts/sync-to-gdrive.py --dry-run   # preview
scripts/sync-to-gdrive.py             # create/update Docs
scripts/sync-to-gdrive.py --prune     # also trash Docs whose source .md is gone
```

A `uv run --script` file (deps declared inline). It mirrors every `.md` (except `CLAUDE.md` and `scripts/`) into a `campaigns-public` folder at My Drive root as **Google Docs**, because NotebookLM needs Docs rather than raw markdown. Things that are deliberate:

- Docs are updated in place, never deleted and recreated. That keeps their file IDs stable, so NotebookLM sources that point at them keep working. Unchanged files are skipped by comparing the source md5 stored in the Doc's `appProperties`.
- It uses the `drive.file` scope, so it sees only files it created. A hand-made folder of the same name is invisible to it.
- `SKILL.md` Docs take their skill directory's name, because NotebookLM shows sources by title only.
- Auth uses the OAuth client at `~/.config/gdrive-cli/credentials.json`, the same location `gdrive-cli`/`drive-tagger` use. The token is cached in `token-campaigns-public.json` next to it.

Run it after the `sync-from-campaigns.sh` diff has been reviewed and committed, not before. Drive is a second publication target.

## Ownership: what the sync overwrites

Treat these paths as upstream-owned. Fix content in `kostadis/campaigns` and re-sync; local edits will be lost or will silently diverge.

| Path | Sync behavior |
|---|---|
| `<campaign>/summaries/` | Deleted and rewritten wholesale each run |
| `<campaign>/npcs/` | Upstream top-level `docs/npcs/*.md` copied over (additive — stale files are **not** removed) |
| `gm-assistant/skills/` | Deleted and rewritten wholesale |
| `gm-assistant/README.md`, `SKILLS.md` | Overwritten |

Campaigns are listed in the `CAMPAIGNS` / `NPC_CAMPAIGNS` arrays in the script (currently `obelisk`, `out-of-the-abyss`, `Phandalin`). Adding a campaign means adding it there; directory names match between the two repos.

## How summaries are selected

Which sessions get published, and their `NNN-session-<slug>.md` filenames, are decided by the upstream publisher `scripts/publish_sumamries/publish_sumamries` (note the upstream misspelling). The sync script imports it and calls `publication()` / `print_preflight()`, but writes the **source bytes unrefactored** — it deliberately skips the publisher's scene-renumbering/reformatting step. Upstream reads `session-summary.md`, `session_summary.md`, and `NOT_WRITTEN.txt` per session directory.

## gm-assistant

Only `skills/`, `README.md`, and `SKILLS.md` are mirrored. The README describes `profiles/`, `working/`, `converted/`, and `.claude/skills/` symlinks that exist only in the private repo — their absence here is expected, not breakage.
