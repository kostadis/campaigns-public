# gm-assistant skills — canonical index

Twelve workspace-scoped Claude Code skills. **Canonical files** live at `gm-assistant/skills/gm-*/SKILL.md`. **Runtime symlinks** at `.claude/skills/gm-*` point back to those — Claude Code auto-discovers them when you open any project inside the campaigns repo.

Edit the files in `gm-assistant/skills/`. The symlinks update transparently.

The skills share a design recipe — *minimal role-frame + rich context loadout from existing campaign docs* — derived from the toee/notes v1-vs-v2 A/B test (see [README.md](README.md)).

---

## The roster

### Pre-session prep cluster

#### `gm-session-prep` — the foundational prep skill

Generates a co-GM session prep document. Output mirrors `toee/notes/phase3_endgame.md`: win condition, default trajectory, the clever play, scene staging with branches, anticipated player questions, stage directions, open decisions.

**Triggers:** "prep the next session" • "co-gm me" • "help me run the next session" • `/gm-session-prep`

**Use when:** You need the whole prep doc, not just one piece of it.

---

#### `gm-faction-network` — operational map of a place

Output mirrors `toee/notes/nulb_network.md`: real-vs-cover identities, supply chains, what-the-party-knows-vs-what-the-GM-knows, ASCII flowcharts, quote canon for each NPC.

**Triggers:** "map the factions in {place}" • "give me the network for {town}" • "who's really running {place}" • `/gm-faction-network`

**Use when:** A single location has multiple competing intrigues you need to keep straight.

---

#### `gm-strategy-doc` — per-antagonist dossier

Output mirrors `toee/notes/hedrack_strategy.md` and `falrinth_strategy.md`: the NPC from inside their own head — their frame, their secret, the optimal play *for* them, the optimal play *against* them, contingencies, voice samples, what they'd never say.

**Triggers:** "give me strategy for {NPC}" • "how would {NPC} actually play this" • "I need a dossier for {antagonist}" • `/gm-strategy-doc`

**Use when:** A specific named antagonist needs deep strategic thinking before the session.

---

#### `gm-handout` — in-world artifact + GM wrapper

Output mirrors `toee/notes/handouts/04_kelno_unsent_letter.md`: precision-tooled in-world text (letter / ledger / dispatch / map / journal page / posted notice) plus a GM wrapper covering where/when found, player-side reveals, GM-side reveals, theatrical timing notes, the late-callback line.

**Triggers:** "I need a handout for {beat}" • "write {NPC}'s letter to {recipient}" • "draft a {ledger/map/dispatch}" • `/gm-handout`

**Use when:** You need a physical artifact the party can find on a body, behind a book, or pinned to a notice board.

---

#### `gm-npc-build` — single NPC dossier

Output is the Kostadis name+tic+anchor pattern (Eden "Gleeful" Gleeson + manservant with eyepatch and teddy bear). Smaller scope than `gm-strategy-doc` — for NPCs who need to exist now but may or may not graduate to recurring importance.

**Triggers:** "I need an NPC for {role/place}" • "build me an innkeeper" • "give me a {merchant/captain/fence}" • `/gm-npc-build`

**Use when:** A new NPC needs to be in the world. If they later prove plot-relevant, promote them to a strategy doc.

---

### At-the-table cluster

#### `gm-improv` — mid-session escape hatch

Three options for *what happens next* when the party goes off-script. Each honors the swerve (no railroading back), has one comedic-and-material consequence baked in, leaves a hook the GM can follow. Total output under 200 words, no doc written.

**Triggers:** "the party just did X, what now" • "they went off-rails" • "I didn't prep for this" • `/gm-improv`

**Use when:** The session is going somewhere you didn't prepare for and you need three options in the next 30 seconds.

---

#### `gm-npc-voice` — mid-session voice grab

Three verbatim lines + one tic + one thing the NPC would never say + one physical accompaniment. Total output under 150 words.

**Triggers:** "voice {NPC} for me" • "I'm about to play {NPC}" • "what does {NPC} sound like" • `/gm-npc-voice`

**Use when:** You're about to play an NPC in 30 seconds and need their voice in your ear.

---

### Mechanics & social-encounter cluster

#### `gm-statblock` — 5e stat blocks (the only lit-RPG skill)

Three modes: **convert** legacy edition (1e/2e/3.x/4e) to 5e via a 5e canonical chassis; **reflavor** an existing 5e block to a new theme (e.g. cleric → water cleric of Imix) preserving math; **build** from scratch at a target CR. Two output sizes: **quick** (essentials for mid-session) and **full** (with lair actions, treasure, tactics, CR calibration).

**The cardinal rule:** preserve the math, change the flavor. Every reflavored ability is annotated with its underlying 5e source (e.g., *"Tidal Mercy (reflavored Cure Wounds, 1st level)"*) so edge cases can be adjudicated at the table.

**Triggers:** "give me a stat block for {NPC}" • "convert {NPC} to 5e" • "reflavor {block} as a {theme}" • "I need a CR-N statblock" • `/gm-statblock`

**Use when:** You need a *playable* creature. Unlike the prose-prep skills which deliberately suppress mechanics, this one is mechanical by design.

---

#### `gm-social-encounter` — wraps the flexai-social tool

Bridges the local `flexai-social` Flask app (`~/src/mytools/flexai-social/`, port 5105) to in-character narration. Auto-picks Social Role × Role Size × Social Context from campaign state, calls the API for NPC-turn rolls and result resolution, translates raw mechanical results ("Answers Grudgingly d100=47") into in-character behavior in the NPC's voice. Multi-turn — maintains continuity across the conversational volley.

**Solves:** "the party captured Orc #3 and wants to interrogate him" and "the party wants to question the rescued prisoners."

**Triggers:** "the party wants to interrogate {captive}" • "they're questioning the prisoners" • "make this conversation not boring" • `/gm-social-encounter`

**Two modes:**
- **Tool running** — calls `localhost:5105` for authoritative DCs and result tables (requires commercial FlexAI xlsx data files at the configured path).
- **Tool cold** — uses the rules framework from `RULES.md` and simulates rolls with `$RANDOM`. Less authoritative but produces the right *shape* of varied results.

**Known data gap:** the FlexAI DC workbook ships without Acquaintance DCs — skill falls back to Opponent/Bystander DCs and warns.

---

### Canon & campaign-record cluster

#### `gm-module-inventory` — canonical proper-noun registry for a module

Builds `docs/background/<module-name>-inventory.md`: every NPC, deity, location, plane, item/spell, faction/title, and event/concept in a published module, with canonical spelling. Sources from a 5etools source ID (preferred) or a module markdown file; per-chapter extraction agents, then a deterministic merge/dedup. Format matches the bundled `example-module-inventory.md`.

**Triggers:** "build an inventory for {module}" • "create a proper-noun list for {module}" • "canonical name list for {module}" • `/gm-module-inventory <module-name> [source]`

**Use when:** You want ground truth for names and spelling to hand to any LLM or tool, so hallucinated variants don't propagate.

---

#### `gm-quest-log` — player-facing quest log

Every open promise, contract, errand, and personal thread the *party* knows about, written in the voice of a party member who keeps notes. Rebuilt from session summaries, oldest to newest — the grounding docs are a cross-check only, because they run stale. Player knowledge only: never module trackers, dossiers, or GM secrets. Written next to the campaign's existing player handouts as a new `{author}-{session}-log.md`.

**Triggers:** "what quests do the players have open" • "make a quest list" • "player-facing quest log" • "what are the party's open threads" • `/gm-quest-log`

**Use when:** You want something you can hand straight to the players.

---

### Post-session cluster

#### `gm-voice-reconstruction` — PC dialogue against voice files

Rewrites each PC's verbatim quote blocks in a session's `scene_extractions_new/` toward their `voice/<character>_voice.md` register: strips filler, collapses false starts, invents nothing. A renderer, not an architect — no re-scoping, re-attribution, or re-ordering. Produces a human review table first; files are replaced in place only after explicit approval. Run `/session-summary-consistency` before it.

**Triggers:** "voice reconstruct the scenes" • "clean up the dialogue against the voice files" • "apply voice files to scene extractions" • `/gm-voice-reconstruction`

**Use when:** A session's scene extractions are VTT-clean but the PCs don't yet sound like themselves. One session directory at a time.

---

## Design notes shared across all skills

- **Campaign isolation.** Every skill refuses to operate outside one of the campaign subdirs (`Phandalin/`, `out-of-the-abyss/`, `Hillsfar/`, `toee/`, or a future sibling) — see the repo-root `CLAUDE.md` for the isolation rule.
- **Fanfic-not-lit-RPG by default.** Prose-prep skills suppress mechanical stat blocks unless asked. `gm-statblock` is the explicit exception.
- **1x1 questioning.** Each skill uses `AskUserQuestion` one question at a time, not in batches.
- **Output shape pinned to v2 ToEE examples.** Every prep skill points at a specific file under `toee/notes/` as its template. The skills are calibrated against *known-good* outputs, not against abstract style guidance.
- **Inline style notes per skill, not a separate style sheet.** The `finished-gm.md` profile is reference, not auto-loaded. Each skill inlines the 3-5 style bullets it needs.

---

## Extending the family

If a new GM workflow recurs enough to write down, write it as a skill. The prep and at-the-table skills share this pattern; the newer clusters follow it loosely:

```yaml
---
name: gm-<name>
description: <when to invoke + what it produces — this doubles as the trigger doc>
---

# gm-<name>

## When to invoke
- trigger phrases

## Inputs to confirm (one at a time, via AskUserQuestion)
1. ...

## Required context (read in this order)
1. ...

## Style notes for this output
- 3-5 inline bullets

## Output shape
{template}

## Steps
1. ...

## What this skill is NOT for
- (cross-reference to sibling skills)
```

Add the new skill to this index so the roster stays canonical.
