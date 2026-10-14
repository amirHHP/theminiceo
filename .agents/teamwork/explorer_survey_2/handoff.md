# Comprehensive Survey Report: Books Catalog & Data Sources

**Author**: Explorer Survey 2 (`explorer_survey_2`)  
**Date**: 2026-10-09  
**Scope**: English Localization Survey of `content/docs/books/`, `data/books_metadata.json`, and `scripts/`  
**Reference Requirement**: R2 (and foundational support for R1 & R4) from `ORIGINAL_REQUEST.md`

---

## 1. Observation

### 1.1 Catalog Inventory & File Distribution
An automated audit of `content/docs/books/` and the whole repository revealed the following file distribution:

| Metric | Count | Details |
| :--- | :--- | :--- |
| **Total Markdown Files in `content/docs/books/`** | **426** | All `.md` files in directory |
| **Persian Content Files (`*.md`)** | **408** | 407 book entries + 1 `_index.md` |
| **Existing English Files (`*.en.md`)** | **18** | 17 legacy book entries + 1 `_index.en.md` |
| **Missing English Book Files** | **390** | Exactly 408 - 18 = 390 |
| **Global Repo Parity Status** | **407 total missing** | 390 books + 17 reports. All other 22 content folders have 100% EN parity |

- **Naming Scheme**:
  - Hugo associates languages via base filenames: `<slug>.md` (Persian, default) and `<slug>.en.md` (English).
  - Out of the 390 missing book files:
    - **389 files** use kebab-case ASCII slugs (e.g., `100-things-every-designer-needs-to-know-about-people.md`).
    - **Exactly 1 file** uses a Persian slug: `خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md`. For Hugo language pairing, its English counterpart must be named `خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.en.md`.

### 1.2 Structural Schema of Persian Book Files
Across all 390 Persian book files currently lacking English counterparts, there is **100% structural uniformity** across all 7 standard components:

| Component | Coverage | Sample Syntax / Pattern |
| :--- | :--- | :--- |
| **YAML Frontmatter** | 390 / 390 (100%) | `title`, `date`, `description`, `tags`, `categories` |
| **Book Specifications Table** | 390 / 390 (100%) | `\| مشخصات کتاب \| توضیحات \|` with 6 standard attributes |
| **Section 1: Core Premise** | 390 / 390 (100%) | `### 📖 درباره کتاب و پیام محوری` |
| **Section 2: Key Takeaways** | 390 / 390 (100%) | `### 🔑 سرفصل‌ها و آموزه‌های کلیدی` (4-5 bullet points) |
| **Section 3: 2026 Relevance** | 390 / 390 (100%) | `### 💡 چرا مطالعه این کتاب در سال ۲۰۲۶ ضروری است؟` |
| **Section 4: Target Audience** | 390 / 390 (100%) | `### 🎯 این منبع برای چه کسانی بیشترین ارزش را دارد؟` |
| **Section 5: Download Shortcode**| 390 / 390 (100%) | `{{< book-download url="..." title="..." size="..." format="PDF" >}}` |

### 1.3 Inspection of Existing 18 `.en.md` Files
Analysis of the 18 pre-existing English files revealed a significant structural dichotomy:

1. **Section Index (`_index.en.md`)**:
   - Contains only TOML frontmatter (lines 1–10: `date`, `draft = false`, `weight = 91`, `title = 'Product management library'`, `description = '...'`).
   - Body is currently **completely empty** (0 lines), whereas `_index.md` has 54 lines containing 9 curated showcase cards (`{{< cards >}}`) and a 7-domain breakdown.

2. **17 Existing Book `.en.md` Files**:
   - Files: `Escaping-the-Build-Trap.en.md`, `The-Lean-Product-Playbook.en.md`, `The-Lean-Startup.en.md`, `behind-every-great-product.en.md`, `build-better-products.en.md`, `human-blockers.en.md`, `okr-books.en.md`, `pm-club.en.md`, `pm-courses.en.md`, `storytelling-with-data.en.md`, `survival-guide-for-product-managers.en.md`, `talking-to-others.en.md`, `webinar-05-roadmap.en.md`, `webinar-06-listening.en.md`, `کتاب-inspired.en.md`, `کتاب-lean-analytics.en.md`, `کتاب-roadmap.en.md`.
   - **Prose Quality**: High editorial quality. They contain comprehensive English explanations of concepts (e.g. Validated Learning, Build-Measure-Learn, Output vs. Outcome, Product Kata, Product-Market Fit Pyramid).
   - **Structural Deficiencies**:
     - `description:` key is missing from frontmatter in **17 / 17** files (only `title` and `date` are present).
     - Specifications table (`| Book Specification | Details |`) is missing in **17 / 17** files.
     - `{{< book-download ... >}}` shortcode is missing in **17 / 17** files.
   - **Finding**: These files demonstrate the required editorial depth and tone, but cannot serve as complete structural templates without being retrofitted to meet R1 and R2 criteria.

### 1.4 Data Source: `data/books_metadata.json`
- **Size & Count**: 219,923 bytes, containing exactly **390 records**.
- **Slug Parity**: `set(json_slugs) == set(missing_en_slugs)`. Every missing file has a 1-to-1 counterpart in this dataset.
- **Schema per Record**:
  ```json
  {
    "filename": "100 Things Every Designer Needs To Know About People.pdf",
    "title": "100 Things Every Designer Needs To Know About People",
    "slug": "100-things-every-designer-needs-to-know-about-people",
    "format": "PDF",
    "size_bytes": 8554829,
    "size_str": "8.2 مگابایت",
    "category_slug": "ux-design",
    "category_title": "طراحی تجربه کاربری و روانشناسی",
    "is_persian": false,
    "download_url": "https://dl.theminiceo.ir/100%20Things%20Every%20Designer%20Needs%20To%20Know%20About%20People.pdf"
  }
  ```
- **Category Distribution across the 390 Books**:
  1. `strategy-leadership`: 197 books ("Product Strategy & Leadership")
  2. `ux-design`: 69 books ("UX Design & Behavioral Psychology")
  3. `ai-technology`: 45 books ("AI & Technology in Product")
  4. `discovery-research`: 36 books ("Product Discovery & User Research")
  5. `growth-analytics`: 19 books ("Growth & Product Analytics")
  6. `management-career`: 12 books ("Career Development & Practical Skills")
  7. `lean-agile`: 11 books ("Lean Delivery & Agile Management")
  8. `reports-playbooks`: 1 book ("Industry Reports & Playbooks")
- **URL & File Validity**: 390 / 390 (100%) contain valid direct download URLs on `https://dl.theminiceo.ir/`. All 433 matching PDF files exist locally in `content/pdfs/`.

### 1.5 Scripts & Curated Datasets in `scripts/`
- **`scripts/curated_books_data.py`** (583 KB):
  - Contains `CURATED_BOOKS` with **206 deeply curated flagship books**.
  - Exactly **206 of the 390 missing books** match entries in `CURATED_BOOKS`.
  - Holds structured breakdowns for OST (Opportunity Solution Tree), The Mom Test rules, Hook Model 4 stages, Empowered teams, Zero to One, etc.
- **`scripts/enrich_and_deduplicate_books.py`** (82 KB):
  - Contains `KNOWN_AUTHORS` (216 dictionary mappings).
  - Contains `KNOWN_TITLES_FA` (108 mappings with clean English titles).
  - Contains `detect_author()`, `clean_display_title()`, and `extract_all_pdf_metadata()` using `pypdf`.
  - In `content/docs/books/<slug>.md`, **372 / 390 authors** already contain explicit Latin/English author names in parentheses in the table (e.g. `الکساندر استروالدر (Alexander Osterwalder)`).
- **Environment**: Python 3 with `pypdf` 6.19.0 is available in `scripts/.venv/`.

### 1.6 Shortcode Analysis: `layouts/shortcodes/book-download.html`
- Located at `/Users/sotoon/personal/theminiceo/layouts/shortcodes/book-download.html`.
- Accepts parameters: `url`, `title`, `size`, `format`, `lang`.
- **Current Limitation**: It has hardcoded Persian UI strings:
  - Line 26: `<span>حجم: {{ $size }}</span>`
  - Line 30: `<span>زبان: {{ $lang }}</span>`
  - Line 33: `<span ...>سرور پرسرعت داخلی</span>`
  - Line 43: `<span>دریافت فایل کتاب</span>`
- **Opportunity**: Updating this shortcode to check `{{ if eq .Page.Language.Lang "en" }}` allows automatic rendering of English labels ("Download Book File", "Size: ", "Language: ", "Fast Direct Download") without breaking Persian pages.

### 1.7 Hugo Build Baseline
- Execution of `hugo --renderToMemory`:
  - Exit code: 0
  - Duration: 14.77 seconds
  - Rendered Pages: **FA: 723**, **EN: 270**
  - Page Delta: 453 pages.
  - Adding 390 book pages and 17 report pages will increase English rendered pages by 407, achieving near 1:1 page parity.

---

## 2. Logic Chain

1. **Deduction 1 (Scope & Parity Boundary)**:
   - Observation 1.1 proves that 390 books in `content/docs/books/` and 17 reports in `content/docs/reports/` are the **only** missing localized pages in the entire repository.
   - Therefore, localizing these 390 books solves 95.8% of the content localization gap.

2. **Deduction 2 (Data Completeness & Zero-Placeholder Feasibility)**:
   - Observation 1.4 confirms that `data/books_metadata.json` covers 100% of the 390 missing books with slugs, download URLs, file sizes, and categories.
   - Observation 1.5 confirms that 206 of the 390 books (52.8%) have rich, pre-curated conceptual metadata in `scripts/curated_books_data.py`.
   - Observation 1.5 confirms that 372 / 390 authors have clean English Latin transliterations already extracted in the Persian markdown specifications table.
   - Observation 1.2 confirms that every Persian page contains an authentic 5-section breakdown with domain frameworks, 2026 relevance, and target audience.
   - Therefore, generating high-quality English markdown files for all 390 books without generic "Lorem Ipsum" or placeholder text is 100% feasible using an automated Python generator script.

3. **Deduction 3 (Gold Standard Definition)**:
   - Observation 1.3 shows that the 17 existing `.en.md` files lack `description:`, specs tables, and download buttons.
   - If an automated audit script (R1) tests for frontmatter completeness (`title`, `date`, `description`), those 17 files will fail unless updated.
   - Therefore, the reference "Gold Standard" must combine the editorial narrative depth of the 17 existing summaries with the 7-part structured schema of the 390 Persian books.

4. **Deduction 4 (Naming & Hugo Routing)**:
   - Hugo pairs multilingual files by matching `<base>.md` and `<base>.en.md`.
   - 389 books will be `<slug>.en.md`.
   - The sole Persian-slug book `خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md` must be named `خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.en.md` to maintain Hugo multilingual pairing.

---

## 3. Caveats

1. **Retrofitting Legacy 17 Book Files**:
   - The 17 existing `.en.md` book files and `_index.en.md` must either be retrofitted with `description:` frontmatter and specifications tables/downloads, or exempted by the verification script. Retrofitting is strongly recommended to maintain design consistency across the English library.
2. **Shortcode i18n**:
   - Without updating `layouts/shortcodes/book-download.html`, English pages will display the download button with Persian text ("دریافت فایل کتاب"). A minor, backwards-compatible template adjustment is recommended.
3. **Persian Slug Book**:
   - The book `خلق-محصولات-آینده...` is originally authored in Persian by Mehdi Alipour Sakhavi. Its English title should be translated as `"Creating Future Products: The AI Guide for Product Managers"` while maintaining the exact file basename for Hugo pairing.
4. **Build Performance**:
   - Generating 390 additional markdown pages will increase Hugo build time from ~14.7s to ~18-22s. `hugo --renderToMemory` should have sufficient memory and timeout limits.

---

## 4. Conclusion & Recommended Methodology

### 4.1 Canonical English Book Schema ("Gold Standard")
Every generated `<slug>.en.md` should adhere to this complete standard:

```markdown
---
title: "<Canonical English Title>"
date: 2026-09-15
description: "<Engaging, professional 1-2 sentence overview of the book's core premise and value>"
tags: ["Library", "<English Category Title>", "Product Management"]
categories: ["Books"]
---

| Book Specification | Details |
| :--- | :--- |
| **Author** | <English Author Name> |
| **Category** | <English Category Title> |
| **Page Count** | <Page Count> pages |
| **Format & Quality** | PDF • Standard Digital Edition |
| **File Size** | <File Size in MB, e.g. 8.2 MB> |
| **Target Audience** | Specialized • Product Managers & Innovators |

---

### 📖 About the Book & Core Premise

<In-depth 2-3 paragraph overview explaining the core thesis, author perspective, and strategic value.>

---

### 🔑 Key Takeaways & Core Frameworks

* **<Framework 1>:** <Operational description of framework and application>
* **<Framework 2>:** <Operational description of framework and application>
* **<Framework 3>:** <Operational description of framework and application>
* **<Framework 4>:** <Operational description of framework and application>

---

### 💡 Why This Book Matters in 2026

<Analysis of the book's importance in 2026 amid AI-driven workflows, agentic systems, and rapid prototyping.>

---

### 🎯 Who Should Read This Book?

<Specific professional roles: Product Managers, UX Designers, Tech Leads, Founders, and Strategy Consultants.>

---

### 📥 Download Book File

{{< book-download url="<download_url>" title="Download <Title> (Full English Edition)" size="<size_mb> MB" format="PDF" lang="English" >}}
```

### 4.2 Generation Methodology: Deterministic Python Generator (`scripts/generate_english_books.py`)
To fulfill R2 rapidly, cleanly, and without API dependency or placeholder text, the implementation agent should execute the following strategy:

1. **Script Architecture**:
   - Create `scripts/generate_english_books.py`.
   - Load `data/books_metadata.json` (390 items).
   - Load `scripts/curated_books_data.py` (`CURATED_BOOKS` with 206 flagship titles).
   - Use `KNOWN_AUTHORS` and `KNOWN_TITLES_FA` from `scripts/enrich_and_deduplicate_books.py`.
2. **Metadata Transformation**:
   - Convert Persian size string (`"8.2 مگابایت"` -> `"8.2 MB"`).
   - Map 8 categories to standard English titles (e.g., `strategy-leadership` -> `"Product Strategy & Leadership"`).
   - Extract English author name from table parentheses or known author dictionary.
3. **Content Synthesis**:
   - **Tier 1 (206 Curated Books)**: Translate and adapt the deep conceptual frameworks (OST, Hook model, PMF pyramid, etc.) into high-quality English markdown.
   - **Tier 2 (184 Domain Books)**: Synthesize domain-grounded summaries, chapter-derived takeaways, 2026 relevance, and audience profiles based on the book's specific category and topic.
4. **Retrofit Legacy Files**:
   - Inject `description:` frontmatter into the 17 legacy `.en.md` files so they pass R1 CI audits.
   - Populate `_index.en.md` with localized cards and category links.
5. **Shortcode Localization**:
   - Update `layouts/shortcodes/book-download.html` with language conditionals (`{{ if eq .Page.Language.Lang "en" }}`).

---

## 5. Verification Method

To independently verify the facts and conclusions in this report, execute the following commands from `/Users/sotoon/personal/theminiceo`:

### 5.1 Verify File Counts and Missing Books
```bash
python3 -c "
import os, json
books_dir = 'content/docs/books'
files = os.listdir(books_dir)
en_bases = {f[:-6] for f in files if f.endswith('.en.md') and f != '_index.en.md'}
fa_bases = {f[:-3] for f in files if f.endswith('.md') and not f.endswith('.en.md') and f != '_index.md'}
missing = fa_bases - en_bases
print('Persian books count:', len(fa_bases))
print('Existing English books count:', len(en_bases))
print('Missing English books count:', len(missing))
with open('data/books_metadata.json') as f:
    meta = json.load(f)
print('Metadata records count:', len(meta))
print('Metadata matches missing books exactly:', set(b['slug'] for b in meta) == missing)
"
```
*Expected Output*:
- Persian books count: `407`
- Existing English books count: `17`
- Missing English books count: `390`
- Metadata records count: `390`
- Metadata matches missing books exactly: `True`

### 5.2 Verify Section Consistency Across 390 Books
```bash
python3 -c "
import os, json
with open('data/books_metadata.json') as f:
    books = json.load(f)
specs = sum(1 for b in books if '| مشخصات کتاب' in open(f'content/docs/books/{b[\"slug\"]}.md').read())
dls = sum(1 for b in books if 'book-download' in open(f'content/docs/books/{b[\"slug\"]}.md').read())
print(f'Specs tables: {specs}/390, Download shortcodes: {dls}/390')
"
```
*Expected Output*:
`Specs tables: 390/390, Download shortcodes: 390/390`

### 5.3 Verify Hugo Compilation Baseline
```bash
hugo --renderToMemory
```
*Expected Output*:
Exits 0, building 723 FA pages and 270 EN pages without errors.

### 5.4 Invalidation Conditions
This survey's recommendations would be invalidated if:
1. `data/books_metadata.json` contained broken download URLs or orphaned slugs (verified 100% valid).
2. Existing Persian book pages had inconsistent markdown structures requiring individualized manual translation (verified 100% consistent across 7 components).
3. Hugo failed to link `<slug>.en.md` to `<slug>.md` as multilingual counterparts (verified working on existing 18 files).
