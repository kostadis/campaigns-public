---
name: gm-npc-build
description: Build a single NPC dossier in the Kostadis name+tic+anchor pattern (Eden "Gleeful" Gleeson + manservant with eyepatch and teddy bear). Smaller scope than gm-strategy-doc — this is for new NPCs who need to exist, not for working through the play of an established antagonist. Invoke when the user says "I need an NPC for {role/place}", "build me an innkeeper", "give me a {merchant/captain/fence/etc}", "/gm-npc-build". Output is a short dossier suitable for docs/npcs/ that can be promoted to a strategy doc later if the NPC matters.
---

# gm-npc-build

Generates a single NPC in the recognizable house pattern: **strong name + one defining tic + one anchor (visible detail / companion / possession that makes them recognizable on sight)**. This is *not* a strategy doc — it's an NPC who exists to fill a role and may or may not graduate to recurring importance.

## When to invoke

Trigger phrases:
- "I need an NPC for {role/place}"
- "build me a {innkeeper/captain/fence/merchant/etc}"
- "give me a name and a face for {scene}"
- "I need someone to deliver this message"
- "/gm-npc-build"

## Inputs to confirm (one at a time, via AskUserQuestion)

1. **Role.** What do they *do* in the world? Innkeeper, town guard captain, smuggler, scholar, etc. Required.
2. **Where they sit.** Which town, dungeon, level, faction. Required.
3. **What the party will likely use them for.** Information source? Obstacle? Ally? Comic relief? Future antagonist? This determines how much depth to give them. A one-scene innkeeper needs less than someone the party will encounter repeatedly.
4. **Vibe / register hint.** Optional. "I want them slightly off-putting," "I want them sympathetic," "I want a comic foil." If the user passes, default to whatever fits the campaign's current tone.

## Required context (read in this order)

1. `docs/world_state.md` — to know which faction landscape they sit in
2. `docs/campaign_state.md` — to know what's happening this week
3. Any existing NPCs under `docs/npcs/` from the same town/region — read 2-3 to match local naming conventions. Don't duplicate. Don't accidentally name them the same as someone else.
4. `docs/background/` — for any setting-specific naming or vocabulary conventions
5. Recent session summaries that touch the location — what's the current vibe of the place?

## Style notes for this output

The signature pattern is **name + tic + anchor**. Each piece has to land independently.

- **Name.** Memorable, evocative, often containing an epithet or a sound-pun. Examples from the source corpus: Eden "Gleeful" Gleeson, Aunt Nonnie, Mama Manyknuckles, Diego Malfoy, Sir Torvel Hawkes, Madame Selentis. Avoid generic fantasy compound names ("Stormwind", "Ironhelm") unless there's a reason. Mix registers — Greyhawk/FR canon names alongside puns alongside real-world cribs (Diego Malfoy) — Kostadis does this freely.
- **Tic.** *One specific thing they do, want, or worry about.* Not a personality summary. Examples: forgot his bride's wedding gift; obsessed with the "best presentation award"; insistent on the "Aunt"; haggling for sport. The tic is what makes the GM remember how to play them next time.
- **Anchor.** A visible detail, companion, or possession that locks them in the GM's mind. Cisco the manservant with the eyepatch and teddy bear. The pristine pressed shirt in a peasant town. The two lanterns lit only when a convoy is incoming. The anchor is what the player describes when they re-encounter the NPC two months later.
- **One quote canon.** A single line the GM can lift verbatim that captures their voice. Three sentences max.
- **What they want from any interaction.** One sentence. Their default motive when the party walks in.
- **What they would never do.** One sentence. The boundary of their character.
- **Modern register is allowed.** Diego Malfoy is a fine name. Don't gatekeep.
- **Mechanical stats omitted by default.** If the user asks "what's their stat block?" point to a published-canon equivalent or leave a `Stat: ___ ` placeholder for them to fill in.

## Output shape

NPC dossiers in this workspace go into `docs/npcs/<slug>.md`. Canonical structure:

```
# {Full Name with epithet if any}

**Role:** {what they do}
**Location:** {where they live or work}
**Faction:** {if any — Harpers, Cult, Iron Circle, no faction, etc.}
**First seen:** {session date / chapter # / "not yet" if pre-introduction}

## Look
{Two sentences. The anchor detail goes here. Visual + one sensory cue (smell of
pipe smoke, sound of a coin-flick, etc.).}

## Tic
{One sentence. The single thing they do or want that the GM will use to re-find
the character mid-session.}

## What they want from any interaction
{One sentence default motive.}

## What they would never do
{One sentence. The boundary.}

## Voice
- *"{verbatim line — captures cadence.}"*
- *"{verbatim line — different emotional register.}"*

## What the party knows about them
{Bulleted. Mark [KNOWN] [SUSPECTED] [GM-ONLY] for anything non-public.}

## Notes for the GM
- {Anything load-bearing: a future plot lever, a reason they might be promoted to
  a strategy doc, a connection to another NPC.}
- {Optional: a single line of "if the players try to {X}, {they respond Y}".}

## Open decisions (for the user)
- {Names, factions, or motivations the user hasn't pinned down yet.}
```

## Steps

1. Read 2-3 existing NPC dossiers from the same town to match conventions and check for name collisions.
2. Ask the 1-4 inputs the user hasn't supplied, one at a time.
3. Propose **3 candidate names** before settling — names are sticky, and the user should pick one. Use AskUserQuestion for the choice if the role matters; just pick if it's a one-scene throwaway.
4. Draft the dossier to `docs/npcs/<slug>.md`. Use the slug form `firstname-lastname` or `epithet-name`.
5. Open with the proposed name + a one-sentence pitch ("This is your innkeeper — she's a former smuggler hiding from her past, and she runs the place because the previous owner owed her money") so the user can redirect before you commit.
6. Produce the dossier.

## What this skill is NOT for

- A full strategy dossier for a major recurring antagonist (use `gm-strategy-doc`)
- An operational map of a town (use `gm-faction-network`)
- A handout the NPC wrote (use `gm-handout`)
- Mid-session voice grab (use `gm-npc-voice`)
