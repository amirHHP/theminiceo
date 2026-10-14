# Milestone 2 Specification Mining Report: Reports Localization & Shortcode i18n

**Author**: `spec_miner_m2_1`  
**Parent**: `orchestrator_2` (`1390bbb4-2296-47f7-8f97-a4b7fde0fc3d`)  
**Target Milestone**: Milestone 2 (Reports English Localization & Shortcode i18n)  
**Date**: 2026-10-10  

---

## 1. Observation

Direct observations from codebase inspection, specification definitions, and test suite execution:

1. **Original Request (`.agents/teamwork/ORIGINAL_REQUEST.md`)**:
   - **§ R3 (English Localization for Reports)**:
     > "Generate corresponding English pages (`*.en.md`) for all 17 reports in `content/docs/reports/`. Translate titles, summaries, key research findings, and preserve download links with proper formatting."
   - **§ R4 (Hugo Build Verification & Site Integrity)**:
     > "`hugo --renderToMemory` must run and exit code 0 with zero build errors. No broken shortcodes, corrupted markdown formatting, or invalid frontmatter syntax."

2. **Project Architecture Contract (`.agents/teamwork/orchestrator_2/PROJECT.md`)**:
   - Lines 20-21:
     - Feature 2: Multilingual Shortcode Support (`layouts/shortcodes/book-download.html` conditionally supporting English labels).
     - Feature 3: Reports English Localization (Generate 17 English reports in `content/docs/reports/*.en.md` from `setup_reports_section.py`).
   - Lines 43-46 (Shortcode Contract):
     - Detects `.Page.Language.Lang == "en"`.
     - If English: renders `"Size: "`, `"Language: "`, `"High-speed Direct CDN"`, `"Download Book File"`.
     - If Persian: renders `"حجم: "`, `"زبان: "`, `"سرور پرسرعت داخلی"`, `"دریافت فایل کتاب"`.

3. **Existing Persian Reports Generator (`scripts/setup_reports_section.py`)**:
   - Contains `reports_map` declaring exactly 17 reports (lines 8–264) with fields: `old_file`, `new_file`, `title`, `category`, `summary`, `dl_url`, `size`, `key_points`.
   - Persian generator function `generate_report_md(report)` (lines 266–299) produces:
     - Frontmatter: YAML delimiters `---`, `title`, `date: 2026-09-16`, `description`, `tags`, `categories: ["گزارش‌ها"]`, `aliases: [/docs/books/<old_slug>/]`.
     - Body: Intro paragraph, `### محورها و دستاوردهای کلیدی گزارش:`, `* <key_points>`, `### این گزارش برای چه کسانی مفید است؟`, `### 📥 دریافت فایل کامل گزارش`, `{{< book-download url="..." title="..." size="..." format="PDF" >}}`.
   - Existing section index `content/docs/reports/_index.en.md` (lines 342–354) already exists and contains 542 bytes, valid TOML frontmatter (`title = 'Reports & Industry Benchmarks'`), and 204 characters body prose.

4. **Shortcode Template (`layouts/shortcodes/book-download.html`)**:
   - Currently hardcoded for Persian only:
     - Line 3: `default "دانلود مستقیم نسخه اصلی کتاب"`
     - Line 6: `default "انگلیسی"`
     - Line 26: `حجم: {{ $size }}`
     - Line 30: `زبان: {{ $lang }}`
     - Line 33: `<span ...>سرور پرسرعت داخلی</span>`
     - Line 43: `<span>دریافت فایل کتاب</span>`
   - Lacks language branching (`.Page.Language.Lang` or `$isEn`).

5. **E2E Test Execution (`scripts/test_localization_e2e.py`) Baseline**:
   - Executing `python3 scripts/test_localization_e2e.py -v` confirmed 10 tests failing directly on Milestone 2 scope:
     - `T1.2`: Missing all 17 `content/docs/reports/*.en.md` files (17 assertion errors).
     - `T1.4`: 0/17 reports have `title`, `date`, `description`, `categories` (68 assertion errors).
     - `T1.5`: 0/17 reports have body >100 chars and structured markdown headings `###` (34 assertion errors).
     - `T2.2`: Missing Persian-slug report `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md` (6 assertion errors).
     - `T2.4`: 17 reports flagged for zero Persian titles check (17 assertion errors).
     - `T2.5`: 17 reports checked for zero dummy placeholders (17 assertion errors).
     - `T2.6`: Missing boundary large report `hbr-2022-11-12.en.md` (~90.4 MB) and small report `heap-digital-experiences-insights-report2.en.md` (~400 KB) (4 assertion errors).
     - `T3.1`: 17 report download URLs mismatched against `setup_reports_section.py` (17 assertion errors).
     - `T3.2`: 17 reports missing `categories: ["Reports"]` (17 assertion errors).
     - `T3.4`: `book-download.html` fails conditional language check, English button text, English size label, English language label, and CDN badge (5 assertion errors).
     - `T3.5`: `hbr-2022-11-12.en.md` missing for ISO date format check (1 assertion error).

6. **Audit Tool Contract (`scripts/verify_localization.py`)**:
   - Lines 532, 587–606, 621–628, 650–679:
     - Strictly requires `description` in frontmatter for reports.
     - Enforces non-empty markdown body > 50 bytes.
     - Rejects any Persian characters in `title` and `description`.
     - In `--strict` mode: requires `categories` to contain `"Reports"` (or `"گزارش"`), checks for `{{< book-download` shortcode, checks ISO 8601 date, and scans for placeholder tokens (`TODO`, `FIXME`, `TBD`, `lorem ipsum`, `[placeholder]`).

---

## 2. Logic Chain

1. **Parity and Co-Location Rule**:
   - `content/docs/reports/` has 17 active Persian `.md` files (and 1 `_index.md`).
   - Per R3 and T1.2, exactly 17 `.en.md` companion files must be created co-located in `content/docs/reports/`.
   - The stem of each English file must strictly match the Persian file: `file[:-3] + ".en.md"`.
   - Specifically, the Persian-slug report `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md` MUST have companion `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md` (tested by T2.2).

2. **Frontmatter Schema & Content Standards**:
   - YAML delimiter `---` must wrap metadata.
   - Fields:
     - `title`: Translated English title, zero Persian characters (T2.4).
     - `date`: Valid ISO 8601 date `YYYY-MM-DD` (e.g. `2026-09-16`) (T1.4, T3.5, verify_localization strict).
     - `description`: Translated English summary string, zero Persian characters, non-empty (T1.4, T2.4, verify_localization).
     - `tags`: English tag list, e.g. `["Reports", "<English Category>", "Product Management", "Market Analysis"]`.
     - `categories`: Must strictly be `["Reports"]` (T1.4, T3.2, verify_localization strict).
     - `aliases`: Preserve legacy redirects from `/docs/books/<old_slug>/` (and `/docs/reports/<old_slug>/` where applicable).

3. **Body Structure and Headings**:
   - Body must be > 100 characters (T1.5, T2.2).
   - Must contain structured markdown headings matching regex `^###?\s+` (T1.5).
   - Headings must have zero Persian characters (T2.4).
   - Recommended 3-part heading schema:
     1. `### Key Research Findings & Takeaways` (contains 4 bulleted English translation points from `key_points`).
     2. `### Who Should Read This Report?` (audience definition).
     3. `### 📥 Download Full Report` (houses the shortcode).

4. **Shortcode Invocations & Parameters in Reports**:
   - Shortcode: `{{< book-download url="..." title="..." size="..." format="PDF" lang="English" >}}`.
   - `url`: Must match verbatim the `dl_url` specified in `setup_reports_section.py` (T3.1).
   - `title`: English download card title, e.g. `"Download The 2024 State of Product Management Report"`.
   - `size`: English size representation matching `setup_reports_section.py`:
     - Boundary requirement for `hbr-2022-11-12.en.md`: size must contain `"90.4"` or `"90"` (e.g. `"90.4 MB"`) (T2.6).
     - Boundary requirement for `heap-digital-experiences-insights-report2.en.md`: size must contain `"400"` or `"0.4"` (e.g. `"400 KB"`) (T2.6).
     - All other reports should use standard `"X.X MB"` notation.
   - `format`: `"PDF"`.
   - `lang`: `"English"`.

5. **Shortcode Template Multilingual Architecture**:
   - `layouts/shortcodes/book-download.html` must detect language:
     `{{ $isEn := eq .Page.Language.Lang "en" }}` (or `{{ if eq .Page.Language.Lang "en" }}`).
   - English mode strings:
     - Size label: `"Size: "` (T3.4).
     - Language label: `"Language: "` (T3.4).
     - Server badge: `"High-speed Direct CDN"` (T3.4).
     - Button text: `"Download Book File"` (T3.4).
     - Default title: `"Download Book File"` or `"Direct Download"`.
     - Default language parameter: `"English"`.
   - Persian mode strings preserved:
     - Size label: `"حجم:"` or `"حجم: "` (T3.4).
     - Language label: `"زبان: "`.
     - Server badge: `"سرور پرسرعت داخلی"`.
     - Button text: `"دریافت فایل کتاب"` (T3.4).
     - Default title: `"دانلود مستقیم نسخه اصلی کتاب"`.
     - Default language parameter: `"انگلیسی"`.

---

## 3. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Report Content | 17 English Report Files Generation | Create 1:1 `.en.md` companion files for all 17 canonical reports in `content/docs/reports/` | Persian report `.md` files + `setup_reports_section.py` | 17 `.en.md` files in `content/docs/reports/` | Test T1.2 fails if any of the 17 files is missing | `ORIGINAL_REQUEST.md` § R3; `PROJECT.md` M2; `test_localization_e2e.py:288` |
| 2 | Report Content | Section Index Parity | Maintain `content/docs/reports/_index.en.md` with English metadata and intro body > 50 chars | `content/docs/reports/_index.md` | `_index.en.md` with TOML frontmatter & body | Test T1.2 fails if missing; T1.5 fails if body < 50 chars | `test_localization_e2e.py:291,468` |
| 3 | Frontmatter | Reports Frontmatter Completeness | Enforce YAML frontmatter containing `title`, `date`, `description`, `tags`, `categories: ["Reports"]`, and `aliases` | English metadata strings | Valid YAML frontmatter block | Test T1.4 and `verify_localization.py` fail if any field missing | `test_localization_e2e.py:355`; `verify_localization.py:542` |
| 4 | Frontmatter | Taxonomy Category Enforcement | Reports must have `categories: ["Reports"]` in frontmatter | Frontmatter `categories` array | Hugo taxonomy `/en/categories/reports/` | Test T3.2 and `verify_localization.py --strict` fail if "Reports" absent | `test_localization_e2e.py:743`; `verify_localization.py:671` |
| 5 | Report Body | Markdown Structure & Minimum Length | Report body must have length > 100 characters and include structured `###` headings | English prose + research findings | Markdown sections with `###` headings | Test T1.5 fails if <100 chars or lacks `###` heading | `test_localization_e2e.py:421` |
| 6 | Report Body | Key Research Takeaways Localization | Translate the 4 bulleted research points from `key_points` into English | Persian `key_points` array from `setup_reports_section.py` | 4 bulleted takeaways under `### Key Research Findings & Takeaways` | Fails user quality criteria if untranslated | `ORIGINAL_REQUEST.md` § R3; `setup_reports_section.py:17` |
| 7 | Shortcode Template | Multilingual Download Card | Update `layouts/shortcodes/book-download.html` to branch on `.Page.Language.Lang == "en"` | Hugo page language context + shortcode params | Localized HTML card (EN or FA) | Test T3.4 fails if labels or language condition missing | `PROJECT.md` § Feature 2; `test_localization_e2e.py:825` |
| 8 | Shortcode Usage | Report Download Shortcode Placement | Embed `{{< book-download url="..." title="..." size="..." format="PDF" lang="English" >}}` in report body | Shortcode parameters | Rendered download button/card | Test T2.2 and `verify_localization.py --strict` fail if shortcode missing | `test_localization_e2e.py:524`; `verify_localization.py:652` |
| 9 | URL Integrity | CDN Download URL Exact Matching | Cross-reference report download URLs against authoritative CDN endpoints | CDN URLs in `setup_reports_section.py` | Exact `dl_url` strings in shortcodes | Test T3.1 fails if URL does not match metadata | `test_localization_e2e.py:675`; `setup_reports_section.py:15` |
| 10 | Quality Control | Zero Untranslated Persian Text | Guarantee zero Persian characters in `title`, `description`, and markdown headings (`^#`) | Generated English content | Pure English metadata & headings | Test T2.4 and `verify_localization.py` fail if Persian regex matches | `test_localization_e2e.py:556`; `verify_localization.py:552,600` |
| 11 | Quality Control | Zero Placeholder Tokens | Prevent dummy tokens (`TODO`, `FIXME`, `TBD`, `lorem ipsum`, `[placeholder]`) in reports | Generated English content | Fully finalized production text | Test T2.5 and `verify_localization.py --strict` fail if regex matches | `test_localization_e2e.py:609`; `verify_localization.py:641` |
| 12 | Navigation & Menus | Multilingual Reports Nav Route | Site navigation links `/docs/reports/` for Persian and `/en/docs/reports/` for English | `hugo.toml` menu configs | Functional Hugo section routes | Hugo build errors or 404s if menu broken | `hugo.toml:68,127`; `test_localization_e2e.py:1083` |

---

## 4. Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Persian Slug Report | File `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md` | Must be named with exact Persian Unicode slug companion to `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md`. Title and description must be in English. Shortcode must be present. Verified by T2.2 (6 assertions). |
| 2 | Extreme Large File Size | `hbr-2022-11-12.en.md` (90.4 MB PDF) | Shortcode `size` parameter MUST include `"90.4"` or `"90"` (e.g. `size="90.4 MB"`). Verified by T2.6. |
| 3 | Extreme Small File Size | `heap-digital-experiences-insights-report2.en.md` (400 KB PDF) | Shortcode `size` parameter MUST include `"400"` or `"0.4"` (e.g. `size="400 KB"`). Verified by T2.6. |
| 4 | ISO Date Consistency | `hbr-2022-11-12.en.md` date format | Must strictly match `^\d{4}-\d{2}-\d{2}` (e.g. `2026-09-16`). Verified by T3.5 and strict audit. |
| 5 | Legacy URL Redirection | Slug change from `1666697156021.md` to `iran-startup-ecosystem-report-techrasa-1400.md` | Must preserve `aliases: [/docs/books/1666697156021/, /docs/reports/1666697156021/]` to avoid broken incoming links. |
| 6 | URL Encoding in Shortcode | Persian filename in URL: `https://dl.theminiceo.ir/%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20...` | The URL in `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md` MUST match verbatim the percent-encoded URL in `setup_reports_section.py` line 180. Verified by T3.1. |
| 7 | Quotation Marks & Colons in Title | Titles containing parentheses or colons, e.g. `Future of Product Management Report 2023: Enterprise Edition` | Frontmatter YAML must properly quote strings (`title: "..."`) to prevent YAML parser errors with colons. |
| 8 | Shortcode Fallback in Missing Param | Calling `{{< book-download url="..." >}}` without explicit `title` or `size` | Shortcode template must use defaults: English title defaults to `"Download Book File"`, Persian defaults to `"دانلود مستقیم نسخه اصلی کتاب"`. |

---

## 5. Authoritative Specification for the 17 English Reports

Below is the complete, canonical specification matrix for generating all 17 English report files (`content/docs/reports/<slug>.en.md`):

### Inventory & Metadata Specifications

| # | Filename (`.en.md`) | Companion (`.md`) | Canonical Title (EN) | Description (EN) | Category | Tags | Download URL (`dl_url`) | Size |
|---|---------------------|-------------------|----------------------|------------------|----------|------|-------------------------|------|
| 1 | `the-2024-state-of-product-management-report.en.md` | `the-2024-state-of-product-management-report.md` | The 2024 State of Product Management Report | Annual benchmark report analyzing product management challenges, team structures, tooling, and AI integration in 2024. | State of Product Management | `["Reports", "State of Product Management", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/The-2024-State-of-Product-Management-Report.pdf` | `3.8 MB` |
| 2 | `the-state-of-product-management-annual-report-2023.en.md` | `the-state-of-product-management-annual-report-2023.md` | The State of Product Management Annual Report 2023 | Comprehensive survey analyzing product manager compensation, tooling, prioritization frameworks, and team dynamics in 2023. | State of Product Management | `["Reports", "State of Product Management", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/The-State-of-Product-Management-Annual-Report-2023.pdf` | `12.2 MB` |
| 3 | `the-2022-state-of-product-management-report-by-productplan.en.md` | `the-2022-state-of-product-management-report-by-productplan.md` | The 2022 State of Product Management Report by ProductPlan | ProductPlan industry study on remote product collaboration, strategic roadmap alignment, and organizational challenges in 2022. | State of Product Management | `["Reports", "State of Product Management", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/The-2022-State-of-Product-Management-Report-by-ProductPlan.pdf` | `5.5 MB` |
| 4 | `wef-future-of-jobs-report-2025.en.md` | `wef-future-of-jobs-report-2025.md` | WEF Future of Jobs Report 2025 | World Economic Forum benchmark report examining labor market transformations, AI automation, and essential workforce skills through 2025 and beyond. | Future of Work & Skills | `["Reports", "Future of Work & Skills", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/WEF_Future_of_Jobs_Report_2025.pdf` | `14.0 MB` |
| 5 | `product-leadership-census-2023-v2.en.md` | `product-leadership-census-2023-v2.md` | Product Leadership Census 2023 | Global census of Chief Product Officers (CPOs) and VPs of Product analyzing organizational structures, reporting lines, and executive strategy. | Product Leadership & People | `["Reports", "Product Leadership & People", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/Product%20Leadership%20Census_2023_v2.pdf` | `7.3 MB` |
| 6 | `fpmr-2023-enterprise.en.md` | `fpmr-2023-enterprise.md` | Future of Product Management Report 2023: Enterprise Edition | Analysis of digital transformation, enterprise agile operating models, and large-scale product development architectures. | State of Product Management | `["Reports", "State of Product Management", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/FPMR-2023_enterprise.pdf` | `1.1 MB` |
| 7 | `the-future-of-product-2024.en.md` | `the-future-of-product-2024.md` | The Future of Product 2024 | Forward-looking perspectives on generative AI agents, automated workflows, and paradigm shifts shaping next-generation software products. | Future of Work & Skills | `["Reports", "Future of Work & Skills", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/The_Future_of_Product_-_2024.pdf` | `9.6 MB` |
| 8 | `amplitude-product-report-2022.en.md` | `amplitude-product-report-2022.md` | Amplitude Product Report 2022 | Behavioral analytics study of active digital users examining engagement patterns, retention benchmarks, and product-led growth drivers. | Data Analytics & User Behavior | `["Reports", "Data Analytics & User Behavior", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/Amplitude%20Product%20Report%202022.pdf` | `2.0 MB` |
| 9 | `airtable-product-insights-report.en.md` | `airtable-product-insights-report.md` | Airtable Product Insights Report | Enterprise report examining how modern teams accelerate product discovery and delivery using no-code platforms and connected data. | Tools & Enterprise Innovation | `["Reports", "Tools & Enterprise Innovation", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/Airtable_Product-insights-report.pdf` | `2.9 MB` |
| 10 | `heap-digital-experiences-insights-report2.en.md` | `heap-digital-experiences-insights-report2.md` | Heap Digital Experiences Insights Report | User experience analysis exploring customer journey friction, funnel drop-off points, and conversion optimization strategies across web and mobile. | Data Analytics & User Behavior | `["Reports", "Data Analytics & User Behavior", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/heap-digital-experiences-insights-report2.pdf` | `400 KB` |
| 11 | `designvaluereport1.en.md` | `designvaluereport1.md` | Design Value Benchmark Report | Empirical study measuring the Return on Investment (ROI) of design and how design-centric companies outperform broader financial markets. | Design & Business Value | `["Reports", "Design & Business Value", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/DesignValueReport1.pdf` | `1.3 MB` |
| 12 | `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md` | `گزارش-صنعت-پرداخت-ایران-نسخه-نهم.md` | Iran Payment Industry Annual Report (9th Edition) | Statistical analysis of electronic payment transactions, PSP market shares, online gateway metrics, and fintech trends in Iran. | Iran Ecosystem & Industries | `["Reports", "Iran Ecosystem & Industries", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B5%D9%86%D8%B9%D8%AA%20%D9%BE%D8%B1%D8%AF%D8%A7%D8%AE%D8%AA%20%D8%A7%DB%8C%D8%B1%D8%A7%D9%86%20%D9%86%D8%B3%D8%AE%D9%87%20%D9%86%D9%87%D9%85.pdf` | `5.7 MB` |
| 13 | `iran-startup-ecosystem-report-techrasa-1400.en.md` | `iran-startup-ecosystem-report-techrasa-1400.md` | Iran Startup Ecosystem Survey - TechRasa (Spring 1400 / 2021) | Survey of Iran's tech startup ecosystem, gathering direct insights from 100+ founders and CEOs on growth metrics, valuations, and economic impact. | Iran Ecosystem & Industries | `["Reports", "Iran Ecosystem & Industries", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/1666697156021.pdf` | `1.8 MB` |
| 14 | `hbr-2022-11-12.en.md` | `hbr-2022-11-12.md` | Harvard Business Review Magazine (Nov-Dec 2022 Issue) | Full November-December 2022 issue of Harvard Business Review exploring strategic leadership during uncertainty and high-stakes decision-making. | Specialized Periodicals & Journals | `["Reports", "Specialized Periodicals & Journals", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/HBR%202022%2011%2012.pdf` | `90.4 MB` |
| 15 | `generative-ai-the-insights-you-need-from-harvard-business-review.en.md` | `generative-ai-the-insights-you-need-from-harvard-business-review.md` | Generative AI: The Insights You Need from Harvard Business Review | Curated HBR research and essays examining generative AI's impact on business strategy, workforce productivity, and competitive advantage. | Specialized Periodicals & Journals | `["Reports", "Specialized Periodicals & Journals", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/Generative_AI_The_Insights_You_Need_From_Harvard_Business_Review.pdf` | `6.7 MB` |
| 16 | `the-analytics-stack-guidebook.en.md` | `the-analytics-stack-guidebook.md` | The Analytics Stack Guidebook | Technical evaluation of modern product analytics architectures comparing Snowflake, BigQuery, Segment, Amplitude, and Mixpanel. | Tools & Enterprise Innovation | `["Reports", "Tools & Enterprise Innovation", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/the-analytics-stack-guidebook.pdf` | `13.5 MB` |
| 17 | `heap-implicit-vs-explicit-guide-2022.en.md` | `heap-implicit-vs-explicit-guide-2022.md` | Heap Implicit vs Explicit Data Guide 2022 | Technical playbook by Heap comparing automatic event capture (implicit data) with manual tracking (explicit data) for digital product optimization. | Data Analytics & User Behavior | `["Reports", "Data Analytics & User Behavior", "Product Management", "Market Analysis"]` | `https://dl.theminiceo.ir/HEAP_Implicit-vs-Explicit_Guide_2022.pdf` | `1.7 MB` |

---

### Detailed Key Research Takeaways (Translated for Reports Generation)

1. **`the-2024-state-of-product-management-report.en.md`**:
   - Examination of key product management priorities in 2024 and the accelerating integration of AI into product lifecycles.
   - Standard product team topologies and cross-functional collaboration with engineering, design, and marketing.
   - Dominant tooling stacks for roadmap planning, behavioral analytics, and continuous user feedback.
   - Macroeconomic headwinds, cost optimization strategies, and shifting focus toward sustainable unit economics over hypergrowth.

2. **`the-state-of-product-management-annual-report-2023.en.md`**:
   - Statistical benchmarks gathered from thousands of international product practitioners across diverse verticals.
   - Primary feature prioritization methodologies and mitigating stakeholder friction.
   - Return-to-office trends and the operational realities of hybrid product management.
   - Performance evaluation metrics, compensation trends, and leadership promotion pathways.

3. **`the-2022-state-of-product-management-report-by-productplan.en.md`**:
   - Evolution of product roadmapping methodologies in remote and distributed team environments.
   - Leading platforms for task execution, sprint tracking, and strategic goal alignment.
   - The misalignment between executive leadership expectations and operational team delivery.
   - The critical role of data analytics in fostering evidence-based product decisions.

4. **`wef-future-of-jobs-report-2025.en.md`**:
   - Top 10 core technical and cognitive competencies required for technology and product leaders over the next 5 years.
   - Global labor market disruption driven by automation, artificial intelligence, and digital transformation.
   - Organizational strategies for workforce reskilling and upskilling programs.
   - Talent acquisition outlook and structural restructuring across digital industries.

5. **`product-leadership-census-2023-v2.en.md`**:
   - Executive reporting structures linking Chief Product Officers (CPOs) and Product VPs to CEOs and boards.
   - Budget governance, resource allocation, and measuring product department ROI.
   - Key talent retention strategies and overcoming hiring hurdles for specialized product roles.
   - Collaboration mechanisms between product leadership and enterprise revenue teams.

6. **`fpmr-2023-enterprise.en.md`**:
   - Structural challenges when transitioning legacy enterprises into modern Product Operating Models.
   - Managing complex software dependencies, architectural debt, and enterprise legacy systems.
   - Enterprise data governance, security compliance, and regulatory risk mitigation.
   - Agile scaling frameworks (SAFe, LeSS) versus autonomous, empowered product teams.

7. **`the-future-of-product-2024.en.md`**:
   - Paradigm shift from traditional graphical user interfaces (GUIs) to intent-based, conversational AI systems.
   - Real-time personalization of digital user experiences enabled by Large Language Models (LLMs).
   - Autonomous AI agents accelerating continuous discovery, automated testing, and iteration loops.
   - Ethical AI product design, data privacy safeguards, and algorithmic transparency.

8. **`amplitude-product-report-2022.en.md`**:
   - User retention benchmarks across B2B SaaS and B2C mobile applications.
   - Predictive user behaviors, activation milestones, and discovering the Aha Moment.
   - Correlation between personalized customer experiences and expansion of Customer Lifetime Value (LTV).
   - Proven frameworks for implementing scalable Product-Led Growth (PLG) motions.

9. **`airtable-product-insights-report.en.md`**:
   - Unlocking cross-functional team agility through visual, relational databases.
   - Accelerating Time-to-Market using rapid prototyping and flexible no-code operational tools.
   - Centralizing multi-source customer feedback directly into quarterly roadmap prioritization.
   - Enterprise case studies on automated workflow pipelines and operational transparency.

10. **`heap-digital-experiences-insights-report2.en.md`**:
    - Pinpointing unnoticed drop-off points throughout user registration and onboarding journeys.
    - Benefits of autocapture behavioral data in uncovering hidden customer paths.
    - Quantifiable impact of page latency and cognitive load on product feature adoption.
    - Proven methodologies for conversion funnel optimization and checkout flow improvement.

11. **`designvaluereport1.en.md`**:
    - Performance comparison of the Design Index companies against the S&P 500 index.
    - Translating superior user experience and interface craft into measurable enterprise value and profit margins.
    - Assessing corporate design maturity levels and their strategic impact on executive decisions.
    - Cultivating enduring customer affinity and retention through cohesive product design identity.

12. **`گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md`**:
    - Transaction volume and value trends across the Shaparak national payment network and online gateways.
    - Market share distribution and ranking of Payment Service Providers (PSPs) in Iran.
    - User behavior patterns across mobile payments, USSD channels, and digital applications.
    - Regulatory frameworks, transaction thresholds, and emerging opportunities in Iranian fintech.

13. **`iran-startup-ecosystem-report-techrasa-1400.en.md`**:
    - Nationwide survey capturing empirical data from over 100 Iranian tech founders and CEOs.
    - Benchmarks across startup funding stages (Pre-seed, Seed, Early Stage, and Growth).
    - Impact of economic headwinds, inflation, pandemic conditions, and digital filtering on tech ventures.
    - Startup valuation dynamics and venture capital (VC) investment activity in Iran.

14. **`hbr-2022-11-12.en.md`**:
    - Executive management essays from Harvard Business School faculty on building organizational resilience.
    - Innovative pricing strategies and agile supply chain adaptation during inflationary periods.
    - Leadership psychology and maintaining team morale during economic downturns.
    - Global case studies on corporate agility and business model transformation.

15. **`generative-ai-the-insights-you-need-from-harvard-business-review.en.md`**:
    - How generative artificial intelligence transforms creative work, knowledge productivity, and software development.
    - Managing commercial AI risks: copyright compliance, model hallucinations, and enterprise privacy.
    - Strategy playbooks for small enterprises competing against incumbents with foundation models.
    - Reinventing customer relationship management and support workflows with intelligent AI bots.

16. **`the-analytics-stack-guidebook.en.md`**:
    - Modern Data Stack (MDS) architectural blueprints from raw event ingestion to executive dashboards.
    - Key architectural trade-offs between Customer Data Platforms (CDPs) and Cloud Data Warehouses.
    - Recommended analytics software stacks tailored to startup maturity stages.
    - Strategies for optimizing data warehouse query costs and storage overhead at scale.

17. **`heap-implicit-vs-explicit-guide-2022.en.md`**:
    - Structural differences between reactive manual event tracking and proactive automated data capture.
    - How implicit behavioral data surfaces unpredicted user journeys and navigational dead-ends.
    - Slashing tracking code maintenance overhead for software engineering teams.
    - Turning raw telemetry data into executive-level product health indicators.

---

### Standard English Report Markdown Template

Each of the 17 English report files (`content/docs/reports/<slug>.en.md`) should adhere to the following schema:

```markdown
---
title: "{canonical_title}"
date: 2026-09-16
description: "{canonical_description}"
tags: ["Reports", "{canonical_category}", "Product Management", "Market Analysis"]
categories: ["Reports"]
aliases:
  - /docs/books/{old_slug}/
  {additional_aliases_if_applicable}
---

{canonical_title} is an authoritative industry benchmark in the domain of **{canonical_category}**. Drawing upon extensive empirical research, industry surveys, and market analysis, this publication delivers vital data and actionable frameworks for product managers, technology leaders, and business strategists.

### Key Research Findings & Takeaways
* {takeaway_1}
* {takeaway_2}
* {takeaway_3}
* {takeaway_4}

### Who Should Read This Report?
* **Product Managers and Leaders (CPO/PM):** To understand the competitive landscape, align strategic roadmaps with global benchmarks, and identify untapped market opportunities.
* **UX Researchers & Product Designers:** To access empirical usage patterns, user journey data, and customer behavior trends.
* **Founders & Executive Strategists:** To make evidence-backed decisions regarding capital allocation, resource planning, and market positioning.

---

### 📥 Download Full Report

{{< book-download url="{dl_url}" title="Download {canonical_title}" size="{canonical_size}" format="PDF" lang="English" >}}
```

---

## 6. Shortcode Multilingual Interface Specification

**File Path**: `layouts/shortcodes/book-download.html`

### Required Logic & Template Updates

```html
{{/* Book Download Shortcode for Hextra Theme */}}
{{ $isEn := eq .Page.Language.Lang "en" }}
{{ $defaultTitle := cond $isEn "Download Book File" "دانلود مستقیم نسخه اصلی کتاب" }}
{{ $defaultLang := cond $isEn "English" "انگلیسی" }}
{{ $url := .Get "url" | default (.Get 0) }}
{{ $title := .Get "title" | default $defaultTitle }}
{{ $size := .Get "size" | default "" }}
{{ $format := .Get "format" | default "PDF" }}
{{ $lang := .Get "lang" | default $defaultLang }}

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
            <span>{{ if $isEn }}Size: {{ else }}حجم: {{ end }}{{ $size }}</span>
          {{ end }}
          {{ if $lang }}
            <span>•</span>
            <span>{{ if $isEn }}Language: {{ else }}زبان: {{ end }}{{ $lang }}</span>
          {{ end }}
          <span>•</span>
          <span class="hx:text-emerald-600 hx:dark:text-emerald-400 hx:font-medium">{{ if $isEn }}High-speed Direct CDN{{ else }}سرور پرسرعت داخلی{{ end }}</span>
        </div>
      </div>
    </div>

    <div class="hx:w-full hx:sm:w-auto hx:flex hx:justify-end">
      <a href="{{ $url }}" target="_blank" rel="noopener noreferrer" download class="hx:w-full hx:sm:w-auto hx:inline-flex hx:items-center hx:justify-center hx:gap-2 hx:py-2.5 hx:px-6 hx:rounded-xl hx:text-sm hx:font-bold hx:text-white hx:bg-blue-600 hx:hover:bg-blue-700 hx:active:scale-[0.98] hx:shadow-md hx:shadow-blue-600/25 hx:transition-all hx:no-underline">
        <svg xmlns="http://www.w3.org/2000/svg" class="hx:w-4 hx:h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        <span>{{ if $isEn }}Download Book File{{ else }}دریافت فایل کتاب{{ end }}</span>
      </a>
    </div>
  </div>
</div>
```

---

## 7. Requirements Traceability Matrix for Milestone 2

| Requirement ID | Description | Source Contract | Implementation Artifact | Verification Assertion / Test | Success Threshold |
|----------------|-------------|-----------------|-------------------------|-------------------------------|-------------------|
| **RTM-M2-01** | 17 English Reports 1:1 Co-Location | `ORIGINAL_REQUEST.md` § R3; `PROJECT.md` Feature 3 | `content/docs/reports/*.en.md` (17 files) | `test_localization_e2e.py:test_t1_2_reports_coverage` | Exactly 17 `.en.md` files match `CANONICAL_REPORT_FILES` |
| **RTM-M2-02** | Reports Section Index Parity | `PROJECT.md` M2 | `content/docs/reports/_index.en.md` | `test_localization_e2e.py:test_t1_2_reports_coverage` (line 292); `test_t1_5_body_content_non_empty` (line 468) | File exists and body > 50 characters |
| **RTM-M2-03** | Frontmatter Completeness | `ORIGINAL_REQUEST.md` § R1; `PROJECT.md` § Book Schema | Frontmatter in all 17 `.en.md` reports | `test_localization_e2e.py:test_t1_4_frontmatter_completeness` (lines 357–389) | Missing count = 0 for `title`, `date`, `description`, `categories` |
| **RTM-M2-04** | Body Content & Headings | `ORIGINAL_REQUEST.md` § R1; `PROJECT.md` § Book Schema | Markdown body in all 17 `.en.md` reports | `test_localization_e2e.py:test_t1_5_body_content_non_empty` (lines 421–440) | Body length > 100 characters and contains regex `^###?\s+` |
| **RTM-M2-05** | Persian Slug Report Validity | `PROJECT.md` § Architecture | `content/docs/reports/گزارش-صنعت-پرداخت-ایران-نسخه-نهم.en.md` | `test_localization_e2e.py:test_t2_1_persian_slug_report` (lines 506–532) | File exists, size >= 200B, English title & desc, body >= 100 chars, shortcode present |
| **RTM-M2-06** | Zero Untranslated Persian Text | `ORIGINAL_REQUEST.md` Acceptance Criteria | All 17 `.en.md` report files | `test_localization_e2e.py:test_t2_4_zero_untranslated_persian_blocks` (lines 557–581) | 0 Persian chars in titles, descriptions, and headings |
| **RTM-M2-07** | Zero Dummy Placeholder Tokens | `ORIGINAL_REQUEST.md` Acceptance Criteria | All 17 `.en.md` report files | `test_localization_e2e.py:test_t2_5_zero_dummy_placeholder_text` (lines 609–622) | 0 matches for `PLACEHOLDER_REGEX` |
| **RTM-M2-08** | Boundary File Sizes Parameter | `PROJECT.md` § Interface Contracts | `hbr-2022-11-12.en.md` & `heap-digital-experiences-insights-report2.en.md` | `test_localization_e2e.py:test_t2_6_boundary_file_sizes_and_special_chars` (lines 633–656) | HBR size has `"90.4"` or `"90"`; Heap size has `"400"` or `"0.4"` |
| **RTM-M2-09** | Download Shortcode URL Integrity | `ORIGINAL_REQUEST.md` § R3; `PROJECT.md` § Feature 3 | Shortcodes in all 17 `.en.md` reports | `test_localization_e2e.py:test_t3_1_download_shortcodes_url_integrity` (lines 675–705) | 17/17 URLs match verbatim `setup_reports_section.py` |
| **RTM-M2-10** | Taxonomy Category "Reports" | `PROJECT.md` § Book Markdown Schema | Frontmatter `categories` | `test_localization_e2e.py:test_t3_2_taxonomy_category_mapping` (lines 743–759) | `categories: ["Reports"]` in all 17 reports |
| **RTM-M2-11** | Multilingual Shortcode Template | `PROJECT.md` § Feature 2 & Interface Contracts | `layouts/shortcodes/book-download.html` | `test_localization_e2e.py:test_t3_4_multilingual_shortcode_template` (lines 825–858) | Language conditional + English labels ("Size: ", "Language: ", "High-speed Direct CDN", "Download Book File") + Persian preserved |
| **RTM-M2-12** | Co-Located Stem Pairing & ISO Date | `PROJECT.md` § Architecture | All 17 `.en.md` report files | `test_localization_e2e.py:test_t3_5_co_located_stem_pairing` (lines 859–880) | 0 orphaned `.en.md` files; date matches `^\d{4}-\d{2}-\d{2}` |
| **RTM-M2-13** | Strict Localization Audit Tool Compliance | `ORIGINAL_REQUEST.md` § R1; `PROJECT.md` M1 | `scripts/verify_localization.py` | `python3 scripts/verify_localization.py --strict` | Exits with code 0 for reports section |
| **RTM-M2-14** | Hugo Clean Compilation & Page Delta | `ORIGINAL_REQUEST.md` § R4; `PROJECT.md` M2/M4 | Hugo static generator | `hugo --renderToMemory` | Exit code 0, 0 build errors, +18 rendered English pages for reports |

---

## 8. Caveats

1. **Books Section Scope**:
   - The 390 books localization and legacy book retrofitting belong to Milestone 3 (`M3`). E2E tests `T1.3`, `T3.3`, `T4.1`, `T4.3` will continue to reflect ungenerated books until Milestone 3 is executed.
   - However, implementing Milestone 2 will clear `T1.2`, `T2.2`, `T2.6`, `T3.4`, and all reports-specific assertions in `T1.4`, `T1.5`, `T2.4`, `T2.5`, `T3.1`, `T3.2`, `T3.5`.
2. **Index File `_index.en.md`**:
   - `content/docs/reports/_index.en.md` already exists and satisfies character length thresholds. No modifications are needed to the index unless enhanced cards are desired.
3. **No Code Modifications Made**:
   - In accordance with the SPECIFICATION MINER role, zero project source files were altered during this audit.

---

## 9. Conclusion

Milestone 2 has clear, authoritative specifications and zero requirements ambiguity.
The target deliverables comprise:
1. Updating `layouts/shortcodes/book-download.html` to support bilingual conditional rendering (`.Page.Language.Lang == "en"`).
2. Generating exactly 17 English reports in `content/docs/reports/<slug>.en.md` conforming to the 3-heading structure, `categories: ["Reports"]`, ISO 8601 date, verbatim CDN URLs from `setup_reports_section.py`, English key research takeaways, and boundary size parameters.

Upon implementation by the Milestone 2 worker, all reports-related E2E assertions across Tiers 1–3 will pass cleanly, paving the way for Milestone 3 (Books localization).

---

## 10. Verification Method

To verify the mined requirements and validate Milestone 2 implementation:

1. **Run Shortcode Template Test**:
   ```bash
   python3 scripts/test_localization_e2e.py -v --tier 3
   # Focus assertion: test_t3_4_multilingual_shortcode_template (8 assertions)
   ```

2. **Run Reports Coverage & Boundary Tests**:
   ```bash
   python3 scripts/test_localization_e2e.py -v --tier 1
   # Focus assertions: test_t1_2_reports_coverage, test_t1_4_frontmatter_completeness, test_t1_5_body_content_non_empty

   python3 scripts/test_localization_e2e.py -v --tier 2
   # Focus assertions: test_t2_2_persian_slug_report, test_t2_4_zero_untranslated_persian_blocks, test_t2_5_zero_dummy_placeholder_text, test_t2_6_boundary_file_sizes_and_special_chars
   ```

3. **Run Audit Tool on Reports Directory**:
   ```bash
   python3 scripts/verify_localization.py --strict --root content/docs/reports
   # Expected exit code: 0
   ```

4. **Verify Hugo Memory Compilation**:
   ```bash
   hugo --renderToMemory
   # Expected exit code: 0, 0 build errors
   ```
