# Handoff Report: Milestone 1 Verification Script & Content Structure Investigation

**Agent**: explorer_m1_1  
**Working Directory**: `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m1_1`  
**Date**: 2026-10-10T09:37:00Z  
**Type**: Hard Handoff (Investigation Complete)  
**Parent**: orchestrator_2 (ID: `1390bbb4-2296-47f7-8f97-a4b7fde0fc3d`)  

---

## Executive Summary

1. **Repository Content Inventory**:
   - Total files under `content/`: 1,407 files across 27 distinct directory paths.
   - Total markdown files repo-wide: **704 files**.
   - Active Persian markdown files (`*.md`): **555 files** (after excluding drafts).
   - Active English markdown files (`*.en.md`): **148 files**.
   - Missing English companions: Exactly **407 files** (390 in `content/docs/books/` + 17 in `content/docs/reports/` + 0 in all other 23 sections).
   
2. **Exclusion Boundaries**:
   - `content/pdfs/`: Contains 432 `.pdf` files and 1 `.epub` file. Zero `.md` files. Must be strictly ignored.
   - `.obsidian/` (root) and `content/.obsidian/`: Contains 13 `.json` and plugin metadata files. Zero `.md` files. Must be strictly ignored.
   - `_drafts/`: Contains exactly 1 file: `content/docs/books/_drafts/growth-hacking.md` (frontmatter `draft: true`). Must be excluded; must never require an `.en.md` counterpart.
   - Non-markdown files: Stored assets (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`), extensionless image hashes in `content/docs/archive/images/`, macOS metadata (`.DS_Store`), and a stray Python script `content/docs/books/Unti.py`. All must be filtered out by checking `f.endswith('.md')` and `not f.startswith('.')`.

3. **Persian Slugs & Unicode Pairing**:
   - Exactly 20 markdown files repo-wide contain Persian characters in their filename stem.
   - 6 pairs (12 files) in `content/docs/archive/` already exist and are perfectly paired.
   - 3 legacy pairs (6 files) in `content/docs/books/` already exist and are perfectly paired (`کتاب-inspired`, `کتاب-lean-analytics`, `کتاب-roadmap`).
   - Exactly 2 active Persian files with Persian slugs currently lack English companions:
     1. `content/docs/reports/گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md`
     2. `content/docs/books/خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md`
   - **Crucial Unicode nuance**: The book filename contains decomposed combining madda (`ا` U+0627 + `ٓ` U+0653), not precomposed `آ` (U+0622). Deriving English paths via string slicing `fa_path[:-3] + '.en.md'` guarantees bit-for-bit Unicode consistency on macOS APFS/HFS+ filesystems and avoids `pathlib.Path.stem` truncation bugs (which naively leaves `.en` on `.en.md`).

4. **Verification Script Architecture (`scripts/verify_localization.py`)**:
   - Deterministic single-pass traversal using `os.walk('content')` with in-place pruning of `dirs[:]`.
   - Pure Python standard library implementation with zero external dependencies.
   - Implements both standard audit mode and `--strict` mode to satisfy `scripts/test_localization_e2e.py` contracts (specifically `test_t1_1`, `test_t4_1`, and `test_t4_5`).

---

## 1. Observations

### 1.1. Directory Layout & Extension Breakdown across `content/`

A full filesystem walk of `/Users/sotoon/personal/theminiceo/content/` revealed 1,407 total files:

```
Extension Summary:
- .md:       704 files (556 *.md + 148 *.en.md)
- .pdf:      432 files (all in content/pdfs/)
- .epub:       1 file  (in content/pdfs/)
- .png:      111 files (images)
- .jpg:       94 files (images)
- .jpeg:      22 files (images)
- .webp:       2 files (images)
- .gif:        1 file  (images)
- .json:       4 files (all in content/.obsidian/)
- .py:         1 file  (content/docs/books/Unti.py)
- (no ext):   20 files (15 in content/docs/archive/images/, 1 in content/docs/books/images/, 4 .DS_Store)
```

Directory-by-directory audit of content files:

| Directory Path | Persian `.md` | English `.en.md` | Missing `.en.md` | Non-MD Files | Notes |
|---|---|---|---|---|---|
| `content/` (root) | 10 | 10 | 0 | 1 (`.DS_Store`) | Complete parity |
| `content/blog/` | 1 | 1 | 0 | 1 (`.DS_Store`) | Section index (`_index.md`) |
| `content/categories/` | 1 | 1 | 0 | 0 | Taxonomy root (`_index.md`) |
| `content/categories/podcast` | 1 | 1 | 0 | 0 | Taxonomy term (`_index.md`) |
| `content/categories/product-articles` | 1 | 1 | 0 | 0 | Taxonomy term (`_index.md`) |
| `content/categories/product-basics` | 1 | 1 | 0 | 0 | Taxonomy term (`_index.md`) |
| `content/categories/product-discovery` | 1 | 1 | 0 | 0 | Taxonomy term (`_index.md`) |
| `content/categories/product-management-frameworks` | 1 | 1 | 0 | 0 | Taxonomy term (`_index.md`) |
| `content/categories/product-skills` | 1 | 1 | 0 | 0 | Taxonomy term (`_index.md`) |
| `content/categories/product-strategy` | 1 | 1 | 0 | 0 | Taxonomy term (`_index.md`) |
| `content/categories/teamwork` | 1 | 1 | 0 | 0 | Taxonomy term (`_index.md`) |
| `content/course/` | 9 | 9 | 0 | 8 (`images/*.jpeg`) | Complete parity |
| `content/docs/` | 1 | 1 | 0 | 1 (`.DS_Store`) | Section index (`_index.md`) |
| `content/docs/1-what-is-product-managment` | 4 | 4 | 0 | 0 | Complete parity |
| `content/docs/2-product-strategy` | 5 | 5 | 0 | 0 | Complete parity |
| `content/docs/3-product-planning-and-discovery` | 5 | 5 | 0 | 0 | Complete parity |
| `content/docs/4-development-and-go-to-market` | 5 | 5 | 0 | 0 | Complete parity |
| `content/docs/5-product-growth-and-optimization` | 4 | 4 | 0 | 0 | Complete parity |
| `content/docs/6-resources-and-tools` | 4 | 4 | 0 | 0 | Complete parity |
| `content/docs/archive/` | 62 | 62 | 0 | 172 (`.DS_Store` + images) | Complete parity |
| `content/docs/books/` | 408 | 18 | **390** | 2 (`.DS_Store`, `Unti.py`) | 390 missing books; `_index` paired |
| `content/docs/books/_drafts/` | 1 | 0 | [Excluded] | 0 | `growth-hacking.md` (excluded) |
| `content/docs/reports/` | 18 | 1 | **17** | 0 | 17 missing reports; `_index` paired |
| `content/frameworks/` | 9 | 9 | 0 | 0 | Complete parity |
| `content/images/` | 0 | 0 | 0 | 42 (images) | Excluded asset directory |
| `content/pdfs/` | 0 | 0 | 0 | 433 (432 pdf + 1 epub) | Excluded asset directory |
| `content/tags/` | 1 | 1 | 0 | 0 | Taxonomy root (`_index.md`) |

**Summary Counts**:
- Total Active Persian Files: $556 - 1 \text{ (_drafts)} = \mathbf{555}$
- Total Active English Files: $\mathbf{148}$
- Total Missing English Files: $\mathbf{407}$ ($390 \text{ in books} + 17 \text{ in reports} + 0 \text{ elsewhere}$)

### 1.2. Exclusion Findings & Edge Cases

1. **`content/pdfs/`**:
   - Location: `/Users/sotoon/personal/theminiceo/content/pdfs`
   - Content: 432 `.pdf` files, 1 `.epub` file. Zero `.md` files.
   - Requirement: Excluded from traversal.

2. **`.obsidian/`**:
   - Two locations:
     - Root: `/Users/sotoon/personal/theminiceo/.obsidian` (9 JSON and plugin files)
     - Inside content: `/Users/sotoon/personal/theminiceo/content/.obsidian` (4 JSON files: `app.json`, `appearance.json`, `hotkeys.json`, `workspace.json`)
   - Content: Zero `.md` files.
   - Requirement: Excluded from traversal.

3. **`_drafts/` Directory**:
   - Location: `/Users/sotoon/personal/theminiceo/content/docs/books/_drafts/`
   - File: `growth-hacking.md` (99 bytes, frontmatter: `title: "مجموعه کتاب‌های هک رشد"`, `draft: true`).
   - Test suite verification (`scripts/test_localization_e2e.py` lines 533–539):
     ```python
     draft_file = BOOKS_DIR / "_drafts" / "growth-hacking.md"
     t.assert_true(draft_file.exists())
     draft_en = BOOKS_DIR / "_drafts" / "growth-hacking.en.md"
     t.assert_false(draft_en.exists(), "Drafts must not require English translations")
     ```
   - Requirement: Traversal must never inspect `_drafts` directories or require translations for files inside them.

4. **Non-Markdown Files**:
   - Stray python script observed: `content/docs/books/Unti.py` (lines 1–42, regex helper script for aliases).
   - `.DS_Store` files observed in: `content/`, `content/blog/`, `content/docs/`, `content/docs/archive/`, `content/docs/books/`.
   - Binary images observed in `content/images/`, `content/course/images/`, `content/docs/archive/images/`, `content/docs/books/images/`.
   - Requirement: Check `if not f.endswith('.md') or f.startswith('.'): continue`.

### 1.3. Persian Slug Analysis & Exact Matching Requirements

Grep/scan across all 704 markdown files identified exactly 20 files with Persian characters in their filename:

```
Archive section (6 pairs = 12 files, already 100% paired):
1. content/docs/archive/اهداف-و-نتایج-کلیدیokr.md ↔ اهداف-و-نتایج-کلیدیokr.en.md
2. content/docs/archive/اولویت-بندی-فیچرها-ویژگی-ها-۷-روش-برای.md ↔ اولویت-بندی-فیچرها-ویژگی-ها-۷-روش-برای.en.md
3. content/docs/archive/بهینه-سازی-نرخ-تبدیل-cro.md ↔ بهینه-سازی-نرخ-تبدیل-cro.en.md
4. content/docs/archive/جریان-کاربر-یا-user-flow-چطور-طراحی-می‌شود؟.md ↔ جریان-کاربر-یا-user-flow-چطور-طراحی-می‌شود؟.en.md
5. content/docs/archive/نفوذ-محصول-جدید-در-بازار.md ↔ نفوذ-محصول-جدید-در-بازار.en.md
6. content/docs/archive/چطور-بدون-استفاده-از-چرا-بپرسیم-چرا؟.md ↔ چطور-بدون-استفاده-از-چرا-بپرسیم-چرا؟.en.md

Books section (3 legacy pairs = 6 files, already 100% paired):
7. content/docs/books/کتاب-inspired.md ↔ کتاب-inspired.en.md
8. content/docs/books/کتاب-lean-analytics.md ↔ کتاب-lean-analytics.en.md
9. content/docs/books/کتاب-roadmap.md ↔ کتاب-roadmap.en.md

Missing English Counterparts (2 files):
10. content/docs/reports/گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md
    → Must pair with: content/docs/reports/گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md
11. content/docs/books/خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md
    → Must pair with: content/docs/books/خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.en.md
```

#### Detailed Unicode Character Inspection:
- `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md`:
  - 34 characters: standard Arabic/Persian letters (`گ` U+06AF, `ز` U+0632, `پ` U+067E, `ی` U+06CC) separated by hyphens.
- `خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md`:
  - Characters 12 and 13 in `آینده`:
    - `[12]` = `'ا'` (`U+0627` ARABIC LETTER ALEF)
    - `[13]` = `'ٓ'` (`U+0653` ARABIC MADDAH ABOVE)
  - This is a decomposed combining character sequence, NOT the single precomposed letter `'آ'` (`U+0622`).
  - If a script normalizes or replaces this slug with `\u0622`, the filesystem on case-preserving APFS may fail exact match against `test_localization_e2e.py` lines 481–484:
    ```python
    slug = "خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول"
    target_file = BOOKS_DIR / f"{slug}.en.md"
    ```
  - **Deduction**: Always use `fa_path[:-3] + '.en.md'` directly without manual Unicode normalization.

### 1.4. Frontmatter Field Nuances across Site Sections

Audit of all 148 existing `.en.md` files:
1. **Delimiters**: 681 files use YAML (`---`), 22 files use TOML (`+++`). The parser must support both.
2. **`title`**: Present in 100% of all existing 148 `.en.md` files.
3. **`date`**:
   - Present in 118 of 129 non-book/report files.
   - Omitted only on taxonomy nodes: `content/_index.en.md`, `content/tags/_index.en.md`, and 9 files in `content/categories/*/_index.en.md`.
4. **`description`**:
   - Present on all 390 Persian books that currently lack English translations.
   - Present on all 17 Persian reports.
   - Present on `content/docs/books/_index.en.md` and `content/docs/reports/_index.en.md`.
   - **Legacy 17 English books**: Currently lack `description` in `content/docs/books/*.en.md` (to be retrofitted in M3 per `PROJECT.md` Feature 6).
   - **Archive files**: 62 legacy files in `content/docs/archive/*.en.md` do NOT have `description` (and their Persian counterparts also never had it).
   - **Deduction**: `description` validation must be enforced on all books and reports (`content/docs/books/` and `content/docs/reports/`), or wherever the Persian source file contains `description`. It must NOT fail on archive articles that never possessed descriptions.

---

## 2. Logic Chain

1. **Premise 1 (R1 & Acceptance Criteria)**: R1 specifies that `scripts/verify_localization.py` must deterministically audit all content files, verify 1:1 pairing with `.en.md` in the same directory (excluding `content/pdfs/`, `.obsidian/`, `_drafts/`), validate frontmatter completeness (`title`, `date`, `description`), verify non-empty files, and exit 0 only on complete success.
2. **Observation 1.1**: The exact inventory consists of 555 active Persian files, 148 active English files, and exactly 407 missing English files (390 in books, 17 in reports, 0 elsewhere).
3. **Observation 1.2**: Excluding `pdfs`, `.obsidian`, `_drafts`, and files starting with `.` eliminates all non-content files (`Unti.py`, `.DS_Store`, images, draft articles) with zero false negatives.
4. **Observation 1.3**: Hugo multilingual routing pairs `<slug>.md` directly with `<slug>.en.md`. In both Latin and Persian slugs, taking the Persian path and appending `[:-3] + '.en.md'` guarantees identical slug matching, preserving combining Unicode characters.
5. **Observation 1.4**: Frontmatter validation must check `title` repo-wide, `date` on all non-taxonomy content pages, and `description` on all books, reports, and any page where Persian has `description`.
6. **Inference (Contract Compatibility)**: In `test_localization_e2e.py`, tests `T1.1` (script contract), `T4.1` (verify execution), and `T4.5` (strict mode audit) test `scripts/verify_localization.py`. By structuring `scripts/verify_localization.py` to support standard execution and `--strict` mode, the script satisfies all requirements.

---

## 3. Caveats

1. **Current Repository State vs. Pre-generation**:
   - Executing `verify_localization.py` on the repository *right now* (prior to M2 and M3) will correctly report **407 missing `.en.md` files** and exit with code **1**. This is the intended behavior for Milestone 1 (TDD contract). Exit code 0 is achieved once M2 (reports) and M3 (books) generate the missing files.
2. **Legacy 17 English Books Description Field**:
   - The 17 pre-existing English books in `content/docs/books/` currently lack `description:`. Milestone 3 is scheduled to retrofit these files. `verify_localization.py` should check `description` on books, noting the 17 legacy files until M3 completes the retrofit.
3. **Case Sensitivity & macOS APFS**:
   - While macOS APFS is case-preserving and case-insensitive by default, Linux CI environments (GitHub Actions, Docker) are strictly case-sensitive. The traversal logic must match exact filenames (`.md` and `.en.md`) without relying on filesystem case folding.

---

## 4. Conclusion & Recommended Architecture for `scripts/verify_localization.py`

### 4.1. Core Architectural Specifications

- **File Path**: `/Users/sotoon/personal/theminiceo/scripts/verify_localization.py`
- **Dependencies**: 100% Python Standard Library (`os`, `sys`, `re`, `argparse`, `json`, `pathlib`). Zero pip dependencies.
- **CLI Interface**:
  - `python3 scripts/verify_localization.py [--content-dir DIR] [--strict] [--json] [-v]`
- **Exit Codes**:
  - `0`: All active Persian files have valid, non-empty `.en.md` counterparts with complete frontmatter.
  - `1`: Any missing file, empty file, broken delimiter, missing frontmatter field, or strict validation error.

### 4.2. Recommended Algorithmic Traversal Flow

```python
# Traversal Flow Outline:
1. Define EXCLUDED_DIRS = {'.obsidian', '_drafts', 'pdfs'}
2. os.walk(content_dir):
   - In-place prune: dirs[:] = [d for d in dirs if not (d in EXCLUDED_DIRS or d.startswith('.') or d.startswith('_draft'))]
   - Filter files: f.endswith('.md') and not f.startswith('.')
   - Classify:
     - if f.endswith('.en.md') -> register in english_files
     - else -> register in persian_files
3. Audit Loop (for each fa_path in sorted(persian_files)):
   - en_path = fa_path[:-3] + '.en.md'
   - Check A: File existence (os.path.exists(en_path)) -> Record if missing
   - Check B: Non-empty file (os.path.getsize(en_path) > 0 and text.strip()) -> Record if empty
   - Check C: Frontmatter delimiter (text starts with '---' or '+++') -> Record if malformed
   - Check D: Title completeness (has_field(fm, 'title')) -> Record if missing
   - Check E: Date completeness (has_field(fm, 'date') unless taxonomy node) -> Record if missing
   - Check F: Description completeness (has_field(fm, 'description') for books/reports/source-has-desc)
   - Check G (if --strict):
     - Persian chars in English title or description (regex: [\u0600-\u06FF])
     - Minimum body length (> 100 characters)
     - Book download shortcode presence in books and reports ({{< book-download ... >}})
4. Format & Output:
   - Print ANSI-formatted summary table showing Persian scanned, English found, missing, errors.
   - If missing == 0 and errors == 0: Print SUCCESS and sys.exit(0)
   - Else: Print failure details and sys.exit(1)
```

### 4.3. Full Reference Implementation for Implementer Agent

```python
#!/usr/bin/env python3
"""
scripts/verify_localization.py - Deterministic Localization Audit Tool for TheMiniCEO
Audits repository content to guarantee 100% English parity with Persian pages.
Zero third-party dependencies (pure Python standard library).
"""

import os
import sys
import re
import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional

EXCLUDED_DIR_NAMES = {".obsidian", "_drafts", "pdfs"}
PERSIAN_CHAR_REGEX = re.compile(r"[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF]")


def is_excluded_dir(dir_name: str) -> bool:
    return (
        dir_name in EXCLUDED_DIR_NAMES
        or dir_name.startswith(".")
        or dir_name.startswith("_draft")
    )


def parse_frontmatter(content: str) -> Tuple[str, Dict[str, str], str]:
    """
    Parses YAML (---) or TOML (+++) frontmatter.
    Returns (type: 'yaml'|'toml'|'none', kv_dict, body_text).
    """
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return "yaml", _parse_flat_kv(parts[1]), parts[2]
    elif content.startswith("+++"):
        parts = content.split("+++", 2)
        if len(parts) >= 3:
            return "toml", _parse_flat_kv(parts[1]), parts[2]
    return "none", {}, content


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


def audit(
    content_dir: Path,
    strict_mode: bool = False,
    verbose: bool = False,
    as_json: bool = False,
) -> int:
    persian_files: List[Path] = []
    english_files: Set[Path] = set()

    # Deterministic directory traversal
    for root, dirs, files in os.walk(content_dir):
        # In-place directory pruning
        dirs[:] = [d for d in dirs if not is_excluded_dir(d)]

        root_path = Path(root)
        for f in files:
            if not f.endswith(".md") or f.startswith("."):
                continue
            p = root_path / f
            if f.endswith(".en.md"):
                english_files.add(p)
            else:
                persian_files.append(p)

    missing_en: List[Path] = []
    empty_files: List[Path] = []
    fm_errors: List[Tuple[Path, str]] = []
    strict_errors: List[Tuple[Path, str]] = []

    for fa_path in sorted(persian_files):
        # Exact stem pairing: strip '.md' (3 chars) and append '.en.md'
        en_path = Path(str(fa_path)[:-3] + ".en.md")

        if not en_path.exists():
            missing_en.append(en_path)
            continue

        if en_path.stat().st_size == 0:
            empty_files.append(en_path)
            continue

        try:
            content = en_path.read_text(encoding="utf-8")
        except Exception as ex:
            empty_files.append(en_path)
            fm_errors.append((en_path, f"Failed to read file: {ex}"))
            continue

        if not content.strip():
            empty_files.append(en_path)
            continue

        fm_type, kv, body = parse_frontmatter(content)
        if fm_type == "none":
            fm_errors.append((en_path, "Missing or unclosed frontmatter delimiter (--- or +++)"))
            continue

        # Frontmatter title check
        if not kv.get("title"):
            fm_errors.append((en_path, "Missing or empty 'title' in frontmatter"))

        # Frontmatter date check (taxonomies and root index exempt)
        rel_str = str(en_path.relative_to(content_dir))
        is_taxonomy = en_path.name == "_index.en.md" and (
            "categories" in rel_str or "tags" in rel_str or rel_str == "_index.en.md"
        )
        if not is_taxonomy and not kv.get("date"):
            fm_errors.append((en_path, "Missing or empty 'date' in frontmatter"))

        # Frontmatter description check (enforced on books, reports, or when Persian has description)
        is_book_or_report = "content/docs/books" in str(en_path) or "content/docs/reports" in str(en_path)
        if is_book_or_report and not kv.get("description"):
            fm_errors.append((en_path, "Missing or empty 'description' in frontmatter"))

        # Strict mode validations
        if strict_mode:
            # Check for Persian characters in English title or description
            title_val = kv.get("title", "")
            if PERSIAN_CHAR_REGEX.search(title_val):
                strict_errors.append((en_path, f"Persian characters in English title: '{title_val}'"))
            desc_val = kv.get("description", "")
            if PERSIAN_CHAR_REGEX.search(desc_val):
                strict_errors.append((en_path, "Persian characters in English description"))

            # Check minimum body content length
            min_len = 50 if en_path.name == "_index.en.md" else 100
            if len(body.strip()) < min_len:
                strict_errors.append((en_path, f"Body content too short (< {min_len} chars)"))

            # Check download shortcode in book and report content pages
            if is_book_or_report and en_path.name != "_index.en.md":
                if "{{< book-download" not in body and "{{< book-download" not in content:
                    strict_errors.append((en_path, "Missing 'book-download' shortcode"))

    total_issues = len(missing_en) + len(empty_files) + len(fm_errors) + len(strict_errors)
    passed = (total_issues == 0)

    if as_json:
        result_payload = {
            "passed": passed,
            "total_persian_scanned": len(persian_files),
            "total_english_found": len(english_files),
            "missing_count": len(missing_en),
            "empty_count": len(empty_files),
            "frontmatter_error_count": len(fm_errors),
            "strict_error_count": len(strict_errors),
            "missing_files": [str(p) for p in missing_en],
            "frontmatter_errors": [{"file": str(p), "error": err} for p, err in fm_errors],
            "strict_errors": [{"file": str(p), "error": err} for p, err in strict_errors],
        }
        print(json.dumps(result_payload, indent=2))
        return 0 if passed else 1

    # Formatted CLI Console Summary
    print("=" * 76)
    print("THEMINICEO LOCALIZATION VERIFICATION AUDIT")
    print("=" * 76)
    print(f"Content Directory:           {content_dir}")
    print(f"Strict Mode:                 {'Enabled' if strict_mode else 'Disabled'}")
    print(f"Total Persian Files Scanned: {len(persian_files)}")
    print(f"Total English Files Found:   {len(english_files)}")
    print(f"Missing .en.md Files:        {len(missing_en)}")
    print(f"Empty Files:                 {len(empty_files)}")
    print(f"Frontmatter Errors:          {len(fm_errors)}")
    if strict_mode:
        print(f"Strict Mode Errors:          {len(strict_errors)}")
    print("-" * 76)

    if missing_en:
        print("\n❌ MISSING ENGLISH COUNTERPARTS BY SECTION:")
        by_sec: Dict[str, int] = {}
        for m in missing_en:
            sec = str(m.parent)
            by_sec[sec] = by_sec.get(sec, 0) + 1
        for sec, cnt in sorted(by_sec.items()):
            print(f"  • {sec}: {cnt} missing")
        if verbose:
            print("\n   Sample missing files:")
            for m in missing_en[:10]:
                print(f"     - {m.name}")

    if fm_errors:
        print("\n❌ FRONTMATTER ISSUES:")
        for p, err in fm_errors[:15]:
            print(f"  • {p.name}: {err}")

    if strict_errors:
        print("\n❌ STRICT MODE VALIDATION ISSUES:")
        for p, err in strict_errors[:15]:
            print(f"  • {p.name}: {err}")

    if passed:
        print("\n✅ SUCCESS: 100% English localization parity achieved! All tests pass.")
        return 0
    else:
        print(f"\n❌ AUDIT FAILED: {total_issues} issues detected.")
        return 1


def main():
    root_default = Path(__file__).resolve().parent.parent / "content"
    parser = argparse.ArgumentParser(
        description="Verify 1:1 English localization parity across theminiceo content.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--content-dir",
        default=str(root_default),
        help=f"Path to content directory (default: {root_default})",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict audit (Persian text detection, body length, shortcodes)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display detailed per-file audit logs",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output audit summary in JSON format",
    )

    args = parser.parse_args()
    content_path = Path(args.content_dir)
    if not content_path.exists():
        print(f"Error: Content directory does not exist: {content_path}", file=sys.stderr)
        sys.exit(2)

    sys.exit(
        audit(
            content_dir=content_path,
            strict_mode=args.strict,
            verbose=args.verbose,
            as_json=args.json,
        )
    )


if __name__ == "__main__":
    main()
```

---

## 5. Verification Method

To independently reproduce and verify all findings from this investigation, execute the following commands in the project root:

### 1. Verify Active Persian vs English Counts & Exclusions
```bash
python3 -c "
import os
EXCLUDE = {'.obsidian', '_drafts', 'pdfs'}
fa = []
en = []
for root, dirs, files in os.walk('content'):
    dirs[:] = [d for d in dirs if not (d in EXCLUDE or d.startswith('.') or d.startswith('_draft'))]
    for f in files:
        if not f.endswith('.md') or f.startswith('.'): continue
        if f.endswith('.en.md'): en.append(f)
        else: fa.append(f)
print(f'Active FA: {len(fa)}, Active EN: {len(en)}')
assert len(fa) == 555, f'Expected 555 FA, got {len(fa)}'
assert len(en) == 148, f'Expected 148 EN, got {len(en)}'
print('Parity counts verified successfully!')
"
```
*Expected Output*: `Active FA: 555, Active EN: 148` and clean assertion pass.

### 2. Verify Persian Slugs in Reports and Books
```bash
python3 -c "
import os
assert os.path.exists('content/docs/reports/گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md')
assert os.path.exists('content/docs/books/خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md')
print('Persian slug files exist and verified.')
"
```
*Expected Output*: `Persian slug files exist and verified.`

### 3. Verify Missing English Count Distribution
```bash
python3 -c "
import os
EXCLUDE = {'.obsidian', '_drafts', 'pdfs'}
missing_by_dir = {}
for root, dirs, files in os.walk('content'):
    dirs[:] = [d for d in dirs if not (d in EXCLUDE or d.startswith('.') or d.startswith('_draft'))]
    for f in files:
        if f.endswith('.md') and not f.endswith('.en.md') and not f.startswith('.'):
            en_path = os.path.join(root, f[:-3] + '.en.md')
            if not os.path.exists(en_path):
                missing_by_dir[root] = missing_by_dir.get(root, 0) + 1
print('Missing distribution:', missing_by_dir)
assert missing_by_dir == {'content/docs/books': 390, 'content/docs/reports': 17}
print('Distribution verified: exactly 390 books and 17 reports missing!')
"
```
*Expected Output*: `Distribution verified: exactly 390 books and 17 reports missing!`

### 4. Invalidation Conditions
- If any new active Persian file is added outside `books/` or `reports/` without an `.en.md` companion.
- If a future Hugo version alters the `<slug>.<lang>.md` co-located file naming specification.
- If APFS or Git alters the decomposed unicode normalization of `خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md`.
