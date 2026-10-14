# Milestone 3 Investigation Report: Books Catalog, Metadata Sources, and Slug Alignment

**Author**: Explorer M3.1 (`explorer_m3_1`)  
**Target Milestone**: Milestone 3 (Books English Localization & Metadata Polish)  
**Parent Orchestrator**: `orchestrator_2` (`1390bbb4-2296-47f7-8f97-a4b7fde0fc3d`)  
**Date**: 2026-10-10  
**Target Artifact**: `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m3_1/handoff.md`

---

## 1. Observation

### 1.1 Catalog Inventory & 1:1 Slug Alignment
Direct programmatic audit of `/Users/sotoon/personal/theminiceo/content/docs/books/` and `/Users/sotoon/personal/theminiceo/data/books_metadata.json` revealed:

* **File Counts in `content/docs/books/`**:
  * Total Markdown files: 426
  * Persian content files (`*.md` excluding `*.en.md` and `_index.md`): **407**
  * Existing English book files (`*.en.md` excluding `_index.en.md`): **17**
  * Section indexes: 2 (`_index.md` and `_index.en.md`)
  * Missing English book files: exactly **390** ($407 - 17 = 390$)

* **Metadata Dataset (`data/books_metadata.json`)**:
  * Total records: **390** (219,923 bytes)
  * Unique slugs in JSON: **390**
  * Set alignment test:
    ```python
    meta_slugs = {b['slug'] for b in meta}
    missing_en_slugs = fa_slugs - en_slugs
    meta_slugs == missing_en_slugs  # Evaluates to True
    ```
  * Discrepancies: **0** (0 slugs in meta missing from content; 0 missing content slugs absent from meta).

* **Metadata Record Field Completeness**:
  * Every single record (390/390, 100%) has all 10 keys present with 0 nulls and 0 empty strings:
    `filename`, `title`, `slug`, `format`, `size_bytes`, `size_str`, `category_slug`, `category_title`, `is_persian`, `download_url`.
  * Format distribution:
    * `PDF`: **389 records**
    * `EPUB`: **1 record** — `triggers-creating-behavior-that-lasts-becoming-the-person-you-want` (`Triggers_Creating_Behavior_That_Lasts_Becoming_the_Person_You_Want.epub`, 2,055,673 bytes).
  * Language flag distribution:
    * `is_persian: False`: **389 records**
    * `is_persian: True`: **1 record** — `خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول`.
  * Category distribution across the 390 missing books:
    1. `strategy-leadership`: 197 books ("Product Strategy & Leadership")
    2. `ux-design`: 69 books ("UX Design & Behavioral Psychology")
    3. `ai-technology`: 45 books ("AI & Technology in Product")
    4. `discovery-research`: 36 books ("Product Discovery & User Research")
    5. `growth-analytics`: 19 books ("Growth & Product Analytics")
    6. `management-career`: 12 books ("Career Development & Practical Skills")
    7. `lean-agile`: 11 books ("Lean Delivery & Agile Management")
    8. `reports-playbooks`: 1 book ("Industry Reports & Playbooks")
  * Download URLs: 390/390 (100%) start with `https://dl.theminiceo.ir/`.

---

### 1.2 Analysis of `scripts/curated_books_data.py` (206 Items)
Inspection of `/Users/sotoon/personal/theminiceo/scripts/curated_books_data.py` (583,331 bytes) revealed:

* **Dictionary Structure**:
  * Root object: `CURATED_BOOKS` with **206 entries**.
  * Keys are internal identifiers (e.g., `continuous_discovery_habits`, `the_mom_test`, `hooked`, `khalaq_mahsulat_ayandeh`).
  * Mapping mechanism: Each entry contains a `match_slugs` list (e.g., `"match_slugs": ["continuous-discovery-habits-discover-products-that-create-customer"]`).
  * Mapping overlap with `data/books_metadata.json`:
    * Total entries in `CURATED_BOOKS`: **206**
    * Total unique slugs across all `match_slugs`: **207** (entry `good_strategy_bad_strategy` contains two aliases: `['good-strategy-bad-st-by-richard-rumelt', 'good-strategy-bad-strategy']`).
    * Slugs matching `data/books_metadata.json`: **exactly 206 of the 390 books** (52.8% coverage).
    * Every single one of the 206 curated entries matches exactly one distinct book in `data/books_metadata.json`.
  * Remaining non-curated books in `data/books_metadata.json`: **184 books** ($390 - 206 = 184$).

* **Data Schema per Curated Entry**:
  * `match_slugs`: List of matching URL slugs.
  * `fa_title`: Persian title with Latin/English title in parentheses (e.g., `کتاب عادت‌های کشف مداوم (Continuous Discovery Habits)`).
  * `author`: Persian author with Latin transliteration in parentheses (e.g., `ترزا تورس (Teresa Torres)`).
  * `desc`: 1-2 sentence core description.
  * `summary`: In-depth 2-3 paragraph overview explaining the central thesis, author perspective, and strategic value.
  * `frameworks`: List of 4-5 tuples `(framework_title, framework_desc)` containing English framework names in bold (e.g., `Opportunity Solution Tree - OST`, `Product Trio`, `Story-based Interviewing`, `The Compliment Trap`, `Hook Model`, `B=MAP`).
  * `relevance_2026`: Dedicated 2026 perspective (AI agent workflows, rapid software delivery, feature commoditization).
  * `audience`: Target personas (Product Managers, UX Designers, Tech Leads, Founders).

---

### 1.3 Persian Slug Book Investigation: `خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md`
Detailed Unicode codepoint and filesystem examination of the sole Persian-slug book revealed:

* **File Path**:
  `/Users/sotoon/personal/theminiceo/content/docs/books/خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.md`

* **Unicode Decomposed Combining Maddah (NFD)**:
  * Codepoint analysis of the slug word `آینده` (ayandeh):
    * Index [12]: `U+0627` (`ARABIC LETTER ALEF`, UTF-8: `\xd8\xa7`)
    * Index [13]: `U+0653` (`ARABIC MADDAH ABOVE`, UTF-8: `\xd9\x93`)
  * Normalization state:
    * `Is filename NFD?`: **True** (4 bytes: `\xd8\xa7\xd9\x93`)
    * `Is filename NFC?`: **False** (Precomposed NFC would be `U+0622` `ARABIC LETTER ALEF WITH MADDA ABOVE`, 2 bytes: `\xd8\xa2`)
  * Consistency:
    * `data/books_metadata.json` slug: **100% byte-identical NFD sequence** (`\xd8\xa7\xd9\x93`).
    * `scripts/curated_books_data.py` (`khalaq_mahsulat_ayandeh["match_slugs"][0]`): **100% byte-identical NFD sequence**.
    * `scripts/test_localization_e2e.py` line 481: **100% byte-identical NFD sequence**.
    * `scripts/verify_localization.py` line 458 (`en_path = fa_path[:-3] + ".en.md"`): slices the string directly without re-encoding, preserving exact NFD bytes.

* **Filename Pairing Requirement for Hugo**:
  * Hugo pairs translations by matching file base stems: `<base>.md` (fa) ↔ `<base>.en.md` (en).
  * The required English filename MUST be:
    `content/docs/books/خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول.en.md`
    using the exact NFD decomposed slug. If a script re-encodes this slug into precomposed NFC `آ` (`\xd8\xa2`), the files will NOT pair on Unix filesystems or git, and both `verify_localization.py` and `test_localization_e2e.py` will fail.

* **Book Metadata & Content**:
  * Original Author: مهدی علیپور سخاوی (`Mehdi Alipour Sakhavi`).
  * Recommended English Title: `"Creating Future Products: The AI Guide for Product Managers"`.
  * Recommended English Description: `"A comprehensive guide on leveraging artificial intelligence, LLMs, and autonomous agents in modern product management, discovery, and growth."`.
  * Format: PDF, 245 pages, 3.0 MB.
  * Download URL:
    `https://dl.theminiceo.ir/%D8%AE%D9%84%D9%82_%D9%85%D8%AD%D8%B5%D9%88%D9%84%D8%A7%D8%AA_%D8%A7%D9%93%DB%8C%D9%86%D8%AF%D9%87_%D8%B1%D8%A7%D9%87%D9%86%D9%85%D8%A7%DB%8C_%D9%87%D9%88%D8%B4_%D9%85%D8%B5%D9%86%D9%88%D8%B9%DB%8C_%D8%A8%D8%B1%D8%A7%DB%8C_%D9%85%D8%AF%DB%8C%D8%B1%D8%A7%D9%86_%D9%85%D8%AD%D8%B5%D9%88%D9%84.pdf`

---

### 1.4 Analysis of 17 Legacy Books & `what-is-product-managment.en.md`
Automated inspection of the 17 legacy `.en.md` books and `content/docs/1-what-is-product-managment/what-is-product-managment.en.md` revealed:

| File Name | Frontmatter Keys Present | Missing `description:` | Missing `categories: ["Books"]` | Has Specs Table | Has Download Shortcode |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `Escaping-the-Build-Trap.en.md` | `title`, `date` | **YES** | **YES** | NO | NO |
| `The-Lean-Product-Playbook.en.md` | `title`, `date` | **YES** | **YES** | NO | NO |
| `The-Lean-Startup.en.md` | `title`, `date` | **YES** | **YES** | NO | NO |
| `behind-every-great-product.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `build-better-products.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `human-blockers.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `okr-books.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `pm-club.en.md` | `title`, `date` | **YES** | **YES** | NO | NO |
| `pm-courses.en.md` | `title`, `date` | **YES** | **YES** | NO | NO |
| `storytelling-with-data.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `survival-guide-for-product-managers.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `talking-to-others.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `webinar-05-roadmap.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `webinar-06-listening.en.md` | `title`, `date` | **YES** | **YES** | NO | NO |
| `کتاب-inspired.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `کتاب-lean-analytics.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| `کتاب-roadmap.en.md` | `title`, `date`, `coverImage` | **YES** | **YES** | NO | NO |
| **`what-is-product-managment.en.md`** | `title`, `date`, `weight`, `linkTitle`, `categories` | **YES** | N/A (`product-skills`) | N/A (Article) | N/A (Article) |

* **Key Findings**:
  1. **Frontmatter Errors**: `python3 scripts/verify_localization.py` detects exactly **18 frontmatter errors**:
     * 17 from the legacy books in `content/docs/books/` (all missing `description:`).
     * 1 from `content/docs/1-what-is-product-managment/what-is-product-managment.en.md` (Persian counterpart has `description: "مدیریت محصول چیست و چه تفاوتی با مدیریت پروژه دارد؟ در این مقاله جامع با وظایف، مهارت‌ها و نقش حیاتی مدیر محصول در موفقیت کسب‌وکارهای دیجیتال آشنا شوید."`, English file lacks `description:`).
  2. **12 Published Books vs 5 Auxiliary Pages**:
     * 12 of the 17 files represent actual published books whose Persian counterparts have specifications tables (`Escaping-the-Build-Trap`, `The-Lean-Product-Playbook`, `The-Lean-Startup`, `behind-every-great-product`, `build-better-products`, `human-blockers`, `storytelling-with-data`, `survival-guide-for-product-managers`, `talking-to-others`, `کتاب-inspired`, `کتاب-lean-analytics`, `کتاب-roadmap`).
     * 8 of these 12 have direct download shortcodes in Persian.
     * 5 files are non-book resources located in `content/docs/books/`: `okr-books` (reading list), `pm-club` (membership), `pm-courses` (workshop), `webinar-05-roadmap` (webinar), `webinar-06-listening` (webinar). These do not have specs tables or download links, but still strictly require `description:` in frontmatter to pass CI.
  3. **Books Section Index (`content/docs/books/_index.en.md`)**:
     * Body length is currently **0 bytes** (empty).
     * E2E test `T1.5` asserts: `content/docs/books/_index.en.md body must not be empty (>50 chars)`.
     * Persian `_index.md` contains 9 curated showcase cards (`{{< cards cols="3" >}}` ... `{{< card link="..." >}}`) and 7 domain categories.

---

### 1.5 E2E Baseline Test Execution
Execution of `python3 scripts/test_localization_e2e.py` showed:
* Total Tests: 21 (142 assertions).
* Passed: 11 tests.
* Failed: 10 tests (all within Milestone 3 scope):
  * `T1.3` (390 missing books)
  * `T1.4` (17 legacy books missing description & categories)
  * `T1.5` (9 legacy books missing `###` headings, `_index.en.md` empty body)
  * `T2.1` (Persian slug book missing)
  * `T3.1` (390 download shortcodes missing)
  * `T3.2` (17 legacy books missing `Books` category)
  * `T3.3` (390 specs tables missing)
  * `T4.1` (`verify_localization.py` exits code 1 with 408 issues: 390 missing files + 18 frontmatter issues)
  * `T4.3` (Hugo rendered page count delta: currently 307 EN pages, requires $\ge 677$ pages)
  * `T4.5` (`verify_localization.py --strict` fails)

---

## 2. Logic Chain

1. **Premise 1 (Deterministic Parity Scope)**:
   Observation 1.1 proves that `set(meta_slugs) == set(missing_en_slugs)`. Every missing book file in `content/docs/books/` has an exact 1-to-1 counterpart in `data/books_metadata.json` with zero missing slugs, zero orphaned records, and complete URLs/file sizes.
   * *Conclusion*: An automated Python generator iterating over `data/books_metadata.json` will resolve 100% of missing book files without manual slug mapping or URL guessing.

2. **Premise 2 (Zero-Placeholder Synthesis via Dual Tiers)**:
   Observation 1.2 proves that 206 of the 390 books (52.8%) match rich, structured conceptual data in `scripts/curated_books_data.py`, while the remaining 184 books possess complete Persian structural templates with page counts, authors, categories, and takeaways in `content/docs/books/<slug>.md`.
   * *Conclusion*: Generating 390 English books with zero placeholder text (`TODO`, `FIXME`, `lorem ipsum`) is completely achievable by adopting a two-tier strategy:
     * *Tier 1 (206 Curated Books)*: Translating and formatting the deep frameworks, summaries, and 2026 relevance from `CURATED_BOOKS`.
     * *Tier 2 (184 Domain Books)*: Extracting metadata and translating core takeaways, author, category, and 2026 relevance from the Persian source markdown.

3. **Premise 3 (Preservation of Unicode Decomposed Codepoints)**:
   Observation 1.3 proves that the Persian slug book and metadata record use decomposed NFD combining madda (`U+0627` + `U+0653`), and `verify_localization.py` matches filenames using raw string slicing (`fa_path[:-3] + ".en.md"`).
   * *Conclusion*: The generator must directly use `b["slug"]` without converting to precomposed NFC `آ`. Preserving the NFD byte sequence guarantees 1:1 filename matching in both git and Hugo across all operating systems.

4. **Premise 4 (Legacy Retrofit & Full CI Green)**:
   Observation 1.4 proves that `verify_localization.py` fails on 18 frontmatter errors: 17 legacy books in `content/docs/books/` and `what-is-product-managment.en.md`. Furthermore, `_index.en.md` has an empty body.
   * *Conclusion*: Milestone 3 cannot be marked complete by merely generating 390 files; the implementer must:
     1. Retrofit `description:`, `categories: ["Books"]`, and specs/downloads into the 17 legacy `.en.md` books.
     2. Add `description:` to `content/docs/1-what-is-product-managment/what-is-product-managment.en.md`.
     3. Populate `content/docs/books/_index.en.md` with localized showcase cards and categories.
     Doing so eliminates all 408 issues in `verify_localization.py` and produces exit code 0.

---

## 3. Caveats

1. **EPUB Format Exception**:
   One book (`triggers-creating-behavior-that-lasts-becoming-the-person-you-want`) has format `"EPUB"`, not `"PDF"`. The generator must dynamically read `format` from metadata (`book["format"]`) rather than hardcoding `"PDF"`.
2. **Download URL Character Encoding**:
   The download URLs in `books_metadata.json` contain URL-encoded percentage escapes (e.g., `%20`, `%D8%AE...`). The generator must write these URLs verbatim into the `book-download` shortcode without double-encoding or decoding.
3. **Hugo Compilation Performance**:
   Adding 390 English books will increase total content files from 572 to 962. Hugo `--renderToMemory` build time is anticipated to increase from ~12s to ~18-22s.

---

## 4. Conclusion & Actionable Implementation Plan

### 4.1 Recommended Generator Architecture: `scripts/generate_english_books.py`
The implementer agent (`coder_m3_1`) should create `scripts/generate_english_books.py` with the following modular components:

1. **Metadata Loading & Mapping**:
   * Load `data/books_metadata.json` (390 items).
   * Load `scripts/curated_books_data.py` (`CURATED_BOOKS`, 206 items) and build a fast lookup map: `slug -> curated_data`.
   * Standard Category Mapping:
     ```python
     CATEGORY_MAP = {
         "strategy-leadership": "Product Strategy & Leadership",
         "ux-design": "UX Design & Behavioral Psychology",
         "ai-technology": "AI & Technology in Product",
         "discovery-research": "Product Discovery & User Research",
         "growth-analytics": "Growth & Product Analytics",
         "management-career": "Career Development & Practical Skills",
         "lean-agile": "Lean Delivery & Agile Management",
         "reports-playbooks": "Industry Reports & Playbooks",
     }
     ```
2. **Author Extraction**:
   * If author has parentheses `... (Latin Name)`, extract Latin Name.
   * If author is in `KNOWN_AUTHORS` (from `scripts/enrich_and_deduplicate_books.py`), use English mapping.
   * If author is Persian-only (18 books), map known authors (e.g. `مهدی علیپور سخاوی` -> `"Mehdi Alipour Sakhavi"`, `مارتینا لاوچنگکو` -> `"Martina Lauchengco"`, etc.).
3. **Content Generation Pipeline (7 Components)**:
   * **Frontmatter**: English `title`, `date`, `description`, `tags`, `categories: ["Books"]`.
   * **Specs Table**: `| Book Specification | Details |` with Author, Category, Page Count, Format, File Size (`<size_mb> MB`), Target Audience.
   * **Section 1**: `### 📖 About the Book & Core Premise`
   * **Section 2**: `### 🔑 Key Takeaways & Core Frameworks` (4-5 markdown bullet points)
   * **Section 3**: `### 💡 Why This Book Matters in 2026`
   * **Section 4**: `### 🎯 Who Should Read This Book?`
   * **Section 5**: `### 📥 Download Book File` with `{{< book-download url="..." title="Download <Title> (Full English Edition)" size="..." format="..." lang="English" >}}`.
4. **Retrofit Legacy Files**:
   * Inject `description:` and `categories: ["Books"]` into all 17 legacy `.en.md` files.
   * For the 12 legacy book files, append specs table and download shortcode matching Persian counterparts.
   * Add `description:` to `content/docs/1-what-is-product-managment/what-is-product-managment.en.md`.
   * Populate `content/docs/books/_index.en.md` with localized English content.

---

## 5. Verification Method

To independently verify all findings and validate subsequent implementation:

### 5.1 Programmatic Slug Alignment & Metadata Check
```bash
python3 -c "
import json, os
books_dir = 'content/docs/books'
files = os.listdir(books_dir)
fa = {f[:-3] for f in files if f.endswith('.md') and not f.endswith('.en.md') and f != '_index.md'}
en = {f[:-6] for f in files if f.endswith('.en.md') and f != '_index.en.md'}
missing = fa - en
with open('data/books_metadata.json') as f:
    meta = json.load(f)
meta_slugs = {b['slug'] for b in meta}
assert len(meta) == 390
assert len(missing) == 390
assert meta_slugs == missing
print('✅ Slug parity verified: exactly 390 missing books matching metadata.')
"
```

### 5.2 Persian Slug Unicode Verification
```bash
python3 -c "
import unicodedata
slug = 'خلق-محصولات-آینده-راهنمای-هوش-مصنوعی-برای-مدیران-محصول'
assert not (slug == unicodedata.normalize('NFC', slug)), 'Must NOT be NFC'
assert slug == unicodedata.normalize('NFD', slug), 'Must be NFD'
assert slug[12:14] == '\u0627\u0653', 'Must contain decomposed alef + combining madda'
print('✅ Persian slug Unicode NFD decomposition verified.')
"
```

### 5.3 CI Localization Audit
```bash
python3 scripts/verify_localization.py
```
*Current state*: Returns exit code 1 with 408 issues (390 missing files + 18 frontmatter issues).  
*Post-implementation state*: Must return exit code 0 with `✅ SUCCESS: 100% English localization parity achieved!`.

### 5.4 E2E Test Suite
```bash
python3 scripts/test_localization_e2e.py
```
*Post-implementation state*: All 21 tests (Tiers 1-4) must PASS.

### 5.5 Hugo Compilation
```bash
hugo --renderToMemory
```
*Post-implementation state*: Returns exit code 0, rendering $\ge 677$ English pages (+407 delta from Persian parity).
