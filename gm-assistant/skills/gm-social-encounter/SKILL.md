---
name: gm-social-encounter
description: Run a social encounter (captive interrogation, rescued-prisoner questioning, hostile-NPC negotiation, asset conversation) using the FlexAI for Social Encounters framework. Wraps the local flexai-social tool at ~/src/mytools/flexai-social (Flask server on port 5105) — auto-picks Role × Size × Context from campaign state, calls the API for NPC-turn and result rolls, then TRANSLATES the raw mechanical results into in-character narration in the NPC's voice. Solves the "Orc #3 interrogation" and "talk to the rescued prisoners" problem where a generic mook becomes a real person with their own goals, lies, and resistance. Invoke when the user says "the party wants to interrogate {captive}", "they're questioning the prisoners", "make this conversation not boring", "the NPC is being interviewed", "/gm-social-encounter". Two modes: tool-running (calls localhost:5105 API) and tool-cold (simulates the rolls using the framework rules). Multi-turn — the skill maintains continuity across the conversational volley.
---

# gm-social-encounter

The skill that solves *"the players want to talk to Orc #3 / the rescued prisoners / the captured cultist."* Instead of "they ask, you answer," you get a real social encounter with NPC moves, PC choices, DCs, and result types that make the NPC feel like a person who is *resisting*, *lying*, *deflecting*, *cracking under pressure*, *changing the subject*, or *revealing a plot clue they shouldn't have*.

## The framework

Wraps the **FlexAI for Social Encounters** rules from the FlexAI Guidebook (Infinium Game Studios, 2020), implemented as a local Flask app at `~/src/mytools/flexai-social/`.

- **Social Role** × **Role Size** × **Social Context** picks a table of available PC Choices and DCs.
- **PC Choices**: Diplomacy, Intimidate, Sense Motive, Mislead, Gather Info, Subject Info.
- **NPC Turn** roll (d100): produces what the NPC does on its turn in the conversational volley (the NPC has moves — it isn't a vending machine).
- **Result** roll (d100, modified by success/failure of the PC's choice): produces one of ~14 outcomes (Turns Hostile, Leaves, Ignores, Answers Grudgingly, Answers, Volunteers Info, Lies, Red Herring, Reveals Plot Clue, Challenges You, Questions Motives, etc.).

The full rule text lives at `~/src/mytools/flexai-social/RULES.md` — reference it for edge cases.

## When to invoke

Trigger phrases:
- "the party wants to interrogate {captive}"
- "they're questioning the prisoners"
- "the players want to talk to {NPC} after the fight"
- "make this {prisoner/captive/interview} not boring"
- "the captured {orc/cultist/bandit} is being interviewed"
- "social encounter with {NPC}"
- "/gm-social-encounter"

## Inputs to confirm (one at a time, via AskUserQuestion)

Most of these can be inferred from context — skip what's already clear.

1. **Who is the NPC.** Name if any (else "captive orc #3", "rescued prisoner — old woman", etc.). If they have a dossier under `docs/npcs/`, read it.
2. **Social Role.** The single most important determinant. Default reasoning:
   - Just captured in combat / openly hostile → **Opponent**
   - Rescued prisoner who has no idea who you are → **Bystander**
   - Rescued prisoner who has reason to be grateful → **Acquaintance**
   - Hireling, faction friend → **Ally**
   - Plot-relevant NPC who has information → **Asset**
   - The DC workbook does NOT ship with Acquaintance DCs (known gap from the README) — fall back to Opponent or Bystander DCs and warn the user.
3. **Role Size.** Default reasoning:
   - Random mook (Orc #3, generic prisoner) → **Minion**
   - Lieutenant, named NPC, anyone with INT > 8 → **Normal**
   - Captain, faction officer, the BBEG's right hand → **Elite**
   - Major character, faction leader, a PC's lost relative → **Solo**
4. **Social Context.** Default reasoning:
   - Combat ended one round ago, blood still wet → **Lull in Fighting**
   - Hours after combat, party rested → **Long Rest** or **Short Rest** depending on length
   - Captive being escorted back to camp → **Passing By**
   - Formal interrogation in a court → **Formal Gathering**
5. **What does the party WANT from the conversation.** This affects what Choices they're likely to pick and what counts as "success." ("Where is the warlord's camp?" "Why did you betray the temple?" "Who else is involved?")
6. **Critical NPC facts the player-facing world hasn't established yet.** What does this NPC actually KNOW that they could reveal? What would they LIE about? What is their breaking point? If the captive is generic and hasn't been written yet, *briefly* improvise these and tell the user — they can override before play.

## Required context (read in this order)

1. The NPC's dossier under `docs/npcs/` if any
2. Any sibling strategy/network doc that names this NPC
3. `docs/campaign_state.md` — for what just happened
4. The most recent session summary — for combat aftermath details
5. `~/src/mytools/flexai-social/RULES.md` — keep the rules handy; don't paraphrase from memory when it matters
6. **NEVER read other campaigns' directories** — campaign isolation rule

## Tool integration

### Mode A — flexai-social server is running

Check first: `curl -s -o /dev/null -w "%{http_code}" http://localhost:5105/api/cell?role=Opponent&size=Minion&context=Lull%20in%20Fighting&rank=1` — a 200 means the server is up.

If running, use the API for the authoritative rolls:

- `GET /api/cell?role={R}&size={S}&context={C}&rank={r}` — returns the FlexCell with available choices, DCs (5E + PF2e), success/failure result tables.
- `POST /api/roll/npc-turn` with `{role, size, context, rank}` — rolls the d100 for the NPC's turn.
- `POST /api/roll/result` with `{role, size, context, rank, success: bool}` — rolls the d100 against the appropriate success or failure result table.
- `POST /api/attempt` with `{role, size, context, rank, choice, pc_total, system}` — full attempt resolution including PC roll vs DC.

Quadded Challenge **rank** — the user can supply, else default to rank 1 for an early-tier party, rank 2 for mid, rank 3 for late. For 5E, the *lower* value of the DC column is used (per RULES.md).

### Mode B — server is cold

If the server isn't running, do NOT attempt to start it (the data files are commercial content and the path is environment-specific). Tell the user once:

> "The flexai-social server isn't running. To get authoritative DCs and result tables, in another terminal: `cd ~/src/mytools/flexai-social && python3 app.py`. For now I'll simulate the rolls using the framework's structure — you'll get the right shape of results but not the published DCs."

Then proceed: pick the Result types by hand using the table in RULES.md, weight them roughly by what feels appropriate to the Role × Size × Context combo. Roll d100s yourself (Bash: `echo $((RANDOM % 100 + 1))`). State the roll openly so the user can see and override.

## The cardinal move: translate mechanical → in-character

This is where the skill earns its keep. The tool gives you a *result type* (e.g., "Answers Grudgingly"). You translate that into **what the NPC actually says and does**, in their voice, given the specific question the party asked.

The translation must honor:

- **The NPC's voice.** Use their dossier voice or improvise in the Kostadis name+tic+anchor pattern. A captive orc's "Answers Grudgingly" is not a captive nobleman's "Answers Grudgingly."
- **The NPC's interiority.** Even a mook has a small goal in this moment (don't get killed, get back to my tribe, protect my sister, embarrass the captain who got me captured). The result is filtered through that goal.
- **What they actually know.** A Minion-tier orc does not know the warlord's strategic plans. They know who their squad leader was, where they camped last night, and what the cook served. **Volunteers Info** for a Minion is a *small* extra fact, not a plot dump.
- **Their resistance method.** "Lies" for one captive is fabricated specifics ("the camp is north"); for another it's smug silence-with-a-smirk; for another it's misdirection-by-overshare. Pick the method that fits their character.
- **The body language.** One line of physical action with each response. (Looks at the floor. Spits. Laughs nervously. Stares at the dwarf's beard. Tries to sit up.)
- **Sticky details that can be followed up.** If the NPC mentions a name, a place, a time — those should be specific enough that the party can come back and pull on them later. Don't generate placeholder text.

## The conversational volley structure

A social encounter is not one roll — it's a back-and-forth. Run it as a multi-turn loop:

1. **Open** — describe the NPC's initial demeanor in two sentences. (Where are they? Bound? Bleeding? Hostile? Resigned?)
2. **NPC turn** — roll the NPC's turn. Translate to in-character behavior (an opening posture, a question of their own, a stalling tactic, a demand).
3. **Wait for the PCs' choice.** The GM tells you what the players actually try. Translate that to one of the six Choices (Diplomacy / Intimidate / Sense Motive / Mislead / Gather Info / Subject Info).
4. **Resolve the attempt.** Either:
   - The GM gives you the PC's roll total → call `POST /api/attempt` (Mode A) or compare to a sensible DC by feel (Mode B). Report success or failure.
   - OR the GM just says "they made it" / "they failed" → roll the Result table directly.
5. **Translate the Result to in-character action.** Three to six sentences. End with what the NPC is doing physically now (so the GM knows the current scene state).
6. **Loop back to step 2** for the next exchange, or end the encounter if the result was Turns Hostile / Leaves / Ignores You and the party stops.

Maintain a running log inside the conversation (just track in your head — don't make the user save anything). The third exchange should *reference* what the captive said in the first exchange. Continuity is the difference between this skill and a one-shot roll.

## Critical failures = immediate consequence (per RULES.md p.262)

If the PCs roll a critical failure (natural 1, or DC missed by 10+), per the rules' "Leniency / Immediacy" guidance you should pick the *immediate* version of the bad result, not the soft version. **Turns Hostile** triggers combat now. **Leaves** means the NPC ends the conversation now and won't be re-engaged this scene. **Questions Motives** becomes a Leaves-on-failure.

State the critical failure openly to the GM and ask: "Treat as immediate consequence (per RULES.md), or do you want me to lenience this one?" — let the GM decide.

## What the skill produces (output shape per exchange)

Keep it terse — this is happening in real-time at the table. Per exchange, you output something like:

```
**NPC turn:** *(d100 = 47 → Answers Grudgingly)*

The orc — call him **Gurzhuk** — stops trying to chew through the rope and lets his
head fall back against the wall. *"Fine. Fine. The camp's at Three Rocks. North of
the river. Don't make me say it twice."* He won't look at the half-elf. He's not
afraid of the dwarf — but the half-elf reminds him of his cousin, who he isn't
proud of.

**Stickies:** Three Rocks (location, north of river). Has a cousin he isn't proud
of — likely a half-elf or part-elf — that's a future hook if the party wants it.

**Currently:** bound, sitting against the wall, head back. One eye on the door.
```

That's the whole shape for one exchange. The GM then says "the party tries to verify with a Sense Motive" or "they ask about who else is in the camp" — and you do another exchange.

## Steps

1. Resolve the 1-6 inputs via AskUserQuestion.
2. Detect whether the server is running.
3. State your read of the Role × Size × Context to the GM. **Wait for confirmation before rolling** — getting these wrong wastes the encounter.
4. If the NPC is generic / hasn't been written yet, give a 3-line improv NPC pitch (name + one tic + one fact they know that the party will care about) and wait for the GM to accept or override.
5. Run the conversational volley. One exchange per response. Don't run multiple exchanges in one block; wait for the GM to tell you what the players try next.
6. End the encounter when the Result type implies it (Turns Hostile, Leaves) or when the GM signals they're done.
7. If the encounter produced new lore (the cousin, Three Rocks, etc.), at the end summarize the stickies in one block so the GM can paste them into their notes.

## What this skill is NOT for

- Full strategic dossier (use `gm-strategy-doc`)
- A new NPC who needs a permanent record (use `gm-npc-build`, *then* this skill in subsequent encounters)
- Quick voice grab without the social-encounter framework (use `gm-npc-voice`)
- Pre-session prep at the scene-design level (use `gm-session-prep`)
- The mid-session "what happens next" question after the encounter ends (use `gm-improv`)
- Combat — the social-encounter framework explicitly excludes active PvNPC combat (per the rules, you have to "start a conversation without suffering additional blows" first)

## References

- Tool: `~/src/mytools/flexai-social/`
- Rules: `~/src/mytools/flexai-social/RULES.md`
- README: `~/src/mytools/flexai-social/README.md`
- Source: FlexAI Guidebook (Infinium Game Studios, 2020-08-17 v1.5), pp. 260-265 — commercial content
- The DC workbook ships without Acquaintance DCs (known gap — fall back to Opponent or Bystander)
