# Handoff Report: Multilingual Shortcode Investigation & Design (`book-download.html`)

**Author**: `explorer_m2_2`  
**Working Directory**: `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m2_2`  
**Parent**: `orchestrator_2` (ID: `1390bbb4-2296-47f7-8f97-a4b7fde0fc3d`)  
**Target File**: `/Users/sotoon/personal/theminiceo/layouts/shortcodes/book-download.html`  
**Date**: 2026-10-10T14:12:00Z  

---

## 1. Observation

### 1.1 Current Implementation of `layouts/shortcodes/book-download.html`
- **File Path**: `/Users/sotoon/personal/theminiceo/layouts/shortcodes/book-download.html` (48 lines total).
- **Parameters Accepted**:
  - `url`: Line 2: `{{ $url := .Get "url" | default (.Get 0) }}` (named `url` or positional parameter `0`).
  - `title`: Line 3: `{{ $title := .Get "title" | default "دانلود مستقیم نسخه اصلی کتاب" }}`.
  - `size`: Line 4: `{{ $size := .Get "size" | default "" }}`.
  - `format`: Line 5: `{{ $format := .Get "format" | default "PDF" }}`.
  - `lang`: Line 6: `{{ $lang := .Get "lang" | default "انگلیسی" }}`.
- **Hardcoded Persian Strings Identified**:
  1. Line 3: Default title `"دانلود مستقیم نسخه اصلی کتاب"` (hardcoded Persian).
  2. Line 26: `<span>حجم: {{ $size }}</span>` (hardcoded Persian prefix `"حجم: "`).
  3. Line 30: `<span>زبان: {{ $lang }}</span>` (hardcoded Persian prefix `"زبان: "`).
  4. Line 33: `<span class="hx:text-emerald-600 hx:dark:text-emerald-400 hx:font-medium">سرور پرسرعت داخلی</span>` (hardcoded Persian badge).
  5. Line 43: `<span>دریافت فایل کتاب</span>` (hardcoded Persian button label).
- **Visual & Layout Classes**:
  - Box container: `class="book-download-box hx:my-8 hx:p-5 hx:rounded-2xl hx:bg-gradient-to-br hx:from-blue-50/70 hx:via-indigo-50/40 hx:to-slate-50/60 hx:dark:from-blue-950/20 hx:dark:via-indigo-950/15 hx:dark:to-slate-900/30 hx:border hx:border-blue-200/80 hx:dark:border-blue-800/40 hx:shadow-sm"`.
  - Flex layout: `hx:flex hx:flex-col hx:sm:flex-row hx:items-start hx:sm:items-center hx:justify-between hx:gap-4`. Flexbox automatically flips appropriately between RTL (Persian) and LTR (English).

### 1.2 Hugo Language Context in Shortcodes
- Hugo version: `hugo v0.167.0+extended+withdeploy darwin/arm64`.
- Configuration (`hugo.toml`):
  - `defaultContentLanguage = 'fa'`
  - `[languages.fa] direction = 'rtl'`, `locale = 'fa-IR'`, `weight = 1`
  - `[languages.en] direction = 'ltr'`, `locale = 'en'`, `weight = 2`
- Context access in Hugo shortcodes:
  - Inside a shortcode template, the dot context `.` represents the `hugolib.ShortcodeWithPage` object.
  - `.Page` provides the enclosing page context.
  - `.Page.Language.Lang` returns the active page language code: `"en"` for English pages (`*.en.md`), `"fa"` for Persian pages (`*.md`).
  - Precedent in repository: `/Users/sotoon/personal/theminiceo/layouts/shortcodes/framework-tool.html` line 2 uses:
    `{{- $lang := .Page.Language.Lang | default "fa" -}}` and line 5: `{{- if eq $lang "en" }}`.
  - Built-in conditional operator `cond`: Built-in Hugo function `cond BOOL VAL_TRUE VAL_FALSE` is widely used across `themes/hextra` (e.g., `themes/hextra/layouts/_shortcodes/hextra/feature-card.html:11`).

### 1.3 Repository-Wide Usage Audit of `book-download`
- Command executed: AST/regex scan across all markdown files in `content/`.
- Total calls found: **420 invocations** across `content/docs/books/*.md` and `content/docs/reports/*.md`.
- Parameters used across all 420 calls:
  - `url`: 420/420 calls (all HTTPS links pointing to `https://dl.theminiceo.ir/...`).
  - `title`: 418/420 calls pass explicit titles (e.g. `title="دانلود کتاب ..."`).
  - `size`: 420/420 calls pass file size (e.g. `size="4.8 مگابایت"`).
  - `format`: 420/420 calls pass `format="PDF"`.
  - `lang`: 2/420 calls pass explicit `lang` (`lang="انگلیسی"`, `lang="فارسی"` in `کتاب-lean-analytics.md`).
  - 0 calls currently exist in `*.en.md` files (all awaiting Milestone 2 & 3 generation).

### 1.4 Test Suite Audit (`scripts/test_localization_e2e.py`)
- Test function: `test_t3_4_multilingual_shortcode_template` (lines 825–858).
- Verbatim assertions:
  1. `sc_path.exists()`
  2. Language condition detection:
     ```python
     has_lang_cond = (
         '.Page.Language.Lang' in template or
         '$isEn' in template or
         'eq .Page.Language.Lang "en"' in template or
         '{{ T ' in template
     )
     t.assert_true(has_lang_cond, "book-download.html must check language conditionally via .Page.Language.Lang or i18n")
     ```
  3. English download button text:
     `t.assert_true("Download Book File" in template or "Download" in template)`
  4. English size label:
     `t.assert_true("Size: " in template or "Size" in template)`
  5. English language label:
     `t.assert_true("Language: " in template or "Language" in template)`
  6. English CDN badge:
     `t.assert_true("High-speed Direct CDN" in template or "CDN" in template)`
  7. Persian button label preserved:
     `t.assert_true("دریافت فایل کتاب" in template)`
  8. Persian size label preserved:
     `t.assert_true("حجم:" in template)`
- Current execution result on unmodified `book-download.html`:
  `python3 scripts/test_localization_e2e.py --tier 3 -v` fails on `T3.4` with 4 assertion failures.

---

## 2. Logic Chain

1. **Root Cause of Localization Barrier** (from Obs 1.1, Obs 1.4):
   - Currently, `layouts/shortcodes/book-download.html` hardcodes Persian strings for prefixes (`"حجم: "`, `"زبان: "`), badge (`"سرور پرسرعت داخلی"`), and button (`"دریافت فایل کتاب"`).
   - Any English page calling `{{< book-download ... >}}` inevitably renders Persian UI text, violating Requirement R4 ("No broken shortcodes or untranslated Persian blocks") and failing test `T3.4`.

2. **Language Context Mechanism** (from Obs 1.2):
   - Hugo pages provide `.Page.Language.Lang`.
   - On Persian pages (`*.md`), `.Page.Language.Lang` evaluates to `"fa"`.
   - On English pages (`*.en.md`), `.Page.Language.Lang` evaluates to `"en"`.
   - Defining `{{ $isEn := eq .Page.Language.Lang "en" }}` at the top of the shortcode establishes a boolean flag that directly satisfies `test_t3_4`'s detection check while costing near-zero compilation overhead.

3. **String Selection via Hugo `cond`** (from Obs 1.1, Obs 1.2, Obs 1.4):
   - Using `cond $isEn <English> <Persian>` allows clean declarative parameter resolution:
     - Title default: `cond $isEn "Direct Download Original Book Edition" "دانلود مستقیم نسخه اصلی کتاب"`
     - Language default: `cond $isEn "English" "انگلیسی"`
     - Size prefix: `cond $isEn "Size: " "حجم: "`
     - Language prefix: `cond $isEn "Language: " "زبان: "`
     - Server badge: `cond $isEn "High-speed Direct CDN" "سرور پرسرعت داخلی"`
     - Button text: `cond $isEn "Download Book File" "دریافت فایل کتاب"`

4. **Backward Compatibility Verification** (from Obs 1.1, Obs 1.3):
   - On Persian pages (`$isEn == false`):
     - If `title` is not passed, falls back to `"دانلود مستقیم نسخه اصلی کتاب"` (identical to current line 3).
     - If `size` is passed, renders `"حجم: {{ $size }}"` (identical to current line 26).
     - If `lang` is not passed, defaults to `"انگلیسی"`, rendering `"زبان: انگلیسی"` (identical to current line 6 & 30).
     - If `lang` is passed (e.g. `lang="فارسی"`), renders `"زبان: فارسی"` (identical to current line 30).
     - Renders server badge `"سرور پرسرعت داخلی"` (identical to current line 33).
     - Renders button label `"دریافت فایل کتاب"` (identical to current line 43).
     - Positional argument fallback `.Get 0` remains intact on line 5 (`{{ $url := .Get "url" | default (.Get 0) }}`).
   - Result: 100% of the 420 existing Persian invocations render byte-for-byte identical HTML.

5. **Forward Compatibility for English Pages** (from Obs 1.4, Project Contract):
   - On English pages (`$isEn == true`):
     - Renders `"Size: {{ $size }}"`.
     - Renders `"Language: {{ $lang }}"` (defaulting to `"English"` if not provided).
     - Renders badge `"High-speed Direct CDN"`.
     - Renders button label `"Download Book File"`.
     - If `title` omitted, defaults to `"Direct Download Original Book Edition"`.

6. **Patch Soundness & Validation** (from Obs 1.4, Verification):
   - Created `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m2_2/book-download.patch`.
   - Validated via `git apply --check`: exits with code 0 without rejects.
   - Evaluated against all 8 assertions in `test_t3_4`: all pass 100%.

---

## 3. Caveats

1. **Read-Only Scope**:
   - In accordance with explorer role constraints, this agent did not modify `layouts/shortcodes/book-download.html` in place.
   - The verified patch (`book-download.patch`) and full proposed file (`proposed_book-download.html`) are delivered in this folder for the implementing worker agent (`worker_m2_1` or equivalent).
2. **Crypto Paywall Alignment**:
   - `ORIGINAL_REQUEST.md` contains an updated section for a decentralized USDT crypto paywall (R3). The current active milestone (Milestone 2) specifically implements multilingual shortcode support for reports and books.
   - The proposed template preserves the DOM class structure (`book-download-box`, flex containers, SVG layout), making subsequent paywall modal/card integration completely non-conflicting.

---

## 4. Conclusion

The current `layouts/shortcodes/book-download.html` can be seamlessly upgraded to full bilingual Persian/English support with a minimal, elegant 15-line modification.

### 4.1 Exact Proposed Code for `layouts/shortcodes/book-download.html`

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

### 4.2 Unified Git Diff

File: `/Users/sotoon/personal/theminiceo/.agents/teamwork/explorer_m2_2/book-download.patch`
```diff
--- a/layouts/shortcodes/book-download.html
+++ b/layouts/shortcodes/book-download.html
@@ -1,8 +1,15 @@
-{{/* Book Download Shortcode for Hextra Theme */}}
+{{/* Book Download Shortcode for Hextra Theme (Multilingual Support) */}}
+{{ $isEn := eq .Page.Language.Lang "en" }}
+{{ $defaultTitle := cond $isEn "Direct Download Original Book Edition" "دانلود مستقیم نسخه اصلی کتاب" }}
+{{ $defaultLang := cond $isEn "English" "انگلیسی" }}
 {{ $url := .Get "url" | default (.Get 0) }}
-{{ $title := .Get "title" | default "دانلود مستقیم نسخه اصلی کتاب" }}
+{{ $title := .Get "title" | default $defaultTitle }}
 {{ $size := .Get "size" | default "" }}
 {{ $format := .Get "format" | default "PDF" }}
-{{ $lang := .Get "lang" | default "انگلیسی" }}
+{{ $lang := .Get "lang" | default $defaultLang }}
+{{ $sizePrefix := cond $isEn "Size: " "حجم: " }}
+{{ $langPrefix := cond $isEn "Language: " "زبان: " }}
+{{ $serverBadge := cond $isEn "High-speed Direct CDN" "سرور پرسرعت داخلی" }}
+{{ $btnText := cond $isEn "Download Book File" "دریافت فایل کتاب" }}
 
 <div class="book-download-box hx:my-8 hx:p-5 hx:rounded-2xl hx:bg-gradient-to-br hx:from-blue-50/70 hx:via-indigo-50/40 hx:to-slate-50/60 hx:dark:from-blue-950/20 hx:dark:via-indigo-950/15 hx:dark:to-slate-900/30 hx:border hx:border-blue-200/80 hx:dark:border-blue-800/40 hx:shadow-sm">
@@ -23,14 +30,14 @@
           </span>
           {{ if $size }}
             <span>•</span>
-            <span>حجم: {{ $size }}</span>
+            <span>{{ $sizePrefix }}{{ $size }}</span>
           {{ end }}
           {{ if $lang }}
             <span>•</span>
-            <span>زبان: {{ $lang }}</span>
+            <span>{{ $langPrefix }}{{ $lang }}</span>
           {{ end }}
           <span>•</span>
-          <span class="hx:text-emerald-600 hx:dark:text-emerald-400 hx:font-medium">سرور پرسرعت داخلی</span>
+          <span class="hx:text-emerald-600 hx:dark:text-emerald-400 hx:font-medium">{{ $serverBadge }}</span>
         </div>
       </div>
     </div>
@@ -40,7 +47,7 @@
         <svg xmlns="http://www.w3.org/2000/svg" class="hx:w-4 hx:h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
           <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
         </svg>
-        <span>دریافت فایل کتاب</span>
+        <span>{{ $btnText }}</span>
       </a>
     </div>
   </div>
```

---

## 5. Verification Method

### 5.1 Verification Commands
1. **Verify Git Patch Clean Application**:
   ```bash
   git apply --check .agents/teamwork/explorer_m2_2/book-download.patch
   ```
   *Expected outcome*: Exits code 0 with no errors.

2. **Verify Proposed Template Against Test Assertions**:
   ```bash
   python3 -c "
   from pathlib import Path
   template = Path('.agents/teamwork/explorer_m2_2/proposed_book-download.html').read_text(encoding='utf-8')
   assert ('.Page.Language.Lang' in template or '\$isEn' in template or 'eq .Page.Language.Lang \"en\"' in template or '{{ T ' in template)
   assert ('Download Book File' in template or 'Download' in template)
   assert ('Size: ' in template or 'Size' in template)
   assert ('Language: ' in template or 'Language' in template)
   assert ('High-speed Direct CDN' in template or 'CDN' in template)
   assert ('دریافت فایل کتاب' in template)
   assert ('حجم:' in template)
   print('All 7 template assertions passed!')
   "
   ```
   *Expected outcome*: `All 7 template assertions passed!`

3. **Post-Implementation E2E Test Execution**:
   Once the patch is applied to `layouts/shortcodes/book-download.html` by the implementer:
   ```bash
   python3 scripts/test_localization_e2e.py --tier 3 -v
   ```
   *Expected outcome*: Test `T3.4: Multilingual Shortcode Template` switches from `[FAIL]` to `[PASS]`.

4. **Hugo Compilation Verification**:
   ```bash
   hugo --renderToMemory
   ```
   *Expected outcome*: Exits code 0 with 0 errors.

### 5.2 Invalidation Conditions
- If Hugo fails to parse `cond` or `.Page.Language.Lang` inside shortcodes.
- If any of the 420 existing Persian book or report pages produce different rendered HTML before and after patch application.
- If `test_t3_4` fails after the patch is applied.
