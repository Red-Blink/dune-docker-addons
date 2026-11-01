#!/usr/bin/env python3
"""Validate catalog metadata and, optionally, the exact pinned install archives."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import zipfile

PERMISSIONS = {
    'players:read', 'ops:read', 'database:read', 'database:write',
    'admin:grant-items', 'rewards:grant', 'players:message', 'server:status',
    'server:restart', 'files:addon-data', 'broadcast:send', 'scheduler:server',
    'realtime:read',
}
LIFECYCLES = {'active', 'deprecated', 'unsupported', 'removed', 'blocked'}
ID = re.compile(r'[a-z0-9][a-z0-9-]{1,63}\Z')
VERSION = re.compile(r'(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?\Z')
MAX_ARCHIVE = 50 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value, field):
    require(isinstance(value, str) and 0 < len(value.strip()) <= 500, f'{field} must be a non-empty string of at most 500 characters')
    return value.strip()


def https_url(value, field):
    parsed = urlparse(text(value, field))
    require(parsed.scheme == 'https' and parsed.hostname and not parsed.username and not parsed.password, f'{field} must be a public HTTPS URL without credentials')
    return parsed


def permissions(value):
    if value is None:
        return []
    if isinstance(value, dict):
        flattened = []
        for scope, actions in value.items():
            require(isinstance(actions, list), f'permissions.{scope} must be an array')
            flattened.extend(f'{scope}:{action}' for action in actions)
    else:
        require(isinstance(value, list), 'permissions must be an object or array')
        flattened = value
    result = sorted(set(text(item, 'permission').lower() for item in flattened))
    require(all(item in PERMISSIONS for item in result), 'unsupported addon permission')
    return result


def safe_path(value):
    value = text(value, 'archive path').replace('\\', '/')
    require(not value.startswith('/') and '\0' not in value and all(part not in {'.', '..'} for part in value.split('/')), 'unsafe archive path')
    return str(PurePosixPath(value))


def download(url):
    with urlopen(Request(url, headers={'User-Agent': 'DuneDocker-Catalog-Validation'}), timeout=30) as response:
        require(urlparse(response.url).scheme == 'https', 'archive redirect must use HTTPS')
        require(int(response.headers.get('Content-Length', 0)) <= MAX_ARCHIVE, 'archive exceeds 50 MiB')
        body = response.read(MAX_ARCHIVE + 1)
    require(0 < len(body) <= MAX_ARCHIVE, 'archive is empty or exceeds 50 MiB')
    return body


def validate_archive(manifest, body):
    require(0 < len(body) <= MAX_ARCHIVE, 'archive size is invalid')
    require(hashlib.sha256(body).hexdigest() == manifest['sha256'].lower(), 'archive checksum does not match catalog')
    with zipfile.ZipFile(io.BytesIO(body)) as archive:
        entries = archive.infolist()
        require(len(entries) <= 10000 and sum(item.file_size for item in entries) <= 250 * 1024 * 1024, 'archive expansion limit exceeded')
        names = set()
        for item in entries:
            name = safe_path(item.filename.rstrip('/'))
            require(name not in names, 'duplicate archive path')
            names.add(name)
            require(stat.S_IFMT(item.external_attr >> 16) != stat.S_IFLNK, 'archive symlinks are not supported')
        require('addon.json' in names, 'archive must contain addon.json at the root')
        require(archive.getinfo('addon.json').file_size <= 65536, 'package manifest is too large')
        packaged = json.loads(archive.read('addon.json'))
        require(packaged.get('id') == manifest['id'] and packaged.get('version') == manifest['version'], 'package identity/version does not match catalog')
        require(packaged.get('schemaVersion', 1) == 1 and packaged.get('type') == 'ui', 'unsupported packaged addon schema/type')
        require(permissions(packaged.get('permissions')) == permissions(manifest.get('permissions')), 'package permissions do not match catalog')
        entry = safe_path(packaged.get('entry', {}).get('path'))
        require(entry in names and not archive.getinfo(entry).is_dir(), 'package entry file is missing')


def validate_catalog(root, verify_packages=False, fetch_archive=download):
    root = Path(root)
    index = json.loads((root / 'index.json').read_text())
    require(isinstance(index, dict) and index.get('schemaVersion') == 1, 'unsupported catalog schema')
    require(isinstance(index.get('addons'), list) and len(index['addons']) <= 200, 'catalog must contain at most 200 addons')
    ids = set()
    for entry in index['addons']:
        addon_id = text(entry.get('id'), 'id')
        require(ID.fullmatch(addon_id) and addon_id not in ids, 'invalid or duplicate addon id')
        ids.add(addon_id)
        lifecycle = entry.get('lifecycle', 'active')
        require(lifecycle in LIFECYCLES, f'{addon_id}: unsupported lifecycle')
        for field in ['name', 'version']:
            text(entry.get(field), field)
        require(entry.get('manifestUrl') == f'https://raw.githubusercontent.com/Red-Blink/dune-docker-addons/main/addons/{addon_id}.json', f'{addon_id}: manifestUrl must point to its reviewed catalog file')
        if entry.get('lifecycleUrl'):
            https_url(entry['lifecycleUrl'], 'lifecycleUrl')
        manifest = json.loads((root / 'addons' / f'{addon_id}.json').read_text())
        require(manifest.get('schemaVersion', 1) == 1 and manifest.get('type') == 'ui', f'{addon_id}: unsupported manifest schema/type')
        require(manifest.get('id') == addon_id and manifest.get('version') == entry['version'], f'{addon_id}: index and manifest identity/version differ')
        for field in ['name', 'description', 'author', 'version']:
            text(manifest.get(field), field)
        require(VERSION.fullmatch(manifest['version']), f'{addon_id}: version must use semantic versioning')
        require(not (set(manifest) & {'lifecycle', 'lifecycleMessage', 'lifecycleUrl'}), f'{addon_id}: lifecycle metadata belongs in index.json')
        https_url(manifest.get('sourceUrl'), 'sourceUrl')
        url = manifest.get('downloadUrl')
        parsed = https_url(url, 'downloadUrl')
        require(parsed.hostname == 'github.com' and re.fullmatch(r'/[^/]+/[^/]+/releases/download/[^/]+/[^/]+\.zip', parsed.path) and not parsed.query and not parsed.fragment and parsed.path.split('/')[5].lower() not in {'latest', 'main', 'master'}, f'{addon_id}: downloadUrl must pin a versioned GitHub release ZIP')
        require(isinstance(manifest.get('sha256'), str) and re.fullmatch('[a-fA-F0-9]{64}', manifest['sha256']), f'{addon_id}: invalid SHA-256')
        permissions(manifest.get('permissions'))
        if verify_packages and lifecycle in {'active', 'deprecated'}:
            validate_archive(manifest, fetch_archive(url))
    require({path.stem for path in (root / 'addons').glob('*.json')} == ids, 'every addon manifest must have exactly one index entry')
    return len(ids)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-packages', action='store_true', help='download and inspect active pinned archives without installing or executing them')
    args = parser.parse_args()
    try:
        count = validate_catalog(Path(__file__).resolve().parents[1], args.verify_packages)
        print(f'PASS: {count} catalog entries validated' + ('; active package checksums, entries and permissions verified' if args.verify_packages else ''))
    except (ValueError, OSError, KeyError, TypeError, zipfile.BadZipFile) as error:
        print(f'Catalog validation failed: {error}', file=sys.stderr)
        sys.exit(1)
