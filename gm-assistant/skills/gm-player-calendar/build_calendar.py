#!/usr/bin/env python3
"""Build the players' calendar page from a campaign's player_calendar.json.

Three systems. Harptos (the default): days are "<d> <Month> <year>" or "<Festival> <year>",
drawn as months of three tendays. Greyhawk ("system": "greyhawk"): Common Year, twelve
months of 28 days and four festival weeks of 7 (Needfest, Growfest, Richfest, Brewfest);
days are "<d> <Month or Festival> <year>", e.g. "20 Goodmonth 576" or "3 Brewfest 576",
drawn as weeks of seven (every month and festival starts on Starday). Day count
("system": "days", with "from_day" and "to_day" as integers): days are "Day N", drawn in
rows of ten, for campaigns with no in-world calendar (e.g. Barovia's "Days in Barovia").
Realms ("system": "realms", with "realms": [{"id", "name", "from_day", "to_day", "gloss"?}]):
one day count per realm on one page, for time spent off the home world (each realm keeps its
own count); every event names its "realm" and its days are "Day N" within that realm. Events
are numbered in list (story) order and must start in order within each realm.

Deterministic: validates every date against the chosen system, then injects the
JSON into template.html. It decides nothing about content; the JSON is the GM-reviewed
origin and the HTML is its replica.

    python3 build_calendar.py <campaign>/notes/handouts/player_calendar.json [-o out.html]
"""
import argparse, json, pathlib, sys

MONTHS = ["Hammer", "Alturiak", "Ches", "Tarsakh", "Mirtul", "Kythorn", "Flamerule",
          "Eleasis", "Eleint", "Marpenoth", "Uktar", "Nightal"]
FEST_AFTER = {"Hammer": ["Midwinter"], "Tarsakh": ["Greengrass"], "Flamerule": ["Midsummer"],
              "Eleint": ["Highharvestide"], "Uktar": ["Feast of the Moon"]}
# Greyhawk Common Year, in order. Needfest opens the year; each festival week sits
# between two months and belongs to neither (toee/docs/arcs/calendar.md, GM 2026-10-31).
GREYHAWK = [("Needfest", 7), ("Fireseek", 28), ("Readying", 28), ("Coldeven", 28),
            ("Growfest", 7), ("Planting", 28), ("Flocktime", 28), ("Wealsun", 28),
            ("Richfest", 7), ("Reaping", 28), ("Goodmonth", 28), ("Harvester", 28),
            ("Brewfest", 7), ("Patchwall", 28), ("Ready'reat", 28), ("Sunsebb", 28)]
MAX_GROUPS = 8
HERE = pathlib.Path(__file__).resolve().parent


def day_list(from_month, to_month):
    m, y = from_month.split(" "); y = int(y); mi = MONTHS.index(m)
    tm, ty = to_month.split(" "); ty = int(ty)
    if tm not in MONTHS:
        raise ValueError(f"unknown month {tm!r}")
    out = []
    for _ in range(12 * 50):
        mon = MONTHS[mi]
        out += [f"{d} {mon} {y}" for d in range(1, 31)]
        fest = list(FEST_AFTER.get(mon, []))
        if mon == "Flamerule" and y % 4 == 0:
            fest.append("Shieldmeet")
        out += [f"{f} {y}" for f in fest]
        if mon == tm and y == ty:
            return out
        mi += 1
        if mi == 12:
            mi, y = 0, y + 1
    raise ValueError("to_month is not after from_month")


def greyhawk_days(from_unit, to_unit):
    names = [n for n, _ in GREYHAWK]
    m, y = from_unit.rsplit(" ", 1); y = int(y)
    tm, ty = to_unit.rsplit(" ", 1); ty = int(ty)
    if m not in names or tm not in names:
        raise ValueError(f"unknown Greyhawk month or festival in {from_unit!r} / {to_unit!r}")
    ui = names.index(m); out = []
    for _ in range(len(GREYHAWK) * 50):
        name, n = GREYHAWK[ui]
        out += [f"{d} {name} {y}" for d in range(1, n + 1)]
        if name == tm and y == ty:
            return out
        ui += 1
        if ui == len(GREYHAWK):
            ui, y = 0, y + 1
    raise ValueError("to_month is not after from_month")


def days_count(a, z):
    if not (isinstance(a, int) and isinstance(z, int)) or z < a:
        raise ValueError("from_day/to_day must be integers with to_day >= from_day")
    return [f"Day {n}" for n in range(a, z + 1)]


def validate(data):
    errs = []
    system = data.get("system", "harptos")
    if system not in ("harptos", "greyhawk", "days", "realms"):
        return [f"unknown system {system!r}"]
    if system == "realms":
        return validate_realms(data)
    rng = ("from_day", "to_day") if system == "days" else ("from_month", "to_month")
    for k in ("title", "subtitle", *rng, "groups", "events"):
        if k not in data:
            errs.append(f"missing key: {k}")
    if errs:
        return errs
    if system == "harptos":
        days = day_list(data["from_month"], data["to_month"])
    elif system == "greyhawk":
        try:
            days = greyhawk_days(data["from_month"], data["to_month"])
        except ValueError as e:
            return [str(e)]
    else:
        try:
            days = days_count(data["from_day"], data["to_day"])
        except ValueError as e:
            return [str(e)]
    pos = {d: i for i, d in enumerate(days)}
    gids = [g["id"] for g in data["groups"]]
    if len(gids) > MAX_GROUPS:
        errs.append(f"{len(gids)} groups; the palette has {MAX_GROUPS}")
    if len(set(gids)) != len(gids):
        errs.append("duplicate group id")
    used = set()
    last_start = -1
    for n, ev in enumerate(data["events"], 1):
        for k in ("group", "from", "to", "what"):
            if k not in ev:
                errs.append(f"event {n}: missing {k}")
        if ev.get("group") not in gids:
            errs.append(f"event {n}: unknown group {ev.get('group')!r}")
        used.add(ev.get("group"))
        a, z = pos.get(ev.get("from")), pos.get(ev.get("to"))
        if a is None:
            errs.append(f"event {n}: 'from' {ev.get('from')!r} is not a day in range")
        if z is None:
            errs.append(f"event {n}: 'to' {ev.get('to')!r} is not a day in range")
        if a is not None and z is not None:
            if z < a:
                errs.append(f"event {n}: ends before it starts")
            if a < last_start:
                errs.append(f"event {n}: starts before event {n-1}; list events in order")
            last_start = a
    unused = set(gids) - used
    if unused:
        errs.append(f"groups with no events: {sorted(unused)}")
    # "unknown": stretches the players cannot date (e.g. time spent off-world). Their days show "?"; with
    # Greyhawk, whole months and festival weeks inside one collapse into a single "???" card.
    for n, u in enumerate(data.get("unknown", []), 1):
        a, z = pos.get(u.get("from")), pos.get(u.get("to"))
        if a is None or z is None or z < a:
            errs.append(f"unknown {n}: 'from'/'to' must be days in range, in order; got {u.get('from')!r}, {u.get('to')!r}")
            continue
        for m, ev in enumerate(data["events"], 1):
            ea, ez = pos.get(ev.get("from")), pos.get(ev.get("to"))
            if ea is not None and ez is not None and ea <= z and a <= ez:
                errs.append(f"unknown {n} overlaps event {m} ({ev.get('what')!r})")
        if data.get("today_day") in pos and a <= pos[data["today_day"]] <= z:
            errs.append(f"unknown {n} contains today_day")
    lt = data.get("later")  # undated aftermath ("A few years later"), drawn after the last month
    if lt is not None and (not lt.get("title") or not lt.get("items") or any(not (i.get("what") and i.get("desc")) for i in lt["items"])):
        errs.append("later: needs a title and items, each with what and desc")
    if data.get("today_day") and data["today_day"] not in pos:
        errs.append(f"today_day {data['today_day']!r} is not a day in range")
    return errs


def validate_realms(data):
    errs = [f"missing key: {k}" for k in ("title", "subtitle", "realms", "groups", "events") if k not in data]
    if errs:
        return errs
    pos, rids = {}, []
    for r in data["realms"]:
        if not all(k in r for k in ("id", "name", "from_day", "to_day")):
            errs.append(f"realm {r!r}: needs id, name, from_day, to_day"); continue
        if r["id"] in rids:
            errs.append(f"duplicate realm id {r['id']!r}")
        rids.append(r["id"])
        try:
            for i, d in enumerate(days_count(r["from_day"], r["to_day"])):
                pos[f"{r['id']}:{d}"] = i
        except ValueError as e:
            errs.append(f"realm {r['id']}: {e}")
    gids = [g["id"] for g in data["groups"]]
    if len(gids) > MAX_GROUPS:
        errs.append(f"{len(gids)} groups; the palette has {MAX_GROUPS}")
    if len(set(gids)) != len(gids):
        errs.append("duplicate group id")
    used, used_realms, last = set(), set(), {}
    for n, ev in enumerate(data["events"], 1):
        for k in ("group", "realm", "from", "to", "what"):
            if k not in ev:
                errs.append(f"event {n}: missing {k}")
        if ev.get("group") not in gids:
            errs.append(f"event {n}: unknown group {ev.get('group')!r}")
        if ev.get("realm") not in rids:
            errs.append(f"event {n}: unknown realm {ev.get('realm')!r}"); continue
        used.add(ev.get("group")); used_realms.add(ev["realm"])
        a, z = pos.get(f"{ev['realm']}:{ev.get('from')}"), pos.get(f"{ev['realm']}:{ev.get('to')}")
        if a is None:
            errs.append(f"event {n}: 'from' {ev.get('from')!r} is not a day of realm {ev['realm']}")
        if z is None:
            errs.append(f"event {n}: 'to' {ev.get('to')!r} is not a day of realm {ev['realm']}")
        if a is not None and z is not None:
            if z < a:
                errs.append(f"event {n}: ends before it starts")
            if a < last.get(ev["realm"], -1):
                errs.append(f"event {n}: starts before the previous event in realm {ev['realm']}")
            last[ev["realm"]] = a
    if set(gids) - used:
        errs.append(f"groups with no events: {sorted(set(gids) - used)}")
    if set(rids) - used_realms:
        errs.append(f"realms with no events: {sorted(set(rids) - used_realms)}")
    t = data.get("today_day")
    if t and (not isinstance(t, dict) or f"{t.get('realm')}:{t.get('day')}" not in pos):
        errs.append(f"today_day must be {{\"realm\": id, \"day\": \"Day N\"}} in range; got {t!r}")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    src = pathlib.Path(a.json)
    data = json.loads(src.read_text())
    # "parts": further calendar JSONs (paths relative to this one) drawn below it on the same page.
    parts = [(src, data)] + [(src.parent / p, json.loads((src.parent / p).read_text())) for p in data.get("parts", [])]
    errs = [f"{p.name}: {e}" for p, d in parts for e in validate(d)]
    if errs:
        print("NOT BUILT:", *errs, sep="\n  ", file=sys.stderr)
        sys.exit(1)
    tpl = (HERE / "template.html").read_text()
    payload = [{k: v for k, v in d.items() if k not in ("artifact_url", "_notes", "parts")} for _, d in parts]
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("__TITLE__", data["title"].replace("<", "&lt;")).replace("__DATA__", blob)
    out = pathlib.Path(a.out) if a.out else src.with_suffix(".html")
    out.write_text(html)
    print(f"built {out} (" + "; ".join(f"{d['title']}: {len(d['events'])} events, {len(d['groups'])} groups" for _, d in parts) + ")")


if __name__ == "__main__":
    main()
