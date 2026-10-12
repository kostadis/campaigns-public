---
name: gm-strategy-doc
description: Build a per-antagonist strategic dossier in the style of toee/notes/hedrack_strategy.md or toee/notes/falrinth_strategy.md — motivations, the optimal play *for* this NPC, the optimal play *against* them, contingencies, what they reveal if cornered, what they do if the party offers a deal. Invoke when the user says "give me strategy for {NPC}", "how would {NPC} actually play this", "I need a dossier for {antagonist}", "/gm-strategy-doc". This is the NPC viewed from inside their own head. For multi-NPC operational maps, use gm-faction-network instead.
---

# gm-strategy-doc

Produces a strategic dossier for a single antagonist or named NPC. The canonical examples are `toee/notes/hedrack_strategy.md` (the campaign-level five-faction landscape from Hedrack's POV) and `toee/notes/falrinth_strategy.md` (the Lolth-thread operator). This is **the NPC viewed from inside their own head** — what they want, how they'd actually play their hand, what they'll concede, what they'll never give up.

## When to invoke

Trigger phrases:
- "give me strategy for {NPC}"
- "how would {NPC} actually play this"
- "I need a dossier for {antagonist}"
- "what's {NPC} doing in the background"
- "/gm-strategy-doc"

Refuse if the working directory isn't a campaign subdir.

## Inputs to confirm (one at a time, via AskUserQuestion)

1. **Who.** The NPC's name. Required.
2. **Where they sit in the campaign right now.** One sentence. ("Hidden in the Greater Temple", "running Nulb logistics", "negotiating with the Seelie court.") If unknown, the skill will derive from docs.
3. **What's their current pressure?** What is *forcing them to act* in the near term? (A debt, a rival, a deadline, a wound.) If unknown, propose 1-2 candidate pressures the user can pick.
4. **Have they met the party?** Yes/no/indirectly. This determines whether the dossier covers a first-meeting scene or a continuation.

## Required context (read in this order)

1. The NPC's dossier under `docs/npcs/` if one exists. Read fully.
2. `docs/campaign_state.md` — for current state
3. `docs/world_state.md` — for faction context
4. `docs/party_state.md` — to know what the NPC would know about the PCs
5. Any session summary where this NPC appeared (search `summaries/` for the name)
6. `docs/background/` — for source-canon details if relevant
7. Sibling strategy/network docs already produced for adjacent NPCs (`notes/*_strategy.md`, `notes/*_network.md`) — link them rather than re-derive

## Style notes for this output

- **The NPC is the protagonist of their own story.** Write from inside their head. They are not "the villain"; they are a person with goals, fears, and a plan that makes sense from their seat.
- **The optimal play *for them* is the spine of the doc.** What would they do if the GM played them as smart as their stat sheet says they are? Spell it out so the GM can either play it (and the party feels the threat) or *choose to soften it* (and the party gets a win).
- **The optimal play *against them* is the GM's hidden map.** Same logic from the other side — what's the party's actual best move, even if they don't know it yet?
- **Contingencies, branching.** What does the NPC do if X happens? If Y? If they're cornered? Give the GM a decision tree.
- **What they'll concede vs what they'll never give up.** This is the negotiation core. A villain who'd surrender everything for the right deal is different from one who'd die first.
- **Voice samples.** 3-5 lines the GM can lift verbatim. Capture the speech rhythm and the recurring tic. Like the Kelno letter's monastic-bitter cadence.
- **Their secret.** What does this NPC know that nobody else in the campaign knows? (Kelno: no actual divine power. Selentis: real noble identity.) The secret is the lever.
- **No mechanical stat blocks.** If the user needs stats, they're in the published module or in `docs/npcs/`. The strategy doc is *thinking*, not stats.

## Output shape

Use `toee/notes/hedrack_strategy.md` or `toee/notes/falrinth_strategy.md` as the template. Canonical structure:

```
# {NPC name} — Strategy Doc

GM-only working doc. Updated as of {date stamp}.

## The Frame ({NPC} from inside their own head)
{2-3 paragraphs in close third-person. What do they want, what do they fear, what
do they think is happening right now. Not from the GM's perspective — from theirs.}

## Their Current Position
- {Bullet points: where they are, who's around them, what's the pressure.}

## Their Secret
{The one thing they know that no one else in the campaign knows. The lever. GM-only.}

## The Optimal Play (For Them)
{Numbered. What would they do this week if the GM played them as smart as they are?
Walk through the plan they would execute in the background.}

## The Optimal Play (Against Them)
{Numbered. What's the party's actual best path? The GM should know this so they can
nudge — not so the GM railroads, but so the GM recognizes when the party stumbles
onto it and can give it weight.}

## Negotiation Stances
- **Concedes:** {what they'll give up to keep their life or their core goal.}
- **Trades:** {what they'll exchange for what.}
- **Never gives up:** {what's load-bearing for them.}

## Contingencies
- **If the party {does X}:** {response.}
- **If {rival Y} moves first:** {response.}
- **If cornered with no exit:** {response.}

## Voice samples
- *"{verbatim line — capture cadence and tic.}"*
- *"{another — different emotional register.}"*
- *"{a line they would never say — the boundary of their voice.}"*

## What they would never say
{One short paragraph. Lines that would break character. Helpful for the GM when
improvising mid-session.}

## Cross-references
- See {sibling strategy doc} for the rival/ally angle.
- See {network doc} for the operational picture they sit inside.

## Open decisions (for the user)
- {Things the docs don't determine that the GM needs to settle.}
```

## Steps

1. Read the NPC's dossier and the docs in the order above.
2. Ask the 1-4 inputs the user hasn't supplied, one at a time.
3. Draft to `notes/{npc-slug}_strategy.md`.
4. Open with a 2-3 sentence summary of how you're reading this NPC — let the user catch you if you've got them wrong.
5. Produce the dossier.
6. End with **Open decisions** and **Cross-references**.

## What this skill is NOT for

- Multi-NPC operational map of a location (use `gm-faction-network`)
- A brand-new NPC who doesn't yet have a dossier (use `gm-npc-build` first, then this skill once they have a role)
- Player-facing rumors about the NPC (use `gm-handout`)
- Mid-session voice for the NPC (use `gm-npc-voice`)
