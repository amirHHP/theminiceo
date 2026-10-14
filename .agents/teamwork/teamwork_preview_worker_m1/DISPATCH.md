## 2026-10-10T14:16:30Z
You are worker_m1 (teamwork_preview_worker).
Your working directory is: /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_worker_m1/

You MUST read:
- /Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md (lines 52-100 contain user requirements for crypto paywall)
- /Users/sotoon/personal/theminiceo/.agents/teamwork/orchestrator_3/PROJECT.md
- /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_2/handoff.md (detailed EVM RPC architecture & reference implementation)
- /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_spec_miner_survey_3/handoff.md (API contracts & schemas)

Your Objective:
Implement Milestone 1: Direct On-Chain Crypto Payment Verification Worker in `workers/paywall/`:
1. Initialize `workers/paywall/`:
   - `package.json`, `tsconfig.json`, `wrangler.toml` (with D1 database binding `DB`, KV namespace binding `PAYMENT_KV`, environment variables `STORE_WALLET_ADDRESS = "0x5A0b54D5dc17e0AadC383d2db43B0a0D3E029c4c"`, `USDT_PRICE = "5.00"`).
   - SQL schema `schema.sql` for D1 `redeemed_transactions` table with PRIMARY KEY `tx_hash`.
2. Multi-Chain Network Configuration (`src/config.ts`):
   - BSC (BEP-20, Chain ID 56): USDT `0x55d398326f99059ff775485246999027b3197955`, 18 decimals, min units `5000000000000000000n`, min confs 3, fallback RPCs.
   - Polygon (PoS, Chain ID 137): USDT `0xc2132D05D31c914a87C6611C10748AEb04B58e8F`, 6 decimals, min units `5000000n`, min confs 10, fallback RPCs (avoid deprecated polygon-rpc.com).
   - Arbitrum One (Chain ID 42161): USDT `0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9`, 6 decimals, min units `5000000n`, min confs 2, fallback RPCs.
3. Fault-Tolerant EVM RPC Client (`src/rpc.ts`):
   - JSON-RPC caller with 3500ms timeout using `AbortController` and fallback URL cycling.
   - Methods: `eth_getTransactionReceipt`, `eth_getTransactionByHash`, `eth_blockNumber`.
4. Payment Verification Engine (`src/verifier.ts`):
   - Format validation (`^0x[0-9a-fA-F]{64}$`).
   - Native `BigInt` arithmetic for units to eliminate IEEE 754 precision errors.
   - Transfer event log parsing: Topic0 `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`, recipient topic2 matching store wallet, amount in data field >= min units.
   - Multi-log traversal to handle DEX aggregators / contract callers.
   - 12 structured diagnostic errors with helpful user feedback.
5. Persistent Replay Protection (`src/replay.ts`):
   - Atomic check and registration in D1 (`INSERT INTO redeemed_transactions ...`) and/or KV (`tx:${network}:${txHash}`).
6. Worker Entrypoint (`src/index.ts`):
   - CORS handling with options preflight.
   - `GET /api/config` returning networks, store wallet, 5 USDT price, token contracts.
   - `POST /api/verify-payment` implementing the full verification flow.
7. Verification & Self-Test:
   - Provide unit/integration tests or a verification script in `workers/paywall/` to ensure all verification logic and BigInt math run cleanly and error cases are correctly handled.

DO NOT CHEAT. All implementations must be genuine. DO NOT
hardcode test results, create dummy/facade implementations, or
circumvent the intended task. A teamwork_preview_auditor will independently
verify your work. Integrity violations WILL be detected and your
work WILL be rejected.

Exclusively Owned Files:
- `workers/paywall/*`

Deliver your completion report in /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_worker_m1/handoff.md and notify your orchestrator via send_message.
