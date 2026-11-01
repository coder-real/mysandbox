#!/usr/bin/env python3
"""Download Scrollmapper MySQL dumps and create e-Sword-style SQLite modules.

Uses only the Python standard library. See README.md for important limitations.
"""
import argparse
import gzip
import html
import io
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

REVISION = '59b18c5af5845728c275d5b7178ad0d024172b1f'
ROOT = 'https://raw.githubusercontent.com/scrollmapper/bible_databases/'
TREE = 'https://api.github.com/repos/scrollmapper/bible_databases/git/trees/'
BOOKS = ('Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|I Samuel|II Samuel|I Kings|II Kings|I Chronicles|II Chronicles|Ezra|Nehemiah|Esther|Job|Psalms|Proverbs|Ecclesiastes|Song of Solomon|Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|John|Acts|Romans|I Corinthians|II Corinthians|Galatians|Ephesians|Philippians|Colossians|I Thessalonians|II Thessalonians|I Timothy|II Timothy|Titus|Philemon|Hebrews|James|I Peter|II Peter|I John|II John|III John|Jude|Revelation of John').split('|')
CANON = {name: n for n, name in enumerate(BOOKS, 1)}
# The dump is MySQL, not SQLite. Parse its narrowly specified INSERT statements;
# never execute remote SQL. PyMySQL's escape_string emits backslash escapes.
QUOTED = r"'((?:[^'\\]|\\.)*)'"
BOOK_RE = re.compile(r'^INSERT INTO `([^`]+)_books` \(`name`\) VALUES \(' + QUOTED + r'\);$')
VERSE_RE = re.compile(r'^INSERT INTO `([^`]+)_verses` \(`book_id`, `chapter`, `verse`, `text`\) VALUES \((\d+), (\d+), (\d+), ' + QUOTED + r'\);$')
ESCAPES = {'0': '\0', 'b': '\b', 'n': '\n', 'r': '\r', 't': '\t', 'Z': '\x1a', '\\': '\\', "'": "'", '"': '"'}
RTL_LANGUAGES = {'ar', 'he', 'hbo', 'fa', 'ur', 'syr', 'arc', 'ps'}


def mysql_unescape(value):
    def replacement(match):
        char = match.group(1)
        if char not in ESCAPES:
            raise ValueError('Unsupported MySQL escape: \\' + char)
        return ESCAPES[char]
    return re.sub(r'\\(.)', replacement, value, flags=re.DOTALL)


def open_url(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'scrollmapper-bblx-converter/1.0', 'Accept': 'application/vnd.github+json'})
    for attempt in range(4):
        try:
            return urllib.request.urlopen(request, timeout=120)
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == 3:
                raise RuntimeError(f'Cannot download {url}: {exc}') from exc
            time.sleep(2 ** attempt)


def download(url, path):
    with open_url(url) as response, open(path, 'wb') as out:
        shutil.copyfileobj(response, out, length=1024 * 1024)


def catalogue(revision):
    with open_url(TREE + revision + '?recursive=1') as response:
        tree = json.load(response)
    if tree.get('truncated'):
        raise RuntimeError('GitHub returned an incomplete tree; cannot safely enumerate translations')
    paths = [item['path'] for item in tree['tree'] if item['type'] == 'blob']
    sql = {p.rsplit('/', 1)[1][:-4]: p for p in paths
           if re.fullmatch(r'formats/sql/[A-Za-z0-9_-]+\.sql', p)
           and not p.rsplit('/', 1)[1].startswith('cross_references_')}
    osis = {}
    for path in paths:
        match = re.fullmatch(r'sources/([^/]+)/([^/]+)/([^/]+)-osis\.json', path)
        if match and match.group(2) == match.group(3):
            if match.group(2) in osis:
                raise RuntimeError('Ambiguous OSIS source for ' + match.group(2))
            osis[match.group(2)] = (match.group(1), path)
    if not sql:
        raise RuntimeError('No translation SQL files found in source tree')
    return sql, osis


def convert_sql(sql_path, output_path, name, language=''):
    books = []
    rows = 0
    unmapped = 0
    invalid = 0
    empty_verses = 0
    actual_books = set()
    title = name
    license_text = 'Unknown'
    seen = set()
    counts = {}
    db = sqlite3.connect(output_path)
    try:
        db.executescript('''CREATE TABLE Details (Description NVARCHAR(250), Abbreviation NVARCHAR(50), Information TEXT, Version INT, Font NVARCHAR(50), RightToLeft BOOL, OT BOOL, NT BOOL, Apocrypha BOOL, Strong BOOL);
CREATE TABLE Bible (Book INT, Chapter INT, Verse INT, Scripture TEXT);
CREATE INDEX BookChapterVerseIndex ON Bible (Book, Chapter, Verse);
CREATE TABLE SourceBooks (SourceBook INT PRIMARY KEY, Name TEXT NOT NULL, MappedBook INT);
CREATE TABLE UnmappedVerses (SourceBook INT, BookName TEXT, Chapter INT, Verse INT, Scripture TEXT, Reason TEXT);''')
        with open(sql_path, encoding='utf-8', newline='') as source:
            for line_no, line in enumerate(source, 1):
                line = line.rstrip('\r\n')
                if line_no == 1 and line.startswith('-- SQL Dump for '):
                    title = line[len('-- SQL Dump for '):].removeprefix('# ').removesuffix(' (' + name + ')')
                elif line.startswith('-- License: '):
                    license_text = line[len('-- License: '):]
                elif line.startswith('INSERT INTO `' + name + '_books`'):
                    m = BOOK_RE.fullmatch(line)
                    if not m or m.group(1) != name:
                        raise ValueError(f'Unrecognized book INSERT at line {line_no}')
                    book = mysql_unescape(m.group(2))
                    books.append(book)
                    db.execute('INSERT INTO SourceBooks VALUES (?,?,?)', (len(books), book, CANON.get(book)))
                elif line.startswith('INSERT INTO `' + name + '_verses`'):
                    m = VERSE_RE.fullmatch(line)
                    if not m or m.group(1) != name:
                        raise ValueError(f'Unrecognized verse INSERT at line {line_no}')
                    source_id, chapter, verse = map(int, m.group(2, 3, 4))
                    if source_id < 1 or source_id > len(books):
                        raise ValueError(f'Unknown book ID {source_id} at line {line_no}')
                    book_name = books[source_id-1]
                    text = mysql_unescape(m.group(5))
                    if not text.strip():
                        empty_verses += 1
                    target = CANON.get(book_name)
                    key = (target, chapter, verse)
                    if target is None:
                        reason = 'Unmapped book'
                    elif chapter < 1 or verse < 1:
                        reason = 'Non-positive chapter or verse'
                    elif key in seen:
                        reason = 'Duplicate reference'
                    else:
                        reason = None
                    if reason:
                        db.execute('INSERT INTO UnmappedVerses VALUES (?,?,?,?,?,?)', (source_id, book_name, chapter, verse, text, reason))
                        counts[book_name + ' — ' + reason] = counts.get(book_name + ' — ' + reason, 0) + 1
                        unmapped += 1
                        if target is not None:
                            invalid += 1
                    else:
                        # Version 4 Scripture is HTML; quote=False keeps apostrophes readable.
                        db.execute('INSERT INTO Bible VALUES (?,?,?,?)', (target, chapter, verse, html.escape(text, quote=False)))
                        seen.add(key)
                        if text.strip():
                            actual_books.add(target)
                    rows += 1
                elif line.startswith('INSERT INTO `') and ('_books`' in line or '_verses`' in line):
                    raise ValueError(f'Unexpected translation INSERT at line {line_no}')
        if not books or not rows:
            raise ValueError('No books or verses parsed from SQL dump')
        info = (f'Source: scrollmapper/bible_databases, revision {REVISION}; license: {license_text}. '
                'Text is from the SQL export; OSIS annotations are provided separately, not rendered here. '
                f'{unmapped} unmapped/unsupported verse rows are stored in UnmappedVerses, not visible in e-Sword.')
        db.execute('INSERT INTO Details VALUES (?,?,?,?,?,?,?,?,?,?)', (title[:250], name[:50], info, 4, 'DEFAULT', int(language in RTL_LANGUAGES), int(any(b <= 39 for b in actual_books)), int(any(40 <= b <= 66 for b in actual_books)), 0, 0))
        db.commit()
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('SQLite integrity check failed')
        if db.execute('SELECT COUNT(*) FROM Bible').fetchone()[0] + db.execute('SELECT COUNT(*) FROM UnmappedVerses').fetchone()[0] != rows:
            raise ValueError('Verse count verification failed')
    finally:
        db.close()
    return {'translation': name, 'title': title, 'license': license_text, 'source_verses': rows,
            'module_verses': rows-unmapped, 'unmapped_verses': unmapped, 'unmapped_details': counts,
            'invalid_or_duplicate_verses': invalid, 'empty_verses': empty_verses, 'source_books': len(books)}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='bblx_output', help='output directory (default: bblx_output)')
    parser.add_argument('--translations', nargs='+', help='abbreviations to process, e.g. KJVPCE KJVA; default is all')
    parser.add_argument('--zip', action='store_true', help='also create bblx_output.zip beside the output folder')
    return parser.parse_args()


def main():
    args = parse_args()
    output = Path(args.output).resolve()
    archive = Path(str(output) + '.zip')
    # Never overwrite a prior run or an unrelated ZIP.
    if output.exists() or (args.zip and archive.exists()):
        raise RuntimeError('Output directory or requested ZIP already exists. Choose a new --output path.')
    print('Reading GitHub catalogue...', flush=True)
    sql, osis = catalogue(REVISION)
    requested = args.translations or sorted(sql)
    if len(set(requested)) != len(requested):
        raise ValueError('Duplicate translation abbreviation requested')
    missing = sorted(set(requested) - sql.keys())
    if missing:
        raise ValueError('Translation(s) not found: ' + ', '.join(missing))
    output.mkdir(parents=True)
    (output / 'modules').mkdir()
    (output / 'source_osis').mkdir()
    report = {'source_revision': REVISION, 'results': [], 'errors': [], 'limitations': [
        'SQL is plain text; OSIS annotations are retained separately and are not displayed by these modules.',
        'Books outside the 66-book mapping and unsupported references are retained in UnmappedVerses, not displayed by e-Sword.',
        'Neither e-Sword compatibility nor translation-specific versification has been verified.']}
    report_path = output / 'conversion-report.json'
    def save_report():
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    save_report()
    with tempfile.TemporaryDirectory(prefix='bblx-convert-') as tmp:
        for index, name in enumerate(requested, 1):
            print(f'[{index}/{len(requested)}] {name}', flush=True)
            module = output / 'modules' / (name + '.bblx')
            sidecar = output / 'source_osis' / (name + '.osis.json.gz')
            try:
                if name not in osis:
                    raise ValueError('No OSIS source found; refusing to omit annotations')
                lang, osis_path = osis[name]
                local_sql = Path(tmp) / 'source.sql'
                local_osis = Path(tmp) / 'source.osis.json'
                local_db = Path(tmp) / 'module.bblx'
                for p in (local_sql, local_osis, local_db):
                    p.unlink(missing_ok=True)
                download(ROOT + REVISION + '/' + sql[name], local_sql)
                result = convert_sql(local_sql, local_db, name, lang)
                download(ROOT + REVISION + '/' + osis_path, local_osis)
                # Validate the downloaded file before including it.
                with local_osis.open(encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, dict) or not isinstance(data.get('books'), list):
                    raise ValueError('OSIS source has unexpected JSON structure')
                del data
                with local_osis.open('rb') as src, gzip.open(sidecar, 'wb', compresslevel=6) as dest:
                    shutil.copyfileobj(src, dest)
                shutil.move(str(local_db), module)
                report['results'].append(result)
                if result['unmapped_verses']:
                    print(f"  WARNING: {result['unmapped_verses']} rows not visible in e-Sword; see report", flush=True)
            except Exception as exc:
                sidecar.unlink(missing_ok=True)
                module.unlink(missing_ok=True)
                report['errors'].append({'translation': name, 'error': str(exc)})
                print(f'  ERROR: {exc}', file=sys.stderr, flush=True)
            save_report()
    (output / 'README.txt').write_text('''Modules are in modules/. Install only after testing in your version of e-Sword.\nOriginal OSIS source JSON, including source annotations, is compressed in source_osis/.\nThose annotations are NOT converted to interactive e-Sword markup. SQL exports may\ncontain normalized text that differs from the OSIS source. Verses outside the\nstandard 66 books, duplicate references, and non-positive references are stored\nin each module's UnmappedVerses table, not displayed in e-Sword. See the JSON report.\nLicences vary; check the report and upstream sources before redistribution.\n''', encoding='utf-8')
    if args.zip:
        with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
            for file in sorted(output.rglob('*')):
                if file.is_file():
                    z.write(file, file.relative_to(output))
        print('Archive:', archive)
    print(f"Created {len(report['results'])} module(s); {len(report['errors'])} failed. Report: {report_path}")
    print('Modules require e-Sword testing; read the report and README.txt.')
    return 1 if report['errors'] or any(r['unmapped_verses'] for r in report['results']) else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (KeyboardInterrupt, Exception) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        sys.exit(1)
