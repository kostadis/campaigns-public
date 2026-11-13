#!/usr/bin/env python3
"""Extract a published-module section into numbered units, and check a playbook covers them.

Deterministic. It decides nothing about how to run the scene. It gives every paragraph,
read-aloud box, sidebar, list item and table of the module section a stable id, so the
playbook written from it can be checked mechanically: every unit is cited, every
blockquote is verbatim module text, and every DC in the playbook is one the module prints.

    module_source.py extract --source OotA 33a [339 ...] -o <out>.source.json
    module_source.py extract --file adventure-oota.json 33a -o <out>.source.json
    module_source.py check <out>.source.json <playbook>.md [--context <ctx>.source.json ...]
    module_source.py extract --source OotA 393 3c1 --max-units 9 -o <out>.context.json

`extract` also writes <out>.source.md, a readable copy with the unit ids, for the GM.
"""
import argparse, glob, json, os, pathlib, re, sys

RUNTIME = pathlib.Path("~/.5etools-mcp-runtime").expanduser()

# ── 5etools inline tags ─────────────────────────────────────────────────────

TAG = re.compile(r"\{@(\w+)\s*([^{}]*?)\}")


def _tag(m):
    kind, body = m.group(1), m.group(2)
    parts = body.split("|")
    if kind == "dc":
        return f"DC {parts[0]}"
    if kind == "hit":
        return f"+{parts[0]}"
    if kind in ("dice", "damage"):
        return parts[1] if len(parts) > 1 and parts[1] else parts[0]
    if kind in ("adventure", "book", "area", "table", "note"):
        return parts[0]  # display text first; later fields are source, chapter index, area id
    if kind == "quickref":
        return parts[4] if len(parts) > 4 and parts[4] else parts[0]
    # display text is the third field when present ({@creature x|src|shown}), else the first
    if len(parts) >= 3 and parts[2]:
        return parts[2]
    return parts[0]


def render(s):
    prev = None
    while prev != s:  # nested tags resolve inside-out
        prev, s = s, TAG.sub(_tag, s)
    return s


def norm(s):
    s = render(s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


# ── walking the entry tree ──────────────────────────────────────────────────


def find_id(node, want):
    if isinstance(node, dict):
        if node.get("id") == want:
            return node
        for v in node.values():
            r = find_id(v, want)
            if r is not None:
                return r
    elif isinstance(node, list):
        for v in node:
            r = find_id(v, want)
            if r is not None:
                return r
    return None


def walk(node, path, out, root):
    def add(kind, text, extra=None):
        seq = sum(1 for x in out if x["id"].rsplit(".", 1)[0] == root) + 1  # numbering restarts per section
        u = {"id": f"{root}.{seq}", "kind": kind, "path": " > ".join(path), "text": text}
        if extra:
            u.update(extra)
        out.append(u)

    if isinstance(node, str):
        add("para", render(node))
        return
    if isinstance(node, list):
        for n in node:
            walk(n, path, out, root)
        return
    if not isinstance(node, dict):
        return
    t = node.get("type")
    name = node.get("name")
    if t in ("entries", "section", None) and "entries" in node:
        walk(node["entries"], path + [name] if name else path, out, root)
    elif t == "insetReadaloud":
        text = "\n\n".join(render(e) if isinstance(e, str) else json.dumps(e) for e in node.get("entries", []))
        add("readaloud", text)
    elif t == "inset":
        walk(node.get("entries", []), path + [f"[sidebar] {name or ''}".strip()], out, root)
    elif t == "list":
        for it in node.get("items", []):
            if isinstance(it, str):
                add("list-item", render(it))
            elif it.get("type") == "item":
                body = it.get("entry") or " ".join(e if isinstance(e, str) else json.dumps(e) for e in it.get("entries", []))
                add("list-item", render(f"{it.get('name', '')} {body}".strip()))
            else:
                walk(it, path, out, root)
    elif t == "table":
        rows = [" | ".join(render(c) if isinstance(c, str) else render(json.dumps(c)) for c in r) for r in node.get("rows", [])]
        head = " | ".join(render(c) for c in node.get("colLabels", []))
        add("table", "\n".join(([head] if head else []) + rows), {"caption": render(node.get("caption", ""))})
    elif t in ("image", "gallery"):
        return  # pictures carry no table instructions
    elif t == "quote":
        add("quote", "\n".join(render(e) for e in node.get("entries", []) if isinstance(e, str)))
    elif "entries" in node:
        walk(node["entries"], path + [name] if name else path, out, root)
    else:
        add(t or "other", render(json.dumps(node)))  # unknown shape: kept, so it is never lost


def locate(source, campaign_dir):
    slug = re.sub(r"[^a-z0-9-]+", "-", pathlib.Path(campaign_dir).resolve().name.lower()).strip("-")
    roots = [RUNTIME / slug / "data", RUNTIME / slug / "homebrew"]
    cands = []
    for r in roots:
        cands += glob.glob(str(r / "adventure" / "*.json")) + glob.glob(str(r / "book" / "*.json"))
    hits = [c for c in cands if pathlib.Path(c).stem.lower().split("-", 1)[-1] == source.lower()]
    if not hits:
        sys.exit(f"no adventure/book file for source {source!r} under {roots}; pass --file")
    return hits[0]


def cmd_extract(a):
    f = a.file or locate(a.source, a.campaign_dir)
    data = json.load(open(f))
    units, heads = [], []
    for sid in a.section_ids:
        node = find_id(data.get("data", data), sid)
        if node is None:
            sys.exit(f"section id {sid!r} not found in {f}")
        heads.append({"id": sid, "name": node.get("name")})
        start = len(units)
        walk(node.get("entries", []), [node.get("name") or sid], units, sid)
        if a.max_units:
            del units[start + a.max_units:]  # context extracts keep only a section's opening units
    doc = {"file": os.path.abspath(f), "sections": heads, "units": units}
    out = pathlib.Path(a.out)
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    title = ", ".join("%s (%s)" % (h["name"], h["id"]) for h in heads)
    md = [f"# Module source: {title}",
          f"*Extracted verbatim from `{f}` by module_source.py. Do not edit; re-extract.*", ""]
    last = None
    for u in units:
        if u["path"] != last:
            md += [f"## {u['path']}", ""]
            last = u["path"]
        label = {"readaloud": "READ-ALOUD", "table": "TABLE", "list-item": "LIST"}.get(u["kind"], "")
        body = u["text"] if u["kind"] != "readaloud" else "\n".join("> " + l if l else ">" for l in u["text"].split("\n"))
        md += [f"**[§{u['id']}]** {label}".rstrip(), (u.get("caption") or "") and f"*{u['caption']}*", body, ""]
    out.with_suffix(".md").write_text("\n".join(l for l in md if l is not None))
    kinds = {}
    for u in units:
        kinds[u["kind"]] = kinds.get(u["kind"], 0) + 1
    print(f"extracted {len(units)} units {kinds} -> {out} and {out.with_suffix('.md')}")


def cmd_check(a):
    src = json.load(open(a.source_json))
    units = {u["id"]: u for u in src["units"]}
    # context units (neighbouring sections, for the intent section) may be cited and quoted,
    # but need not all be cited
    ctx = {}
    for c in a.context or []:
        ctx.update({u["id"]: u for u in json.load(open(c))["units"]})
    pb = pathlib.Path(a.playbook).read_text()
    errs, warns = [], []

    cited = set(re.findall(r"§([0-9a-zA-Z_-]+\.\d+)", pb))
    missing = [] if a.advice else [i for i in units if i not in cited]  # advice need not cover every unit
    unknown = sorted(cited - set(units) - set(ctx))
    for i in missing:
        u = units[i]
        errs.append(f"UNCITED §{i} ({u['kind']}, {u['path']}): {u['text'][:110]!r}")
    for i in unknown:
        errs.append(f"UNKNOWN citation §{i}: not a unit of this source")

    # blockquotes are verbatim module text only
    alltext = norm(" ".join(u["text"] for u in list(units.values()) + list(ctx.values())))
    block, blocks = [], []
    for line in pb.splitlines() + [""]:
        if line.lstrip().startswith(">"):  # indented quotes under a bullet count too
            block.append(line.lstrip().lstrip(">").strip())
        elif block:
            blocks.append(" ".join(block)); block = []
    for b in blocks:
        for piece in re.split(r"\s*\[§[^\]]+\]\s*|\s*\.\.\.\s*|\s*…\s*", b):
            p = norm(piece.strip('*_ '))
            if len(p) > 12 and p not in alltext:
                errs.append(f"NOT VERBATIM blockquote: {piece[:110]!r}")

    # inline "quotations" of four words or more are verbatim module text too
    for q in re.findall(r'["\u201c]([^"\u201c\u201d\n]{8,}?)["\u201d]', "\n".join(l for l in pb.splitlines() if not l.lstrip().startswith(">"))):
        if len(q.split()) >= 4 and norm(q.strip(" .,;:!?")) not in alltext:
            errs.append(f"NOT VERBATIM quote: {q[:110]!r}")

    src_dcs = set(re.findall(r"DC (\d+)", " ".join(u["text"] for u in list(units.values()) + list(ctx.values()))))
    for dc in sorted(set(re.findall(r"DC (\d+)", pb)) - src_dcs, key=int):
        if a.advice and all(re.search(r"\[INVENTED\]|suggest", l, re.I) for l in pb.splitlines() if f"DC {dc}" in l):
            continue  # an advice file may propose a DC, tagged on its line
        errs.append(f"DC {dc} is in the playbook but the module prints no DC {dc} here (mark GM rulings outside the playbook)")

    ra = [i for i, u in units.items() if u["kind"] == "readaloud"]
    print(f"{len(units)} units, {len(cited & set(units))} cited, {len(ra)} read-aloud, {len(blocks)} blockquotes")
    for e in errs:
        print("  " + e)
    print("PASS" if not errs else f"FAIL ({len(errs)})")
    sys.exit(1 if errs else 0)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("extract")
    e.add_argument("section_ids", nargs="+")
    e.add_argument("--source")
    e.add_argument("--file")
    e.add_argument("--campaign-dir", default=".")
    e.add_argument("-o", "--out", required=True)
    e.add_argument("--max-units", type=int, help="keep only the first N units of each section (context extracts)")
    c = sp.add_parser("check")
    c.add_argument("source_json")
    c.add_argument("playbook")
    c.add_argument("--advice", action="store_true", help="a GM-take file: coverage not required; a DC not in the module needs [INVENTED] or 'suggested' on its line")
    c.add_argument("--context", action="append", help="a .source.json of neighbouring sections the playbook may cite")
    a = ap.parse_args()
    if a.cmd == "extract" and not (a.source or a.file):
        ap.error("extract needs --source or --file")
    (cmd_extract if a.cmd == "extract" else cmd_check)(a)


if __name__ == "__main__":
    main()
