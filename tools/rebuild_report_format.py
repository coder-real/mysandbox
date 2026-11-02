#!/usr/bin/env python3
"""Rebuild 'Fox's Car Safety System-33 (5).docx' using the formatting of
'Fox's Car Safety System-2.docx'.

The new document's text, tables and embedded figure objects are preserved.
The old document contributes: styles, numbering, settings, footers, section
layout, page numbering, live TOC / table-of-tables / table-of-figures fields,
and chapter-based live captions.
"""
import copy
import re
import zipfile
from pathlib import Path

from lxml import etree as ET

ROOT = Path(__file__).resolve().parent.parent
OLD = ROOT / "Fox's Car Safety System-2.docx"
NEW = ROOT / "Fox's Car Safety System-33 (5).docx"
OUT = ROOT / "Fox's Car Safety System-33 (Reformatted).docx"

NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_XML = "http://www.w3.org/XML/1998/namespace"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"
NS_PKGREL = "http://schemas.openxmlformats.org/package/2006/relationships"

NSMAP = {
    "w": NS_W,
    "r": NS_R,
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "w10": "urn:schemas-microsoft-com:office:word",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
}


def W(t):
    return "{%s}%s" % (NS_W, t)


def R(t):
    return "{%s}%s" % (NS_R, t)


def mk(tag, attrs=None, text=None):
    e = ET.Element(tag)
    for k, v in (attrs or {}).items():
        e.set(k, v)
    if text is not None:
        e.text = text
    return e


def sub(parent, tag, attrs=None, text=None):
    e = mk(tag, attrs, text)
    parent.append(e)
    return e


def wval(name, value):
    return {W("val"): value}


def para_text(p):
    out = []
    for n in p.iter():
        if n.tag == W("t"):
            out.append(n.text or "")
        elif n.tag == W("tab"):
            out.append("\t")
    return "".join(out)


# --------------------------------------------------------------------------
# field / bookmark helpers
# --------------------------------------------------------------------------
def rpr_hidden():
    rp = mk(W("rPr"))
    sub(rp, W("noProof"))
    sub(rp, W("webHidden"))
    return rp


def r_fld(kind, hidden=False):
    r = mk(W("r"))
    if hidden:
        r.append(rpr_hidden())
    sub(r, W("fldChar"), {W("fldCharType"): kind})
    return r


def r_instr(text, hidden=False):
    r = mk(W("r"))
    if hidden:
        r.append(rpr_hidden())
    i = sub(r, W("instrText"))
    i.set("{%s}space" % NS_XML, "preserve")
    i.text = text
    return r


def r_text(text, bold=False, hidden=False):
    r = mk(W("r"))
    rp = mk(W("rPr"))
    if bold:
        sub(rp, W("b"))
    if hidden:
        sub(rp, W("noProof"))
        sub(rp, W("webHidden"))
    if len(rp):
        r.append(rp)
    t = sub(r, W("t"))
    t.set("{%s}space" % NS_XML, "preserve")
    t.text = text
    return r


def r_tab(hidden=False):
    r = mk(W("r"))
    if hidden:
        r.append(rpr_hidden())
    sub(r, W("tab"))
    return r


def field_seq(label, cached, chapter):
    """STYLEREF 1 \\s + '.' + SEQ <label> \\* ARABIC \\s 1"""
    runs = []
    runs.append(r_fld("begin", True))
    runs.append(r_instr(" STYLEREF 1 \\s ", True))
    runs.append(r_fld("separate", True))
    runs.append(r_text(str(chapter), hidden=True))
    runs.append(r_fld("end", True))
    runs.append(r_text("."))
    runs.append(r_fld("begin", True))
    runs.append(r_instr(" SEQ %s \\* ARABIC \\s 1 " % label, True))
    runs.append(r_fld("separate", True))
    runs.append(r_text(str(cached), hidden=True))
    runs.append(r_fld("end", True))
    runs.append(r_text(" "))
    return runs


def bookmark_start(name, bid):
    return mk(W("bookmarkStart"), {W("id"): str(bid), W("name"): name})


def bookmark_end(bid):
    return mk(W("bookmarkEnd"), {W("id"): str(bid)})


def add_bookmark(p, name, bid):
    pp = p.find(W("pPr"))
    p.insert(1 if pp is not None else 0, bookmark_start(name, bid))
    p.append(bookmark_end(bid))


def hyperlink_entry(label, anchor, page, style_prefix=""):
    h = mk(W("hyperlink"), {W("anchor"): anchor, W("history"): "1"})
    h.append(r_text(style_prefix + label))
    h.append(r_tab(True))
    h.append(r_fld("begin", True))
    h.append(r_instr(" PAGEREF %s \\h " % anchor, True))
    h.append(r_fld("separate", True))
    h.append(r_text(str(page), hidden=True))
    h.append(r_fld("end", True))
    return h


def make_pPr(children):
    pp = mk(W("pPr"))
    for c in children:
        pp.append(c)
    return pp


def p_style(style):
    return mk(W("pStyle"), {W("val"): style})


def spacing(before=None, after=None, line=None, line_rule="auto"):
    a = {}
    if before is not None:
        a[W("before")] = str(before)
    if after is not None:
        a[W("after")] = str(after)
    if line is not None:
        a[W("line")] = str(line)
        a[W("lineRule")] = line_rule
    return mk(W("spacing"), a)


def tabs_right(pos=9016):
    t = mk(W("tabs"))
    sub(t, W("tab"), {W("val"): "right", W("pos"): str(pos)})
    return t


def numpr(num_id, ilvl=0):
    n = mk(W("numPr"))
    sub(n, W("ilvl"), {W("val"): str(ilvl)})
    sub(n, W("numId"), {W("val"): str(num_id)})
    return n


def jc(val):
    return mk(W("jc"), {W("val"): val})


PPR_ORDER = [
    "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
    "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
    "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct",
    "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
    "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
    "suppressOverlap", "jc", "textDirection", "textAlignment",
    "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr",
    "pPrChange",
]
PPR_RANK = {W(n): i for i, n in enumerate(PPR_ORDER)}


def set_pPr(p, children):
    old = p.find(W("pPr"))
    if old is not None:
        p.remove(old)
    children.sort(key=lambda c: PPR_RANK.get(c.tag, 999))
    p.insert(0, make_pPr(children))


# --------------------------------------------------------------------------
# load packages
# --------------------------------------------------------------------------
old_z = zipfile.ZipFile(OLD)
new_z = zipfile.ZipFile(NEW)

old_doc = ET.fromstring(old_z.read("word/document.xml"))
old_body = old_doc.find(W("body"))
new_doc = ET.fromstring(new_z.read("word/document.xml"))
new_body = new_doc.find(W("body"))
orig_children = list(new_body)

# old section properties, in document order
old_sects = []
for el in old_body:
    sp = el.find(W("pPr") + "/" + W("sectPr")) if el.tag == W("p") else None
    if sp is not None:
        old_sects.append(copy.deepcopy(sp))
if old_body[-1].tag == W("sectPr"):
    old_sects.append(copy.deepcopy(old_body[-1]))
assert len(old_sects) == 6, len(old_sects)

FOOTER_MAP = {
    "rId8": "fmtFooter1",
    "rId9": "fmtFooter2",
    "rId10": "fmtFooter3",
    "rId11": "fmtFooter4",
}
for sp in old_sects:
    for ref in sp.findall(W("footerReference")) + sp.findall(W("headerReference")):
        rid = ref.get(R("id"))
        if rid in FOOTER_MAP:
            ref.set(R("id"), FOOTER_MAP[rid])

# cached page numbers from the old TOC
def norm(s):
    s = re.sub(r"^[\d.\s]+", "", s)
    return re.sub(r"[^a-z0-9]", "", s.lower())


old_pages = {}
old_sdt = old_body[87]
for p in old_sdt.iter(W("p")):
    ps = p.find(W("pPr") + "/" + W("pStyle"))
    if ps is None or not (ps.get(W("val")) or "").startswith("TOC"):
        continue
    level = int(ps.get(W("val"))[3:])
    texts = [t.text or "" for t in p.iter(W("t"))]
    if len(texts) < 2:
        continue
    label = "".join(texts[:-1]).strip()
    page = texts[-1].strip()
    title = re.sub(r"^[\d.]+\s*", "", label)
    if page and norm(title):
        old_pages[(level, norm(title))] = page

# --------------------------------------------------------------------------
# pass 1 - classify the new document's paragraphs
# --------------------------------------------------------------------------
headings = {}       # idx -> level
lists = set()
covers = set()
objects = set()

for i, el in enumerate(orig_children):
    if el.tag != W("p"):
        continue
    pp = el.find(W("pPr"))
    if pp is None:
        continue
    num = pp.find(W("numPr"))
    ind = pp.find(W("ind"))
    left = ind.get(W("left")) if ind is not None else None
    hang = ind.get(W("hanging")) if ind is not None else None
    kn = pp.find(W("keepNext")) is not None
    kl = pp.find(W("keepLines")) is not None
    first_rpr = el.find(W("r") + "/" + W("rPr"))
    bold = first_rpr is not None and first_rpr.find(W("b")) is not None
    if num is not None and kn and kl and bold and left in ("432", "576", "720"):
        headings[i] = {"432": 1, "576": 2, "720": 3}[left]
    elif num is not None and hang == "360" and not kn:
        lists.add(i)
    if el.findall(".//" + W("object")):
        objects.add(i)
    if i <= 41:
        covers.add(i)

UNNUMBERED = {
    "DECLARATION": "i",
    "CERTIFICATION": "ii",
    "DEDICATION": "iii",
    "ACKNOWLEDGEMENT": "iv",
    "REFERENCES": "31",
}

# explicit caption locations in the new document
FIG_CAPTIONS = {
    171: ("HC-SR04 Ultrasonic Sensor Module", 2, 1),
    185: ("Arduino Nano Development Board", 2, 2),
    210: ("16×2 Liquid Crystal Display", 2, 3),
    216: ("I²C LCD interface", 2, 4),
    329: ("Circuit Diagram of Unit 1 — Obstacle Detection System", 3, 1),
    333: ("Circuit Diagram of Unit 2 — Parking Space Allocation System", 3, 2),
    336: ("Operational Flowchart of Unit 2 — Parking Space Allocation System", 3, 3),
    339: ("Operational Flowchart of Unit 2 — Parking Space Allocation System", 3, 4),
}
TBL_CAPTIONS = {
    178: ("Technical specifications of HC-SR04", 2, 1),
    191: ("Arduino Nano Pin Allocation Unit 1 (Obstacle Avoidance System)", 2, 2),
    200: ("Arduino Nano Pin Allocation Unit 2 (Parking Space Allocation System)", 2, 3),
    266: ("Arduino Nano Pin Allocation — Unit 1 (Obstacle Detection)", 3, 1),
    274: ("Arduino Nano Pin Allocation — Unit 2 (Parking Space Allocation)", 3, 2),
    289: ("Obstacle Detection Zones and System Responses — Unit 1", 3, 3),
    313: ("Unit 1 Power Consumption Summary", 3, 4),
    318: ("Unit 2 Power Consumption Summary", 3, 5),
}
# two block-diagram captions present in the new document's own figure list but
# missing from the body; they are inserted after the two block-diagram images.
EXTRA_FIG_CAPTIONS = {
    241: ("Block Diagram of Unit 1 Obstacle Detection System", 2, 5),
    243: ("Block Diagram of Unit 2 Parking Space Allocation System", 2, 6),
}

TOT_TITLE = 92
TOT_ENTRIES = list(range(93, 101))
TOF_TITLE = 104
TOF_ENTRIES = list(range(105, 115))
SECTION_BREAKS = {20: 0, 41: 1, 76: 2, 78: 3, 116: 4}
TOC_AT = 87

# bookmarks + heading numbers + cached TOC pages
bm_counter = [9000]
def next_bm():
    bm_counter[0] += 1
    bid = bm_counter[0]
    return "_Toc%d" % bid, bid


heading_info = []
h1 = h2 = h3 = 0
last_page = "1"
for i in sorted(headings):
    level = headings[i]
    text = para_text(orig_children[i]).strip()
    upper = text.strip().upper()
    unnum = upper in UNNUMBERED
    if unnum:
        prefix = ""
    elif level == 1:
        h1 += 1
        h2 = h3 = 0
        prefix = str(h1)
    elif level == 2:
        h2 += 1
        h3 = 0
        prefix = "%d.%d" % (h1, h2)
    else:
        h3 += 1
        prefix = "%d.%d.%d" % (h1, h2, h3)
    if unnum:
        page = UNNUMBERED[upper]
    else:
        key = (level, norm(text))
        page = old_pages.get(key)
        if page is None:
            # fall back to a page from the old TOC with the same title
            page = next((v for (lv, k), v in old_pages.items() if k == norm(text)),
                        last_page)
        last_page = page
    name, bid = next_bm()
    heading_info.append(dict(idx=i, level=level, text=text, prefix=prefix,
                             page=page, bm=name, bid=bid, unnum=unnum))

HINFO = {h["idx"]: h for h in heading_info}

# caption bookmarks
cap_info = {}
for label, src in (("Figure", FIG_CAPTIONS), ("Table", TBL_CAPTIONS),
                   ("Figure", EXTRA_FIG_CAPTIONS)):
    for idx, (title, chap, seq) in src.items():
        name, bid = next_bm()
        cap_info[(label, idx)] = dict(title=title, chapter=chap, seq=seq,
                                     bm=name, bid=bid, label=label, idx=idx)

fig_order = [("Figure", i) for i in [171, 185, 210, 216, 241, 243, 329, 333, 336, 339]]
tbl_order = [("Table", i) for i in [178, 191, 200, 266, 274, 289, 313, 318]]

# parse the typed front-matter lists into (label, page) for cached field results
def parse_typed_entry(p):
    t = para_text(p)
    parts = t.split("\t")
    parts = [x for x in parts if x.strip()]
    label = parts[0].strip() if parts else ""
    page = parts[-1].strip() if len(parts) > 1 else ""
    return label, page


tot_entries = [(parse_typed_entry(orig_children[i])[0],
                parse_typed_entry(orig_children[i])[1]) for i in TOT_ENTRIES]
tof_entries = [(parse_typed_entry(orig_children[i])[0],
                parse_typed_entry(orig_children[i])[1]) for i in TOF_ENTRIES]

# --------------------------------------------------------------------------
# builders for generated blocks
# --------------------------------------------------------------------------
def build_caption_p(info):
    label = info["label"]
    p = mk(W("p"))
    children = [p_style("Caption")]
    if label == "Table":
        children.append(mk(W("keepNext")))
    else:
        children.append(jc("center"))
    set_pPr(p, children)
    add_bookmark(p, info["bm"], info["bid"])
    # place bookmarkStart/End correctly: add_bookmark inserts start at index 1
    # and appends end; insert runs before the end element.
    end = p[-1]
    p.remove(end)
    p.append(r_text(label + " "))
    for r in field_seq(label, info["seq"], info["chapter"]):
        p.append(r)
    p.append(r_text(info["title"]))
    p.append(end)
    return p


def build_toc_sdt():
    sdt = mk(W("sdt"))
    sdtPr = sub(sdt, W("sdtPr"))
    sub(sdtPr, W("id"), {W("val"): "-594399182"})
    dpo = sub(sdtPr, W("docPartObj"))
    sub(dpo, W("docPartGallery"), {W("val"): "Table of Contents"})
    sub(dpo, W("docPartUnique"))
    content = sub(sdt, W("sdtContent"))

    title = mk(W("p"))
    set_pPr(title, [spacing(line=360)])
    r = mk(W("r"))
    rp = sub(r, W("rPr"))
    sub(rp, W("b"))
    sub(rp, W("sz"), {W("val"): "32"})
    sub(rp, W("szCs"), {W("val"): "32"})
    sub(r, W("t"), text="Table of Contents")
    title.append(r)
    content.append(title)

    for n, h in enumerate(heading_info):
        p = mk(W("p"))
        set_pPr(p, [p_style("TOC%d" % h["level"]), tabs_right()])
        if n == 0:
            p.append(r_fld("begin", True))
            p.append(r_instr(' TOC \\o "1-3" \\h \\z \\u ', True))
            p.append(r_fld("separate", True))
        p.append(hyperlink_entry(h["text"], h["bm"], h["page"],
                                 style_prefix=h["prefix"]))
        content.append(p)

    endp = mk(W("p"))
    set_pPr(endp, [spacing(line=360)])
    endp.append(r_fld("end", True))
    content.append(endp)
    return sdt


def build_list_entry_p(label, page, anchor, first, last):
    p = mk(W("p"))
    set_pPr(p, [p_style("TableofFigures"), tabs_right()])
    if first:
        p.append(r_fld("begin", True))
        p.append(r_instr(' TOC \\h \\z \\c "Table" ' if anchor in [cap_info[k]["bm"] for k in tbl_order]
                         else ' TOC \\h \\z \\c "Figure" ', True))
        p.append(r_fld("separate", True))
    # keep the leading tab from the original lists
    p.append(r_tab())
    p.append(hyperlink_entry(label, anchor, page))
    if last:
        p.append(r_fld("end", True))
    return p


# --------------------------------------------------------------------------
# pass 2 - rebuild the body
# --------------------------------------------------------------------------
out_children = []
for i, el in enumerate(orig_children):
    if i == TOC_AT:
        out_children.append(build_toc_sdt())
        continue

    if el.tag != W("p"):
        out_children.append(el)
        continue

    p = el
    text = para_text(p)
    stripped = text.strip()

    # --- section break on this paragraph ---
    brk = SECTION_BREAKS.get(i)

    # --- headings ---
    if i in HINFO:
        h = HINFO[i]
        children = [p_style("Heading%d" % h["level"])]
        if h["unnum"]:
            children.append(numpr(0))
        children.append(spacing(line=360))
        if h["unnum"]:
            children.append(jc("center"))
        if brk is not None:
            children.append(copy.deepcopy(old_sects[brk]))
        set_pPr(p, children)
        add_bookmark(p, h["bm"], h["bid"])
        out_children.append(p)
        continue

    # --- live captions ---
    cap = (None if i in EXTRA_FIG_CAPTIONS else
           cap_info.get(("Figure", i)) or cap_info.get(("Table", i)))
    if cap is not None:
        cp = build_caption_p(cap)
        if brk is not None:
            cp.find(W("pPr")).append(copy.deepcopy(old_sects[brk]))
        out_children.append(cp)
        continue

    # --- table / figure list titles ---
    if i in (TOT_TITLE, TOF_TITLE):
        children = [tabs_right()]
        if i == TOF_TITLE:
            children.insert(0, p_style("TableofFigures"))
            children.append(spacing(after=240))
        if brk is not None:
            children.append(copy.deepcopy(old_sects[brk]))
        set_pPr(p, children)
        out_children.append(p)
        continue

    # --- typed list entries become generated-field results ---
    if i in TOT_ENTRIES:
        n = TOT_ENTRIES.index(i)
        label, page = tot_entries[n]
        anchor = cap_info[tbl_order[n]]["bm"]
        p2 = build_list_entry_p(label, page, anchor, n == 0, n == len(TOT_ENTRIES) - 1)
        if brk is not None:
            p2.find(W("pPr")).append(copy.deepcopy(old_sects[brk]))
        out_children.append(p2)
        continue
    if i in TOF_ENTRIES:
        n = TOF_ENTRIES.index(i)
        label, page = tof_entries[n]
        anchor = cap_info[fig_order[n]]["bm"]
        p2 = build_list_entry_p(label, page, anchor, n == 0, n == len(TOF_ENTRIES) - 1)
        if brk is not None:
            p2.find(W("pPr")).append(copy.deepcopy(old_sects[brk]))
        out_children.append(p2)
        continue

    # --- list paragraphs ---
    if i in lists:
        children = [p_style("ListParagraph"), numpr(5), spacing(line=360)]
        if brk is not None:
            children.append(copy.deepcopy(old_sects[brk]))
        set_pPr(p, children)
        out_children.append(p)
        continue

    # --- figure object paragraphs ---
    if i in objects:
        children = [mk(W("keepNext")), spacing(line=360), jc("center")]
        if brk is not None:
            children.append(copy.deepcopy(old_sects[brk]))
        set_pPr(p, children)
        out_children.append(p)
        if i in EXTRA_FIG_CAPTIONS:
            out_children.append(build_caption_p(cap_info[("Figure", i)]))
        continue

    # --- cover / title / ordinary body paragraphs ---
    keep_jc = None
    old_tabs = None
    pp = p.find(W("pPr"))
    if pp is not None:
        j = pp.find(W("jc"))
        if j is not None and j.get(W("val")) not in (None, "both"):
            keep_jc = j.get(W("val"))
        old_tabs = pp.find(W("tabs"))
    children = []
    if old_tabs is not None:
        children.append(copy.deepcopy(old_tabs))
    if keep_jc:
        children.append(jc(keep_jc))
    children.append(spacing(line=360))
    if brk is not None:
        children.append(copy.deepcopy(old_sects[brk]))
    set_pPr(p, children)
    out_children.append(p)


# final section
for c in list(new_body):
    new_body.remove(c)
for c in out_children:
    new_body.append(c)
new_body.append(copy.deepcopy(old_sects[5]))

# ensure namespace prefixes are declared on the root
ET.cleanup_namespaces(new_doc, top_nsmap=NSMAP, keep_ns_prefixes=list(NSMAP))

# --------------------------------------------------------------------------
# package assembly
# --------------------------------------------------------------------------
parts = {n: new_z.read(n) for n in new_z.namelist()}

# old formatting parts
for name in ["word/styles.xml", "word/numbering.xml", "word/settings.xml",
             "word/footer1.xml", "word/footer2.xml", "word/footer3.xml",
             "word/footer4.xml", "word/footnotes.xml", "word/endnotes.xml",
             "word/fontTable.xml", "word/theme/theme1.xml",
             "word/webSettings.xml"]:
    parts[name] = old_z.read(name)

# ask Word to refresh all fields on open
settings = ET.fromstring(parts["word/settings.xml"])
uf = mk(W("updateFields"), {W("val"): "true"})
for idx, child in enumerate(settings):
    if child.tag in (W("hdrShapeDefaults"), W("footnotePr"), W("endnotePr"), W("compat")):
        settings.insert(idx, uf)
        break
else:
    settings.append(uf)
parts["word/settings.xml"] = ET.tostring(settings, xml_declaration=True,
                                         encoding="UTF-8", standalone=True)

parts["word/document.xml"] = ET.tostring(new_doc, xml_declaration=True,
                                         encoding="UTF-8", standalone=True)

# relationship additions (styles + numbering already exist in the new package)
rels = ET.fromstring(parts["word/_rels/document.xml.rels"])
RELBASE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
extra = [
    ("fmtSettings", "settings", "settings.xml"),
    ("fmtFootnotes", "footnotes", "footnotes.xml"),
    ("fmtEndnotes", "endnotes", "endnotes.xml"),
    ("fmtFooter1", "footer", "footer1.xml"),
    ("fmtFooter2", "footer", "footer2.xml"),
    ("fmtFooter3", "footer", "footer3.xml"),
    ("fmtFooter4", "footer", "footer4.xml"),
    ("fmtFontTable", "fontTable", "fontTable.xml"),
    ("fmtTheme", "theme", "theme/theme1.xml"),
    ("fmtWebSettings", "webSettings", "webSettings.xml"),
]
existing = {r.get("Id") for r in rels}
for rid, typ, target in extra:
    if rid in existing:
        continue
    sub(rels, "{%s}Relationship" % NS_PKGREL,
        {"Id": rid, "Type": RELBASE + typ, "Target": target})
parts["word/_rels/document.xml.rels"] = ET.tostring(
    rels, xml_declaration=True, encoding="UTF-8", standalone=True)

# content types
ct = ET.Element("{%s}Types" % NS_CT, nsmap={None: NS_CT})
defaults = [
    ("rels", "application/vnd.openxmlformats-package.relationships+xml"),
    ("xml", "application/xml"),
    ("bin", "application/vnd.openxmlformats-officedocument.oleObject"),
    ("wmf", "image/x-wmf"),
    ("png", "image/png"),
    ("jpeg", "image/jpeg"),
    ("emf", "image/x-emf"),
]
for ext, ctype in defaults:
    sub(ct, "{%s}Default" % NS_CT, {"Extension": ext, "ContentType": ctype})
overrides = {
    "/word/document.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
    "/word/styles.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml",
    "/word/numbering.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml",
    "/word/settings.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml",
    "/word/footnotes.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml",
    "/word/endnotes.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml",
    "/word/fontTable.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml",
    "/word/theme/theme1.xml": "application/vnd.openxmlformats-officedocument.theme+xml",
    "/word/webSettings.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.webSettings+xml",
}
for i in range(1, 5):
    overrides["/word/footer%d.xml" % i] = \
        "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"
for part, ctype in overrides.items():
    sub(ct, "{%s}Override" % NS_CT, {"PartName": part, "ContentType": ctype})
parts["[Content_Types].xml"] = ET.tostring(ct, xml_declaration=True,
                                           encoding="UTF-8", standalone=True)

with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for name, data in parts.items():
        z.writestr(name, data)

print("wrote", OUT, OUT.stat().st_size, "bytes")
print("headings:", len(heading_info), "figure captions:", len(fig_order),
      "table captions:", len(tbl_order), "sections:", len(old_sects))
