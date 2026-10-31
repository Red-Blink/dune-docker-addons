# Catalog Compatibility Review

Reviewed against the current Dune Docker Console on October 31, 2026. Catalog
versions remain pinned to reviewed packages; the newest upstream version is not
automatically the version offered to server owners.

## Unsupported Listings

These listings remain in the catalog with an explanation, and new installations
are unavailable. Existing installed copies are not disabled by `unsupported`
status. This is a compatibility finding, not a claim that the addons are malicious.

| Addon | Reviewed package | Finding |
| --- | --- | --- |
| Dune Chat Monitor | 0.2.9 | Its UI fetches `web/live/status.json`, `messages.json` and history JSON directly. The Console's `connect-src 'none'` sandbox policy blocks those requests, even for same-host files. |
| MapViewer3D | 0.3.1 | Its map-data loader fetches terrain metadata from GitHub/CDN mirrors. Its connection code also calls Console REST endpoints directly with an API key. Those requests are outside the addon bridge and blocked by the sandbox. |

The blocked requests were reproduced in an isolated browser using the Console's
actual sandbox policy and the pinned release files. No live server, credentials,
player data or installation was used. Reinstatement requires a release tested
inside the supported Console sandbox. Server owners should not weaken that
sandbox to make an addon work.

## Retained Version Pins

**Dune Ops Observability remains at 0.4.7.** The newer
[v0.5.1 release](https://github.com/yacketrj/dune-ops-observability-addon/releases/tag/v0.5.1)
asset inspected during this review places `addon.json` inside a top-level
`dune-ops-observability-0.5.1/` folder. The Console requires `addon.json` at the
ZIP root, so that asset is not a valid install package. The pinned 0.4.7 archive
passes checksum, entry-file and permission validation.

MapViewer3D has a newer upstream release, but a version bump alone does not
establish sandbox compatibility. Its listing remains unavailable pending a
compatible, reviewed package. EDA Exchange Bot remains retired because its
replacement is already built into the Console.

## Package Checks

All seven previously active pinned packages were downloaded and verified during
the review: SHA-256, package identity/version, root manifest, entry file and
requested permissions matched their catalog records. These checks establish
package integrity; they do not prove every addon feature works in game.

Run `python3 scripts/validate.py --verify-packages` to verify the currently active
and deprecated packages. GitHub Actions repeats these checks for contributions
and on a weekly schedule. See [Addon Submission](addon-submission.md) for the
runtime compatibility requirements.
