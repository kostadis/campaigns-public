---
name: gm-bible-backfill
description: Turn a campaign's hand-written bible (one long markdown of chapters, no recordings) into GM-ruled enhanced summaries, a ruled Harptos calendar, published docs/summaries and a players' calendar page. A staged runbook, with one GM checkpoint and one PR per stage. It records what each stage produces, how it is checked, and the traps hit on the first run (stormgiants, 2026-11-06, PRs #629–#633). Invoke as /gm-bible-backfill <campaign-dir> [stage], or when the user says "do the stormgiants process for <campaign>", "backfill summaries from the bible", or "start <campaign>'s bible from the top".
---

# gm-bible-backfill

The end-to-end process first run on stormgiants (*The Hero's Journey or The War of the Giants*, 86 chapters) on 2026-11-06. It turns a bible into:

- `docs/chapters/`, the split;
- `summaries/NNN-<slug>/session-summary.md`;
- `docs/arcs/calendar.md`;
- `docs/summaries/`;
- `notes/handouts/player_calendar.*`.

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
