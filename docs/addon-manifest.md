# Addon Manifest

Each addon manifest describes one installable addon release. The short entries in `index.json` point to these manifest files through `manifestUrl`.

Example:

```json
{
  "id": "leadership-board",
  "name": "Leadership Board",
  "description": "Shows a ranked overview of players with level, faction, guild, status, and last seen details.",
  "author": "Red-Blink",
  "version": "1.0.0",
  "type": "ui",
  "sourceUrl": "https://github.com/Red-Blink/dune-docker-leadership",
  "downloadUrl": "https://github.com/Red-Blink/dune-docker-leadership/releases/download/v1.0.0/leadership-board.zip",
  "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "permissions": {
    "players": ["read"]
  }
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
- `permissions`: Requested console permissions. Use structured permissions such as `{ "players": ["read"] }`. The console also accepts legacy string arrays like `["players:read"]`, but structured permissions are preferred for new addons.

Supported permission names are `players:read`, `ops:read`, `server:status`,
`files:addon-data`, `rewards:grant`, `players:message`, `admin:grant-items`,
`database:read`, `database:write`, `server:restart`, `broadcast:send`,
`scheduler:server` and `realtime:read` (written `{ "realtime": ["read"] }`; it needs a
Console that provides the `realtime.health` and `realtime.objects` bridge actions). A recognized permission does not guarantee a general action
exists: restart/broadcast are reserved, and scheduler access is legacy. For new
addons, prefer the typed player, storage, hardware and delivery APIs described
in the [template permission guide](https://github.com/Red-Blink/dune-docker-addon-template/blob/main/docs/permissions.md).

## SHA-256

The checksum must match the exact archive served by `downloadUrl`.

Generate it after building the addon zip:

```bash
sha256sum leadership-board.zip
```

The console should refuse to install community addons when `sha256` is missing, malformed, or does not match the downloaded archive.

## Catalog Lifecycle Metadata

Lifecycle fields belong in `index.json`, not in the install manifest under `addons/`.

Example `index.json` entry:

```json
{
  "id": "leadership-board",
  "name": "Leadership Board",
  "description": "Shows a ranked overview of players with level, faction, guild, status, and last seen details.",
  "author": "Red-Blink",
  "version": "1.0.0",
  "lifecycle": "active",
  "lifecycleMessage": "",
  "lifecycleUrl": "",
  "manifestUrl": "https://raw.githubusercontent.com/Red-Blink/dune-docker-addons/main/addons/leadership-board.json"
}
```

Supported lifecycle states:

- `active`: supported and installable.
- `deprecated`: installable, but maintenance may end.
- `unsupported`: blocked from new installs because it is no longer supported.
- `removed`: blocked from new installs because it was removed from the catalog.
- `blocked`: disabled by the console for safety.

This lets the console warn users about abandoned addons and block unsafe addons without changing the addon's released package.
