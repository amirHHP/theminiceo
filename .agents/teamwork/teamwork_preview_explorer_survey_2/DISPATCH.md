## 2026-10-10T14:04:23Z
From: 9ed02628-d33c-493d-a7b6-1a1e0cf0ad72 (parent)

You are survey_explorer_2 (teamwork_preview_explorer).
Your working directory is: /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_2/
You MUST read:
- /Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md (under 2026-10-10T14:01:00Z)

Your Objective:
Survey and design the direct on-chain crypto payment verification architecture for Cloudflare Workers without third-party payment gateways:
1. Identify authoritative public EVM RPC endpoints for low-fee networks: BNB Smart Chain (BSC - BEP20), Polygon (POS), Arbitrum One.
2. Identify canonical USDT contract addresses on BSC (0x55d398326f99059fF775485246999027B3197955), Polygon (0xc2132D05D31c914a87C6611C10748AEb04B58e8F), Arbitrum One (0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9), including decimals (BSC=18, Polygon=6, Arbitrum=6).
3. Specify JSON-RPC methods (`eth_getTransactionReceipt`, `eth_getTransactionByHash`, `eth_blockNumber`) to verify:
   - Status: confirmed (status == "0x1") and sufficient confirmations.
   - Logs parsing: standard ERC-20 `Transfer(address from, address to, uint256 value)` event (Topic0: `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`).
   - Verifying log contract address matches legitimate USDT.
   - Verifying recipient (`to` address in topic2) matches designated store wallet address.
   - Verifying value in data field is >= 5 USDT (accounting for network decimals).
4. Replay protection design: Cloudflare KV or D1 schema, key structure (`redeemed:${network}:${txHash}`), atomic check-and-set, persistence.
5. Error cases and diagnostics: fake tokens, wrong recipient, insufficient amount, pending/failed tx, invalid tx hash, RPC timeout/fallback strategy.

Constraints:
- You are read-only. Do NOT write or modify source code files.
- Deliver your detailed report in /Users/sotoon/personal/theminiceo/.agents/teamwork/teamwork_preview_explorer_survey_2/handoff.md.
- Send a completion message via send_message to your orchestrator when done.
