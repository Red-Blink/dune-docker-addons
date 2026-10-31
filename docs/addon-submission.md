# Addon Submission

Addon submissions are reviewed through pull requests. This repository is only the community addon list; addon code and release packages stay in each addon developer's own repository.

## Requirements

- Create your addon from `https://github.com/Red-Blink/dune-docker-addon-template`.
- Publish your addon from its own public repository.
- Build an addon install archive containing `addon.json` and the addon files needed at runtime.
- Upload that archive as a GitHub Release asset.
- Add a manifest file under `addons/`. This full manifest contains `sourceUrl`, `downloadUrl`, `sha256`, and `permissions`.
- Add the manifest to `index.json` by adding a short entry with `id`, `name`, `description`, `author`, `version`, lifecycle fields, and `manifestUrl`.
- Include a SHA-256 checksum for the release archive. Addons without a valid checksum are not considered installable.

## Validate Your Submission

Run these from the catalog repository before opening a PR:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
python3 scripts/validate.py --verify-packages
```

The first catalog check is offline. The optional package check downloads active
and deprecated releases without installing or executing them, verifies their
checksums, and checks that each ZIP has `addon.json` at its root, a valid entry
file, and matching identity, version and permissions. These checks also run in
GitHub Actions on PRs, pushes and a weekly schedule.

Test the packaged UI inside the Console sandbox before submitting it. Direct
REST calls, external asset downloads and browser storage are not granted by an
addon manifest. Use the permissioned bridge and bundle needed runtime assets.
See the template's [Bridge API](https://github.com/Red-Blink/dune-docker-addon-template/blob/main/docs/bridge-api.md)
and the Console's [Addon Runtime API](https://github.com/Red-Blink/dune-awakening-selfhost-docker/blob/main/docs/addons/addon-runtime-api.md).

## Manual Release Package Flow

GitHub's automatic `Source code (zip)` and `Source code (tar.gz)` downloads are not addon install packages.

Before submitting or updating an addon:

1. Build the addon package from the addon repository.
2. Upload the generated `.zip` file as a GitHub Release asset.
3. Generate the SHA-256 checksum from that exact `.zip` file.
4. Set `downloadUrl` to the uploaded release asset URL.
5. Set `sha256` to the checksum for that uploaded release asset.

The release asset should contain the addon runtime files, such as:

```text
addon.json
web/
README.md
```

Do not use GitHub's automatic source archive as `downloadUrl`.

## Updating an Existing Addon

Do not create a new addon manifest for every release.

For a new addon version, update the existing file in `addons/`:

- `version`
- `downloadUrl`
- `sha256`
- any changed permissions, description, or metadata

For example, `addons/leadership-board.json` remains the same file when moving from `1.0.0` to `1.0.1`; only the versioned values change.

Only create a new JSON file when submitting a completely new addon.

## Lifecycle States

The community index controls addon lifecycle state. Addon packages should not put lifecycle fields in `addon.json`.

Use these states in `index.json`:

- `active`: supported and available for install.
- `deprecated`: still installable, but may stop receiving updates.
- `unsupported`: no longer supported; hidden from normal recommendation and blocked from new installs.
- `removed`: removed from the community catalog and blocked from new installs.
- `blocked`: blocked for safety; already-installed copies are disabled by the console and cannot be opened or enabled.

Each entry should include:

```json
"lifecycle": "active",
"lifecycleMessage": "",
"lifecycleUrl": ""
```

Use `lifecycleMessage` for a short user-facing reason, and `lifecycleUrl` for more details when needed.

If an addon is abandoned, mark it `unsupported` or `removed` instead of deleting the entry immediately. If an addon is unsafe, mark it `blocked`.

## Release Pinning

Community addon entries must point to a specific reviewed release archive, not a floating `latest` URL.

Good:

```text
https://github.com/example/dune-addon/releases/download/v1.0.1/addon.zip
```

Avoid:

```text
https://github.com/example/dune-addon/releases/latest/download/addon.zip
```

Pinned releases keep installs reproducible and let the console verify the archive against the submitted SHA-256 checksum.

## Review Notes

Addons should request the smallest permission set needed. Dangerous permissions such as Docker access, host filesystem writes, or command execution require clear justification.
