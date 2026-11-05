"""Build the corrected report: BLE iPixel panel, separate panel supply, Wi-Fi dashboard."""
import os
import re
import shutil
import sys
import zipfile

import lxml.etree as ET

import figures
import wlib
from wlib import (body, body_runs, bullet, caption, code_line, equation, field_block, figure, frag,
                  heading1, heading2, heading3, page_break, photo_box, run, spacer, table)
from ch13_a import chapter1, chapter2
from ch13_b import chapter3
from ch4 import chapter4
from ch5 import chapter5
from refs import APPENDIX_INTRO, REFERENCES

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/home/user/mysandbox"
SRC = os.path.join(REPO, "Approved Departmental Schedule display (Corrected).docx")
OUT = os.path.join(REPO, "Approved Departmental Schedule display (Corrected).docx")
SKETCH = os.path.join(REPO, "EEE_Campus.ino")
MEDIA = os.path.join(HERE, "pkg", "word", "media")

FIG_WIDTH = 5_900_000          # 6.45 inches, inside the 6.5 inch text column
FIG_WIDTH_PORTRAIT = 4_700_000
PHOTO_WIDTH = 5_400_000

W = wlib.W


def figure_specs():
    return {
        # chapter two photographs and chapter three drawings
        "photo_panel":   ("rId201", os.path.join(HERE, "figs", "panel.png"), 5.2, "panel"),
        "photo_esp32":   ("rId202", os.path.join(MEDIA, "image2.jpeg"), 3.0, "esp32"),
        "photo_pir":     ("rId203", os.path.join(MEDIA, "image3.png"), 2.6, "pir"),
        "photo_rtc":     ("rId204", os.path.join(MEDIA, "image4.jpeg"), 3.0, "rtc"),
        "photo_keypad":  ("rId205", os.path.join(MEDIA, "image5.jpeg"), 2.6, "keypad"),
        "fig3_3_block":  ("rId206", os.path.join(HERE, "fig3_1_block.png"), 6.4, "block diagram"),
        "fig3_1_circuit": ("rId207", os.path.join(HERE, "fig3_2_circuit.png"), 6.5, "circuit diagram"),
        "fig3_2_bleframe": ("rId208", os.path.join(HERE, "fig3_3_bleframe.png"), 6.3, "frame format"),
        "fig3_4_flowchart": ("rId209", os.path.join(HERE, "fig3_4_flowchart.png"), 4.9, "flowchart"),
        # chapter four photographs and screenshot
        "photo_breadboard": ("rId210", os.path.join(MEDIA, "image104.jpeg"), 5.2, "breadboard"),
        "photo_assembly":   ("rId211", os.path.join(MEDIA, "image105.jpeg"), 4.6, "assembly"),
        "photo_idle":       ("rId212", os.path.join(MEDIA, "image106.jpeg"), 4.6, "idle clock"),
        "photo_scroll":     ("rId213", None, 4.6, "scrolling message"),
        "fig4_6_dashboard": ("rId214", os.path.join(HERE, "fig4_6_dashboard.png"), 5.6, "dashboard"),
    }


class Report:
    def __init__(self):
        self.blocks = []
        self.assets = []
        self.chapter = 0
        self.counts = {}
        self.docpr = 900
        self.specs = figure_specs()

    # ---------------------------------------------------------------- helpers
    def h1(self, text, numbered=True):
        title = text.upper()
        for name in ("INTRODUCTION", "LITERATURE REVIEW", "CIRCUIT ANALYSIS AND DESIGN",
                     "CONSTRUCTION, TESTING", "SUMMARY, CONCLUSION"):
            if title.startswith(name):
                self.chapter += 1
                self.counts = {}
                break
        self.blocks.append(heading1(text, numbered=numbered))

    def h2(self, text):
        self.blocks.append(heading2(text))

    def h3(self, text):
        self.blocks.append(heading3(text))

    def p(self, text, first_indent=True):
        self.blocks.append(body(text, first_indent=first_indent))

    def eq(self, expr):
        self.blocks.append(equation(expr))

    def bullet(self, text):
        self.blocks.append(bullet(text))

    def spacer(self):
        self.blocks.append(spacer())

    def _num(self, kind):
        self.counts[kind] = self.counts.get(kind, 0) + 1
        return self.counts[kind]

    def table(self, title, rows, widths, font=17):
        n = self._num("Table")
        self.blocks.append(caption("Table", self.chapter, n, title))
        self.blocks.append(table(rows, widths, font=font))
        self.blocks.append(spacer())

    def figure(self, key, title, width_inches, descr):
        rid, path, _w, _n = self.specs[key]
        n = self._num("Figure")
        if path is None:
            self.blocks.append(photo_box([
                "",
                "[ Insert photograph here ]",
                "",
            ]))
        else:
            emu = int(width_inches * 914400)
            cx, cy = wlib.emu_for(path, emu)
            self.docpr += 1
            self.blocks.append(figure(rid, self.docpr, cx, cy, f"Picture {self.docpr}", descr))
            self.assets.append((rid, path))
        self.blocks.append(caption("Figure", self.chapter, n, title))

    def code(self, lines):
        for line in lines:
            self.blocks.append(code_line(line))

    def xml(self, fragment):
        self.blocks.append(fragment)


# ---------------------------------------------------------------------------- dashboard picture
def make_dashboard(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle

    plt.rcParams["font.family"] = "DejaVu Sans"
    fig, ax = plt.subplots(figsize=(8.6, 6.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 72)
    ax.axis("off")

    ax.add_patch(Rectangle((0, 0), 100, 72, facecolor="#f4f6f8", edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((0, 64), 100, 8, facecolor="#1f4e79", edgecolor="none", zorder=1))
    ax.text(3, 68, "EEE Campus Display", color="white", fontsize=12, fontweight="bold", va="center")
    ax.text(97, 68, "192.168.4.1", color="#cfe0f0", fontsize=9, ha="right", va="center")

    cards = [
        (4, 44, 44, 16, "Upload timetable", ["Choose file  eee_timetable.json", "", "[ Browse ]   [ Upload and validate ]",
                                             "Status: validated and saved"]),
        (52, 44, 44, 16, "Clock", ["Current time  HH:MM:SS", "Day            Monday", "",
                                   "[ Set clock from this browser ]"]),
        (4, 24, 44, 16, "Preview a level", ["Level  100L 200L 300L 400L 500L", "Day    automatic",
                                            "[ Show on the panel ]", "Scrolling speed  58 px/s  [ Calibrate ]"]),
        (52, 24, 44, 16, "System status", ["BLE link      connected", "AP clients    1",
                                           "Free heap     142 kB", "Last reset    power-on"]),
    ]
    for x, y, w, h, title, lines in cards:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2",
                                    facecolor="white", edgecolor="#c3ccd6", lw=1.0, zorder=2))
        ax.text(x + 2, y + h - 2.6, title, fontsize=9.5, fontweight="bold", color="#1f4e79", va="center")
        for i, line in enumerate(lines):
            ax.text(x + 2, y + h - 6.4 - i * 2.5, line, fontsize=8.0, color="#333333", va="center")

    ax.add_patch(FancyBboxPatch((4, 4), 92, 14, boxstyle="round,pad=0.3,rounding_size=1.2",
                                facecolor="#eef4ea", edgecolor="#9dbfa8", lw=1.0, zorder=2))
    ax.text(6, 14.6, "Network", fontsize=9.5, fontweight="bold", color="#1e6b3a", va="center")
    ax.text(6, 10.4, "Access point   CampusDisplay-Offline    192.168.4.1    channel 6", fontsize=8.2,
            color="#333333", va="center")
    ax.text(6, 7.2, "Departmental router   not configured   (optional; supplies network time only)",
            fontsize=8.2, color="#333333", va="center")

    fig.savefig(path, dpi=200, bbox_inches="tight", pad_inches=0.05, facecolor="white")
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------------------- front matter
def front_matter():
    """Cover, declaration, certification, dedication, acknowledgement, and the field lists."""
    out = []

    def centred(text, size=24, bold=False, space_before=0, space_after=0):
        return (f'<w:p {wlib.NS}><w:pPr><w:spacing w:before="{space_before}" w:after="{space_after}" '
                f'w:line="276" w:lineRule="auto"/><w:jc w:val="center"/></w:pPr>'
                f'{run(text, bold=bold, size=size)}</w:p>')

    def blank(n=1, size=24):
        return "".join(centred("", size=size) for _ in range(n))

    out.append(centred("DESIGN AND IMPLEMENTATION OF A MOTION-ACTIVATED REAL-TIME INTERACTIVE LED "
                       "DEPARTMENTAL SCHEDULE DISPLAY", size=28, bold=True, space_before=720))
    out.append(blank(3))
    out.append(centred("BY", size=24))
    out.append(blank(2))
    out.append(centred("ATAYI WISDOM", size=26, bold=True))
    out.append(centred("21/58437/UE", size=24))
    out.append(centred("&", size=24))
    out.append(centred("DEMKAA A. JOSHUA", size=26, bold=True))
    out.append(centred("21/58439/UE", size=24))
    out.append(blank(3))
    out.append(centred("DEPARTMENT OF ELECTRICAL AND ELECTRONICS ENGINEERING,", size=22))
    out.append(centred("JOSEPH SARWUAN TARKA UNIVERSITY, MAKURDI.", size=22))
    out.append(blank(2))
    out.append(centred("NOVEMBER, 2026", size=22))
    out.append(page_break())

    out.append(centred("DESIGN AND IMPLEMENTATION OF A MOTION-ACTIVATED REAL-TIME INTERACTIVE LED "
                       "DEPARTMENTAL SCHEDULE DISPLAY", size=26, bold=True, space_before=480))
    out.append(blank(2))
    out.append(centred("BY", size=22))
    out.append(blank(1))
    out.append(centred("ATAYI WISDOM          21/58437/UE", size=22))
    out.append(centred("DEMKAA A. JOSHUA      21/58439/UE", size=22))
    out.append(blank(2))
    out.append(body("A project report submitted to the Department of Electrical and Electronics Engineering, "
                    "Joseph Sarwuan Tarka University, Makurdi, in partial fulfilment of the requirements for "
                    "the award of the degree of Bachelor of Engineering (B.Eng.) in Electrical and Electronics "
                    "Engineering.", first_indent=False))
    out.append(blank(2))
    out.append(centred("NOVEMBER, 2026", size=22))
    out.append(page_break())

    out.append(heading1("DECLARATION", numbered=False))
    out.append(body("We declare that the work described in this report is original, and has not been submitted "
                    "previously to any university or similar institution for the award of any degree or "
                    "certificate.", first_indent=False))
    out.append(spacer())
    for name, reg in (("ATAYI WISDOM", "21/58437/UE"), ("DEMKAA A. JOSHUA", "21/58439/UE")):
        out.append(body(f"Name of candidate: {name}", first_indent=False))
        out.append(body(f"Registration number: {reg}", first_indent=False))
        out.append(body("Signature: ……………………………………………………   Date: …………………………", first_indent=False))
        out.append(spacer())
    out.append(page_break())

    out.append(heading1("CERTIFICATION", numbered=False))
    out.append(body("We, the undersigned, certify that this project report, presented by ATAYI WISDOM "
                    "(21/58437/UE) and DEMKAA A. JOSHUA (21/58439/UE), is accepted as fulfilling part of the "
                    "requirements for the award of the degree of Bachelor of Engineering in Electrical and "
                    "Electronics Engineering.", first_indent=False))
    out.append(spacer())
    for role in ("Project Supervisor", "Project Coordinator", "Head of Department"):
        out.append(body(f"{role}: ……………………………………………………", first_indent=False))
        out.append(body("Signature / Date: ……………………………………………………", first_indent=False))
        out.append(spacer())
    out.append(page_break())

    out.append(heading1("DEDICATION", numbered=False))
    out.append(body("This work is dedicated to the Almighty God, for His mercies every day and for sustaining us "
                    "through this project, and to our families, whose patience and support made it possible.",
                    first_indent=False))
    out.append(page_break())

    out.append(heading1("ACKNOWLEDGEMENT", numbered=False))
    for para in (
        "We return all honour and glory to God Almighty, whose hand has kept us through a process that seemed "
        "impossible at the start.",
        "We express our heartfelt gratitude to our project supervisor, Engr. A. S. Iannah, for his commitment, "
        "his professional guidance and his constructive criticism throughout the research and the "
        "implementation. His technical depth and his insistence on evidence moulded this work and brought it to "
        "its present standard.",
        "Our sincere appreciation goes to the Department of Electrical and Electronics Engineering, Joseph "
        "Sarwuan Tarka University, Makurdi, for the environment and the resources that supported the work, and "
        "to our lecturers and the departmental staff for their mentorship.",
        "We thank our colleagues and friends whose suggestions and assistance enriched the design, and above "
        "all our families, whose moral support and belief in us remained a source of strength throughout.",
    ):
        out.append(body(para, first_indent=False))
    out.append(page_break())

    out.append(heading1("TABLE OF CONTENTS", numbered=False))
    out.append(field_block('TOC \\o "1-3" \\h \\z \\u', [
        "Right-click here and choose Update Field to build the contents list",
        "Headings 1 to 3 are collected, with page numbers",
    ]))
    out.append(page_break())

    out.append(heading1("LIST OF FIGURES", numbered=False))
    out.append(field_block('TOC \\h \\z \\c "Figure"', [
        "Right-click here and choose Update Field to build the list of figures",
        "Every Figure caption in the document is collected",
    ]))
    out.append(spacer())
    out.append(heading1("LIST OF TABLES", numbered=False))
    out.append(field_block('TOC \\h \\z \\c "Table"', [
        "Right-click here and choose Update Field to build the list of tables",
        "Every Table caption in the document is collected",
    ]))
    out.append(page_break())

    out.append(heading1("LIST OF ABBREVIATIONS AND SYMBOLS", numbered=False))
    out.append(table([
        ["Abbreviation", "Meaning"],
        ["AP", "Access point"],
        ["BLE", "Bluetooth Low Energy"],
        ["CRC", "Cyclic redundancy check"],
        ["DS3231", "Temperature-compensated real-time clock"],
        ["ESP32", "Espressif dual-core microcontroller with Wi-Fi and Bluetooth"],
        ["GATT", "Generic Attribute Profile"],
        ["GPIO", "General-purpose input/output"],
        ["I²C", "Inter-integrated circuit bus"],
        ["JSON", "JavaScript Object Notation"],
        ["Li-ion", "Lithium-ion"],
        ["MTU", "Maximum transmission unit"],
        ["PIR", "Passive infrared"],
        ["RTC", "Real-time clock"],
        ["UUID", "Universally unique identifier"],
        ["WAT", "West Africa Time (UTC+1)"],
    ], [2000, 6700], font=17))
    out.append(page_break())

    out.append(heading1("ABSTRACT", numbered=False))
    out.append(body("This report presents the design and construction of a motion-activated, real-time "
                    "interactive LED departmental schedule display for the Department of Electrical and "
                    "Electronics Engineering, Joseph Sarwuan Tarka University, Makurdi. Timetables in the "
                    "department are published on printed paper, which fades, tears, cannot be corrected "
                    "without a reprint and cannot be filtered to a student's own level. The system described "
                    "here replaces that sheet with a 64 × 20 iPixel Bluetooth Low Energy LED matrix driven by "
                    "an ESP32 microcontroller over a Bluetooth GATT link, with no conductor between the "
                    "controller and the panel. An HC-SR501 passive infrared sensor starts a session only when "
                    "somebody is present, a DS3231 real-time clock supplies the time and day from which the "
                    "greeting and the timetable entry are chosen, and a 4 × 4 keypad lets the student select "
                    "an academic level, confirmed with # and cleared with *. The same ESP32 publishes its own "
                    "Wi-Fi access point, on which a departmental administrator uploads a validated JSON "
                    "timetable, sets the clock, previews any level and reads the state of the system, without "
                    "any internet connection and without touching the unit. The controller is powered through "
                    "a 2-in-1 lithium-ion charge and discharge module with a 4 000 mAh cell, which changes "
                    "over without a relay, while the panel is powered from a separate 5 V, 2 A supply because "
                    "it draws about six times the current of the controller. The completed unit detects a "
                    "person at the distances required of a corridor, greets according to the hour, displays "
                    "the classes of the selected level and day in a single scroll, returns to a stationary "
                    "clock, and continues to operate while the mains supply is interrupted. The limitations "
                    "of the approach — the font and single colour imposed by the panel controller, a "
                    "280-character message limit, and the sharing of the 2.4 GHz band between Bluetooth and "
                    "Wi-Fi — are stated, and recommendations for their removal are given.",
                    first_indent=False))
    out.append(page_break())
    return out


# ---------------------------------------------------------------------------- appendix
def appendix():
    out = [heading1("APPENDIX A: COMPLETE PROGRAM LISTING")]
    for para in APPENDIX_INTRO:
        out.append(body(para, first_indent=False))
    out.append(spacer())
    with open(SKETCH, encoding="utf8", errors="replace") as f:
        lines = f.read().split("\n")
    out.extend(code_line(line) for line in lines)
    return out


def references_block():
    out = [heading1("REFERENCES")]
    for entry in REFERENCES:
        out.append(f'<w:p {wlib.NS}><w:pPr><w:spacing w:before="0" w:after="120" w:line="360" '
                   f'w:lineRule="auto"/><w:ind w:left="567" w:hanging="567"/><w:jc w:val="left"/></w:pPr>'
                   f'{run(entry)}</w:p>')
    out.append(page_break())
    return out


# ---------------------------------------------------------------------------- assembly
def build():
    os.makedirs(os.path.join(HERE, "figs"), exist_ok=True)
    keep = os.path.join(REPO, "originals", "previous_build.docx")
    if not os.path.exists(keep) and os.path.exists(SRC):
        os.makedirs(os.path.dirname(keep), exist_ok=True)
        shutil.copy2(SRC, keep)
        print("backed up the previous build to", keep)
    make_dashboard(os.path.join(HERE, "fig4_6_dashboard.png"))

    r = Report()
    blocks = front_matter()
    for chapter in (chapter1, chapter2, chapter3, chapter4, chapter5):
        chapter(r)
        blocks.extend(r.blocks)
        r.blocks = []
        blocks.append(page_break())
    blocks.extend(references_block())
    blocks.extend(appendix())
    for name in ("photo_panel", "photo_esp32", "photo_pir", "photo_rtc", "photo_keypad",
                 "fig3_3_block", "fig3_1_circuit", "fig3_2_bleframe", "fig3_4_flowchart",
                 "photo_breadboard", "photo_assembly", "photo_idle", "fig4_6_dashboard"):
        rid, path, _w, _n = r.specs[name]
        if path and all(rid != a[0] for a in r.assets):
            r.assets.append((rid, path))

    # ---- package write
    parts = wlib.load_package(SRC)
    names = [n for n, _ in parts]
    doc_xml = ("<w:document " + wlib.NSM +
               ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
               'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
               'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
               'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
               'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml">'
               "<w:body>" + "".join(blocks) +
               '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
               '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
               'w:header="720" w:footer="720" w:gutter="0"/>'
               '<w:pgNumType w:fmt="decimal"/>'
               '<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>'
               "</w:body></w:document>")

    rels = [n for n, d in parts if n == "word/_rels/document.xml.rels"][0]
    rel_xml = [d.decode() for n, d in parts if n == rels][0]
    rel_xml = re.sub(r"<Relationship [^>]*/>", "", rel_xml)
    new_rels = ['<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/styles" Target="styles.xml"/>',
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/settings" Target="settings.xml"/>',
                '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/numbering" Target="numbering.xml"/>',
                '<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/fontTable" Target="fontTable.xml"/>',
                '<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/theme" Target="theme/theme1.xml"/>',
                '<Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                'relationships/webSettings" Target="webSettings.xml"/>']
    for rid, path in r.assets:
        ext = os.path.splitext(path)[1].lstrip(".").lower()
        ext = "jpeg" if ext in ("jpg", "jpeg") else ext
        target = f"media/{rid}.{ext}"
        new_rels.append(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/'
                        f'2006/relationships/image" Target="{target}"/>')
    rel_xml = rel_xml.replace("</Relationships>", "".join(new_rels) + "</Relationships>")

    out_parts = []
    for name, data in parts:
        if name == "word/document.xml":
            out_parts.append((name, doc_xml.encode("utf8")))
        elif name == rels:
            out_parts.append((name, rel_xml.encode("utf8")))
        elif name.startswith("word/media/"):
            continue
        else:
            out_parts.append((name, data))
    for rid, path in r.assets:
        ext = os.path.splitext(path)[1].lstrip(".").lower()
        ext = "jpeg" if ext in ("jpg", "jpeg") else ext
        with open(path, "rb") as f:
            out_parts.append((f"word/media/{rid}.{ext}", f.read()))

    # make Word recompute the field lists when the document is opened
    idx = [i for i, (n, _) in enumerate(out_parts) if n == "word/settings.xml"][0]
    settings = out_parts[idx][1].decode("utf8")
    if "updateFields" not in settings:
        settings = settings.replace("<w:defaultTabStop", '<w:updateFields w:val="true"/><w:defaultTabStop', 1)
    out_parts[idx] = ("word/settings.xml", settings.encode("utf8"))

    wlib.write_package(out_parts, OUT)
    print("written", OUT, os.path.getsize(OUT))
    return r


if __name__ == "__main__":
    figures.block_diagram()
    figures.circuit_diagram()
    figures.ble_frame()
    figures.flowchart()
    build()
