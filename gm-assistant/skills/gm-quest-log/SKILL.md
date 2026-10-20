---
name: gm-quest-log
description: Build a player-facing quest log for the active campaign — every open promise, contract, errand, and personal thread the party currently knows about, reconstructed from session summaries rather than the grounding docs. Written in the voice of a party member who keeps notes, so it can be handed straight to players. Invoke when the user says "what quests do the players have open", "make a quest list", "player-facing quest log", "what are the party's open threads", "/gm-quest-log". Output goes next to the campaign's existing player handouts. Player-knowledge only — never module trackers, dossiers, or GM secrets.
---

# gm-quest-log

Produces the list of open business the *party* believes it has. Not the list the GM is tracking — the list the players would write down if one of them kept a notebook, which is a strictly smaller and more interesting document.

The value is in the gap. What the party thinks it owes, who it thinks it owes it to, and which threads it has noticed but nobody has paid it to pursue.

## When to invoke

- "what quests do the players have open"
- "make me a player-facing quest list"
- "what's the party actually chasing right now"
- "give the players a quest log"
- "/gm-quest-log"

## The rule that matters most: rebuild from summaries, not grounding docs

**The grounding docs will be stale, and they will be confidently stale.**

`docs/campaign_state.md`, `docs/world_state.md`, `docs/planning.md`, and `docs/party.md` are pipeline outputs regenerated on a cadence that does not match play. In the obelisk campaign they were four chapters behind: `campaign_state.md` listed Glasstaff as "not yet confronted" when the party had already fought him, wounded him, and watched him teleport away — and listed Halia as "unvisited" three sessions after she was interrogated at the Sleeping Giant.

A quest log built from those docs would have handed the players quests they had already finished.

So:

1. **Session summaries are the source of truth.** Read every one, oldest to newest.
2. **Grounding docs are a cross-check only** — useful for catching a thread you missed, never for setting status.
3. **When a summary and a grounding doc disagree, the summary wins.** Say so in the report-back.

## Required context (read in this order)

1. `ls -d summaries/*/` — enumerate every session directory. **Directory naming varies by campaign**: obelisk uses numbered dirs (`004/`), Out of the Abyss and ToEE use dated ones (`20260727/`, `20260705/`). Glob `summaries/*/*.md` and look, rather than guessing.

   **Which file in the dir is the session summary — in precedence order:**

   1. `session-summary.md` if present. Use it.
   2. Otherwise `session_YYYY_MM_DD_<title>.md` (e.g. `session_2026_07_05_chapter_32_the_minotaur.md`). This is the **new output name for the gm-assist doc**, and it is a full session summary carrying the same `## Summary` / `## Memorable Moments` / `## Scenes` / `## Locations` / `## NPCs` / `## Items` skeleton as the old `session-summary.md`. Read it exactly the same way.

   A campaign will have both conventions side by side — older dirs on `session-summary.md`, newer dirs on `session_YYYY_MM_DD_*.md`. Resolve per directory, not once for the campaign.

   Ignore `gm-assist-doc.md`, `session_doc.md`, `session-roleplay.md`, `scene*.md`, `consistency_report.md`, and `voice_critique_*.md` — these are downstream renderings or pipeline reports, not the summary of record.
2. **Check for an archive subdir** — `summaries/old/`, and watch for duplicate dirs with a `.old` or similar suffix holding a superseded cut of the same session. Enumerate before reading so you don't read a session twice or mistake a duplicate for an extra session. A fast `head -4` over every candidate file maps chapter numbers to dirs in one call.
3. Every session doc, **oldest first**. The `## Scenes` and `## NPCs` sections carry quest offers; `## Summary` carries the outcome.
4. Any session dir with **neither** of the two filenames above — check for `gm-assist.md` instead. (A dir holding only `session_YYYY_MM_DD_*.md` is not a gap; that file *is* the summary.) A missing summary does not mean a missing session, and quests get handed out in exactly those gaps. (obelisk session 004 had no summary and contained two of the campaign's four paid contracts.)
5. The campaign's opening doc if present (`notes/open.md`, `notes/session1_*.md`) — the founding job usually lives there and nowhere else.
6. The four grounding docs, last, as a cross-check.

### Establish the summary coverage window first

**`summaries/` may not go back to session one.** Out of the Abyss had 60 played chapters and summaries for only 46–60; everything before that lived exclusively in the narrative wing (`docs/chapters/`). Three genuinely open promises — two unclaimed truthful-answer boons from a ghost, an unpaid reward, a completed ritual the grounding docs still listed as unfinished — were all outside the window.

So, after step 3: **note the earliest chapter the summaries cover.** If the campaign started before it, the pre-window history is in `docs/chapters/` (or whatever the campaign's authoritative narrative split is — check its `CLAUDE.md`).

Do **not** read 45 chapter files. Grep them for promise-shaped language and read only the hits:

```bash
grep -rniE "boon|reward|promised|in exchange|owes|agreed to|asked (them|us|the party) to" docs/chapters/ | head -40
```

Then grep the specific proper nouns the later summaries or grounding docs mention as unresolved. Anything you cannot confirm from a chapter file does not go in the handout.

## Match the campaign's existing handout format

**Before writing, look for a player-facing handout this table has already seen.** Check the handouts dir, and ask the GM if one isn't obvious. If the players liked a prior format, that format wins over the template in this file.

The template below is a *default*, not a house style. Out of the Abyss had an established player tracker built from dense tables with a "Your read" column, ⭐ markers on load-bearing facts, and per-part "where you're picking up next" blocks. The quest log was far more useful matching that than following this skill's prose-block shape — the players already knew how to read it.

What to carry over from an existing handout: table-vs-prose density, how suspicion is marked, emphasis conventions, whether it addresses the party as *you* or is written as *we*. A GM-authored tracker addressed to the players says "you"; a quest log kept by a named party member says "we" — adapt rather than copy.

## Open with "We Are Here"

Every quest log must orient the players before presenting the quest list. Immediately after the title, narrator byline, and current-as-of line, include a compact **We Are Here** block answering:

- **Where the party physically is now** — the specific settlement, dungeon area, ship, camp, or other table-start location.
- **Why they are there now** — the immediate purpose that brought them to this place.
- **What they left running elsewhere** — who is holding their previous position and any active situation that matters while they are away. Omit this line when nothing relevant was left behind.
- **Their immediate advantage or constraint** — the piece of positioning players need in order to make their first decision, such as a useful false identity, a deadline, an enemy's mistaken belief, or a failing supply.

This is a present-tense table orientation, **not a recap**. Keep it to roughly three to five sentences or short labeled lines, in the narrator's voice. Do not retell how the party arrived, summarize the previous session, or introduce GM-only context. A player should be able to read this block and immediately answer, “Where are we, what are we doing here, and what is true at the instant play resumes?”

## Method: walk the timeline, log offers, then close them

For each session in order, record two things:

- **Promises opened.** An NPC offered work, named a price, asked a favour, or extracted an agreement. Capture *who asked*, *the terms*, and *what the party was told*.
- **Promises closed.** The party did the thing, or the thing became moot on-screen.

A quest is open if it was offered on-screen and never closed on-screen. Anything else is inference — and inference goes in the report-back to the GM, not in the handout.

**Partial closure is the most common state and the most interesting one.** "Find Iarno Albrek" was not open, and not closed — the party found him, identified him, wounded him, and lost him. That is a third thing, and the log should say so in the party's own terms.

## The leak checklist — run this before writing a line

Player-facing means the document contains only what the party has seen, been told, or reasonably inferred at the table. Before including any item, ask: *when did a player learn this?* If there's no answer, it doesn't go in.

**Never include, under any circumstances:**

- **Module trackers.** Files like `docs/oblesik_tracking.md` are the full published-adventure checklist across every chapter — future villains, unrevealed identities, the ending. Do not read from it for this skill. It will hand you the campaign's biggest reveals in a bulleted list.
- **`docs/npcs/` dossiers and `notes/*_strategy.md`** — these are the NPC viewed from inside their own head.
- **The `## DM Notes` section of `planning.md`** and anything under a "Hidden:" label in a dossier.
- **Secrets held by friendly NPCs.** Daran Edermath being a 500-year-old drow is in `world_state.md`; no player has been told.
- **Extractions.** `distill_extractions/`, `planning_extractions/` are search accelerators over GM material.
- **Mechanical GM state.** Threat-arc scores, encounter CRs, "the party is meant to go here next."

**Do include, because the party genuinely knows it:**

- What NPCs said out loud, including lies the party has not yet caught.
- Reveals extracted under interrogation or exposed by a monster. If a Nothic broadcast Pip's secret to the whole party telepathically, it is player knowledge now, however much Pip wishes otherwise.
- The party's own suspicions, framed as suspicion. "She is not what she pretends to be" is player-facing. "She is Zhentarim" is not.

## Voice: the party's notekeeper, not the GM

Write it as one specific party member's notebook. Pick whoever canonically takes notes — check `docs/party.md` and the voice files for a character who writes things down (Veyra of the Blue Candle, in obelisk, because she was established rereading her notes by candlelight).

This is not decoration. A named narrator solves three problems at once:

- **It bounds knowledge naturally.** A character can only write what they witnessed, so the leak checklist enforces itself.
- **It lets suspicion be stated as suspicion.** "The invitation stands anyway" carries the party's read on Halia without asserting a fact they don't have.
- **It makes the document readable at the table** instead of an administrative list players skim.

Read the narrator's voice file under `voice/` before writing. Match their register — dry, breathless, sardonic. Keep entries short; this is a working notebook, not prose.

If no character plausibly keeps notes, use a plain neutral log and say why in the report-back.

## Output shape

**Resolve the location — do not assume `notes/handouts/`.** Campaigns differ, and a handout filed somewhere the GM doesn't look is a handout that doesn't exist.

```bash
find . -path ./.git -prune -o -type d -name handouts -print
```

Write next to the campaign's existing player handouts if that dir exists (Out of the Abyss keeps them in `notes/handouts/`). Only fall back to creating `notes/handouts/` when the campaign has no handouts dir at all.

Quest logs are immutable session artifacts. **Never overwrite or delete an earlier log.** Name each new file `{session}-{author}-log.md` — session first, so the handouts dir sorts chronologically — using the session identifier supplied by the GM (normally the upcoming session date as `YYYYMMDD`) and a filesystem-safe lowercase author slug, such as `20260830-owlbear-log.md`. Never put the author first: `owlbear-20260830-log.md` scatters a campaign's logs by narrator instead of by date. If no session identifier is supplied, infer it from the session being prepared; if that cannot be done confidently, ask the GM. An older campaign file with a legacy name such as `player_quest_log.md` remains in place and serves only as the base/reference for the new dated log.

```
# Quest Log

*Kept by {narrator}, {one clause establishing why they're the one writing}.*
*Current as of {the last on-screen event, in the party's words}.*

---

## We Are Here

**{Current location}.** {One sentence establishing the party's physical position.}

**Why we're here:** {The immediate purpose, not the campaign history.}

**What we left behind:** {Only active off-site state that matters now; omit if none.}

**Our present position:** {The immediate advantage, constraint, deadline, or misconception shaping the opening decision.}

---

## {The founding job — the one that started the campaign}

### {Quest name in the party's words}
**Who's asking:** {or "Nobody had to ask" if it's personal}
**What we know:** {2-4 lines, only what was said on-screen}
**Where/why:** {the operative unknown}
**Status:** {Open / Urgent / etc, in plain speech}

---

## Paid Work
{Contracts with named patrons and stated terms. Include the actual gold figure
and who negotiated it — players remember the haggling. Note partial progress
explicitly: found-but-escaped, started-but-abandoned.}

## Unfinished Business at {current location}
{Things the party walked away from mid-solve. Barricaded doors, unexplored
levels, monsters left alive behind them. This section is usually the most
actionable and is almost never in the grounding docs.}

## Errands and Offers
{Undelivered goods, standing invitations, quests offered but not accepted,
NPCs owed a follow-up.}

## Our Own Business
{Per-character personal threads. One block per character with a live thread.}

## Things Nobody Has Hired Us For, Which We Notice Anyway
{Unexplained events, unanswered questions, names with no referent. Short
bullets. This is where foreshadowing lives without becoming a quest.}

---

*{One closing line the narrator would write — the pattern they've spotted but
can't name yet. Only if the threads genuinely converge; skip it if they don't.}*
```

Section names should bend to the campaign. The shape is: **the spine, the paid work, the immediate mess, the small stuff, the personal, the unexplained.**

## Steps

1. Enumerate `summaries/*/` (including any archive subdir) and read every session doc oldest-first, resolving each dir's summary file by the precedence rule above (`session-summary.md`, else `session_YYYY_MM_DD_<title>.md`). Check genuine gap sessions for `gm-assist.md`.
2. Note the earliest chapter covered. If the campaign predates it, grep `docs/chapters/` for promise-shaped language and read only the hits.
3. Read the opening doc for the founding job.
4. Build the offer/closure ledger. Note every disagreement with the grounding docs.
5. Run the leak checklist over the candidate list.
6. Pick the narrator; read their voice file. Find and read any existing player handout, and match its format.
7. Write the **We Are Here** block from the final on-screen state: current location, immediate purpose, relevant off-site situation, and opening advantage or constraint. Confirm that it orients rather than recaps.
8. Resolve the output location; write a new `{session}-{author}-log.md`. Preserve every prior log unchanged.
9. **Report back to the GM separately** — see below. This part does not go in the file.

## The report-back is not optional

The handout is a rendering of state; the GM is the only one who can confirm the state is right. End every run with a short list, in chat and not in the file, covering:

- **Contradictions found** — where a grounding doc disagreed with a summary, and which one the log followed. **Report the same error once, at source, naming every doc carrying it.** Pipeline docs copy from each other: the Out of the Abyss run found "Jorlan is Daz's brother" in `world_state.md` and `party.md` when every summary made him the Duskryn *sisters'* brother — one error in three places, not three findings. Also flag when the grounding docs are pinned to a chapter the summaries have already moved past; that reframes every other disagreement.
- **Genuine uncertainties** — things the summaries left ambiguous. The obelisk run surfaced barricaded bugbears that session 006 shut behind a door and session 007 never mentioned again; the log listed them as alive, flagged for the GM to overrule. State the assumption, don't silently pick.
- **Anything omitted as a GM secret** that the GM might have intended the players to have.
- **Continuity noise** — names spelled two ways across summaries ("Forepot" / "Foreput"), NPCs merged or split by transcription error. These belong in the spell-pass glossary.

Do not fold these into the handout as caveats. The players get a clean document; the GM gets the diff.

## What this skill is NOT for

- GM-side thread tracking or "what should happen next" (use `gm-session-prep`)
- An in-world artifact the party *finds* — a letter, notice, ledger (use `gm-handout`)
- Faction intel and who-really-runs-this-town (use `gm-faction-network`)
- Regenerating `campaign_state.md` — that's the CampaignGenerator pipeline, not this skill. This skill never writes to `docs/`.
