# Plan: theminiceo Crypto Paywall System

## Objective
Implement and verify a production-grade decentralized, non-KYC crypto paywall for book downloads on `theminiceo` static site:
1. Direct On-Chain Crypto Payment Verification via Cloudflare Workers (zero-intermediary EVM public RPC for USDT on BSC, Polygon, Arbitrum; recipient, contract, amount checks, replay protection).
2. Secure File Delivery & Expiring Download Links (Cloudflare R2 protection, presigned expiring URLs, backup email dispatch).
3. Hugo Frontend Checkout & Paywall Component (responsive paywall card/modal in `layouts/shortcodes/book-download.html`, network selector, QR code, instant verification, dark/light mode).

## Orchestration Plan
### Phase 0: Survey & Scope Mapping
- Dispatch 3 parallel Explorers:
  - Explorer 1 (`survey_explorer_1`): Survey Hugo codebase, shortcodes (`layouts/shortcodes/book-download.html`), assets, scripts, existing download links, styling and themes.
  - Explorer 2 (`survey_explorer_2`): Survey EVM RPC integration patterns, USDT contracts (BSC, Polygon, Arbitrum), transaction receipt decoding, replay protection options (KV/D1/in-memory/storage), and Cloudflare Worker architecture.
  - Explorer 3 (`survey_explorer_3`): Survey Cloudflare R2 bucket configuration, presigned URL generation mechanisms in Cloudflare Workers, and email delivery integrations (Resend API / Cloudflare Email Workers).
- Synthesize findings into `PROJECT.md` (Architecture, Feature Inventory, Milestones, Code Layout, Interface Contracts) and `TEST_INFRA.md`.

### Phase 1: Dual Track Execution
- **Track 1: Implementation Track**
  - Milestone 1: Cloudflare Worker backend for direct EVM on-chain RPC verification (BSC, Polygon, Arbitrum USDT), amount validation (≥ 5 USDT), store address validation, replay protection.
  - Milestone 2: Cloudflare R2 secure bucket protection, time-limited presigned download URL generation (e.g. 2h), and backup email dispatch service.
  - Milestone 3: Hugo frontend checkout component upgrade (`layouts/shortcodes/book-download.html`, CSS/JS assets, QR code generation, network selector, transaction submission, real-time UI states, dark/light mode).
- **Track 2: E2E Testing Track**
  - Comprehensive 4-Tier test suite covering on-chain RPC verification, edge cases (bad hash, wrong token, wrong recipient, insufficient amount, replay attack), R2 presigning expiration, email dispatch, and Hugo frontend integration.

### Phase 2: Final Milestone & Gate
- Verify 100% of E2E tests pass.
- Adversarial coverage hardening.
- Forensic Auditor integrity check (clean verification, no dummy facades/hardcoding).
- Final delivery report to Sentinel.
