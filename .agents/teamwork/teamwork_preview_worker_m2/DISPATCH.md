## 2026-10-10T14:40:59Z

You are worker_m2 (teamwork_preview_worker).
Your working directory is: /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_worker_m2/

You MUST read:
- /Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md (lines 52-100 contain user requirements for crypto paywall)
- /Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_3/PROJECT.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_3/TEST_INFRA.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_spec_miner_survey_3/handoff.md (detailed specifications for R2, tokens, and email)
- /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_worker_m1/handoff.md (Milestone 1 foundation)

Your Objective:
Implement Milestone 2: Secure File Delivery, Cloudflare R2 Streaming, Expiring HMAC Download Links, and Resend Backup Email Dispatch in `workers/paywall/`:
1. Cloudflare R2 Bucket Binding & Storage (`src/storage.ts`):
   - In `wrangler.toml`, ensure `r2_buckets` binding `BOOKS_BUCKET` is configured for bucket `theminiceo-books`.
   - Implement `fetchBookFromR2(env, filename, rangeHeader?)`:
     - Accesses private bucket via `env.BOOKS_BUCKET.get(filename, { range: ... })`.
     - Streams object body (`object.body`) directly with zero memory buffering.
     - Sets RFC 6266 `Content-Disposition: attachment; filename="<slug>.pdf"; filename*=UTF-8''<encoded-title>.pdf`.
     - Sets `Content-Type: application/pdf`, `ETag`, `Content-Length`, `Accept-Ranges: bytes`.
     - Supports HTTP Range requests: returns HTTP 206 Partial Content when `Range` header is provided.
     - Returns HTTP 404 `FILE_NOT_FOUND` if object does not exist in R2.
2. Web Crypto HMAC Expiring Download Tokens (`src/token.ts`):
   - Signed URL structure: `/api/download?token=<base64url_payload>.<base64url_sig>`.
   - Native Web Crypto `crypto.subtle` HMAC-SHA256 signature over raw base64url payload string.
   - Payload: `{ bookId, filename, txHash, email, network, iat, exp, nonce }`.
   - Expiration: exactly 2 hours (`exp = iat + 7200`).
   - Token Verification:
     - Catch malformed token strings -> HTTP 400 `MALFORMED_TOKEN`.
     - Missing token -> HTTP 400 `MISSING_TOKEN`.
     - Invalid / tampered signature -> HTTP 403 `INVALID_SIGNATURE`.
     - Past expiration timestamp (`exp < Date.now() / 1000`) -> HTTP 410 `TOKEN_EXPIRED`.
3. Download Attempt Rate Limiter (`src/token.ts` or `src/replay.ts`):
   - KV counter `dl_count:${txHash}`.
   - Allows up to 5 download attempts per token.
   - 6th attempt returns HTTP 429 `DOWNLOAD_LIMIT_EXCEEDED`.
4. Backup Email Dispatch Integration (`src/email.ts`):
   - Asynchronous and non-blocking in `ctx.waitUntil(sendBackupEmail(...))`.
   - Resend REST API integration (`POST https://api.resend.com/emails`).
   - Responsive bilingual HTML and plaintext email templates (English & Persian) containing book details, 2-hour expiring download CTA button, transaction receipt, expiration notice, and support contact.
   - Graceful fallback when `RESEND_API_KEY` is not configured (simulated in local dev/tests, logs cleanly, does not fail the purchase).
5. Router & Endpoints Integration (`src/index.ts`):
   - Implement `GET /api/download?token=...`: verifies token, checks expiration, enforces download limit, streams PDF from R2.
   - In `POST /api/verify-payment`: trigger `ctx.waitUntil(sendBackupEmail(...))` on successful verification and return `emailDispatched: true` in response.
   - Harden input validation on `verifyPayment`: ensure `typeof txHash === "string"` and `typeof network === "string"` to prevent type confusion errors on malformed JSON bodies.
6. Tests & Verification:
   - Add unit/integration tests in `workers/paywall/test/` covering storage streaming, range requests, token expiry/tampering, download attempt limit, and email dispatch.
   - Run `npm run typecheck`, `npm run build`, and `npm test` in `workers/paywall/`.
   - Run `python3 scripts/test_crypto_paywall_e2e.py -v`. Ensure 100% of tests pass.

DO NOT CHEAT. All implementations must be genuine. DO NOT
hardcode test results, create dummy/facade implementations, or
circumvent the intended task. A teamwork_preview_auditor will independently
verify your work. Integrity violations WILL be detected and your
work WILL be rejected.

Exclusively Owned Files:
- `workers/paywall/*`

Deliver your completion report in /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_worker_m2/handoff.md and notify your orchestrator via send_message.
