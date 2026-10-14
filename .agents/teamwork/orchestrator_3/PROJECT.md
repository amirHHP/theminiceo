# Project: theminiceo Crypto Paywall System

## Architecture
- **Backend Runtime**: Cloudflare Workers (TypeScript / V8 engine with Fetch API, Web Crypto `crypto.subtle`, native `BigInt`, R2 bucket binding, and KV/D1 bindings).
- **Blockchain Verification Engine**: Direct zero-intermediary JSON-RPC queries to public node clusters on BNB Smart Chain (BEP-20), Polygon (PoS), and Arbitrum One.
- **Storage & Security**: Cloudflare R2 bucket (`theminiceo-books`) configured with public access disabled; accessed strictly via Worker internal binding.
- **Expiring Links**: URL-safe HMAC-SHA256 signed tokens (`/api/download?token=...`) with 2-hour expiration, tamper-proof payload, and download attempt counters.
- **Email Delivery**: Asynchronous backup download dispatch via Resend REST API using native `fetch()` inside `ctx.waitUntil(...)`.
- **Frontend Integration**: Hugo static site (`theminiceo`), upgrading `layouts/shortcodes/book-download.html` into an interactive paywall card with zero-dependency client-side vector SVG QR code generation (`assets/js/paywall-qr.js`), responsive checkout controller (`assets/js/book-paywall.js`), dark/light theme matching Hextra (`.dark` class), and bilingual RTL/LTR support.

---

## Feature Inventory
Every feature identified during the Survey phase is assigned to a milestone below:

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Configuration Endpoint (`GET /api/config`) | Exposes supported networks, store wallet, 5 USDT price, token contracts, and explorer URLs | M1 | Survey / R1 |
| 2 | Multi-Chain RPC Client with Fallback | Fault-tolerant EVM JSON-RPC client with 3.5s timeout, AbortController, and multi-endpoint failover | M1 | Survey / R1 |
| 3 | Canonical USDT & Decimals Normalization | Validates canonical contract addresses on BSC (18 dec), Polygon (6 dec), Arbitrum (6 dec) using native `BigInt` | M1 | Survey / R1 |
| 4 | Transaction Receipt & Confirmation Checks | Validates status (`0x1`), block confirmations (BSC 3, Polygon 10, Arbitrum 2), and pending mempool states | M1 | Survey / R1 |
| 5 | ERC-20 Transfer Log Parsing & Multi-Log Traversal | Decodes `Transfer` event (topic0), recipient address (topic2), and verifies amount >= 5 USDT | M1 | Survey / R1 |
| 6 | Persistent Replay Protection | Atomic check-and-insert using Cloudflare D1 (PRIMARY KEY) and KV storage (`tx:${network}:${txHash}`) | M1 | Survey / R1 |
| 7 | Diagnostic Error Taxonomy | 12 structured error codes with clear user-facing messages for invalid hashes, wrong tokens, underpayment, etc. | M1 | Survey / R1 |
| 8 | Cloudflare R2 Binding & Object Key Mapping | Private bucket binding (`env.BOOKS_BUCKET`) and whitelist manifest mapping `bookId` to R2 filenames | M2 | Survey / R2 |
| 9 | Web Crypto HMAC Expiring Download Tokens | Generates and verifies 2-hour HMAC-SHA256 signed download tokens using native `crypto.subtle` | M2 | Survey / R2 |
| 10 | Streamed File Delivery (`GET /api/download`) | Streams PDF from R2 with RFC 6266 `Content-Disposition`, MIME type, and HTTP Range support | M2 | Survey / R2 |
| 11 | Download Attempt Limiter | KV-backed counter limiting successful downloads to 5 attempts per token to prevent unauthorized redistribution | M2 | Survey / R2 |
| 12 | Backup Email Dispatch (Resend API) | Asynchronous email dispatch via Resend REST API in `ctx.waitUntil` with bilingual template and receipt | M2 | Survey / R2 |
| 13 | Security Controls & CORS Whitelist | IP sliding-window rate limiting (5 req/min) and strict CORS origin validation | M2 | Survey / R2 |
| 14 | Hugo Shortcode Upgrade (`book-download.html`) | Upgrades shortcode to interactive paywall card while maintaining 100% backward compatibility for all 420 book pages | M3 | Survey / R3 |
| 15 | Standalone Client-Side SVG QR Code Engine | Zero-dependency vanilla JS vector QR generator (`assets/js/paywall-qr.js`) with high-contrast quiet-zone container | M3 | Survey / R3 |
| 16 | Paywall UI Controller (`book-paywall.js`) | Handles network selection, wallet copy, TxHash & email input, validation, and API communication | M3 | Survey / R3 |
| 17 | Real-Time UI States & Error Handling | Clear visual feedback for idle, pending verification, confirmation countdown, error, and success states | M3 | Survey / R3 |
| 18 | Instant Download Trigger & Session Caching | Unlocks download button immediately without page reload and caches unlocked state in `localStorage` | M3 | Survey / R3 |
| 19 | Dark/Light Mode & Bilingual Styling | CSS styles supporting Hextra theme dark mode (`.dark`), custom variables, and Persian/English RTL/LTR | M3 | Survey / R3 |
| 20 | E2E Opaque-Box Test Suite (Tiers 1-4) | Comprehensive test suite (`scripts/test_crypto_paywall_e2e.py`) validating all 4 tiers against requirements | E2E Track | Acceptance Criteria |
| 21 | Adversarial Hardening (Tier 5) & Audit Gate | White-box adversarial testing, edge case stress-testing, and Forensic Auditor integrity verification | M4 (Phase 2) | Acceptance Criteria |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | On-Chain EVM Payment Verification Worker | Implement Cloudflare Worker payment verification engine (`workers/paywall/src/`), multi-chain RPC client, native BigInt decimal validation, receipt/log parsing, D1/KV replay protection, and `GET /api/config`, `POST /api/verify-payment` endpoints | none | DONE |
| M2 | Secure R2 File Delivery, Expiring Links & Email Dispatch | Implement Cloudflare R2 private streaming, Web Crypto HMAC token generation/verification (2h expiry), download rate limiting, Resend email dispatch service, and `GET /api/download` endpoint | M1 | IN_PROGRESS |
| M3 | Hugo Frontend Paywall Shortcode & UI Component | Implement `layouts/shortcodes/book-download.html`, `assets/js/paywall-qr.js`, `assets/js/book-paywall.js`, `assets/css/paywall.css`, network selector, QR code, instant verification, dark/light theme, and RTL/LTR support | M2 | PLANNED |
| M4 | E2E Test Suite Validation, Adversarial Hardening & Final Gate | Pass 100% of E2E tests (Tiers 1-4), execute Tier 5 adversarial testing, verify forensic integrity with `teamwork_preview_auditor`, and complete Sentinel handoff | M3, E2E Track | PLANNED |

---

## Interface Contracts

### 1. `GET /api/config`
- **Output**:
  ```json
  {
    "success": true,
    "pricing": { "amount": "5.00", "currency": "USDT" },
    "storeWallet": "0x5A0b54D5dc17e0AadC383d2db43B0a0D3E029c4c",
    "networks": [
      { "id": "bsc", "name": "BNB Smart Chain (BEP-20)", "chainId": 56, "usdtContract": "0x55d398326f99059ff775485246999027b3197955", "decimals": 18 },
      { "id": "polygon", "name": "Polygon PoS", "chainId": 137, "usdtContract": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F", "decimals": 6 },
      { "id": "arbitrum", "name": "Arbitrum One", "chainId": 42161, "usdtContract": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", "decimals": 6 }
    ],
    "downloadExpirySeconds": 7200
  }
  ```

### 2. `POST /api/verify-payment`
- **Input**: `{ "network": "bsc"|"polygon"|"arbitrum", "txHash": "0x...", "bookId": "string", "email": "string" }`
- **Success (200 OK)**:
  ```json
  {
    "success": true,
    "downloadUrl": "https://theminiceo.ir/api/download?token=...",
    "expiresAt": 1791650400,
    "book": { "id": "...", "title": "...", "format": "PDF" },
    "txDetails": { "network": "bsc", "txHash": "0x...", "amountUsdt": "5.00" },
    "emailDispatched": true
  }
  ```
- **Errors**: `400 INVALID_TX_HASH`, `404 TRANSACTION_NOT_FOUND`, `202 TRANSACTION_PENDING`, `409 TRANSACTION_ALREADY_REDEEMED`, `400 INSUFFICIENT_AMOUNT`, `400 WRONG_RECIPIENT`, `429 RATE_LIMIT_EXCEEDED`, `503 RPC_CONNECTION_FAILURE`.

### 3. `GET /api/download?token=...`
- **Input**: Query parameter `token=<base64url_payload>.<base64url_sig>`
- **Output**: Streamed binary PDF (`Content-Type: application/pdf`, `Content-Disposition: attachment; filename="<slug>.pdf"`).
- **Errors**: `400 MISSING_TOKEN`, `403 INVALID_SIGNATURE`, `410 TOKEN_EXPIRED`, `404 FILE_NOT_FOUND`, `429 DOWNLOAD_LIMIT_EXCEEDED`.

### 4. Hugo Shortcode `{{< book-download ... >}}`
- **Parameters**: `url` (required/default 0), `title` (optional), `size` (optional), `format` (optional, default "PDF"), `lang` (optional, default "انگلیسی").
- **DOM Attributes**: `data-paywall-url`, `data-book-id`, `data-book-title`, `data-book-size`, `data-book-format`.

---

## Code Layout
- `workers/paywall/wrangler.toml` — Cloudflare Worker configuration, bindings, and environment variables.
- `workers/paywall/package.json` — Worker package definition and scripts.
- `workers/paywall/src/index.ts` — Worker entrypoint, router, and CORS handling.
- `workers/paywall/src/config.ts` — Multi-chain network definitions, USDT contracts, decimals, and RPC endpoints.
- `workers/paywall/src/rpc.ts` — Fault-tolerant JSON-RPC client with fallback rotation.
- `workers/paywall/src/verifier.ts` — Payment verification logic, log parsing, and BigInt math.
- `workers/paywall/src/replay.ts` — D1 & KV replay protection registry.
- `workers/paywall/src/token.ts` — Web Crypto HMAC token generation and verification.
- `workers/paywall/src/storage.ts` — R2 bucket streaming and HTTP Range support.
- `workers/paywall/src/email.ts` — Resend REST API email dispatcher and templates.
- `workers/paywall/src/manifest.json` — Book metadata lookup table mapping slugs to filenames.
- `layouts/shortcodes/book-download.html` — Upgraded paywall shortcode component.
- `assets/js/paywall-qr.js` — Client-side SVG QR code generator.
- `assets/js/book-paywall.js` — Client-side paywall UI controller.
- `assets/css/paywall.css` — Paywall component styling, dark/light theme, and RTL/LTR rules.
- `scripts/test_crypto_paywall_e2e.py` — 4-Tier E2E test suite runner.
