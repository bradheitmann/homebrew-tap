import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("promotion", ROOT / "scripts/promote_minimux.py")
promotion = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(promotion)


class PromotionTests(unittest.TestCase):
    def setUp(self):
        self.version = "0.2.0"
        self.release = {"tag_name": "v0.2.0", "draft": False, "prerelease": False,
                        "published_at": "2026-10-19T00:00:00Z", "assets": []}
        self.bytes = {}
        base = "https://github.com/bradheitmann/minimux/releases/download/v0.2.0/"
        for target in promotion.TARGETS:
            name = "minimux-v0.2.0-" + target + ".tar.gz"
            archive = ("fixture archive " + target).encode()
            digest = hashlib.sha256(archive).hexdigest()
            self.bytes[base + name] = archive
            self.bytes[base + name + ".sha256"] = (digest + "  " + name + "\n").encode()
            self.release["assets"].extend([
                {"name": name, "browser_download_url": base + name, "digest": "sha256:" + digest},
                {"name": name + ".sha256", "browser_download_url": base + name + ".sha256"}])

    def fetch(self, url, limit):
        value = self.bytes[url]
        self.assertLessEqual(len(value), limit)
        return value

    def test_complete_verified_release_updates_all_platforms_and_health_assertion(self):
        archives = promotion.verified_archives(self.version, self.release, self.fetch)
        source = (ROOT / "Formula/minimux.rb").read_text()
        updated = promotion.render_formula(source, self.version, archives)
        self.assertEqual(updated.count("/releases/download/v0.2.0/"), 4)
        self.assertIn("assert_match '\"version\":\"0.2.0\"'", updated)
        self.assertIn('bin.install "minimux"', updated)

    def test_draft_prerelease_or_wrong_version_is_rejected(self):
        for field, value in [("draft", True), ("prerelease", True), ("published_at", None),
                             ("tag_name", "v0.1.1")]:
            release = copy.deepcopy(self.release)
            release[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                promotion.verified_archives(self.version, release, self.fetch)

    def test_one_corrupted_platform_prevents_a_promotion(self):
        url = next(url for url in self.bytes if url.endswith("x86_64-linux.tar.gz"))
        self.bytes[url] = b"corrupted archive"
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            promotion.verified_archives(self.version, self.release, self.fetch)

    def test_missing_duplicate_or_foreign_asset_is_rejected(self):
        variants = []
        missing = copy.deepcopy(self.release)
        missing["assets"].pop()
        variants.append(missing)
        duplicate = copy.deepcopy(self.release)
        duplicate["assets"].append(duplicate["assets"][0])
        variants.append(duplicate)
        foreign = copy.deepcopy(self.release)
        foreign["assets"][0]["browser_download_url"] = "https://example.invalid/binary"
        variants.append(foreign)
        for release in variants:
            with self.assertRaises(ValueError):
                promotion.verified_archives(self.version, release, self.fetch)

    def test_checksum_must_name_exact_archive(self):
        url = next(url for url in self.bytes if url.endswith(".sha256"))
        self.bytes[url] = b"0" * 64 + b"  different-archive.tar.gz\n"
        with self.assertRaisesRegex(ValueError, "Malformed checksum"):
            promotion.verified_archives(self.version, self.release, self.fetch)

    def test_unexpected_formula_structure_fails_instead_of_partial_edit(self):
        archives = promotion.verified_archives(self.version, self.release, self.fetch)
        with self.assertRaises(ValueError):
            promotion.render_formula("class Minimux < Formula\nend\n", self.version, archives)


if __name__ == "__main__":
    unittest.main()
