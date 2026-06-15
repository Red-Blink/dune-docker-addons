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
  "sha256": "",
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
- `version`: Addon release version.
- `type`: Addon type, initially `ui`.
- `sourceUrl`: Public source repository.
- `downloadUrl`: Release archive URL.
- `sha256`: SHA-256 checksum of the archive.
- `permissions`: Requested console permissions.
