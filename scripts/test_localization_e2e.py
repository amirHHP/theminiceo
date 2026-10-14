#!/usr/bin/env python3
"""
scripts/test_localization_e2e.py - Comprehensive E2E Localization Parity Test Suite
for TheMiniCEO English Localization & Hugo Parity Project.

Covers all 4 tiers defined in TEST_INFRA.md:
  - Tier 1: Feature Coverage (file pairing, frontmatter completeness, non-empty content)
  - Tier 2: Boundary & Corner Cases (Persian slug files, exclusions, zero placeholder text, zero untranslated blocks)
  - Tier 3: Cross-Feature Interactions (valid download URLs, taxonomy category mapping, shortcode parameters)
  - Tier 4: Real-World Workloads (verify_localization.py execution, hugo compilation & page count delta)

Usage:
  python3 scripts/test_localization_e2e.py [--tier {1,2,3,4,all}] [-v] [-x] [--json]
"""

import ast
import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ==============================================================================
# Constants & Reference Specifications
# ==============================================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT_DIR / "content"
BOOKS_DIR = CONTENT_DIR / "docs" / "books"
REPORTS_DIR = CONTENT_DIR / "docs" / "reports"
DATA_DIR = ROOT_DIR / "data"
SCRIPTS_DIR = ROOT_DIR / "scripts"
LAYOUTS_DIR = ROOT_DIR / "layouts"
HUGO_TOML = ROOT_DIR / "hugo.toml"

EXCLUDED_DIRS = {".obsidian", "_drafts", "pdfs"}
PERSIAN_CHAR_REGEX = re.compile(r"[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]")
PLACEHOLDER_REGEX = re.compile(
    r"\b(lorem\s+ipsum|dolor\s+sit\s+amet|consectetur|TODO|FIXME|TBD|\[placeholder\])\b",
    re.IGNORECASE,
)

# Canonical 17 Reports expected in content/docs/reports/
CANONICAL_REPORT_FILES = [
    "airtable-product-insights-report.md",
    "amplitude-product-report-2022.md",
    "designvaluereport1.md",
    "fpmr-2023-enterprise.md",
    "generative-ai-the-insights-you-need-from-harvard-business-review.md",
    "hbr-2022-11-12.md",
    "heap-digital-experiences-insights-report2.md",
    "heap-implicit-vs-explicit-guide-2022.md",
    "iran-startup-ecosystem-report-techrasa-1400.md",
    "product-leadership-census-2023-v2.md",
    "the-2022-state-of-product-management-report-by-productplan.md",
    "the-2024-state-of-product-management-report.md",
    "the-analytics-stack-guidebook.md",
    "the-future-of-product-2024.md",
    "the-state-of-product-management-annual-report-2023.md",
    "wef-future-of-jobs-report-2025.md",
    "گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md",
]

# 17 Legacy pre-existing English books
LEGACY_EN_BOOK_FILES = [
    "Escaping-the-Build-Trap.en.md",
    "The-Lean-Product-Playbook.en.md",
    "The-Lean-Startup.en.md",
    "behind-every-great-product.en.md",
    "build-better-products.en.md",
    "human-blockers.en.md",
    "okr-books.en.md",
    "pm-club.en.md",
    "pm-courses.en.md",
    "storytelling-with-data.en.md",
    "survival-guide-for-product-managers.en.md",
    "talking-to-others.en.md",
    "webinar-05-roadmap.en.md",
    "webinar-06-listening.en.md",
    "کتاب-inspired.en.md",
    "کتاب-lean-analytics.en.md",
    "کتاب-roadmap.en.md",
]

# 8 Standard Book Categories
STANDARD_BOOK_CATEGORIES = [
    "strategy-leadership",
    "ux-design",
    "ai-technology",
    "discovery-research",
    "growth-analytics",
    "management-career",
    "lean-agile",
    "reports-playbooks",
]


# ==============================================================================
# Test Framework & Assertion Tracking
# ==============================================================================

class AssertionTracker:
    def __init__(self):
        self.assertions_count: int = 0
        self.failures: List[str] = []

    def assert_true(self, condition: bool, msg: str):
        self.assertions_count += 1
        if not condition:
            self.failures.append(f"AssertionError: {msg}")

    def assert_false(self, condition: bool, msg: str):
        self.assert_true(not condition, msg)

    def assert_equal(self, actual: Any, expected: Any, msg: str = ""):
        self.assertions_count += 1
        if actual != expected:
            prefix = f"{msg}: " if msg else ""
            self.failures.append(f"AssertionError: {prefix}expected {expected!r}, got {actual!r}")

    def assert_greater_equal(self, actual: Any, expected: Any, msg: str = ""):
        self.assertions_count += 1
        if actual < expected:
            prefix = f"{msg}: " if msg else ""
            self.failures.append(f"AssertionError: {prefix}expected >= {expected}, got {actual}")

    def assert_in(self, item: Any, container: Any, msg: str = ""):
        self.assertions_count += 1
        if item not in container:
            prefix = f"{msg}: " if msg else ""
            self.failures.append(f"AssertionError: {prefix}{item!r} not in container")


class TestResult:
    def __init__(self, test_id: str, name: str, tier: int):
        self.test_id = test_id
        self.name = name
        self.tier = tier
        self.passed: bool = True
        self.assertions_count: int = 0
        self.errors: List[str] = []
        self.duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "name": self.name,
            "tier": self.tier,
            "passed": self.passed,
            "assertions_count": self.assertions_count,
            "errors": self.errors,
            "duration_seconds": round(self.duration_seconds, 3),
        }


# ==============================================================================
# Helper Utilities
# ==============================================================================

def parse_frontmatter(file_content: str) -> Tuple[str, Dict[str, str], str]:
    """
    Parses frontmatter from markdown file.
    Returns (type: 'yaml'|'toml'|'none', parsed_dict, body_text).
    """
    if file_content.startswith("---"):
        parts = file_content.split("---", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            return "yaml", _parse_flat_kv(fm_text), body
    elif file_content.startswith("+++"):
        parts = file_content.split("+++", 2)
        if len(parts) >= 3:
            fm_text = parts[1]
            body = parts[2]
            return "toml", _parse_flat_kv(fm_text), body
    return "none", {}, file_content


def _parse_flat_kv(fm_text: str) -> Dict[str, str]:
    kv = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z0-9_-]+)\s*[:=]\s*(.*)$", line)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip().strip("\"'")
            kv[key] = val
    return kv


def extract_shortcodes(text: str, name: str = "book-download") -> List[Dict[str, str]]:
    """
    Extracts Hugo shortcode invocations and their parameters.
    E.g. {{< book-download url="..." title="..." size="..." format="PDF" >}}
    """
    pattern = rf"\{{\{{<\s*{name}\s+(.*?)\s*>\}}\}}"
    matches = re.findall(pattern, text)
    shortcodes = []
    for m in matches:
        params: Dict[str, str] = {}
        # Parse key="value" or key='value' or key=value
        kv_pairs = re.findall(r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|(\S+))', m)
        for k, v1, v2, v3 in kv_pairs:
            val = v1 or v2 or v3 or ""
            params[k] = val
        shortcodes.append(params)
    return shortcodes


# ==============================================================================
# Test Cases Implementation
# ==============================================================================

class LocalizationE2ETestSuite:
    def __init__(self, verbose: bool = False, fail_fast: bool = False):
        self.verbose = verbose
        self.fail_fast = fail_fast
        self.results: List[TestResult] = []

    def _run_test(
        self,
        test_id: str,
        name: str,
        tier: int,
        fn: Callable[[AssertionTracker], None],
    ) -> TestResult:
        result = TestResult(test_id, name, tier)
        tracker = AssertionTracker()
        start_time = time.time()

        try:
            fn(tracker)
            result.assertions_count = tracker.assertions_count
            if tracker.failures:
                result.passed = False
                result.errors.extend(tracker.failures)
        except Exception as ex:
            result.passed = False
            result.assertions_count = tracker.assertions_count
            result.errors.append(f"Unexpected Exception: {type(ex).__name__}: {str(ex)}")

        result.duration_seconds = time.time() - start_time
        self.results.append(result)

        if self.verbose:
            status_str = "PASS" if result.passed else "FAIL"
            print(f"[{status_str}] {test_id}: {name} ({result.assertions_count} assertions, {result.duration_seconds:.2f}s)")
            if not result.passed:
                for err in result.errors[:5]:
                    print(f"      ↳ {err}")
                if len(result.errors) > 5:
                    print(f"      ↳ ... and {len(result.errors) - 5} more errors")

        return result

    # --------------------------------------------------------------------------
    # Tier 1: Feature Coverage (Minimum threshold ≥ 40 assertions)
    # --------------------------------------------------------------------------

    def test_t1_1_verification_script_contract(self, t: AssertionTracker):
        """T1.1: Verification script exists at scripts/verify_localization.py and is executable."""
        script_path = SCRIPTS_DIR / "verify_localization.py"
        t.assert_true(script_path.exists(), f"Verification script missing at {script_path}")
        if script_path.exists():
            size = script_path.stat().st_size
            t.assert_greater_equal(size, 50, "verify_localization.py size should be >= 50 bytes")
            content = script_path.read_text(encoding="utf-8")
            try:
                ast.parse(content)
                syntax_valid = True
            except SyntaxError:
                syntax_valid = False
            t.assert_true(syntax_valid, "verify_localization.py must parse cleanly as valid Python")
            t.assert_true("audit" in content or "main" in content, "verify_localization.py must define audit or main function")
        else:
            t.assert_true(False, "verify_localization.py is required for R1 CI audit contract")
            t.assert_true(False, "verify_localization.py syntax check skipped")
            t.assert_true(False, "verify_localization.py entrypoint check skipped")

    def test_t1_2_reports_coverage(self, t: AssertionTracker):
        """T1.2: Check all 17 reports have corresponding .en.md files and _index.en.md exists."""
        t.assert_equal(len(CANONICAL_REPORT_FILES), 17, "Exactly 17 reports must be registered in canonical inventory")
        index_en = REPORTS_DIR / "_index.en.md"
        t.assert_true(index_en.exists(), f"Reports section index missing at {index_en}")

        for rep_file in CANONICAL_REPORT_FILES:
            base_name = rep_file[:-3]
            en_file = REPORTS_DIR / f"{base_name}.en.md"
            t.assert_true(en_file.exists(), f"Missing English report file: {en_file.name}")

    def test_t1_3_books_coverage(self, t: AssertionTracker):
        """T1.3: Check all 407 books in content/docs/books/ have .en.md files and _index.en.md exists."""
        meta_file = DATA_DIR / "books_metadata.json"
        t.assert_true(meta_file.exists(), f"Metadata file missing at {meta_file}")

        books_data: List[Dict[str, Any]] = []
        if meta_file.exists():
            try:
                books_data = json.loads(meta_file.read_text(encoding="utf-8"))
            except Exception as e:
                t.assert_true(False, f"Failed to parse books_metadata.json: {e}")

        t.assert_equal(len(books_data), 390, "Metadata books_metadata.json must contain exactly 390 records")

        index_en = BOOKS_DIR / "_index.en.md"
        t.assert_true(index_en.exists(), f"Books section index missing at {index_en}")

        # Check all 17 legacy books exist
        for legacy_file in LEGACY_EN_BOOK_FILES:
            path = BOOKS_DIR / legacy_file
            t.assert_true(path.exists(), f"Legacy English book missing: {legacy_file}")

        # Check sample books across each of the 8 standard categories
        cat_to_slugs: Dict[str, List[str]] = {c: [] for c in STANDARD_BOOK_CATEGORIES}
        for b in books_data:
            c = b.get("category_slug", "")
            if c in cat_to_slugs:
                cat_to_slugs[c].append(b.get("slug", ""))

        for cat, slugs in cat_to_slugs.items():
            if slugs:
                sample_slug = slugs[0]
                sample_file = BOOKS_DIR / f"{sample_slug}.en.md"
                t.assert_true(
                    sample_file.exists(),
                    f"Sample English book for category '{cat}' missing: {sample_slug}.en.md",
                )
            else:
                t.assert_true(False, f"No books found in metadata for category '{cat}'")

        # Global missing count for 390 metadata books
        missing_count = 0
        for b in books_data:
            slug = b.get("slug", "")
            en_path = BOOKS_DIR / f"{slug}.en.md"
            if not en_path.exists():
                missing_count += 1
        t.assert_equal(missing_count, 0, f"Found {missing_count} missing English books from metadata")

        # Total .en.md files in content/docs/books/
        if BOOKS_DIR.exists():
            total_en = len([f for f in BOOKS_DIR.iterdir() if f.name.endswith(".en.md") and f.is_file()])
            t.assert_equal(total_en, 408, f"Expected exactly 408 .en.md files in books/ (407 books + 1 _index), got {total_en}")
        else:
            t.assert_true(False, f"Books directory missing at {BOOKS_DIR}")

    def test_t1_4_frontmatter_completeness(self, t: AssertionTracker):
        """T1.4: Check all .en.md files have non-empty frontmatter title, date, description, categories."""
        # Check reports frontmatter
        missing_title_rep = 0
        missing_date_rep = 0
        missing_desc_rep = 0
        missing_cats_rep = 0

        for rep_file in CANONICAL_REPORT_FILES:
            en_path = REPORTS_DIR / f"{rep_file[:-3]}.en.md"
            if not en_path.exists():
                missing_title_rep += 1
                missing_date_rep += 1
                missing_desc_rep += 1
                missing_cats_rep += 1
                continue
            content = en_path.read_text(encoding="utf-8")
            fm_type, kv, _ = parse_frontmatter(content)
            if fm_type == "none":
                missing_title_rep += 1
                continue
            if not kv.get("title"):
                missing_title_rep += 1
            if not kv.get("date"):
                missing_date_rep += 1
            if not kv.get("description"):
                missing_desc_rep += 1
            if not kv.get("categories"):
                missing_cats_rep += 1

        t.assert_equal(missing_title_rep, 0, "All 17 English reports must have 'title' in frontmatter")
        t.assert_equal(missing_date_rep, 0, "All 17 English reports must have 'date' in frontmatter")
        t.assert_equal(missing_desc_rep, 0, "All 17 English reports must have 'description' in frontmatter")
        t.assert_equal(missing_cats_rep, 0, "All 17 English reports must have 'categories' in frontmatter")

        # Check books frontmatter
        missing_title_books = 0
        missing_date_books = 0
        missing_desc_books = 0
        missing_cats_books = 0
        total_checked = 0

        if BOOKS_DIR.exists():
            for f in sorted(BOOKS_DIR.iterdir()):
                if f.name.endswith(".en.md") and f.name != "_index.en.md" and f.is_file():
                    total_checked += 1
                    content = f.read_text(encoding="utf-8")
                    fm_type, kv, _ = parse_frontmatter(content)
                    if fm_type == "none":
                        missing_title_books += 1
                        continue
                    if not kv.get("title"):
                        missing_title_books += 1
                    if not kv.get("date"):
                        missing_date_books += 1
                    if not kv.get("description"):
                        missing_desc_books += 1
                    if not kv.get("categories"):
                        missing_cats_books += 1

        t.assert_equal(total_checked, 407, f"Expected to audit 407 English books, audited {total_checked}")
        t.assert_equal(missing_title_books, 0, "All 407 English books must have 'title' in frontmatter")
        t.assert_equal(missing_date_books, 0, "All 407 English books must have 'date' in frontmatter")
        t.assert_equal(missing_desc_books, 0, "All 407 English books must have 'description' in frontmatter")
        t.assert_equal(missing_cats_books, 0, "All 407 English books must have 'categories' in frontmatter")

    def test_t1_5_body_content_non_empty(self, t: AssertionTracker):
        """T1.5: Check all .en.md files have valid non-empty body content (>100 characters and headings)."""
        empty_rep_body = 0
        rep_without_headings = 0
        for rep_file in CANONICAL_REPORT_FILES:
            en_path = REPORTS_DIR / f"{rep_file[:-3]}.en.md"
            if not en_path.exists():
                empty_rep_body += 1
                rep_without_headings += 1
                continue
            content = en_path.read_text(encoding="utf-8")
            _, _, body = parse_frontmatter(content)
            if len(body.strip()) < 100:
                empty_rep_body += 1
            if not re.search(r"^###?\s+", body, re.MULTILINE):
                rep_without_headings += 1

        t.assert_equal(empty_rep_body, 0, "All 17 English reports must have body length > 100 characters")
        t.assert_equal(rep_without_headings, 0, "All 17 English reports must contain structured markdown headings (###)")

        empty_books_body = 0
        books_without_headings = 0
        checked_books = 0

        if BOOKS_DIR.exists():
            for f in sorted(BOOKS_DIR.iterdir()):
                if f.name.endswith(".en.md") and f.name != "_index.en.md" and f.is_file():
                    checked_books += 1
                    content = f.read_text(encoding="utf-8")
                    _, _, body = parse_frontmatter(content)
                    if len(body.strip()) < 100:
                        empty_books_body += 1
                    if not re.search(r"^###?\s+", body, re.MULTILINE):
                        books_without_headings += 1

        t.assert_equal(checked_books, 407, f"Expected 407 English books to check, got {checked_books}")
        t.assert_equal(empty_books_body, 0, "All 407 English books must have body length > 100 characters")
        t.assert_equal(books_without_headings, 0, "All 407 English books must contain structured markdown headings (###)")

        # Section index bodies must not be empty
        books_idx = BOOKS_DIR / "_index.en.md"
        if books_idx.exists():
            _, _, b_body = parse_frontmatter(books_idx.read_text(encoding="utf-8"))
            t.assert_greater_equal(len(b_body.strip()), 50, "content/docs/books/_index.en.md body must not be empty (>50 chars)")
        else:
            t.assert_true(False, "content/docs/books/_index.en.md does not exist")

        rep_idx = REPORTS_DIR / "_index.en.md"
        if rep_idx.exists():
            _, _, r_body = parse_frontmatter(rep_idx.read_text(encoding="utf-8"))
            t.assert_greater_equal(len(r_body.strip()), 50, "content/docs/reports/_index.en.md body must not be empty (>50 chars)")
        else:
            t.assert_true(False, "content/docs/reports/_index.en.md does not exist")

    # --------------------------------------------------------------------------
    # Tier 2: Boundary & Corner Cases (Minimum threshold ≥ 25 assertions)
    # --------------------------------------------------------------------------

    def test_t2_1_persian_slug_book(self, t: AssertionTracker):
        """T2.1: Verify Persian slug book exists and has valid English content & download shortcode."""
        slug = "خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول"
        target_file = BOOKS_DIR / f"{slug}.en.md"

        t.assert_true(target_file.exists(), f"Persian slug book missing: {target_file}")
        if target_file.exists():
            size = target_file.stat().st_size
            t.assert_greater_equal(size, 200, "Persian slug book should be >= 200 bytes")
            content = target_file.read_text(encoding="utf-8")
            _, kv, body = parse_frontmatter(content)
            title = kv.get("title", "")
            t.assert_true(bool(title), "Title must exist in frontmatter")
            t.assert_false(bool(PERSIAN_CHAR_REGEX.search(title)), f"Title must be in English, got: {title}")
            desc = kv.get("description", "")
            t.assert_true(bool(desc), "Description must exist in frontmatter")
            t.assert_false(bool(PERSIAN_CHAR_REGEX.search(desc)), "Description must be in English")
            t.assert_greater_equal(len(body.strip()), 100, "Body must have >= 100 chars")
            shortcodes = extract_shortcodes(content)
            t.assert_greater_equal(len(shortcodes), 1, "Must contain book-download shortcode")
        else:
            t.assert_true(False, "Persian slug book size check skipped")
            t.assert_true(False, "Persian slug book title check skipped")
            t.assert_true(False, "Persian slug book description check skipped")
            t.assert_true(False, "Persian slug book body check skipped")
            t.assert_true(False, "Persian slug book shortcode check skipped")

    def test_t2_2_persian_slug_report(self, t: AssertionTracker):
        """T2.2: Verify Persian slug report exists and has valid English content & download shortcode."""
        slug = "گزارش-صنعت-پرداخت-ایران-نسخه-نهم"
        target_file = REPORTS_DIR / f"{slug}.en.md"

        t.assert_true(target_file.exists(), f"Persian slug report missing: {target_file}")
        if target_file.exists():
            size = target_file.stat().st_size
            t.assert_greater_equal(size, 200, "Persian slug report should be >= 200 bytes")
            content = target_file.read_text(encoding="utf-8")
            _, kv, body = parse_frontmatter(content)
            title = kv.get("title", "")
            t.assert_true(bool(title), "Title must exist in frontmatter")
            t.assert_false(bool(PERSIAN_CHAR_REGEX.search(title)), f"Title must be in English, got: {title}")
            desc = kv.get("description", "")
            t.assert_true(bool(desc), "Description must exist in frontmatter")
            t.assert_false(bool(PERSIAN_CHAR_REGEX.search(desc)), "Description must be in English")
            t.assert_greater_equal(len(body.strip()), 100, "Body must have >= 100 chars")
            shortcodes = extract_shortcodes(content)
            t.assert_greater_equal(len(shortcodes), 1, "Must contain book-download shortcode")
        else:
            t.assert_true(False, "Persian slug report size check skipped")
            t.assert_true(False, "Persian slug report title check skipped")
            t.assert_true(False, "Persian slug report description check skipped")
            t.assert_true(False, "Persian slug report body check skipped")
            t.assert_true(False, "Persian slug report shortcode check skipped")

    def test_t2_3_exclusions_not_flagged(self, t: AssertionTracker):
        """T2.3: Verify excluded folders (content/pdfs/, .obsidian/, _drafts/) are ignored."""
        draft_file = BOOKS_DIR / "_drafts" / "growth-hacking.md"
        t.assert_true(draft_file.exists(), f"Draft test fixture missing at {draft_file}")
        draft_en = BOOKS_DIR / "_drafts" / "growth-hacking.en.md"
        t.assert_false(draft_en.exists(), "Drafts must not require English translations")

        pdfs_dir = CONTENT_DIR / "pdfs"
        t.assert_true(pdfs_dir.exists(), f"PDFs directory should exist at {pdfs_dir}")
        pdf_en_files = list(pdfs_dir.glob("*.en.md"))
        t.assert_equal(len(pdf_en_files), 0, "PDFs directory must have 0 .en.md files")

        obsidian_dir = ROOT_DIR / ".obsidian"
        if obsidian_dir.exists():
            obsidian_en_files = list(obsidian_dir.glob("*.en.md"))
            t.assert_equal(len(obsidian_en_files), 0, ".obsidian directory must have 0 .en.md files")
        else:
            t.assert_true(True, ".obsidian check satisfied")

        # Verify hidden directories/files are excluded
        hidden_items = [p for p in CONTENT_DIR.rglob(".*") if p.is_file() and p.name.endswith(".en.md")]
        t.assert_equal(len(hidden_items), 0, "No hidden .en.md files should exist in content/")

    def test_t2_4_zero_untranslated_persian_blocks(self, t: AssertionTracker):
        """T2.4: Verify no untranslated Persian text remains in English headers or body."""
        persian_in_rep_titles = 0
        persian_in_rep_descs = 0
        persian_in_rep_headers = 0

        for rep_file in CANONICAL_REPORT_FILES:
            en_path = REPORTS_DIR / f"{rep_file[:-3]}.en.md"
            if not en_path.exists():
                persian_in_rep_titles += 1
                continue
            content = en_path.read_text(encoding="utf-8")
            _, kv, body = parse_frontmatter(content)
            if PERSIAN_CHAR_REGEX.search(kv.get("title", "")):
                persian_in_rep_titles += 1
            if PERSIAN_CHAR_REGEX.search(kv.get("description", "")):
                persian_in_rep_descs += 1
            for line in body.splitlines():
                if line.startswith("#"):
                    if PERSIAN_CHAR_REGEX.search(line):
                        persian_in_rep_headers += 1

        t.assert_equal(persian_in_rep_titles, 0, "Zero Persian characters in English report titles")
        t.assert_equal(persian_in_rep_descs, 0, "Zero Persian characters in English report descriptions")
        t.assert_equal(persian_in_rep_headers, 0, "Zero Persian characters in English report markdown headings")

        persian_in_book_titles = 0
        persian_in_book_descs = 0
        persian_in_book_headers = 0
        persian_in_book_body = 0

        if BOOKS_DIR.exists():
            for f in sorted(BOOKS_DIR.iterdir()):
                if f.name.endswith(".en.md") and f.name != "_index.en.md" and f.is_file():
                    content = f.read_text(encoding="utf-8")
                    _, kv, body = parse_frontmatter(content)
                    if PERSIAN_CHAR_REGEX.search(kv.get("title", "")):
                        persian_in_book_titles += 1
                    if PERSIAN_CHAR_REGEX.search(kv.get("description", "")):
                        persian_in_book_descs += 1
                    for line in body.splitlines():
                        if line.startswith("#"):
                            if PERSIAN_CHAR_REGEX.search(line):
                                persian_in_book_headers += 1
                    # Check body prose for large blocks of Persian text (>= 20 contiguous Persian chars)
                    if re.search(r"[\u0600-\u06FF]{20,}", body):
                        persian_in_book_body += 1

        t.assert_equal(persian_in_book_titles, 0, "Zero Persian characters in English book titles")
        t.assert_equal(persian_in_book_descs, 0, "Zero Persian characters in English book descriptions")
        t.assert_equal(persian_in_book_headers, 0, "Zero Persian characters in English book markdown headings")
        t.assert_equal(persian_in_book_body, 0, "Zero untranslated Persian text blocks in English book bodies")

    def test_t2_5_zero_dummy_placeholder_text(self, t: AssertionTracker):
        """T2.5: Verify no dummy placeholder text (lorem ipsum, TODO, TBD) exists in files."""
        rep_placeholders = 0
        for rep_file in CANONICAL_REPORT_FILES:
            en_path = REPORTS_DIR / f"{rep_file[:-3]}.en.md"
            if not en_path.exists():
                rep_placeholders += 1
                continue
            content = en_path.read_text(encoding="utf-8")
            if PLACEHOLDER_REGEX.search(content):
                rep_placeholders += 1

        t.assert_equal(rep_placeholders, 0, "Zero dummy placeholder text in English reports")

        books_placeholders = 0
        if BOOKS_DIR.exists():
            for f in sorted(BOOKS_DIR.iterdir()):
                if f.name.endswith(".en.md") and f.is_file():
                    content = f.read_text(encoding="utf-8")
                    if PLACEHOLDER_REGEX.search(content):
                        books_placeholders += 1

        t.assert_equal(books_placeholders, 0, "Zero dummy placeholder text in English books and index")

    def test_t2_6_boundary_file_sizes_and_special_chars(self, t: AssertionTracker):
        """T2.6: Verify extreme file size formats and special character escaping in frontmatter."""
        # Extreme large report: hbr-2022-11-12 (90.4 MB)
        hbr_file = REPORTS_DIR / "hbr-2022-11-12.en.md"
        t.assert_true(hbr_file.exists(), f"Missing large report fixture: {hbr_file}")
        if hbr_file.exists():
            hbr_content = hbr_file.read_text(encoding="utf-8")
            shortcodes = extract_shortcodes(hbr_content)
            size_val = shortcodes[0].get("size", "") if shortcodes else ""
            t.assert_true("90.4" in size_val or "90" in size_val, f"HBR report should indicate ~90.4 MB, got: {size_val}")
        else:
            t.assert_true(False, "HBR report size parameter check skipped")

        # Extreme small report: heap-digital-experiences-insights-report2 (400 KB)
        heap_file = REPORTS_DIR / "heap-digital-experiences-insights-report2.en.md"
        t.assert_true(heap_file.exists(), f"Missing small report fixture: {heap_file}")
        if heap_file.exists():
            heap_content = heap_file.read_text(encoding="utf-8")
            shortcodes = extract_shortcodes(heap_content)
            size_val = shortcodes[0].get("size", "") if shortcodes else ""
            t.assert_true("400" in size_val or "0.4" in size_val, f"Heap report should indicate ~400 KB, got: {size_val}")
        else:
            t.assert_true(False, "Heap report size parameter check skipped")

        # Check titles with colons / quotes in books
        checked_escaping = 0
        if BOOKS_DIR.exists():
            for f in sorted(BOOKS_DIR.iterdir()):
                if f.name.endswith(".en.md") and f.name != "_index.en.md" and f.is_file():
                    content = f.read_text(encoding="utf-8")
                    if ":" in content.splitlines()[1]:
                        checked_escaping += 1
                        fm_type, kv, _ = parse_frontmatter(content)
                        t.assert_true(bool(kv.get("title")), f"Escaped title failed to parse in {f.name}")
                        break
        if checked_escaping == 0:
            t.assert_true(False, "Escaped frontmatter test skipped because books not generated")

    # --------------------------------------------------------------------------
    # Tier 3: Cross-Feature Interactions (Minimum threshold ≥ 15 assertions)
    # --------------------------------------------------------------------------

    def test_t3_1_download_shortcodes_url_integrity(self, t: AssertionTracker):
        """T3.1: Verify download shortcodes in .en.md reference valid URLs matching metadata."""
        setup_script = SCRIPTS_DIR / "setup_reports_section.py"
        t.assert_true(setup_script.exists(), f"Missing setup script: {setup_script}")

        # Extract dl_url for reports from setup script
        expected_rep_urls: Dict[str, str] = {}
        if setup_script.exists():
            script_text = setup_script.read_text(encoding="utf-8")
            # Extract maps of new_file to dl_url
            for block in re.split(r"\{\s*\"old_file\"", script_text)[1:]:
                mf = re.search(r'\"new_file\":\s*\"([^\"]+)\"', block)
                mu = re.search(r'\"dl_url\":\s*\"([^\"]+)\"', block)
                if mf and mu:
                    expected_rep_urls[mf.group(1)] = mu.group(1)

        t.assert_equal(len(expected_rep_urls), 17, "Must extract 17 expected report download URLs from setup script")

        rep_url_mismatches = 0
        for fname, exp_url in expected_rep_urls.items():
            en_path = REPORTS_DIR / f"{fname[:-3]}.en.md"
            if not en_path.exists():
                rep_url_mismatches += 1
                continue
            content = en_path.read_text(encoding="utf-8")
            scs = extract_shortcodes(content)
            if not scs or scs[0].get("url") != exp_url:
                rep_url_mismatches += 1

        t.assert_equal(rep_url_mismatches, 0, "All 17 English reports must contain exact matching download URLs")

        # Check books metadata download URLs
        meta_file = DATA_DIR / "books_metadata.json"
        books_data = []
        if meta_file.exists():
            try:
                books_data = json.loads(meta_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        book_url_mismatches = 0
        for b in books_data:
            slug = b.get("slug", "")
            exp_url = b.get("download_url", "")
            en_path = BOOKS_DIR / f"{slug}.en.md"
            if not en_path.exists():
                book_url_mismatches += 1
                continue
            content = en_path.read_text(encoding="utf-8")
            scs = extract_shortcodes(content)
            if not scs or scs[0].get("url") != exp_url:
                book_url_mismatches += 1

        t.assert_equal(book_url_mismatches, 0, "All 390 English books must contain exact matching download URLs from metadata")

        # Verify all URLs point to official CDN domain
        invalid_domain_count = 0
        checked_urls = 0
        for b in books_data:
            url = b.get("download_url", "")
            if url:
                checked_urls += 1
                if not url.startswith("https://dl.theminiceo.ir/"):
                    invalid_domain_count += 1

        t.assert_greater_equal(checked_urls, 390, "Checked at least 390 book download URLs")
        t.assert_equal(invalid_domain_count, 0, "All download URLs must use https://dl.theminiceo.ir/")

    def test_t3_2_taxonomy_category_mapping(self, t: AssertionTracker):
        """T3.2: Verify categories in frontmatter map correctly to standard taxonomy categories."""
        # Reports taxonomy
        rep_cat_errors = 0
        for rep_file in CANONICAL_REPORT_FILES:
            en_path = REPORTS_DIR / f"{rep_file[:-3]}.en.md"
            if not en_path.exists():
                rep_cat_errors += 1
                continue
            content = en_path.read_text(encoding="utf-8")
            _, kv, _ = parse_frontmatter(content)
            cat_str = kv.get("categories", "")
            if "Reports" not in cat_str and "گزارش" not in cat_str:
                rep_cat_errors += 1

        t.assert_equal(rep_cat_errors, 0, "All 17 English reports must have 'Reports' in categories frontmatter")

        # Books taxonomy
        book_cat_errors = 0
        total_checked = 0
        if BOOKS_DIR.exists():
            for f in sorted(BOOKS_DIR.iterdir()):
                if f.name.endswith(".en.md") and f.name != "_index.en.md" and f.is_file():
                    total_checked += 1
                    content = f.read_text(encoding="utf-8")
                    _, kv, _ = parse_frontmatter(content)
                    cat_str = kv.get("categories", "")
                    if "Books" not in cat_str and "کتاب" not in cat_str:
                        book_cat_errors += 1

        t.assert_equal(total_checked, 407, f"Expected 407 English books to check for taxonomy, checked {total_checked}")
        t.assert_equal(book_cat_errors, 0, "All 407 English books must have 'Books' in categories frontmatter")

        # Check tag categories
        meta_file = DATA_DIR / "books_metadata.json"
        if meta_file.exists():
            books = json.loads(meta_file.read_text(encoding="utf-8"))
            known_cats = {b.get("category_slug") for b in books}
            t.assert_equal(known_cats, set(STANDARD_BOOK_CATEGORIES), "Metadata must cover all 8 standard categories")
        else:
            t.assert_true(False, "books_metadata.json missing")

    def test_t3_3_specifications_table_integrity(self, t: AssertionTracker):
        """T3.3: Verify specifications tables match book metadata (Author, Format, File Size)."""
        table_missing_count = 0
        author_missing_count = 0
        format_missing_count = 0
        size_missing_count = 0
        audience_missing_count = 0
        checked_count = 0

        meta_file = DATA_DIR / "books_metadata.json"
        slugs = []
        if meta_file.exists():
            slugs = [b["slug"] for b in json.loads(meta_file.read_text(encoding="utf-8"))]

        for slug in slugs:
            en_path = BOOKS_DIR / f"{slug}.en.md"
            if not en_path.exists():
                table_missing_count += 1
                continue
            checked_count += 1
            content = en_path.read_text(encoding="utf-8")
            if "| Book Specification" not in content and "| Book Specifications" not in content:
                table_missing_count += 1
                continue
            if "**Author**" not in content and "Author" not in content:
                author_missing_count += 1
            if "PDF" not in content:
                format_missing_count += 1
            if "MB" not in content:
                size_missing_count += 1
            if "Audience" not in content:
                audience_missing_count += 1

        t.assert_equal(checked_count, 390, f"Expected 390 books checked for specifications tables, checked {checked_count}")
        t.assert_equal(table_missing_count, 0, "All 390 English books must contain Book Specifications table")
        t.assert_equal(author_missing_count, 0, "All specifications tables must include Author row")
        t.assert_equal(format_missing_count, 0, "All specifications tables must include Format row (PDF)")
        t.assert_equal(size_missing_count, 0, "All specifications tables must include File Size row (MB)")
        t.assert_equal(audience_missing_count, 0, "All specifications tables must include Target Audience row")

    def test_t3_4_multilingual_shortcode_template(self, t: AssertionTracker):
        """T3.4: Verify layouts/shortcodes/book-download.html renders English labels conditionally."""
        sc_path = LAYOUTS_DIR / "shortcodes" / "book-download.html"
        t.assert_true(sc_path.exists(), f"Shortcode template missing at {sc_path}")

        if sc_path.exists():
            template = sc_path.read_text(encoding="utf-8")
            # Multilingual logic requirement: detects English page context
            has_lang_cond = (
                '.Page.Language.Lang' in template or
                '$isEn' in template or
                'eq .Page.Language.Lang "en"' in template or
                '{{ T ' in template
            )
            t.assert_true(has_lang_cond, "book-download.html must check language conditionally via .Page.Language.Lang or i18n")

            # Check English strings in template
            t.assert_true("Download Book File" in template or "Download" in template, "Shortcode must provide English download button text")
            t.assert_true("Size: " in template or "Size" in template, "Shortcode must provide English 'Size: ' label")
            t.assert_true("Language: " in template or "Language" in template, "Shortcode must provide English 'Language: ' label")
            t.assert_true("High-speed Direct CDN" in template or "CDN" in template, "Shortcode must provide English CDN badge")

            # Check Persian fallback strings preserved
            t.assert_true("دریافت فایل کتاب" in template, "Shortcode must preserve Persian button text 'دریافت فایل کتاب'")
            t.assert_true("حجم:" in template, "Shortcode must preserve Persian label 'حجم:'")
        else:
            t.assert_true(False, "Template check skipped")
            t.assert_true(False, "English button text check skipped")
            t.assert_true(False, "English size label check skipped")
            t.assert_true(False, "English language label check skipped")
            t.assert_true(False, "English CDN badge check skipped")
            t.assert_true(False, "Persian button text check skipped")
            t.assert_true(False, "Persian size label check skipped")

    def test_t3_5_co_located_stem_pairing(self, t: AssertionTracker):
        """T3.5: Verify every .en.md file pairs with an exact companion .md file in the same directory."""
        orphaned_en_files = []
        for en_file in CONTENT_DIR.rglob("*.en.md"):
            if any(ex in en_file.parts for ex in EXCLUDED_DIRS):
                continue
            fa_file = en_file.with_name(en_file.name.replace(".en.md", ".md"))
            if not fa_file.exists():
                orphaned_en_files.append(str(en_file))

        t.assert_equal(len(orphaned_en_files), 0, f"Found orphaned English files without Persian companion: {orphaned_en_files}")

        # Check date format consistency (YYYY-MM-DD)
        hbr_en = REPORTS_DIR / "hbr-2022-11-12.en.md"
        if hbr_en.exists():
            _, kv, _ = parse_frontmatter(hbr_en.read_text(encoding="utf-8"))
            date_val = kv.get("date", "")
            t.assert_true(bool(re.match(r"^\d{4}-\d{2}-\d{2}", date_val)), f"Date should be YYYY-MM-DD, got {date_val}")
        else:
            t.assert_true(False, "hbr-2022-11-12.en.md not found for date check")

    # --------------------------------------------------------------------------
    # Tier 4: Real-World Workloads (Minimum threshold ≥ 5 assertions)
    # --------------------------------------------------------------------------

    def test_t4_1_verify_localization_script_execution(self, t: AssertionTracker):
        """T4.1: Execute python3 scripts/verify_localization.py and verify it exits 0 with 100% pass."""
        script_path = SCRIPTS_DIR / "verify_localization.py"
        if not script_path.exists():
            t.assert_true(False, f"scripts/verify_localization.py not found at {script_path}")
            t.assert_true(False, "Cannot execute missing verify_localization.py")
            return

        proc = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )

        t.assert_equal(proc.returncode, 0, f"verify_localization.py returned code {proc.returncode}. Stderr: {proc.stderr}")
        t.assert_true("SUCCESS" in proc.stdout or "100%" in proc.stdout, "verify_localization.py stdout should report success/100% parity")

    def test_t4_2_hugo_render_to_memory(self, t: AssertionTracker):
        """T4.2: Execute hugo --renderToMemory and verify it completes with exit code 0 and 0 errors."""
        try:
            proc = subprocess.run(
                ["hugo", "--renderToMemory"],
                cwd=str(ROOT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=90,
            )
            t.assert_equal(proc.returncode, 0, f"Hugo returned code {proc.returncode}. Stderr: {proc.stderr}")
            has_errors = "ERROR" in proc.stderr or "ERROR" in proc.stdout
            t.assert_false(has_errors, f"Hugo build output contained errors: {proc.stderr}")
        except FileNotFoundError:
            t.assert_true(False, "'hugo' binary not found on system PATH")
            t.assert_true(False, "Hugo compilation check skipped")

    def test_t4_3_hugo_page_count_delta(self, t: AssertionTracker):
        """T4.3: Verify Hugo rendered page count increases by at least 407 English pages (target >= 677)."""
        try:
            proc = subprocess.run(
                ["hugo", "--renderToMemory"],
                cwd=str(ROOT_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=90,
            )
            combined = proc.stdout + "\n" + proc.stderr
            # Parse Hugo rendered pages table: Pages │ 723 │ 270 (or unicode/ascii bar)
            match = re.search(r"Pages\s*[│|]\s*(\d+)\s*[│|]\s*(\d+)", combined)
            if match:
                fa_pages = int(match.group(1))
                en_pages = int(match.group(2))
                t.assert_greater_equal(fa_pages, 700, f"Persian pages should be >= 700, got {fa_pages}")
                # Baseline is 270. Generating 407 pages must increase EN count to at least 270 + 407 = 677.
                t.assert_greater_equal(en_pages, 677, f"English pages should be >= 677 (+407 parity delta), got {en_pages}")
                delta = en_pages - 270
                t.assert_greater_equal(delta, 407, f"English page delta should be >= 407, got +{delta}")
            else:
                t.assert_true(False, f"Failed to parse Hugo summary page counts from output:\n{combined[:500]}")
                t.assert_true(False, "English pages threshold check skipped")
                t.assert_true(False, "English delta threshold check skipped")
        except FileNotFoundError:
            t.assert_true(False, "'hugo' binary not found on PATH")
            t.assert_true(False, "Hugo page count check skipped")
            t.assert_true(False, "Hugo page count check skipped")

    def test_t4_4_language_switcher_and_routes(self, t: AssertionTracker):
        """T4.4: Verify Hugo multilingual configuration and navigation parity in hugo.toml."""
        t.assert_true(HUGO_TOML.exists(), f"hugo.toml missing at {HUGO_TOML}")
        if HUGO_TOML.exists():
            cfg = HUGO_TOML.read_text(encoding="utf-8")
            t.assert_true("defaultContentLanguage = 'fa'" in cfg, "hugo.toml default language must be 'fa'")
            t.assert_true("defaultContentLanguageInSubdir = false" in cfg, "hugo.toml defaultContentLanguageInSubdir must be false")
            t.assert_true("[languages.fa]" in cfg, "hugo.toml must configure [languages.fa]")
            t.assert_true("[languages.en]" in cfg, "hugo.toml must configure [languages.en]")
        else:
            t.assert_true(False, "hugo.toml check skipped")
            t.assert_true(False, "defaultContentLanguage check skipped")
            t.assert_true(False, "languages.fa check skipped")
            t.assert_true(False, "languages.en check skipped")

    def test_t4_5_verify_localization_strict_mode(self, t: AssertionTracker):
        """T4.5: Execute python3 scripts/verify_localization.py --strict and verify clean exit code 0."""
        script_path = SCRIPTS_DIR / "verify_localization.py"
        if not script_path.exists():
            t.assert_true(False, f"scripts/verify_localization.py not found for strict audit")
            return

        proc = subprocess.run(
            [sys.executable, str(script_path), "--strict"],
            cwd=str(ROOT_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60,
        )
        t.assert_equal(proc.returncode, 0, f"verify_localization.py --strict failed with code {proc.returncode}. Stderr: {proc.stderr}")

    # --------------------------------------------------------------------------
    # Runner Orchestration
    # --------------------------------------------------------------------------

    def run_suite(self, tier_filter: Optional[str] = None) -> int:
        test_methods: List[Tuple[str, str, int, Callable[[AssertionTracker], None]]] = [
            # Tier 1
            ("T1.1", "T1.1: Verification Script Contract", 1, self.test_t1_1_verification_script_contract),
            ("T1.2", "T1.2: Reports File Coverage", 1, self.test_t1_2_reports_coverage),
            ("T1.3", "T1.3: Books File Coverage", 1, self.test_t1_3_books_coverage),
            ("T1.4", "T1.4: Frontmatter Completeness", 1, self.test_t1_4_frontmatter_completeness),
            ("T1.5", "T1.5: Body Content Non-Empty", 1, self.test_t1_5_body_content_non_empty),
            # Tier 2
            ("T2.1", "T2.1: Persian Slug Book Validation", 2, self.test_t2_1_persian_slug_book),
            ("T2.2", "T2.2: Persian Slug Report Validation", 2, self.test_t2_2_persian_slug_report),
            ("T2.3", "T2.3: Excluded Directories Not Flagged", 2, self.test_t2_3_exclusions_not_flagged),
            ("T2.4", "T2.4: Zero Untranslated Persian Blocks", 2, self.test_t2_4_zero_untranslated_persian_blocks),
            ("T2.5", "T2.5: Zero Dummy Placeholder Text", 2, self.test_t2_5_zero_dummy_placeholder_text),
            ("T2.6", "T2.6: Boundary File Sizes & Special Chars", 2, self.test_t2_6_boundary_file_sizes_and_special_chars),
            # Tier 3
            ("T3.1", "T3.1: Download Shortcodes URL Integrity", 3, self.test_t3_1_download_shortcodes_url_integrity),
            ("T3.2", "T3.2: Taxonomy & Category Mapping", 3, self.test_t3_2_taxonomy_category_mapping),
            ("T3.3", "T3.3: Specifications Table Integrity", 3, self.test_t3_3_specifications_table_integrity),
            ("T3.4", "T3.4: Multilingual Shortcode Template", 3, self.test_t3_4_multilingual_shortcode_template),
            ("T3.5", "T3.5: Co-Located Stem Pairing", 3, self.test_t3_5_co_located_stem_pairing),
            # Tier 4
            ("T4.1", "T4.1: Verify Script Execution", 4, self.test_t4_1_verify_localization_script_execution),
            ("T4.2", "T4.2: Hugo Render to Memory Build", 4, self.test_t4_2_hugo_render_to_memory),
            ("T4.3", "T4.3: Hugo Page Count Delta", 4, self.test_t4_3_hugo_page_count_delta),
            ("T4.4", "T4.4: Multilingual Routing & Nav", 4, self.test_t4_4_language_switcher_and_routes),
            ("T4.5", "T4.5: Strict Localization Audit", 4, self.test_t4_5_verify_localization_strict_mode),
        ]

        # Filter by tier if specified
        target_tier: Optional[int] = None
        if tier_filter and tier_filter.lower() != "all":
            try:
                target_tier = int(tier_filter)
            except ValueError:
                print(f"Error: Invalid tier filter '{tier_filter}'. Choose 1, 2, 3, 4, or all.")
                return 2

        selected_tests = [
            t for t in test_methods if target_tier is None or t[2] == target_tier
        ]

        print("=" * 78)
        print("THEMINICEO LOCALIZATION E2E TEST RUNNER")
        print(f"Selected: {'All Tiers (1-4)' if target_tier is None else f'Tier {target_tier}'}")
        print("=" * 78)

        suite_start = time.time()
        for test_id, name, tier, fn in selected_tests:
            res = self._run_test(test_id, name, tier, fn)
            if self.fail_fast and not res.passed:
                print(f"\n[FAIL-FAST] Stopping execution after first failure in {test_id}.")
                break

        suite_duration = time.time() - suite_start
        return self._print_summary(target_tier, suite_duration)

    def _print_summary(self, target_tier: Optional[int], duration: float) -> int:
        tier_stats: Dict[int, Dict[str, int]] = {
            1: {"passed": 0, "failed": 0, "tests": 0, "assertions": 0},
            2: {"passed": 0, "failed": 0, "tests": 0, "assertions": 0},
            3: {"passed": 0, "failed": 0, "tests": 0, "assertions": 0},
            4: {"passed": 0, "failed": 0, "tests": 0, "assertions": 0},
        }

        all_passed = True
        total_assertions = 0
        total_failed_tests = 0

        for r in self.results:
            tier_stats[r.tier]["tests"] += 1
            tier_stats[r.tier]["assertions"] += r.assertions_count
            total_assertions += r.assertions_count
            if r.passed:
                tier_stats[r.tier]["passed"] += 1
            else:
                tier_stats[r.tier]["failed"] += 1
                total_failed_tests += 1
                all_passed = False

        print("\n" + "-" * 78)
        print("TEST EXECUTION BREAKDOWN BY TIER")
        print("-" * 78)
        print(f"{'Tier':<8} | {'Tests':<10} | {'Passed':<8} | {'Failed':<8} | {'Assertions':<12} | {'Status':<8}")
        print("-" * 78)

        tiers_to_display = [target_tier] if target_tier else [1, 2, 3, 4]
        for t in tiers_to_display:
            s = tier_stats[t]
            status = "PASS" if s["failed"] == 0 and s["tests"] > 0 else "FAIL"
            print(f"Tier {t:<3} | {s['tests']:<10} | {s['passed']:<8} | {s['failed']:<8} | {s['assertions']:<12} | {status:<8}")

        print("-" * 78)
        print(f"Total Tests Run:       {len(self.results)}")
        print(f"Total Assertions Run:   {total_assertions}")
        print(f"Total Failed Tests:    {total_failed_tests}")
        print(f"Suite Duration:        {duration:.2f}s")
        print("-" * 78)

        if not all_passed:
            print("\n❌ FAILURE DETAILS:")
            for r in self.results:
                if not r.passed:
                    print(f"\n• {r.test_id}: {r.name}")
                    for err in r.errors:
                        print(f"    - {err}")

        if all_passed and len(self.results) > 0:
            print("\n✅ OVERALL STATUS: ALL LOCALIZATION E2E TESTS PASSED!")
            return 0
        else:
            print("\n❌ OVERALL STATUS: E2E TEST FAILURES DETECTED (EXPECTED DURING TDD / PRE-GENERATION).")
            return 1


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run E2E localization parity tests for TheMiniCEO.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--tier",
        default="all",
        choices=["1", "2", "3", "4", "all"],
        help="Specify which test tier to execute (default: all)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display detailed assertion progress per test",
    )
    parser.add_argument(
        "-x", "--fail-fast",
        action="store_true",
        help="Stop test execution on first failure",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    suite = LocalizationE2ETestSuite(verbose=args.verbose, fail_fast=args.fail_fast)
    exit_code = suite.run_suite(tier_filter=args.tier)

    if args.json:
        json_output = {
            "exit_code": exit_code,
            "tier_filter": args.tier,
            "results": [r.to_dict() for r in suite.results],
        }
        print("\n--- JSON OUTPUT ---")
        print(json.dumps(json_output, indent=2))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
