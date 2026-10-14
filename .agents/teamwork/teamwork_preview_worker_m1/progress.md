# Progress — Milestone 1: Crypto Paywall Worker

Last visited: 2026-10-10T14:28:30Z

## Status
- [x] Initialized DISPATCH.md and BRIEFING.md
- [x] Reviewed upstream research, specs, and requirements
- [x] Initialized `workers/paywall/`:
  - `package.json` (ESM, scripts, devDependencies)
  - `tsconfig.json` (ES2022, NodeNext resolution, strict)
  - `wrangler.toml` (D1 DB binding, KV PAYMENT_KV binding, STORE_WALLET_ADDRESS, USDT_PRICE)
  - `schema.sql` (D1 table redeemed_transactions with PRIMARY KEY tx_hash)
- [x] Implemented `src/config.ts`:
  - BSC (Chain ID 56, 18 decimals, 5000000000000000000n, min confs 3, fallback RPCs)
  - Polygon (Chain ID 137, 6 decimals, 5000000n, min confs 10, fallback RPCs without polygon-rpc.com)
  - Arbitrum One (Chain ID 42161, 6 decimals, 5000000n, min confs 2, fallback RPCs)
  - Pure BigInt formatting and format validators
- [x] Implemented `src/rpc.ts`:
  - Fault-tolerant EVM JSON-RPC client with 3500ms AbortController timeout
  - Endpoint failover cycling
  - eth_getTransactionReceipt, eth_getTransactionByHash, eth_blockNumber
- [x] Implemented `src/replay.ts`:
  - Atomic D1 PRIMARY KEY check and insert
  - Cloudflare KV namespace check and put
  - Safe error handling for duplicate transactions
- [x] Implemented `src/verifier.ts`:
  - Format regex validation
  - Confirmation depth verification
  - Multi-log traversal for DEX aggregators & routers
  - Strict canonical USDT token address and store wallet recipient matching
  - 12 structured diagnostic errors with exact codes and messages
- [x] Implemented `src/token.ts`:
  - Web Crypto HMAC-SHA256 2-hour expiring download tokens
  - Base64Url encoding/decoding
- [x] Implemented `src/manifest.json`:
  - Book metadata lookup mapping slugs to filenames
- [x] Implemented `src/index.ts`:
  - CORS preflight and headers
  - GET /api/config
  - POST /api/verify-payment
- [x] Verified and tested:
  - 41 unit/integration tests passing in `workers/paywall` (6 suites, 0 failures)
  - 36/36 tests passing in `scripts/test_crypto_paywall_e2e.py` (204 assertions, 0 failures)
  - wrangler types generated successfully
