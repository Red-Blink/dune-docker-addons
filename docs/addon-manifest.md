# Addon Manifest

Each addon entry describes one installable addon release.

Example:

```json
{
  "id": "leadership-board",
  "name": "Leadership Board",
  "description": "Shows a ranked overview of players with level, faction, guild, status, and last seen details.",
  "author": "Red-Blink",
  "version": "1.0.0",
  "type": "ui",
  "sourceUrl": "https://github.com/Red-Blink/dune-console-addon-leadership-board",
  "downloadUrl": "https://github.com/Red-Blink/dune-console-addon-leadership-board/releases/download/v1.0.0/leadership-board.zip",
  "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "permissions": [
    "players:read"
  ]
}
```

## Fields

- `id`: Stable lowercase addon ID. Use letters, numbers, and hyphens.
- `name`: User-facing addon name.
- `description`: Short user-facing summary.
- `author`: Addon author or organization.
- `version`: Addon release version. Update this value in the same addon manifest for new releases.
- `type`: Addon type, initially `ui`.
- `sourceUrl`: Public source repository.
- `downloadUrl`: Pinned release archive URL. Do not use floating `latest` URLs.
- `sha256`: Required SHA-256 checksum of the archive.
- `permissions`: Requested console permissions.

## SHA-256

The checksum must match the exact archive served by `downloadUrl`.

Generate it after building the addon zip:

```bash
sha256sum leadership-board.zip
```

The console should refuse to install community addons when `sha256` is missing, malformed, or does not match the downloaded archive.
