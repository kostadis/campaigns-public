---
name: gm-handout
description: Produce an in-world handout (letter, ledger, dispatch, map text, journal page, posted notice) plus a GM wrapper explaining who wrote it, when/where the party finds it, what it reveals player-side, what it reveals GM-side, and theatrical timing notes. Style is toee/notes/handouts/04_kelno_unsent_letter.md — the in-fiction text is precision-tooled, the GM wrapper is operational. Invoke when the user says "I need a handout for {beat}", "write {NPC}'s letter to {recipient}", "draft a {ledger/map/dispatch/notice}", "/gm-handout". The output goes to notes/handouts/.
---

# gm-handout

Produces an in-world artifact the party can find, plus a GM wrapper explaining how it lands. Canonical example: `toee/notes/handouts/04_kelno_unsent_letter.md` — a single letter that recontextualizes a major NPC and creates branching emotional consequences based on *when* the party reads it.

## When to invoke

Trigger phrases:
- "I need a handout for {beat}"
- "write {NPC}'s letter to {recipient}"
- "draft a {ledger/map/dispatch/notice/journal page}"
- "I want something the party can find on the body"
- "/gm-handout"

## Inputs to confirm (one at a time, via AskUserQuestion)

1. **Type.** Letter? Ledger? Map text? Dispatch? Posted notice? Journal page? Torn page? The type drives the voice — a ledger is dry, a letter is intimate, a dispatch is curt.
2. **Author.** Who wrote it? The handout's voice is *theirs*, not the GM's. If the author already has a strategy doc or NPC dossier, read it first.
3. **Recipient or audience.** Letters need a recipient (often dead, often estranged — see Kelno). Notices need an audience. Ledgers can be self-addressed.
4. **What it reveals, and what it conceals.** A good handout is *one* clear reveal that *recontextualizes* something the party already half-knows. Not a dump. Ask the user: "what should the party walk away knowing they didn't know before?"
5. **When/where the party finds it.** On the body. Tucked behind a book. Pinned to a notice board. Sealed in wax. The discovery framing changes everything.
6. **Active or passive discovery?** Does the NPC hand it over, or does the party have to search? Passive discovery (the party has to look) is almost always richer.

## Required context (read in this order)

1. Author's dossier under `docs/npcs/` and any `notes/{npc}_strategy.md`
2. `docs/campaign_state.md` for the current moment
3. Recent session summaries — especially any scene where the author has appeared
4. `docs/background/` for vocabulary and naming conventions specific to this campaign's setting
5. Sibling handouts under `notes/handouts/` — read the README if present; match the existing format and naming convention

## Style notes for this output

Two distinct voices in one file: the *in-world text* and the *GM wrapper*. Don't blend them.

**For the in-world text:**

- **The author's voice is everything.** Cadence, vocabulary, what they would and would never write. If they're a bureaucrat, the letter reads like a memo. If they're a grieving administrator (Kelno), it reads like late-night Marcus Aurelius. If they're a teenage cult acolyte, it's breathless.
- **Constrained line length, monospace presentation.** In-world artifacts read better as fixed-width text inside a code block — the visual artifact effect is part of the impact.
- **In-world dates, in-world geography, in-world idioms.** Use Greyhawk's "Plant 6, 579" or Faerûn's "3rd day of the 1st tenday of Taraskh." Mention places the author would know.
- **One clear emotional or factual reveal, plus texture.** The reveal is the spine; the texture (the apprentice's name, the dead gnoll, the count on the shelf) is what makes it land.
- **What the author would never say is what makes them real.** A letter that says everything explicitly is a letter the player will dismiss as exposition. Let them omit, hint, deflect.

**For the GM wrapper:**

- **Quoted-block (`>`) framing for all GM-only content** so the in-fiction artifact stays visually distinct.
- **GM context** at top: where/when found, who has access, what tone to use for read-aloud.
- **Player-side reveals**: bulleted, specific, "what this tells the party."
- **GM-side reveals**: bulleted, specific, "what this tells *the GM* about future plot levers."
- **Theatrical timing**: when to introduce it, when to leave silence, what *not* to fill. ("Leave the table silent for a beat. Don't fill the silence.")
- **The retroactive variant.** If the party finds it *after* killing the author, what does the discovery do to them? This is often the most powerful version.

## Output shape

Use `toee/notes/handouts/04_kelno_unsent_letter.md` as the template:

```
# HANDOUT — {short descriptive title}

> **GM context:** {Where the handout is. How the party finds it. Active or passive
> discovery. The tone for read-aloud — single sentence.}
>
> {Optional: a paragraph of who wrote it, when, why. Anchored to a date if relevant.}
>
> **Tone for read-aloud:** {one-sentence description of cadence and emotional register.}

---

```
{IN-WORLD TEXT IN A FENCED CODE BLOCK.

 Fixed-width, line-broken to roughly 60-65 chars wide.

 Signed at the end if it's a letter.}
```

---

> **What this reveals about {author} (player-side):**
>
> - **{Reveal 1}** — {one sentence + the exact quote that conveys it.}
> - **{Reveal 2}** — same shape.
> - **{Reveal 3}** — same shape.
> - **{The "small detail" reveal}** — the one piece of texture (a date, a name, a number) that lands harder than the explicit reveals.
>
> **What this reveals about {author} (GM-side):**
>
> - {The future-plot lever this opens up.}
> - {What the GM can do later because of this.}
> - **If {author} dies before/after the party finds this:** {the retroactive consequence.}

> **GM use:**
>
> - {When to introduce it.}
> - {When NOT to introduce it.}
> - {Silence cue if applicable.}
> - {The single line the author would say if asked about it later — verbatim. This
>   is the late callback the GM can pull.}
```

## Steps

1. Read author's dossier + recent summaries. Get the voice in your ear before you write a word.
2. Ask the 1-6 inputs the user hasn't supplied, one at a time.
3. Determine the next handout number by listing `notes/handouts/` — files are `NN_short-title.md`.
4. Draft the file. Open with a 2-3 sentence summary of how you're reading the author's voice so the user can catch a mis-read before the artifact is fixed in place.
5. Produce the handout in the structure above.
6. End the GM wrapper with the **single line the author would say if asked about it later** — this is what makes the artifact recurringly useful.

## What this skill is NOT for

- Player-facing canon docs (use the campaign's grounding-doc pipeline, not this)
- NPC dossier (use `gm-npc-build`)
- The whole session's prep (use `gm-session-prep`)
- A faction overview (use `gm-faction-network`)
