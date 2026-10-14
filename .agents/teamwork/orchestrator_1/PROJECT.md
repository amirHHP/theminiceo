# Project: theminiceo English Localization & Hugo Parity

## Architecture
- Static Site Generator: Hugo v0.167.0 with Hextra theme (`themes/hextra`).
- Multilingual Configuration:
  - Default Language: Persian (`fa`, RTL, route `/`)
  - Target Language: English (`en`, LTR, route `/en/`)
  - Translation pairing: Co-located `<slug>.md` ↔ `<slug>.en.md`
- Components:
  - Content Catalog: `content/docs/books/` (407 books), `content/docs/reports/` (17 reports), 23 other folders (already at 100% parity).
  - Shortcodes: `layouts/shortcodes/book-download.html` (needs multilingual labels).
  - Tooling: `scripts/verify_localization.py` (deterministic audit tool).
  - Generator: `scripts/generate_english_books.py` (data-driven book generation).
  - Metadata: `data/books_metadata.json` (390 items), `scripts/curated_books_data.py` (206 items), `scripts/setup_reports_section.py` (17 items).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Automated Verification Script | `scripts/verify_localization.py` auditing 1:1 file parity, frontmatter completeness, non-empty files, exit 0/1 | M1 | R1 |
| 2 | Multilingual Shortcode Support | Update `layouts/shortcodes/book-download.html` to support English labels conditionally | M2 | Survey / R4 |
| 3 | Reports English Localization | Generate 17 English reports in `content/docs/reports/*.en.md` from `setup_reports_section.py` | M2 | R3 |
| 4 | Books Generator Tooling | `scripts/generate_english_books.py` utilizing metadata & curated books data | M3 | R2 |
| 5 | Books English Localization | Generate 390 English books in `content/docs/books/*.en.md` adhering to 7-part gold standard | M3 | R2 |
| 6 | Legacy Books & Index Retrofit | Add `description:` to 17 legacy `.en.md` books and populate `_index.en.md` | M3 | R2 |
| 7 | Hugo Build & Memory Render | Verify `hugo --renderToMemory` succeeds with exit 0 and +407 rendered English pages | M4 | R4 |
| 8 | E2E Testing Suite (Tiers 1-4) | Comprehensive test harness validating localization coverage, frontmatter, shortcodes, and Hugo compilation | E2E Track | R1-R4 |
| 9 | Adversarial Coverage Hardening | Tier 5 adversarial testing for broken links, syntax anomalies, and edge cases | M4 (Phase 2) | Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Automated Localization Audit & CI Verification Tool | Create `scripts/verify_localization.py` adhering strictly to R1 specification | none | PLANNED |
| M2 | Reports English Localization & Shortcode i18n | Update `layouts/shortcodes/book-download.html` and create all 17 `content/docs/reports/*.en.md` | M1 | PLANNED |
| M3 | Books English Localization | Create `scripts/generate_english_books.py`, generate 390 `.en.md` books, retrofit legacy 17 books and `_index.en.md` | M2 | PLANNED |
| M4 | Hugo Build Integrity & E2E Validation | Pass 100% E2E tests, verify Hugo compilation (+407 pages, exit 0), and adversarial coverage hardening | M3, E2E | PLANNED |

## Interface Contracts
### `scripts/verify_localization.py` ↔ CI / Orchestrator
- Invocation: `python3 scripts/verify_localization.py`
- Exit Code: `0` if all active Persian content pages have valid `.en.md` counterparts with complete frontmatter (`title`, `date`, `description`) and non-empty content. `1` if any file is missing or invalid.
- Exclusions: `content/pdfs/`, `.obsidian/`, `_drafts/`.

### `layouts/shortcodes/book-download.html` ↔ Content Markdown
- Detects `.Page.Language.Lang == "en"`.
- If English: renders `"Size: "`, `"Language: "`, `"High-speed Direct CDN"`, `"Download Book File"`.
- If Persian: renders `"حجم: "`, `"زبان: "`, `"سرور پرسرعت داخلی"`, `"دریافت فایل کتاب"`.

### Book Markdown `<slug>.en.md` Schema (7 Components)
1. YAML Frontmatter: `title`, `date`, `description`, `tags`, `categories: ["Books"]`.
2. Specifications Table: `| Book Specification | Details |` (Author, Category, Pages, Format, File Size, Target Audience).
3. Section 1: `### 📖 About the Book & Core Premise`.
4. Section 2: `### 🔑 Key Takeaways & Core Frameworks`.
5. Section 3: `### 💡 Why This Book Matters in 2026`.
6. Section 4: `### 🎯 Who Should Read This Book?`.
7. Section 5: `### 📥 Download Book File` with `{{< book-download url="..." title="..." size="..." format="PDF" lang="English" >}}`.

## Code Layout
- `scripts/verify_localization.py` — Verification & audit script.
- `scripts/generate_english_books.py` — Books generation script.
- `scripts/test_localization_e2e.py` — E2E test runner.
- `layouts/shortcodes/book-download.html` — Multilingual download card shortcode.
- `content/docs/reports/*.en.md` — 17 English reports.
- `content/docs/books/*.en.md` — 390 English books + 17 retrofitted books + `_index.en.md`.
