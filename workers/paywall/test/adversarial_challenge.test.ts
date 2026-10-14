import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { handleRequest, type Env } from "../src/index.js";
import {
  DEFAULT_STORE_WALLET,
  DEFAULT_USDT_PRICE,
  ERC20_TRANSFER_TOPIC,
  NETWORKS,
  isValidTxHash,
  formatUsdtAmount,
} from "../src/config.js";
import { verifyPaymentOnChain, DIAGNOSTIC_ERRORS } from "../src/verifier.js";
import { recordRedemption, isTransactionRedeemed } from "../src/replay.js";
import type { EvmRpcClient } from "../src/rpc.js";

// Minimal thread-safe mock D1 for concurrency & ACID testing
function createMockD1(): D1Database {
  const store = new Map<string, any[]>();
  return {
    prepare(query: string) {
      let boundParams: any[] = [];
      return {
        bind(...params: any[]) {
          boundParams = params;
          return this;
        },
        async first() {
          if (query.includes("SELECT")) {
            const key = String(boundParams[0]).toLowerCase();
            return store.get(key) ? { tx_hash: key } : null;
          }
          return null;
        },
        async run() {
          if (query.includes("INSERT")) {
            const key = String(boundParams[0]).toLowerCase();
            if (store.has(key)) {
              throw new Error("UNIQUE constraint failed: redeemed_transactions.tx_hash");
            }
            store.set(key, boundParams);
            return { success: true };
          }
          return { success: true };
        },
      } as unknown as D1PreparedStatement;
    },
  } as unknown as D1Database;
}

function topicAddress(address: string): string {
  const clean = address.toLowerCase().replace(/^0x/, "");
  return "0x" + clean.padStart(64, "0");
}

function dataValue(value: bigint): string {
  return "0x" + value.toString(16).padStart(64, "0");
}

function buildMockRpcClient(receiptConfig: {
  txHash: string;
  network: "bsc" | "polygon" | "arbitrum";
  tokenAddress?: string;
  recipientAddress?: string;
  senderAddress?: string;
  rawAmount: bigint;
  status?: string;
  receiptBlock?: number;
  latestBlock?: number;
  extraLogs?: any[];
}): EvmRpcClient {
  const net = NETWORKS[receiptConfig.network];
  const token = (receiptConfig.tokenAddress || net.usdtContract).toLowerCase();
  const recipient = (receiptConfig.recipientAddress || DEFAULT_STORE_WALLET).toLowerCase();
  const sender = (receiptConfig.senderAddress || "0x1111111111111111111111111111111111111111").toLowerCase();
  const status = receiptConfig.status ?? "0x1";
  const rBlock = receiptConfig.receiptBlock ?? 5000;
  const lBlock = receiptConfig.latestBlock ?? (rBlock + net.minConfirmations + 5);

  const transferLog = {
    address: token,
    topics: [
      ERC20_TRANSFER_TOPIC,
      topicAddress(sender),
      topicAddress(recipient),
    ],
    data: dataValue(receiptConfig.rawAmount),
  };

  const logs = receiptConfig.extraLogs
    ? [...receiptConfig.extraLogs, transferLog]
    : [transferLog];

  return {
    async eth_getTransactionReceipt(hash: string) {
      if (hash.toLowerCase() !== receiptConfig.txHash.toLowerCase()) return null;
      return {
        transactionHash: receiptConfig.txHash,
        blockNumber: "0x" + rBlock.toString(16),
        status,
        logs,
      };
    },
    async eth_getTransactionByHash(hash: string) {
      return {
        hash,
        blockNumber: "0x" + rBlock.toString(16),
      };
    },
    async eth_blockNumber() {
      return BigInt(lBlock);
    },
  } as unknown as EvmRpcClient;
}

// ============================================================================
// SUITE 1: ADVERSARIAL MALFORMED TRANSACTION HASHES
// ============================================================================
describe("Adversarial Stress Test: Malformed Transaction Hashes", () => {
  const malformedStringTxHashes: Array<{ label: string; value: string }> = [
    // Length violations
    { label: "Empty string", value: "" },
    { label: "Whitespace only", value: "    " },
    { label: "Only prefix '0x' (len 2)", value: "0x" },
    { label: "Prefix plus 1 char (len 3)", value: "0xa" },
    { label: "Short length 10", value: "0x12345678" },
    { label: "Short length 63 total", value: "0x" + "a".repeat(61) },
    { label: "Short length 64 total", value: "0x" + "a".repeat(62) },
    { label: "Short length 65 total (1 char short)", value: "0x" + "a".repeat(63) },
    { label: "Overlong length 67 total (1 char too long)", value: "0x" + "a".repeat(65) },
    { label: "Overlong length 70", value: "0x" + "a".repeat(68) },
    { label: "Overlong length 128", value: "0x" + "a".repeat(126) },
    { label: "Huge length 1024", value: "0x" + "a".repeat(1022) },

    // Missing 0x prefix
    { label: "64 hex chars missing 0x prefix", value: "a".repeat(64) },
    { label: "Uppercase 0X prefix", value: "0X" + "a".repeat(64) },
    { label: "Prefix 'x' instead of '0x'", value: "x" + "a".repeat(64) },
    { label: "Prefix '#x' instead of '0x'", value: "#x" + "a".repeat(64) },
    { label: "Prefix '0 ' instead of '0x'", value: "0 " + "a".repeat(64) },

    // Non-hex characters
    { label: "Character 'g' at position 0", value: "0x" + "g" + "a".repeat(63) },
    { label: "Character 'z' at middle position", value: "0x" + "a".repeat(31) + "z" + "a".repeat(32) },
    { label: "Character 'q' at final position", value: "0x" + "a".repeat(63) + "q" },
    { label: "Internal space character", value: "0x" + "a".repeat(31) + " " + "a".repeat(32) },
    { label: "Internal tab character", value: "0x" + "a".repeat(31) + "\t" + "a".repeat(32) },
    { label: "Internal newline character", value: "0x" + "a".repeat(31) + "\n" + "a".repeat(32) },
    { label: "Internal null byte character", value: "0x" + "a".repeat(31) + "\0" + "a".repeat(32) },
    { label: "Internal hyphen", value: "0x" + "a".repeat(31) + "-" + "a".repeat(32) },
    { label: "Internal period", value: "0x" + "a".repeat(31) + "." + "a".repeat(32) },

    // Injection & Exploit Payloads
    { label: "SQL Injection payload", value: "0x' OR '1'='1" },
    { label: "SQL Drop Table injection", value: "0x'; DROP TABLE redeemed_transactions; --" },
    { label: "XSS script payload", value: "<script>alert('xss')</script>" },
    { label: "Prefixed XSS script payload", value: "0x<script>alert('xss')</script>" },
    { label: "Path traversal payload", value: "0x../../../../etc/passwd" },
    { label: "Emoji unicode payload", value: "0x" + "🔥".repeat(32) },
  ];

  test("isValidTxHash unit oracle rejects all malformed string hashes", () => {
    for (const { label, value } of malformedStringTxHashes) {
      assert.equal(
        isValidTxHash(value),
        false,
        `Expected isValidTxHash to reject: ${label} (${value})`
      );
    }
  });

  test("isValidTxHash accepts strictly valid hashes with upper, lower, and mixed case", () => {
    const validLower = "0x" + "a".repeat(64);
    const validUpper = "0x" + "A".repeat(64);
    const validMixed = "0x" + "0123456789abcdefABCDEF".repeat(2) + "0123456789abcdefABCDEF".slice(0, 20); // 22 + 22 + 20 = 64
    assert.equal(validMixed.length, 66, "validMixed must have length 66");

    const validWithWhitespace = "   0x" + "b".repeat(64) + "   ";

    assert.equal(isValidTxHash(validLower), true, "Valid lowercase hash");
    assert.equal(isValidTxHash(validUpper), true, "Valid uppercase hash");
    assert.equal(isValidTxHash(validMixed), true, "Valid mixed case hash");
    assert.equal(isValidTxHash(validWithWhitespace), true, "Valid hash with surrounding whitespace");
  });

  test("verifyPaymentOnChain rejects all malformed string hashes with status 400 and INVALID_TX_HASH_FORMAT", async () => {
    for (const { label, value } of malformedStringTxHashes) {
      const res = await verifyPaymentOnChain(
        { network: "bsc", txHash: value },
        {}
      );
      assert.equal(res.success, false, `Must fail for: ${label}`);
      assert.equal(res.status, 400, `Status must be 400 for: ${label}`);
      assert.equal(
        res.error,
        DIAGNOSTIC_ERRORS.INVALID_TX_HASH_FORMAT.code,
        `Error code must be INVALID_TX_HASH_FORMAT for: ${label}`
      );
      assert.ok(res.message.includes("Must be a 66-character"), `Informative message for: ${label}`);
    }
  });

  test("HTTP POST /api/verify-payment rejects all malformed string hashes with 400 Bad Request", async () => {
    const env: Env = {
      STORE_WALLET_ADDRESS: DEFAULT_STORE_WALLET,
      USDT_PRICE: DEFAULT_USDT_PRICE,
      DOWNLOAD_HMAC_SECRET: "test-secret-12345",
      BASE_URL: "https://theminiceo.ir",
      DB: createMockD1(),
    };

    for (const { label, value } of malformedStringTxHashes) {
      const req = new Request("https://theminiceo.ir/api/verify-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          network: "bsc",
          txHash: value,
          bookId: "the-lean-startup",
          email: "victim@example.com",
        }),
      });

      const res = await handleRequest(req, env);
      assert.equal(res.status, 400, `HTTP status must be 400 for: ${label}`);
      const json = (await res.json()) as any;
      assert.equal(json.success, false, `JSON success must be false for: ${label}`);
      assert.equal(json.error, "INVALID_TX_HASH_FORMAT", `Error code must match for: ${label}`);
    }
  });

  test("Type confusion hardened: non-string txHash (number, object, boolean) safely returns 400 instead of crashing", async () => {
    const env: Env = {
      STORE_WALLET_ADDRESS: DEFAULT_STORE_WALLET,
      USDT_PRICE: DEFAULT_USDT_PRICE,
      DOWNLOAD_HMAC_SECRET: "test-secret-12345",
      BASE_URL: "https://theminiceo.ir",
      DB: createMockD1(),
    };

    const typeConfusionPayloads = [
      { label: "Number type", value: 123456789 },
      { label: "Object type", value: { malicious: "object" } },
      { label: "Boolean true", value: true },
    ];

    for (const { label, value } of typeConfusionPayloads) {
      const req = new Request("https://theminiceo.ir/api/verify-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          network: "bsc",
          txHash: value,
          bookId: "the-lean-startup",
          email: "attacker@example.com",
        }),
      });

      const res = await handleRequest(req, env);
      assert.equal(res.status, 400, `Must safely return 400 for ${label}`);
      const json = (await res.json()) as any;
      assert.equal(json.success, false);
      assert.equal(json.error, "INVALID_TX_HASH_FORMAT");
    }
  });
});

// ============================================================================
// SUITE 2: CRITICAL BOUNDARY AMOUNTS (BSC 18 DEC, POLYGON 6 DEC, ARBITRUM 6 DEC)
// ============================================================================
describe("Adversarial Stress Test: Critical Boundary Amounts & Decimal Math", () => {
  // --- BSC (18 Decimals) Tests ---
  describe("BNB Smart Chain (18 Decimals, Min Units: 5 * 10^18)", () => {
    const net = "bsc";
    const minUnits = 5000000000000000000n; // 5.00 USDT

    test("Underpayment by 1 wei (4.999999999999999999 USDT) is strictly rejected with 400 INSUFFICIENT_AMOUNT", async () => {
      const txHash = "0x" + "10".repeat(32);
      const underByOneWei = minUnits - 1n; // 4999999999999999999n

      const mockRpc = buildMockRpcClient({
        txHash,
        network: net,
        rawAmount: underByOneWei,
      });

      const res = await verifyPaymentOnChain(
        { network: net, txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.code);
      assert.ok(res.message.includes("4.99 USDT"), `Expected 4.99 formatted string, got: ${res.message}`);
    });

    test("Underpayment 4.990000000000000000 USDT is strictly rejected", async () => {
      const txHash = "0x" + "11".repeat(32);
      const amount499 = 4990000000000000000n;

      const mockRpc = buildMockRpcClient({
        txHash,
        network: net,
        rawAmount: amount499,
      });

      const res = await verifyPaymentOnChain(
        { network: net, txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.code);
    });

    test("Underpayment 0 wei and 1 wei are strictly rejected", async () => {
      for (const rawAmount of [0n, 1n, 1000000000n]) {
        const txHash = "0x" + "12".repeat(32);
        const mockRpc = buildMockRpcClient({
          txHash,
          network: net,
          rawAmount,
        });

        const res = await verifyPaymentOnChain(
          { network: net, txHash },
          {},
          { customRpcClient: mockRpc }
        );

        assert.equal(res.success, false);
        assert.equal(res.status, 400);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.code);
      }
    });

    test("Exact boundary 5.000000000000000000 USDT (5000000000000000000n) succeeds with 200 OK", async () => {
      const txHash = "0x" + "13".repeat(32);
      const mockRpc = buildMockRpcClient({
        txHash,
        network: net,
        rawAmount: minUnits,
      });

      const res = await verifyPaymentOnChain(
        { network: net, txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, true);
      assert.equal(res.status, 200);
      assert.equal(res.data?.amountUsdt, "5.00");
      assert.equal(res.data?.amountRaw, minUnits.toString());
    });

    test("Overpayment by 1 wei (5000000000000000001n) and massive overpayment succeed", async () => {
      const txHash1 = "0x" + "14".repeat(32);
      const overByOneWei = minUnits + 1n;

      const mockRpc1 = buildMockRpcClient({
        txHash: txHash1,
        network: net,
        rawAmount: overByOneWei,
      });

      const res1 = await verifyPaymentOnChain(
        { network: net, txHash: txHash1 },
        {},
        { customRpcClient: mockRpc1 }
      );

      assert.equal(res1.success, true);
      assert.equal(res1.status, 200);
      assert.equal(res1.data?.amountUsdt, "5.00");

      const txHash2 = "0x" + "15".repeat(32);
      const massiveOverpayment = 5000000000000000000000n; // 5000 USDT
      const mockRpc2 = buildMockRpcClient({
        txHash: txHash2,
        network: net,
        rawAmount: massiveOverpayment,
      });

      const res2 = await verifyPaymentOnChain(
        { network: net, txHash: txHash2 },
        {},
        { customRpcClient: mockRpc2 }
      );

      assert.equal(res2.success, true);
      assert.equal(res2.status, 200);
      assert.equal(res2.data?.amountUsdt, "5000.00");
    });
  });

  // --- Polygon (6 Decimals) Tests ---
  describe("Polygon PoS (6 Decimals, Min Units: 5 * 10^6 = 5000000n)", () => {
    const net = "polygon";
    const minUnits = 5000000n; // 5.00 USDT

    test("Underpayment by 1 unit (4.999999 USDT / 4999999n) is strictly rejected with 400 INSUFFICIENT_AMOUNT", async () => {
      const txHash = "0x" + "20".repeat(32);
      const underByOneUnit = minUnits - 1n; // 4999999n

      const mockRpc = buildMockRpcClient({
        txHash,
        network: net,
        rawAmount: underByOneUnit,
      });

      const res = await verifyPaymentOnChain(
        { network: net, txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.code);
      assert.ok(res.message.includes("4.99 USDT"), `Expected 4.99 formatted string, got: ${res.message}`);
    });

    test("Underpayment 4.990000 USDT (4990000n) is strictly rejected", async () => {
      const txHash = "0x" + "21".repeat(32);
      const amount499 = 4990000n;

      const mockRpc = buildMockRpcClient({
        txHash,
        network: net,
        rawAmount: amount499,
      });

      const res = await verifyPaymentOnChain(
        { network: net, txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.code);
    });

    test("Exact boundary 5.000000 USDT (5000000n) succeeds with 200 OK", async () => {
      const txHash = "0x" + "22".repeat(32);
      const mockRpc = buildMockRpcClient({
        txHash,
        network: net,
        rawAmount: minUnits,
      });

      const res = await verifyPaymentOnChain(
        { network: net, txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, true);
      assert.equal(res.status, 200);
      assert.equal(res.data?.amountUsdt, "5.00");
      assert.equal(res.data?.amountRaw, "5000000");
    });

    test("Overpayment by 1 unit (5.000001 USDT / 5000001n) succeeds with 200 OK", async () => {
      const txHash = "0x" + "23".repeat(32);
      const mockRpc = buildMockRpcClient({
        txHash,
        network: net,
        rawAmount: 5000001n,
      });

      const res = await verifyPaymentOnChain(
        { network: net, txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, true);
      assert.equal(res.status, 200);
      assert.equal(res.data?.amountUsdt, "5.00");
    });
  });

  // --- Arbitrum One (6 Decimals) Tests ---
  describe("Arbitrum One (6 Decimals, Min Units: 5 * 10^6 = 5000000n)", () => {
    const net = "arbitrum";
    const minUnits = 5000000n;

    test("Underpayment by 1 unit (4.999999 USDT / 4999999n) is strictly rejected", async () => {
      const txHash = "0x" + "30".repeat(32);
      const mockRpc = buildMockRpcClient({
        txHash,
        network: net,
        rawAmount: minUnits - 1n,
      });

      const res = await verifyPaymentOnChain(
        { network: net, txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.code);
    });

    test("Exact boundary 5.000000 USDT (5000000n) succeeds with 200 OK", async () => {
      const txHash = "0x" + "31".repeat(32);
      const mockRpc = buildMockRpcClient({
        txHash,
        network: net,
        rawAmount: minUnits,
      });

      const res = await verifyPaymentOnChain(
        { network: net, txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, true);
      assert.equal(res.status, 200);
      assert.equal(res.data?.amountUsdt, "5.00");
    });
  });

  // --- Cross-Chain Decimal Spoofing Attack ---
  describe("Cross-Chain Decimal Confusion Attack", () => {
    test("Attacker transfers 5000000n on BSC (expecting 6 decimal treatment): strictly rejected on BSC", async () => {
      const txHash = "0x" + "40".repeat(32);
      // 5000000n on BSC is 0.000000000005 USDT!
      const mockRpc = buildMockRpcClient({
        txHash,
        network: "bsc",
        rawAmount: 5000000n,
      });

      const res = await verifyPaymentOnChain(
        { network: "bsc", txHash },
        {},
        { customRpcClient: mockRpc }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.code);
      assert.ok(res.message.includes("0.00 USDT"));
    });
  });

  // --- Decimal Formatting Oracle Tests ---
  describe("formatUsdtAmount Decimal Arithmetic Oracle", () => {
    test("BSC 18 decimals formatting precision", () => {
      assert.equal(formatUsdtAmount(4999999999999999999n, 18), "4.99");
      assert.equal(formatUsdtAmount(5000000000000000000n, 18), "5.00");
      assert.equal(formatUsdtAmount(5050000000000000000n, 18), "5.05");
      assert.equal(formatUsdtAmount(12345678901234567890n, 18), "12.34");
    });

    test("Polygon/Arbitrum 6 decimals formatting precision", () => {
      assert.equal(formatUsdtAmount(4999999n, 6), "4.99");
      assert.equal(formatUsdtAmount(5000000n, 6), "5.00");
      assert.equal(formatUsdtAmount(5050000n, 6), "5.05");
      assert.equal(formatUsdtAmount(12345678n, 6), "12.34");
    });
  });
});

// ============================================================================
// SUITE 3: REPLAY ATTACK DEFENSE & CONCURRENCY STRESS
// ============================================================================
describe("Adversarial Stress Test: Replay Attack Defense & Double-Spending", () => {
  const storeWallet = DEFAULT_STORE_WALLET;

  test("Sequential replay: second submission strictly rejected with HTTP 409 Conflict", async () => {
    const txHash = "0x" + "50".repeat(32);
    const mockRpc = buildMockRpcClient({
      txHash,
      network: "bsc",
      rawAmount: 5000000000000000000n,
    });

    const env: Env = {
      STORE_WALLET_ADDRESS: storeWallet,
      USDT_PRICE: "5.00",
      DOWNLOAD_HMAC_SECRET: "test-secret-replay",
      BASE_URL: "https://theminiceo.ir",
      DB: createMockD1(),
      CUSTOM_RPC_CLIENT: mockRpc,
    };

    // 1st submission
    const req1 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "bsc",
        txHash,
        bookId: "the-lean-startup",
        email: "alice@example.com",
      }),
    });
    const res1 = await handleRequest(req1, env);
    assert.equal(res1.status, 200, "1st submission must succeed");
    const json1 = (await res1.json()) as any;
    assert.equal(json1.success, true);
    assert.ok(json1.downloadUrl);

    // 2nd submission (Replay)
    const req2 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "bsc",
        txHash,
        bookId: "the-lean-startup",
        email: "alice@example.com",
      }),
    });
    const res2 = await handleRequest(req2, env);
    assert.equal(res2.status, 409, "2nd submission must return 409 Conflict");
    const json2 = (await res2.json()) as any;
    assert.equal(json2.success, false);
    assert.equal(json2.error, "TRANSACTION_ALREADY_REDEEMED");

    // 3rd submission (Replay)
    const req3 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "bsc",
        txHash,
        bookId: "the-lean-startup",
        email: "alice@example.com",
      }),
    });
    const res3 = await handleRequest(req3, env);
    assert.equal(res3.status, 409, "3rd submission must return 409 Conflict");
  });

  test("Case-variant replay: uppercase vs lowercase variant strictly rejected with 409", async () => {
    const rawLower = "0x" + "a1b2c3d4e5f6".repeat(5) + "a1b2";
    const rawUpper = "0x" + "A1B2C3D4E5F6".repeat(5) + "A1B2";

    const mockRpc = buildMockRpcClient({
      txHash: rawLower,
      network: "polygon",
      rawAmount: 5000000n,
    });

    const env: Env = {
      STORE_WALLET_ADDRESS: storeWallet,
      USDT_PRICE: "5.00",
      DOWNLOAD_HMAC_SECRET: "test-secret-replay",
      BASE_URL: "https://theminiceo.ir",
      DB: createMockD1(),
      CUSTOM_RPC_CLIENT: mockRpc,
    };

    // First submission: uppercase
    const req1 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "polygon",
        txHash: rawUpper,
        bookId: "inspired",
        email: "alice@example.com",
      }),
    });
    const res1 = await handleRequest(req1, env);
    assert.equal(res1.status, 200);

    // Second submission: lowercase
    const req2 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "polygon",
        txHash: rawLower,
        bookId: "inspired",
        email: "alice@example.com",
      }),
    });
    const res2 = await handleRequest(req2, env);
    assert.equal(res2.status, 409, "Case variant must trigger 409 Conflict");
    const json2 = (await res2.json()) as any;
    assert.equal(json2.error, "TRANSACTION_ALREADY_REDEEMED");
  });

  test("Cross-book replay attack: using same txHash to unlock different book is strictly rejected with 409", async () => {
    const txHash = "0x" + "52".repeat(32);
    const mockRpc = buildMockRpcClient({
      txHash,
      network: "arbitrum",
      rawAmount: 5000000n,
    });

    const env: Env = {
      STORE_WALLET_ADDRESS: storeWallet,
      USDT_PRICE: "5.00",
      DOWNLOAD_HMAC_SECRET: "test-secret-replay",
      BASE_URL: "https://theminiceo.ir",
      DB: createMockD1(),
      CUSTOM_RPC_CLIENT: mockRpc,
    };

    // Purchase book 1
    const req1 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "arbitrum",
        txHash,
        bookId: "the-lean-startup",
        email: "alice@example.com",
      }),
    });
    const res1 = await handleRequest(req1, env);
    assert.equal(res1.status, 200);

    // Try to unlock book 2 with same txHash
    const req2 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "arbitrum",
        txHash,
        bookId: "zero-to-one",
        email: "alice@example.com",
      }),
    });
    const res2 = await handleRequest(req2, env);
    assert.equal(res2.status, 409, "Cross-book replay must be rejected with 409");
    const json2 = (await res2.json()) as any;
    assert.equal(json2.error, "TRANSACTION_ALREADY_REDEEMED");
  });

  test("Cross-email replay attack: using same txHash with different email is strictly rejected with 409", async () => {
    const txHash = "0x" + "53".repeat(32);
    const mockRpc = buildMockRpcClient({
      txHash,
      network: "bsc",
      rawAmount: 5000000000000000000n,
    });

    const env: Env = {
      STORE_WALLET_ADDRESS: storeWallet,
      USDT_PRICE: "5.00",
      DOWNLOAD_HMAC_SECRET: "test-secret-replay",
      BASE_URL: "https://theminiceo.ir",
      DB: createMockD1(),
      CUSTOM_RPC_CLIENT: mockRpc,
    };

    const req1 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "bsc",
        txHash,
        bookId: "the-lean-startup",
        email: "alice@example.com",
      }),
    });
    const res1 = await handleRequest(req1, env);
    assert.equal(res1.status, 200);

    const req2 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "bsc",
        txHash,
        bookId: "the-lean-startup",
        email: "attacker@evil.com",
      }),
    });
    const res2 = await handleRequest(req2, env);
    assert.equal(res2.status, 409, "Cross-email replay must be rejected with 409");
  });

  test("Concurrent double-spending race condition: 25 simultaneous requests yield exactly 1 success and 24 409 conflicts", async () => {
    const txHash = "0x" + "54".repeat(32);
    const mockRpc = buildMockRpcClient({
      txHash,
      network: "bsc",
      rawAmount: 5000000000000000000n,
    });

    const env: Env = {
      STORE_WALLET_ADDRESS: storeWallet,
      USDT_PRICE: "5.00",
      DOWNLOAD_HMAC_SECRET: "test-secret-race",
      BASE_URL: "https://theminiceo.ir",
      DB: createMockD1(),
      CUSTOM_RPC_CLIENT: mockRpc,
    };

    const CONCURRENT_REQUESTS = 25;
    const requests = Array.from({ length: CONCURRENT_REQUESTS }, (_, idx) =>
      new Request("https://theminiceo.ir/api/verify-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          network: "bsc",
          txHash,
          bookId: "the-lean-startup",
          email: `concurrent_user_${idx}@example.com`,
        }),
      })
    );

    // Launch all 25 requests simultaneously
    const responses = await Promise.all(requests.map((r) => handleRequest(r, env)));
    const statuses = responses.map((r) => r.status);

    const successCount = statuses.filter((s) => s === 200).length;
    const conflictCount = statuses.filter((s) => s === 409).length;

    assert.equal(
      successCount,
      1,
      `Exactly 1 request must succeed with 200 OK. Got: ${successCount}`
    );
    assert.equal(
      conflictCount,
      CONCURRENT_REQUESTS - 1,
      `All other ${CONCURRENT_REQUESTS - 1} requests must fail with 409 Conflict. Got: ${conflictCount}`
    );
  });
});

// ============================================================================
// SUITE 4: ADVERSARIAL TRANSACTION RECEIPT & SMART CONTRACT ATTACKS
// ============================================================================
describe("Adversarial Stress Test: Receipt & Contract Manipulation Attacks", () => {
  const storeWallet = DEFAULT_STORE_WALLET.toLowerCase();
  const legitimateBscUsdt = NETWORKS.bsc.usdtContract;

  test("Fake Token Contract Attack: attacker creates rogue token and sends 5 tokens to store wallet -> rejected with 400 INVALID_TOKEN_CONTRACT", async () => {
    const txHash = "0x" + "60".repeat(32);
    const fakeTokenAddress = "0x9999999999999999999999999999999999999999";

    const mockRpc = buildMockRpcClient({
      txHash,
      network: "bsc",
      tokenAddress: fakeTokenAddress,
      recipientAddress: storeWallet,
      rawAmount: 5000000000000000000n,
    });

    const res = await verifyPaymentOnChain(
      { network: "bsc", txHash },
      {},
      { customRpcClient: mockRpc }
    );

    assert.equal(res.success, false);
    assert.equal(res.status, 400);
    assert.equal(res.error, DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.code);
    assert.ok(res.message.includes("Only canonical USDT is accepted"));
  });

  test("Wrong Recipient Attack: attacker sends canonical USDT to different address -> rejected with 400 WRONG_RECIPIENT", async () => {
    const txHash = "0x" + "61".repeat(32);
    const wrongRecipient = "0x7777777777777777777777777777777777777777";

    const mockRpc = buildMockRpcClient({
      txHash,
      network: "bsc",
      tokenAddress: legitimateBscUsdt,
      recipientAddress: wrongRecipient,
      rawAmount: 5000000000000000000n,
    });

    const res = await verifyPaymentOnChain(
      { network: "bsc", txHash },
      {},
      { customRpcClient: mockRpc }
    );

    assert.equal(res.success, false);
    assert.equal(res.status, 400);
    assert.equal(res.error, DIAGNOSTIC_ERRORS.WRONG_RECIPIENT.code);
    assert.ok(res.message.includes(wrongRecipient.toLowerCase()));
  });

  test("Reverted On-Chain Transaction: status = '0x0' -> rejected with 400 TRANSACTION_FAILED", async () => {
    const txHash = "0x" + "62".repeat(32);
    const mockRpc = buildMockRpcClient({
      txHash,
      network: "bsc",
      rawAmount: 5000000000000000000n,
      status: "0x0", // Reverted!
    });

    const res = await verifyPaymentOnChain(
      { network: "bsc", txHash },
      {},
      { customRpcClient: mockRpc }
    );

    assert.equal(res.success, false);
    assert.equal(res.status, 400);
    assert.equal(res.error, DIAGNOSTIC_ERRORS.TRANSACTION_FAILED.code);
  });

  test("Insufficient Confirmations: BSC with 1 confirmation (3 required) -> returns 202 INSUFFICIENT_CONFIRMATIONS", async () => {
    const txHash = "0x" + "63".repeat(32);
    const receiptBlock = 1000;
    const latestBlock = 1000; // only 1 confirmation (1000 - 1000 + 1 = 1)

    const mockRpc = buildMockRpcClient({
      txHash,
      network: "bsc",
      rawAmount: 5000000000000000000n,
      receiptBlock,
      latestBlock,
    });

    const res = await verifyPaymentOnChain(
      { network: "bsc", txHash },
      {},
      { customRpcClient: mockRpc }
    );

    assert.equal(res.success, false);
    assert.equal(res.status, 202);
    assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.code);
    assert.ok(res.message.includes("1/3 confirmations"));
  });

  test("Multi-Log Traversal Adversarial Bomb: 6 decoy logs with DEX swaps, fake tokens, underpayments; verifier successfully finds legitimate transfer", async () => {
    const txHash = "0x" + "64".repeat(32);
    const fakeToken = "0x8888888888888888888888888888888888888888";
    const wrongRecipient = "0x4444444444444444444444444444444444444444";

    const extraLogs = [
      // Decoy 1: Swap event
      {
        address: "0x10ed43c718714eb63d5aa57b78b54704e256024e",
        topics: ["0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"],
        data: "0x0000",
      },
      // Decoy 2: Fake token transfer to store wallet
      {
        address: fakeToken,
        topics: [ERC20_TRANSFER_TOPIC, topicAddress("0x1111"), topicAddress(storeWallet)],
        data: dataValue(5000000000000000000n),
      },
      // Decoy 3: Legitimate USDT to wrong recipient
      {
        address: legitimateBscUsdt,
        topics: [ERC20_TRANSFER_TOPIC, topicAddress("0x1111"), topicAddress(wrongRecipient)],
        data: dataValue(5000000000000000000n),
      },
      // Decoy 4: Legitimate USDT to store wallet with INSUFFICIENT amount (1 USDT)
      {
        address: legitimateBscUsdt,
        topics: [ERC20_TRANSFER_TOPIC, topicAddress("0x1111"), topicAddress(storeWallet)],
        data: dataValue(1000000000000000000n),
      },
      // Decoy 5: Removed log (reorg event)
      {
        removed: true,
        address: legitimateBscUsdt,
        topics: [ERC20_TRANSFER_TOPIC, topicAddress("0x1111"), topicAddress(storeWallet)],
        data: dataValue(5000000000000000000n),
      },
    ];

    // The genuine log will be appended by buildMockRpcClient
    const mockRpc = buildMockRpcClient({
      txHash,
      network: "bsc",
      rawAmount: 5000000000000000000n, // 5.00 USDT
      extraLogs,
    });

    const res = await verifyPaymentOnChain(
      { network: "bsc", txHash },
      {},
      { customRpcClient: mockRpc }
    );

    assert.equal(res.success, true, "Multi-log traversal must successfully locate genuine transfer");
    assert.equal(res.status, 200);
    assert.equal(res.data?.amountUsdt, "5.00");
  });
});
