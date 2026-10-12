---
name: gm-npc-voice
description: Mid-session voice grab. The GM is about to play an NPC in 30 seconds and needs the voice in their ear — three sentences of dialogue they can lift verbatim, one tic, one thing the NPC would never say. Fast skill, no doc-writing. Invoke when the user says "voice {NPC} for me", "I'm about to play {NPC}, give me a line", "what does {NPC} sound like", "/gm-npc-voice". For full NPC building, use gm-npc-build. For strategic dossiers, use gm-strategy-doc.
---

# gm-npc-voice

The GM is about to play an NPC in real-time. Output is terse and immediately useful at the table.

## When to invoke

Trigger phrases:
- "voice {NPC} for me"
- "I'm about to play {NPC}"
- "give me a line for {NPC}"
- "what does {NPC} sound like"
- "/gm-npc-voice"

## Inputs to confirm

1. **The NPC name.** Required. Look them up in `docs/npcs/` and any `notes/*_strategy.md` mentioning them.
2. **The moment.** What's about to happen? "Negotiating with the party," "discovered a body," "lying to a superior," "drunk." This determines emotional register. Optional but useful — if not given, default to the NPC's most-natural register.

That's it. Don't ask more — the user is waiting.

## Required context

Whatever's pre-warmed. If cold: read the NPC's dossier under `docs/npcs/<slug>.md` and any `notes/<slug>_strategy.md`. Skip everything else — speed matters.

If the NPC doesn't have a dossier yet, say so and offer to spin up `gm-npc-build` instead of guessing.

## Style notes

- **Three verbatim lines, no more.** Different emotional registers. The GM picks which fits.
- **One tic.** A speech habit, a phrase they reach for, a verbal mannerism (calls people by their job title; never finishes sentences; says "I think" before assertions; uses "we" for "I").
- **One line they would never say.** This is the *boundary* of their voice. It's load-bearing because under pressure the GM might be tempted to put it in their mouth.
- **One physical accompaniment.** A gesture, a pause, a thing they do with their hands or face while talking. ("Taps the band on his head before deflecting." "Looks at the floor when he lies.")
- **No prose framing. No headings beyond what's shown below. Total output under 150 words.**

## Output shape

```
**{NPC name}** — {one-line register: "weary, restrained, monastic" or "loud, performative, insecure"}.

*"{verbatim line 1 — neutral register.}"*

*"{verbatim line 2 — under pressure / heightened emotion.}"*

*"{verbatim line 3 — when they want something from the party.}"*

**Tic:** {one short sentence.}

**Never says:** *"{a line that would break character.}"*

**Body:** {one short sentence — gesture, pause, posture.}
```

## Steps

1. Look up the NPC. If no dossier exists, stop and offer `gm-npc-build`.
2. Produce the output above. Stop.
3. Do not propose follow-on skills unless the user asks.

## What this skill is NOT for

- Building a new NPC (use `gm-npc-build`)
- Working out the NPC's strategic moves (use `gm-strategy-doc`)
- Off-script improv when the party did something unexpected (use `gm-improv`)
- Session prep (use `gm-session-prep`)
