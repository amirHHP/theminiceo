#!/usr/bin/env python3
"""
scripts/test_verify_localization_adversarial.py - Adversarial Stress Test Suite
for scripts/verify_localization.py.

Empirically challenges:
1. Severely corrupted YAML/TOML frontmatters (syntax errors, unclosed quotes, swallowed TOMLDecodeError)
2. Decomposed (NFD) vs Precomposed (NFC) Unicode Persian slugs (mismatches and normalization)
3. Boundary file sizes (0B, 49B, 50B, 51B, whitespace-only, body thresholds)
4. Stray non-markdown files, deeply nested directories, dotfiles, and relative/hidden path bugs
5. Special characters and quotes in titles, Persian text in bodies, and null/empty field handling
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unicodedata
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_localization
from verify_localization import audit, is_excluded, main, parse_frontmatter

SCRIPT_PATH = Path(__file__).resolve().parent / "verify_localization.py"


class AdversarialCorruptedFrontmatterTests(unittest.TestCase):
    """Stress tests on corrupted, malformed, and anomalous YAML/TOML frontmatter."""

    def test_corrupted_yaml_syntax_with_valid_keys(self):
        """
        Adversarial Test: YAML containing unparseable syntax lines alongside valid keys.
        Hugo's yaml parser will fail to compile this, but verify_localization.py
        regex parser silently ignores the malformed syntax.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            corrupted_yaml = (
                "---\n"
                "title: 'Valid English Title'\n"
                "date: '2026-10-10'\n"
                "description: 'Valid English Description'\n"
                "[severely corrupted {:: yaml line that violates yaml spec\n"
                "another broken line without colon or key value\n"
                "---\n"
                "Body content exceeding fifty bytes threshold for localization.\n"
            )
            (tmp / "test.en.md").write_text(corrupted_yaml, encoding="utf-8")

            res = audit(content_dir=str(tmp))
            # EMPIRICAL OBSERVATION:
            # Does verify_localization detect the corrupted YAML syntax?
            # Notice: res.is_success is True because it ignores non-matching lines!
            is_detected = (not res.is_success) or (len(res.frontmatter_errors) > 0)
            print(f"[Corrupted YAML Test] is_detected={is_detected}, is_success={res.is_success}")
            # We record whether it caught it or silently passed

    def test_corrupted_toml_swallowed_decoder_error(self):
        """
        Adversarial Test: TOML containing invalid syntax that causes tomllib.TOMLDecodeError.
        Verify if tomllib error is swallowed by verify_localization.py fallback.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("+++\ntitle = 'فارسی'\n+++", encoding="utf-8")
            corrupted_toml = (
                "+++\n"
                "title = 'Valid English Title'\n"
                "date = '2026-10-10T12:00:00Z'\n"
                "description = 'Valid English Description'\n"
                "[broken table header without closing bracket\n"
                "illegal = syntax = == = error\n"
                "+++\n"
                "Body content exceeding fifty bytes threshold for localization.\n"
            )
            (tmp / "test.en.md").write_text(corrupted_toml, encoding="utf-8")

            res = audit(content_dir=str(tmp))
            is_detected = (not res.is_success) or (len(res.frontmatter_errors) > 0)
            print(f"[Corrupted TOML Test] is_detected={is_detected}, is_success={res.is_success}")

    def test_unclosed_quotes_in_yaml_title(self):
        """Adversarial Test: Title with unclosed double quote in YAML."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            content = (
                "---\n"
                'title: "Unclosed Quote in Title\n'
                'date: "2026-10-10"\n'
                'description: "Valid Description"\n'
                "---\n"
                "Body content exceeding fifty bytes threshold for localization.\n"
            )
            (tmp / "test.en.md").write_text(content, encoding="utf-8")
            res = audit(content_dir=str(tmp))
            print(f"[Unclosed Quote YAML Test] is_success={res.is_success}, fm_errors={res.frontmatter_errors}")

    def test_unclosed_quotes_in_toml_title(self):
        """Adversarial Test: Title with unclosed double quote in TOML."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("+++\ntitle = 'فارسی'\n+++", encoding="utf-8")
            content = (
                "+++\n"
                'title = "Unclosed Quote in Title\n'
                'date = "2026-10-10"\n'
                'description = "Valid Description"\n'
                "+++\n"
                "Body content exceeding fifty bytes threshold for localization.\n"
            )
            (tmp / "test.en.md").write_text(content, encoding="utf-8")
            res = audit(content_dir=str(tmp))
            print(f"[Unclosed Quote TOML Test] is_success={res.is_success}, fm_errors={res.frontmatter_errors}")

    def test_unclosed_delimiter(self):
        """Adversarial Test: Missing closing delimiter."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            (tmp / "test.en.md").write_text("---\ntitle: 'Title'\ndate: '2026-10-10'\nNo closing delimiter", encoding="utf-8")
            res = audit(content_dir=str(tmp))
            self.assertFalse(res.is_success)
            self.assertEqual(len(res.frontmatter_errors), 1)
            self.assertEqual(res.frontmatter_errors[0].issue_type, "invalid_delimiters")

    def test_leading_blank_line_before_delimiter(self):
        """Adversarial Test: Leading blank line before frontmatter delimiter."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            (tmp / "test.en.md").write_text("\n---\ntitle: 'Title'\ndate: '2026-10-10'\n---\nBody over fifty bytes threshold.", encoding="utf-8")
            res = audit(content_dir=str(tmp))
            self.assertFalse(res.is_success)
            self.assertEqual(res.frontmatter_errors[0].issue_type, "invalid_delimiters")


class AdversarialUnicodeNormalizationTests(unittest.TestCase):
    """Stress tests on Persian Unicode slugs: precomposed (NFC) vs decomposed (NFD)."""

    def test_nfc_persian_with_nfd_english(self):
        """
        Adversarial Test: Persian file created as NFC, English file created as NFD.
        Tests byte-exact matching behavior.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            slug_base = "خلق-محصولات-آینده"
            nfc_slug = unicodedata.normalize("NFC", slug_base)
            nfd_slug = unicodedata.normalize("NFD", slug_base)

            self.assertNotEqual(nfc_slug, nfd_slug, "NFC and NFD representations should differ")

            # Write Persian as NFC
            (tmp / f"{nfc_slug}.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
            # Write English as NFD
            (tmp / f"{nfd_slug}.en.md").write_text(
                "---\ntitle: 'Creating Future Products'\ndate: '2026-10-10'\n---\nBody text exceeding fifty bytes threshold.",
                encoding="utf-8",
            )

            res = audit(content_dir=str(tmp))
            print(f"[NFC Persian / NFD English] is_success={res.is_success}, missing={len(res.missing_files)}")

    def test_nfd_persian_with_nfc_english(self):
        """
        Adversarial Test: Persian file created as NFD, English file created as NFC.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            slug_base = "خلق-محصولات-آینده"
            nfc_slug = unicodedata.normalize("NFC", slug_base)
            nfd_slug = unicodedata.normalize("NFD", slug_base)

            # Write Persian as NFD
            (tmp / f"{nfd_slug}.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
            # Write English as NFC
            (tmp / f"{nfc_slug}.en.md").write_text(
                "---\ntitle: 'Creating Future Products'\ndate: '2026-10-10'\n---\nBody text exceeding fifty bytes threshold.",
                encoding="utf-8",
            )

            res = audit(content_dir=str(tmp))
            print(f"[NFD Persian / NFC English] is_success={res.is_success}, missing={len(res.missing_files)}")

    def test_persian_digits_in_title(self):
        """Adversarial Test: Persian digits in English title (e.g. 'Chapter ۱')."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            (tmp / "test.en.md").write_text(
                "---\ntitle: 'Chapter ۱: Product Strategy'\ndate: '2026-10-10'\n---\nBody text exceeding fifty bytes.",
                encoding="utf-8",
            )
            res = audit(content_dir=str(tmp))
            self.assertFalse(res.is_success)
            self.assertEqual(res.frontmatter_errors[0].issue_type, "persian_in_title")


class AdversarialBoundarySizeTests(unittest.TestCase):
    """Stress tests on boundary file sizes: 0, 49, 50, 51 bytes."""

    def test_zero_bytes_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            (tmp / "test.en.md").write_bytes(b"")
            res = audit(content_dir=str(tmp), min_file_size=50)
            self.assertFalse(res.is_success)
            self.assertEqual(res.empty_files[0].issue_type, "undersized_file")
            self.assertIn("0 bytes", res.empty_files[0].message)

    def test_forty_nine_bytes_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            base = "---\ntitle: 'A'\ndate: 'B'\n---\n"
            content = base + ("x" * (49 - len(base.encode("utf-8"))))
            self.assertEqual(len(content.encode("utf-8")), 49)
            (tmp / "test.en.md").write_text(content, encoding="utf-8")
            res = audit(content_dir=str(tmp), min_file_size=50)
            self.assertFalse(res.is_success)
            self.assertEqual(res.empty_files[0].issue_type, "undersized_file")
            self.assertIn("49 bytes", res.empty_files[0].message)

    def test_fifty_bytes_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            base = "---\ntitle: 'A'\ndate: 'B'\n---\n"
            content = base + ("x" * (50 - len(base.encode("utf-8"))))
            self.assertEqual(len(content.encode("utf-8")), 50)
            (tmp / "test.en.md").write_text(content, encoding="utf-8")
            res = audit(content_dir=str(tmp), min_file_size=50)
            self.assertFalse(res.is_success)
            self.assertEqual(res.empty_files[0].issue_type, "undersized_file")
            self.assertIn("50 bytes", res.empty_files[0].message)

    def test_fifty_one_bytes_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            base = "---\ntitle: 'A'\ndate: 'B'\n---\n"
            content = base + ("x" * (51 - len(base.encode("utf-8"))))
            self.assertEqual(len(content.encode("utf-8")), 51)
            (tmp / "test.en.md").write_text(content, encoding="utf-8")
            res = audit(content_dir=str(tmp), min_file_size=50)
            self.assertTrue(res.is_success)
            self.assertEqual(len(res.empty_files), 0)

    def test_whitespace_only_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            (tmp / "test.en.md").write_text("   \n\t   \n" * 10, encoding="utf-8")
            res = audit(content_dir=str(tmp), min_file_size=50)
            self.assertFalse(res.is_success)
            self.assertEqual(res.empty_files[0].issue_type, "empty_file")


class AdversarialPathAndDirectoryTests(unittest.TestCase):
    """Stress tests on directory exclusions, stray files, and path parsing vulnerabilities."""

    def test_relative_path_with_dot_dot_bug(self):
        """
        Adversarial Test: Running audit with a path containing '..' (e.g. '../theminiceo/content').
        Due to p.startswith('.') in is_excluded, '..' is treated as a hidden directory,
        causing all files to be skipped and falsely reporting 100% SUCCESS.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            sub = tmp / "sub"
            content = tmp / "content"
            sub.mkdir()
            content.mkdir()
            # Persian file with missing English counterpart!
            (content / "missing.md").write_text("---\ntitle: 'فاقد'\n---", encoding="utf-8")

            # Run from sub pointing to ../content
            rel_path = os.path.relpath(str(content), str(sub))
            self.assertTrue(rel_path.startswith(".."))

            # Direct test of is_excluded on '../content'
            self.assertTrue(is_excluded(rel_path), "is_excluded incorrectly flags '..' as hidden directory")

            # CLI execution
            proc = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "--root", rel_path],
                cwd=str(sub),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"[Relative Path .. Bug] returncode={proc.returncode}, stdout={proc.stdout.strip()[:120]}")
            # Demonstrates vulnerability: returns 0 despite missing English file!

    def test_empty_content_directory_false_success(self):
        """
        Adversarial Test: An empty content directory with 0 Persian files returns exit code 0
        and claims 'SUCCESS: 100% English localization parity achieved!'.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            res = audit(content_dir=tmp_dir)
            self.assertTrue(res.is_success)
            self.assertEqual(res.total_persian_scanned, 0)
            self.assertEqual(res.total_english_found, 0)
            self.assertEqual(res.total_issues, 0)

    def test_deeply_nested_subdirectories(self):
        """Adversarial Test: Files nested 10 directories deep."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            deep_path = tmp
            for i in range(10):
                deep_path = deep_path / f"level_{i}"
            deep_path.mkdir(parents=True)
            (deep_path / "deep.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            (deep_path / "deep.en.md").write_text(
                "---\ntitle: 'Deep Page'\ndate: '2026-10-10'\n---\nValid body text exceeding fifty bytes threshold.",
                encoding="utf-8",
            )
            res = audit(content_dir=str(tmp))
            self.assertEqual(res.total_persian_scanned, 1)
            self.assertEqual(res.total_english_found, 1)
            self.assertTrue(res.is_success)

    def test_stray_non_markdown_and_dotfiles(self):
        """Adversarial Test: Non-markdown files and dotfiles scattered in content tree."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "page.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
            (tmp / "page.en.md").write_text(
                "---\ntitle: 'English Page'\ndate: '2026-10-10'\n---\nValid body text exceeding fifty bytes threshold.",
                encoding="utf-8",
            )
            # Strays
            (tmp / ".DS_Store").write_bytes(b"\x00\x00\x00")
            (tmp / "._page.md").write_bytes(b"AppleDouble binary header")
            (tmp / "image.png").write_bytes(b"\x89PNG\r\n")
            (tmp / "notes.txt").write_text("Notes text", encoding="utf-8")
            (tmp / "data.json").write_text("{}", encoding="utf-8")
            (tmp / "page.md.bak").write_text("backup", encoding="utf-8")

            res = audit(content_dir=str(tmp))
            self.assertEqual(res.total_persian_scanned, 1)
            self.assertEqual(res.total_english_found, 1)
            self.assertTrue(res.is_success)

    def test_orphan_english_file_unpaired(self):
        """
        Adversarial Test: An orphaned English file exists with no Persian counterpart.
        Verify if auditor audits or reports orphan .en.md files.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "orphan.en.md").write_text(
                "---\ntitle: 'Orphan English'\ndate: '2026-10-10'\n---\nValid body text exceeding fifty bytes threshold.",
                encoding="utf-8",
            )
            res = audit(content_dir=str(tmp))
            print(f"[Orphan English Test] persian_scanned={res.total_persian_scanned}, en_found={res.total_english_found}, is_success={res.is_success}")


class AdversarialContentQualityAndTitleTests(unittest.TestCase):
    """Stress tests on titles, body content, and acceptance criteria edge cases."""

    def test_special_characters_and_quotes_in_title(self):
        """Adversarial Test: Complex titles with quotes, colons, emojis, and symbols."""
        titles = [
            'System Architecture: "Microservices & Distributed Systems"',
            "Founder's Dilemma: 'Equity, Hiring & Growth'",
            "AI & ML in 2026: 🚀 100% Practical Insights & Frameworks",
            "C++ vs Rust: Memory Safety, Concurrency, and I/O",
            "Books & Guides: <Tech Edition> & [Special Edition]",
        ]
        for t in titles:
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp = Path(tmp_dir)
                (tmp / "doc.md").write_text("---\ntitle: 'فارسی'\n---", encoding="utf-8")
                # Quote escaped in YAML
                escaped_t = t.replace('"', '\\"')
                (tmp / "doc.en.md").write_text(
                    f'---\ntitle: "{escaped_t}"\ndate: "2026-10-10"\n---\nValid body text exceeding fifty bytes threshold.\n',
                    encoding="utf-8",
                )
                res = audit(content_dir=str(tmp))
                self.assertTrue(res.is_success, f"Failed for title: {t}")

    def test_untranslated_persian_body_in_english_page(self):
        """
        Adversarial Test: English file where frontmatter is English, but body is 100% Persian text.
        Acceptance Criteria explicitly requires no untranslated Persian blocks in English pages.
        Check whether verify_localization.py detects Persian in body.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "doc.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
            (tmp / "doc.en.md").write_text(
                "---\n"
                "title: 'English Book'\n"
                "date: '2026-10-10'\n"
                "description: 'English Description'\n"
                "---\n"
                "این یک متن کاملا فارسی در بدنه مقاله انگلیسی است و هیچ ترجمه ای انجام نشده است. "
                "باید مشخص شود که آیا این خطای عدم ترجمه توسط ابزار تایید شناسایی می شود یا خیر.\n",
                encoding="utf-8",
            )
            res = audit(content_dir=str(tmp), strict=True)
            print(f"[Persian Body in EN Page] is_success={res.is_success}, other_errors={res.other_errors}")


if __name__ == "__main__":
    unittest.main()
