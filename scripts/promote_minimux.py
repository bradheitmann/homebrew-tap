#!/usr/bin/env python3
"""Promote a published Minimux release after verifying every platform archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.request import Request, urlopen

REPOSITORY = "bradheitmann/minimux"
TARGETS = ("aarch64-macos", "x86_64-macos", "aarch64-linux", "x86_64-linux")
MAX_ARCHIVE_BYTES = 64 * 1024 * 1024


def version_text(value: str) -> str:
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", value):
        raise ValueError("Version must be a stable numeric version such as 0.2.0")
    return value


def download(url: str, limit: int) -> bytes:
    request = Request(url, headers={"User-Agent": "minimux-formula-promotion"})
    with urlopen(request, timeout=60) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Release asset exceeds the download limit")
    return data


def verified_archives(version: str, release: dict, fetch=download) -> dict[str, tuple[str, str]]:
    version_text(version)
    tag = "v" + version
    if release.get("tag_name") != tag or release.get("draft") is not False or release.get("prerelease") is not False:
        raise ValueError("The requested release must be published, stable, and match the version")
    if not release.get("published_at"):
        raise ValueError("Release publication has not completed")
    assets = release.get("assets", [])
    by_name = {}
    for asset in assets:
        name = asset.get("name")
        if not isinstance(name, str) or name in by_name:
            raise ValueError("Release asset names are missing or duplicated")
        by_name[name] = asset
    verified = {}
    base = f"https://github.com/{REPOSITORY}/releases/download/{tag}/"
    for target in TARGETS:
        name = f"minimux-{tag}-{target}.tar.gz"
        url = base + name
        for expected in (name, name + ".sha256"):
            if by_name.get(expected, {}).get("browser_download_url") != base + expected:
                raise ValueError(f"Missing or unexpected release URL for {expected}")
        checksum = fetch(url + ".sha256", 4096).decode("ascii").strip()
        match = re.fullmatch(r"([0-9a-fA-F]{64})[ \t]+\*?" + re.escape(name), checksum)
        if match is None:
            raise ValueError(f"Malformed checksum record for {name}")
        archive = fetch(url, MAX_ARCHIVE_BYTES)
        digest = hashlib.sha256(archive).hexdigest()
        if digest != match[1].lower():
            raise ValueError(f"Archive checksum mismatch for {name}")
        platform_digest = by_name[name].get("digest")
        if platform_digest is not None and platform_digest != "sha256:" + digest:
            raise ValueError(f"GitHub asset digest mismatch for {name}")
        verified[target] = (url, digest)
    return verified


def render_formula(source: str, version: str, archives: dict[str, tuple[str, str]]) -> str:
    version_text(version)
    if set(archives) != set(TARGETS):
        raise ValueError("All four platform archives are required")
    result = source
    for target in TARGETS:
        url, digest = archives[target]
        expected = f"https://github.com/{REPOSITORY}/releases/download/v{version}/minimux-v{version}-{target}.tar.gz"
        if url != expected or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Archive identity is invalid")
        pattern = (r'url "https://github\.com/bradheitmann/minimux/releases/download/v[^/]+/'
                   r'minimux-v[^/]+-' + re.escape(target) + r'\.tar\.gz"\n(\s*)sha256 "[0-9a-f]{64}"')
        result, count = re.subn(pattern, lambda match: f'url "{url}"\n{match[1]}sha256 "{digest}"', result)
        if count != 1:
            raise ValueError(f"Formula must contain exactly one archive for {target}")
    result, count = re.subn(r"assert_match '\"version\":\"[0-9]+\.[0-9]+\.[0-9]+\"', output",
                            lambda _: f"assert_match '\"version\":\"{version}\"', output", result)
    if count != 1:
        raise ValueError("Formula version assertion is missing or ambiguous")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", type=version_text)
    parser.add_argument("--write", action="store_true", help="Replace the formula after all assets verify")
    args = parser.parse_args()
    formula = Path(__file__).resolve().parents[1] / "Formula" / "minimux.rb"
    release = json.loads(download(f"https://api.github.com/repos/{REPOSITORY}/releases/tags/v{args.version}", 1024 * 1024))
    archives = verified_archives(args.version, release)
    source = formula.read_text()
    proposed = render_formula(source, args.version, archives)
    if not args.write:
        print(proposed, end="")
        return
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=formula.parent, prefix=".minimux-", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(proposed)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(formula.stat().st_mode & 0o777)
        # Refuse to overwrite another maintainer's concurrent edit.
        if formula.read_text() != source:
            raise RuntimeError("Formula changed during validation; inspect and retry")
        os.replace(temporary, formula)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f"Updated {formula.name} to {args.version}; run formula CI before merge")


if __name__ == "__main__":
    main()
