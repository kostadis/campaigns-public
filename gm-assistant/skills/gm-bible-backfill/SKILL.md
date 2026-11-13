---
name: gm-bible-backfill
description: Turn a campaign's hand-written bible (one long markdown of chapters, no recordings) into GM-ruled enhanced summaries, a ruled Harptos calendar, published docs/summaries, a players' calendar page and GM-signed NPC dossiers. A staged runbook, with one GM checkpoint and one PR per stage. It records what each stage produces, how it is checked, and the traps hit on the first run (stormgiants, 2026-11-06, PRs #629–#633). Invoke as /gm-bible-backfill <campaign-dir> [stage], or when the user says "do the stormgiants process for <campaign>", "backfill summaries from the bible", or "start <campaign>'s bible from the top".
---

# gm-bible-backfill

The end-to-end process first run on stormgiants (*The Hero's Journey or The War of the Giants*, 86 chapters) on 2026-11-06. It turns a bible into:

- `docs/chapters/`, the split;
- `summaries/NNN-<slug>/session-summary.md`;
- `docs/arcs/calendar.md`;
- `docs/summaries/`;
- `notes/handouts/player_calendar.*`;
- `docs/npcs/<slug>.md`, GM-signed NPC dossiers (Stage 11).

Every stage is GM-ruled before the next one runs.

**What this removes from the GM:** nothing. Claude finds things, counts them, drafts them and applies them under count guards. Every spelling, identity, date and wording is the GM's ruling, made on a review page.

## Run state: start from where you are

Before doing anything, work out which stages are done:

```bash
cd <campaign>
ls docs/chapters | wc -l                              # Stage 3 done?
ls -d summaries/[0-9][0-9][0-9]-* 2>/dev/null | wc -l # Stage 4 done?
ls summaries/chapter_enhance_review/ 2>/dev/null      # consistency/, calendar/, typos_* → Stages 5–8
test -f docs/arcs/calendar.md && grep -c 'ruled \[GM' docs/arcs/calendar.md
ls docs/summaries | wc -l                             # Stage 9
test -f notes/handouts/player_calendar.json && echo "Stage 10 done"
test -f docs/npcs/summary_native/publish_log.json && echo "Stage 11 started"   # NPC dossiers
git log --oneline -- <campaign> | head -20
```

Tell the GM which stage you are resuming at and why, then start there. Each stage ends in its own commit and PR (one campaign per PR), merged only when the GM says "ship".

## Standing rules (all from the workspace CLAUDE.md; they bit on the first run)

- **Origin vs replica:**
  - The bible is the origin.
  - `docs/chapters/` is a replica: re-split after every bible edit, never hand-edit it.
  - `docs/summaries/` is a replica of `summaries/`: republish it, never hand-edit it.
  - Summaries are an origin of their own. Mirror every bible fix into them.
- **Names:**
  - Every proper noun is checked against the canon chain: `config/party.yaml` → glossary → `docs/entity_registry.yaml` → dossiers → known additions.
  - Changes are shown before → after. Contested ones are spelled letter by letter (the GM is dyslexic).
- **Review volume:** more than about 12 rulings go on one review artifact:
  - build it with `~/.claude/skills/_shared/review-artifact/build_review.py`;
  - publish it with `capabilities {"artifact":{}}`;
  - read it back with an Artifact read using `path:"index.html"`, then `read_decisions.py`.
- **Reading the verdicts back:**
  - **Unmarked cards are re-asked**, never defaulted.
  - **Discuss notes** are confirmed when they are ambiguous, or when they would invent canon.
- **Count-guarded edits:** every bible replacement asserts its expected count. Scope it to the chapter: split on `^# Chapter N`, then replace inside the block. A bible-wide replace of a short string ("Orsik", "Unla Key") matched 3,001 times on the first run. Match headings as whole lines.
- **Backups:** back up the bible to the scratchpad before each apply pass, and diff against the backup afterwards.
- **After every bible edit:**
  1. Run `split_chapters <bible> --output-dir docs/chapters`.
  2. Split again into a scratch directory and run `diff -rq` against `docs/chapters`. Expect no differences.
  3. Re-run the verifier on every summary.

## Stages

### 0. Import the bible and create the campaign directory (when it is new)
- The bibles are Google Docs. Google Drive is mounted at `/mnt/g/My Drive/`. Ready-made Markdown exports live in `Adventure Stories/Markdown/` (find them with `find /mnt/g -maxdepth 4 -iname '*<word>*'`). Compare the export's mtime with the Doc's last edit; if the Doc is newer, ask the GM to re-export. The Drive MCP can't fetch these: a single read is too small for docs that run to tens of MB with images.
- Copy each export **unchanged** into `<campaign>/docs/source/` and record its sha256.
- Several books make one bible: get the GM's ruling. Then build `docs/<Bible>.md` with a count-guarded script kept next to the sources (`docs/source/build_bible.py`). The script applies the structural rulings:
  - promote plain chapter-title lines to `# ` headings;
  - drop duplicated title lines;
  - demote stray top-level headings to `##`.

  It must fail unless the chapter headings come out as exactly 1…N, in order.
- Chapters with a title and no text (`Gap`, `Secret`) are kept as placeholders if the GM rules so. Their summary folders get a `NOT_WRITTEN.txt`; `publish_sumamries` reports them.
- **The splitter's heading prefix:** if the headings are `# NN – Title` rather than `# Chapter NN`, pass `--prefix '# '`. The splitter still checks that each heading's number matches its position.
- Reference: curse-of-strahd, 2026-11-06 (two books, 46 chapters).

### 1. Module inventory and entity registry
- If the campaign runs a published module: run `/gm-module-inventory`, which writes `docs/background/<module>-inventory.md`, then import it into `docs/entity_registry.yaml`.
- The GM rules identity: merges, distinct pairs, approved aliases.
- New campaign NPCs from the bible go through a "New NPC" review page.
- Re-project with `/home/kostadis/.venv/bin/registry project .` and `registry check .`.
- Reference: stormgiants `0fdba44ad`.

### 2. Bible proper-noun spelling, then the ordinary-word spell check
- **Proper nouns:** check them against the canon chain and the module (5etools `get_section`). A PC's spelling comes from the character sheet or `party.yaml`, never from the bible's majority usage ("Unla Kee" → **Unla Key**). Apply count-guarded. Reference: `c072abae8`.
- **Ordinary words:** run the spell check in rounds, with GM rulings, including month names (`Taraskh` → **Tarsakh**). Approved names go into the registry. Reference: `8034cef05`.
- Don't re-split yet if more passes are coming.

### 3. Split into chapters
- Run `split_chapters <bible> --output-dir docs/chapters` (add `--prefix '# '` for `# NN – Title` headings). Files are named `chapter_NN_<slug>.md`, zero-padded to 2 digits.
- First check the bible's chapter headings:
  - broken headings;
  - numbering that skips or repeats;
  - **duplicate chapters**. Stormgiants' Ch. 55 was a copy of Ch. 53. It was removed and the chapters after it renumbered.
- Compare any duplicate in full before removing it. The GM rules on the renumbering.

### 4. Enhanced summaries
- Use the `chapter-enhance` method (`~/.claude/skills/chapter-enhance`). Output goes to `summaries/NNN-<slug>/session-summary.md`, with three-digit NNN matching the chapter number.
- **Gate:** run `verify_enhanced.py --chapter docs/chapters/chapter_NN_* --summary summaries/NNN-*/session-summary.md` and require `RESULT: CLEAN` on all chapters.
- Hold questions until the whole batch is done: names, unnamed-but-identifiable people, typos. Put them on one name-review page. Stormgiants had 153 cards.
- Apply the rulings to the bible, then re-split and re-verify.
- Keep `applied.md`: verdict counts, Discuss notes applied straight from the note, and follow-ups.
- Reference: `a8572aec3`.

### 5. Cross-chapter consistency pass
- Run a multi-agent check: 6-chapter windows, long-range entities, timeline. Verify each finding's quotes against the files.
- **Summary-only slips** (wrong pronoun, wrong speaker, slips from the bulk edit) are fixed in the summaries. Where the chapter names no one, remove the attribution; don't reassign it.
- **Bible-level findings** go on a review page. Hold the timeline cards for Stage 6.
- Needs-GM items go 1x1 in chat. Stormgiants had 8: Ch. 82 fireball, whale vs shark per the module key, Thuul.
- Reference: `86bcd9897`, files under `summaries/chapter_enhance_review/consistency/`.

### 6. Calendar (`docs/arcs/calendar.md`, GM-owned)
- **Build the rows:**
  - Gather the time evidence: date headers, "the next day", "two weeks", travel distances. Turn it into rows (Ch. / Days / Starts / Ends / How dated / Basis / Source / Status), a Travel table and a Checks table that recounts every line that counts time.
  - **Find the GM's fixed point first.** For stormgiants it was the narrative deadline: the party reaches Silverymoon just before Bob's 30 days run out, so the fight is the night of 23 Eleint. Lay the calendar around that fixed point, not only from the start.
- **Conflicts:** list them as K1…Kn. For each, give both sides, the lines each side rests on, and the options. The GM rules each one.
- **Paces:** module paces where the bible is silent (SKT ch. 11: cloud castle 24 mi/day, airship 192 mi/day).
- **Harptos placement** (I got this wrong once, so check):
  - Greengrass falls after Tarsakh.
  - Midsummer, and Shieldmeet in years divisible by 4, fall after Flamerule.
  - **Highharvestide falls after Eleint** (not after Eleasis).
  - Feast of the Moon falls after Uktar.
  - Midwinter falls after Hammer.
- **No in-world calendar** (Curse of the Hags: Barovia is tied to no realm). Ask the GM for the system first; there it was "Days in Barovia". Anchor Day 1 on a GM ruling (K0: the night the mists take the party), count every row as `Day N`, and write each summary's Date line as `Days N–M in Barovia`. Empty chapters ("Gap"/"Secret") still get a row saying what they must cover.
- Expect 2+ review rounds. A ruling on one stretch frees others to move ("now that we fixed 55-65, we can move things earlier or later").
- Reference: `6e5ed0e89`, files under `summaries/chapter_enhance_review/calendar/`. Day-count example: Curse of the Hags `3e69162e0`.

### 7. Header rewrite and dated summaries
- Rewrite the bible's date headers to match the ruled calendar. Edits are scoped to a chapter: the same header text appears in several chapters (one matched 4 times).
- Show each chapter's lines on a review page with struck and inserted text.
- Set every summary's `Date:` line from calendar.md: `Date: <range> 1492 DR (from \`docs/arcs/calendar.md\`, ruled by the GM <date>)`. Patch stale dates in the summary bodies too.
- Re-split and re-verify.
- Ships with Stage 6.

### 8. Typo pass, held rulings, unnamed people
- **Typo key:** each item records chapter, before, after and reason. Put them on a review page with alternatives where there are any.
- **Apply:**
  - Scope every edit to its chapter.
  - Use line anchors for headings, block replace for short fixes inside the text.
  - Never write the reviewer's hedge into the bible (an "(if a typo)" was once inserted).
- **Bulk approval:** with 200+ fixes, the GM may ask to "auto approve the one word slips". Define it strictly and say so: one word changed, not a name or capital, not flagged by the agents as possible voice. Write the list to `typos_auto_approved.md` and put everything else on the page. Curse of the Hags: 88 auto, 155 on 86 cards.
- **Mirror into the summaries**, then re-verify. Fix leftover old spellings that the verifier flags.
  - Match quote marks loosely but **write back the summary's own style**: replacing `"` with the card's `“` breaks the verifier's quote pairing.
  - Summaries often quote a fixed line with different trailing punctuation (`"previous Major,"`). Run the verifier, read each failing `quote:`, and fix those by hand.
  - Short `before` strings can match more than once; check every multi-match (e.g. "lays on hand" must not become "handss").
- **Unnamed-people queue:** publish it as a visibility page even when the GM chooses "leave as is": "so I can see what I am choosing to not review". The GM also wants a kept record: write `notes/unnamed_characters.md` (each person, the chapter evidence, status "left unnamed", none of it canon).
- **Split-personality or shared-body PCs** (Curse of the Hags: Marron the Paladin and Merrin the Cleric, one aasimar). Spelling-pass rulings by letters alone are provisional. Before the scan, ask the GM three framing questions: what decides the name (who is in control), what happens before the second name exists (keep the first), and pronouns (change only where they mean that PC). Then one agent per chapter group tracks control (class cues, explicit switches) and flags only mismatches with cue quotes and a confidence. High-confidence pronoun fixes apply under the ruling; everything else goes on cards (guess: change high/medium, keep low). Reference: `21db6d81f`, `summaries/chapter_enhance_review/aasimar/`.
- **Name changes reach summary prose, not just quotes.** After mirroring exact quotes, find summary sentences that retell a changed line (old name + 3 or more of the line's distinctive words in one sentence), check each by hand, and fix them; the verifier only checks quotes. Combined entries ("Marron proposes …, casts …, sacrifices …") may need splitting between the two names.
- Reference: `0eff74438` (`typos_applied.md`).

### 9. Publish the summaries
- Run `scripts/publish_sumamries/publish_sumamries <campaign> --dry-run` first, then without `--dry-run`.
- The script copies the summaries, reformats them and numbers the scenes.
- Folders named only by a date (e.g. `summaries/20250226`) have no chapter number and are skipped. Report them.
- Reference: `537804f28`.

### 10. Players' calendar
- Run `/gm-player-calendar`. Draft one event per ruled row and put them on a review page. Split a row that covers two places (Ch. 17–18: the hags, then dinner at Strahd's).
- For a day-count calendar use `"system": "days"` with `from_day`/`to_day` (added in #645; Curse of the Hags first).
- Check every quote in the event text against the bible, and flag every wording of your own on its card.
- Publish with icon `calendar`, then write the URL into `notes/handouts/player_calendar.json`.
- Reference: `149b68fb8`, https://claude.ai/artifact/AghHa74faiREBWh9Bq8Qd9. Day count: Curse of the Hags `450cf9eb4`, https://claude.ai/artifact/UU1tgfMiFJ7BLTQzbuDWyd.

### 11. NPC dossiers (summary_native)
Built from the published `docs/summaries/` (Stage 9), so run this stage last. The full reference is `~/src/CampaignGenerator/docs/cli/npc_dossiers_howto.md`. First run: drow-empire, 2026-11-13 (96 NPCs, PRs #716 and earlier).

**What this removes from the GM:** nothing. Linking is deterministic. The model drafts the prose, a verifier checks every citation, and the GM signs each exact draft on a review page. `npc-publish` refuses anything unsigned.

- **Setup:**
  - `SN=/home/kostadis/.venv/bin/summary_native`. Every call needs `CG_BACKEND=claude-code` or `CG_BACKEND=codex-cli`, or the backend guard refuses, even `--help`. Never fall back to the API key unless the GM asks.
  - `$SN authority init --campaign-dir .`, then `$SN review init --campaign-dir .`. Sign-off refuses with `REVIEW_AUTHORITY_REQUIRED` until both have run. Commit `docs/authority*` and `docs/reviews/`, but never `docs/authority/.lock`.
- **Link first, then rule what it withholds:**
  1. `$SN build --since 1 --until N --force`, then `$SN npc-link --since 1 --until N --force`. Read `docs/npcs/summary_native/ch001-NNN/link_report.md`.
  2. Rule on every withheld form with the GM before drafting:
     - ambiguous forms;
     - one-word generic names (Major, Tanner, Empress) → `link_rulings` in `docs/summary_native/canon.yaml`, `safe` or `never`;
     - NPCs whose registry `type` is wrong (deities typed `deity` get no dossier; drow-empire's GM moved four to `npc`);
     - a name a summary heading uses that the registry lacks.
  3. A mismatch that is really a bible error goes back to the bible and the summaries: fix it in the origin, re-split, re-verify and republish, then re-link. On drow-empire, Freedahl was named as a place where the text meant his city, Plagueridge Rampart.
  4. The PCs: ask the GM whether they get dossiers. For a finished campaign, drow-empire's GM said yes: "now they are NPCs". In that case there is no `players.yaml`.
  5. Re-link until the report shows 0 ambiguous forms and 0 unruled generic forms. Commit the rulings as their own commit.
- **Draft:**
  - Trial one NPC first (`npc-draft --name X`), read it, then `npc-draft --since 1 --until N --all`. The GM picks the backend and model; drow-empire used `--backend codex-cli --model gpt-6.1-sol --codex-reasoning-effort medium`.
  - The run drafts, verifies and composes in one go. With codex-cli `--parallel` did not parallelise: about 50 s per NPC, roughly 90 minutes for 96. Run it in the background.
  - Re-running `--all` redrafts only NPCs whose evidence or authored file changed (`skipped (unchanged)`). Use it after any re-link to find what moved.
- **Review (always an artifact; this is well over 12 rulings):**
  1. Build a selection JSON, `{"dossiers":[{"id","npc","draft_path","evidence_path","summary_paths"}]}`, one entry per `draft/npc_*.md` (skip `.verify.md`). `summary_paths` are the `docs/summaries/NNN-*.md` files for the draft frontmatter's `chapters:`. If an NPC has an authored file, add `"manual"`: its `manual` list of strings, not the path.
  2. `$SN review create --campaign-dir . --kind npc_verification --selection sel.json --json`.
  3. `KIT=~/.claude/skills/_shared/review-artifact`, then `python3 $KIT/npc_review_items.py docs/reviews/<id> --campaign . --out items.json` and `python3 $KIT/build_review.py --in items.json --out page.html`. Publish it with `capabilities {"artifact":{}}`.
     - The page has one sign-off card per draft plus the verifier's findings.
     - "Claim vs evidence" findings on status words (alive, dead, captured) are the ones that matter: the model filling a gap the chapters leave.
     - Quote-mark findings and the grouped noise classes are cosmetic.
  4. Read it back: an Artifact read with `path:"index.html"`, then `python3 $KIT/read_decisions.py --npc --html <saved> --review <id> --out decisions.json`.
  5. `$SN review cards decide <id> --decisions decisions.json --reviewer GM --campaign-dir .` prints a plan. Show it to the GM, then re-run with `--write --plan-sha256 <hash>`. Never use `review decide` or `review npc sign` for page verdicts. Claude never signs.
- **A rejected line:**
  - The draft is never hand-edited. Ask the GM what the line should say; a bare reject has no fix in it.
  - Put the fix in `docs/npcs/authored/<slug>.authored.yaml` (`npc-compose --since 1 --until N --init <Name>` creates it). Add it under `manual:` as a list item that cites the GM ruling and its date.
  - Redraft that NPC (`--name`). The old sign-off goes stale, so put the new draft on a small follow-up review. Drow-empire's Molril went from "not specified" to "died in the fight at his tower (Ch 40)".
- **Publish:** `$SN npc-publish --since 1 --until N --all` publishes every signed NPC and refuses the rest, with a reason:
  - `NPC_DRAFT_SIGNOFF_REQUIRED` means the draft is unsigned or stale;
  - `slug collision` means two linked subjects share a file name; it is usually a punctuation variant.

  Re-run with `--name` after a follow-up review.
- **Commit:** following Phandalin, commit `draft/`, `evidence/`, `gm/`, the link reports, `docs/reviews/`, `docs/authority*`, `docs/npcs/*.md` and `authored/`. From `runs/`, keep only `record.json`, `selection.json` and `verify.json`. The raw prompts and outputs (14 MB on drow-empire) are not tracked.
- Reference: drow-empire `92119657c` (rulings) and `194639401` (dossiers), PR #716. Reviews `npc-review-16999e9f22ba` (134 cards) and `npc-review-9062d374b118`.

## Lessons from drow-empire (Stages 0–10, 2026-11-11 to 11-13)

Drow Empire was a 52-chapter, roughly 111,000-word bible played through the 21 Dan Hass Drow Campaign books, set in Greyhawk, with no recordings. PRs #686–#706 and #716. The write-up is `~/src/CampaignGenerator/docs/drow-empire-bible-backfill.md`. These are the lessons the earlier runs did not teach:

- **Stage 0, the date in the heading.** The bible's chapter headings carried the date. `build_bible.py` moved each one verbatim to the line below the heading, so headings are titles only and Stage 7 can rewrite date lines without touching a heading (`70f7737f4`).
- **Stage 1, many module books.**
  - Write one inventory per book: 21 files, from the rpg-library 5etools JSON listed in `config/refs.yaml`. Check every name verbatim against its own book.
  - Record cross-book variants as printed (Yagrak/Yagrat) and let the GM pick the canonical one at import. The GM also ruled that book and product titles are dropped.
  - **Module misprints are not aliases.** Strip them from the alias list (Altylin on Antyln) and queue the bible's misspellings for Stage 2 instead (`402a7dc9f`, `706239bb2`).
  - Create `config/party.yaml` as soon as the PCs are known. Every later name check depends on it.
  - A PC's full name comes from the character sheet (KP).
- **Stage 2, routing the review.**
  - Proposals come from the Stage 1 queue, a deterministic near-miss scan and aspell for ordinary words.
  - Stock Clef (on the Spark) scored each fix, which splits the page into bulk lists and cards. The GM still marks every item.
  - Store the exact text sent to Clef next to its score.
  - On the typo pass the GM approved all 126 fixes Clef scored below 80%, so a low score is a routing signal, never a reject.
- **Look for duplicates across the whole bible, not just adjacent chapters.** Ch 39 was a revised near-copy of Ch 38 (also in the other Drive copy). The GM kept the later one (`dec17c526`). Before splitting, check for any paragraph of 120+ characters that repeats across chapters (`af16da387`).
- **Stage 4, parallel agents and the verifier.**
  - Ten agents, five chapters each, worked well.
  - One agent worked around a verifier bug instead of reporting it: the bug split Graz’zt at the apostrophe, so the agent wrote "his liege", and that reversed who was liege to whom. **If the verifier fails on a name the chapter really contains, fix the verifier, never the wording** (`6961d34be`).
  - Hold every question the batch raises in `held_questions.json` (422 on drow-empire). Each later stage works from that queue.
- **Stage 5, the consistency pass.**
  - Discuss notes were often settled only after reading the module (DC books). Check the module before proposing a Discuss resolution.
  - A summary that retells a changed line needs a hand fix: 63 of the 90 mirrors on drow-empire were retold lines, not exact quotes.
- **Stages 6–7, story order.**
  - The bible was out of story order. The GM ruled a renumber (7↔8, 14↔15, 23↔24) and added two draft chapters that had never been pasted into the bible (`34cf9879b`). Keep a `renumber_map.json`; every later reference uses the new numbers.
  - Greyhawk: months have 28 days, festival weeks 7 (Needfest, Growfest, Richfest, Brewfest). Use CY dates.
  - **Time off-world** (Ch 26–51): the GM ruled that each realm counts its own days, with Day 1 being the arrival. `calendar.md` gained Realm and Realm-days columns, and the Greyhawk dates stay as the GM's record.
- **Stage 8, unnamed people.**
  - When the GM chooses to name the numbered extras ("Drow-4", "Human-2"), draw names from the GM's own supplements in the rpg-library and put them on a card page.
  - Run each new name through `registry check`. "Wolf" was a fuzzy near-duplicate of WLF, so the GM renamed him Lud (`f6c90acb2`).
  - Some "unnamed" people turn out to be a known NPC (Ch 8 "Drow 4" = Xunzmyr). That is an identity ruling, so ask the GM.
  - A generic one-word name (Tanner, Wright, Major) will need a `link_rulings` entry in Stage 11, so note it when you create one.
- **Stage 10, the players' calendar.**
  - What the players cannot know is shown as unknown. Off-world date lines read "The Abyss, Day 98 (??? on Oerth)". On the players' page those months collapse into one "???" card (`unknown`).
  - Several calendars go on one page (`parts`; the realms use `"system": "realms"`), and the page ends with the epilogue (`later`). See gm-player-calendar (#703).
  - Review scripts that read `calendar.md` must read the `## Chapters` table by column name. The Checks table's rows once overwrote the chapter rows in the card evidence (`444aab167`).
- **After Stage 9:** provision the campaign's mempalace with mneme (`mneme mp bringup <campaign> --dir`). The GM rules the corpus; on drow-empire `docs/chapters` became its own authoritative kind, "bible" (`d7ec6673e`).
- **Pace:** all 11 stages took three days because each stage's rulings were applied, verified and merged before the next began. Do not start a stage on unmerged rulings.

## Traps from the first run

| Trap | Fix |
|---|---|
| A bible-wide replace of a short name hit 3,001 times | Scope every edit to its chapter block; restore from the backup and re-apply |
| A heading fix matched the same heading in other chapters | Match whole lines, inside the chapter's block |
| The reviewer's hedge text ended up in the bible | Apply only the `after` string, never the card's commentary |
| The verifier failed after bible fixes | Mirror each fix into the matching summary quote |
| A Harptos festival was put after the wrong month | Use the table in Stage 6 |
| `git pull` failed with "incorrect old value" right after a merge | `git fetch origin && git merge --ff-only origin/main` |
| Sparse checkout: other campaigns are absent from disk | Read their files with `git show HEAD:<path>` |
| Mirroring fixes into summaries turned straight quotes curly | Restore the summaries from the backup and re-mirror, keeping each match's quote style |
| A summary retold a renamed line in its own words, so the verifier passed but the name was wrong | Run the word-overlap sentence check after every name change |
| An agent's `before` used curly quotes where the file had straight ones | Re-find each flag on its line before applying; fix by hand the ones that don't match |
| A regex used to pick "the aasimar questions" also caught unrelated ones (maid counts, poltergeists) | Have the scan mark each held question covered, no-change or needs-GM, and report the off-topic ones separately |
| An agent wrote around a verifier false positive ("his liege" for Graz’zt) and reversed a relationship | Report a verifier failure on a real name; fix the verifier |
| A review script read every table in `calendar.md`, and the Checks rows overwrote the chapter rows | Parse the named table by its column headers |
| An invented extra's name ("Wolf") nearly collided with an existing one (WLF) | Run `registry check` for fuzzy near-dups before you apply a new name |
| `summary_native` refused `--help`, and the config wasn't found | Set `CG_BACKEND`; bring the local main up to date with origin first (`git merge --ff-only origin/main`) |
| A summary heading "Humph, the Champion" (with a comma) split one NPC into two, and publish refused with a slug collision | Ask the GM to add the variant as a registry alias, `registry project .`, re-link, redraft the one NPC, then a follow-up review |
| The GM rejected an NPC line with no note | Ask what it should say; the fix goes in the authored file, never the draft |
| `review create` refused with "manual edits must be strings" | The selection's `manual` is the list of edit strings, not the authored file's path |
