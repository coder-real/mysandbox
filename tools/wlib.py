"""Low-level Office Open XML helpers for the schedule display report."""
import os
import zipfile
from xml.sax.saxutils import escape

import lxml.etree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
NS = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
NSM = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
       'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"')

BODY_BOOKMARK = "_body"


def frag(xml):
    return ET.fromstring(xml)


# --------------------------------------------------------------------------- inline runs
def run(text, bold=False, italic=False, size=None, mono=False, color=None, caps=False):
    props = []
    if mono:
        props.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/>')
    if bold:
        props.append("<w:b/><w:bCs/>")
    if italic:
        props.append("<w:i/><w:iCs/>")
    if caps:
        props.append("<w:caps/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if size:
        props.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


# --------------------------------------------------------------------------- blocks
def body(text, first_indent=True, jc="both", spacing=360, before=0, after=0):
    ind = '<w:ind w:firstLine="720"/>' if first_indent else ""
    return (f'<w:p {NS}><w:pPr><w:spacing w:before="{before}" w:after="{after}" '
            f'w:line="{spacing}" w:lineRule="auto"/>{ind}<w:jc w:val="{jc}"/></w:pPr>'
            f'{run(text)}</w:p>')


def body_runs(parts, first_indent=True, jc="both"):
    ind = '<w:ind w:firstLine="720"/>' if first_indent else ""
    inner = "".join(run(**p) if isinstance(p, dict) else run(p) for p in parts)
    return (f'<w:p {NS}><w:pPr><w:spacing w:line="360" w:lineRule="auto"/>{ind}'
            f'<jc w:val="{jc}"/></w:pPr>{inner}</w:p>').replace('<jc ', '<w:jc ').replace('</jc>', '</w:jc>')


def heading1(text, numbered=True):
    num = "" if numbered else '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr>'
    ind = '' if numbered else '<w:ind w:left="432" w:firstLine="0"/>'
    return (f'<w:p {NS}><w:pPr><w:pStyle w:val="Heading1"/>{num}{ind}'
            f'<w:spacing w:before="0" w:after="240"/><w:jc w:val="left"/>'
            f'<w:rPr><w:b/><w:bCs/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr></w:pPr>'
            f'{run(text, bold=True, size=28)}</w:p>')


def heading2(text):
    return (f'<w:p {NS}><w:pPr><w:pStyle w:val="Heading2"/><w:spacing w:before="320" w:after="160"/>'
            f'<w:jc w:val="both"/></w:pPr>{run(text, bold=True)}</w:p>')


def heading3(text):
    return (f'<w:p {NS}><w:pPr><w:pStyle w:val="Heading3"/><w:spacing w:before="240" w:after="120"/>'
            f'</w:pPr>{run(text, bold=True)}</w:p>')


def bullet(text, num_id="7"):
    return (f'<w:p {NS}><w:pPr><w:pStyle w:val="ListParagraph"/>'
            f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num_id}"/></w:numPr>'
            f'<w:spacing w:line="360" w:lineRule="auto"/><w:ind w:left="720" w:hanging="360"/>'
            f'<w:jc w:val="both"/></w:pPr>{run(text)}</w:p>')


def spacer():
    return (f'<w:p {NS}><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
            f'</w:pPr></w:p>')


def page_break():
    return (f'<w:p {NS}><w:r><w:br w:type="page"/></w:r></w:p>')


def equation(expr):
    return (f'<w:p {NSM}><w:pPr><w:spacing w:before="120" w:after="120" w:line="240" w:lineRule="auto"/>'
            f'<w:jc w:val="center"/></w:pPr><m:oMathPara><m:oMath><m:r>'
            f'<m:t xml:space="preserve">{escape(expr)}</m:t></m:r></m:oMath></m:oMathPara></w:p>')


def caption(kind, chapter, number, title):
    """Literal chapter.number caption, styled as a caption and entered in the field lists."""
    return (f'<w:p {NS}><w:pPr><w:pStyle w:val="Caption"/><w:keepNext/>'
            f'<w:spacing w:before="120" w:after="200" w:line="240" w:lineRule="auto"/>'
            f'<w:jc w:val="center"/><w:rPr><w:szCs w:val="18"/></w:rPr></w:pPr>'
            f'{run(f"{kind} {chapter}.{number}: {title}", bold=True, size=20)}</w:p>')


def figure(rid, docpr_id, cx, cy, name, descr):
    return (f'<w:p {NS} xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
            f'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
            f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            f'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<w:pPr><w:spacing w:before="120" w:after="60" w:line="240" w:lineRule="auto"/>'
            f'<w:jc w:val="center"/></w:pPr>'
            f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
            f'<wp:docPr id="{docpr_id}" name="{name}" descr="{escape(descr)}"/>'
            f'<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{docpr_id}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            f'</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')


def photo_box(lines, width=8640, height=2600):
    """A bordered placeholder box standing in for a photograph the authors must supply."""
    paras = "".join(
        f'<w:p {NS}><w:pPr><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
        f'<w:jc w:val="center"/></w:pPr>{run(t, italic=True, size=20, color="666666")}</w:p>'
        for t in lines)
    return (f'<w:tbl {NS}><w:tblPr><w:tblW w:w="{width}" w:type="dxa"/><w:jc w:val="center"/>'
            f'<w:tblBorders>'
            + "".join(f'<w:{s} w:val="dashed" w:sz="8" w:space="0" w:color="999999"/>'
                      for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
            + f'</w:tblBorders><w:tblCellMar><w:top w:w="120" w:type="dxa"/>'
              f'<w:bottom w:w="120" w:type="dxa"/></w:tblCellMar></w:tblPr>'
              f'<w:tblGrid><w:gridCol w:w="{width}"/></w:tblGrid>'
              f'<w:tr><w:trPr><w:trHeight w:val="{height}" w:hRule="atLeast"/></w:trPr>'
              f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/><w:vAlign w:val="center"/></w:tcPr>'
              f'{paras}</w:tc></w:tr></w:tbl>')


def table(rows, widths, header=True, font=18, align_center=True):
    total = sum(widths)
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    border = "".join(f'<w:{s} w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                     for s in ("top", "left", "bottom", "right", "insideH", "insideV"))
    out = [f'<w:tbl {NS}><w:tblPr><w:tblStyle w:val="TableGrid"/><w:tblW w:w="{total}" w:type="dxa"/>'
           f'<w:jc w:val="center"/><w:tblBorders>{border}</w:tblBorders>'
           f'<w:tblLayout w:type="fixed"/></w:tblPr><w:tblGrid>{grid}</w:tblGrid>']
    for i, row in enumerate(rows):
        head = header and i == 0
        out.append("<w:tr>")
        if head:
            out.append('<w:trPr><w:tblHeader/></w:trPr>')
        for j, cell in enumerate(row):
            jc = "center" if (head or align_center) else "left"
            bold = "<w:b/><w:bCs/>" if head else ""
            out.append(f'<w:tc><w:tcPr><w:tcW w:w="{widths[j]}" w:type="dxa"/>'
                       f'<w:vAlign w:val="center"/></w:tcPr>'
                       f'<w:p {NS}><w:pPr><w:spacing w:before="40" w:after="40" w:line="240" '
                       f'w:lineRule="auto"/><w:jc w:val="{jc}"/></w:pPr>'
                       f'<w:r><w:rPr>{bold}<w:sz w:val="{font}"/><w:szCs w:val="{font}"/></w:rPr>'
                       f'<w:t xml:space="preserve">{escape(str(cell))}</w:t></w:r></w:p></w:tc>')
        out.append("</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def field_block(instr, placeholder_lines, style=None):
    """A Word field whose cached result spans several paragraphs (contents and field lists)."""
    style_pr = f'<w:pStyle w:val="{style}"/><w:keepNext/>' if style else ""
    first = (f'<w:p {NS}><w:pPr>{style_pr}<w:spacing w:before="0" w:after="0" w:line="240" '
             f'w:lineRule="auto"/></w:pPr>'
             f'<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
             f'<w:r><w:instrText xml:space="preserve"> {instr} </w:instrText></w:r>'
             f'<w:r><w:fldChar w:fldCharType="separate"/></w:r></w:p>')
    middle = "".join(
        f'<w:p {NS}><w:pPr><w:pStyle w:val="TableofFigures"/><w:spacing w:before="0" w:after="0" '
        f'w:line="240" w:lineRule="auto"/></w:pPr>{run(t, size=20)}</w:p>' for t in placeholder_lines)
    last = (f'<w:p {NS}><w:pPr><w:pStyle w:val="TableofFigures"/><w:spacing w:before="0" w:after="0" '
            f'w:line="240" w:lineRule="auto"/></w:pPr>'
            f'<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')
    return first + middle + last


def code_line(text, size=15):
    return (f'<w:p {NS}><w:pPr><w:spacing w:before="0" w:after="0" w:line="200" w:lineRule="auto"/>'
            f'<w:ind w:left="0" w:firstLine="0"/><w:jc w:val="left"/></w:pPr>'
            f'{run(text.rstrip(chr(10)).replace(chr(9), "    "), mono=True, size=size)}</w:p>')


# --------------------------------------------------------------------------- package
def load_package(path):
    """Return the package as an ordered list of (name, bytes) so it can be rewritten byte for byte."""
    with zipfile.ZipFile(path) as z:
        return [(info.filename, z.read(info.filename)) for info in z.infolist()]


def write_package(parts, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts:
            z.writestr(name, data)


def image_size_px(path):
    from PIL import Image
    with Image.open(path) as im:
        return im.size


def emu_for(path, width_emu):
    w, h = image_size_px(path)
    return width_emu, int(width_emu * h / w)
