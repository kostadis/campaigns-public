---
name: gm-arc
description: Track a campaign's arcs across sessions — sandboxes (places the party lives in for several sessions, with factions and an affordance menu), arcs (storylines with a question, possible beats, rulings and what the party has seen), clocks.md and junctions.md under docs/arcs/. Three verbs. `new` drafts an arc or sandbox for GM confirmation. `record` writes what a played session's summary shows, as a GM-approved delta. `mine` searches the thread pool for plot ideas the players already planted. Invoke as /gm-arc new <arc-or-sandbox>, /gm-arc record [session-dir], /gm-arc mine <subject>, or when the user says "make an arc for…", "set up the sandbox for…", "record last session into the arcs", "what threads touch…". Design and rulings are in gm-assistant/working/arc-tracking/DESIGN.md and DECISIONS.md.
---

# gm-arc

Arcs hold the GM's intent across sessions so that session prep stops rediscovering it. The full design is in `gm-assistant/working/arc-tracking/DESIGN.md`. The rulings behind it, and what was dropped, are in `DECISIONS.md` alongside it. **Read DESIGN.md once per session before using this skill.**

## The two principles this skill exists to enforce

1. ***Arcs drive story; the sandbox is what the players can do to drive story.*** Arcs are the GM's side. Sandboxes are the players' side, as affordances that push arcs.
2. ***Outcomes and hopes are two different things.*** `record` writes **outcomes**: only what the session summary shows. `new`, and the prep deltas, write **hopes**: what the GM intends. **Never write arc text into a grounding doc** (`docs/campaign_state.md`, `world_state.md`, `planning.md`, `party.md`). Never infer that something happened.

## Scope

Run this from inside a campaign directory (`obelisk/`, `Phandalin/`, `out-of-the-abyss/`, `toee/`, `Hillsfar/`, `stormgiants/`). Refuse if you're not in one. Read and write only that campaign. Everything lives in `<campaign>/docs/arcs/`:

```
docs/arcs/
  <arc-slug>.md                  # one per arc
  sandboxes/<place-slug>.md      # one per sandbox
  clocks.md                      # small obligations, minor NPCs not yet promoted
  calendar.md                    # the in-fiction date, and days per chapter
  junctions.md                   # where arcs CAN meet
```

All of these are **GM-owned origin files**. Nothing regenerates them. Formats are in `templates.md`, next to this file.

## Hard rules (every verb)

- **Nothing is written without explicit GM confirmation.** Show a draft or a diff and wait. An unanswered or ambiguous reply is not a confirmation, so re-ask. A delta of more than about a dozen items goes into one Approve / Reject / Discuss artifact, per the repo CLAUDE.md long-queue rule. It never goes as a serial chat queue.
- **Provenance on every line.** Tag it `[TABLE]` (played or locked; cite `Ch. N / scene`), `[GM yyyy-mm-dd]` (a ruling), `[MODULE §x]`, or `[OVERLAY]` (your invention). **You write the tags. The GM never tags anything.** If the GM writes an untagged line, tag it on your next pass.
- **States.**
  - Rulings: `unrevealed` / `revealed Ch. N` / `contradicted Ch. N`.
  - Beats: `pending` / `seen Ch. N` / `dead (why)`.
  - Affordances: `untouched` / `offered Ch. N` / `used Ch. N — outcome` / `dead (why)`.
- **Numbering.** "Ch. N" always means a played session. Write module references as "Module §…".
- **Names.** Resolve every proper noun with `registry_resolve_name` (the canon chain in the repo CLAUDE.md) before writing it. If a name is `not_canon` or `ambiguous`, it goes to the GM. Never pick a spelling yourself.
- **Villain ledgers live in the villain's strategy doc** (`notes/<npc>_strategy.md`, from `gm-strategy-doc`), never in an arc. Arcs link to the strategy doc. If the villain has no strategy doc, **ask the GM** where the ledger goes for now. That is open question Q4 in DECISIONS.md.
- **Evil Overlord.** Any villain beat you draft must pass `gm-assistant/references/evil_overlord_dnd.md`. A villain acts only on facts in its ledger, each with a named source.
- **Thread firewall.** Pool threads are suggestions. None enters an arc unless the GM pulls it in by name.
- **Arcs hold all rulings that touch them**, both world-fact and table-procedure (GM ruling R1c).
- **Staging stays in prep.** Arcs hold *possible beats* with gates. Which room, which line, which handoff belongs in `notes/session_prep/`.

---

## `/gm-arc new <name>`

Drafts one arc or one sandbox.

1. **Classify, and ask if it's unclear.** A sandbox is a place the party will spend several sessions in, with factions. It has no question. An arc has a question. If what the GM named has no question and is not a multi-session place, it is probably a **clock**. Propose a `clocks.md` row instead.
2. **Read the sources:**
   - the most recent `notes/session_prep/*.md`;
   - any `notes/gm_rulings_*.md`;
   - `docs/campaign_state.md` and `docs/planning.md`;
   - the summaries the arc touches, from `summaries/<session>/session-summary.md`, which is authoritative;
   - linked strategy docs;
   - existing `docs/arcs/` files, so you link to them and don't duplicate them;
   - the module section, if the campaign has one in `docs/background/`.
3. **Draft from `templates.md`.** For an arc:
   - Fill **Seen by the party** from the summaries only, with a chapter citation for each entry. If it's empty, say so; that is the payoff flag.
   - Fill **If nobody intervenes** as `[OVERLAY]`, unless the GM has ruled it.
   - Set `driver: players` only when the summaries show the players pushing it on their own initiative.
   - Draft **possible beats** with gates, and with states taken from the summaries.

   For a sandbox:
   - Draft the faction roster (state · want · clock).
   - Draft standing rules, **party goals** (players' own words, with a chapter citation), the affordance menu (each entry with the arcs it pushes, and labelled *not exhaustive*), and the arcs running here.
4. **Run `mine <name>`** and list up to 5 pool threads under the draft as *"plot ideas the players already planted"*. They are not part of the file unless the GM pulls them in.
5. **List junctions.** These are people, objects or places this arc shares with existing arcs. Propose any new `junctions.md` rows.
6. **Present the draft and the open decisions.** Wait for the GM to confirm or correct, then write. Update `links:` in any arcs the new one connects to, and show those edits in the same diff.

## `/gm-arc record [session-dir]`

Runs after a session's `summaries/<session>/session-summary.md` exists. If no session dir is given, use the newest one past the lowest `as_of` in `docs/arcs/`. **Record writes outcomes only.**

1. **Read** the session summary (authoritative), every active arc, sandbox, `clocks.md`, `calendar.md`, `junctions.md`, and the linked strategy docs.
   - **Also read the session's live notes** (`notes/session_prep/*_live_notes.md`), if there are any, **as leads only.** They are a map of where to look in the summary: what the GM reported, and which in-session suggestions may have been used. **Nothing is recorded from them unless the summary shows it** (GM ruling P1).
2. **Build the delta.** Every entry cites `Ch. N / scene`.
   - **Beats:** pending → `seen Ch. N`, or → `dead (why)` when play removed a gate. A dead beat is never carried forward or re-offered.
   - **Seen by the party:** new on-screen sightings for each arc.
   - **Affordances:** state changes. **Unlisted player actions are appended** to the sandbox menu, not treated as off-plan.
   - **Clocks touched:** new state, `last touched: Ch. N`.
   - **Calendar** (when `calendar.md` exists): a proposed row for the chapter. Give the days it covered, its end date and how it was dated (`stated` / `counted` / `travel` / `?`), and quote the summary lines the count rests on. New routes go in the Travel table. A count is a precision decision: the GM rules it, and an unruled row stays `?`. Give any clock that just got a start day its `Due` date. Recount every check (a line that counts time, like "seventy-three days"), and flag any that no longer holds. Flag any GM-approved date the new row moves. The lessons from Phandalin's backfill are in `templates.md`, under *What the Phandalin calendar taught*.
   - **Rulings:** reveal-state changes (`revealed Ch. N` / `contradicted Ch. N`). A contradicted ruling is flagged to the GM. Never rewrite it to fit.
   - **Villains who gained a source:** a ledger entry for that villain's **strategy doc** (fact · source · Ch. N). Add one only if the summary shows the villain gaining the information.
   - **PC scores** (`docs/tracking/`): moves only on recorded player actions, never on staged scenes.
   - **Party goals:** anything the players said they want, in their words.
   - Bump `as_of` on every arc and sandbox reconciled.
3. **Flags** go at the end, as information for the GM, not as edits:
   - clocks untouched for 2 or more chapters, and arcs untouched for 4 or more;
   - arcs with nothing in *Seen by the party*;
   - PCs with no `driver: players` arc (a target, not a rule; the GM decides);
   - **at most 3 orphan threads**: pool threads resurfacing in this chapter or recently that no arc claims (see `mine`);
   - any [OVERLAY] the session made obsolete;
   - **anything play contradicts in the module or a sandbox:** a fact said or shown at the table that disagrees with a `[MODULE §x]` or sandbox line (e.g. Snarl given to the hobgoblins when the module puts him with Grol). Show both, cite each, and ask: misinformation in-world, a slip at the table, or new canon? **Never auto-fix it in either direction** (GM ruling P2).
4. **Present the delta and wait** (artifact if more than about 12 items), then apply exactly what was approved. Record in the arc files that the delta was GM-approved, with the date.

**Precision check.** "Was this beat seen?" and "did this villain gain a source?" are attribution decisions. Never mark one without a summary citation. When the summary is ambiguous, ask.

**What record does NOT do:** it does not advance clocks nobody touched. ADVANCE happens at the next prep, with one GM question per untouched clock (`gm-session-prep`). If the GM runs `record` with no prep planned, list the untouched clocks and offer to ask about them now. Don't assume they ticked.

## `/gm-arc mine <subject>`

Read-only. Writes nothing.

1. **Pool source,** in order:
   - `docs/summary_native/<range>/state/notes/*.out.md`: the `## Threads` sections, formatted as `- [OPENED|ADVANCED|RESOLVED] **Title** — text [ch NNN / scene]`. Use the newest range.
   - Otherwise `docs/ensemble/threads.md`.
   - If neither exists, say so and stop.
   - Read through `git show HEAD:<path>` when the checkout is sparse.
2. **Search** for the subject and its registry aliases (`registry_resolve_name`). Group the hits by thread title. The latest status wins. Down-rank RESOLVED threads, and threads untouched for 6 or more chapters, but never drop them.
3. **Output** up to 10 threads, as *"plot ideas the players already planted"*: title · latest status · one line · citations · which arc claims it, if any (by matching against arc `Threads pulled in` and the arc topics). Unclaimed threads that keep resurfacing are the orphan signal.
4. **Stop.** Promotion happens only when the GM pulls a thread in by name, through `new` or a prep delta.

## Relationship to other skills

- **`gm-session-prep`** reads `docs/arcs/` and runs ADVANCE. It seeds its mandatory blocks from arcs, and ends with a proposed arc delta, which goes through the same GM-confirm gate as this skill.
- **`gm-strategy-doc`** owns each villain's ledger, position and next move (no phases). `record` proposes ledger entries to it.
- **`gm-faction-network`** is the right tool for building a sandbox's faction roster in depth.
- **`/grounding-refresh`** is the outcome side. Nothing here feeds it text.
