# Addon Submission

Addon submissions are reviewed through pull requests.

## Requirements

- Publish your addon from its own public repository.
- Attach a release archive containing `addon.json` and addon files.
- Add a manifest file under `addons/`.
- Add the manifest to `index.json`.
- Include a SHA-256 checksum for the release archive before the addon is considered installable.

## Review Notes

Addons should request the smallest permission set needed. Dangerous permissions such as Docker access, host filesystem writes, or command execution require clear justification.
