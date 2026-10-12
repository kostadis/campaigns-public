---
name: gm-improv
description: Mid-session emergency improv. The party went off-script and the GM needs three plausible next moves in under 30 seconds of reading. Each option honors the swerve (no railroading back), has one comedic-and-material consequence baked in, and leaves a hook the GM can follow. Invoke when the user says "the party just did X, what now", "they went off-rails", "I didn't prep for this", "/gm-improv". This is a fast skill — short input, short output, no doc-writing.
---

# gm-improv

Mid-session escape hatch. The party did something unanticipated; the GM needs three plausible next moves *now*. The output is **terse, scannable in 20 seconds, no prep doc generated**.

## When to invoke

Trigger phrases:
- "the party just {X}, what now"
- "they went off-rails"
- "I didn't prep for this"
- "I need an emergency option"
- "improv me {beat}"
- "/gm-improv"

The skill assumes Claude is already pre-warmed with the campaign context (same Claude Code session that's been running). If it's a cold start, fall back: read `docs/campaign_state.md` and the most recent session summary, then proceed. Don't do a full doc-reading pass — the GM is waiting.

## Inputs to confirm (one at a time, via AskUserQuestion — but ONLY if not given)

1. **What just happened.** One sentence from the GM. ("They killed the NPC I needed alive." "They went into the wrong room." "They told the cult leader the truth." "The wizard wants to teleport away.") Required.
2. **Time pressure.** Is this real-time at the table (need answer in 30s), or "the session is paused and I have 2 minutes"? Adjust output length accordingly.

Default to *no other questions*. The user can correct mid-stream.

## Required context

Whatever is already loaded in this Claude Code session. If the campaign context isn't loaded:

- `docs/campaign_state.md` — current state, one fast read
- The most recent session summary under `summaries/` — one fast read

Do not read more. Speed matters more than completeness here. If you don't know something, name what you don't know in one of the three options.

## Style notes for this output

- **Three options, no more, no less.** Two feels stingy; four overwhelms. Three is the right number.
- **Each option honors the swerve.** No "the NPC actually didn't die" do-overs. Players' actions stand.
- **Each option has one comedic-and-material consequence.** A loss, a complication, a new NPC who shows up, a reputation shift. Not "they take damage."
- **Each option opens a hook, doesn't close one.** The GM should be able to follow any of the three into the next scene.
- **Variety across the three options.**
  - Option 1: the *natural consequence* — what would happen if the world reacts honestly.
  - Option 2: the *escalation* — someone or something with a stake responds bigger than expected.
  - Option 3: the *unexpected ally / unexpected cost* — a swerve from a direction the players weren't watching.
- **One line of NPC voice per option** if relevant. The GM can lift it verbatim.
- **No headings, no markdown structure, no "GM context."** Just three labeled options, each 3-5 sentences max. Total output under 200 words.

## Output shape

```
**Quick read:** {one sentence — what you understood happened.}

**1. {Natural-consequence label}.** {3-4 sentences. The world reacts honestly. One specific NPC name or place. End with the hook.}

**2. {Escalation label}.** {3-4 sentences. Someone reacts bigger. Comedic-and-material consequence baked in. End with the hook.}

**3. {Unexpected swerve label}.** {3-4 sentences. From a direction they weren't watching. Could be an ally appearing, could be a cost they didn't see coming. End with the hook.}

**Pick one (or steal from two) — your call.**
```

## Steps

1. Confirm what happened in one sentence (only if not obvious from the user's input).
2. Generate three options under the shape above.
3. Stop. Do not write a doc. Do not propose follow-on skills.
4. If the user picks one and asks for more depth, *then* offer to spin up `gm-session-prep` for the next session.

## What this skill is NOT for

- Pre-session planning (use `gm-session-prep`)
- An NPC's full voice (use `gm-npc-voice`)
- A handout that needs to be written (use `gm-handout`)
- Anything that takes more than 30 seconds of reading
