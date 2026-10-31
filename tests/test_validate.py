import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('catalog_validator', Path(__file__).resolve().parents[1] / 'scripts/validate.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'addons').mkdir()
        self.manifest = {'schemaVersion': 1, 'id': 'test-addon', 'name': 'Test Addon', 'description': 'Test fixture', 'author': 'Fixture', 'version': '1.2.3', 'type': 'ui', 'sourceUrl': 'https://github.com/example/addon', 'downloadUrl': 'https://github.com/example/addon/releases/download/v1.2.3/addon.zip', 'sha256': '0' * 64, 'permissions': {'players': ['read']}}
        self.entry = {key: self.manifest[key] for key in ['id', 'name', 'version']}
        self.entry.update(lifecycle='active', manifestUrl='https://raw.githubusercontent.com/Red-Blink/dune-docker-addons/main/addons/test-addon.json')
        self.index = {'schemaVersion': 1, 'addons': [self.entry]}

    def save(self):
        (self.root / 'index.json').write_text(json.dumps(self.index))
        (self.root / 'addons/test-addon.json').write_text(json.dumps(self.manifest))

    def archive(self, wrapped=False, extra=None, changed_permissions=False):
        body = io.BytesIO()
        package = {**self.manifest, 'entry': {'path': 'web/index.html'}}
        if changed_permissions:
            package['permissions'] = ['database:write']
        prefix = 'release/' if wrapped else ''
        with zipfile.ZipFile(body, 'w') as archive:
            archive.writestr(prefix + 'addon.json', json.dumps(package))
            archive.writestr(prefix + 'web/index.html', '<html></html>')
            if extra:
                archive.writestr(extra, 'fixture')
        return body.getvalue()

    def test_valid_offline_and_pinned_archive(self):
        body = self.archive()
        self.manifest['sha256'] = hashlib.sha256(body).hexdigest()
        self.save()
        self.assertEqual(validator.validate_catalog(self.root, True, lambda _: body), 1)

    def test_rejects_duplicate_ids_version_drift_and_external_manifest(self):
        for change in [lambda: self.index['addons'].append(copy.deepcopy(self.entry)), lambda: self.entry.update(version='9.9.9'), lambda: self.entry.update(manifestUrl='https://other.test/addon.json')]:
            saved = copy.deepcopy(self.index)
            change()
            self.save()
            with self.assertRaises(ValueError):
                validator.validate_catalog(self.root)
            self.index = saved
            self.entry = self.index['addons'][0]

    def test_current_permissions_accepted_unknown_permissions_rejected(self):
        self.manifest['permissions'] = ['ops:read', 'server:status', 'files:addon-data', 'players:message', 'rewards:grant', 'admin:grant-items']
        self.save()
        self.assertEqual(validator.validate_catalog(self.root), 1)
        self.manifest['permissions'].append('host:exec')
        self.save()
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            validator.validate_catalog(self.root)

    def test_rejects_floating_downloads_and_malformed_hashes(self):
        for url in ['http://github.com/example/addon/releases/download/v1/a.zip', 'https://github.com/example/addon/releases/latest/download/a.zip', 'https://github.com/example/addon/releases/download/latest/a.zip']:
            self.manifest['downloadUrl'] = url
            self.save()
            with self.assertRaises(ValueError):
                validator.validate_catalog(self.root)
        self.manifest['downloadUrl'] = 'https://github.com/example/addon/releases/download/v1.2.3/a.zip'
        self.manifest['sha256'] = 'bad'
        self.save()
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            validator.validate_catalog(self.root)

    def test_rejects_wrapped_traversal_and_permission_mismatch_packages(self):
        for body in [self.archive(wrapped=True), self.archive(extra='../outside'), self.archive(changed_permissions=True)]:
            self.manifest['sha256'] = hashlib.sha256(body).hexdigest()
            with self.assertRaises(ValueError):
                validator.validate_archive(self.manifest, body)

    def test_rejects_changed_archive_bytes(self):
        with self.assertRaisesRegex(ValueError, 'checksum'):
            validator.validate_archive(self.manifest, self.archive())

    def test_inactive_entries_do_not_download_retired_releases(self):
        self.entry['lifecycle'] = 'removed'
        self.save()
        def forbidden(_):
            raise AssertionError('Inactive addon must not be downloaded')
        self.assertEqual(validator.validate_catalog(self.root, True, forbidden), 1)

    def test_unlisted_manifest_and_unknown_lifecycle_are_rejected(self):
        self.entry['lifecycle'] = 'mystery'
        self.save()
        with self.assertRaises(ValueError):
            validator.validate_catalog(self.root)
        self.entry['lifecycle'] = 'active'
        self.save()
        (self.root / 'addons/unlisted.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'index entry'):
            validator.validate_catalog(self.root)


if __name__ == '__main__':
    unittest.main()
