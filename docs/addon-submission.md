# Addon Submission

Addon submissions are reviewed through pull requests.

## Requirements

- Publish your addon from its own public repository.
- Attach a release archive containing `addon.json` and addon files.
- Add a manifest file under `addons/`.
- Add the manifest to `index.json`.
- Include a SHA-256 checksum for the release archive. Addons without a valid checksum are not considered installable.

## Updating an Existing Addon

Do not create a new addon manifest for every release.

For a new addon version, update the existing file in `addons/`:

- `version`
- `downloadUrl`
- `sha256`
- any changed permissions, description, or metadata

For example, `addons/leadership-board.json` remains the same file when moving from `1.0.0` to `1.0.1`; only the versioned values change.

Only create a new JSON file when submitting a completely new addon.

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
