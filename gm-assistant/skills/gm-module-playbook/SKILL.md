---
name: gm-module-playbook
description: Turn a published-module section into a table playbook that says, in order, what to say and when, exactly as the module wrote it, with no campaign overlays. Read-aloud text verbatim, triggers, NPC behaviour as written, checks with the printed DCs, branches, how the scene ends, an "easy to miss" list, and what the module leaves unsaid. A deterministic script numbers every paragraph, read-aloud box, sidebar, list item and table of the section, and checks that the playbook cites every one, quotes read-aloud verbatim, and prints no DC the module doesn't. Use when the GM says "how does the module run this", "what does the book say to do here", "play it straight", "no overlays", or before a session that touches a module section. Invoke as /gm-module-playbook [source] [section or chapter].
---

# gm-module-playbook

The prep says what *this campaign* does. This skill says what *the book* does, so the GM
can see the module's own sequence, wording and conditions, and nothing gets missed
because the prep didn't mention it.

*Why (GM, 2026-11-03): the Ch. 74 prep worked at the table, but the module itself had a
paragraph the GM missed: Bruenor's Plan read-aloud (OotA 339), the speech that names
the Zhentarim, Mantol-Derith, Ghazrim DuLoc and the map to Gravenhollow. A prep is built
from the overlays; a paragraph the overlays never touched is invisible in it. First
playbook: `out-of-the-abyss/notes/module_playbooks/OotA-339-events-in-gauntlgrym.md`.*

*Why the intent section (GM, 2026-11-03): a running order says what to do, but not what
the chapter was for, so the GM can't tell which parts carry the design and which can bend.
Example: `OotA-34e-mantol-derith.md`, "How the module means it to play".*

## What decision this removes from the GM

None. The script picks no content: it extracts and numbers the module's text, then checks
coverage. The model renders that text into running order; the GM reads the playbook
against the numbered source before using it. Nothing downstream consumes the playbook
automatically.

## Hard rules

- **No overlays.** Read only the module text (the extracted source below and, for stat
  blocks, the 5etools MCP). Do not read campaign prep, notes, strategy docs, arcs,
  dossiers, the registry or the summaries while writing. No campaign NPC, ruling,
  change or "in our game" appears in the playbook. If the GM wants the comparison, that
  is a separate step (step 8), done after the playbook passes.
- **Every unit is cited.** Each paragraph, read-aloud box, sidebar entry, list item and
  table gets its `[§id.n]` somewhere in the playbook: in a beat, in *Easy to miss*, or in
  *Background only*. The check fails on any uncited unit. Background is a valid home;
  silence is not.
- **Blockquotes are verbatim module text, and only that.** Read-aloud goes in `>` lines,
  copied exactly (you may cut with `…`). Anything paraphrased, summarised or suggested is
  a plain bullet, never a blockquote. Inline "quotations" of four words or more must be
  verbatim too. The check fails any it can't find in the source or context.
- **Numbers are the module's.** A DC, damage figure, distance or count appears only if the
  module prints it here. When the module calls for a check without a DC, write
  "the module gives no DC". Never supply one. The check fails a DC the source lacks.
- **Silence stays silent.** Where the module doesn't say what happens (no failure result,
  no NPC answer, no timing), list it under *The module doesn't say*. Do not fill it.
- **Names as printed.** Write names the way the module prints them. This is a reading of
  the book, not campaign canon. Don't normalise them toward the campaign's spellings, and
  don't use the campaign's spellings here.
- **Intent is the module's, or labelled.** The intent section states what the book says
  the part is for. An inference is marked **Reading:** and cites the units it rests on.
  It never brings in outside lore or the campaign.
- **Never invent.** No `[INVENTED]` content belongs in a playbook. If you're tempted to
  add something, it goes in *The module doesn't say* as a question.

## Steps

### 1. Pick the section

Ask the GM (or take from the arguments) the module and the part of it: a scene, a
section, or a whole chapter. Resolve it with the 5etools MCP: `search` with the source id
(e.g. `OotA`) or `get_toc`. Show the GM the section names and ids you'll use, and confirm
before extracting. A chapter is fine (OotA Ch. 8 is 134 units); for a long chapter, offer
one playbook per section so each stays readable at the table.

Include the sections the scene depends on: a feast that "can be interrupted by an option
from *Enemies Among Us*" needs that section too. Name these to the GM; don't add them
silently.

### 2. Extract

```bash
P=<workspace>/gm-assistant/skills/gm-module-playbook/module_source.py
OUT=notes/module_playbooks/<source>-<firstid>-<slug>
python3 $P extract --source <SOURCE> <id> [<id> ...] --campaign-dir . -o $OUT.source.json
```

Run it from the campaign directory. It finds the module JSON in the campaign's 5etools
runtime (`~/.5etools-mcp-runtime/<campaign>/`); pass `--file <adventure.json>` to override.
It reads the raw JSON, so nothing is truncated (the MCP's `get_section` cuts at 10,000
characters) and read-aloud boxes, sidebars and tables stay separate units. It writes
`$OUT.source.json` (for the check) and `$OUT.source.md` (a readable copy with every unit
id). Both are replicas of the module: never edit them, re-extract.

Then extract the **context**: the opening units of the section before and the section
after, which is where the module says what this part sets up and what the next part
expects to receive. Reuse an existing playbook's `.source.json` when one covers the
neighbour.

```bash
python3 $P extract --source <SOURCE> <next-id> [<prev-id>] --max-units 9 -o $OUT.context.json
```

### 3. Read the whole source

Read `$OUT.source.md` start to finish before drafting, then `$OUT.context.md`. Mark every conditional sentence
("if the characters…", "unless…", "when…", "after…"), every sidebar, and every
instruction buried mid-paragraph. Those are where missed paragraphs live.

### 4. Write the playbook

Write `$OUT.md` in this shape:

```markdown
# <Section name> — as the module runs it
*Module: <title> (<source>), sections <ids>. No campaign overlays. Source: [<file>](<file>.source.md).*

## At a glance
What this scene is for, in the module's terms. Who is present. What the players can get
from it. One short paragraph, cited.

## How the module means it to play
What the book says this part is for, built from its own text and its neighbours:
- **Where it sits:** what the previous part set up, and what the next part assumes the
  party brings. Quote the next chapter's opening when it names the hand-off. [§…]
- **The promise and the twist:** what the players are led to expect, and what they find.
- **The goal, and what stands in the way.**
- **The situation on arrival:** what is already in motion. [§…]
- **The shape:** linear, hub, sandbox, mystery, siege; where the paths converge.
- **The leads:** each lead to the answer, step by step, and where they end.
- **The clock:** what happens if the party does nothing, and which choice decides the outcome.
- **The theme,** when the text shows one across many units.
- **Fail-safes:** what the module provides if the party misses the goal (often in the
  next chapter).
- **What it hands on:** the items, knowledge, allies, level and route the next part expects.

Every line cites. Where the module states a purpose, quote it. Where you infer one
from several units, start the line with **Reading:** and cite every unit it rests on.
A reading draws only on the cited text; no outside lore, no campaign.

## Starts when
The trigger, as written. [§…]

## Running order
### 1. <beat name>
- **Do:** what the GM does or describes. [§…]
- **Read aloud:** [§…]
  > verbatim text
- **<NPC> as written:** what they want, what they say, what they answer, what they refuse. [§…]
- **Checks:** <skill>, DC <n> as printed: on a success …; on a failure … (or "the module gives no failure result"). [§…]
- **If …:** each branch the module gives. [§…]
- **Next:** what moves the scene on. [§…]

### 2. …

## Ends when
How the module closes the scene, and where it points next (section name and id). [§…]

## Easy to miss
Every conditional, sidebar, optional event, and one-line instruction that a skim would
lose, each with its trigger and its citation. This list is the reason the skill exists.

## The module doesn't say
Questions the text leaves open (no DC, no failure result, no NPC reaction, no timing).
Questions only, no answers.

## Background only
Units that are GM-facing lore, not table instructions, one line each with the citation.
Nothing here is said aloud.

## Creatures and stat blocks
Each creature the section names, with count and where it appears, as printed. Link the
stat block by name; don't copy it.
```

Order beats by when they happen at the table, not by where they sit on the page. When the
module's order and its sequence differ (an "at any time" event, a sidebar that applies
mid-scene), put the instruction where it fires and cite it there.

### 5. Check

```bash
python3 $P check $OUT.source.json $OUT.md --context $OUT.context.json [--context <other>.source.json]
```

Context units may be cited and quoted, but need not all be.

Fix every `UNCITED`, `NOT VERBATIM` and DC finding, and re-run until it prints `PASS`.
Don't game it: citing a unit in a beat it doesn't support is a wrong citation, and the GM
will read the source beside it. If a unit really is background, put it in *Background
only*.

### 6. GM review

Give the GM the playbook and the source copy side by side. Report the unit counts and
how many items are in *Easy to miss* and *The module doesn't say*. The GM reads it
against the source. Corrections go into the playbook, then the check runs again.

### 7. Optional: an experienced GM's take

When the GM asks how *they* should run it, not only what the book says. Do this only after
step 6. The playbook gives the module's facts and intent; this step adds table craft.

Hand it to a **fresh subagent** (general-purpose), so it reads the playbook cold rather
than anchored on your drafting. Brief it as a veteran GM who has run this module, who
reads the playbook, its source and its context, and writes `$OUT.gm-take.md`:

```markdown
# <Section> — how I'd run it
*An experienced GM's proposals, built on [the playbook](<file>.md). Advice, not module text.
Every claim about the book cites it; anything the book doesn't contain is tagged [INVENTED].
The GM rules on all of it.*

## The pitch            what the table should feel, in two sentences
## Before the session   what to have ready: maps, NPC cheat lines, a timeline
## Pacing               session-sized chunks, where to break, rough time per chunk
## Opening              the first ten minutes: how to land the promise and the twist
## Keeping them moving  signposts, pressure, who to put in front of a stuck party
## The clock, made concrete  a proposed GM-side timeline for events the book leaves untimed
## The leads            which leads are fragile, and a backup route to each answer
## The big scene        how to stage the climax (positions, who acts when, how to keep it readable)
## The companions       what the expedition NPCs do here
## Answers to "the module doesn't say"  one proposal per open question, each for the GM to rule
## What to cut, what never to cut  the load-bearing parts vs the optional ones
## Pitfalls             how this chapter usually goes wrong at the table
```

Rules for the take:
- **It never contradicts the module silently.** A proposal that changes what the book
  says starts with **Change:** and cites the unit it changes.
- **Facts cite; invention is tagged.** A statement about the book cites `[§…]`. A name,
  number, timing or detail the book doesn't give is tagged `[INVENTED]`. A proposed DC
  carries `[INVENTED]` or "suggested" on its line.
- **No campaign.** Still module-only; how the campaign differs is step 8.
- **Every proposal is the GM's to accept.** Present the take as options with reasons,
  never as rulings, and never apply any of it to prep or canon.

Check it: `python3 $P check $OUT.source.json $OUT.gm-take.md --advice --context …`
(citations valid, quotes verbatim, no untagged DC). Then give it to the GM.

*Why (GM, 2026-11-03): the playbook said what the book says and what it's for, but not how
to run it. A Gemini summary that did give that intuition also mixed in invented
instructions with no way to tell them apart. The take gives the intuition and keeps the
seams visible.*

### 8. Optional: compare with the prep

Only if the GM asks, and only after step 6. Read tonight's prep and list, per beat, where
the prep differs from the module: changed, dropped, or added. List them; don't resolve them.
A module paragraph the prep never mentions is the finding that matters most. Write this in
a separate file (`$OUT.vs-prep.md`), so the playbook itself stays overlay-free.

### 9. Corpus

`notes/module_playbooks/` holds published module text, which stays outside the palace. The
first time the folder is created, run `/corpus-gaps` and recommend the GM rule the folder
out (published modules are reached through the 5etools MCP). The GM rules; you don't.

## Output

- `notes/module_playbooks/<source>-<id>-<slug>.md`: the playbook (origin, checked).
- `….source.json` and `….source.md`: the extracted module text (replicas, re-extract to update).
- `….gm-take.md`: only when step 7 runs (advice, checked with `--advice`).
- `….vs-prep.md`: only when step 8 runs.

Commit only when the user asks, one campaign per commit.
