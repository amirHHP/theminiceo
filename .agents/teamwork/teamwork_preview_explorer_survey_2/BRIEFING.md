# BRIEFING — 2026-10-10T14:11:00Z

## Mission
Survey and design the direct on-chain crypto payment verification architecture for Cloudflare Workers without third-party payment gateways for BSC, Polygon, and Arbitrum One USDT payments.

## 🔒 My Identity
- Archetype: teamwork_preview_explorer
- Roles: explorer, analyst, architecture designer
- Working directory: /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_2/
- Original parent: 9ed02628-d33c-493d-a7b6-1a1e0cf0ad72
- Milestone: Survey & Architecture Design (Crypto Paywall R1)

## 🔒 Key Constraints
- Read-only investigation — do NOT implement or modify source code files
- Deliver detailed report in /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_2/handoff.md
- Send completion message via send_message to orchestrator (9ed02628-d33c-493d-a7b6-1a1e0cf0ad72) when done

## Current Parent
- Conversation ID: 9ed02628-d33c-493d-a7b6-1a1e0cf0ad72
- Updated: not yet

## Investigation State
- **Explored paths**:
  - Web3 EVM RPC registries (Chainlist, BNBChain official docs, Polygon documentation, Arbitrum Nitro docs)
  - Canonical USDT contract specifications & token standards
  - Cloudflare Workers runtime capabilities (Fetch API, BigInt, D1 SQLite ACID transactions, KV eventual consistency)
- **Key findings**:
  - Found Polygon official RPC (`polygon-rpc.com`) was decommissioned; reliable fallbacks identified (PublicNode, 1RPC, dRPC).
  - Crucial decimal divergence: BSC BEP-20 USDT has 18 decimals (`5 * 10^18`), while Polygon and Arbitrum One have 6 decimals (`5 * 10^6`). JS native `BigInt` is mandatory to avoid IEEE 754 precision loss on BSC.
  - ERC-20 Transfer Topic0 `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef` verified. Recipient address extracted from rightmost 20 bytes (40 hex chars) of Topic2.
  - Replay protection: Cloudflare D1 `PRIMARY KEY (tx_hash)` provides true ACID atomicity against race conditions; Cloudflare KV provides lightweight global key-value fallback with `redeemed:${network}:${txHash}`.
  - Formulated full JSON-RPC verification flow with fallback array, request abort timeout, and diagnostic error codes.
- **Unexplored areas**: None. Technical survey is comprehensive and complete.

## Key Decisions Made
- Recommend multi-tier RPC fallback array with `AbortSignal.timeout(3500)` per request.
- Recommend Cloudflare D1 for authoritative atomic replay protection, with KV schema documented for zero-database deployment.
- Enforce strict BigInt arithmetic for raw token amounts across all chains.

## Artifact Index
- /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_2/DISPATCH.md — Dispatch log
- /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_2/BRIEFING.md — Situational awareness
- /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_2/progress.md — Liveness heartbeat
- /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_2/handoff.md — Final 5-component report
