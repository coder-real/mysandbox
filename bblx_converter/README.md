# Scrollmapper SQL to e-Sword BBLX converter

This Python script downloads the translation SQL dumps from the Scrollmapper GitHub repository, builds one SQLite `.bblx` per translation, and optionally makes a ZIP. It also downloads each translation's original OSIS JSON as a compressed sidecar so that annotations in that source are retained.

**Important: this is not yet a complete conversion of everything into e-Sword.**

- The repository's SQL dumps contain plain verse text. Strong's numbers, morphology, notes and formatting in the separate OSIS sources are **not rendered or interactive in the BBLX**. They are preserved in `source_osis/*.osis.json.gz` for future processing. The SQL export can also differ from the OSIS source due to upstream text normalization.
- Only books in the standard 66-book canon are mapped to e-Sword book numbers. The script stores Apocrypha and other unrecognized book verses, as well as duplicate or zero chapter/verse references, in an extra `UnmappedVerses` table in the same BBLX. **e-Sword will not normally display those rows.** Counts and names appear in the report. It does not guess extra book numbers.
- Source chapter and verse numbers are preserved, not converted between versification systems. Some references may not display correctly in e-Sword. Partial translations remain partial.
- Compatibility, HTML rendering, and right-to-left behavior must be tested in your particular e-Sword version. A database integrity check does not replace that test.
- The repository's separate cross-reference datasets are not converted to Bible modules or included in the output.
- Translation licences differ. Check `conversion-report.json` and upstream licences before redistributing.

## What you need

- Python **3.9 or newer** (https://www.python.org/downloads/). On Windows, select “Add Python to PATH” during installation.
- Internet access to `api.github.com` and `raw.githubusercontent.com`.
- Several gigabytes of free disk space and a stable connection. At the pinned revision the SQL exports total roughly 1 GB and OSIS files roughly 2 GB to download. The final archive and the output folder are both kept, so they require additional space. Actual sizes vary.
- No third-party Python packages or MySQL installation are needed. The script parses the expected SQL inserts; it does not execute downloaded SQL.

## Run

Open a terminal in this folder. On Windows PowerShell or Command Prompt:

```powershell
py -3 convert_bibles.py --zip
```

On macOS or Linux:

```sh
python3 convert_bibles.py --zip
```

The script creates a new `bblx_output` folder and `bblx_output.zip` in the current directory. The ZIP contains:

- `modules/`: generated `.bblx` files.
- `source_osis/`: the original OSIS JSON files, individually compressed with gzip; these are not e-Sword modules.
- `conversion-report.json`: results, licences, unmapped counts and download/conversion errors.
- `README.txt`: a summary of limitations.

To test just two translations first:

```sh
python3 convert_bibles.py --translations KJVPCE KJVA --output test_bibles --zip
```

On Windows replace `python3` with `py -3`. Use `--output` to choose another folder; the ZIP is created beside that folder with the same name and a `.zip` extension. Existing output folders or ZIPs are not overwritten. To retry failed translations, use their names from the report with `--translations` and choose a new `--output` folder.

The script returns a nonzero exit status if a translation failed or any verses could not be mapped, even though it still writes completed modules, a report and, when requested, a ZIP. A successful exit does **not** mean annotations were converted or that e-Sword compatibility was tested.

### Connection problems

The script retries interrupted catalogue and source-file downloads up to three times. It checks the catalogue response length when provided and checks source-file lengths against the pinned GitHub catalogue. If it still fails with an `IncompleteRead` or connection error, check your internet connection and rerun. A failure while reading the catalogue happens before the output folder is created, so you can run the same command again. If the output folder or ZIP already exists, use a new `--output` name; consult `conversion-report.json` for any translations that need retrying.

The source revision is pinned to `59b18c5af5845728c275d5b7178ad0d024172b1f` for reproducibility; the catalogue contained 140 translations at that revision. Later upstream additions are not automatically included. Original project: https://github.com/scrollmapper/bible_databases

## Install and test

Extract the ZIP, then copy selected `.bblx` files from `modules/` to your e-Sword Bible modules folder and restart e-Sword. Test at least a few expected references in each translation, including an Old Testament verse, a New Testament verse, non-Latin text and any special versification. Keep the report and OSIS files for review.

## Tests for developers

```sh
python3 -m unittest discover -s . -v
```
