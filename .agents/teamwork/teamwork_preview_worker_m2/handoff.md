# Handoff Report: Milestone 2 — Secure R2 File Delivery, Expiring Links, and Resend Backup Email Dispatch

**Author**: `worker_m2` (`teamwork_preview_worker`)  
**Target Module**: `workers/paywall/*`  
**Date**: 2026-10-10  
**Handoff Type**: Hard (Milestone 2 Complete)

---

## 1. Observation

1. **Bucket Configuration and Bindings** (`workers/paywall/wrangler.toml:22-24`):
   Added Cloudflare R2 bucket binding configured for `theminiceo-books`:
   ```toml
   [[r2_buckets]]
   binding = "BOOKS_BUCKET"
   bucket_name = "theminiceo-books"
   ```

2. **Cloudflare R2 Bucket Streaming & Header Delivery** (`workers/paywall/src/storage.ts`):
   - Implemented `fetchBookFromR2(env, filename, rangeHeader?, optionsOrTitle?)`:
     - Accesses private bucket via `env.BOOKS_BUCKET.get(filename, getOptions)`.
     - Zero memory buffering: returns `new Response(object.body, { status, headers })` directly streaming the `ReadableStream` body without buffering into memory.
     - Sets RFC 6266 / RFC 5987 header: `Content-Disposition: attachment; filename="<slug>.pdf"; filename*=UTF-8''<encoded-title>.pdf`.
     - Sanitizes book slugs (`sanitizeSlug`) to strip path traversal sequences (`../../etc/passwd` -> `etc-passwd`).
     - Standard HTTP delivery headers: `Content-Type: application/pdf`, `Accept-Ranges: bytes`, `ETag`, `Content-Length`.
     - HTTP Range support (`parseRangeHeader`): supports `bytes=start-end`, `bytes=start-`, and `bytes=-suffix`. Returns HTTP 206 Partial Content with `Content-Range: bytes ${start}-${end}/${total}`.
     - Clean error handling: returns HTTP 404 `FILE_NOT_FOUND` when the object is missing or `BOOKS_BUCKET` is unconfigured.

3. **Web Crypto HMAC Expiring Download Tokens & Rate Limiter** (`workers/paywall/src/token.ts`):
   - Native Web Crypto `crypto.subtle` HMAC-SHA256 signature over raw base64url payload string (`${b64Payload}.${b64Sig}`).
   - Payload: `{ bookId, filename, txHash, email, network, iat, exp, nonce }`.
   - Expiration: exactly 2 hours (`exp = iat + 7200`).
   - Token Verification (`verifyDownloadToken`):
     - Missing token -> HTTP 400 `MISSING_TOKEN`.
     - Malformed token strings (no dot, extra dots, invalid base64url) -> HTTP 400 `MALFORMED_TOKEN`.
     - Tampered payload or signature mismatch -> HTTP 403 `INVALID_SIGNATURE`.
     - Expired timestamp (`exp < Date.now() / 1000`) -> HTTP 410 `TOKEN_EXPIRED`.
   - Download Rate Limiter (`checkAndIncrementDownloadLimit`):
     - Key format: `dl_count:${txHash.toLowerCase()}` in Cloudflare KV (`env.PAYMENT_KV`).
     - Tracks successful downloads up to 5 attempts per token.
     - 6th attempt is blocked, returning HTTP 429 `DOWNLOAD_LIMIT_EXCEEDED`.

4. **Resend Backup Email Dispatch Integration** (`workers/paywall/src/email.ts`):
   - Integrates with Resend REST API (`POST https://api.resend.com/emails`) using native fetch.
   - Generates responsive bilingual HTML and plaintext email templates (English & Persian) containing:
     - Book details (title, PDF format, digital edition),
     - High-contrast download CTA button linking to expiring signed URL,
     - Expiration notice (2-hour validity, up to 5 downloads),
     - Transaction receipt with network, amount (5.00 USDT), TxHash, and store wallet address (`0x5A0b54D5dc17e0AadC383d2db43B0a0D3E029c4c`),
     - Support contact (`support@theminiceo.ir`).
   - Graceful fallback: when `RESEND_API_KEY` is unset (local development / testing), cleanly logs and returns `{ success: true, simulated: true }` without crashing or throwing.

5. **Router Integration & Endpoint Hardening** (`workers/paywall/src/index.ts`):
   - Added `GET /api/download?token=...`: verifies token, enforces 5-download rate limit, streams PDF from R2, sets CORS headers.
   - Updated `POST /api/verify-payment`:
     - Hardened input validation against type confusion attacks: checks `typeof body.txHash === "string"`, `typeof body.network === "string"`, `typeof body.bookId === "string"`, `typeof body.email === "string"`.
     - Triggers asynchronous, non-blocking email dispatch wrapped in `ctx?.waitUntil(sendBackupEmail(...))`.
     - Returns `{ ..., emailDispatched: true }` in response.

6. **Test Executions**:
   - `npm run typecheck`: Exit code 0, 0 compiler errors.
   - `npm run build`: Exit code 0, cleanly built to `dist/`.
   - `npm test`: Exit code 0, 106 tests passed across 21 test suites in 89ms:
     - `test/storage.test.ts`: 7 tests passed (full file streaming, 206 Range requests, RFC 6266 headers, path traversal sanitization, 404 missing object).
     - `test/email.test.ts`: 4 tests passed (bilingual payload generation, simulation fallback, Resend API dispatch, error handling).
     - `test/token.test.ts`: 7 tests passed (token generation, tampering rejection, expired boundary, malformed string handling, 5-attempt rate limiter).
     - `test/api.test.ts`: 11 tests passed (download endpoint, token validation, rate limit 429, Range 206, missing 404, verify-payment email trigger with `ctx.waitUntil`).
     - `test/adversarial_challenge.test.ts`: 17 tests passed (type confusion validation safely returning 400).
   - `python3 scripts/test_crypto_paywall_e2e.py -v`:
     - 36 tests run across all 4 tiers (T1–T4).
     - 204 assertions evaluated.
     - 0 failures, 100% pass rate.

---

## 2. Logic Chain

1. **Zero Memory Buffering for Large PDF Streams**:
   By directly returning `new Response(object.body, { status, headers })` where `object.body` is the `ReadableStream` from `env.BOOKS_BUCKET.get()`, Cloudflare Worker V8 isolates stream chunks straight to the client socket without holding multi-megabyte buffers in Worker RAM (avoiding 128MB worker memory limits).

2. **RFC 6266 with UTF-8 Filename Parameter**:
   HTTP downloads across different browsers (Chrome, Safari, Firefox) handle non-ASCII filenames inconsistently when using only legacy `filename="..."`. Setting `filename="<slug>.pdf"; filename*=UTF-8''<encoded-title>.pdf` provides ASCII fallback for legacy clients while delivering accurate Persian/Unicode titles (`نوپای ناب`) on modern clients.

3. **Slug Sanitization against Path Traversal**:
   Attackers could craft download tokens with malicious slugs like `../../etc/passwd`. Passing the slug through `sanitizeSlug` strips directory separators (`/`, `\`) and leading dots before constructing headers, preventing path leakage and injection.

4. **Cryptographic Token Verification Order**:
   In `GET /api/download`, token verification proceeds in strict defense-in-depth order:
   - Format validation (`parts.length === 2`) -> 400 `MALFORMED_TOKEN`
   - Native Web Crypto HMAC verification -> 403 `INVALID_SIGNATURE`
   - Expiration timestamp check (`exp < now`) -> 410 `TOKEN_EXPIRED`
   - Download counter check (`dl_count >= 5`) -> 429 `DOWNLOAD_LIMIT_EXCEEDED`
   - R2 object retrieval -> 404 `FILE_NOT_FOUND`
   This sequence guarantees that an expired token returns 410 rather than being counted against the rate limiter, and tampered tokens are rejected before touching storage.

5. **Asynchronous Non-Blocking Email Dispatch**:
   Dispatching transactional email via Resend in `ctx.waitUntil(sendBackupEmail(...))` decouples the email HTTP latency from the payment verification response. The user receives their download link in the browser within ~100ms, while email dispatch proceeds in the background.

---

## 3. Caveats

- **Cloudflare KV Consistency**: KV counter `dl_count:${txHash}` is eventually consistent across edge nodes within ~60 seconds. For normal usage (individual users downloading their book up to 5 times), this is well within acceptable tolerance.
- **Resend Domain Verification**: In local test and preview environments, `RESEND_API_KEY` is optional and simulated. For production delivery to arbitrary customer email addresses, `books@theminiceo.ir` requires domain verification in the Resend dashboard.

---

## 4. Conclusion

Milestone 2 is completely implemented, verified, and ready:
- `workers/paywall/src/storage.ts` provides R2 streaming with RFC 6266 headers and HTTP Range requests.
- `workers/paywall/src/token.ts` provides HMAC-SHA256 download token verification and a 5-download rate limiter.
- `workers/paywall/src/email.ts` provides bilingual Resend email dispatch with receipt details and graceful fallback.
- `workers/paywall/src/index.ts` exposes `GET /api/download` and integrates `ctx.waitUntil` email delivery in `POST /api/verify-payment`.
- All 106 unit/integration tests and all 36 E2E tests pass with 100% success.

---

## 5. Verification Method

To independently verify this milestone:

1. **TypeScript Compilation & Typecheck**:
   ```bash
   cd workers/paywall
   npm run typecheck
   npm run build
   ```
   *Expected outcome*: Exit code 0, 0 type errors.

2. **Unit & Integration Test Suite**:
   ```bash
   cd workers/paywall
   npm test
   ```
   *Expected outcome*: 106 tests pass across 21 test suites in ~90ms, 0 failures.

3. **End-to-End Test Suite**:
   ```bash
   python3 scripts/test_crypto_paywall_e2e.py -v
   ```
   *Expected outcome*: 36 tests pass across Tiers 1–4 with 204 assertions, exit code 0.
