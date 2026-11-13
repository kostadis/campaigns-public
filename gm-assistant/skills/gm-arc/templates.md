# gm-arc templates

Formats for the files under `<campaign>/docs/arcs/`. Tags and states are defined in `SKILL.md`.

## Arc — `docs/arcs/<slug>.md`

```markdown
---
arc: <slug>
title: <Title>
kind: conflict                      # conflict | mystery
driver: gm                          # gm | players
status: active                      # active | dormant | resolved | abandoned
sandboxes: [<place-slug>]           # several if the arc travels
links: [<other-arc-slug>]
as_of: <N>                          # last Ch. reconciled
villains: [<npc-slug>]              # → notes/<npc>_strategy.md (owns the ledger)
pc_scores: []                       # → docs/tracking/
---

# <Title>

> GM-owned origin file. Hopes, not outcomes; never copied into grounding docs.
> Last GM-approved delta: <yyyy-mm-dd> (<new | record Ch. N | prep>)

## Question and win condition
<one question> [tag]

## If nobody intervenes
- <default trajectory> [OVERLAY | GM date]

## Seen by the party
- <what the table witnessed> [TABLE Ch. N / scene]
<!-- empty = payoff flag -->

## Possible beats
| Beat | Gate (depends_on / not-before) | State | Tag |
|---|---|---|---|
| <beat> | <gate> | pending | [GM date] |

## Clocks
| Clock | State | Last touched | Tag |
|---|---|---|---|

## Mystery ledger            <!-- mysteries only -->
| GM truth | Evidence held | Evidence available | SPENT |
|---|---|---|---|

## Rulings
| Date | Ruling | Reveal state | Source |
|---|---|---|---|

## Deferred decisions
| Decision | Decide by | Raised |
|---|---|---|

## Beats played
- Ch. N / scene — <beat>

## Threads pulled in
- <thread title> — [ch NNN / scene] — pulled by GM <date>
```

## Sandbox — `docs/arcs/sandboxes/<place-slug>.md`

```markdown
---
sandbox: <place-slug>
title: <Place>
status: active                      # active | left | closed
as_of: <N>
arcs: [<arc-slug>]
---

# <Place>

> GM-owned origin file. The players' side: what they can do here.

## The stage
<geography, key rooms> [MODULE §x]

## Faction roster
| Faction | Current state | Want | Clock | Tag |
|---|---|---|---|---|

## Standing rules of the place
- <alarm protocol, price ladder, …> [tag]

## Party goals
- "<players' own words>" — <PC> [TABLE Ch. N / scene]

## Affordance menu (not exhaustive — unlisted player actions are expected and get appended)
| Affordance | Pushes arcs | State | Tag |
|---|---|---|---|

## Arcs running here
- [<Title>](../<arc-slug>.md) — <one-line status>
```

## `docs/arcs/clocks.md`

```markdown
# Clocks

| Clock | Sandbox / tag | State | Last touched | Due | Arc | Source |
|---|---|---|---|---|---|---|
```

`Due` is a date from `calendar.md`, in the campaign's System, or `—` when the clock has no date. A clock that counts days ("a week from Ch. 57") gets its date the moment the start day is ruled. Files written before the calendar existed may lack the column; add it when the campaign adopts `calendar.md`.

## `docs/arcs/calendar.md`

The method: use dates the table or the bible already gave, estimate the rest from travel, and say how sure you are. The worked example is `Phandalin/docs/arcs/calendar.md` (2026-10-30), which replaced the hand calendar in `Phandalin/notes/arc_cleanup/campaign_calendar.md`.

```markdown
# Calendar

> GM-owned origin file. Claude proposes each row with the lines it rests on; the GM rules. Unruled rows say `?`.
> System: <Harptos (Forgotten Realms) | Common Year (Greyhawk) | …> [GM yyyy-mm-dd]
> Anchor: <event>, <date> [GM yyyy-mm-dd]
> Backfill: <from Ch. N on | open clocks only | every chapter> [GM yyyy-mm-dd]

**Today (end of Ch. N):** <date> (±N days)

## Chapters

| Ch. | Days | Starts | Ends | How dated | Basis | Source |
|---|---|---|---|---|---|---|
| 59 | 1 | Deadwinter's Eve | Deadwinter's Eve | stated | "around 11am on Deadwinter's Eve" | [TABLE Ch. 59 / scene]; [GM yyyy-mm-dd] |

## Before the campaign

| Event | Date | Why | Source |
|---|---|---|---|

## Travel

| Route | Distance | Terrain | Time |
|---|---|---|---|

## What comes next

| Event | Expected date | Why | Clock |
|---|---|---|---|
```

- **Days** counts every day since the previous row ended, travel and downtime included.
- **How dated**, strongest first. `stated`: the table or the bible gives the date, such as a chapter header (Phandalin's bible stamps `01-02-Tarsakh 1495`, day–tenday–month) or a line like "Deadwinter's Eve". `counted`: days counted from a stated date using time markers in the summary ("the next morning", "three days on the road"). `travel`: estimated from the Travel table. `?`: nothing to go on, so ask. Never let a `travel` estimate quietly become `stated`.
- **Basis** quotes the summary lines the count rests on. "No time markers" is a valid basis, and the GM's ruling is still needed.
- **Travel** carries the distances and paces the estimates use (Phandalin's are road 24 mi/day, forest 15, rough 12). Distances come from the module or the map. When an estimate later meets a stated date, check the table against it.
- **Today** carries a ± range until a stated date pins it. Widen the range as `travel` and `?` rows pile up.
- **What comes next** lists dated expectations: a clock's `Due`, an NPC's arrival, a festival. Prep reads it as "in motion".
- **Harptos** (Forgotten Realms): twelve months of 30 days, three tendays each: Hammer, Alturiak, Ches, Tarsakh, Mirtul, Kythorn, Flamerule, Eleasis, Eleint, Marpenoth, Uktar, Nightal. Festival days fall between months and belong to neither: Midwinter (after 30 Hammer; Deadwinter Day in the North), Greengrass (after 30 Tarsakh), Midsummer (after 30 Flamerule), Shieldmeet (after Midsummer, in years divisible by 4), Highharvestide (after 30 Eleint), the Feast of the Moon (after 30 Uktar).
- **Other systems** (ToEE uses Greyhawk's Common Year, e.g. "Planting 15, 579"): write the month list and festival weeks under the System line the first time the file is made, and have the GM confirm them.
- **Before the campaign** dates events the table only counts back to ("absent for exactly seventy-three days", "seven tendays ago").

### What the Phandalin calendar taught (GM rulings, 2026-10-30)

- **When the bible and the summary disagree, ask. Don't pick a winner.** The bible's headers skipped nights the summaries count. The GM ruled the nights count, and the extra days came out of downtime ("Shrink the downtime"). Show both sources and let the GM rule.
- **Bible headers can be rewritten.** Phandalin's were folded once (commit `9c713511c`). If the history shows more than one set, the GM picks the baseline. Write the commit in the file's header.
- **Lines that count time are checks.** An NPC who says "exactly seventy-three days" or "three weeks ago" fixes a gap. List each one, with its source, and recount them after every ruling. Downtime is where the slack goes, so set downtime to make them hold. A check that fails goes to the GM.
- **The table can be wrong too.** A travel time said at the table ("seven days" to Neverwinter) can be a slip. Check it against the Travel table and ask. The GM: "I goofed with the seven days."
- **"Weeks" usually means tendays** in a Harptos game. "Seven weeks" turned out to be seven tendays (70 days), and "since midsummer" was a prep error. Ask before you read either way.
- **Fix the words at the origin, not the calendar.** When a ruling says the prose was wrong, fix the summary and the bible at the origin and regenerate their replicas. The tapes (VTTs) keep what was said.
- **A moved date re-opens its approval.** The GM approves a date, not a count. If a later ruling moves an approved date (a festival, an NPC's conversion), tell the GM the new date.
- **Check month names.** Phandalin had four wrong ones (`Taraksh`, `Tarksh`, `Taraskh` for **Tarsakh**). Check each against the System's month list. Fixing them is a name change, so show each one.
- **Many rows go in one artifact.** Phandalin's backfill was 24 cards: one per span, with a box for the GM's own day count, and the dates and checks recounted live as the GM marked them.
- **Keep the old hand calendar.** Mark it "Superseded by `docs/arcs/calendar.md` (date). Kept as a record." Don't delete it.

## `docs/arcs/junctions.md`

```markdown
# Junctions — where arcs CAN meet (possibilities, never schedules)

| Junction (person / object / place) | Arcs | How they could collide | Source |
|---|---|---|---|
```
