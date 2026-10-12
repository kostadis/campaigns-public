# gm-assistant

A workspace-scoped GM co-pilot: a family of Claude Code skills, a style profile drawn from one finished campaign, and a small bridge to the local `flexai-social` tool.

This directory is **self-contained** — the skills themselves live here under `skills/`, and `.claude/skills/gm-*` are relative symlinks pointing back. Clone the campaigns repo on a new machine and everything is restored together. (Claude Code reads the symlinks at runtime; the canonical files live here.)

---

## What's here

```
gm-assistant/
├── README.md                          ← you are here
├── SKILLS.md                          ← canonical index of the 12-skill family
├── skills/                            ← THE CANONICAL skill files (symlinked from ../.claude/skills/)
│   ├── gm-session-prep/SKILL.md
│   ├── gm-faction-network/SKILL.md
│   ├── gm-strategy-doc/SKILL.md
│   ├── gm-handout/SKILL.md
│   ├── gm-npc-build/SKILL.md
│   ├── gm-improv/SKILL.md
│   ├── gm-npc-voice/SKILL.md
│   ├── gm-statblock/SKILL.md
│   ├── gm-social-encounter/SKILL.md
│   ├── gm-module-inventory/SKILL.md   (+ example-module-inventory.md)
│   ├── gm-quest-log/SKILL.md
│   └── gm-voice-reconstruction/SKILL.md
├── profiles/
│   └── finished-gm.md                 ← v1 GM style profile, drawn from one finished campaign (Hero's Journey)
├── working/
│   ├── hero-journey-notes.md          ← running reading notes from the source narrative
│   └── summary-native-npc-dossiers/   ← WORKFLOW.md + scripts for the NPC dossier verify → publish run (source for a future skill)
└── converted/
    └── hero-journey.md                ← cleaned markdown of Hero's Journey (image-stripped)
```

And at the workspace root:

```
campaigns/.claude/skills/
├── gm-session-prep → ../../gm-assistant/skills/gm-session-prep   (symlink)
├── gm-faction-network → ../../gm-assistant/skills/gm-faction-network
├── ... (all 12 gm-* skills are relative symlinks back to gm-assistant/skills/)
├── oota-chapter-release/                                          (real dir — pre-existing)
└── phandalin-chapter-release/                                     (real dir — pre-existing)
```

---

## What the system does

Twelve Claude Code skills, invokable by trigger phrase or `/skill-name`, that give Kostadis tool-shaped support for:

- **Pre-session prep** — generating session-prep docs, in-world handouts, NPC dossiers, antagonist strategy docs, faction-network maps.
- **At-the-table play** — emergency improv when the party goes off-script, on-demand NPC voice, on-the-fly stat blocks, structured prisoner-interrogation / social-encounter scenes via the local `flexai-social` tool.
- **Canon and campaign records** — a canonical proper-noun inventory for a published module, and a player-facing quest log rebuilt from session summaries.
- **Post-session cleanup** — voice-reconstructing PC dialogue in scene extractions against each character's voice file, behind a human review table.

The design intent and the recipe behind the system: see [SKILLS.md](SKILLS.md).

---

## How the system was built

The defining discovery was that Kostadis's own ToEE notes already contained an A/B test on the workflow:

| Commit | Prompt | Output |
|---|---|---|
| `d108c19` | None — Claude treated as a tool | Utility scripts, VTT pipeline data, basic session-prep stubs |
| `41a89ab` | *"You are my co-gm helping me create the next session. This is a political thriller. The players were 15."* + context loadout | Deep prep docs, in-world handouts, NPC strategy, faction networks, 428-line endgame plan — *one of his best ToEE sessions ever* |

The skill family is built around that A/B finding. The recipe — **minimal role-frame + rich context loadout from existing campaign docs** — is baked into every skill: each one reads `docs/campaign_state.md`, `docs/world_state.md`, `docs/party_state.md`, the most recent session summaries, and the relevant entries in `docs/npcs/` and `docs/background/`. The prompt itself does little; the context does the work.

The style basis comes from a v1 profile drawn from one finished campaign (*The Hero's Journey or The War of the Giants* — 88 chapters, ~190k words, post-Hoard-of-the-Dragon-Queen, heavily modified Storm King's Thunder). See [profiles/finished-gm.md](profiles/finished-gm.md) for the 15 defining moves and the open questions.

---

## Restoring on a new machine

Everything you need lives in two places: this repo and the `flexai-social` tool repo.

### 1. Clone the campaigns repo

```bash
git clone <campaigns repo url> <campaigns-root>
```

`<campaigns-root>` is wherever you clone it — it differs per host (`~/src/campaigns` on one, `~/campaigns` on another; hypostasis records it as `data_roots.campaigns`). Nothing here depends on the location: the `.claude/skills` symlinks are relative, and every path in these docs is relative to the repo root.

The skills come with the repo at `gm-assistant/skills/gm-*/SKILL.md`, and the symlinks at `.claude/skills/gm-*` point back to them. Claude Code picks them up automatically when you open any project inside the campaigns repo.

**On Windows native (not WSL):** ensure `git config --global core.symlinks true` before cloning, otherwise the symlinks at `.claude/skills/gm-*` come down as text files containing the symlink target path and Claude Code won't load them. WSL and Linux native clone correctly by default.

To verify the symlinks resolve after cloning:
```bash
ls -la <campaigns-root>/.claude/skills/gm-session-prep    # should be a symlink → ../../gm-assistant/skills/...
cat <campaigns-root>/.claude/skills/gm-session-prep/SKILL.md | head -3   # should print the frontmatter
```

### 2. Install dependencies

The skills are inert markdown and need nothing to load. But two skills wrap external tools:

- **`gm-social-encounter`** wraps `flexai-social`:
  ```bash
  git clone <flexai-social repo url> ~/src/mytools/flexai-social
  cd ~/src/mytools/flexai-social
  pip install -r requirements.txt
  ```
  The tool also needs the commercial FlexAI Digital Resource Companion xlsx files (not committable). Point at them via `--data-dir`, `$FLEXAI_DATA_DIR`, or the hardcoded default Drive path. Start the server: `python3 app.py`.

- **`gm-statblock`** uses the **5etools MCP server** if configured (per the campaign's `.mcp.json`) for canonical 5e stat-block lookups. Without it the skill falls back to SRD-from-memory + canon-by-feel.

- **All prep skills** assume the campaign workspace has the conventional structure (per the repo-root `CLAUDE.md`):
  ```
  <campaign>/
  ├── config.yaml
  ├── docs/
  │   ├── campaign_state.md
  │   ├── world_state.md
  │   ├── party_state.md  (or party.md)
  │   ├── background/
  │   └── npcs/
  └── summaries/
      └── YYYYMMDD/
  ```
  If a campaign lacks these, the skills will tell Claude to mark the gap rather than fail.

### 3. Optional: the source narrative for the style profile

If you want to re-derive the Finished-GM profile (or add to it from the other four finished campaigns), the narratives live on Kostadis's Google Drive at `/mnt/g/My Drive/Adventure Stories/`. Only *Hero's Journey* is pre-converted to markdown. The other four (Curse of the Hags Book 1+2, Drow Conspiracy, Storm King's Thunder Boys, Temple of Elemental Evil) are .docx in the 40-90 MB range with embedded images that need stripping during conversion. See [working/hero-journey-notes.md](working/hero-journey-notes.md) for the methodology and [profiles/finished-gm.md](profiles/finished-gm.md) for the open questions about how patterns generalize across campaigns.

---

## What still needs to be done

See task list in any Claude Code session inside this repo. The notable pending item:

- **Smoke-test `gm-session-prep` against a real ToEE session.** The skill was built to mimic the output shape of `toee/notes/phase3_endgame.md` from the v2 commit. The right test is: invoke `/gm-session-prep` in a fresh Claude Code session inside the campaigns repo's `toee/` with the upcoming session as input, and compare the output to that hand-built doc. If the skill produces tool-shaped output rather than co-GM-shaped output, iterate the skill (most likely: tune the "Style notes for this output" section).

---

## How to extend

When you find a new GM workflow that you keep doing by hand:

1. Note the workflow + an example of "good" output you've already produced.
2. Create the canonical skill at `gm-assistant/skills/gm-<name>/SKILL.md`, then the runtime symlink from the repo root: `ln -s ../../gm-assistant/skills/gm-<name> .claude/skills/gm-<name>`.
3. Use the existing skills as templates — the prep and at-the-table skills share the structure: frontmatter, *When to invoke* (triggers), *Inputs to confirm* (AskUserQuestion 1x1), *Required context* (which docs to read), *Style notes* (3-5 inline bullets), *Output shape* (with example template), *Steps*, *What this skill is NOT for*.
4. Add it to [SKILLS.md](SKILLS.md) so the index stays the canonical roster.

Avoid: keeping pasteable prompt templates around and expecting to remember to use them. If a workflow recurs enough to write down, it's worth a skill.

---

## See also

- `CLAUDE.md` (campaigns repo root) — the workspace conventions (campaign isolation rule, trust hierarchy)
- `~/src/CampaignGenerator/CLAUDE.md` — the engine these campaigns run against
- `~/src/mempalace/CLAUDE.md` — the local-first verbatim memory / MCP server
- `~/src/mytools/flexai-social/RULES.md` — the social-encounter rule text
