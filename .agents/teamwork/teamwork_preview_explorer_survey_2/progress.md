# Progress — survey_explorer_2

Last visited: 2026-10-10T14:12:30Z
Current status: Investigation complete. All deliverables finalized and verified. Ready to submit handoff to orchestrator.

## Steps
- [x] Initialized DISPATCH.md, BRIEFING.md, and progress.md
- [x] Investigate authoritative public EVM RPC endpoints for BSC, Polygon, Arbitrum One
  - Discovered critical deprecation: `polygon-rpc.com` retired in 2026; replaced with PublicNode, 1RPC, dRPC
  - Identified multi-tier fallback architecture for BSC, Polygon, and Arbitrum One
- [x] Verify canonical USDT contract addresses, decimals, and ABI signatures
  - BSC: 0x55d398326f99059ff775485246999027b3197955 (18 decimals, 5 * 10^18 units)
  - Polygon: 0xc2132D05D31c914a87C6611C10748AEb04B58e8F (6 decimals, 5 * 10^6 units)
  - Arbitrum: 0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9 (6 decimals, 5 * 10^6 units)
- [x] Specify JSON-RPC parsing, confirmation depth, topic/data extraction logic
  - Event Topic0: 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
  - Decoded 32-byte topics to 20-byte addresses; BigInt decoding for data field
  - Confirmation requirements: BSC (3 blocks), Polygon (10 blocks), Arbitrum (2 blocks)
- [x] Design replay protection architecture (KV vs D1, key format, atomicity)
  - Detailed D1 ACID schema with PRIMARY KEY unique conflict handling
  - Detailed KV alternative with `redeemed:${network}:${txHash}` key structure
- [x] Formulate comprehensive error taxonomy, validation stages, and fallback strategies
  - Detailed 12 distinct diagnostic error codes with user-friendly remediation messages
- [x] Compiled handoff.md with full reference TypeScript implementation
- [x] Send completion message via send_message to orchestrator
