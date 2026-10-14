# Frontend Architecture Survey Report: Book Download Delivery & Paywall Integration

## 1. Observation

### 1.1 Existing Shortcodes and Templates
- **`layouts/shortcodes/book-download.html` (lines 1-48)**:
  ```html
  {{/* Book Download Shortcode for Hextra Theme */}}
  {{ $url := .Get "url" | default (.Get 0) }}
  {{ $title := .Get "title" | default "دانلود مستقیم نسخه اصلی کتاب" }}
  {{ $size := .Get "size" | default "" }}
  {{ $format := .Get "format" | default "PDF" }}
  {{ $lang := .Get "lang" | default "انگلیسی" }}

  <div class="book-download-box hx:my-8 hx:p-5 hx:rounded-2xl hx:bg-gradient-to-br hx:from-blue-50/70 hx:via-indigo-50/40 hx:to-slate-50/60 hx:dark:from-blue-950/20 hx:dark:via-indigo-950/15 hx:dark:to-slate-900/30 hx:border hx:border-blue-200/80 hx:dark:border-blue-800/40 hx:shadow-sm">
    <div class="hx:flex hx:flex-col hx:sm:flex-row hx:items-start hx:sm:items-center hx:justify-between hx:gap-4">
      <div class="hx:flex hx:items-center hx:gap-3.5">
        <div class="hx:w-12 hx:h-12 hx:rounded-xl hx:bg-blue-600 hx:text-white hx:flex hx:items-center hx:justify-center hx:shrink-0 hx:shadow-md hx:shadow-blue-500/20">
          ...
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
              <span>حجم: {{ $size }}</span>
            {{ end }}
            {{ if $lang }}
              <span>•</span>
              <span>زبان: {{ $lang }}</span>
            {{ end }}
            <span>•</span>
            <span class="hx:text-emerald-600 hx:dark:text-emerald-400 hx:font-medium">سرور پرسرعت داخلی</span>
          </div>
        </div>
      </div>

      <div class="hx:w-full hx:sm:w-auto hx:flex hx:justify-end">
        <a href="{{ $url }}" target="_blank" rel="noopener noreferrer" download class="hx:w-full hx:sm:w-auto hx:inline-flex hx:items-center hx:justify-center hx:gap-2 hx:py-2.5 hx:px-6 hx:rounded-xl hx:text-sm hx:font-bold hx:text-white hx:bg-blue-600 hx:hover:bg-blue-700 hx:active:scale-[0.98] hx:shadow-md hx:shadow-blue-600/25 hx:transition-all hx:no-underline">
          ...
          <span>دریافت فایل کتاب</span>
        </a>
      </div>
    </div>
  </div>
  ```
- **`layouts/shortcodes/buy-button.html` (lines 1-40)**: Implements ZarinPal course purchase card with price breakdown, old price strike-through, and `(T "buyDefaultText")` localization.
- **`layouts/_partials/custom/head-end.html` (lines 7-17)**:
  ```html
  {{- if .HasShortcode "framework-tool" -}}
    {{- $fwTools := resources.Get "js/framework-tools.js" -}}
    {{- if $fwTools -}}
      {{- if hugo.IsProduction -}}
        {{- $fwTools = $fwTools | minify | fingerprint -}}
      {{- end -}}
      <script src="{{ $fwTools.RelPermalink }}" integrity="{{ $fwTools.Data.Integrity }}" defer></script>
    {{- else -}}
      <script src="{{ "js/framework-tools.js" | relURL }}" defer></script>
    {{- end -}}
  {{- end -}}
  ```
- **`layouts/_partials/scripts.html` (lines 1-11)**: Included by `layouts/baseof.html` right before `</body>`:
  ```html
  {{/* Core scripts (theme, menu, tabs, etc.) */}}
  {{- partialCached "scripts/core.html" . .Language.Lang -}}
  {{/* Search */}}
  {{- partialCached "scripts/search.html" . .Language.Lang -}}
  {{/* Mermaid */}}
  {{- if (.Store.Get "hasMermaid") -}}
    {{- partial "scripts/mermaid.html" . -}}
  {{- end -}}
  ```

### 1.2 Content Invocations across `content/docs/books/`
- Tool command: `python3` AST regex search across all `content/**/*.md`.
- Result: **420 invocations** of `{{< book-download ... >}}`.
- Parameter keys observed across the repository: `['format', 'lang', 'size', 'title', 'url']`.
- Representative calls:
  - `content/docs/books/how-to-succeed-with-your-remote-design-team.md:53`:
    `{{< book-download url="https://dl.theminiceo.ir/How%20to%20Succeed%20with%20Your%20Remote%20Design%20Team.pdf" title="دانلود کتاب How to Succeed with Your Remote Design Team (نسخه کامل)" size="15.9 مگابایت" format="PDF" >}}`
  - `content/docs/books/Escaping-the-Build-Trap.md:87`:
    `{{< book-download url="https://dl.theminiceo.ir/Escaping_the_Build_Trap_How_Effective_Product_Management_Creates.pdf" title="دانلود کتاب Escaping the Build Trap (نسخه اصلی انگلیسی)" size="20.9 مگابایت" format="PDF" >}}`
  - `content/docs/books/atomic-habits-clear-james-2018.md:50`:
    `{{< book-download url="https://dl.theminiceo.ir/Atomic%20Habits%20%28Clear%2C%20James%20-%202018%29.pdf" title="دانلود کتاب Atomic Habits (نسخه کامل)" size="3.9 مگابایت" format="PDF" >}}`
- Target URL pattern: 100% of URLs point to `https://dl.theminiceo.ir/<filename>.pdf`.
- `data/books_metadata.json`: Contains 390+ books with fields `filename`, `title`, `slug`, `format`, `size_bytes`, `size_str`, `download_url`.

### 1.3 Styling, Theme, and JavaScript Architecture
- **Theme**: Hextra (`themes/hextra`).
- **Dark/Light Theme Toggle** (`themes/hextra/assets/js/theme.js:8-38`):
  - State persisted in `localStorage.getItem("color-theme")` ('dark' | 'light').
  - Active theme applied via CSS class `dark` on root element `document.documentElement.classList.add("dark")` / `classList.remove("dark")`.
  - Inline head script in `themes/hextra/layouts/_partials/head.html:63-84` executes before render to prevent theme flashing.
- **CSS Architecture** (`assets/css/custom.css`):
  - Uses standard `.dark .selector` and `html.dark .selector` overrides.
  - Directional styling supported via `[dir="rtl"]` and `[dir="ltr"]`.
  - Typography uses Vazirmatn variable font (`--font-sans`).
- **Interactive JS Patterns** (`assets/js/framework-tools.js:1-14`):
  - Self-contained vanilla JS with UMD wrapper, DOMContentLoaded auto-mount, zero NPM dependencies at runtime.
  - Bilingual string dictionaries: `COPY = { fa: { ... }, en: { ... } }`.
  - Hugo compilation: `hugo --renderToMemory` succeeded with 0 errors in 5589 ms (723 FA pages, 270 EN pages).

---

## 2. Logic Chain

1. **Shortcode Drop-in Compatibility**:
   - *From Observation 1.1 & 1.2*: All 420 existing book pages invoke `{{< book-download ... >}}` with `url`, `title`, `size`, `format`, and optionally `lang`.
   - *Inference*: The upgraded shortcode must accept the exact same parameter interface so that all existing markdown pages render seamlessly without touching 420 content files.
   - *Inference*: In `layouts/shortcodes/book-download.html`, the R2 object key can be extracted directly via Hugo:
     `{{ $fileKey := path.Base $url }}` or passed to the DOM element via data attributes: `data-book-id="{{ $fileKey }}" data-book-title="{{ $title }}"`.

2. **Paywall UX: In-Page Card vs. Modal**:
   - *From Observation 1.1*: `book-download-box` currently occupies a distinct container at the end of every book article.
   - *Inference*: Rather than a floating modal that could suffer z-index conflicts or mobile overflow issues, an interactive paywall card embedded directly in `book-download.html` (which expands or tabs into the payment flow) provides a superior, frictionless user experience. An optional modal toggle can sit inside the card if a compact preview is preferred.

3. **Dynamic QR Code Generation**:
   - *From Observation 1.3*: The project does not currently have any QR code generator.
   - *Inference*: For static Hugo sites, external QR image APIs (e.g., Google Charts, api.qrserver.com) introduce external network dependencies, privacy leaks, and latency.
   - *Inference*: A zero-dependency client-side vanilla JS QR Code generator in `assets/js/paywall-qr.js` (or bundled with `book-paywall.js`) that produces a crisp SVG element is optimal:
     - Pure vector SVG renders sharply on high-DPI displays.
     - Enclosed in a white quiet-zone container (`bg-white p-3 rounded-xl`) to ensure camera scanners reliably decode the QR code even when the website is in dark mode.

4. **Cloudflare Worker API Integration Flow**:
   - *From Observation 1.1, 1.2 & Orchestrator Scope*:
     - Client requires store wallet address, supported networks, and fixed price (5 USDT).
     - Flow:
       1. **Step 1 (Network Selection)**: User selects network: BNB Smart Chain (`bsc`), Polygon (`polygon`), or Arbitrum (`arbitrum`).
       2. **Step 2 (Payment Display)**: UI updates the QR code, store address, and warning badge for the selected network. Quick-copy button copies address to clipboard.
       3. **Step 3 (Transaction Submission)**: User enters their email and the transaction hash (TxHash).
       4. **Step 4 (Verification Request)**: Client issues `POST /api/verify-payment`:
          ```json
          {
            "network": "bsc",
            "txHash": "0x...",
            "bookId": "filename.pdf",
            "bookTitle": "...",
            "email": "user@example.com"
          }
          ```
       5. **Step 5 (Response & Download Trigger)**:
          - If successful (`200 OK` with `{ success: true, downloadUrl: "...", expiresAt: ... }`):
            - Frontend unlocks the download button.
            - Automatically triggers download (`window.location.assign(downloadUrl)` or synthetic `<a>` click).
            - Displays success banner notifying that a backup link valid for 2 hours was also emailed.
            - Caches token/state in `localStorage` under `tmc_unlocked_<bookId>` to maintain unlocked state on page refresh.
          - If error (`400/409/422` with `{ success: false, error: "REPLAY_DETECTED" | "INSUFFICIENT_AMOUNT" | ... }`):
            - Frontend shows precise localized error feedback with retry action.

5. **Theme & Asset Integration**:
   - *From Observation 1.1 & 1.3*: Hugo Pipes (`resources.Get` + `minify` + `fingerprint`) in `layouts/_partials/scripts.html` or `layouts/_partials/custom/head-end.html` allows lazy loading `book-paywall.js` only on pages that contain `book-download`.
   - *Inference*: Using `.dark .paywall-*` and CSS variables ensures seamless styling matching Hextra's dark/light toggle with zero flickering.

---

## 3. Caveats

1. **Worker API Hostname**:
   In production, the Cloudflare Worker can be routed on a custom subdomain (e.g. `https://pay.theminiceo.ir` or `/api/verify-payment` via Cloudflare Route). The frontend script must have a configurable `apiUrl` parameter (defaulting to relative `/api` or `site.Params.paywall.api_url`).
2. **Direct R2 Access Deprecation**:
   Existing book pages currently have URLs like `https://dl.theminiceo.ir/Book.pdf`. Once the R2 paywall is activated in Cloudflare, direct GET requests to `dl.theminiceo.ir` without a valid token must be blocked (or redirected to the corresponding book landing page).
3. **Web3 Provider Availability**:
   Web3 one-click transfer via `window.ethereum` is an optional accelerator for desktop browser users with MetaMask/Rabby. Mobile users and exchange senders must always have first-class support for manual TxHash entry.

---

## 4. Conclusion

The Hugo static site architecture is well-suited for the crypto paywall upgrade:
1. **Shortcode Structure**: Upgrading `layouts/shortcodes/book-download.html` with backward-compatible parameters (`url`, `title`, `size`, `format`, `lang`) maintains 100% compatibility across all 420 book entries.
2. **Component Model**: An interactive in-page Paywall Card with 3 clear steps (Network Selection -> Payment & Copy -> Submit TxHash & Email) provides the most robust UX without modal dialog complications.
3. **QR Code Engine**: A client-side SVG QR code generator embedded in `assets/js/` provides zero-latency, offline-capable vector rendering with a dedicated light quiet-zone box for dark-mode contrast.
4. **API Integration**: Direct `fetch` calls to `POST /api/verify-payment` with immediate unlock and automatic download trigger without page reload.
5. **Theme & Localization**: Full compatibility with Hextra's `.dark` class system, RTL/LTR layout, and dual-language strings (`fa`/`en`).

---

## 5. Verification Method

### Independent Verification Steps:
1. **Inspect Shortcode Invocations**:
   Run:
   ```bash
   python3 -c "import glob, re; files = glob.glob('content/**/*.md', recursive=True); matches = sum(len(re.findall(r'\{\{<\s*book-download', open(f, encoding='utf-8').read())) for f in files); print(f'Total shortcodes: {matches}')"
   ```
   Confirm output equals 420.
2. **Verify Hugo Compilation**:
   Run:
   ```bash
   hugo --renderToMemory
   ```
   Confirm exit code 0 and successful rendering of both Persian and English sites.
3. **Inspect Theme Dark Mode Selector**:
   Inspect `themes/hextra/assets/js/theme.js` lines 8-38 to confirm `.dark` class management on `document.documentElement`.
4. **Invalidation Conditions**:
   - If any book page uses positional arguments incompatible with `.Get "url" | default (.Get 0)`.
   - If Hugo build fails with custom JS asset inclusion in `_partials/scripts.html`.
