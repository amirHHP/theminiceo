# Handoff Report: Milestone 1 — Direct On-Chain Crypto Payment Verification Worker

**Author**: `worker_m1` (`teamwork_preview_worker`)  
**Target Module**: `workers/paywall/*`  
**Date**: 2026-10-10  
**Handoff Type**: Hard (Milestone 1 Complete)

---

## 1. Observation

1. **Repository Layout and Exclusively Owned Files**:
   Implemented exclusively within `workers/paywall/`:
   - `workers/paywall/package.json`: Configured with `"type": "module"`, scripts (`build`, `test`, `typecheck`), and dependencies (`@cloudflare/workers-types`, `@types/node`, `typescript`).
   - `workers/paywall/tsconfig.json`: Targets `ES2022`, `NodeNext` module and resolution, `resolveJsonModule: true`, strict typechecking.
   - `workers/paywall/wrangler.toml`: Configured with `main = "src/index.ts"`, bindings: D1 database `DB`, KV namespace `PAYMENT_KV`, environment variables `STORE_WALLET_ADDRESS = "0x5A0b54D5dc17e0AadC383d2db43B0a0D3E029c4c"`, `USDT_PRICE = "5.00"`, `BASE_URL = "https://theminiceo.ir"`, `DOWNLOAD_HMAC_SECRET = "paywall-secret-key-theminiceo-2026-prod"`.
   - `workers/paywall/schema.sql`: D1 SQL table schema `redeemed_transactions` with `tx_hash TEXT PRIMARY KEY`.
   - `workers/paywall/src/config.ts`: Multi-chain network definitions for BSC (56), Polygon (137), and Arbitrum One (42161).
   - `workers/paywall/src/rpc.ts`: Fault-tolerant JSON-RPC client with 3500ms `AbortController` timeout and fallback endpoint rotation.
   - `workers/paywall/src/replay.ts`: Persistent replay protection using D1 ACID primary key and Cloudflare KV edge namespace.
   - `workers/paywall/src/verifier.ts`: Payment verification logic with `BigInt` arithmetic, multi-log traversal, and 12 structured diagnostic errors.
   - `workers/paywall/src/token.ts`: Native Web Crypto (`crypto.subtle`) HMAC-SHA256 2-hour expiring download token engine.
   - `workers/paywall/src/manifest.json`: 524 book slugs and identifiers mapped to filenames, titles, format, and sizes.
   - `workers/paywall/src/index.ts`: Worker entrypoint with CORS preflight, `GET /api/config`, and `POST /api/verify-payment`.
   - `workers/paywall/test/*.test.ts`: 6 test suites covering config, RPC client, replay protection, verifier diagnostics, token generation, and API endpoints.

2. **Network Parameters and Decimals Verification**:
   - BSC (`0x55d398326f99059ff775485246999027b3197955`, 18 decimals, min units `5000000000000000000n`, min confs 3).
   - Polygon (`0xc2132D05D31c914a87C6611C10748AEb04B58e8F`, 6 decimals, min units `5000000n`, min confs 10). Deprecated `polygon-rpc.com` excluded.
   - Arbitrum One (`0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9`, 6 decimals, min units `5000000n`, min confs 2).

3. **Compilation & Typecheck Verification**:
   - `npm run typecheck`: Exit code 0, 0 type errors.
   - `npm run build`: Exit code 0, compiled TypeScript to `dist/src` and `dist/test`.
   - `wrangler types ./src/worker-types.d.ts`: Exit code 0, verified valid `wrangler.toml` bindings (`DB`, `PAYMENT_KV`).

4. **Test Suite Execution**:
   - `npm test` (`node --test dist/test/*.test.js`):
     - Total suites: 6
     - Total tests: 41
     - Passed: 41
     - Failed: 0
     - Duration: 61ms
   - `python3 scripts/test_crypto_paywall_e2e.py -v`:
     - Total tiers: 4 (Tiers 1–4)
     - Total tests: 36
     - Total assertions: 204
     - Passed: 36
     - Failed: 0
     - Duration: 16.01s

---

## 2. Logic Chain

1. **Precision Correctness via Native BigInt**:
   JavaScript standard numbers truncate IEEE 754 floating point precision above `9 * 10^15`. For BSC (18 decimals), 5 USDT is `5 * 10^18` (`5000000000000000000n`). By performing all arithmetic on native `BigInt` values (`rawUnits / divisor` and remainder modulo formatting), zero floating point precision loss occurs.

2. **Decimals Normalization by Network**:
   Polygon and Arbitrum One operate on 6 decimals (`minUnits = 5000000n`), whereas BSC operates on 18 decimals (`minUnits = 5000000000000000000n`). The verifier looks up the network configuration dynamically, ensuring exact threshold validation without cross-chain contamination.

3. **Resilient JSON-RPC Communication**:
   Public EVM nodes can experience intermittent timeouts or rate limits. Wrapping every request with an `AbortController` (3500ms timeout) and iterating through prioritized endpoint arrays guarantees that transient failures on an individual RPC do not fail client payment verifications.

4. **Multi-Log Traversal for Smart Contract & DEX Callers**:
   Transactions routed through aggregators or contract wallets contain multiple event logs (swap events, approvals, router fees). Searching through all receipt logs for the canonical USDT address, `0xddf252ad...` `Transfer` topic, and `0x` + `topic[2].slice(-40)` store wallet address ensures legitimate payments are never rejected simply because they were not the 0th log in the receipt.

5. **Replay Defense via D1 & KV**:
   Cloudflare D1 enforces ACID uniqueness through `tx_hash TEXT PRIMARY KEY`. Simultaneous or subsequent attempts to redeem an already processed transaction fail with SQLite unique constraint errors, preventing double-redemption attacks across edge nodes.

---

## 3. Caveats

- **Network Availability**: Public RPC endpoints are subject to third-party public node availability. In production environments, adding authenticated provider keys (e.g. Alchemy or QuickNode) to the RPC arrays can further maximize uptime.
- **Milestone Boundaries**: R2 bucket streaming (`GET /api/download`) and Resend email sending are scheduled for Milestone 2. Milestone 1 generates genuine HMAC-SHA256 expiring download tokens (`/api/download?token=...`) and registers all transactions for Milestone 2 consumption.

---

## 4. Conclusion

Milestone 1 is fully implemented, verified, and complete:
- Multi-chain network configuration (`src/config.ts`), fault-tolerant EVM RPC client (`src/rpc.ts`), D1/KV replay protection (`src/replay.ts`), verification engine (`src/verifier.ts`), Web Crypto HMAC token generator (`src/token.ts`), and Worker entrypoint (`src/index.ts`) are completely implemented.
- 12 structured diagnostic errors with exact user guidance are in place.
- All 41 unit/integration tests and all 36 E2E tests pass with 100% success (0 failures).

---

## 5. Verification Method

To independently verify this milestone:

1. **TypeScript Typecheck & Build**:
   ```bash
   cd workers/paywall
   npm run typecheck
   npm run build
   ```
   *Expected outcome*: Exit code 0, 0 compiler errors.

2. **Worker Unit & Integration Tests**:
   ```bash
   cd workers/paywall
   npm test
   ```
   *Expected outcome*: 41 tests pass across 6 suites, 0 failures.

3. **E2E Test Suite Execution**:
   ```bash
   python3 scripts/test_crypto_paywall_e2e.py -v
   ```
   *Expected outcome*: 36 tests pass across Tiers 1–4 with 204 assertions, exit code 0.
