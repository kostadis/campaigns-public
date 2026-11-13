---
name: gm-player-calendar
description: Build or update a player-facing calendar page (Harptos, Greyhawk, or a day count) ("The Road So Far") showing the major events the party has lived through, day by day, from the campaign's GM-ruled docs/arcs/calendar.md. Event wording is drafted from table-facing facts only, every proper noun is checked against canon, and the GM reviews the event list before anything is published; a deterministic script then builds the page from the reviewed JSON and it is republished to the same link. Invoke when the user says "show the players a calendar", "update the players' calendar", "/gm-player-calendar", or from gm-session-prep's calendar step.
---

# gm-player-calendar

A page the GM can share with the players: each Harptos month drawn as three tendays of ten days, the festival days standing alone between months (for Greyhawk, each month as four seven-day weeks with the festival weeks between them; for a campaign that counts days instead, Day 1 to Day N in cards of ten), every day coloured by where the party was, and a numbered list of events under each month. First built for Out of the Abyss on 2026-11-02 (https://claude.ai/artifact/U8FoJVNJBmZ2CRwLRtsZLa).

## What decision this removes from the GM

None. The dates are already the GM's (they come from `docs/arcs/calendar.md`, where every row is GM-ruled). Claude drafts the **wording** of each event and the **grouping** into coloured stretches. Both are scope decisions about what players see, so the GM reviews the event list before it is published. The build is deterministic.

## Files

| File | Role |
|---|---|
| `<campaign>/docs/arcs/calendar.md` | Source of every date. GM-ruled. Never edited by this skill. |
| `<campaign>/notes/handouts/player_calendar.json` | **Origin.** The reviewed event list, groups, title, "today", range and the artifact URL. Edit this. |
| `<campaign>/notes/handouts/player_calendar.html` | **Replica.** Built by the script; carries a `cg-generated - do not hand-edit` header. |
| `build_calendar.py` (next to this file) | Validates every date against Harptos, Greyhawk or the day count, then injects the JSON into `template.html`. |
| `template.html` (next to this file) | The page design. Shared by every campaign. |

JSON shape:

```json
{
  "artifact_url": "https://claude.ai/artifact/...",   // absent until first publish
  "title": "The Road So Far",
  "subtitle": "...",
  "today_label": "1 Alturiak 1492 DR, evening, at the Gauntlgrym feast",
  "today_day": "1 Alturiak 1492",
  "from_month": "Eleasis 1491", "to_month": "Alturiak 1492",
  "footer": "...",
  "groups": [{"id": "capt", "name": "Velkynvelve and the escape"}],   // at most 8, in order
  "events": [{"group": "capt", "from": "12 Eleasis 1491", "to": "15 Eleasis 1491",
              "what": "Taken by the drow", "chapters": "Ch. 1", "desc": "..."}]
}
```

**Day count:** set `"system": "days"`, `"from_day"` and `"to_day"` (integers) in place of `from_month`/`to_month`, an optional `"count_gloss"` (e.g. "Days in Barovia"), and write every day as `"Day N"`, `today_day` included. Times of day (morning, dusk) go in `desc`, not in the date.

**Greyhawk:** set `"system": "greyhawk"`; `from_month`/`to_month` name a month or a festival week (`"Goodmonth 576"`, `"Brewfest 576"`). Every day, `today_day` included, is `"<d> <Month or Festival> <year>"`, e.g. `"20 Goodmonth 576"` or `"3 Brewfest 576"`. The year is the Common Year (CY). Months have 28 days; the festival weeks have 7: Needfest (opens the year, before Fireseek), Growfest (Coldeven–Planting), Richfest (Wealsun–Reaping) and Brewfest (Harvester–Patchwall). Every month and festival starts on Starday. First used for original-group-toee, 2026-11-09.

**Several calendars on one page:** add `"parts": ["other_calendar.json"]` (paths relative to this JSON) to the main JSON. Each part is validated on its own and drawn below the main one, with its own title, legend and footer, and a link bar at the top. An optional `"later": {"title", "chapters", "items": [{"what", "desc"}]}` (undated aftermath, e.g. an epilogue's "A few years later") is drawn as the last card on the page. Only the main JSON carries `artifact_url`. First used for drow-empire, 2026-11-13: Greyhawk on Oerth, then a `"system": "realms"` part, one day count per realm, for the party's time off-world.

**Days the players cannot date:** `"unknown": [{"from", "to", "what", "chapters", "desc"}]` marks a stretch the party could not count (time off-world). Its days show "?" on a grey hatch, never an event colour. With Greyhawk, whole months and festival weeks inside it collapse into one "???" card. It may not overlap an event or contain `today_day`. First used for drow-empire, 2026-11-13 (GM: "the days outside of Oerth should not have Oerth days other than ???").

Harptos days are written `"<d> <Month> <year>"`; festivals `"<Festival> <year>"` (Midwinter, Greengrass, Midsummer, Shieldmeet in years divisible by 4, Highharvestide, Feast of the Moon). Events are listed in start order.

## Steps

### 1. Preconditions
- The campaign has `docs/arcs/calendar.md` with ruled chapter rows. If it doesn't, stop: the dates have to be ruled first (gm-session-prep step 1a, or `/gm-arc`). Never date events yourself from summaries.
- The template draws three systems: Harptos, Greyhawk (`"system": "greyhawk"`, first used for original-group-toee, 2026-11-09), and a plain day count (`"system": "days"`, first used for Curse of the Hags' "Days in Barovia", 2026-11-07). For any other system, stop and tell the GM.

### 2. Find what is new
- **First build:** every ruled chapter row.
- **Update:** compare `calendar.md`'s chapter rows with the JSON's `events[].chapters`. Only rows not yet on the page are new. Also check whether *Today* changed.
- Rows marked `?` are unruled. Leave them off and say so.

### 3. Draft the events
For each new row, draft one event (or split one row into two when it holds two distinct things the party would remember, e.g. a journey and an arrival):
- **Dates:** the row's Starts and Ends, exactly.
- **`what`:** a short name for the stretch, the way a player would say it ("Across the Darklake").
- **`desc`:** one or two sentences, drawn only from the row's table-facing facts: what the party did and counted. Quote the table's own words where the Basis column quotes them.
- **Leave out everything GM-only:** source tags, line numbers, rulings about what was "really" meant (e.g. "his exaggeration"), the GM's own asides at the table, superseded bible dates, clocks and their `Due` dates, anything from a strategy doc or the Mystery ledger, and anything about the future.
- **Groups:** one coloured stretch per region or phase of the journey. Reuse existing groups; add one only for a new region. At most 8.
- **Every proper noun** goes through the workspace canon chain (`config/party.yaml`, `notes/vtt_transcription_corrections.md`, `docs/entity_registry.yaml`, dossiers, `notes/vtt_known_additions.md`). A name absent from the chain is surfaced to the GM, never invented. Show the check (name → where it was found).
- **Any word not in the source row** (an epithet, a species name, a characterisation) is your wording: flag it to the GM by name.

### 4. GM review (the checkpoint)
Show the GM the new or changed events, each with its source row, plus the flagged wordings. About a dozen or fewer: in chat. More: one Approve / Reject / Discuss artifact (workspace long-queue rule). Undecided is re-asked; a discuss note is confirmed before applying. Record any unruled flag in the JSON's `_notes`.

### 5. Build and publish
```bash
python3 <workspace>/gm-assistant/skills/gm-player-calendar/build_calendar.py <campaign>/notes/handouts/player_calendar.json
```
- The script refuses to build on any bad date, out-of-order event, unknown group or unused group. Fix the JSON, never the HTML.
- Publish `player_calendar.html` with the Artifact tool. **If `artifact_url` is set, publish to that URL** (read it first if this conversation hasn't), so the players' link keeps working. On a first publish, use icon `calendar`, then write the returned URL into the JSON.
- Remind the GM the page is private until shared from its Share menu.

### 6. Commit
The JSON and the rebuilt HTML go in the same commit, in the campaign's own branch and PR (campaign isolation). Only when the user asks.

## Hard rules
- Dates come only from ruled `calendar.md` rows.
- Nothing GM-only reaches the page. When in doubt, leave it out and ask.
- Never hand-edit the HTML. Edit the JSON and rebuild.
- Never invent or normalise a name silently.
