# E2E Test Infra: theminiceo Localization Parity

## Test Philosophy
- Opaque-box, requirement-driven.
- Verifies full site compliance with R1, R2, R3, R4, and acceptance criteria without depending on internal implementation details.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Interactions + Real-World Workloads.

## Feature Inventory & Test Mapping
| # | Feature | Requirement | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---------|-------------|:------:|:------:|:------:|:------:|
| 1 | Verification Script Parity Audit | R1 | 5 | 5 | ✓ | ✓ |
| 2 | Frontmatter Completeness | R1, R2, R3 | 5 | 5 | ✓ | ✓ |
| 3 | Books Localization Parity | R2 | 5 | 5 | ✓ | ✓ |
| 4 | Books 7-Part Structure Quality | R2 | 5 | 5 | ✓ | ✓ |
| 5 | Reports Localization Parity | R3 | 5 | 5 | ✓ | ✓ |
| 6 | Reports Research Takeaways Quality | R3 | 5 | 5 | ✓ | ✓ |
| 7 | Multilingual Shortcode Rendering | R4 | 5 | 5 | ✓ | ✓ |
| 8 | Hugo Compilation & Memory Render | R4 | 5 | 5 | ✓ | ✓ |

## Test Architecture
- Test Runner: `scripts/test_localization_e2e.py`
- Command: `python3 scripts/test_localization_e2e.py`
- Pass/Fail semantics: Exit code 0 on all tests passing, non-zero on failure.
- Assertions:
  - Tier 1 (Feature Coverage):
    - T1.1: Verification script exists at `scripts/verify_localization.py` and is executable.
    - T1.2: Check all 17 reports have `.en.md` files.
    - T1.3: Check all 407 books in `content/docs/books/` have `.en.md` files (390 newly generated + 17 existing).
    - T1.4: Check all `.en.md` files have non-empty frontmatter `title`, `date`, `description`.
    - T1.5: Check all `.en.md` files have valid non-empty body content (>100 characters).
  - Tier 2 (Boundary & Corner Cases):
    - T2.1: Verify Persian slug book `خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.en.md` exists and is valid.
    - T2.2: Verify Persian slug report `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md` exists and is valid.
    - T2.3: Verify excluded folders (`content/pdfs/`, `.obsidian/`, `_drafts/`) are not flagged as missing.
    - T2.4: Verify no untranslated Persian blocks remain in English book/report headers or body.
    - T2.5: Verify no dummy placeholder text (`lorem ipsum`, `TODO`, `TBD`, `placeholder`) in generated files.
  - Tier 3 (Cross-Feature Combinations):
    - T3.1: Verify download shortcodes in `.en.md` reference valid URLs matching `data/books_metadata.json` and `setup_reports_section.py`.
    - T3.2: Verify categories in frontmatter map correctly to standard taxonomy categories.
    - T3.3: Verify specifications tables match book metadata (Author, Format, File Size).
    - T3.4: Verify `layouts/shortcodes/book-download.html` renders English labels when language is `en`.
  - Tier 4 (Real-World Application Scenarios):
    - T4.1: Execute `python3 scripts/verify_localization.py` and verify it exits 0 with 100% pass report.
    - T4.2: Execute `hugo --renderToMemory` and verify it completes with exit code 0 and 0 errors.
    - T4.3: Verify Hugo rendered page count increases by at least 407 English pages.
    - T4.4: Verify Hugo language switchers pair correctly between Persian and English URLs.

## Coverage Thresholds
- Minimum Tier 1 tests: ≥ 40
- Minimum Tier 2 tests: ≥ 25
- Minimum Tier 3 tests: ≥ 15
- Minimum Tier 4 tests: ≥ 5
- Total test cases: ≥ 85 assertions across all tiers.
