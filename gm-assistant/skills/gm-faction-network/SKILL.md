---
name: gm-faction-network
description: Build an operational map of a place — factions, real-vs-cover identities, supply chains, what-the-party-knows-vs-what-the-GM-knows — in the style of toee/notes/nulb_network.md. Invoke when the user says "map the factions in {place}", "give me the network for {town}", "/gm-faction-network", "who's really running {place}". This is GM-only operational intel, not a player handout. Use this when a single location has multiple competing intrigues the GM needs to keep straight; for a single antagonist's strategy, use gm-strategy-doc instead.
---

# gm-faction-network

Produces a GM-only operational map of a location — the canonical example is `toee/notes/nulb_network.md`. Treats the place as a layered system: who *appears* to run it, who *actually* runs it, the supply chain, the chain of command, the cover stories, the gaps the party can exploit.

## When to invoke

Trigger phrases:
- "map the factions in {place}"
- "give me the network for {town/region}"
- "who's really running {place}"
- "show me the operational picture for {place}"
- "/gm-faction-network"

Refuse politely if the working directory is not inside a campaign subdir. Campaign-scoped — see `campaigns/CLAUDE.md`.

## Inputs to confirm (one at a time, via AskUserQuestion)

1. **The place.** Town, neighborhood, dungeon level, region. Single locale, not "the whole continent."
2. **What the party already knows.** Critical. The doc must distinguish *known* from *suspected* from *GM-only*. The user may say "they know X but not Y" — capture it.
3. **The principal antagonist** running this place, if known. Hedrack for Nulb, Iymrith for the desert, etc. If the user doesn't know yet, that's OK — the doc can include "the actual top dog is TBD."
4. **Scope.** A single locale (~5-15 named entities) is the sweet spot. If the user asks for "the whole northern alliance," push back — that's too big; offer to do it as nested per-locale docs.

## Required context (read in this order)

1. `docs/campaign_state.md` — campaign-level current state
2. `docs/world_state.md` — for factions that exist at world level
3. `docs/npcs/` — any NPC dossier matching the place. Read all that are relevant.
4. Recent session summaries that mention the place (search `summaries/` for the place name)
5. `docs/background/` — any source-material doc covering the location
6. The published-module section if 5etools MCP is configured — use that for canon area numbers and stat blocks, don't paraphrase

Do not invent identities. If a "real name behind the cover" doesn't exist in the docs, ask the user to decide it.

## Style notes for this output

- **Layer the place.** Surface ("what the party sees") → middle ("the locals' open secrets") → operational ("the actual machinery") → deepest ("the unwritten facts only the principal antagonist knows").
- **Real names vs cover names are always paired.** "Madame Selentis — Real Name Lady Nysera Krivaltis" — both, in the heading.
- **Supply chains are diagrams.** When goods or people move through the place, draw the path in an ASCII flowchart (river → tavern cellar → manor → cottage → tunnel). This is signature for this output shape.
- **Quote canon for each principal NPC.** A one-line line of dialogue that captures who they are — the GM can lift it verbatim. Example: *"Order is a story we tell the frightened. I sell the ending."*
- **What-the-party-knows is a section, not an afterthought.** Mark every piece of intel with one of: `[KNOWN]`, `[SUSPECTED]`, `[GM-ONLY]`. The party's information state is *the gap the GM exploits to introduce NPCs credibly*.
- **Cross-reference sibling docs.** "See also: hedrack_strategy.md for the campaign-level five-faction landscape." Skills compose.
- **No stat blocks unless the NPC has a published one and it matters.** Then a one-liner: "Captain Krael Vortash — Bandit Captain stat block." Not the full table.

## Output shape

Use `toee/notes/nulb_network.md` as the template. Canonical structure:

```
# {Place} Network — GM Reference

{One-paragraph framing: what this place is, why it matters, what the party has done here so far.}

See also: {related strategy docs and network docs}.

---

## The {Principal} Operation

### {Principal NPC} — {Real Name if cover identity}

{One-paragraph description: surface vs reality.}

**Origin canon:**
- {Where they came from. Use FR / Greyhawk lore if relevant.}
- {How they got installed here. Who protects them.}

**What they run:**
- {Bulleted list. Specific. Not "criminal stuff" — "smuggling, prisoner sorting, contraband supply routing."}

**Personality:** {2-3 sentences. Tic. What they do under pressure.}

**Quote canon:** *"{a line the GM can lift verbatim}"*

**What the party currently knows:** {paragraph. Mark items [KNOWN] [SUSPECTED] [GM-ONLY].}

### {Lieutenant 1 / 2 / 3 — same shape, shorter}

---

## The Supply Chain — {Antagonist}'s True Operation Here

{ASCII flowchart of how goods/people/information move.}

```
Source → Intake → Sort → Storage → Routing → Destination
```

### {Each named node}
- {Who runs the node, what happens there, what's vulnerable.}

---

## The Hidden Operators (good-aligned or rival factions)

{Same shape — name, role, what they want, what the party knows. These are the levers the party can pull. Often appear in a sibling doc — link rather than duplicate.}

---

## Gaps the GM can exploit
- {Specific moments when an NPC could plausibly enter the scene because of *what the party doesn't know*.}
- {The "Lucius introduces himself" gap is the prototype.}

## Open decisions (for the user)
- {Things the docs don't determine that the GM needs to settle.}
```

## Steps

1. Read the docs in the order above. Especially: every session summary that mentions the place.
2. Ask the 1-4 inputs the user hasn't supplied, one at a time.
3. Draft the doc to `notes/{place-slug}_network.md`.
4. Open with a 2-3 sentence summary of what you understood so the user can catch misreads.
5. Produce the doc.
6. End with **Open decisions** and **Cross-references** — link to sibling strategy/network docs.

## What this skill is NOT for

- A single antagonist's strategy (use `gm-strategy-doc`)
- A single NPC (use `gm-npc-build`)
- A player-facing rumor sheet (handout — use `gm-handout`)
- The entire campaign's faction picture (do it as multiple per-locale docs and a top-level strategy doc)
