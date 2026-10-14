# Handoff Report: Hugo Site Architecture & English Localization Survey

**Author**: Explorer Survey 1 (Hugo Site Architecture)  
**Date**: 2026-10-09T17:12:00Z  
**Working Directory**: `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_survey_1`  

---

## 1. Observation

### 1.1 Hugo Configuration & Multilingual Setup
- **Config File**: `/Users/sotoon/personal/theminiceo/hugo.toml` (252 lines total).
- **Core Parameters**:
  - Line 1: `baseURL = 'https://theminiceo.ir'`
  - Line 2: `defaultContentLanguage = 'fa'`
  - Line 4: `theme = 'hextra'`
  - Line 10: `ignoreFiles = ['content/pdfs/.*']`
  - Line 21: `defaultContentLanguageInSubdir = false`
    - Persian content renders at root `/` (e.g., `/docs/books/`).
    - English content renders under `/en/` prefix (e.g., `/en/docs/books/`).
  - Lines 17–19: Taxonomies configured: `category = "categories"` and `tag = "tags"`.
  - Lines 47–50: Goldmark markdown renderer with `unsafe = true` (HTML passthrough enabled).
- **Language Configurations**:
  - Lines 23–31 (`[languages.fa]`):
    - `label = 'فارسی'`, `locale = 'fa-IR'`, `direction = 'rtl'`, `weight = 1`, `title = 'مدیرعامل کوچک | TheMiniCEO'`.
  - Lines 33–41 (`[languages.en]`):
    - `label = 'English'`, `locale = 'en'`, `direction = 'ltr'`, `weight = 2`, `title = 'TheMiniCEO'`.
- **Navigation Menus**:
  - Both Persian (`[[languages.fa.menu.main]]`, lines 52–110) and English (`[[languages.en.menu.main]]`, lines 111–168) have complete 8-item menus:
    - `docs` (`/docs/`), `courses` (`/course/`), `library` (`/docs/books/`), `reports` (`/docs/reports/`), `frameworks` (`/frameworks/`), `consulting` (`/product-consultant/`), `about` (`/about/`), `products` (`Zendo`), `search`.
- **Module Mounts**:
  - Lines 217–237 mount standard root directories: `content`, `data`, `layouts`, `i18n`, `archetypes`, `assets`, `static`.
  - Lines 242–252 mount static English image routes:
    - `content/docs/Archive/images` → `static/en/docs/archive/images`
    - `content/docs/Books/images` → `static/en/docs/books/images`
    - `content/images` → `static/en/images`
    - `content/course/images` → `static/en/course/images`

### 1.2 Content Organization & Repository-Wide Inventory
- **Multilingual Content Structure**:
  - Hugo uses co-located files within a single content directory tree.
  - Persian (default language) files: `<filename>.md`
  - English files: `<filename>.en.md`
- **Audit of Markdown Content (`content/`)**:
  - Total markdown files across repository: 704
  - Total Persian (`*.md`) files: 556
  - Total English (`*.en.md`) files: 148
  - Across 25 directories, **23 directories already have 100% FA ↔ EN parity**:
    - Root (`content/`): 10 FA, 10 EN
    - `blog`: 1 FA, 1 EN
    - `categories` and 8 subcategories: 9 FA, 9 EN
    - `course`: 9 FA, 9 EN
    - `docs`: 1 FA, 1 EN
    - `docs/1-what-is-product-managment` through `docs/6-resources-and-tools`: 27 FA, 27 EN
    - `docs/archive`: 62 FA, 62 EN
    - `frameworks`: 9 FA, 9 EN
    - `tags`: 1 FA, 1 EN
  - **Only 2 content directories lack English counterparts**:
    1. `content/docs/books/`: 408 Persian files total.
       - 1 is section index (`_index.md`, already has `_index.en.md`).
       - 17 existing books have `.en.md` translations (e.g. `Escaping-the-Build-Trap.en.md`, `The-Lean-Startup.en.md`).
       - **390 books lack English versions (`.en.md`)**.
    2. `content/docs/reports/`: 18 Persian files total.
       - 1 is section index (`_index.md`, already has `_index.en.md`).
       - **17 reports lack English versions (`.en.md`)**.
  - Excluded directories:
    - `content/docs/books/_drafts`: 1 file (`growth-hacking.md`), drafts excluded by Hugo and project requirements.
    - `content/pdfs/`: binary assets excluded in `hugo.toml` (`ignoreFiles = ['content/pdfs/.*']`).
    - `.obsidian/`: editor metadata directory.
  - **Total missing English files**: Exactly **407 files** (390 books + 17 reports).

### 1.3 Data Sources for Generation
- **Books Metadata**:
  - `/Users/sotoon/personal/theminiceo/data/books_metadata.json` contains a JSON array of exactly 390 items.
  - Verification: 390 out of 390 `slug` fields match existing Persian `.md` files in `content/docs/books/` (e.g. `100-things-every-designer-needs-to-know-about-people`).
  - Available fields per entry: `title`, `slug`, `format`, `size_str`, `category_slug`, `category_title`, `download_url`.
- **Reports Metadata**:
  - `/Users/sotoon/personal/theminiceo/scripts/setup_reports_section.py` lines 8–370 contain the structured `reports_map` dictionary for all 17 reports.
  - Available fields per entry: `new_file`, `title`, `category`, `summary`, `dl_url`, `size`, `key_points`.

### 1.4 Shortcodes, Layouts, and i18n
- **Theme**: Hextra (`themes/hextra`).
- **Translation Files (`i18n/`)**:
  - `i18n/fa.yaml` (102 lines) and `i18n/en.yaml` (102 lines).
  - 100% key parity between Persian and English UI translations.
- **Shortcode `book-download.html` (`/Users/sotoon/personal/theminiceo/layouts/shortcodes/book-download.html`)**:
  - Accepts `.Get "url"`, `.Get "title"`, `.Get "size"`, `.Get "format"`, `.Get "lang"`.
  - **CRITICAL DEFECT DETECTED**:
    - Lines 3, 26, 30, 33, 43 contain hardcoded Persian text without language detection:
      - Line 3: Default title `"دانلود مستقیم نسخه اصلی کتاب"`
      - Line 26: `"حجم: {{ $size }}"` (hardcoded `"حجم: "`)
      - Line 30: `"زبان: {{ $lang }}"` (default `"انگلیسی"`, hardcoded `"زبان: "`)
      - Line 33: `<span ...>سرور پرسرعت داخلی</span>` (hardcoded Persian badge)
      - Line 43: `<span>دریافت فایل کتاب</span>` (hardcoded button label)
  - Other shortcodes like `framework-tool.html` and `buy-button.html` are properly localized:
    - `framework-tool.html` uses `{{- if eq $lang "en" }}`.
    - `buy-button.html` uses `{{ T "buyDefaultText" }}`.
- **Language Switcher Behavior**:
  - `layouts/_partials/navbar.html` (lines 121–134) calls `themes/hextra/layouts/_partials/utils/lang-link.html`.
  - `lang-link.html` inspects `$page.AllTranslations`.
  - If `<slug>.en.md` exists, clicking `EN` opens the translated page. If missing, it falls back to homepage (`/en/`).

### 1.5 Hugo Build Performance & Diagnostics
- **Command Tested**: `hugo --renderToMemory`
- **Binary**: Hugo v0.167.0+extended+withdeploy darwin/arm64
- **Exit Code**: 0 (Clean build)
- **Execution Time**: 12.768 seconds
- **Current Rendered Page Output**:
  ```
                    │ FA  │ EN  
  ──────────────────┼─────┼─────
   Pages            │ 723 │ 270 
   Paginator pages  │   0 │   0 
   Non-page files   │ 246 │   0 
   Static files     │ 489 │ 489 
   Processed images │  59 │   0 
   Aliases          │ 145 │   8 
   Cleaned          │   0 │   0 
  ```
- **Deprecation Warnings**: 4 harmless deprecation notices from Hextra upstream templates:
  - `WARN .Site.Data was deprecated in Hugo v0.156.0`
  - `WARN .Site.Languages was deprecated in Hugo v0.156.0`
  - `WARN .Language.LanguageName was deprecated in Hugo v0.158.0`
  - `WARN .Site.Sites and .Page.Sites was deprecated in Hugo v0.156.0`
- **Error Count**: 0 errors.

### 1.6 Frontmatter Structure Standards
- Persian books generated from dataset (`docs/books/*.md`) follow this pattern:
  - Frontmatter: `title`, `date`, `description`, `tags`, `categories`.
  - Specifications table: Author, Domain, Pages, Format, File size, Target audience.
  - Sections: About book & core premise, Key takeaways, 2026 relevance, Audience, Download shortcode.
- Note on existing English files:
  - 148 `.en.md` files currently exist.
  - All 148 have `title`.
  - 137 have `date`.
  - Only 57 have `description` (91 older files lack `description`).
  - All 390 target Persian books and all 17 target Persian reports currently have `description` in their frontmatter.

---

## 2. Logic Chain

1. **Language & Routing Topology** (from Obs 1.1):
   - Hugo is configured with `defaultContentLanguage = 'fa'` and `defaultContentLanguageInSubdir = false`.
   - Persian pages reside at root routes (`/docs/books/<slug>/`), and English pages reside under `/en/` (`/en/docs/books/<slug>/`).
   - Hugo pairs translation variants strictly by filename stem (`<slug>.md` ↔ `<slug>.en.md`).
2. **Missing Page Scope** (from Obs 1.2, 1.3):
   - Out of 556 Persian content files, 148 already have `.en.md` counterparts with 100% parity across 23 subdirectories.
   - The remaining gaps are strictly confined to `content/docs/books/` (390 missing) and `content/docs/reports/` (17 missing).
   - `390 + 17 = 407` total files required.
   - `data/books_metadata.json` covers all 390 books with 100% slug matching.
   - `scripts/setup_reports_section.py` covers all 17 reports.
3. **Language Switcher Integrity** (from Obs 1.4):
   - `lang-link.html` evaluates `$page.AllTranslations`.
   - Because English counterparts are currently missing for 407 pages, clicking the `EN` language toggle redirects visitors away from the article to `/en/`.
   - Generating the 407 `<slug>.en.md` files will automatically enable contextual bilingual toggling for every single page.
4. **Shortcode Defect & Parity Requirement** (from Obs 1.4):
   - Acceptance criteria require: *"No placeholder dummy text or untranslated Persian blocks inside the generated English pages."*
   - Even if English markdown pages provide English parameters to `{{< book-download ... >}}`, the shortcode template `/Users/sotoon/personal/theminiceo/layouts/shortcodes/book-download.html` hardcodes `"حجم: "`, `"زبان: "`, `"سرور پرسرعت داخلی"`, and `"دریافت فایل کتاب"`.
   - Therefore, the shortcode template must be upgraded to support English labels conditionally or via i18n to achieve true English parity.
5. **Compilation Viability** (from Obs 1.5):
   - `hugo --renderToMemory` compiles in ~12s with exit code 0.
   - Adding 407 `.en.md` pages will increase rendered English pages by ~407 content pages plus associated taxonomy terms, bringing English page count (~677+) near full parity with Persian (723).

---

## 3. Caveats

1. **Mount Casing on Linux CI/CD**:
   - `hugo.toml` line 245 mounts `content/docs/Books/images` (capital `B`).
   - On macOS (APFS case-insensitive), this succeeds transparently. On case-sensitive Linux environments (e.g. GitHub Actions / Cloudflare Pages), if the directory is `content/docs/books/images`, this mount could fail if not kept lowercase.
2. **Legacy `.en.md` Files Missing Description**:
   - 91 pre-existing `.en.md` files (mostly under `docs/archive/`) lack a `description` field.
   - The verification script (`verify_localization.py`) should ensure that all newly generated 407 book and report files have `title`, `date`, and `description`, while deciding whether to flag or exempt legacy archive pages without descriptions.
3. **Shortcode Modifying Permission**:
   - This survey agent operated in read-only mode and did not modify `layouts/shortcodes/book-download.html`. The proposed code snippet is provided below for the implementing agent.

---

## 4. Conclusion & Actionable Recommendations

### 4.1 Scope of English Generation
- **Target Count**: Exactly 407 `.en.md` files to generate:
  - **390 Books** in `content/docs/books/<slug>.en.md` using `data/books_metadata.json` and Persian source files.
  - **17 Reports** in `content/docs/reports/<slug>.en.md` using `scripts/setup_reports_section.py` and Persian source files.
- **Excluded**: `content/docs/books/_drafts/`, `content/pdfs/`, `.obsidian/`.

### 4.2 Standard Structure for English Book Pages
Each generated `content/docs/books/<slug>.en.md` should contain:
```yaml
---
title: "<Canonical English Title>"
date: <Date matching Persian or metadata>
description: "<Concise English 1-2 sentence description>"
tags: ["Library", "<English Category>", "Product Management"]
categories: ["Books"]
---
```
Followed by:
1. Markdown specifications table (`| Book Specifications | Details |`)
2. `### 📖 About the Book & Core Premise`
3. `### 🔑 Key Takeaways & Core Lessons`
4. `### 💡 Why This Book Matters in 2026`
5. `### 🎯 Target Audience`
6. `### 📥 Download Book File`
7. `{{< book-download url="..." title="..." size="..." format="PDF" lang="English" >}}`

### 4.3 Proposed Patch for `layouts/shortcodes/book-download.html`
To prevent hardcoded Persian text on English book and report pages, replace `/Users/sotoon/personal/theminiceo/layouts/shortcodes/book-download.html` with:

```html
{{/* Book Download Shortcode for Hextra Theme (Multilingual Support) */}}
{{ $isEn := eq .Page.Language.Lang "en" }}
{{ $defaultTitle := cond $isEn "Direct Download Original Book Edition" "دانلود مستقیم نسخه اصلی کتاب" }}
{{ $defaultLang := cond $isEn "English" "انگلیسی" }}
{{ $url := .Get "url" | default (.Get 0) }}
{{ $title := .Get "title" | default $defaultTitle }}
{{ $size := .Get "size" | default "" }}
{{ $format := .Get "format" | default "PDF" }}
{{ $lang := .Get "lang" | default $defaultLang }}
{{ $sizePrefix := cond $isEn "Size: " "حجم: " }}
{{ $langPrefix := cond $isEn "Language: " "زبان: " }}
{{ $serverBadge := cond $isEn "High-speed Direct CDN" "سرور پرسرعت داخلی" }}
{{ $btnText := cond $isEn "Download Book File" "دریافت فایل کتاب" }}

<div class="book-download-box hx:my-8 hx:p-5 hx:rounded-2xl hx:bg-gradient-to-br hx:from-blue-50/70 hx:via-indigo-50/40 hx:to-slate-50/60 hx:dark:from-blue-950/20 hx:dark:via-indigo-950/15 hx:dark:to-slate-900/30 hx:border hx:border-blue-200/80 hx:dark:border-blue-800/40 hx:shadow-sm">
  <div class="hx:flex hx:flex-col hx:sm:flex-row hx:items-start hx:sm:items-center hx:justify-between hx:gap-4">
    <div class="hx:flex hx:items-center hx:gap-3.5">
      <div class="hx:w-12 hx:h-12 hx:rounded-xl hx:bg-blue-600 hx:text-white hx:flex hx:items-center hx:justify-center hx:shrink-0 hx:shadow-md hx:shadow-blue-500/20">
        <svg xmlns="http://www.w3.org/2000/svg" class="hx:w-6 hx:h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <div>
        <div class="hx:text-base hx:font-bold hx:text-slate-900 hx:dark:text-white">
          {{ $title }}
        </div>
        <div class="hx:flex hx:items-center hx:gap-2 hx:mt-1 hx:text-xs hx:text-slate-600 hx:dark:text-slate-400">
          <span class="hx:inline-flex hx:items-center hx:px-2 hx:py-0.5 hx:rounded-md hx:font-medium hx:bg-blue-100 hx:text-blue-800 hx:dark:bg-blue-900/50 hx:dark:text-blue-300">
            {{ $format }}
          </span>
          {{ if $size }}
            <span>•</span>
            <span>{{ $sizePrefix }}{{ $size }}</span>
          {{ end }}
          {{ if $lang }}
            <span>•</span>
            <span>{{ $langPrefix }}{{ $lang }}</span>
          {{ end }}
          <span>•</span>
          <span class="hx:text-emerald-600 hx:dark:text-emerald-400 hx:font-medium">{{ $serverBadge }}</span>
        </div>
      </div>
    </div>

    <div class="hx:w-full hx:sm:w-auto hx:flex hx:justify-end">
      <a href="{{ $url }}" target="_blank" rel="noopener noreferrer" download class="hx:w-full hx:sm:w-auto hx:inline-flex hx:items-center hx:justify-center hx:gap-2 hx:py-2.5 hx:px-6 hx:rounded-xl hx:text-sm hx:font-bold hx:text-white hx:bg-blue-600 hx:hover:bg-blue-700 hx:active:scale-[0.98] hx:shadow-md hx:shadow-blue-600/25 hx:transition-all hx:no-underline">
        <svg xmlns="http://www.w3.org/2000/svg" class="hx:w-4 hx:h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        <span>{{ $btnText }}</span>
      </a>
    </div>
  </div>
</div>
```

---

## 5. Verification Method

To independently verify the observations and conclusions:

1. **Verify Missing Page Inventory**:
   ```bash
   python3 -c "
   from pathlib import Path
   content = Path('content')
   missing = []
   for md in content.rglob('*.md'):
       if md.name.endswith('.en.md') or any(ex in str(md) for ex in ['_drafts', 'pdfs', '.obsidian']):
           continue
       if not md.with_name(md.stem + '.en.md').exists():
           missing.append(md)
   print(f'Total missing .en.md: {len(missing)}')
   assert len(missing) == 407, f'Expected 407, got {len(missing)}'
   "
   ```
2. **Verify Book Metadata Slug Match**:
   ```bash
   python3 -c "
   import json
   from pathlib import Path
   with open('data/books_metadata.json') as f:
       books = json.load(f)
   assert len(books) == 390
   for b in books:
       assert (Path('content/docs/books') / f\"{b['slug']}.md\").exists()
   print('390/390 slugs verified!')
   "
   ```
3. **Verify Clean Hugo Build**:
   ```bash
   hugo --renderToMemory
   ```
   Confirm exit code is 0, errors are 0, and current pages are FA: 723, EN: 270.

4. **Invalidation Conditions**:
   - If any Persian file outside `docs/books` or `docs/reports` lacks an `.en.md` file.
   - If `hugo --renderToMemory` fails or outputs non-zero exit code.
   - If `data/books_metadata.json` items fail to map to corresponding Persian files.
