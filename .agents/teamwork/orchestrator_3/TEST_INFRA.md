# E2E Test Infra: theminiceo Crypto Paywall System

## Test Philosophy
- **Requirement-Driven & Opaque-Box**: Tests are derived strictly from `ORIGINAL_REQUEST.md` (R1: On-Chain Payment Verification, R2: Secure File Delivery & Expiring Links, R3: Hugo Frontend Checkout & Paywall Component) and interface contracts in `PROJECT.md`.
- **Zero Mock Facades in Production**: Verification against real or fully-compliant EVM RPC formats, genuine Web Crypto HMAC signatures, authentic R2 streaming headers, and valid Hugo compilation.
- **Methodology**: 4-Tier Systematic Testing (Category-Partition, Boundary Value Analysis, Pairwise Combinatorial, and Real-World Application Scenarios).

---

## Feature Inventory & Test Mapping

| # | Feature | Requirements Source | Tier 1 (Feature) | Tier 2 (Boundary) | Tier 3 (Cross-Feature) | Tier 4 (Real-World) |
|---|---------|---------------------|:---:|:---:|:---:|:---:|
| F1 | `GET /api/config` Parameters & Pricing | R1 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F2 | Multi-Chain EVM RPC Client & Rotation | R1 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F3 | Canonical USDT & Decimals (18 BSC, 6 Poly, 6 Arb) | R1 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F4 | Transaction Confirmation Depth & Status Checks | R1 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F5 | ERC-20 Transfer Log Parsing & Recipient Match | R1 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F6 | Persistent Replay Protection (Double-Spending) | R1 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F7 | Diagnostic Error Codes & User Messages | R1 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F8 | Cloudflare R2 Private Bucket Protection | R2 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F9 | Web Crypto HMAC Expiring Download Tokens (2h) | R2 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F10 | Streamed File Delivery (`GET /api/download`) | R2 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F11 | Download Attempt Limiter (Max 5 attempts) | R2 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F12 | Backup Email Dispatch (Resend API) | R2 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F13 | Hugo Shortcode Backward Compatibility (420 books) | R3 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F14 | Standalone Client-Side SVG QR Code Generator | R3 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F15 | Paywall UI Controller & Interactive Card Flow | R3 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F16 | Real-Time UI States & Instant Download Unlock | R3 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F17 | Dark/Light Mode Theme & Bilingual RTL/LTR | R3 | ≥ 5 | ≥ 5 | ✓ | ✓ |
| F18 | Hugo Full Site Compilation (`hugo --renderToMemory`) | R3 / Site | ≥ 5 | ≥ 5 | ✓ | ✓ |

---

## Test Architecture

### Test Runner
- **Command**: `python3 scripts/test_crypto_paywall_e2e.py`
- **Options**:
  - `--tier {1,2,3,4,all}`: Filter test tier.
  - `-v`: Verbose output with assertion traces.
  - `-x`: Fail-fast mode.
  - `--json`: Machine-readable JSON output for automated gate checks.

### Coverage Thresholds
- **Tier 1 (Feature Coverage)**: ≥ 50 assertions verifying all endpoints, shortcodes, and crypto validation features in isolation.
- **Tier 2 (Boundary & Corner Cases)**: ≥ 35 assertions testing boundary amounts (4.999999 USDT, 5.000000 USDT), hex case insensitivity, malformed hashes, expired tokens (+1 sec), tampered HMAC signatures, and special-character filenames.
- **Tier 3 (Cross-Feature Combinations)**: ≥ 25 assertions testing pairwise interactions (Network × Token × Replay, Shortcode × R2 Mapping, Payment × Email Trigger).
- **Tier 4 (Real-World Application Scenarios)**: ≥ 10 full end-to-end user workflows (e.g., User selects BSC -> Pays 5 USDT -> Submits TxHash -> Download link generated -> Link streams PDF -> Email dispatched -> Second submission rejected as replay).
- **Total Assertions**: ≥ 120 assertions.

---

## Real-World Application Scenarios (Tier 4)
1. **Scenario 1: Happy Path BSC Purchase**: User selects BSC, submits valid 5 USDT transaction hash, receives 2-hour expiring download link, streams book PDF, receives backup email.
2. **Scenario 2: Happy Path Polygon & Arbitrum**: Validates 6-decimal token amount calculations and confirmations on Polygon and Arbitrum One.
3. **Scenario 3: Replay Attack Defense**: Re-submitting an already redeemed transaction hash is immediately rejected with 409 Conflict.
4. **Scenario 4: Underpayment Attack Rejection**: Transaction with 4.99 USDT is rejected with explicit diagnostic message and amount delta.
5. **Scenario 5: Wrong Token / Fake Contract Rejection**: Transaction transferring a spoofed USDT contract is rejected.
6. **Scenario 6: Expired Token Rejection**: Download token past the 2-hour window returns HTTP 410 Gone with support redirect.
7. **Scenario 7: Tampered Token Rejection**: Modifying the bookId in the download token payload breaks HMAC signature and returns HTTP 403 Forbidden.
8. **Scenario 8: Hugo Site Parity & Theme Integrity**: Full site build (`hugo --renderToMemory`) compiles all 420 book pages with zero errors, dark/light theme CSS rules valid, and shortcode parameters properly bound.
