---
name: gm-session-prep
description: Generate a co-GM session prep document for the active campaign in the style of toee/notes/phase3_endgame.md — win condition, default trajectory, branches, scene staging, anticipated player questions. Invoke when the user says "prep the next session", "co-gm me", "help me run the next session", "/gm-session-prep", or asks for help thinking through what happens at the next table. The output is a working doc for the GM to read at the table, not a player-facing handout. This is the foundational co-GM prep skill; other skills (gm-faction-network, gm-strategy-doc, gm-handout, gm-npc-build) are narrower specializations.
---

# gm-session-prep

The co-GM prep workflow that produced `toee/notes/phase3_endgame.md`. The output is a **working doc the GM reads before and during the session** — not narrative prose, not a player handout.

## When to invoke

Trigger phrases:
- "prep the next session"
- "co-gm me"
- "help me prep/run the next session"
- "/gm-session-prep"
- Any "help me think through what happens when [event]"

Refuse politely if the working directory is not inside one of the campaign subdirs (`Phandalin/`, `out-of-the-abyss/`, `Hillsfar/`, `toee/`, or a future sibling). The skill is campaign-scoped — see `campaigns/CLAUDE.md` for the isolation rule.

## Inputs to confirm (one at a time, via AskUserQuestion)

Only ask for things you can't infer. If the user already supplied an answer in the invocation, skip that question.

1. **The beat.** What does the user want this session to *do*? One sentence. ("The party arrives in Kelno's quarters", "the cult attacks the wedding", "the merchant prince tests the party's loyalty.")
2. **Genre/tone.** Political thriller? Dungeon crawl? Heist? Comedy of errors? Horror? This is the single most useful framing the user can give — it determines pacing, NPC density, and which moves to pull from the style sheet. Default if pressed: "whatever fits the current campaign state."
3. **Player level.** Numeric. Affects which threats are existential vs trivial. The user's own recipe was "the players were 15."
4. **Anything else load-bearing the docs won't tell you.** E.g., "one player is missing this week", "we're running short — needs to wrap in 90 minutes", "I want to introduce X NPC."

## Required context (read in this order)

Read from the current campaign's `docs/` and `summaries/`. If a path doesn't exist in this campaign, skip it and note the gap rather than failing.

0. `docs/gm_doctrine.md` — **read first when present.** The campaign's standing GM rulings (how villains, gods, factions and ordinary people behave) and an index of its design docs. Follow the index to any design doc the beat touches. Its rulings override your defaults.
0a. `docs/arcs/` — **read when present.** These are the GM's arc files, owned by `gm-arc`:
    - the sandbox the party is in (`sandboxes/<place>.md`);
    - every arc running there, plus any travelling arc tonight touches;
    - `clocks.md`, `calendar.md` and `junctions.md`;
    - the strategy docs those arcs link to. **The strategy doc owns each villain's ledger.**

    Arcs are **hopes**, not outcomes. Seed the prep from them, but verify anything they say *happened* against the summaries. If `docs/arcs/` is missing, see step 0.
1. `docs/campaign_state.md` — current state of the campaign
2. `docs/world_state.md` — the world's current state (factions, weather, calendar)
3. `docs/party_state.md` or `docs/party.md` — who the PCs are right now
4. `docs/background/` — campaign background lore (read selectively if large; prioritize files matching the beat)
5. The **last two session summaries** under `summaries/YYYYMMDD/` — most recent first. These are the *authoritative* record of what just happened.
6. `docs/npcs/` — selective. Read dossiers for any NPC the user named in the beat, plus their lieutenants.
7. If a `mempalace` is configured (`.mcp.json` lists it), assume the user can also retrieve scene-level detail via search — but don't depend on it.
8. **Every ruling already on file for tonight** (read in full, not scanned; step 1b turns it into a table):
    - every prep in `notes/session_prep/` since the prep for the last played chapter, including follow-up and rulings files, and the scene files under them;
    - each cast NPC's and faction's strategy doc (`notes/*_strategy.md`): its Ruled lines, Open decisions and hidden rows;
    - the sandbox's design folder (e.g. `docs/gauntlgrym/`): NPC cards, asset table, pitches;
    - every player handout and offer card tonight's cast can touch (`notes/handouts/`, `roll20/` if present).

Do **not** read other campaigns' directories. Do **not** invent canon — if a fact isn't in the docs, mark it as a decision the user needs to make.

## Style notes for this output

Co-GM prep docs in this workspace follow a recognizable shape. The user has corrected explicitly: **this is fanfic-narrative GMing, not lit-RPG.** That means:

- **Strategic clarity over mechanical exhaustion.** State the win condition plainly. State the default trajectory if the party does nothing. State the optimal play. Don't drown the GM in stat blocks — they have those elsewhere.
- **Mechanics live in their own file, never in the scene.** Fights bury structure: a scene with stat lines, spell lists and round-by-round tactics hides who wants what and where the scene points (GM, 2026-10-27). A scene with a fight says only what the fight is *for* and how it ends, then links one file per combatant at `notes/statblocks/{npc-slug}.md` (built with `/gm-statblock`, full mode). That file opens with **How to play them** (stance, body, voice, round by round, cuttable lines), then the block, tactics, the tells players can read, and the flaw's blind spot. The prep's "Open alongside" line links it too.
- **Every NPC in the cast has a stat block, fight or no fight** (GM, 2026-10-28). Anyone in THE CAST can end up in a fight, or travel with the party into one. Combatants get full mode; everyone else gets at least quick mode, filed at the same path. *Failure this fixes: at the machine-room session (Phandalin, played 2026-10-28), Bimble came along, and the prep linked no stat block for him because it only built blocks for the planned fight. His quick block existed but was linked from nothing, so the GM had to hunt for it mid-combat ("I thought I had created a stat block").*
- **Every scene has its own file, with the dialogue in it** (GM, 2026-10-28). The prep doc carries a scene's structure and rulings, and a ruling only says what happens: "Bimble works out the machine can be repaired" is not something the GM can say aloud. Each scene gets one file at `notes/session_prep/{prep-stem}/scene-{NN}-{scene-slug}.md`, where `{prep-stem}` is the prep's filename without `.md`. It lists the scene's beats in order, and **every beat an NPC delivers has the line they say**, tagged (`[TABLE]` for canon quotes, `[OVERLAY]` for lines you wrote). Branches that change who delivers a beat (an optional NPC absent, a PC finding it instead) get their own line. Template in step 11. *Failure this fixes: at the same session, Bimble's "oh look, I can fix it" beat got lost. The ruling was in the prep, but nothing gave the GM his words.*
- **Every NPC in the cast has a VTT token before play** (GM, 2026-10-28). The prep ends with a **Table setup** checklist the GM ticks off in Roll20 before the session: one row per cast NPC and companion, with the numbers the token needs taken from the stat block. You can't see Roll20, so you never mark a row done; the GM does. Template in step 12. *Failure this fixes: at the machine-room session (Phandalin, played 2026-10-28), there was no Aletra token when she stepped out of the machine ("I do not have an icon of her"), and Bimble's token hadn't been added to the party, so a player had to ask for it.*
- **Rooms live in their own file, never in the scene.** A scene can carry the whole story and still leave the GM with nothing to say when the players walk in (GM, 2026-10-28). Each place a scene happens in gets one file at `notes/locations/{place-slug}.md`, linked from the scene's **Where** line and from the prep's "Open alongside" line. The file belongs to the place, not the session, so later preps link the same file and add to it. **Rooms come after the beats are settled** (GM, 2026-10-28): a room built for a beat that changes is wasted work. Template in step 9.
- **Branches, not rails.** For every choice point, sketch ≥2 paths. The party *will* go off-script; pre-stage the off-script.
- **Antagonists get interiority.** Even one-scene NPCs need a stake, a worry, a small goal. The party may never learn it; the GM needs to know it to play the NPC right.
- **Failure is comedic and material.** If a roll fails, what does the party *lose*? (A bow. A reputation. An ally's trust. Not "you take damage.")
- **In-fiction vs GM-only is explicit.** Mark which information the players can pick up and which is GM-only. Use quoted-block (`>`) for GM-only.
- **Theatrical timing matters.** When to be silent. When to escalate. When to let an NPC interrupt. Call these out as stage directions.
- **Modern register is fine.** Contemporary jokes, management-speak, references — all in bounds. Don't force "thou."
- **The Tenday calendar is real.** Use FR date stamps when relevant. When `docs/arcs/calendar.md` exists, it is the only source for today's date. Never work a date out from prose.
- **Mark provenance on every claim.** The GM must be able to tell, at a glance, what is adventure canon, what is already-played table history, and what you invented. See *The mandatory blocks*, below.
- **Organize by person, not by thing.** At the table the GM thinks "what does Morista give them?", not "where's the spore-ward file?". Every offer, handout and promise hangs off the person it belongs to. See block 4.
- **Nothing at the table needs a search.** If the GM would have to grep a folder or ask an AI mid-session to find something, the prep has failed. One click from the prep doc reaches every handout, card and term the session can touch.
- **No NPC arrives unannounced.** If someone can speak this session, they are in the cast sheet with a reason for being there.
- **Offstage clocks are visible to the GM.** Anything running on its own schedule is listed up front, not buried in a branch.
- **BBEGs pass the Evil Overlord test.** Every villain move must pass `gm-assistant/references/evil_overlord_list.md` (see the workspace `CLAUDE.md`). **A counter the villain knows about violates the rule**: if a party spell, item or trick is known to the villain, the plan already accounts for it. Exceptions only for in-character reasons the GM has ruled.
- **Every NPC knows only what they have a source for** (GM, 2026-11-02). The no-meta-gaming rule (D-rules) covers every speaking NPC, not just villains: a line names a fact only if that NPC saw it, was told it, or could reasonably know it. A handout that reveals something the party hasn't worked out yet carries its trigger ("hand over once the party connects X"). *Failure this fixes: in the Ch. 74 follow-on prep (out-of-the-abyss, 2026-11-02), Bruenor's forge line named the Dust of Mechanus, which he doesn't know about, and the clock card and vault list were set to be handed over before the party connected the dust to the anvil.*
- **Player-facing text passes a secrecy check** (GM, 2026-11-02). Before any player handout, sheet or shared artifact is written, regenerated or shared, check it against the strategy docs' hidden rows, `GM-ONLY` notes in `docs/entity_registry.yaml` and every GM-only tag in the prep, and bring every hit to the GM. *Failure this fixes: the same prep named Yi Lao as SEER on the Roll20 faction sheets and the shared player sheet. Her identity is a state secret: only those who meet her know.*
- **A ruling is written once and propagated** (GM, 2026-11-02). When the GM rules, every file that repeats the ruled thing changes with it (step 8). A ruling that lands in the prep but not on the NPC card is a contradiction the GM will read mid-scene.

## The mandatory blocks (before Scene 1)

**These go at the top of every prep doc, after the rulings and before the first scene.** They exist because of failures at the table, and each block fixes one. Blocks 1–3 are always required. Block 4 is required whenever the party can receive anything (an offer, a gift, a deal, a handout) from more than one NPC this session. Block 5 is required whenever more than three NPCs can speak; it's written after the scenes but sits with the others.

**Counting NPCs:** count everyone who can speak in any branch, including by *Sending*, letter or projection. One NPC in two forms (in person and as a projection) is one card with two rows.

**Prep that already exists:** insert the missing blocks above Scene 1. Don't rewrite the scenes; where a scene restates an NPC, replace the restatement with a link to the NPC's card.

### 1. Provenance legend — and tag accordingly

The GM cannot tell where the module ends, the intended plan begins, and your invention starts. **Fix it with visible tags:**

| Tag | Means | Trust |
|---|---|---|
| `[MODULE §x]` | Adventure text, with a section reference | Canon |
| `[TABLE]` | Already played at the table | Canon |
| `[RULED date]` | A GM ruling, with its date | Canon |
| `[OPEN]` | Not yet decided; listed under Open decisions | **Ask before play** |
| `[OVERLAY]` | **Yours.** Invention, staging, connective tissue, recommendations | **Cuttable — nothing downstream breaks** |

State the tiebreak explicitly: **if an overlay item and a module item disagree, the module wins and the overlay is what you got wrong.**

*Failure this fixes: prep docs blended module canon, campaign state, and invention indistinguishably, so the GM could not tell what was safe to cut or what the adventure actually required.*

### 2. THE CAST — everyone who can walk on this session

A table: **who they are, what they are, why they are here, and the source tag.**

**Include module-supplied support NPCs first** — the allied detachment attached to an objective, the faction contact, the escort. **These are the ones that ambush the GM**, because they arrive automatically without being anybody's plot.

*Failure this fixes: an allied priestess the module attaches to an objective walked into a scene and the GM said "what's she doing there?" — she had been mentioned only in a setup line and an NPC-notes footer.*

### 3. ALREADY IN MOTION — clocks running whether or not the party touches them

A table of everything happening offstage this session on its own schedule, with where each one stands tonight. When `calendar.md` exists, open the block with today's date (and its ± range), and add every row from its *What comes next* table that falls within reach of this session.

**The rule this enforces:** *if something is going to land on the party later, it should already be visible this session as noise, weather, or a messenger — never introduced at the moment it matters.*

*Failure this fixes: a major NPC was leaving a trail of bodies across the region during a session and the GM did not realise it was happening.*

### 4. WHO HAS WHAT — the person-first index, plus one player sheet

**GM side: a table with one row per person**, in the order they're likely to come up:

| Who | What they offer | For whom | Handout | What they ask | What the party promised |
|---|---|---|---|---|---|

- **Who:** the NPC making the offer, and who actually delivers it if that's someone else (sponsor → operator).
- **For whom:** the whole party, or the one PC it's tied to. Say so when it's one PC.
- **Handout:** a direct link to every card that belongs to this person. **No handout exists without a row here.** A card that isn't linked from a person is a card the GM can't find. PC-kept logs and briefings belong to no NPC: list them on one line, and check each against tonight's offers for contradictions.
- **What the party promised:** left blank for the GM to fill in at the table, in the party's own words. This is the live record. Don't keep a second copy of it anywhere else in the doc.

**Player side: one consolidated sheet** at `notes/handouts/{YYYYMMDD}_{slug}_who_has_what.md` (same date rule as the prep file). **Hand it over when the NPCs are introduced**, not afterwards: the players need the names the moment they hear them.

It opens with **"How this scene works"**: two or three sentences the GM can also read aloud. Who is offering, whether the party picks one or can take several, and when (if ever) the deals will pull against each other. Then:

| Who (faction) | What they care about | Heard yet? | What they give us | How we use it | What we owe them | If we break the deal |
|---|---|---|---|---|---|---|

- **Generate it from the GM table**, dropping the GM-only columns and anything behind the firewall. Never write it independently: two hand-kept copies drift.
- **What they care about:** one line, in the players' terms ("the Gauntlet fears adventurers on a killing spree"). It saves the GM explaining every faction out of character.
- **Heard yet?:** *not yet* / *heard* / *offered* / *agreed*. It answers "have we heard from everybody?"
- **If we break the deal:** the consequence, as the NPC would state it. If the docs don't say, it's a question for the GM before play, never improvised into the sheet. If the consequence is deliberately hidden, write *not told*.
- **Reveals stay off the sheet until they land.** An offer that is itself a twist (a villain's projection bidding for the books) is added when it happens, not before.
- Plain language, one line per cell. It's a lookup, not flavour; the individual cards carry the flavour.
- Link it from the top of the prep doc and from block 4.
- **Send it ahead when you can.** A per-PC briefing sent before the session worked: at Chapter 74 (out-of-the-abyss) Daz's player read the character briefing that morning and said it felt "like slipping on the glove that fits perfect". The player sheet can go out the same way.

Individual handout cards are still `gm-handout`'s job. This block is what ties them to people and gives the players one page instead of twelve.

*Failure this fixes: at the Gauntlgrym negotiation (out-of-the-abyss Chapter 74, played 2026-10-26), twelve offer cards were named by asset rather than by who gave them, and there was no single sheet of who gave the party what. The GM had to search flat files mid-session, an AI lookup was too slow for the table, and the players got confused and frustrated. Tracked in kostadis/campaigns#506.*

### 5. DOES IT HANG TOGETHER — the pre-flight for social sessions

**Required whenever more than three NPCs can speak.** Write it *after* the scenes. Bring it to the GM before play as a short list of questions. **Never answer them yourself.**

**a. The players' goal, in one sentence a player could repeat.** It names a place and the next step, not only a purpose ("go into the Underdark" is not enough; where?). If it only becomes clear after Scene N, say what the players think they're doing before that. If you can't write it from the docs, stop and ask.

**b. One card per speaking NPC, on one screen.** Everything the GM needs to run them, in one place. Every other file links to the card and never restates it: two phrasings in two files is a defect, and it's how a GM misreads an offer mid-scene. Walk-ons may share a card.

| Field | One line each |
|---|---|
| **Role** | ally / gatekeeper / rival / threat / fun. Most aren't threats. "Fun to talk to" is a real role. |
| **Wants tonight** | 12 words max. If files disagree, name the file that wins. *Not stated* is a question for the GM. |
| **Why the PCs bother** | Tied to sentence (a). *Nothing tonight* is an honest answer: then they're colour or a seed. |
| **The ask / the offer** | What they want from the party; what they give. Kept visibly apart. |
| **Hook and its stakes** | How they open (a game, a dish, a note). If it's a game or test, what winning gets the party, and the ask and offer are said *before* it starts. |
| **If they break the deal** | What this NPC does. Feeds the player sheet. *Not told* if it's hidden from the players. |
| **Off-script** | One line covering insulted, robbed, recruited, ignored. Or a link to the branch that already covers it. |
| **Players can see it?** | If a hidden fact makes them look like something else from the player side (a dealer who reads as a trap), say so and pick: play the visible version, or give the players one clue. |

**c. Crowds react too.** One line per group present (a clan, a court, a guild): what it does if the party says or does something touchy.

**d. Needs versus hooks.** List the NPCs the party *needs* tonight to reach sentence (a), and the ones with the most fun hooks. Players go to the best hook first. If those are different NPCs, flag it, and give each needed NPC a way to reach the party (a note, an interruption) or a time budget per conversation.

**e. Pointing check.** List everything that tells the players what to do: the commission, each offer, each gift, any checklist or clock. One line each: does it point at sentence (a)? Anything pulling another way is a GM question with file:line, not a silent fix.

**f. Overlap.** Offers that fill the same need. Merge, cut, or say why both stay.

**g. Player words.** Every term on a player card is defined on a player card.

*Failure this fixes: at the same Chapter 74 session, the transcript shows the GM starting one representative's turn with another's hook, and correcting a misread offer mid-scene. The players asked mid-session whether they had to pick one faction, and what a chess game was for before anyone had offered anything. They spent the evening on the three representatives with the best hooks, who answered nothing they needed that night, and ran out of time before the two they did need. Every "if you break the deal" consequence was improvised. Two reviews of the prep found three representatives' wants written differently across four files.*

---

## Output shape

Use `toee/notes/phase3_endgame.md` for register and `toee/notes/sessions/nulb-knows-now.md` for **structure** — the latter states the intended session order up front in a blockquote, gives "keep this beside you" reference tables before Scene 1, and labels its invented layer explicitly as an overlay. The headings vary by session shape, but the canonical structure is:

```
# {Session title — evocative, not functional}

Co-GM working doc. Not canon yet — staging for {what session}.
Party: {level, names, who is player-run vs GM-run}
Register: {one line — the genre this session is in}

> **Scope:** where the session opens and where it stops. State the intended order and say what NOT to pull forward.

## How to read this doc — provenance legend
{[MODULE §x] / [TABLE] / [RULED date] / [OPEN] / [OVERLAY], and the tiebreak}

## Rulings already on file
{Step 1b. Topic · ruling · date · file:line. Superseded rulings struck through, with what replaced them.}

## THE CAST — everyone who can walk on tonight
{Table: who / what they are / why they are here / tag. Module-supplied support NPCs FIRST.}

## ALREADY IN MOTION — running whether or not the party touches it
{Table: what / where it stands tonight / tag}

## WHO HAS WHAT — by person
{When required (see block 4). Table: who / offers / for whom / handout links / ask / promised (blank).
Link to the player sheet: notes/handouts/{YYYYMMDD}_{slug}_who_has_what.md}

## DOES IT HANG TOGETHER — pre-flight
{When required (see block 5). The players' goal in one sentence; one card per speaking NPC;
crowds; needs vs hooks; pointing check; overlap; player words. Open items are GM questions.}

## The Win Condition (state plainly to yourself)
{One paragraph. What state must obtain for this session to count as "landed"?}

## The Default Trajectory (what happens if the party does nothing)
{Bulleted. The fates of each major NPC/faction if the party is passive.}

## The Clever Play (what the optimal party would do — the GM should know this)
{Numbered. Not because the party must do this, but so the GM knows when to nudge.}

---

## {Scene 1 — name}

### Setup
- Time and place in-fiction.
- Who's present, who's offstage.
- **Where:** [{place}](../locations/{place-slug}.md). Room details live there, not here (step 9).
- **Lines:** [Scene 1 dialogue]({prep-stem}/scene-01-{scene-slug}.md). What each NPC says at each beat lives there (step 11).

### Approach — {sub-area or first beat}
{Prose + dialogue snippets the GM can lift verbatim if the moment lands.}

### Fight — if there is one
- **What it's for:** {one line: what the fight changes in the story, not who wins on HP}.
- **How it ends:** {death, retreat, capture, surrender; and what each one costs}.
- **Stat block and how to play them:** [{NPC}](../statblocks/{npc-slug}.md). No stat lines, spell lists or rounds here.

### Branch — if the party {does X}
{Consequence + how the next scene shifts.}

### Branch — if the party {does Y}
{Consequence + how the next scene shifts.}

### NPC notes
- **{NPC}** — link to their block 5 card. Add only what is new in this scene (a voice tic, a line); never restate their want, ask or offer.

---

## {Scene 2 — name}
...

---

## Anticipated player questions
- **"What about {X}?"** → answer the GM should give, plus what's *not* answered.
- **"Can we just {bypass plan}?"** → the path-of-least-resistance the GM should leave open or close.

## Stage directions (timing/silence cues)
- When the party reads {handout}, leave a beat before reacting.
- If {NPC} is killed, don't fill the silence.
- {Other moments where pacing carries the weight.}

## Table setup — tokens and maps (GM ticks these in Roll20 before play)
{Step 12, pass 2. One row per cast NPC and companion: ☐ / who / token art / AC / HP / init / stat-block link / placement. One row per map.}

## Open decisions (for the user — don't decide for them)
- {Things the canon-and-state docs don't answer that the GM needs to pick before play.}

## Plot ideas the players already planted
- {Pool threads from `/gm-arc mine` touching tonight's cast and places: title · status · citation. Suggestions only, never written into an arc unless the GM pulls one in.}

## Proposed arc delta (GM approves before anything is written to docs/arcs/)
- {New possible beats (with gate), rulings made during this prep (all of them, tagged and given a reveal state), deferred decisions with a "decide by" trigger, new clocks, new affordances, junctions. As a diff, per arc or sandbox file.}
```

## Steps

The prep is built in two passes (GM, 2026-10-28). **Pass 1 is the structure**: what the session is for, the cast, the scenes and their beats, the rulings and the open questions. **Pass 2 is the details**, and starts only after the GM has signed off pass 1.

### Pass 1: the structure

0. **Arcs check.** If the campaign has no `docs/arcs/`, this prep is the campaign's import point (arc-tracking ruling D5). Ask the GM whether to set up the sandbox and arcs first with `/gm-arc new`. If the GM declines, prep without them and say so in the doc. Never create arc files without the GM's confirmation.
1. Read the docs in the order above. Take ~5 minutes of clock time max for items 0–7 — don't try to absorb everything; scan for what matters for this beat. Item 8 (the rulings on file) is the exception: step 1b reads it in full.
1a. **ADVANCE: the date first, then one question per untouched clock.**
    - **The date** (when `calendar.md` exists). If the latest played chapter has no ruled row, propose one: its days and end date, with the summary lines the count rests on. The GM rules it. Then say how many days have passed since each clock was last touched, and which `Due` dates have arrived or passed.
    - **The clocks.** List every clock (in `clocks.md`, and in the arcs' Clocks sections) whose `last touched` predates the latest played chapter. For each one, ask the GM: "*<clock>* — did it move offscreen since Ch. N? If so, to what?"
    - Ask one at a time. If there are more than about 12, use one Approve / Reject / Discuss artifact (the repo's long-queue rule).
    - **Nothing advances without an answer.** An unanswered clock stays where it was, and is listed under Open decisions.
    - Answers go into the proposed arc delta, not straight into the files.
1b. **Rulings sweep, before anything is drafted** (GM, 2026-11-02). Read every source in Required context item 8 and build a **Rulings already on file** table in the prep (topic · ruling · date · file:line). Later rulings supersede earlier ones; say which. **An open decision may be raised only when no ruling covers it**, and each one names what you searched. *Failure this fixes: the Ch. 74 follow-on prep's Pass 1 raised eight open decisions, several already settled in the 10-27 and 10-29 files (the clock's first tick, the Whisper Chain wording, Davra's room and her ask). The GM had to point to the earlier preps, the faction clarifications and the player handouts, one at a time, before they were read.*
1c. **Promises sweep** (GM, 2026-11-02). List everything earlier preps, rulings and handouts promised the players and that hasn't happened yet: rewards, offered items, documents ("the DM will provide a written comparison"), choices to be put to them. Each one gets a scene and who delivers it, or an Open decision. *Failure this fixes: in the same prep the vault items (one per PC, if the party stays two days and spends the dust) had dropped out of the draft until the GM raised them.*
2. Ask the 1-4 inputs the user hasn't supplied, one at a time.
3. **Draft the doc to `notes/session_prep/{YYYYMMDD}_{last_chapter_title}.md`.** Create `notes/session_prep/` if it does not exist — do not fall back to a flat `notes/{slug}.md` just because the directory is missing, and do not name the file after the location or the beat.

   - **`{YYYYMMDD}` is the date the prep is written**, not the date of the session being prepped and not the date of the chapter it follows.
   - **`{last_chapter_title}` is the title of the most recent *played* chapter**, snake-cased, chapter number included — the session this prep picks up from. Take it verbatim from that session's summary heading. If the chapter has no title yet, use `chapter_NN`. A prep written on 2026-09-04 to follow `# Chapter 10 The Wizard of the Old Owl Well` is:

     ```
     notes/session_prep/20260904_chapter_10_the_wizard_of_the_old_owl_well.md
     ```

   **Why the last chapter and not the next one:** the chapter being prepped has no title yet, and it will not have one until it is played and summarised — sessions routinely stop somewhere other than where the prep expected, so a forward-looking name goes stale the moment the dice hit the table. Naming from the played chapter makes the filename a stable, sortable pointer to a document that already exists, and it means the prep and the summary it descends from can be lined up by eye.

   The `# H1` inside the doc is still the evocative session title — the filename is an index, not a headline. If prep gets rewritten before the session runs, overwrite the same file rather than minting a second date.
4. Open with a 2-3 sentence summary of what you understood from the docs so the user can catch you if you misread.
5. Produce the working doc. **Write the mandatory blocks before writing any scene** — building the cast sheet first is also how you catch NPCs you were about to leave unintroduced.
   - **When arcs exist, seed the blocks from them.**
     - ALREADY IN MOTION comes from the clocks, with tonight's ADVANCE answers applied.
     - THE CAST comes from the sandbox's faction roster.
     - The villain ledger is **linked from** each villain's strategy doc, not re-derived.
     - Possible beats whose gates are open become candidate scenes.
   - **Stage scenes here, never in the arc.** Rooms, lines and handoffs belong to this doc. A possible beat marked `dead` is never staged again.
   - **Respect the payoff rule.** An arc with nothing under *Seen by the party* can't pay off tonight. Plant it on-screen first.
5a. **Mine threads.** Run `/gm-arc mine` for tonight's key NPCs and places, and list the useful hits under *Plot ideas the players already planted*. They are suggestions behind the firewall.
6. **Re-read your own scenes and check every named NPC appears in the cast sheet.** If one doesn't, add it — that is exactly the NPC that will surprise the GM.
6a. **Run the Evil Overlord audit.** For each BBEG beat, check it against `gm-assistant/references/evil_overlord_list.md`, the D&D rules in `gm-assistant/references/evil_overlord_dnd.md` (D1–D19), and the party's sheets: does the party hold a counter the villain knows about? If a beat fails, fix it or list it under Open decisions with the rule number. The list is a guideline and villains aren't prescient: for each BBEG in the session, name their flaw and the blind spot it opens tonight, and list the blind spots in the prep so the GM can recognize, and reward, players who find them. Villains think they are right: for each beat, ask whether the villain would call it correct. If it is the flaw talking, keep it and list it as a blind spot; if it is a plain mistake, fix it (workspace `CLAUDE.md`). A BBEG with no recorded flaw is a question for the GM. Never write "the villain planned for that" unless the plan is written down.
6b. **Run the table-lookup check.** List every handout, card and term sheet the session can touch, including ones written by earlier preps. Each must be linked from a person's row in WHO HAS WHAT, and each row's offer must appear on the player sheet. Fix any orphan. **Then check every card against the rulings** (GM, 2026-11-02): for each term a player card states (price, reward, timing, break-faith consequence, what was already given), compare it with the latest ruling in the step 1b table. Bring each contradiction to the GM with the card line and the ruling side by side; never fix a player card silently. Then write or regenerate the player sheet from the GM table, and run the secrecy check (Style notes) on it. *Failure this fixes: at the 2026-11-02 prep, the departure clock card had the brief's timing backwards, Bruenor's "Given now" listed offers nobody had accepted, the Brief card promised "later briefs" after there was only one, and Morista's note left out her main ask. Every card was linked, so the link check passed.*
6c. **Run the hang-together pre-flight (block 5).** Bring every *not stated*, *nothing tonight*, missing consequence, needs-versus-hooks flag, pointing conflict, overlap and undefined player term to the GM as questions before play. Never fill them in yourself. More than about a dozen: use the Approve / Reject / Discuss artifact.
7. End with **Open decisions** explicitly. Don't decide things the user should decide.
8. **Propose the arc delta** (when `docs/arcs/` exists). Include every ruling the GM made during this prep (arcs hold all rulings that touch them), new possible beats, deferred decisions, the ADVANCE answers, and new clocks and affordances. Show it as a diff. **Write to `docs/arcs/` only after the GM approves**, and then only what was approved.
8a. **Propagate the rulings** (GM, 2026-11-02). For every ruling made in this prep, list each other file that repeats the ruled thing: NPC cards, offer cards (their GM headers too), strategy docs' Open decisions and *not yet heard* lines, the player sheet, and the prep's own status banner. Show one diff per file in the same delta. When scenes or beats are renumbered, update every cross-reference to them. *Failure this fixes: after the 2026-11-02 rulings, the NPC cards still said "Not stated" for five answered questions, seven offer cards pointed at retired beat numbers, and the strategy docs said the break-faith terms were "not yet heard". It took a separate 1x1 pass to catch them.*

### Checkpoint: the GM signs off the structure

Stop here. Bring the GM the doc as it stands: the scenes and their beats, the rulings, Open decisions and the pre-flight questions. **Pass 2 starts only when the GM has ruled on them.** A beat still open stays out of pass 2 until it is settled: detail built on a beat that changes is wasted work, and detail that looks finished hides that the beat underneath it is still open.

### Pass 2: the details (after the GM signs off)

Everything the GM needs at the table, built on the settled structure: rooms, stat blocks, the words each NPC says, and the Roll20 setup.

9. **Build the rooms, once the beats are settled.** Start this only after the GM has ruled on the scenes and Open decisions; if a beat is still open, its room waits. For each place a settled scene happens in: is there a file at `notes/locations/{place-slug}.md`, and is it linked? If not, write it. Look first for what is already canon: the place's reference file (e.g. a district file), earlier preps, the summaries, the module (5etools `get_section`). Tag every detail `[TABLE]`, `[MODULE]` or `[INVENTED]`. **Invented details are proposals:** bring them to the GM, one at a time or in the review artifact if there are more than about a dozen, and change a tag only after the GM rules. The file has these sections, in this order:
   - **What they see first.** Two or three short sentences the GM can read aloud.
   - **Size, light, sound, smell.** One line each.
   - **Ways in and out.** Every door, window, hatch and stair, and where it leads.
   - **What's in the room.** A numbered list. Each item says what it is, where it is, and what a PC can do with it (climb, hide behind, break, read, use).
   - **Who is where.** Where each NPC stands or waits when the scene opens.
   - **If it turns into a fight.** Cover, height, hazards, chokepoints. Terrain only; combatants stay in `notes/statblocks/`. **Ask the GM for the room's size and grid** (e.g. 120 × 60 ft at 5-ft squares) rather than inventing it, then offer a battle map: a player copy with no labels and a GM copy keyed to the numbered items, with the layout tagged `[INVENTED]` for the GM to rule on. Maps and the scripts that draw them go in `notes/location_maps/`, outside the corpus dirs, so the search index never mines them (GM, 2026-11-02).
     - **Size every player map for the VTT: 70 px per 5-ft square** (Roll20's default), with the grid starting at the image's top-left corner. Make every edge a whole number of squares, so the image drops onto the page and lines up. In the report, state the image's size in pixels and in squares (e.g. "1960 × 2170 px = 28 × 31 squares"). If a map can't be made at 70 px, **tell the GM the pixel size of a square** instead of leaving them to measure it (GM, 2026-11-11).
     - **Draw both copies from one script**, with a `--player` flag that leaves out everything the party can't see: trigger radii, DCs and damage, NPC names, internal room names, and GM notes. Check that the GM copy still renders byte-for-byte identical after you change the script.
     - **A player copy may be split by floor or area**, so parts can be revealed as the party reaches them (e.g. the basement handed over at the stair). Each part follows the same 70-px rules.
   - **Hidden (GM-only).** What a search finds, and where.
   - **Sources.** Where each `[TABLE]` and `[MODULE]` detail comes from.

9a. **City colour, for any scene in a settlement** (GM, 2026-11-02). Write `notes/locations/{place}-colour.md`: numbered sights, people and rumours the GM can drop between scenes or roll for, so the place feels lived in. Draw first on canon (the module, summaries, earlier preps), tag every entry, and give rumours a truth tag (true / partial / false, GM-only). Link it from each scene's **Between scenes** line. Invented entries go to the GM for review with the rest of pass 2.
10. **Build the stat blocks (mechanics check).** For **every NPC in THE CAST**, not only the ones in a planned fight: is there a stat-block file at `notes/statblocks/{npc-slug}.md`, and is it linked from the prep's "Open alongside" line? If not, build it with `/gm-statblock`, asking its questions one at a time: full mode for anyone in a planned fight, at least quick mode for everyone else. For each fight, the combatants' files must open with How to play them. Then strip any stat lines, spell lists or round-by-round tactics left in the scene, and move them into those files.
11. **Write the scene files, and run the dialogue check.** For each scene, write `notes/session_prep/{prep-stem}/scene-{NN}-{scene-slug}.md` and link it from the scene's **Lines** entry. Then walk every ruling and beat in the scene: if an NPC delivers it, the scene file must have the words. A ruling with no line is the failure this step exists for. Read the NPC's voice file or strategy-doc voice samples before writing; reuse a canon quote where one fits, and tag everything you write `[OVERLAY]`. The file has these sections, in this order:
   - **Who's in it.** Each speaking NPC, linked to their block 5 card (or cast row) and their stat block.
   - **Beats, in order.** One numbered entry per beat: what happens (one line), **who says it**, and **the line**, quoted, ready to read aloud. Add a second line when the beat lands differently with a different listener (e.g. Valphine).
   - **If {NPC} isn't there.** For each optional NPC, who delivers their beats instead, and that person's line.
   - **Lines for likely questions.** What the NPC says when the party asks the obvious thing. Point to the prep's Anticipated questions for the ruling; only the words go here.
   - **Never says.** From the voice file or strategy doc.

   Then run the **knowledge check** (Style notes): for every line, does this NPC have a source for each fact in it? For every handout a beat hands over, is its trigger written? Rewrite or flag any line that fails.
12. **Write the Table setup checklist**, as the prep's last section before Open decisions. One row per NPC in THE CAST, plus companions who travel with the party (an optional NPC the party may bring, a mount, a familiar):

    | ☐ | Who | Token art | AC | HP | Init | Link | Placement |
    |---|---|---|---|---|---|---|---|

    - **AC, HP, Init** come from the stat block in `notes/statblocks/`, so they match it. A blank here means step 10 isn't finished.
    - **Link** is the stat-block file, so the numbers are one click away at the table.
    - **Placement**: *on the party page* (companions and anyone who may tag along), *on the map at {spot}*, or *GM layer until they arrive* (anyone who enters mid-scene, like a villain through a door or a machine).
    - **Token art**: the art the GM already has, if the prep's sources name it; otherwise *needs art*. Never generate or pick art yourself.
    - Add one row per map: the location file and whether the map is built.
    - Leave the ☐ column empty. Only the GM ticks it.
13. **Update the players' calendar** (when `docs/arcs/calendar.md` exists). If step 1a ruled a new chapter row, or moved *Today*, run `/gm-player-calendar` to add the new events to the players' page (`notes/handouts/player_calendar.json`) and republish it to the same link. Its own GM review applies: the event wording is a proposal until the GM rules. If the campaign has no players' calendar yet, ask the GM whether they want one; don't build it unasked. Add a row to the Table setup checklist: *players' calendar updated to Ch. N* (☐ left for the GM).
14. **Corpus check before committing** (GM, 2026-11-02). If the prep created a new folder (e.g. `notes/locations/`, `roll20/`), run the `/corpus-gaps` scan so the new documents become searchable, and generated files (HTML copies, images, scripts) are kept out of the declared dirs instead of being moved later. Membership is the GM's ruling, through that skill.

## What this skill is NOT for

- Writing individual player handouts (use `gm-handout`). The one exception is the consolidated WHO HAS WHAT sheet, which this skill generates from block 4.
- Building a faction operational map (use `gm-faction-network`)
- Per-NPC strategic dossier (use `gm-strategy-doc`)
- Designing a single NPC (use `gm-npc-build`)
- Mid-session improv (use `gm-improv`)
- Writing up what happened *after* the session (that's CampaignGenerator's job, not this skill)
- Recording a played session into the arcs (use `/gm-arc record`, once the summary exists)
