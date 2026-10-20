#!/usr/bin/env python3
"""ndc — deterministic helpers for the gm-npc-dossier-cleanup skill.

Every subcommand runs from a campaign directory (or takes --campaign-dir) and reads the
summary_native range from config/grounding.yaml. Run files live in
<npc-range-dir>/cleanup/<tag>/ so the questions the GM was asked are kept next to the work.

Nothing here decides anything. It reads state, checks edits, builds pages, and turns
rulings the GM already made into the exact request bodies `summary_native review decide` takes.

Subcommands (see --help on each):
  targets            pick the NPCs for this run (from /state or from a draft run)
  verify             run npc-verify for the targets and collect failures
  evidence           print cited evidence items for a stem (for spot checks)
  check-edits        validate edits/*.json and dry-run them on a scratch copy
  corrections-page   build the GM corrections page (one card per wording edit)
  approved-ids       read the corrections decisions back into an id list
  apply              apply approved edits to the real drafts, then verify + compose
  flags              classify number/ordinal advisories offline (before the review exists)
  selection          write review_selection.json for the targets (all must pass verify)
  policy             build >=90%-policy decision batches for checker flags in a review
  signoff-page       build the GM sign-off page (one card per draft + leftover flags)
  ledger             turn the GM's sign-off decisions into decision batches
  gate               check _current_draft_signoff for every target
  ctx                print VTT cues around a regex (for reject adjudication)
"""
from __future__ import annotations

import argparse
import collections
import difflib
import glob
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from types import SimpleNamespace

CG = Path(os.environ.get("CAMPAIGN_GENERATOR", Path.home() / "src/CampaignGenerator"))
sys.path.insert(0, str(CG))
SUMMARY_NATIVE = str(Path.home() / ".venv/bin/summary_native")
REVIEW_PAGE = Path(os.environ.get("REVIEW_PAGE", Path.home() / "src/mytools/dotfiles/codex/skills/_shared/review-page"))
BATCH = 40


# ---------------------------------------------------------------- context

class Ctx:
    def __init__(self, a):
        import yaml
        self.root = Path(a.campaign_dir).resolve()
        g = yaml.safe_load((self.root / "config/grounding.yaml").read_text())["summary_native"]
        self.since, self.until = int(g["range_since"]), int(g["range_until"])
        self.summaries_dir = g.get("summaries_dir", "docs/summaries")
        self.range = f"ch{self.since:03d}-{self.until:03d}"
        self.npc_root = self.root / (a.npc_root or "docs/npcs/summary_native")
        self.rdir = self.npc_root / self.range
        self.run = self.rdir / "cleanup" / a.run if getattr(a, "run", None) else None
        if self.run:
            self.run.mkdir(parents=True, exist_ok=True)

    def rel(self, p) -> str:
        return Path(p).resolve().relative_to(self.root).as_posix()

    def draft(self, stem):
        return self.rdir / "draft" / f"{stem}.md"

    def evidence(self, stem):
        return self.rdir / "evidence" / f"{stem}.md"

    def subject(self, stem):
        m = re.search(r"^subject: (.+)$", self.evidence(stem).read_text(encoding="utf-8"), re.M)
        return m.group(1).strip()

    def targets(self):
        p = self.run / "targets.json"
        if not p.exists():
            sys.exit(f"no {p}; run `ndc targets` first")
        return json.loads(p.read_text())

    def summaries(self):
        out = []
        for p in sorted((self.root / self.summaries_dir).glob("*.md")):
            m = re.match(r"(\d+)-", p.name)
            if m and self.since <= int(m.group(1)) <= self.until:
                out.append(self.rel(p))
        return out

    def sn(self, *args, check=True):
        cmd = [SUMMARY_NATIVE, *args]
        r = subprocess.run(cmd, cwd=self.root, text=True, capture_output=True,
                           env={**os.environ, "CG_BACKEND": "claude-code"})
        if check and r.returncode:
            sys.exit(f"{' '.join(cmd[:3])} failed ({r.returncode}):\n{r.stdout[-2000:]}{r.stderr[-2000:]}")
        return r

    def range_args(self):
        return ["--summaries-dir", self.summaries_dir, "--since", str(self.since), "--until", str(self.until)]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def write_json(p: Path, v):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


# ---------------------------------------------------------------- targets

def cmd_targets(c: Ctx, a):
    if a.from_draft_run:
        sel = json.loads((c.rdir / "runs" / a.from_draft_run / "selection.json").read_text())
        rows = [{"stem": r["stem"], "subject": r["subject"]} for r in sel["included"]]
    else:
        import urllib.request
        url = f"{a.server}/api/npc-dossiers/state?since={c.since}&until={c.until}"
        st = json.load(urllib.request.urlopen(url))
        npcs = st["npcs"]
        tally = collections.Counter((r["draft"], r["verify"], r["published"], r["exclusion"]) for r in npcs)
        print(f"/state {c.range}: link_stale={st.get('link_stale')} warnings={st.get('warnings')}")
        for k, v in tally.most_common():
            print(f"  {v:4d}  draft={k[0]} verify={k[1]} published={k[2]} exclusion={k[3]}")
        ruled = ruled_names(c)
        unreg = [r["subject"] for r in npcs if r["exclusion"] == "not in registry"]
        fresh = [n for n in unreg if n not in ruled]
        print(f"  not in registry: {len(unreg)} ({len(unreg) - len(fresh)} already ruled in triage/, {len(fresh)} unruled)")
        for n in fresh:
            print(f"    UNRULED {n}")
        rows = [r for r in npcs if not r["exclusion"] and r["n_entries"] >= a.min_entries
                and (a.include_drafted or r["draft"] == "none")]
        rows = [{"stem": r["stem"], "subject": r["subject"], "n_entries": r["n_entries"],
                 "n_scenes": r["n_scenes"]} for r in rows]
    write_json(c.run / "targets.json", rows)
    print(f"targets: {len(rows)} -> {c.rel(c.run / 'targets.json')}")


def ruled_names(c: Ctx) -> set[str]:
    """Names the GM already ruled in an earlier triage page (cards + saved decisions)."""
    out = set()
    for d in sorted((c.rdir / "triage").glob("*/")):
        items, dec = d / "review_items.json", d / "decisions.json"
        if not (items.exists() and dec.exists()):
            continue
        decided = {k for k, v in json.loads(dec.read_text())["decisions"].items() if v in ("approve", "reject")}
        for it in json.loads(items.read_text())["items"]:
            if it["id"] in decided:
                blob = html.unescape(it["t"] + it["y"] + it.get("ev", ""))
                out.add(blob)
    # a name counts as ruled when it appears as a whole word in a decided card
    class _S(set):
        def __contains__(self, name):
            pat = re.compile(r"(?<![\w])" + re.escape(name) + r"(?![\w])")
            return any(pat.search(b) for b in out)
    return _S()


# ---------------------------------------------------------------- verify

FAIL_RE = re.compile(r"^- (?P<code>[\w-]+) \((?:line (?P<line>\d+)|draft)\): (?P<text>.*?)(?: -- (?P<detail>.*))?$")


def parse_verify_md(p: Path):
    t = p.read_text(encoding="utf-8")
    verdict = re.search(r"\*\*Verdict: (\w+)\*\*", t).group(1)
    sec = t.split("## Failures", 1)[1].split("\n## ", 1)[0]
    fails = []
    for ln in sec.splitlines():
        m = FAIL_RE.match(ln.strip())
        if m:
            fails.append({k: (int(v) if k == "line" and v else v) for k, v in m.groupdict().items()})
    return verdict, fails


def run_verify(c: Ctx, subjects, npc_root=None):
    args = ["npc-verify", *c.range_args()]
    if npc_root:
        args += ["--npc-root", str(npc_root)]
    # npc-verify exits non-zero when any draft fails; that is a result, not an error.
    # Callers read the verdicts from the .verify.md files.
    for i in range(0, len(subjects), 40):
        r = c.sn(*args, "--name", *subjects[i:i + 40], check=False)
        if r.returncode and "verified " not in r.stdout + r.stderr:
            sys.exit(f"npc-verify failed ({r.returncode}):\n{r.stdout[-2000:]}{r.stderr[-2000:]}")
        print((r.stdout + r.stderr).strip().split("\n")[-1])


def cmd_verify(c: Ctx, a):
    t = c.targets()
    run_verify(c, [r["subject"] for r in t])
    out, n_fail = [], 0
    for r in t:
        vp = c.rdir / "draft" / f"{r['stem']}.verify.md"
        if not vp.exists():
            out.append({"stem": r["stem"], "verdict": "missing", "failures": []})
            continue
        verdict, fails = parse_verify_md(vp)
        lines = c.draft(r["stem"]).read_text(encoding="utf-8").split("\n")
        for f in fails:
            if f.get("line"):
                f["draft_line"] = lines[f["line"] - 1]
        n_fail += verdict != "pass"
        out.append({"stem": r["stem"], "subject": r["subject"], "verdict": verdict, "failures": fails})
    write_json(c.run / "verify_failures.json", out)
    codes = collections.Counter(f["code"] for r in out for f in r["failures"])
    print(f"verify: {len(out) - n_fail} pass, {n_fail} fail; failure codes {dict(codes)}")
    for r in out:
        if r["verdict"] != "pass":
            print(f"  {r['stem']}: {r['verdict']} {[(f['code'], f.get('line')) for f in r['failures']]}")


# ---------------------------------------------------------------- evidence lookup

def evidence_items(text: str):
    """(chapter '054', target '054.06'|'entry'|'moment', n) -> item text."""
    items, ch, cur = {}, None, None
    for ln in text.split("\n"):
        m = re.match(r"## Chapter (\d+)", ln)
        if m:
            ch, cur = m.group(1), None
            continue
        m = re.match(r"### (?:Scene (\d+\.\d+)|(Entry)|(Moment))", ln)
        if m and ch:
            tgt = m.group(1) or (m.group(2) or m.group(3)).lower()
            n = 0
            while (ch, tgt, n) in items:
                n += 1
            cur = (ch, tgt, n)
            items[cur] = [ln]
            continue
        if cur:
            items[cur].append(ln)
    return {k: "\n".join(v) for k, v in items.items()}


def cmd_evidence(c: Ctx, a):
    items = evidence_items(c.evidence(a.stem).read_text(encoding="utf-8"))
    for cite in a.cites:  # "054/054.06" or "054/entry"
        ch, tgt = cite.split("/")
        for k, v in items.items():
            if int(k[0]) == int(ch) and k[1] == tgt:
                print(f"===== ch {k[0]} / {k[1]} #{k[2]}\n{v[:a.max_chars]}")


# ---------------------------------------------------------------- edits

EDIT_KEYS = ("id", "stem", "line", "old", "new")


def load_edits(c: Ctx, only_ids=None):
    edits = []
    for f in sorted((c.run / "edits").glob("*.json")):
        for e in json.loads(f.read_text(encoding="utf-8")):
            missing = [k for k in EDIT_KEYS if k not in e]
            if missing:
                sys.exit(f"{f.name}: edit {e.get('id')} lacks {missing}")
            e.setdefault("src", f.stem)
            edits.append(e)
    sup = {e["supersedes"] for e in edits if e.get("supersedes")}
    edits = [e for e in edits if e["id"] not in sup]
    if only_ids is not None:
        edits = [e for e in edits if e["id"] in only_ids]
    for e in edits:
        e["citation_only"] = strip_cites(e["old"]) == strip_cites(e["new"])
    return edits


def strip_cites(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"\[ch [^\]]*\]", "", s)).strip()


def apply_edits(edits, draft_dir: Path, write: bool):
    problems, by = [], collections.defaultdict(list)
    ids = collections.Counter(e["id"] for e in edits)
    problems += [f"duplicate id {i}" for i, n in ids.items() if n > 1]
    for e in edits:
        if "\n" in e["new"] or "\n" in e["old"]:
            problems.append(f"{e['id']}: old/new spans a newline")
        by[e["stem"]].append(e)
    for stem, es in by.items():
        p = draft_dir / f"{stem}.md"
        lines = p.read_text(encoding="utf-8").split("\n")
        spans = collections.defaultdict(list)
        for e in es:
            if e["line"] > len(lines):
                problems.append(f"{e['id']}: line {e['line']} past end of {stem}")
                continue
            ln = lines[e["line"] - 1]
            n = ln.count(e["old"])
            if n != 1:
                problems.append(f"{e['id']}: old occurs {n}x on {stem} L{e['line']}")
                continue
            i = ln.index(e["old"])
            spans[e["line"]].append((i, i + len(e["old"]), e))
        for line, ss in spans.items():
            ss.sort(key=lambda s: s[0])
            for (a1, b1, e1), (a2, b2, e2) in zip(ss, ss[1:]):
                if a2 < b1:
                    problems.append(f"overlap {e1['id']} / {e2['id']} on {stem} L{line}")
            ln = lines[line - 1]
            for i, j, e in sorted(ss, key=lambda s: -s[0]):
                ln = ln[:i] + e["new"] + ln[j:]
            lines[line - 1] = ln
        if write:
            p.write_text("\n".join(lines), encoding="utf-8")
    return problems


def cmd_check_edits(c: Ctx, a):
    edits = load_edits(c)
    srcs = collections.Counter(e["src"] for e in edits)
    print(f"edits: {len(edits)} {dict(srcs)}; citation-only {sum(e['citation_only'] for e in edits)}")
    scratch = Path(tempfile.mkdtemp(prefix="ndc-npcroot-"))
    shutil.copytree(c.rdir, scratch / c.range, ignore=shutil.ignore_patterns("runs", "cleanup", "verify_runs"))
    probs = apply_edits(edits, scratch / c.range / "draft", write=True)
    print(f"problems: {len(probs)}")
    for p in probs:
        print("  ", p)
    stems = sorted({e["stem"] for e in edits})
    run_verify(c, [c.subject(s) for s in stems], npc_root=scratch)
    still = []
    for s in stems:
        verdict, fails = parse_verify_md(scratch / c.range / "draft" / f"{s}.verify.md")
        if verdict != "pass":
            still.append((s, [(f["code"], f.get("line"), f["text"][:80]) for f in fails]))
    print(f"after scratch apply: {len(stems) - len(still)}/{len(stems)} edited drafts pass verify")
    for s, f in still:
        print(f"  FAIL {s}: {f}")
    shutil.rmtree(scratch)
    sys.exit(1 if probs or still else 0)


def word_diff(old: str, new: str):
    a, b = re.findall(r"\s+|\w+|[^\w\s]", old), re.findall(r"\s+|\w+|[^\w\s]", new)
    o, n = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        x, y = esc("".join(a[i1:i2])), esc("".join(b[j1:j2]))
        if tag == "equal":
            o.append(x); n.append(y)
        else:
            if x: o.append(f"<del style='background:#f8d0d0'>{x}</del>")
            if y: n.append(f"<ins style='background:#c8efc8;text-decoration:none'>{y}</ins>")
    return "".join(o), "".join(n)


def build_page(items_path: Path, page_path: Path):
    r = subprocess.run([sys.executable, str(REVIEW_PAGE / "build_review.py"), "--in", str(items_path),
                        "--out", str(page_path)], text=True, capture_output=True)
    if r.returncode:
        sys.exit(f"build_review failed: {r.stdout}{r.stderr}")
    print(f"page: {page_path}")


def cmd_corrections_page(c: Ctx, a):
    edits = load_edits(c)
    auto = [e for e in edits if e["citation_only"]]
    cards, subj = [], {}
    for e in sorted((e for e in edits if not e["citation_only"]), key=lambda e: (e["stem"], e["line"], e["id"])):
        s = subj.setdefault(e["stem"], c.subject(e["stem"]))
        o, n = word_diff(e["old"], e["new"])
        kind = e.get("kind") or ("verify" if e["src"].startswith("verify") else "edit")
        cards.append({
            "id": e["id"],
            "t": f"<b>{esc(s)}</b> · L{e['line']} · <i>{esc(kind)}</i> — {esc(e.get('why', ''))}",
            "y": f"Change the draft to:<br><blockquote>{n or '<i>(clause deleted)</i>'}</blockquote>",
            "n": "Keep the draft verbatim (no change from this card).",
            "ev": (f"Draft now:<br><blockquote>{o}</blockquote>"
                   + (f"Source: {esc(e['evidence'])}<br>" if e.get("evidence") else "")
                   + f"<small>{esc(e['stem'])}.md L{e['line']} · confidence {esc(e.get('confidence', '?'))}"
                   + f" · {esc(e['src'])}</small>"),
        })
    extra_ids = []
    for x in a.extra or []:  # hand-written cards (e.g. canon conflicts), same schema
        xs = json.loads(Path(x).read_text(encoding="utf-8"))
        cards += xs
        extra_ids += [i["id"] for i in xs]
    n_stems = len({e["stem"] for e in edits})
    doc = {
        "title": a.title or "NPC draft corrections",
        "reviewId": f"npc-cleanup:{c.range}:{a.run}:corrections",
        "outputName": f"npc_corrections_{a.run}_decisions.json",
        "eyebrow": f"{c.root.name} / summary-native NPC dossiers / {c.range}",
        "lede": (f"{len(cards)} proposed changes across {n_stems} drafts. Approve = change the draft to the green "
                 "text. Reject = keep the line verbatim. Discuss = we talk it through first. Nothing is edited "
                 "until you save."),
        "footer": (f"Applied without a card (citation-only, no wording change): {len(auto)}"
                   + (" — " + ", ".join(e["id"] for e in auto) if auto else "") + ". "
                   "Number/ordinal checker flags are handled later under your ≥90% policy."),
        "items": cards,
    }
    d = c.run / "corrections"
    write_json(d / "review_items.json", doc)
    write_json(d / "citation_only_ids.json", [e["id"] for e in auto])
    write_json(d / "extra_ids.json", extra_ids)
    build_page(d / "review_items.json", d / "review.html")
    print(f"cards: {len(cards)}; citation-only auto: {len(auto)}")


def read_decisions(decisions: Path, items: Path):
    r = subprocess.run([sys.executable, str(REVIEW_PAGE / "read_decisions.py"), "--in", str(decisions),
                        "--items", str(items)], text=True, capture_output=True)
    if r.returncode:
        sys.exit(f"read_decisions refused ({r.returncode}): {r.stdout}{r.stderr}")
    return json.loads(decisions.read_text(encoding="utf-8"))


def cmd_approved_ids(c: Ctx, a):
    d = c.run / "corrections"
    dec = read_decisions(Path(a.decisions), d / "review_items.json")
    asked = [i["id"] for i in json.loads((d / "review_items.json").read_text())["items"]]
    v = dec.get("decisions", {})
    by = collections.defaultdict(list)
    for i in asked:
        by[v.get(i, "UNDECIDED")].append(i)
    # Hand-written cards (canon conflicts) are rulings, not edits: report them, never apply them.
    xp = d / "extra_ids.json"
    extra = set(json.loads(xp.read_text())) if xp.exists() else set()
    for i in sorted(extra):
        print(f"  RULING {i}: {v.get(i, 'UNDECIDED')}  note: {dec.get('notes', {}).get(i, '')}")
    approved = [i for i in by["approve"] if i not in extra] + json.loads((d / "citation_only_ids.json").read_text())
    write_json(d / "approved_ids.json", approved)
    print(f"savedAt {dec.get('savedAt')}: " + ", ".join(f"{k} {len(x)}" for k, x in by.items()))
    for k in ("discuss", "UNDECIDED"):
        for i in by.get(k, []):
            print(f"  {k}: {i}  note: {dec.get('notes', {}).get(i, '')}")
    for i, n in dec.get("notes", {}).items():
        if v.get(i) in ("approve", "reject"):
            print(f"  NOTE on {v[i]} {i}: {n}")
    print(f"approved_ids.json: {len(approved)} (incl. citation-only). DISCUSS and UNDECIDED are NOT in it.")


def cmd_apply(c: Ctx, a):
    ids = set(json.loads(Path(a.ids).read_text()))
    edits = load_edits(c, only_ids=ids)
    missing = ids - {e["id"] for e in edits}
    if missing:
        sys.exit(f"ids not found in edits/: {sorted(missing)}")
    probs = apply_edits(edits, c.rdir / "draft", write=False)
    if probs:
        sys.exit("refusing; dry run found problems:\n  " + "\n  ".join(probs))
    apply_edits(edits, c.rdir / "draft", write=True)
    stems = sorted({e["stem"] for e in edits})
    subjects = [c.subject(s) for s in stems]
    run_verify(c, subjects)
    for i in range(0, len(subjects), 40):
        c.sn("npc-compose", *c.range_args(), "--name", *subjects[i:i + 40])
    log = c.run / "applied.json"
    prev = json.loads(log.read_text()) if log.exists() else []
    write_json(log, prev + [{"id": e["id"], "stem": e["stem"], "line": e["line"]} for e in edits])
    bad = [s for s in stems if parse_verify_md(c.rdir / "draft" / f"{s}.verify.md")[0] != "pass"]
    print(f"applied {len(edits)} edits to {len(stems)} drafts; verify fail: {bad or 'none'}; recomposed gm/ copies")


# ---------------------------------------------------------------- flags (offline advisories)

def cmd_flags(c: Ctx, a):
    from pipelines.summary_native import npc_check
    from pipelines.summary_native.review import verification as V
    out = []
    for r in c.targets():
        stem = r["stem"]
        draft = c.draft(stem).read_text(encoding="utf-8")
        ev = c.evidence(stem).read_text(encoding="utf-8")
        found = V._deterministic_semantic_advisories(SimpleNamespace(draft_text=draft, evidence_text=ev))
        idx = npc_check.EvidenceIndex.of(npc_check.split_chapters(ev))
        lines = draft.splitlines()
        by_line = collections.defaultdict(list)
        for f in found:
            by_line[f.line].append(f.code)
        for line, codes in sorted(by_line.items()):
            text = lines[line - 1]
            claim_markers = V._markers(V._claim_without_pointers(text))
            union, chapters = set(), set()
            for _br, (ch, it) in npc_check.citation_parts(text):
                if ch < 0:
                    continue
                chapters.add(ch)
                occ = idx.items_at(ch, it)
                if len(occ) == 1:
                    union |= V._markers(occ[0].text)
            missing = sorted(claim_markers - union)
            if not missing:
                cls = "covered"
            elif all(m.isdigit() and int(m) in chapters and re.search(rf"Chapters?\s+0*{int(m)}\b", text)
                     for m in missing):
                cls = "chapter-ref"
            else:
                cls = "inspect"
            out.append({"stem": stem, "line": line, "codes": codes, "class": cls, "missing": missing,
                        "text": text})
    write_json(c.run / "flags.json", out)
    tally = collections.Counter(o["class"] for o in out)
    print(f"flag lines: {len(out)} {dict(tally)}")
    for o in out:
        if o["class"] == "inspect":
            print(f"  INSPECT {o['stem']} L{o['line']} {o['codes']} missing={o['missing']}\n    {o['text'][:220]}")


# ---------------------------------------------------------------- selection / review

def cmd_selection(c: Ctx, a):
    t = c.targets()
    run_verify(c, [r["subject"] for r in t])
    bad = [r["stem"] for r in t if parse_verify_md(c.rdir / "draft" / f"{r['stem']}.verify.md")[0] != "pass"]
    if bad:
        sys.exit(f"refusing: these drafts fail verify, the sign-off item would refuse: {bad}")
    summ = c.summaries()
    sel = {"dossiers": [{"id": r["stem"], "npc": c.subject(r["stem"]), "draft_path": c.rel(c.draft(r["stem"])),
                         "evidence_path": c.rel(c.evidence(r["stem"])), "summary_paths": summ} for r in t]}
    p = write_json(c.run / "review_selection.json", sel)
    print(f"selection: {len(t)} dossiers, {len(summ)} summaries -> {c.rel(p)}")
    print(f"next: summary_native review create --kind npc_verification --selection {c.rel(p)} --campaign-dir . --json")


def review_items(c: Ctx, rid):
    items = {}
    for p in (c.root / "docs/reviews" / rid / "items").glob("*/*.json"):
        i = json.loads(p.read_text(encoding="utf-8"))
        if i["item_id"] not in items or i["revision"] > items[i["item_id"]]["revision"]:
            items[i["item_id"]] = i
    gen = json.loads((c.root / "docs/reviews" / rid / "manifest.json").read_text())["generation"]
    return items, gen


def decision(i, verdict, note):
    signoff = i["proposed_action"]["action"] == "signoff_npc_draft"
    disp = {"approve": "document_signoff" if signoff else "accept_no_change",
            "reject": "reject_action", "discuss": "defer"}[verdict]
    return {"item_id": i["item_id"], "item_revision": i["revision"], "review_digest": i["review_digest"],
            "expected_decision_revision": 0, "verdict": verdict, "disposition": disp, "note": note}


def write_batches(c: Ctx, name, decisions, reviewer, gen):
    paths = []
    for k in range(0, len(decisions), BATCH):
        body = {"version": 1, "request_id": f"{name}-{uuid.uuid4().hex[:12]}", "review_generation": gen,
                "reviewer": reviewer, "decisions": decisions[k:k + BATCH]}
        paths.append(write_json(c.run / "ledger" / f"{name}_{k // BATCH + 1:02d}.json", body))
    return paths


POLICY_REASON = {
    "typography-normalised": "Quote matches the source word for word; only curly/straight marks differ.",
    "covered": "Every number/ordinal on the line appears in one of the line's cited items, attached to the same fact.",
    "chapter-ref": "The flagged number is a 'Chapter N' reference, and the line cites that chapter.",
}


def cmd_policy(c: Ctx, a):
    items, gen = review_items(c, a.review)
    flags = {(f["stem"], f["line"]): f for f in json.loads((c.run / "flags.json").read_text())}
    extra = json.loads(Path(a.approve_extra).read_text()) if a.approve_extra else {}
    auto, gm = [], []
    for i in items.values():
        if i["proposed_action"]["action"] == "signoff_npc_draft":
            continue
        code = i["diagnostics"][0]["legacy_code"]
        stem = Path(i["locator"]["source_path"]).stem
        line = i["locator"].get("display_line")
        reason = None
        if i["item_id"] in extra:
            reason = extra[i["item_id"]]
        elif code == "typography-normalised":
            reason = POLICY_REASON[code]
        elif code in ("number-inconsistency", "ordinal-inconsistency"):
            f = flags.get((stem, line))
            if f and f["class"] in ("covered", "chapter-ref"):
                reason = POLICY_REASON[f["class"]]
        if reason:
            auto.append(decision(i, "approve", f"GM-delegated ≥90% policy: {reason}"))
        else:
            gm.append({"item_id": i["item_id"], "stem": stem, "line": line, "code": code,
                       "message": i["diagnostics"][0]["message"], "claim": i.get("claim_text", "")})
    paths = write_batches(c, "policy", auto, "Claude (GM-delegated policy)", gen)
    write_json(c.run / "gm_flags.json", gm)
    print(f"policy-approved: {len(auto)} in {len(paths)} batch file(s); left for the GM: {len(gm)} -> gm_flags.json")
    for g in gm:
        print(f"  GM {g['stem']} L{g['line']} {g['code']}: {g['message'][:120]}")
    print("apply each batch: summary_native review decide " + a.review + " --decisions <file> --campaign-dir . --json")


def cmd_signoff_page(c: Ctx, a):
    items, _ = review_items(c, a.review)
    gm = json.loads((c.run / "gm_flags.json").read_text()) if (c.run / "gm_flags.json").exists() else []
    cards, shas = [], {}
    for g in gm:
        i = items[g["item_id"]]
        ex = next((e.get("exact_excerpt") for e in i.get("evidence", []) if e.get("exact_excerpt")), "")
        cards.append({"id": g["item_id"],
                      "t": f"<b>{esc(c.subject(g['stem']))}</b> · L{g['line']} · checker flag <i>{esc(g['code'])}</i>",
                      "y": "Keep the line as written (the claim is supported).",
                      "n": "The claim is wrong; we fix the line (this voids that draft's sign-off and needs a fresh review).",
                      "ev": f"Claim:<blockquote>{esc(g['claim'])}</blockquote>Checker: {esc(g['message'])}"
                            + (f"<br>Cited source:<blockquote>{esc(ex[:1500])}</blockquote>" if ex else "")})
    for i in sorted((i for i in items.values() if i["proposed_action"]["action"] == "signoff_npc_draft"),
                    key=lambda i: i["proposed_action"]["details"]["npc"]):
        d = i["proposed_action"]["details"]
        body = (c.root / d["draft_path"]).read_bytes()
        if sha256(body) != d["draft_sha256"]:
            sys.exit(f"{d['draft_path']} changed since the review was created; build a fresh review")
        text = re.sub(r"\A<!--.*?-->\n", "", body.decode("utf-8"), flags=re.S)
        shas[i["item_id"]] = d["draft_sha256"]
        cards.append({"id": i["item_id"],
                      "t": f"<b>{esc(d['npc'])}</b> — sign off this exact draft for publication",
                      "y": f"Sign off sha256 <code>{d['draft_sha256'][:16]}…</code>; npc-publish may publish it.",
                      "n": "No sign-off; the dossier is not published this run.",
                      "ev": f"<details><summary>Full draft ({len(text.splitlines())} lines, verify {esc(d['mechanical_verdict'])})"
                            f"</summary><pre style='white-space:pre-wrap'>{esc(text)}</pre></details>"})
    doc = {"title": a.title or "NPC dossier sign-off",
           "reviewId": f"npc-cleanup:{c.range}:{a.run}:signoff:{a.review}",
           "outputName": f"npc_signoff_{a.run}_decisions.json",
           "eyebrow": f"{c.root.name} / {a.review}",
           "lede": (f"{len(shas)} drafts to sign off" + (f", plus {len(gm)} checker flags I was not sure about" if gm else "")
                    + ". Approve a draft = it can be published exactly as shown."),
           "footer": a.footer or "",
           "items": cards}
    d = c.run / "signoff"
    write_json(d / "review_items.json", doc)
    write_json(d / "draft_sha256.json", shas)
    build_page(d / "review_items.json", d / "review.html")


def cmd_ledger(c: Ctx, a):
    d = c.run / "signoff"
    dec = read_decisions(Path(a.decisions), d / "review_items.json")
    items, gen = review_items(c, a.review)
    shas = json.loads((d / "draft_sha256.json").read_text())
    asked = [x["id"] for x in json.loads((d / "review_items.json").read_text())["items"]]
    out, unmarked = [], []
    for iid in asked:
        v = dec["decisions"].get(iid)
        if v is None:
            unmarked.append(iid)
            continue
        i = items[iid]
        if iid in shas:
            cur = sha256((c.root / i["proposed_action"]["details"]["draft_path"]).read_bytes())
            if cur != shas[iid]:
                sys.exit(f"{iid}: draft bytes changed since the page was built; the GM signed different bytes")
        note = dec.get("notes", {}).get(iid, "")
        out.append(decision(i, v, (note + " " if note else "") + f"GM ruling, page saved {dec.get('savedAt')}."))
    paths = write_batches(c, "gm", out, "GM", gen)
    print(f"GM decisions: {collections.Counter(x['verdict'] for x in out)} in {len(paths)} batch file(s)")
    if unmarked:
        print(f"UNMARKED (re-ask, never default): {unmarked}")


def cmd_gate(c: Ctx, a):
    from pipelines.summary_native.npc_publish import _current_draft_signoff
    ok = []
    t = c.targets()
    for r in t:
        p = c.draft(r["stem"])
        if _current_draft_signoff(c.root, p, sha256(p.read_bytes())):
            ok.append(r["stem"])
    print(f"publish gate: {len(ok)}/{len(t)} drafts carry a current sign-off")
    for r in t:
        if r["stem"] not in ok:
            print(f"  NO SIGN-OFF {r['stem']}")


def cmd_ctx(c: Ctx, a):
    pat = re.compile(a.regex, re.I)
    cues = []
    for b in Path(a.vtt).read_text(encoding="utf-8").split("\n\n"):
        ls = b.strip().split("\n")
        t = [l for l in ls if "-->" in l]
        if t:
            cues.append((t[0].split(" -->")[0], " ".join(ls[ls.index(t[0]) + 1:])))
    shown = set()
    for i, (ts, tx) in enumerate(cues):
        if pat.search(tx):
            for j in range(max(0, i - a.before), min(len(cues), i + a.after + 1)):
                if j not in shown:
                    print(cues[j][0], cues[j][1]); shown.add(j)
            print("----")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--campaign-dir", default=".")
    ap.add_argument("--npc-root", default=None)
    sp = ap.add_subparsers(dest="cmd", required=True)

    def sub(name, fn, run=True):
        p = sp.add_parser(name)
        if run:
            p.add_argument("--run", required=True, help="run tag; files go to <range>/cleanup/<tag>/")
        p.set_defaults(fn=fn)
        return p

    p = sub("targets", cmd_targets)
    p.add_argument("--server", default="http://127.0.0.1:5000")
    p.add_argument("--min-entries", type=int, default=1)
    p.add_argument("--include-drafted", action="store_true")
    p.add_argument("--from-draft-run", help="take the targets from runs/<id>/selection.json instead")
    sub("verify", cmd_verify)
    p = sub("evidence", cmd_evidence, run=False)
    p.add_argument("stem"); p.add_argument("cites", nargs="+", help="054/054.06  054/entry  054/moment")
    p.add_argument("--max-chars", type=int, default=4000)
    sub("check-edits", cmd_check_edits)
    p = sub("corrections-page", cmd_corrections_page)
    p.add_argument("--title"); p.add_argument("--extra", nargs="*", help="JSON files of hand-written cards")
    p = sub("approved-ids", cmd_approved_ids); p.add_argument("--decisions", required=True)
    p = sub("apply", cmd_apply); p.add_argument("--ids", required=True)
    sub("flags", cmd_flags)
    sub("selection", cmd_selection)
    p = sub("policy", cmd_policy); p.add_argument("--review", required=True)
    p.add_argument("--approve-extra", help="JSON {item_id: reason} for flags Claude checked by hand at >=90%%")
    p = sub("signoff-page", cmd_signoff_page); p.add_argument("--review", required=True)
    p.add_argument("--title"); p.add_argument("--footer")
    p = sub("ledger", cmd_ledger); p.add_argument("--review", required=True); p.add_argument("--decisions", required=True)
    sub("gate", cmd_gate)
    p = sub("ctx", cmd_ctx, run=False)
    p.add_argument("vtt"); p.add_argument("regex")
    p.add_argument("before", type=int, nargs="?", default=3); p.add_argument("after", type=int, nargs="?", default=3)

    a = ap.parse_args()
    a.fn(Ctx(a), a)


if __name__ == "__main__":
    main()
