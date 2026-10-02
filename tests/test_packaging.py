"""Release archives must be complete and leave prior releases intact on failure."""
import datetime
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import packer


class PackagingTests(unittest.TestCase):
    def prepare_files(self, source):
        files = {'dist/main.exe': b'MZ-test-executable'}
        files.update({name: name.encode('utf-8') for name in packer.RESOURCES})
        for name, content in files.items():
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        return files

    def test_archive_contains_executable_and_all_resources_from_another_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / 'source with spaces'
            other = Path(temporary) / 'other'
            other.mkdir()
            files = self.prepare_files(source)
            previous = Path.cwd()
            try:
                os.chdir(other)
                with patch('packer.SOURCE_DIR', source):
                    archive = packer.create_archive(date=datetime.date(2026, 10, 2))
            finally:
                os.chdir(previous)
            self.assertEqual(archive.parent, source / 'output')
            with zipfile.ZipFile(archive) as package:
                self.assertIsNone(package.testzip())
                self.assertEqual(set(package.namelist()), {'贝娜的量角器.exe', *packer.RESOURCES})
                self.assertEqual(package.read('贝娜的量角器.exe'), files['dist/main.exe'])
                for name in packer.RESOURCES:
                    self.assertEqual(package.read(name), files[name])

    def test_missing_executable_or_resource_does_not_create_an_empty_archive(self):
        for missing in ('dist/main.exe', 'translation/anne_dictionary.json'):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as temporary:
                source = Path(temporary)
                self.prepare_files(source)
                (source / missing).unlink()
                with self.assertRaises(FileNotFoundError):
                    packer.create_archive(source)
                self.assertFalse((source / 'output').exists())

    def test_write_failure_preserves_previous_release_and_removes_partial_archive(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary)
            self.prepare_files(source)
            archive = packer.create_archive(source)
            previous = archive.read_bytes()
            with patch('packer.zipfile.ZipFile.write', side_effect=OSError('simulated disk failure')):
                with self.assertRaises(OSError):
                    packer.create_archive(source)
            self.assertEqual(archive.read_bytes(), previous)
            self.assertEqual(list(archive.parent.iterdir()), [archive])


if __name__ == '__main__':
    unittest.main()
