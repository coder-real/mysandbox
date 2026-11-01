import contextlib
import gzip
import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('converter', Path(__file__).with_name('convert_bibles.py'))
converter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(converter)


class ConverterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_escapes(self):
        self.assertEqual(converter.mysql_unescape(r"Jacob\'s \\ tent\nline"), "Jacob's \\ tent\nline")
        with self.assertRaises(ValueError):
            converter.mysql_unescape(r'bad\q')

    def test_mapping_html_and_unmapped_preservation(self):
        sql = self.root / 'input.sql'
        sql.write_text("""-- SQL Dump for # Test (X)
-- License: Test license
INSERT INTO `X_books` (`name`) VALUES ('Matthew');
INSERT INTO `X_books` (`name`) VALUES ('Tobit');
INSERT INTO `X_books` (`name`) VALUES ('Genesis');
INSERT INTO `X_verses` (`book_id`, `chapter`, `verse`, `text`) VALUES (1, 1, 1, 'Jacob\\'s & <text>');
INSERT INTO `X_verses` (`book_id`, `chapter`, `verse`, `text`) VALUES (2, 1, 1, 'extra');
INSERT INTO `X_verses` (`book_id`, `chapter`, `verse`, `text`) VALUES (3, 1, 0, 'heading');
INSERT INTO `X_verses` (`book_id`, `chapter`, `verse`, `text`) VALUES (1, 1, 1, 'duplicate');
""", encoding='utf-8')
        output = self.root / 'out.bblx'
        result = converter.convert_sql(sql, output, 'X', 'he')
        self.assertEqual((result['source_verses'], result['module_verses'], result['unmapped_verses']), (4, 1, 3))
        with contextlib.closing(sqlite3.connect(output)) as db:
            self.assertEqual(db.execute('SELECT * FROM Bible').fetchone(), (40, 1, 1, "Jacob's &amp; &lt;text&gt;"))
            self.assertEqual(db.execute('SELECT BookName, Scripture FROM UnmappedVerses ORDER BY rowid').fetchall(), [('Tobit', 'extra'), ('Genesis', 'heading'), ('Matthew', 'duplicate')])
            self.assertEqual(db.execute('SELECT RightToLeft, OT, NT, Apocrypha, Strong FROM Details').fetchone(), (1, 0, 1, 0, 0))
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_bad_insert_is_not_silently_ignored(self):
        sql = self.root / 'bad.sql'
        sql.write_text("INSERT INTO `X_books` (`name`) VALUES ('Genesis');\nINSERT INTO `X_verses` unexpected;\n", encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Unrecognized verse INSERT'):
            converter.convert_sql(sql, self.root / 'bad.bblx', 'X')

    def test_main_writes_zip_report_and_lossless_osis(self):
        out = self.root / 'batch'
        sql_text = "INSERT INTO `X_books` (`name`) VALUES ('Genesis');\nINSERT INTO `X_verses` (`book_id`, `chapter`, `verse`, `text`) VALUES (1, 1, 1, 'Hi');\n"
        osis_text = '{"books": [{"name":"Genesis", "text":"<w lemma=\\"strong:H1\\">Hi</w>"}]}'
        def download(url, path):
            Path(path).write_text(osis_text if url.endswith('-osis.json') else sql_text, encoding='utf-8')
        with patch.object(converter, 'catalogue', return_value=({'X': 'formats/sql/X.sql'}, {'X': ('en', 'sources/en/X/X-osis.json')})), patch.object(converter, 'download', side_effect=download), patch.object(sys, 'argv', ['convert_bibles.py', '--translations', 'X', '--output', str(out), '--zip']):
            self.assertEqual(converter.main(), 0)
        self.assertTrue(out.with_suffix('.zip').is_file())
        self.assertEqual(gzip.open(out / 'source_osis/X.osis.json.gz', 'rt', encoding='utf-8').read(), osis_text)
        self.assertEqual(json.loads((out / 'conversion-report.json').read_text())['results'][0]['module_verses'], 1)


if __name__ == '__main__':
    unittest.main()
