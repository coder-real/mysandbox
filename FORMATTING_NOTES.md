# Formatting rebuild — Fox's Car Safety System

**Deliverable:** `Fox's Car Safety System-33 (Reformatted).docx`
**Rebuild script:** `tools/rebuild_report_format.py` (re-runnable; reads the two source files, writes the deliverable)

## What was done

The content of `Fox's Car Safety System-33 (5).docx` (the new version) was kept, and the formatting architecture of `Fox's Car Safety System-2.docx` (the old version) was applied to it.

**From the old document (formatting only)**
- `styles.xml`, `numbering.xml`, `settings.xml`, `fontTable.xml`, `theme1.xml`, `webSettings.xml`, footnotes/endnotes and the four footer parts.
- Body: Times New Roman 12 pt, justified, 1.5 line spacing, 1-inch margins.
- Real Word styles: `Heading 1`, `Heading 2`, `Heading 3` with automatic multilevel numbering (1 / 1.1 / 1.1.1); H1 18 pt before, H2/H3 8 pt before; bold black.
- `DECLARATION`, `CERTIFICATION`, `DEDICATION`, `ACKNOWLEDGEMENT` and `REFERENCES` are unnumbered Heading 1s, as in the old file.
- `Caption`, `TOC1/2/3`, `TableofFigures` and `List Paragraph` styles.
- 6 section breaks copied from the old file: first two sections US Letter, rest A4; lowercase roman page numbers in the front matter, restart at 1 (decimal) on Chapter 1; centred `PAGE` fields in the footers.
- Live fields: a Table of Contents field (`TOC \o "1-3" \h \z \u`), generated table-of-tables (`TOC \h \z \c "Table"`) and table-of-figures (`TOC \h \z \c "Figure"`) fields, with hyperlinks and `PAGEREF` fields.
- Chapter-based captions built from `STYLEREF 1 \s` + `SEQ Figure/Table \* ARABIC \s 1`, so figures/tables number as 2.1, 2.2 … 3.1, 3.2 … and renumber automatically if chapters change.
- `w:updateFields` is enabled, so Word refreshes the fields on open.

**From the new document (content kept)**
- All revised text (including "Unit 1 Obstacle Detection System" and the revised LED and power sections).
- All 9 tables, unchanged.
- All 11 embedded figure images. They are OLE `StaticMetafile` (WMF) pictures sitting at the 11 figure positions in the new file — **not** equations. The old file's 13 images were therefore **not** imported; doing so would have duplicated the figures.
- All plain-text equations and external hyperlinks in the references.

## Two small structural additions

- The new file's own "Table of Figures" lists Figure 2.5 and Figure 2.6 (the two block diagrams), but those two captions were missing from the body. They were added as live captions using the titles from the new file's own list, so the generated figure list is complete.
- The fixed page numbers in the typed table/figure lists were converted into `PAGEREF` fields (keeping the original numbers as cached results).

## Before submission — one required step

Open the file in Microsoft Word. If Word asks to update fields, choose **Yes**; otherwise press **Ctrl+A** then **F9** and choose **Update entire table**. This recalculates the Table of Contents, the two generated lists, the caption numbers and the page numbers. The page numbers visible before that refresh are cached values inherited from the old document's TOC and from the new document's typed lists, so they must be refreshed after the new layout is paginated.

## Content points to check (not changed)

- The body caption for Figure 3.3 reads "Operational Flowchart of **Unit 2** — Parking Space Allocation System", while the new document's own figure list says "Figure 3.3 … **Unit 1** — Obstacle Detection System" and the paragraph above it describes Unit 1. This looks like a copy/paste error in the source; the text was left exactly as supplied.
- The new file's typed figure list contains "Obstacle DetectionSystem" (missing space) for Figure 3.1; it was preserved as typed and will be replaced by the caption text when Word regenerates the list.
- The buzzer illustration is captioned "Figure 2.5: Electronic (Sound) Buzzer" as a normal paragraph (not a live caption), exactly as in the old file, while the generated Figure 2.5 is the Unit 1 block diagram. This duplicate numbering also exists in the old version.

## Verification performed

The output opens cleanly with `python-docx`; all XML parts are well-formed; all relationship IDs, bookmarks and content types resolve; field begin/separate/end markers are balanced; 62 headings, 18 captions, 9 tables, 11 embedded images and 6 sections are present. This workspace has no Word/LibreOffice renderer, so pagination and the on-screen appearance could not be visually verified — the field refresh in Word is the final check.
