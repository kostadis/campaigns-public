---
name: gm-statblock
description: Generate or convert a 5e stat block, with optional re-flavoring (theme / cult / element / faction) that PRESERVES the underlying math. Three modes — (a) convert a legacy-edition block (1e/2e/3.x/4e) to 5e using published 5e creatures as the math chassis; (b) re-flavor an existing 5e block to a new theme (e.g. cleric → water cleric, where spells are renamed and re-described but mechanically unchanged); (c) build from scratch at a target CR. Also supports a quick mode (essentials only, mid-session) and a full mode (with lair actions, treasure, tactical notes). Invoke when the user says "give me a stat block for X", "convert X to 5e", "reflavor Y as a Z", "I need a CR-N statblock for X", "/gm-statblock". Unlike the other gm- skills, this one IS lit-RPG mechanical — real numbers, real action economy.
---

# gm-statblock

The mechanics-bearing sibling of the prose-prep skills. The other gm-* skills deliberately omit stat blocks; this one is where they live. Use this skill when the user needs a *playable* creature at the table — accurate 5e math, dressed in the right flavor.

## When to invoke

Trigger phrases:
- "give me a stat block for {NPC}"
- "convert {NPC / module monster} to 5e"
- "reflavor {existing block} as a {water/fire/fey/undead/etc} {role}"
- "I need a CR-{N} statblock for {role}"
- "what's {NPC}'s stat block"
- "/gm-statblock"

If the user wants the NPC's *personality, plan, voice* — that's `gm-strategy-doc` or `gm-npc-build`. This skill is mechanics only.

## Inputs to confirm (one at a time, via AskUserQuestion)

Skip any input the user already supplied in the invocation.

1. **Mode.** One of:
   - **Convert** — there's an existing block in a legacy edition (1e/2e/3.x/4e). User points to the source.
   - **Reflavor** — there's an existing 5e block. User says what theme to re-skin it as.
   - **Build** — no source; build from scratch at a target CR for a specific role.
2. **The source / target.**
   - Convert mode: which legacy block? (e.g. "Belsornig from 1e ToEE", "the canon Mordrammo block")
   - Reflavor mode: which 5e block? (e.g. "Priest", "Cult Fanatic", "Acolyte", "Cleric of the Tempest Domain") — and what theme? ("Water cleric of Imix", "Lolth-touched drow priestess", "Fey emissary")
   - Build mode: what role? ("Town watch sergeant", "river-bandit captain") and what CR target?
3. **CR target.** The party's level matters more than the block's "canonical" CR — a 1e Belsornig was challenging in 1e math but trivial at 5e level 15. Ask the user what CR they need for *their* party. Default: derive from `docs/party_state.md` and pick a CR that makes this a single-creature credible threat or a mook depending on role.
4. **Quick mode or full mode?**
   - **Quick** — just AC, HP, speed, ability scores, attacks, key traits. ~30 second read. For mid-session use.
   - **Full** — quick mode PLUS reactions, lair actions if a leader, tactical notes, treasure, "how they actually fight."
5. **Solo encounter or part of a group?** Affects HP target (solo creatures need ~3× HP) and whether to give them legendary resistances or escape mechanics.

## Required context (read in this order)

1. The NPC's existing dossier under `docs/npcs/` if any
2. Any sibling strategy doc `notes/{npc}_strategy.md` — affects tactical notes
3. `docs/party_state.md` — to size the CR correctly
4. `docs/background/` and any published-module source — for the legacy block if Convert mode
5. **5etools MCP if configured** — use `get_section` or `search` to pull canonical 5e base stat blocks to use as the math chassis. Don't paraphrase from memory; look up the actual block.
6. Existing reflavored blocks under `notes/` for naming conventions specific to this campaign

If 5etools MCP isn't available, fall back to: use the canonical 5e block from the SRD or Monster Manual that best matches the role + CR target, and note the source in a comment.

## The cardinal rule: preserve the math, change the flavor

When **re-flavoring**, every mechanical effect must come from a real 5e ability (spell, attack, trait). Do not invent. The re-flavor changes:

- **The ability's *name*** (e.g., *Cure Wounds* → *Tidal Mercy*).
- **The ability's *description*** in the stat block (replace fire imagery with water imagery, replace "divine light" with "cold currents," etc.).
- **The damage *type*** ONLY if you swap one type for another of equivalent rules-impact (fire ↔ cold is usually fine; fire → necrotic is not — necrotic is far less commonly resisted than fire, so this would change power).
- **The save / attack** stays the same. DCs unchanged. Save type unchanged unless you're explicitly tuning.

When **converting** legacy → 5e, the math is *built fresh from 5e canon*, not arithmetically translated. A 1e block does not have a 5e math equivalent — pick the closest 5e canonical block, re-skin it, adjust HP/AC ±10% if needed for tone.

**Mark every reflavored ability with its underlying 5e source** in the stat block, so the GM can adjudicate edge cases at the table:

```
- ***Tidal Mercy*** *(reflavored Cure Wounds, 1st level)*. The priest gestures, and
  a coil of cold seawater envelops the target, knitting their wounds.
  One creature the priest can touch regains hit points = 1d8 + 3.
```

The italic parenthetical line is the GM's reference. Don't omit it.

## Damage-type swaps that are safe vs unsafe

Use this table when re-flavoring elemental abilities.

| Original | Safe swap | Risky swap | Why |
|---|---|---|---|
| Fire | Cold, lightning, thunder | Necrotic, radiant, psychic | Necrotic/radiant/psychic are far less commonly resisted; you'd be buffing the creature. |
| Cold | Fire, lightning, thunder | Necrotic | Same. |
| Acid | Poison, force | — | Acid and poison are similarly common; force is rare-resist (slight buff, often acceptable). |
| Slashing/Piercing/Bludgeoning | Each other | Don't swap to non-physical without recalibration | Resistance to non-magical physical is common; abilities that bypass that change in value. |

When in doubt, *keep the damage type* and only change the *description*. ("The Tidal Mace is treated as a magical bludgeoning weapon that strikes with the weight of compressed water" — still bludgeoning, no math impact.)

## Style notes specific to this skill

- **5e formatting conventions.** Use the standard 5e stat block format. Italicized trait names, bolded action names, parenthetical roll formulas (e.g., `(1d8 + 4)`), `DC N {Stat} saving throw`, `+N to hit, reach 5 ft., one target`, etc.
- **Flavor in the descriptions, not in the stat line.** AC 18, HP 102, Speed 30 ft. — these are the same regardless of theme. The flavor lives in the trait/action *text*.
- **Tactical notes belong at the bottom in full mode.** A short "How this creature fights" paragraph. Belsornig should fight differently from a generic priest — he's a tired administrator who breaks for the door if the fight goes wrong, not a fanatic who dies in place. *That* is the GM's at-the-table currency.
- **Lair actions only for tier-4 leaders or boss creatures.** Don't proliferate them.
- **Spell lists go in a single paragraph block**, not in a table. Group by level. Mark reflavored names with the underlying spell in italics.
- **CR sanity-check at the end.** State: "intended CR {N}, calibrated for a party of {level}, {composition}. Expected outcome: {tough fight / mook / boss with retreat option}."

## Output shape

For **quick mode** (mid-session):

```
**{Name}** — {one-line concept: "Tired water-cult administrator, level-7 cleric chassis"}

**AC** {N} ({source}) | **HP** {N} ({avg}) | **Speed** {N} ft.
**STR** {N} ({mod}) **DEX** {N} ({mod}) **CON** {N} ({mod}) **INT** {N} ({mod}) **WIS** {N} ({mod}) **CHA** {N} ({mod})
**Saves:** {as relevant}
**Skills:** {as relevant}
**Senses:** {passive Perception, darkvision, etc.}
**Languages:** {as relevant}
**CR** {N} ({XP} XP)

***{Trait name}*** *(reflavored {underlying}, if applicable)*. {Short description.}

**Actions**

***Multiattack.*** {Description.}

***{Attack name}.*** *(Melee/Ranged Weapon Attack):* +{N} to hit, reach {N} ft., one target. *Hit:* {N} ({dice}) {damage type} damage.

***{Spell-cast / spell-like ability}.*** *(reflavored {underlying spell}, {level} level slot)*. {Short description.} {Effect line.}

***{1-2 more actions as needed.}***

**How they fight:** {2-3 sentences. Their tactical preference. When they break and run.}
```

For **full mode**, add after the quick block:

```
**Reactions**

***{Reaction name}.*** *(reflavored {underlying}, if applicable)*. {Trigger.} {Effect.}

**Spellcasting (Spell Slots: {1st-1 2nd-2 3rd-3 ...})**

The {creature} is a {level} caster. Spellcasting ability is {Stat} (spell save DC {N}, +{N} to hit with spell attacks).

- **Cantrips:** *{Spellname 1}* (reflavored *X*), *{Spellname 2}* (reflavored *Y*), ...
- **1st level ({N} slots):** *...*
- **2nd level ({N} slots):** *...*
- **{etc}**

**Lair Actions** *(only if leader / boss / has a defended area)*

On initiative count 20, the {creature} can take one of the following lair actions; it cannot use the same lair action two rounds in a row.

- {Action 1.}
- {Action 2.}
- {Action 3.}

**Tactics**

{1-2 paragraphs. How this creature actually plays the fight. Opening move, mid-fight pivot, escape condition. The "when they break and run" line is load-bearing.}

**Treasure**

{What's on the body if they die. Tied to the campaign — Kelno-style "the dagger of venom he was saving for one of his rivals" is the kind of specificity that matters.}

**CR calibration**

Intended CR {N}, sized for a party of {level} ({N} PCs of {classes}). Expected outcome: {brief}.

**Source / chassis**

This block uses {published 5e block, e.g., "Priest (MM p348)"} as its mathematical chassis, reflavored as {theme}. Spell list adjusted: {what changed}.
```

## Steps

1. Resolve mode + source + target via AskUserQuestion 1x1.
2. Read the NPC's dossier + party_state.md + 5etools chassis (via MCP if available).
3. Pick the underlying 5e canonical block and state it explicitly to the user before producing the block — give them a chance to redirect. ("I'm going to use *Priest (MM p348)* as the chassis for Belsornig, reflavored as a water cleric of Imix. Sound right, or would you prefer *Cleric of the Tempest Domain* or a custom build?")
4. Once chassis is confirmed, produce the stat block in the requested mode.
5. Save the result depending on context:
   - Quick mode mid-session: just print to chat; do not file.
   - Full mode beforehand: save to `notes/statblocks/{npc-slug}.md` (create the dir if needed).
6. End with the CR calibration line and source/chassis line, so the user can re-derive at the table if something feels off.

## Common pitfalls to avoid

- **Don't reflavor by inventing.** If you can't find a 5e ability that does what the legacy block did, name a *close* 5e ability and note the gap explicitly. Tell the user: "the 1e block had X, the closest 5e equivalent is Y, here's the difference."
- **Don't scale by arithmetic.** A 1e CR-6 is not a 5e CR-6. Pick the right *5e* CR for the party, not the legacy CR.
- **Don't pad with flavor in the stat line.** *"Tidal Mace (cool-looking, glows with seawater) — +7 to hit, …"* is wrong. Flavor lives in trait/action descriptions, not action headers.
- **Don't omit the underlying-mechanic parenthetical.** The GM will adjudicate edge cases at the table and needs to know what spell/ability they're really calling.
- **Don't add lair actions or legendary actions to a non-boss.** Inflation kills the framework.

## What this skill is NOT for

- The NPC's motivations, voice, or strategic plan (use `gm-strategy-doc` or `gm-npc-build`)
- A faction overview (use `gm-faction-network`)
- A handout the NPC wrote (use `gm-handout`)
- Pre-session prep at the scene-design level (use `gm-session-prep`)
- Mid-session voice grab (use `gm-npc-voice`)
- Mid-session "what should happen next" (use `gm-improv`)
