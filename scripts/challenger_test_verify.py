#!/usr/bin/env python3
"""
scripts/challenger_test_verify.py - Adversarial & Contract Verification Harness
Executed by challenger_m1_2 to empirically verify CLI contracts, exit codes,
JSON output schema, and stress-test scripts/verify_localization.py.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "verify_localization.py"


class ChallengerContractAndExitCodeTests(unittest.TestCase):
    """Verifies the core contract and exit code semantics specified in dispatch."""

    def run_cli(self, args, cwd=None):
        cmd = [sys.executable, str(SCRIPT_PATH)] + args
        proc = subprocess.run(
            cmd,
            cwd=str(cwd or ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        return proc

    def test_synthetic_100_percent_paired_valid_tree(self):
        """On synthetic 100% paired valid directory tree -> verify exit 0, stdout contains 'SUCCESS' and '100%'."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            # Create a multi-tier tree with standard pages, books, reports, categories
            # 1. Standard page
            p1_fa = tmp / "intro.md"
            p1_en = tmp / "intro.en.md"
            p1_fa.write_text("---\ntitle: 'معرفی'\n---\nمتن معرفی فارسی.", encoding="utf-8")
            p1_en.write_text("---\ntitle: 'Introduction'\ndate: '2026-10-10'\n---\nFull English introduction content exceeding fifty bytes threshold.", encoding="utf-8")

            # 2. Book page in docs/books
            books_dir = tmp / "docs" / "books"
            books_dir.mkdir(parents=True)
            b1_fa = books_dir / "clean-code.md"
            b1_en = books_dir / "clean-code.en.md"
            b1_fa.write_text("---\ntitle: 'کد تمیز'\n---\nمتن کتاب فارسی.", encoding="utf-8")
            b1_en.write_text(
                "---\ntitle: 'Clean Code'\ndate: '2026-10-10'\ndescription: 'A Handbook of Agile Software Craftsmanship'\ncategories: ['Books']\n---\n"
                "### 📖 About the Book\nComprehensive English book review exceeding threshold.\n"
                "{{< book-download url=\"https://dl.theminiceo.ir/books/clean-code.pdf\" title=\"Clean Code\" size=\"10 MB\" format=\"PDF\" lang=\"English\" >}}\n",
                encoding="utf-8",
            )

            # 3. Report page in docs/reports
            reports_dir = tmp / "docs" / "reports"
            reports_dir.mkdir(parents=True)
            r1_fa = reports_dir / "tech-trends-2026.md"
            r1_en = reports_dir / "tech-trends-2026.en.md"
            r1_fa.write_text("---\ntitle: 'روندهای فناوری ۲۰۲۶'\n---\nمتن گزارش فارسی.", encoding="utf-8")
            r1_en.write_text(
                "---\ntitle: 'Tech Trends 2026'\ndate: '2026-10-10'\ndescription: 'Annual technology report'\ncategories: ['Reports']\n---\n"
                "### 📊 Key Insights\nDetailed analysis of 2026 trends exceeding threshold.\n"
                "{{< book-download url=\"https://dl.theminiceo.ir/reports/tech-trends-2026.pdf\" title=\"Tech Trends 2026\" size=\"5 MB\" format=\"PDF\" lang=\"English\" >}}\n",
                encoding="utf-8",
            )

            # 4. Taxonomy category index
            cat_dir = tmp / "categories" / "tech"
            cat_dir.mkdir(parents=True)
            c1_fa = cat_dir / "_index.md"
            c1_en = cat_dir / "_index.en.md"
            c1_fa.write_text("---\ntitle: 'فناوری'\n---\nلیست مقالات فناوری.", encoding="utf-8")
            c1_en.write_text("---\ntitle: 'Technology'\n---\nListing of technology content exceeding fifty bytes threshold.", encoding="utf-8")

            # Run verify_localization.py
            proc = self.run_cli(["--root", str(tmp)])
            self.assertEqual(proc.returncode, 0, f"Expected returncode 0, got {proc.returncode}. Output:\n{proc.stdout}\n{proc.stderr}")
            self.assertIn("SUCCESS", proc.stdout)
            self.assertIn("100%", proc.stdout)

    def test_synthetic_tree_missing_en_file(self):
        """On synthetic tree with 1 missing .en.md file -> verify exit 1."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            p1_fa = tmp / "valid.md"
            p1_en = tmp / "valid.en.md"
            p1_fa.write_text("---\ntitle: 'معتبر'\n---\nبدنه.", encoding="utf-8")
            p1_en.write_text("---\ntitle: 'Valid'\ndate: '2026-10-10'\n---\nValid body text exceeding fifty bytes threshold.", encoding="utf-8")

            # Missing counterpart
            p2_fa = tmp / "untranslated.md"
            p2_fa.write_text("---\ntitle: 'بدون ترجمه'\n---\nفارسی فقط.", encoding="utf-8")

            proc = self.run_cli(["--root", str(tmp)])
            self.assertEqual(proc.returncode, 1, f"Expected exit 1 on missing file, got {proc.returncode}")
            self.assertIn("FAILED", proc.stdout)
            self.assertIn("Missing .en.md files:        1", proc.stdout)

    def test_synthetic_tree_invalid_frontmatter(self):
        """On synthetic tree with invalid frontmatter -> verify exit 1."""
        # Case A: Missing closing delimiter
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            p1_fa = tmp / "doc.md"
            p1_en = tmp / "doc.en.md"
            p1_fa.write_text("---\ntitle: 'تست'\n---\nبدنه.", encoding="utf-8")
            p1_en.write_text("---\ntitle: 'Broken'\ndate: '2026-10-10'\nNo closing delimiter anywhere!", encoding="utf-8")

            proc = self.run_cli(["--root", str(tmp)])
            self.assertEqual(proc.returncode, 1, "Expected exit 1 on unclosed frontmatter")
            self.assertIn("FAILED", proc.stdout)
            self.assertIn("Frontmatter error count:     1", proc.stdout)

        # Case B: Missing required title
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            p1_fa = tmp / "doc.md"
            p1_en = tmp / "doc.en.md"
            p1_fa.write_text("---\ntitle: 'تست'\n---\nبدنه.", encoding="utf-8")
            p1_en.write_text("---\ndate: '2026-10-10'\n---\nValid body content exceeding fifty bytes threshold.", encoding="utf-8")

            proc = self.run_cli(["--root", str(tmp)])
            self.assertEqual(proc.returncode, 1, "Expected exit 1 on missing title")
            self.assertIn("FAILED", proc.stdout)
            self.assertIn("Missing or empty 'title' field", proc.stdout)

        # Case C: Persian characters in English title
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            p1_fa = tmp / "doc.md"
            p1_en = tmp / "doc.en.md"
            p1_fa.write_text("---\ntitle: 'تست'\n---\nبدنه.", encoding="utf-8")
            p1_en.write_text("---\ntitle: 'Book عنوان'\ndate: '2026-10-10'\n---\nValid body content exceeding fifty bytes.", encoding="utf-8")

            proc = self.run_cli(["--root", str(tmp)])
            self.assertEqual(proc.returncode, 1, "Expected exit 1 on Persian in title")
            self.assertIn("FAILED", proc.stdout)
            self.assertIn("Title contains untranslated Persian text", proc.stdout)

        # Case D: Missing description in book
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            books_dir = tmp / "docs" / "books"
            books_dir.mkdir(parents=True)
            b_fa = books_dir / "book1.md"
            b_en = books_dir / "book1.en.md"
            b_fa.write_text("---\ntitle: 'کتاب'\n---\nبدنه.", encoding="utf-8")
            b_en.write_text("---\ntitle: 'Book 1'\ndate: '2026-10-10'\n---\nValid body text exceeding fifty bytes threshold.", encoding="utf-8")

            proc = self.run_cli(["--root", str(tmp)])
            self.assertEqual(proc.returncode, 1, "Expected exit 1 on missing description in book")
            self.assertIn("FAILED", proc.stdout)
            self.assertIn("Missing or empty 'description' field in frontmatter", proc.stdout)

    def test_json_output_schema(self):
        """Test JSON output schema with --json flag."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            p1_fa = tmp / "valid.md"
            p1_en = tmp / "valid.en.md"
            p1_fa.write_text("---\ntitle: 'فارسی'\n---\nبدنه.", encoding="utf-8")
            p1_en.write_text("---\ntitle: 'English'\ndate: '2026-10-10'\n---\nValid English body exceeding fifty bytes threshold.", encoding="utf-8")

            p2_fa = tmp / "missing.md"
            p2_fa.write_text("---\ntitle: 'فاقد'\n---\nبدنه.", encoding="utf-8")

            proc = self.run_cli(["--root", str(tmp), "--json"])
            self.assertEqual(proc.returncode, 1)

            try:
                data = json.loads(proc.stdout)
            except json.JSONDecodeError as e:
                self.fail(f"--json output was not valid JSON: {e}\nRaw output:\n{proc.stdout}")

            expected_keys = {
                "root_dir",
                "is_success",
                "total_issues",
                "total_persian_scanned",
                "total_english_found",
                "missing_count",
                "empty_count",
                "frontmatter_error_count",
                "other_error_count",
                "missing_files",
                "empty_files",
                "frontmatter_errors",
                "other_errors",
            }
            self.assertTrue(expected_keys.issubset(set(data.keys())), f"Missing expected keys in JSON schema: {expected_keys - set(data.keys())}")
            self.assertIsInstance(data["root_dir"], str)
            self.assertIsInstance(data["is_success"], bool)
            self.assertIsInstance(data["total_issues"], int)
            self.assertIsInstance(data["total_persian_scanned"], int)
            self.assertIsInstance(data["total_english_found"], int)
            self.assertIsInstance(data["missing_count"], int)
            self.assertIsInstance(data["empty_count"], int)
            self.assertIsInstance(data["frontmatter_error_count"], int)
            self.assertIsInstance(data["other_error_count"], int)
            self.assertIsInstance(data["missing_files"], list)
            self.assertIsInstance(data["empty_files"], list)
            self.assertIsInstance(data["frontmatter_errors"], list)
            self.assertIsInstance(data["other_errors"], list)

            self.assertFalse(data["is_success"])
            self.assertEqual(data["total_persian_scanned"], 2)
            self.assertEqual(data["total_english_found"], 1)
            self.assertEqual(data["missing_count"], 1)
            self.assertEqual(data["total_issues"], 1)

            # Check structure of items in missing_files list
            item = data["missing_files"][0]
            self.assertIn("file_path", item)
            self.assertIn("issue_type", item)
            self.assertIn("message", item)
            self.assertEqual(item["issue_type"], "missing_counterpart")

    def test_strict_mode_validation(self):
        """Test strict mode --strict validation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            books_dir = tmp / "docs" / "books"
            books_dir.mkdir(parents=True)
            b_fa = books_dir / "clean-code.md"
            b_en = books_dir / "clean-code.en.md"
            b_fa.write_text("---\ntitle: 'کد تمیز'\n---\nبدنه.", encoding="utf-8")

            # 1. Test placeholder detection in strict mode
            b_en.write_text(
                "---\ntitle: 'Clean Code'\ndate: '2026-10-10'\ndescription: 'Desc'\ncategories: ['Books']\n---\n"
                "### 📖 About\nTODO: complete this paragraph.\n"
                "{{< book-download url=\"x\" >}}\n",
                encoding="utf-8",
            )
            # Normal mode should ignore TODO and exit 0
            proc_norm = self.run_cli(["--root", str(tmp)])
            self.assertEqual(proc_norm.returncode, 0, f"Normal mode should pass: {proc_norm.stdout}")

            # Strict mode should flag TODO and exit 1
            proc_strict = self.run_cli(["--root", str(tmp), "--strict"])
            self.assertEqual(proc_strict.returncode, 1, "Strict mode must fail on TODO")
            self.assertIn("Contains dummy placeholder text", proc_strict.stdout)

            # 2. Test missing download shortcode in strict mode
            b_en.write_text(
                "---\ntitle: 'Clean Code'\ndate: '2026-10-10'\ndescription: 'Desc'\ncategories: ['Books']\n---\n"
                "### 📖 About\nClean review text exceeding fifty bytes threshold.\n",
                encoding="utf-8",
            )
            proc_strict2 = self.run_cli(["--root", str(tmp), "--strict"])
            self.assertEqual(proc_strict2.returncode, 1, "Strict mode must fail on missing download shortcode")
            self.assertIn("Missing 'book-download' shortcode", proc_strict2.stdout)

            # 3. Test invalid category in strict mode
            b_en.write_text(
                "---\ntitle: 'Clean Code'\ndate: '2026-10-10'\ndescription: 'Desc'\ncategories: ['Articles']\n---\n"
                "### 📖 About\nClean review text exceeding fifty bytes threshold.\n"
                "{{< book-download url=\"x\" >}}\n",
                encoding="utf-8",
            )
            proc_strict3 = self.run_cli(["--root", str(tmp), "--strict"])
            self.assertEqual(proc_strict3.returncode, 1, "Strict mode must fail on missing 'Books' category")
            self.assertIn("Missing 'Books' category in frontmatter", proc_strict3.stdout)

            # 4. Test invalid date format in strict mode
            b_en.write_text(
                "---\ntitle: 'Clean Code'\ndate: 'October 10, 2026'\ndescription: 'Desc'\ncategories: ['Books']\n---\n"
                "### 📖 About\nClean review text exceeding fifty bytes threshold.\n"
                "{{< book-download url=\"x\" >}}\n",
                encoding="utf-8",
            )
            proc_strict4 = self.run_cli(["--root", str(tmp), "--strict"])
            self.assertEqual(proc_strict4.returncode, 1, "Strict mode must fail on non-ISO date format")
            self.assertIn("is not valid ISO 8601 format", proc_strict4.stdout)

            # 5. When all strict requirements are satisfied, strict mode must exit 0
            b_en.write_text(
                "---\ntitle: 'Clean Code'\ndate: '2026-10-10'\ndescription: 'Desc'\ncategories: ['Books']\n---\n"
                "### 📖 About\nClean review text exceeding fifty bytes threshold.\n"
                "{{< book-download url=\"https://dl.theminiceo.ir/books/clean-code.pdf\" >}}\n",
                encoding="utf-8",
            )
            proc_strict_ok = self.run_cli(["--root", str(tmp), "--strict"])
            self.assertEqual(proc_strict_ok.returncode, 0, f"Strict mode must exit 0 when compliant: {proc_strict_ok.stdout}")
            self.assertIn("SUCCESS", proc_strict_ok.stdout)
            self.assertIn("100%", proc_strict_ok.stdout)


class AdversarialStressAndEdgeCaseTests(unittest.TestCase):
    """Stress tests and boundary condition edge cases."""

    def run_cli(self, args, cwd=None):
        cmd = [sys.executable, str(SCRIPT_PATH)] + args
        return subprocess.run(
            cmd,
            cwd=str(cwd or ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )

    def test_edge_empty_content_directory(self):
        """Empty content directory with 0 files: what is the behavior?"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            proc = self.run_cli(["--root", tmp_dir])
            # Total scanned = 0, total issues = 0 -> is_success = True, exit 0
            self.assertEqual(proc.returncode, 0)
            self.assertIn("Total Persian files scanned: 0", proc.stdout)
            self.assertIn("SUCCESS", proc.stdout)

    def test_edge_nonexistent_directory(self):
        """Nonexistent content directory: flags dir_not_found error and exits 1."""
        proc = self.run_cli(["--root", "/tmp/this_path_does_not_exist_at_all_99999"])
        self.assertEqual(proc.returncode, 1)
        self.assertIn("FAILED", proc.stdout)
        self.assertIn("Content directory does not exist", proc.stdout)

    def test_edge_deeply_nested_unicode_paths(self):
        """Directories with Persian names and nested subdirectories."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            nested = Path(tmp_dir) / "بخش-اول" / "زیرمجموعه"
            nested.mkdir(parents=True)
            fa = nested / "صفحه-اصلی.md"
            en = nested / "صفحه-اصلی.en.md"
            fa.write_text("---\ntitle: 'صفحه اصلی'\n---\nبدنه.", encoding="utf-8")
            en.write_text("---\ntitle: 'Main Page'\ndate: '2026-10-10'\n---\nValid body text exceeding fifty bytes threshold.", encoding="utf-8")

            proc = self.run_cli(["--root", tmp_dir])
            self.assertEqual(proc.returncode, 0)
            self.assertIn("SUCCESS", proc.stdout)

    def test_edge_complex_yaml_multiline_and_quotes(self):
        """YAML with colons in title, quotes, and block scalar descriptions."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            p_fa = Path(tmp_dir) / "complex.md"
            p_en = Path(tmp_dir) / "complex.en.md"
            p_fa.write_text("---\ntitle: 'تست'\n---\nمتن.", encoding="utf-8")
            p_en.write_text(
                '---\n'
                'title: "System Design: Modern Microservices & Distributed Architecture"\n'
                'date: "2026-10-10T12:00:00Z"\n'
                'description: "A detailed overview: covering scaling, fault-tolerance, and design."\n'
                'categories: ["Architecture", "Engineering"]\n'
                '---\n'
                'Body content for complex markdown page exceeding fifty bytes threshold.\n',
                encoding="utf-8",
            )
            proc = self.run_cli(["--root", tmp_dir])
            self.assertEqual(proc.returncode, 0)
            self.assertIn("SUCCESS", proc.stdout)

    def test_edge_toml_frontmatter_support(self):
        """TOML frontmatter parsing (+++ delim)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            p_fa = Path(tmp_dir) / "toml_page.md"
            p_en = Path(tmp_dir) / "toml_page.en.md"
            p_fa.write_text("+++\ntitle = 'تست'\n+++\nمتن.", encoding="utf-8")
            p_en.write_text(
                "+++\n"
                "title = 'TOML Guide'\n"
                "date = '2026-10-10'\n"
                "description = 'Guide to TOML frontmatter'\n"
                "categories = ['Guide']\n"
                "+++\n"
                "Body content for TOML page exceeding fifty bytes threshold.\n",
                encoding="utf-8",
            )
            proc = self.run_cli(["--root", tmp_dir])
            self.assertEqual(proc.returncode, 0)
            self.assertIn("SUCCESS", proc.stdout)

    def test_edge_custom_size_thresholds(self):
        """Custom --min-file-size and --min-body-size flags."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            p_fa = Path(tmp_dir) / "docs" / "books" / "small.md"
            p_en = Path(tmp_dir) / "docs" / "books" / "small.en.md"
            p_fa.parent.mkdir(parents=True)
            p_fa.write_text("---\ntitle: 'کتاب'\n---\nمتن.", encoding="utf-8")
            p_en.write_text(
                "---\ntitle: 'Small'\ndate: '2026-10-10'\ndescription: 'Desc'\n---\nBody is exactly 60 bytes long here and not any longer at all.\n",
                encoding="utf-8",
            )
            # Default body threshold is 50 bytes -> passes
            proc1 = self.run_cli(["--root", tmp_dir])
            self.assertEqual(proc1.returncode, 0)

            # Strict threshold of 200 bytes -> fails
            proc2 = self.run_cli(["--root", tmp_dir, "--min-body-size", "200"])
            self.assertEqual(proc2.returncode, 1)
            self.assertIn("expected > 200 bytes", proc2.stdout)

    def test_edge_combining_characters_nfc_nfd(self):
        """Unicode NFD decomposed combining characters in file paths."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Slug with decomposed Alef + Madda (U+0627 + U+0653)
            nfd_slug = "خلق-محصولات-\u0627\u0653ینده"
            p_fa = Path(tmp_dir) / f"{nfd_slug}.md"
            p_en = Path(tmp_dir) / f"{nfd_slug}.en.md"
            p_fa.write_text("---\ntitle: 'عنوان'\n---\nمتن.", encoding="utf-8")
            p_en.write_text("---\ntitle: 'Creating Future Products'\ndate: '2026-10-10'\n---\nBody text exceeding fifty bytes threshold.", encoding="utf-8")

    def test_edge_unquoted_colon_title(self):
        """Unquoted colons in title like 'title: Book: Subtitle'."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            p_fa = Path(tmp_dir) / "colons.md"
            p_en = Path(tmp_dir) / "colons.en.md"
            p_fa.write_text("---\ntitle: تست\n---\nمتن.", encoding="utf-8")
            p_en.write_text(
                "---\n"
                "title: Book: Subtitle of the Book\n"
                "date: 2026-10-10\n"
                "---\n"
                "Body content exceeding fifty bytes threshold.\n",
                encoding="utf-8",
            )
            proc = self.run_cli(["--root", tmp_dir])
            self.assertEqual(proc.returncode, 0)
            self.assertIn("SUCCESS", proc.stdout)

    def test_edge_empty_frontmatter(self):
        """Empty frontmatter (--- followed immediately by ---) with body > 50 bytes."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            p_fa = Path(tmp_dir) / "empty_fm.md"
            p_en = Path(tmp_dir) / "empty_fm.en.md"
            p_fa.write_text("---\n---\nمتن.", encoding="utf-8")
            p_en.write_text("---\n---\nThis is a sufficiently long body that exceeds the fifty bytes threshold for file size.\n", encoding="utf-8")
            proc = self.run_cli(["--root", tmp_dir])
            self.assertEqual(proc.returncode, 1)
            self.assertIn("Missing or empty 'title'", proc.stdout)

    def test_edge_verbose_flag_with_failures(self):
        """--verbose flag displays all missing files without truncation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            for i in range(25):
                (tmp / f"missing_{i:02d}.md").write_text("---\ntitle: 'تست'\n---\nمتن.", encoding="utf-8")

            # Default non-verbose should show sample and truncation message
            proc_default = self.run_cli(["--root", str(tmp)])
            self.assertEqual(proc_default.returncode, 1)
            self.assertIn("... and 10 more (use --verbose to view all)", proc_default.stdout)

            # Verbose should list all 25 files
            proc_verbose = self.run_cli(["--root", str(tmp), "-v"])
            self.assertEqual(proc_verbose.returncode, 1)
            self.assertNotIn("more (use --verbose to view all)", proc_verbose.stdout)
            for i in range(25):
                self.assertIn(f"missing_{i:02d}.en.md", proc_verbose.stdout)

    def test_edge_non_utf8_encoding_error(self):
        """Files containing invalid UTF-8 bytes should report encoding_error without crashing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            p_fa = Path(tmp_dir) / "bad.md"
            p_en = Path(tmp_dir) / "bad.en.md"
            p_fa.write_text("---\ntitle: 'عنوان'\n---\nمتن.", encoding="utf-8")
            # Write invalid UTF-8 byte sequence with size > 50 bytes
            bad_bytes = b"---\ntitle: 'Test'\ndate: '2026-10-10'\n---\n" + b"\xff\xfe\xfa" * 30
            p_en.write_bytes(bad_bytes)

            proc = self.run_cli(["--root", tmp_dir, "--json"])
            self.assertEqual(proc.returncode, 1)
            data = json.loads(proc.stdout)
            self.assertEqual(data["other_error_count"], 1)
            self.assertEqual(data["other_errors"][0]["issue_type"], "encoding_error")


if __name__ == "__main__":
    unittest.main()

