# Handoff Report: Direct On-Chain EVM Payment Verification Architecture for Cloudflare Workers

**Agent**: `survey_explorer_2` (`teamwork_preview_explorer`)  
**Date**: 2026-10-10  
**Target Module**: Cloudflare Worker On-Chain Crypto Paywall (`POST /api/verify-payment`)  
**Milestone**: Survey & Architecture Design (Milestone 1 — Crypto Paywall Verification Engine)

---

## 1. Observation

### 1.1 Direct Repository and Environment Observations
- **Target Work Environment**: Cloudflare Workers (V8 JavaScript / TypeScript runtime with standard Fetch API, native `BigInt`, Web Crypto, KV, and D1 bindings).
- **Project Requirements Document**: `/Users/sotoon/personal/theminiceo/.agents/teamwork/ORIGINAL_REQUEST.md` (lines 52–100):
  > "Implement a decentralized, non-KYC crypto paywall for book downloads on the Hugo static site (`theminiceo`) using Cloudflare Workers, on-chain RPC verification for multi-chain USDT, and secure temporary Cloudflare R2 download links with email delivery."  
  > "Support low-fee EVM networks for USDT (e.g. BNB Smart Chain BEP-20, Polygon, Arbitrum). ... Transferred amount is at least the fixed price of 5 USDT."

### 1.2 Multi-Chain RPC Infrastructure & Deprecation Finding
From authoritative block explorer registries and RPC provider audits:
- **BNB Smart Chain (BSC - Chain ID 56 / `0x38`)**:
  - Official Foundation RPC: `https://bsc-dataseed.bnbchain.org`, `https://bsc-dataseed-public.bnbchain.org` (Rate limit: ~10k req / 5 min).
  - High-availability public fallbacks: `https://bsc-rpc.publicnode.com`, `https://binance.llamarpc.com`, `https://1rpc.io/bnb`.
- **Polygon PoS (Chain ID 137 / `0x89`)**:
  - **CRITICAL DISCOVERY**: `https://polygon-rpc.com` has been officially **deprecated and decommissioned** by Polygon Labs in 2026. Hardcoding this legacy endpoint results in connection failures.
  - Active high-reliability public RPC endpoints:
    - `https://polygon-bor-rpc.publicnode.com` (PublicNode, privacy-preserving)
    - `https://public.1rpc.io/matic` (1RPC relay)
    - `https://polygon.drpc.org` (dRPC decentralized endpoint)
    - `https://rpc.ankr.com/polygon` (Ankr public tier)
- **Arbitrum One (Chain ID 42161 / `0xa4b1`)**:
  - Official Nitro RPC: `https://arb1.arbitrum.io/rpc` (Offchain Labs public endpoint, unauthenticated, subject to IP rate-limiting).
  - High-availability public fallbacks: `https://arbitrum-one-rpc.publicnode.com`, `https://public.1rpc.io/arb`, `https://arbitrum.drpc.org`.

### 1.3 Canonical USDT Token Contracts & Decimals Divergence
Verbatim contract parameters confirmed via Arbiscan, PolygonScan, and BscScan:
- **BNB Smart Chain (BSC - BEP20)**:
  - Contract Address: `0x55d398326f99059ff775485246999027b3197955` (Binance-Peg BSC-USD)
  - Decimals: **18**
  - Minimum Units for 5 USDT: `5 * 10^18` = `5,000,000,000,000,000,000` (`0x4563918244f40000` / `5000000000000000000n`)
- **Polygon (PoS)**:
  - Contract Address: `0xc2132D05D31c914a87C6611C10748AEb04B58e8F` (Tether USD)
  - Decimals: **6**
  - Minimum Units for 5 USDT: `5 * 10^6` = `5,000,000` (`0x4c4b40` / `5000000n`)
- **Arbitrum One (Nitro)**:
  - Contract Address: `0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9` (Tether USD, canonical native deployment)
  - Decimals: **6**
  - Minimum Units for 5 USDT: `5 * 10^6` = `5,000,000` (`0x4c4b40` / `5000000n`)

### 1.4 EVM Event Topic & Data Format
Standard ERC-20 `Transfer` event specification:
- Solidity definition: `event Transfer(address indexed from, address indexed to, uint256 value);`
- **Topic 0**: `keccak256("Transfer(address,address,uint256)")` = `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`
- **Topic 1**: `indexed from` address, 32-byte left-zero-padded hex string (24 zeros + 40 hex chars).
- **Topic 2**: `indexed to` address, 32-byte left-zero-padded hex string (24 zeros + 40 hex chars). Address extracted via `0x` + `topic.slice(-40)`.
- **Data**: Non-indexed `uint256 value`, 32-byte hex string representing the exact raw token units.

---

## 2. Logic Chain

```
[User submits { network, txHash, bookId, email }]
                      │
                      ▼
[Pre-flight Validation & Format Check]
  ├── Regex: /^0x[0-9a-fA-F]{64}$/
  └── Network supported: bsc | polygon | arbitrum
                      │
                      ▼
[Replay Cache Pre-Check (D1 / KV)]
  ├── If txHash exists in DB -> Fail fast (409 Conflict)
                      │
                      ▼
[Query EVM RPC: eth_getTransactionReceipt(txHash)]
  ├── Timeout: 3500ms with multi-RPC fallback rotation
  ├── If receipt is null:
  │     └── Diagnostic call: eth_getTransactionByHash(txHash)
  │           ├── If pending (blockNumber null) -> Return 202 "Pending in mempool"
  │           └── If not found -> Return 400 "Transaction does not exist"
  └── If receipt.status != "0x1" -> Return 400 "Transaction reverted on-chain"
                      │
                      ▼
[Confirmations Depth Check: eth_blockNumber]
  ├── confirmations = latestBlock - receipt.blockNumber + 1
  └── If confirmations < minRequired -> Return 202 "Awaiting block confirmations"
                      │
                      ▼
[Filter & Validate Event Logs]
  ├── Scan receipt.logs for matching Transfer event:
  │     1. log.removed !== true
  │     2. log.address.toLowerCase() === canonical USDT contract
  │     3. log.topics[0] === 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
  │     4. "0x" + log.topics[2].slice(-40).toLowerCase() === STORE_WALLET.toLowerCase()
  │     5. BigInt(log.data) >= minUnits (5 USDT)
  └── If no match found -> Return specific diagnostic (fake token, wrong recipient, insufficient amount)
                      │
                      ▼
[Atomic Replay Registration (D1 INSERT)]
  ├── UNIQUE constraint on tx_hash prevents race conditions
                      │
                      ▼
[Grant Download Authorization & Issue Token]
```

### Detailed Logic Steps

1. **Precision Safety via `BigInt`**: JavaScript standard `Number` is an IEEE 754 64-bit float with `MAX_SAFE_INTEGER = 9,007,199,254,740,991` (~`9 * 10^15`). BSC BEP-20 uses 18 decimals, where 5 USDT is `5 * 10^18` (`5,000,000,000,000,000,000`). Passing 18-decimal token amounts through standard JS `Number` causes silent precision truncation. Using native V8 `BigInt(log.data)` and comparing against `BigInt(5n * (10n ** 18n))` guarantees mathematical correctness without external library overhead.

2. **Divergent Decimals Handling**: Because Polygon and Arbitrum One use 6 decimals while BSC uses 18 decimals, hardcoding a single token threshold is fatal. The verification engine must dynamically look up the token configuration by network:
   - BSC: `5n * 10n**18n` = `5_000_000_000_000_000_000n`
   - Polygon: `5n * 10n**6n` = `5_000_000n`
   - Arbitrum: `5n * 10n**6n` = `5_000_000n`

3. **Multi-Log Traversal for Aggregators & DEX Routers**: Users may pay using a smart wallet, a 1inch/Paraswap aggregator, or a token transfer helper contract. In these transactions, `receipt.to` is the router or contract address, and `receipt.logs` contains multiple events (swaps, approvals, intermediate transfers). Checking only `receipt.to` or only `receipt.logs[0]` causes false rejections. The verifier must iterate through `receipt.logs` and locate the specific log that matches the canonical USDT address, the `Transfer` signature, and the store recipient address.

4. **Replay Protection: D1 vs KV Atomicity Analysis**:
   - **Cloudflare KV**: Key-value store with global eventual consistency. A small concurrency window exists if an attacker issues two simultaneous requests from geographically distant edge nodes with the same txHash before KV writes propagate.
   - **Cloudflare D1**: Serverless SQLite database based on Cloudflare's durable storage. Executing `INSERT INTO redeemed_transactions (tx_hash, ...)` with `tx_hash TEXT PRIMARY KEY` guarantees ACID atomicity. If a concurrent duplicate attempt occurs, SQLite throws `UNIQUE constraint failed`, strictly preventing double-redemption.
   - **Architecture Recommendation**: Use Cloudflare D1 as the primary transactional ledger. If running in a zero-database environment, Cloudflare KV with key `redeemed:${network}:${txHash.toLowerCase()}` serves as a secondary option.

5. **Fault-Tolerant RPC Fallback & Request Abort**: Public RPC endpoints can experience transient 429 rate limits, network partitions, or latency spikes. Making naked `fetch` requests risks hanging the Cloudflare Worker or returning 500 errors. Every RPC call must be wrapped with an `AbortController` (timeout 3500ms) and cycle through a prioritized array of fallback RPC endpoints.

---

## 3. Caveats

1. **Reorgs & Confirmation Depths**:
   - On **Polygon PoS**, short reorganizations of 1–4 blocks have historically occurred. Requiring 10 confirmations (~20–25 seconds) provides robust safety for e-commerce checkouts.
   - On **BSC**, BEP-126 fast finality achieves deterministic finality within ~2 blocks. Requiring 3 confirmations (~9 seconds) is sufficient.
   - On **Arbitrum One**, transactions sequenced by the Nitro sequencer have soft finality in <1 second. Requiring 2 confirmations (~1–2 seconds) is sufficient for digital downloads. Waiting for L1 batch settlement (10–15 minutes) or fraud proof challenge periods (7 days) is unnecessary and harmful for UX.
2. **Fee-on-Transfer Tokens & Proxies**: Canonical USDT on BSC, Polygon, and Arbitrum One does not currently charge a fee-on-transfer. However, the `value` in `Transfer` data reflects the gross amount credited to the store wallet. Checking `value >= minUnits` accurately reflects received funds.
3. **Store Wallet Normalization**: Ethereum addresses are case-insensitive, but block explorers and wallets often display EIP-55 mixed-case checksums. The verification code must normalize both the configured `STORE_WALLET_ADDRESS` and the extracted `log.topics[2]` using `.toLowerCase()` prior to comparison.
4. **Network Outages**: If all public RPC endpoints for a specific chain go offline simultaneously, requests for that chain will return `RPC_CONNECTION_FAILURE`. Adding an optional private provider URL (e.g. Alchemy or QuickNode via Worker environment variable `ALCHEMY_KEY`) as the first tier in the array can provide 99.99% enterprise uptime.

---

## 4. Conclusion & Complete Architectural Specification

### 4.1 Master Network & USDT Configuration Matrix

| Network Key | Chain ID | Network Name | Canonical USDT Contract | Decimals | 5 USDT Atomic Units | Min Confs | Primary & Fallback RPC Endpoints |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `bsc` | `56` | BNB Smart Chain (BEP-20) | `0x55d398326f99059ff775485246999027b3197955` | 18 | `5000000000000000000` (`5*10^18`) | 3 | 1. `https://bsc-dataseed.bnbchain.org`<br>2. `https://bsc-dataseed-public.bnbchain.org`<br>3. `https://bsc-rpc.publicnode.com`<br>4. `https://binance.llamarpc.com`<br>5. `https://1rpc.io/bnb` |
| `polygon` | `137` | Polygon (PoS) | `0xc2132D05D31c914a87C6611C10748AEb04B58e8F` | 6 | `5000000` (`5*10^6`) | 10 | 1. `https://polygon-bor-rpc.publicnode.com`<br>2. `https://public.1rpc.io/matic`<br>3. `https://polygon.drpc.org`<br>4. `https://rpc.ankr.com/polygon`<br>*(Note: `polygon-rpc.com` retired)* |
| `arbitrum` | `42161` | Arbitrum One | `0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9` | 6 | `5000000` (`5*10^6`) | 2 | 1. `https://arb1.arbitrum.io/rpc`<br>2. `https://arbitrum-one-rpc.publicnode.com`<br>3. `https://public.1rpc.io/arb`<br>4. `https://arbitrum.drpc.org` |

---

### 4.2 Replay Protection Data Layer Specification

#### Option 1: Cloudflare D1 (Recommended Primary Storage)
**Schema Definition (`schema.sql`)**:
```sql
CREATE TABLE IF NOT EXISTS redeemed_transactions (
    tx_hash TEXT PRIMARY KEY,
    network TEXT NOT NULL,
    book_id TEXT NOT NULL,
    email TEXT NOT NULL,
    sender_address TEXT NOT NULL,
    amount_raw TEXT NOT NULL,
    block_number INTEGER NOT NULL,
    redeemed_at INTEGER NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_redeemed_book_email ON redeemed_transactions (book_id, email);
```

**Atomic Check-and-Insert Pattern**:
```typescript
async function recordRedemptionD1(db: D1Database, record: {
  txHash: string;
  network: string;
  bookId: string;
  email: string;
  senderAddress: string;
  amountRaw: string;
  blockNumber: number;
}): Promise<boolean> {
  try {
    await db.prepare(`
      INSERT INTO redeemed_transactions 
        (tx_hash, network, book_id, email, sender_address, amount_raw, block_number, redeemed_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      record.txHash.toLowerCase(),
      record.network,
      record.bookId,
      record.email,
      record.senderAddress.toLowerCase(),
      record.amountRaw,
      record.blockNumber,
      Date.now()
    ).run();
    return true;
  } catch (err: any) {
    if (err.message && err.message.includes("UNIQUE constraint failed")) {
      return false; // Duplicate transaction detected
    }
    throw err;
  }
}
```

#### Option 2: Cloudflare KV (Lightweight / Fallback Storage)
- **Key Namespace**: `PAYMENTS_KV`
- **Key Format**: `redeemed:${network}:${txHash.toLowerCase()}`
- **Value Schema**:
  ```json
  {
    "txHash": "0x123...abc",
    "network": "bsc",
    "bookId": "the-lean-startup",
    "email": "user@example.com",
    "senderAddress": "0x456...def",
    "amountRaw": "5000000000000000000",
    "blockNumber": 42100500,
    "redeemedAt": 1728570000000
  }
  ```
- **TTL**: No expiration or 10-year expiration (`expirationTtl: 315360000`). Mined transactions on an immutable ledger never expire.

---

### 4.3 Diagnostic Error Taxonomy & User Guidance

| Error Code | HTTP Status | Root Cause | User Feedback / Diagnostic Message |
| :--- | :---: | :--- | :--- |
| `INVALID_TX_HASH_FORMAT` | 400 | Regex mismatch (`^0x[0-9a-fA-F]{64}$`) | "Invalid transaction hash. Must be a 66-character hexadecimal string beginning with 0x." |
| `UNSUPPORTED_NETWORK` | 400 | Network param not in `bsc`, `polygon`, `arbitrum` | "Unsupported network. Please select BNB Smart Chain, Polygon, or Arbitrum One." |
| `TRANSACTION_ALREADY_REDEEMED` | 409 | TxHash exists in D1 or KV | "This transaction has already been redeemed. Each transaction hash can only be used once." |
| `TRANSACTION_NOT_FOUND` | 404 | Node returned null for receipt and tx | "Transaction not found on this network. Please ensure the transaction has been broadcast and you selected the correct network." |
| `TRANSACTION_PENDING` | 202 | Tx is in mempool (`blockNumber == null`) | "Transaction is pending in the network mempool. Please wait 15–30 seconds and click verify again." |
| `TRANSACTION_FAILED` | 400 | `receipt.status === "0x0"` | "Transaction reverted on-chain. The payment was not completed by the network." |
| `INSUFFICIENT_CONFIRMATIONS` | 202 | Current confirmations < required | "Transaction has {current}/{required} confirmations. Please wait a few seconds and try again." |
| `NO_USDT_TRANSFER_FOUND` | 400 | No Transfer event to store wallet | "No transfer of USDT to the designated store wallet was found in this transaction." |
| `INVALID_TOKEN_CONTRACT` | 400 | Transfer occurred on scam/custom token | "Transfer was executed with an unauthorized token. Only canonical USDT is accepted." |
| `WRONG_RECIPIENT` | 400 | Transfer `to` address != store wallet | "Payment was sent to a different wallet address ({actual}). Expected store address: {expected}." |
| `INSUFFICIENT_AMOUNT` | 400 | Transferred units < 5 USDT | "Payment amount is insufficient. Received {actual} USDT; required amount is 5.00 USDT." |
| `RPC_CONNECTION_FAILURE` | 503 | All fallback RPCs timed out or failed | "Unable to connect to blockchain RPC nodes at this time. Please try again in a moment." |

---

### 4.4 Reference Cloudflare Worker Implementation (TypeScript)

```typescript
// ============================================================================
// On-Chain Crypto Payment Verification Engine for Cloudflare Workers
// ============================================================================

export interface Env {
  DB: D1Database; // Cloudflare D1 Binding
  PAYMENTS_KV?: KVNamespace; // Optional KV Binding
  STORE_WALLET_ADDRESS: string; // Environment secret: e.g. "0xYourWallet..."
}

export interface VerifyPaymentRequest {
  network: "bsc" | "polygon" | "arbitrum";
  txHash: string;
  bookId: string;
  email: string;
}

export interface NetworkConfig {
  chainId: number;
  name: string;
  usdtAddress: string;
  decimals: number;
  minUnits: bigint;
  minConfirmations: number;
  rpcUrls: string[];
}

export const NETWORKS: Record<string, NetworkConfig> = {
  bsc: {
    chainId: 56,
    name: "BNB Smart Chain (BEP-20)",
    usdtAddress: "0x55d398326f99059ff775485246999027b3197955".toLowerCase(),
    decimals: 18,
    minUnits: 5_000_000_000_000_000_000n, // 5 * 10^18
    minConfirmations: 3,
    rpcUrls: [
      "https://bsc-dataseed.bnbchain.org",
      "https://bsc-dataseed-public.bnbchain.org",
      "https://bsc-rpc.publicnode.com",
      "https://binance.llamarpc.com",
      "https://1rpc.io/bnb",
    ],
  },
  polygon: {
    chainId: 137,
    name: "Polygon (PoS)",
    usdtAddress: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F".toLowerCase(),
    decimals: 6,
    minUnits: 5_000_000n, // 5 * 10^6
    minConfirmations: 10,
    rpcUrls: [
      "https://polygon-bor-rpc.publicnode.com",
      "https://public.1rpc.io/matic",
      "https://polygon.drpc.org",
      "https://rpc.ankr.com/polygon",
    ],
  },
  arbitrum: {
    chainId: 42161,
    name: "Arbitrum One",
    usdtAddress: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9".toLowerCase(),
    decimals: 6,
    minUnits: 5_000_000n, // 5 * 10^6
    minConfirmations: 2,
    rpcUrls: [
      "https://arb1.arbitrum.io/rpc",
      "https://arbitrum-one-rpc.publicnode.com",
      "https://public.1rpc.io/arb",
      "https://arbitrum.drpc.org",
    ],
  },
};

const ERC20_TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef".toLowerCase();

// Safe RPC caller with timeout and fallback array
async function callRpcWithFallback(
  rpcUrls: string[],
  method: string,
  params: any[],
  timeoutMs = 3500
): Promise<any> {
  let lastError: Error | null = null;
  for (const url of rpcUrls) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jsonrpc: "2.0",
          method,
          params,
          id: 1,
        }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data: any = await res.json();
      if (data.error) {
        throw new Error(data.error.message || "RPC Error");
      }
      return data.result;
    } catch (err: any) {
      lastError = err;
    }
  }
  throw new Error(`All RPC endpoints failed: ${lastError?.message}`);
}

export async function verifyPayment(
  req: VerifyPaymentRequest,
  env: Env
): Promise<{ success: boolean; status: number; data?: any; error?: string; message?: string }> {
  const txHash = req.txHash.toLowerCase().trim();
  const networkKey = req.network.toLowerCase().trim();

  // 1. Format Validation
  if (!/^0x[0-9a-f]{64}$/.test(txHash)) {
    return {
      success: false,
      status: 400,
      error: "INVALID_TX_HASH_FORMAT",
      message: "Invalid transaction hash format. Expected 66-character hex string starting with 0x.",
    };
  }

  const networkConfig = NETWORKS[networkKey];
  if (!networkConfig) {
    return {
      success: false,
      status: 400,
      error: "UNSUPPORTED_NETWORK",
      message: "Unsupported blockchain network selected.",
    };
  }

  const storeWallet = env.STORE_WALLET_ADDRESS?.toLowerCase().trim();
  if (!storeWallet || !/^0x[0-9a-f]{40}$/.test(storeWallet)) {
    return {
      success: false,
      status: 500,
      error: "STORE_WALLET_MISCONFIGURED",
      message: "Server store wallet is not properly configured.",
    };
  }

  // 2. Pre-flight Replay Check (D1)
  if (env.DB) {
    const existing = await env.DB.prepare(
      "SELECT tx_hash FROM redeemed_transactions WHERE tx_hash = ?"
    ).bind(txHash).first();
    if (existing) {
      return {
        success: false,
        status: 409,
        error: "TRANSACTION_ALREADY_REDEEMED",
        message: "This transaction has already been redeemed for a download.",
      };
    }
  }

  // 3. Query Transaction Receipt
  let receipt: any = null;
  try {
    receipt = await callRpcWithFallback(networkConfig.rpcUrls, "eth_getTransactionReceipt", [txHash]);
  } catch (err: any) {
    return {
      success: false,
      status: 503,
      error: "RPC_CONNECTION_FAILURE",
      message: "Unable to reach blockchain nodes. Please retry shortly.",
    };
  }

  // 4. Handle Pending or Missing Transaction
  if (!receipt) {
    try {
      const tx = await callRpcWithFallback(networkConfig.rpcUrls, "eth_getTransactionByHash", [txHash]);
      if (tx && tx.blockNumber === null) {
        return {
          success: false,
          status: 202,
          error: "TRANSACTION_PENDING",
          message: "Transaction is currently pending in the network mempool. Please wait 15-30 seconds.",
        };
      }
    } catch {}
    return {
      success: false,
      status: 404,
      error: "TRANSACTION_NOT_FOUND",
      message: "Transaction not found on this network. Please verify your TxHash and selected network.",
    };
  }

  // 5. Verify Execution Status
  if (receipt.status !== "0x1") {
    return {
      success: false,
      status: 400,
      error: "TRANSACTION_FAILED",
      message: "Transaction reverted or failed on-chain. No payment was transferred.",
    };
  }

  // 6. Confirmations Check
  const receiptBlock = BigInt(receipt.blockNumber);
  let latestBlockHex = "0x0";
  try {
    latestBlockHex = await callRpcWithFallback(networkConfig.rpcUrls, "eth_blockNumber", []);
  } catch {}
  const latestBlock = BigInt(latestBlockHex);
  const confirmations = latestBlock >= receiptBlock ? (latestBlock - receiptBlock + 1n) : 0n;

  if (confirmations < BigInt(networkConfig.minConfirmations)) {
    return {
      success: false,
      status: 202,
      error: "INSUFFICIENT_CONFIRMATIONS",
      message: `Transaction has ${confirmations}/${networkConfig.minConfirmations} confirmations. Please wait a few seconds.`,
    };
  }

  // 7. Parse & Filter ERC-20 Transfer Logs
  const logs = receipt.logs || [];
  let validLog: any = null;
  let detectedWrongRecipient = false;
  let detectedInsufficientAmount = false;
  let foundAmount = 0n;

  for (const log of logs) {
    if (log.removed === true) continue;
    if (log.address.toLowerCase() !== networkConfig.usdtAddress) continue;
    if (!Array.isArray(log.topics) || log.topics.length < 3) continue;
    if (log.topics[0].toLowerCase() !== ERC20_TRANSFER_TOPIC) continue;

    const recipient = ("0x" + log.topics[2].slice(-40)).toLowerCase();
    if (recipient !== storeWallet) {
      detectedWrongRecipient = true;
      continue;
    }

    const value = BigInt(log.data);
    foundAmount = value;
    if (value < networkConfig.minUnits) {
      detectedInsufficientAmount = true;
      continue;
    }

    validLog = log;
    break;
  }

  if (!validLog) {
    if (detectedInsufficientAmount) {
      const divisor = 10n ** BigInt(networkConfig.decimals);
      const whole = foundAmount / divisor;
      const frac = (foundAmount % divisor).toString().padStart(networkConfig.decimals, "0").slice(0, 2);
      return {
        success: false,
        status: 400,
        error: "INSUFFICIENT_AMOUNT",
        message: `Transferred amount (${whole}.${frac} USDT) is less than required 5.00 USDT.`,
      };
    }
    if (detectedWrongRecipient) {
      return {
        success: false,
        status: 400,
        error: "WRONG_RECIPIENT",
        message: "USDT was sent to a different address than the store wallet.",
      };
    }
    return {
      success: false,
      status: 400,
      error: "NO_USDT_TRANSFER_FOUND",
      message: "No legitimate USDT transfer to the store wallet was found in this transaction.",
    };
  }

  const senderAddress = ("0x" + validLog.topics[1].slice(-40)).toLowerCase();
  const transferredAmount = BigInt(validLog.data).toString();

  // 8. Atomic Replay Registration in D1
  if (env.DB) {
    try {
      await env.DB.prepare(`
        INSERT INTO redeemed_transactions
          (tx_hash, network, book_id, email, sender_address, amount_raw, block_number, redeemed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `).bind(
        txHash,
        networkKey,
        req.bookId,
        req.email,
        senderAddress,
        transferredAmount,
        Number(receiptBlock),
        Date.now()
      ).run();
    } catch (err: any) {
      if (err.message && err.message.includes("UNIQUE constraint failed")) {
        return {
          success: false,
          status: 409,
          error: "TRANSACTION_ALREADY_REDEEMED",
          message: "This transaction has already been redeemed.",
        };
      }
      throw err;
    }
  }

  // 9. Payment Successfully Verified
  return {
    success: true,
    status: 200,
    data: {
      txHash,
      network: networkKey,
      senderAddress,
      amountRaw: transferredAmount,
      blockNumber: Number(receiptBlock),
      confirmations: Number(confirmations),
      verifiedAt: Date.now(),
    },
  };
}
```

---

## 5. Verification Method

To independently verify the architecture and specifications outlined in this report:

1. **Verify Canonical Contract Addresses & Decimals on Explorers**:
   - BSC-USD on BscScan: `https://bscscan.com/token/0x55d398326f99059ff775485246999027b3197955` (Inspect Contract Tab: Decimals = 18).
   - Tether USD on PolygonScan: `https://polygonscan.com/token/0xc2132D05D31c914a87C6611C10748AEb04B58e8F` (Inspect Contract Tab: Decimals = 6).
   - Tether USD on Arbiscan: `https://arbiscan.io/token/0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9` (Inspect Contract Tab: Decimals = 6).

2. **Verify Public RPC Endpoints**:
   - BSC: Execute `curl -X POST https://bsc-dataseed.bnbchain.org -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'` -> Returns latest hex block number.
   - Polygon: Execute `curl -X POST https://polygon-bor-rpc.publicnode.com -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'` -> Returns latest hex block number.
   - Arbitrum: Execute `curl -X POST https://arb1.arbitrum.io/rpc -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'` -> Returns latest hex block number.

3. **Verify Event Topic0 Calculation**:
   - In Node.js or browser console:
     ```javascript
     const keccak256 = require("ethers").id; // or viem keccak256(toHex("Transfer(address,address,uint256)"))
     console.log(keccak256("Transfer(address,address,uint256)"));
     // Expected: 0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef
     ```

4. **Verify Decimal Math Safety**:
   - In Node.js / V8 console:
     ```javascript
     const bsc5Usdt = 5n * (10n ** 18n); // 5000000000000000000n (exact BigInt)
     const polygon5Usdt = 5n * (10n ** 6n); // 5000000n (exact BigInt)
     console.assert(bsc5Usdt.toString(16) === "4563918244f40000");
     console.assert(polygon5Usdt.toString(16) === "4c4b40");
     ```

5. **Invalidation Conditions**:
   - If Tether changes the canonical USDT contract address on any of the three networks (e.g. migrating to a new token contract).
   - If Cloudflare D1 pricing or deployment constraints mandate a purely KV-only implementation (in which case the secondary KV schema provided in Section 4.2 must be utilized).
