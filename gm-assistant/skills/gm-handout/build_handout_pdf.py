#!/usr/bin/env python3
"""Build the player PDF for a gm-handout file.

The handout's origin is its Markdown file (notes/handouts/NN_slug.md). The
in-world text is the first fenced code block in it (``` or ```text). This
script renders that block, and only that block, to a one-sheet PDF: aged
paper, brown ink, serif type. The PDF is a replica, so rebuild it rather
than editing it.

Layout comes from the fixed-width text itself:

  * Lines indented 8+ spaces at the top of the block are the header,
    centered. The first group is bold and larger; later groups are smaller.
  * Inside the body, a one-line paragraph indented 8+ spaces is centered.
    If it is all capitals it is set large and bold (a name on a writ).
  * A one-line paragraph in capitals at the left margin, such as "PURPOSE"
    or "2. THE SHARE", is a section heading.
  * Lines starting "1." / "(a)" / "-" / "*" are list items with a hanging
    indent.
  * A paragraph of short lines (34 characters or fewer) keeps its line
    breaks: signatures and titles. Indented 16+ spaces, it sits to the right.
  * Every other paragraph is reflowed.

Options go in an HTML comment anywhere in the Markdown file, which renders
invisibly:

  <!-- handout-pdf: title="Phandalin - Welcome" author="Linene Graywind"
       italic="Linene Graywind; Aldus Hern" accent="DRAFT. NOT ADOPTED."
       border=true seal="N" -->

  title / author  PDF metadata. The default title is the Markdown H1.
  italic          ;-separated lines set in italics (signatures).
  accent          ;-separated lines set in red.
  border          true draws a double rule round the page.
  seal            one or two letters in a wax-seal roundel, bottom right.

Usage (ReportLab is installed in ~/.venv):

  ~/.venv/bin/python build_handout_pdf.py notes/handouts/03_x.md [out.pdf]

The default output is <campaign>/output/pdf/<stem>.pdf for a file under
<campaign>/notes/handouts/. After building, the script extracts the PDF's
text with pdftotext (if installed) and fails unless it carries exactly the
words of the code block, in order.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
from xml.sax.saxutils import escape

INK = HexColor("#4a3424")
PAPER = HexColor("#fbf9f2")
ACCENT = HexColor("#8a2b1e")
GOLD = HexColor("#b08d57")

FONT_DIRS = ["/usr/share/fonts/truetype/liberation", "/usr/share/fonts/liberation"]
FONTS = {
    "Serif": "LiberationSerif-Regular.ttf",
    "Serif-Bold": "LiberationSerif-Bold.ttf",
    "Serif-Italic": "LiberationSerif-Italic.ttf",
}


def register_fonts():
    for d in FONT_DIRS:
        if all((Path(d) / f).exists() for f in FONTS.values()):
            for name, f in FONTS.items():
                pdfmetrics.registerFont(TTFont(name, str(Path(d) / f)))
            pdfmetrics.registerFontFamily(
                "Serif", normal="Serif", bold="Serif-Bold", italic="Serif-Italic"
            )
            return "Serif", "Serif-Bold", "Serif-Italic"
    return "Times-Roman", "Times-Bold", "Times-Italic"


def parse_options(md):
    m = re.search(r"<!--\s*handout-pdf:(.*?)-->", md, re.S)
    opts = {}
    if m:
        for k, v in re.findall(r'(\w+)=("[^"]*"|\S+)', m.group(1)):
            opts[k] = v.strip('"')
    h1 = re.search(r"^#\s+(.+)$", md, re.M)
    opts.setdefault("title", h1.group(1).strip() if h1 else "Handout")
    opts.setdefault("author", "")
    split = lambda s: {x.strip() for x in s.split(";") if x.strip()}
    opts["italic"] = split(opts.get("italic", ""))
    opts["accent"] = split(opts.get("accent", ""))
    opts["border"] = str(opts.get("border", "false")).lower() == "true"
    return opts


def text_block(md):
    m = re.search(r"^```[a-zA-Z]*\n(.*?)^```", md, re.S | re.M)
    if not m:
        sys.exit("no fenced code block found: the in-world text must be in one")
    return m.group(1).rstrip("\n").split("\n")


def indent(line):
    return len(line) - len(line.lstrip(" "))


def paragraphs(lines):
    paras, cur = [], []
    for line in lines:
        if line.strip():
            cur.append(line.rstrip())
        elif cur:
            paras.append(cur)
            cur = []
    if cur:
        paras.append(cur)
    return paras


LIST_RE = re.compile(r"^\s*(\d+\.|\([a-z0-9]+\)|[-*])\s+")
CAPS_RE = re.compile(r"^(\d+\.\s+)?[A-Z0-9][A-Z0-9 ,.'&:-]*$")


def build(md_path, out_path):
    md = Path(md_path).read_text()
    opts = parse_options(md)
    lines = text_block(md)
    regular, bold, italic = register_fonts()

    base = ParagraphStyle("body", fontName=regular, fontSize=11, leading=14.5,
                          textColor=INK, spaceAfter=7)
    st = {
        "body": base,
        "h1": ParagraphStyle("h1", parent=base, fontName=bold, fontSize=12,
                             alignment=TA_CENTER, spaceAfter=1),
        "h2": ParagraphStyle("h2", parent=base, fontName=bold, fontSize=9.5,
                             alignment=TA_CENTER, spaceAfter=1),
        "center": ParagraphStyle("center", parent=base, alignment=TA_CENTER,
                                 fontSize=10, leading=13, spaceAfter=0),
        "name": ParagraphStyle("name", parent=base, fontName=bold, fontSize=14,
                               alignment=TA_CENTER, spaceBefore=4, spaceAfter=9),
        "head": ParagraphStyle("head", parent=base, fontName=bold,
                               spaceBefore=6, spaceAfter=3),
        "item": ParagraphStyle("item", parent=base, leftIndent=30,
                               firstLineIndent=-18, spaceAfter=3),
        "short": ParagraphStyle("short", parent=base, spaceAfter=0),
        "right": ParagraphStyle("right", parent=base, leftIndent=250, spaceAfter=0),
    }

    def markup(text):
        t = escape(text)
        if text in opts["italic"]:
            return f"<i>{t}</i>"
        if text in opts["accent"]:
            return f'<font color="{ACCENT.hexval()}"><b>{t}</b></font>'
        return t

    paras = paragraphs(lines)
    story = []

    # Header: leading paragraphs whose every line is indented 8+ spaces.
    header = []
    while paras and all(indent(l) >= 8 for l in paras[0]):
        header.append(paras.pop(0))
    for gi, group in enumerate(header):
        for li, line in enumerate(group):
            text = line.strip()
            if text in opts["accent"]:
                story.append(Paragraph(markup(text), ParagraphStyle(
                    "acc", parent=st["h1"], spaceBefore=6, spaceAfter=4)))
            elif not CAPS_RE.match(text):
                story.append(Paragraph(markup(text), st["center"]))
            else:
                story.append(Paragraph(markup(text), st["h1"] if gi == 0 else st["h2"]))
        story.append(Spacer(1, 5))
    if header:
        story.append(HRFlowable(width="100%", color=INK, thickness=0.6,
                                spaceBefore=2, spaceAfter=10))

    for p in paras:
        texts = [l.strip() for l in p]
        if len(p) == 1 and indent(p[0]) >= 8 and indent(p[0]) < 16:
            style = st["name"] if CAPS_RE.match(texts[0]) else st["center"]
            story.append(Paragraph(markup(texts[0]), style))
        elif len(p) == 1 and indent(p[0]) >= 16 and CAPS_RE.match(texts[0]):
            story.append(Paragraph(markup(texts[0]), st["name"]))
        elif len(p) == 1 and CAPS_RE.match(texts[0]) and len(texts[0]) <= 40:
            story.append(Paragraph(markup(texts[0]), st["head"]))
        elif all(len(t) <= 34 for t in texts) and (len(p) > 1 or indent(p[0]) >= 16):
            style = st["right"] if all(indent(l) >= 16 for l in p) else st["short"]
            story.append(Spacer(1, 4))
            for t in texts:
                story.append(Paragraph(markup(t), style))
            story.append(Spacer(1, 8))
        elif any(LIST_RE.match(l) for l in p):
            intro, items = [], []
            for l in p:
                if LIST_RE.match(l):
                    items.append([l.strip()])
                elif items:
                    items[-1].append(l.strip())
                else:
                    intro.append(l.strip())
            if intro:
                story.append(Paragraph(markup(" ".join(intro)), st["body"]))
            for it in items:
                story.append(Paragraph(markup(" ".join(it)), st["item"]))
            story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(markup(" ".join(texts)), st["body"]))

    seal = opts.get("seal")

    def page(c, doc):
        w, h = letter
        c.saveState()
        c.setFillColor(PAPER)
        c.rect(0, 0, w, h, stroke=0, fill=1)
        if opts["border"]:
            c.setStrokeColor(GOLD)
            c.setLineWidth(1.2)
            c.rect(36, 36, w - 72, h - 72)
            c.setLineWidth(0.5)
            c.rect(42, 42, w - 84, h - 84)
        if seal:
            x, y = w - 100, 100
            c.setStrokeColor(ACCENT)
            c.setLineWidth(1)
            c.circle(x, y, 22)
            c.setLineWidth(0.5)
            c.circle(x, y, 18)
            c.setFillColor(ACCENT)
            c.setFont(bold, 16)
            c.drawCentredString(x, y - 5.5, seal)
        c.restoreState()

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(out_path), pagesize=letter, leftMargin=90,
                            rightMargin=90, topMargin=72, bottomMargin=72,
                            title=opts["title"], author=opts["author"])
    doc.build(story, onFirstPage=page, onLaterPages=page)
    return lines, seal


def verify(lines, out_path, seal):
    if not shutil.which("pdftotext"):
        print("pdftotext not installed: text not verified", file=sys.stderr)
        return True
    pdf = subprocess.run(["pdftotext", str(out_path), "-"], capture_output=True,
                         text=True, check=True).stdout
    words = lambda t: re.findall(r"\S+", t)
    want, got = words("\n".join(lines)), words(pdf)
    if seal and got and got[-1] == seal:
        got = got[:-1]
    if want == got:
        print(f"verified: {len(want)} words match the code block")
        return True
    import difflib
    diff = [d for d in difflib.ndiff(want, got) if d[0] in "+-"]
    print("TEXT MISMATCH between the code block and the PDF:", diff[:30], file=sys.stderr)
    return False


def default_out(md_path):
    p = Path(md_path).resolve()
    if p.parent.name == "handouts" and p.parent.parent.name == "notes":
        return p.parent.parent.parent / "output" / "pdf" / f"{p.stem}.pdf"
    return p.with_suffix(".pdf")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("handout", help="the handout's Markdown file")
    ap.add_argument("out", nargs="?", help="output PDF (default: <campaign>/output/pdf/<stem>.pdf)")
    a = ap.parse_args()
    out = Path(a.out) if a.out else default_out(a.handout)
    lines, seal = build(a.handout, out)
    print(f"wrote {out}")
    sys.exit(0 if verify(lines, out, seal) else 1)


if __name__ == "__main__":
    main()
