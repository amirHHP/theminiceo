#!/usr/bin/env python3
"""
scripts/test_verify_localization.py - Unit Test Suite for scripts/verify_localization.py

Uses standard library unittest and tempfile.TemporaryDirectory to rigorously test:
- Frontmatter parsing (YAML, TOML, inline lists, block lists, quotes, colons, UTF-8 BOM, horizontal rules)
- Directory exclusions (content/pdfs/, .obsidian/, _drafts/, hidden files, non-markdown files)
- Language pairing & Persian Unicode slug preservation (including decomposed combining madda)
- Validation rules (title, date, description, non-empty files, body thresholds)
- Strict mode validations (placeholders, categories, download shortcodes, ISO date formatting)
- CLI invocation, flags (--root, --content-dir, --strict, --json, -v, -q), and exit codes (0 vs 1)
"""

import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

# Import functions and classes from scripts/verify_localization.py
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_localization import (
    AuditResult,
    FileIssue,
    audit,
    get_field_str,
    has_persian,
    is_excluded,
    main,
    parse_frontmatter,
)


class TestFrontmatterParsing(unittest.TestCase):
    """Tests for YAML and TOML frontmatter parsing logic."""

    def test_yaml_basic_frontmatter(self):
        content = """---
title: "Product Strategy 101"
date: "2026-09-15"
description: "A comprehensive guide to product strategy"
draft: false
weight: 10
---
This is the body content of the article.
"""
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "yaml")
        self.assertEqual(kv.get("title"), "Product Strategy 101")
        self.assertEqual(kv.get("date"), "2026-09-15")
        self.assertEqual(kv.get("description"), "A comprehensive guide to product strategy")
        self.assertEqual(kv.get("draft"), False)
        self.assertEqual(kv.get("weight"), 10)
        self.assertIn("This is the body content", body)

    def test_yaml_quotes_and_colons_in_title(self):
        content = """---
title: "Webinar: Starting Online Businesses & PM"
subtitle: 'Discovery: A Case Study'
---
Body text.
"""
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "yaml")
        self.assertEqual(kv.get("title"), "Webinar: Starting Online Businesses & PM")
        self.assertEqual(kv.get("subtitle"), "Discovery: A Case Study")

    def test_yaml_inline_arrays(self):
        content = """---
title: "Book Title"
categories: ["Books", "Strategy"]
tags: ["pm", "agile"]
---
Body text.
"""
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "yaml")
        self.assertEqual(kv.get("categories"), ["Books", "Strategy"])
        self.assertEqual(kv.get("tags"), ["pm", "agile"])

    def test_yaml_block_sequence(self):
        content = """---
title: "Book Title"
categories:
  - Books
  - Product Management
tags:
  - lean
  - discovery
---
Body text.
"""
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "yaml")
        self.assertEqual(kv.get("categories"), ["Books", "Product Management"])
        self.assertEqual(kv.get("tags"), ["lean", "discovery"])

    def test_yaml_nested_mappings(self):
        content = """---
title: "Framework Overview"
sidebar:
  exclude: true
  open: false
---
Body text.
"""
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "yaml")
        self.assertEqual(kv.get("title"), "Framework Overview")
        self.assertIsInstance(kv.get("sidebar"), dict)
        self.assertEqual(kv["sidebar"].get("exclude"), True)
        self.assertEqual(kv["sidebar"].get("open"), False)

    def test_toml_basic_and_tables(self):
        content = """+++
date = '2026-09-15T10:00:00+03:30'
draft = false
title = 'Product Management Library'
description = 'Overview of books and resources'
weight = 91

[sidebar]
  open = false
+++
Index page body intro.
"""
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "toml")
        self.assertEqual(kv.get("title"), "Product Management Library")
        self.assertEqual(kv.get("draft"), False)
        self.assertEqual(kv.get("weight"), 91)
        self.assertIn("Index page body intro", body)

    def test_toml_inline_arrays(self):
        content = """+++
title = 'Report Collection'
categories = ["Reports", "Analytics"]
+++
Body text.
"""
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "toml")
        self.assertEqual(kv.get("categories"), ["Reports", "Analytics"])

    def test_utf8_bom_handling(self):
        content = "\ufeff---\ntitle: \"BOM File\"\ndate: \"2026-09-15\"\n---\nBody with BOM."
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "yaml")
        self.assertEqual(kv.get("title"), "BOM File")
        self.assertIn("Body with BOM", body)

    def test_body_with_horizontal_rule(self):
        content = """---
title: "Post with Dividers"
date: "2026-09-15"
---
First section.

---

Second section after divider.
"""
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "yaml")
        self.assertEqual(kv.get("title"), "Post with Dividers")
        self.assertIn("First section.", body)
        self.assertIn("---", body)
        self.assertIn("Second section after divider.", body)

    def test_missing_closing_delimiter(self):
        content = """---
title: "Unclosed Frontmatter"
date: "2026-09-15"
This is never closed!
"""
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "none")
        self.assertEqual(kv, {})

    def test_no_frontmatter(self):
        content = "# Just a Markdown Heading\n\nSome standard markdown text."
        fmt, kv, raw, body = parse_frontmatter(content)
        self.assertEqual(fmt, "none")
        self.assertEqual(kv, {})


class TestDirectoryExclusions(unittest.TestCase):
    """Tests for directory and file exclusion logic."""

    def test_is_excluded_function(self):
        self.assertTrue(is_excluded("content/pdfs/sample.pdf"))
        self.assertTrue(is_excluded("content/pdfs/sub/document.md"))
        self.assertTrue(is_excluded(".obsidian/workspace.json"))
        self.assertTrue(is_excluded("content/.obsidian/app.json"))
        self.assertTrue(is_excluded("content/docs/books/_drafts/growth-hacking.md"))
        self.assertTrue(is_excluded("content/docs/_drafts/sample.md"))
        self.assertTrue(is_excluded(".git/config"))
        self.assertTrue(is_excluded("content/.DS_Store"))
        self.assertFalse(is_excluded("content/docs/books/book1.md"))
        self.assertFalse(is_excluded("content/docs/reports/report1.md"))

    def test_audit_ignores_excluded_directories(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            # Create valid pair in docs/
            docs_dir = tmp / "docs"
            docs_dir.mkdir(parents=True)
            (docs_dir / "valid.md").write_text("---\ntitle: 'عنوان'\n---", encoding="utf-8")
            (docs_dir / "valid.en.md").write_text(
                "---\ntitle: 'Valid Title'\ndate: '2026-09-15'\n---\nValid body exceeding threshold.",
                encoding="utf-8",
            )

            # Create un-paired files in excluded dirs
            pdfs_dir = tmp / "pdfs"
            pdfs_dir.mkdir()
            (pdfs_dir / "sample.pdf").write_bytes(b"%PDF-1.4...")
            (pdfs_dir / "sample.md").write_text("---\ntitle: 'In PDF'\n---", encoding="utf-8")

            obsidian_dir = tmp / ".obsidian"
            obsidian_dir.mkdir()
            (obsidian_dir / "app.json").write_text("{}", encoding="utf-8")

            drafts_dir = tmp / "docs" / "_drafts"
            drafts_dir.mkdir()
            (drafts_dir / "draft1.md").write_text("---\ntitle: 'Draft'\n---", encoding="utf-8")

            # Non-markdown file
            (docs_dir / "helper.py").write_text("print('hello')", encoding="utf-8")
            (docs_dir / ".DS_Store").write_bytes(b"\x00\x00")

            result = audit(content_dir=str(tmp))
            self.assertEqual(result.total_persian_scanned, 1)
            self.assertEqual(result.total_english_found, 1)
            self.assertEqual(result.missing_files, [])
            self.assertTrue(result.is_success)


class TestLanguagePairingAndUnicodeSlugs(unittest.TestCase):
    """Tests for 1-to-1 language pairing and Persian Unicode slugs."""

    def test_standard_ascii_slug_pairing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "guide.md").write_text("---\ntitle: 'راهنما'\n---", encoding="utf-8")
            (tmp / "guide.en.md").write_text(
                "---\ntitle: 'Guide'\ndate: '2026-09-15'\n---\nBody content for guide.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertEqual(result.total_persian_scanned, 1)
            self.assertEqual(result.total_english_found, 1)
            self.assertTrue(result.is_success)

    def test_persian_slug_pairing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            slug = "کتاب-lean-analytics"
            (tmp / f"{slug}.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
            (tmp / f"{slug}.en.md").write_text(
                "---\ntitle: 'Lean Analytics'\ndate: '2026-09-15'\n---\nBody content here.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertEqual(result.total_persian_scanned, 1)
            self.assertEqual(result.total_english_found, 1)
            self.assertTrue(result.is_success)

    def test_persian_slug_decomposed_combining_madda(self):
        """Preserves decomposed combining madda (ا U+0627 + ٓ U+0653) in filenames."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            slug = "خلق-محصولات-آینده-راهنمای-هوش-مصنوعی"
            (tmp / f"{slug}.md").write_text("---\ntitle: 'کتاب هوش مصنوعی'\n---", encoding="utf-8")
            (tmp / f"{slug}.en.md").write_text(
                "---\ntitle: 'Creating Future Products'\ndate: '2026-09-15'\n---\nBody content here.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertEqual(result.total_persian_scanned, 1)
            self.assertEqual(result.total_english_found, 1)
            self.assertTrue(result.is_success)

    def test_missing_counterpart_detection(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "untranslated.md").write_text("---\ntitle: 'بدون ترجمه'\n---", encoding="utf-8")
            result = audit(content_dir=str(tmp))
            self.assertEqual(result.total_persian_scanned, 1)
            self.assertEqual(result.total_english_found, 0)
            self.assertEqual(len(result.missing_files), 1)
            self.assertEqual(result.missing_files[0].issue_type, "missing_counterpart")
            self.assertFalse(result.is_success)


class TestFrontmatterValidation(unittest.TestCase):
    """Tests for frontmatter field validation (title, date, description)."""

    def test_missing_title(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "page.md").write_text("---\ntitle: 'تست'\n---", encoding="utf-8")
            (tmp / "page.en.md").write_text(
                "---\ndate: '2026-09-15'\n---\nValid body text that exceeds the fifty bytes threshold.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.frontmatter_errors if e.issue_type == "missing_title"]
            self.assertEqual(len(errs), 1)

    def test_persian_in_title(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "page.md").write_text("---\ntitle: 'تست'\n---", encoding="utf-8")
            (tmp / "page.en.md").write_text(
                "---\ntitle: 'Product مدیریت'\ndate: '2026-09-15'\n---\nValid body text.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.frontmatter_errors if e.issue_type == "persian_in_title"]
            self.assertEqual(len(errs), 1)

    def test_missing_date_on_content_page(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "article.md").write_text("---\ntitle: 'مقاله'\n---", encoding="utf-8")
            (tmp / "article.en.md").write_text(
                "---\ntitle: 'Article'\n---\nValid body text that exceeds the fifty bytes threshold.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.frontmatter_errors if e.issue_type == "missing_date"]
            self.assertEqual(len(errs), 1)

    def test_date_exempt_on_taxonomy_index(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            cat_dir = tmp / "categories" / "strategy"
            cat_dir.mkdir(parents=True)
            # Persian taxonomy index without date
            (cat_dir / "_index.md").write_text("---\ntitle: 'استراتژی'\n---", encoding="utf-8")
            # English taxonomy index without date
            (cat_dir / "_index.en.md").write_text(
                "---\ntitle: 'Strategy'\n---\nTaxonomy category listing body text exceeding fifty bytes.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertTrue(result.is_success)
            self.assertEqual(result.frontmatter_errors, [])

    def test_date_required_when_persian_has_date(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            cat_dir = tmp / "categories"
            cat_dir.mkdir()
            (cat_dir / "_index.md").write_text("---\ntitle: 'دسته‌ها'\ndate: '2026-09-15'\n---", encoding="utf-8")
            (cat_dir / "_index.en.md").write_text(
                "---\ntitle: 'Categories'\n---\nTaxonomy category listing body text exceeding fifty bytes.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.frontmatter_errors if e.issue_type == "missing_date"]
            self.assertEqual(len(errs), 1)

    def test_description_required_for_books(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            books_dir = tmp / "docs" / "books"
            books_dir.mkdir(parents=True)
            (books_dir / "book1.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
            # English book without description
            (books_dir / "book1.en.md").write_text(
                "---\ntitle: 'Book 1'\ndate: '2026-09-15'\n---\nValid body over 50 bytes for book.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.frontmatter_errors if e.issue_type == "missing_description"]
            self.assertEqual(len(errs), 1)

    def test_description_required_for_reports(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            rep_dir = tmp / "docs" / "reports"
            rep_dir.mkdir(parents=True)
            (rep_dir / "report1.md").write_text("---\ntitle: 'گزارش'\n---", encoding="utf-8")
            # English report without description
            (rep_dir / "report1.en.md").write_text(
                "---\ntitle: 'Report 1'\ndate: '2026-09-15'\n---\nValid body over 50 bytes for report.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.frontmatter_errors if e.issue_type == "missing_description"]
            self.assertEqual(len(errs), 1)

    def test_description_required_when_persian_has_description(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "article.md").write_text(
                "---\ntitle: 'مقاله'\ndescription: 'توضیحات فارسی'\n---",
                encoding="utf-8",
            )
            (tmp / "article.en.md").write_text(
                "---\ntitle: 'Article'\ndate: '2026-09-15'\n---\nValid body text.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.frontmatter_errors if e.issue_type == "missing_description"]
            self.assertEqual(len(errs), 1)

    def test_persian_in_description(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            books_dir = tmp / "docs" / "books"
            books_dir.mkdir(parents=True)
            (books_dir / "book1.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
            (books_dir / "book1.en.md").write_text(
                "---\ntitle: 'Book 1'\ndate: '2026-09-15'\ndescription: 'Book description با متن فارسی'\n---\nValid body text.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.frontmatter_errors if e.issue_type == "persian_in_description"]
            self.assertEqual(len(errs), 1)


class TestContentAndBodyQuality(unittest.TestCase):
    """Tests for file size thresholds and body completeness."""

    def test_empty_file_zero_bytes(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'تست'\n---", encoding="utf-8")
            (tmp / "test.en.md").write_text("", encoding="utf-8")
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.empty_files if e.issue_type == "undersized_file"]
            self.assertEqual(len(errs), 1)

    def test_undersized_file_below_threshold(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'تست'\n---", encoding="utf-8")
            (tmp / "test.en.md").write_text("--- short ---", encoding="utf-8")
            result = audit(content_dir=str(tmp), min_file_size=50)
            self.assertFalse(result.is_success)
            errs = [e for e in result.empty_files if e.issue_type == "undersized_file"]
            self.assertEqual(len(errs), 1)

    def test_whitespace_only_file(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'تست'\n---", encoding="utf-8")
            (tmp / "test.en.md").write_text("   \n\n\t   \n" * 10, encoding="utf-8")
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.empty_files if e.issue_type == "empty_file"]
            self.assertEqual(len(errs), 1)

    def test_empty_body_in_content_page(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "test.md").write_text("---\ntitle: 'تست'\n---", encoding="utf-8")
            (tmp / "test.en.md").write_text(
                "---\ntitle: 'Test Title'\ndate: '2026-09-15'\n---\n   \n",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp))
            self.assertFalse(result.is_success)
            errs = [e for e in result.empty_files if e.issue_type == "empty_body"]
            self.assertEqual(len(errs), 1)

    def test_undersized_body_in_books(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            books_dir = tmp / "docs" / "books"
            books_dir.mkdir(parents=True)
            (books_dir / "b.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
            (books_dir / "b.en.md").write_text(
                "---\ntitle: 'Book'\ndate: '2026-09-15'\ndescription: 'Desc'\n---\nShort body.",
                encoding="utf-8",
            )
            result = audit(content_dir=str(tmp), min_body_size=50)
            self.assertFalse(result.is_success)
            errs = [e for e in result.empty_files if e.issue_type == "undersized_body"]
            self.assertEqual(len(errs), 1)


class TestStrictModeValidations(unittest.TestCase):
    """Tests for strict audit mode (--strict)."""

    def test_strict_mode_placeholder_detection(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "page.md").write_text("---\ntitle: 'مقاله'\n---", encoding="utf-8")
            (tmp / "page.en.md").write_text(
                "---\ntitle: 'Page Title'\ndate: '2026-09-15'\n---\nTODO: finish this section.",
                encoding="utf-8",
            )
            # Standard mode ignores TODO
            std_res = audit(content_dir=str(tmp), strict=False)
            self.assertTrue(std_res.is_success)

            # Strict mode flags TODO
            strict_res = audit(content_dir=str(tmp), strict=True)
            self.assertFalse(strict_res.is_success)
            errs = [e for e in strict_res.other_errors if e.issue_type == "placeholder_text"]
            self.assertEqual(len(errs), 1)

    def test_strict_mode_download_shortcode(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            books_dir = tmp / "docs" / "books"
            books_dir.mkdir(parents=True)
            (books_dir / "b.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
            (books_dir / "b.en.md").write_text(
                "---\ntitle: 'Book'\ndate: '2026-09-15'\ndescription: 'Desc'\ncategories: ['Books']\n---\n"
                + "A full markdown review of the book that spans more than one hundred characters long.\n",
                encoding="utf-8",
            )
            # Strict mode checks book-download shortcode
            strict_res = audit(content_dir=str(tmp), strict=True)
            self.assertFalse(strict_res.is_success)
            errs = [e for e in strict_res.other_errors if e.issue_type == "missing_download_shortcode"]
            self.assertEqual(len(errs), 1)

    def test_strict_mode_book_category(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            books_dir = tmp / "docs" / "books"
            books_dir.mkdir(parents=True)
            (books_dir / "b.md").write_text("---\ntitle: 'کتاب'\n---", encoding="utf-8")
            (books_dir / "b.en.md").write_text(
                "---\ntitle: 'Book'\ndate: '2026-09-15'\ndescription: 'Desc'\ncategories: ['Tech']\n---\n"
                + "A full markdown review of the book with download {{< book-download url=\"x\" >}}.\n",
                encoding="utf-8",
            )
            strict_res = audit(content_dir=str(tmp), strict=True)
            self.assertFalse(strict_res.is_success)
            errs = [e for e in strict_res.frontmatter_errors if e.issue_type == "invalid_category"]
            self.assertEqual(len(errs), 1)

    def test_strict_mode_valid_iso_date(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "page.md").write_text("---\ntitle: 'مقاله'\n---", encoding="utf-8")
            (tmp / "page.en.md").write_text(
                "---\ntitle: 'Page Title'\ndate: 'invalid-date'\n---\nValid body text over fifty bytes.",
                encoding="utf-8",
            )
            strict_res = audit(content_dir=str(tmp), strict=True)
            self.assertFalse(strict_res.is_success)
            errs = [e for e in strict_res.frontmatter_errors if e.issue_type == "invalid_date_format"]
            self.assertEqual(len(errs), 1)


class TestCLIAndExitCodes(unittest.TestCase):
    """Tests for CLI arguments, stdout outputs, and exit codes."""

    def test_clean_directory_exit_zero_and_success_output(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "post.md").write_text("---\ntitle: 'پست'\n---", encoding="utf-8")
            (tmp / "post.en.md").write_text(
                "---\ntitle: 'English Post'\ndate: '2026-09-15'\n---\nValid body content exceeding fifty bytes threshold.",
                encoding="utf-8",
            )
            # Run main directly capturing stdout
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                ret = main(["--content-dir", str(tmp)])
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout

            self.assertEqual(ret, 0)
            self.assertIn("SUCCESS", output)
            self.assertIn("100%", output)

    def test_missing_file_exit_one_and_failure_output(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "missing.md").write_text("---\ntitle: 'فاقد ترجمه'\n---", encoding="utf-8")

            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                ret = main(["--content-dir", str(tmp)])
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout

            self.assertEqual(ret, 1)
            self.assertIn("FAILED", output)

    def test_quiet_flag_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "post.md").write_text("---\ntitle: 'پست'\n---", encoding="utf-8")
            (tmp / "post.en.md").write_text(
                "---\ntitle: 'English Post'\ndate: '2026-09-15'\n---\nValid body content exceeding fifty bytes threshold.",
                encoding="utf-8",
            )
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                ret = main(["--content-dir", str(tmp), "-q"])
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout

            self.assertEqual(ret, 0)
            self.assertIn("SUCCESS", output)
            self.assertIn("100%", output)

    def test_quiet_flag_failure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "missing.md").write_text("---\ntitle: 'فاقد ترجمه'\n---", encoding="utf-8")

            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                ret = main(["--content-dir", str(tmp), "--quiet"])
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout

            self.assertEqual(ret, 1)
            self.assertIn("FAILED: 1 issues detected.", output)

    def test_json_flag_output(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "post.md").write_text("---\ntitle: 'پست'\n---", encoding="utf-8")
            (tmp / "post.en.md").write_text(
                "---\ntitle: 'English Post'\ndate: '2026-09-15'\n---\nValid body content exceeding fifty bytes threshold.",
                encoding="utf-8",
            )
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                ret = main(["--content-dir", str(tmp), "--json"])
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout

            self.assertEqual(ret, 0)
            data = json.loads(output)
            self.assertTrue(data["is_success"])
            self.assertEqual(data["total_issues"], 0)
            self.assertEqual(data["total_persian_scanned"], 1)
            self.assertEqual(data["total_english_found"], 1)

    def test_root_flag_alias(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            (tmp / "post.md").write_text("---\ntitle: 'پست'\n---", encoding="utf-8")
            (tmp / "post.en.md").write_text(
                "---\ntitle: 'English Post'\ndate: '2026-09-15'\n---\nValid body content exceeding fifty bytes threshold.",
                encoding="utf-8",
            )
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                ret = main(["--root", str(tmp), "-q"])
            finally:
                sys.stdout = old_stdout

            self.assertEqual(ret, 0)

    def test_nonexistent_directory(self):
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            ret = main(["--content-dir", "/nonexistent/path/xyz"])
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

        self.assertEqual(ret, 1)
        self.assertIn("FAILED", output)


if __name__ == "__main__":
    unittest.main()
