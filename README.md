# homebrew-tap

Homebrew formulae for bradheitmann projects.

```bash
brew tap bradheitmann/tap
brew install minimux
```

The default install contains the full released daemon. The tap does not disable
runtime capabilities or substitute a source checkout for a verified release.

## Promote a verified release

After the Minimux release workflow has published all four platform archives and
their checksum files, preview the next formula:

```bash
python3 scripts/promote_minimux.py 0.2.0
```

The script requires a published stable release in `bradheitmann/minimux`, exact
asset URLs for every supported platform, correctly named checksum records, and
matching SHA-256 digests of the downloaded archives. When GitHub supplies an
asset digest, that digest must match too. Draft, incomplete, mismatched, or
corrupted releases fail before any formula write.

To apply the validated update:

```bash
python3 scripts/promote_minimux.py 0.2.0 --write
```

The formula replacement is atomic and refuses an observed concurrent edit.
Review the diff, then let the macOS formula workflow run style, audit, install,
and executable health checks before merging. Checksums establish artifact
consistency with the trusted release channel; they are not publisher signatures
or a substitute for the upstream release gates.

The formula advances only after real published artifacts are available. A new
version in the upstream source alone is not enough to update an installation.
