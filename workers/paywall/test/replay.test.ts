import { test, describe } from "node:test";
import assert from "node:assert/strict";
import {
  isTransactionRedeemed,
  recordRedemption,
  getRedemptionRecord,
  getKvKey,
} from "../src/replay.js";

// Minimal mock D1 implementation
function createMockD1(): D1Database {
  const store = new Map<string, any>();
  return {
    prepare(query: string) {
      let boundParams: any[] = [];
      return {
        bind(...params: any[]) {
          boundParams = params;
          return this;
        },
        async first<T = unknown>(): Promise<T | null> {
          if (query.includes("SELECT")) {
            const key = boundParams[0];
            return (store.get(key) as T) || null;
          }
          return null;
        },
        async run() {
          if (query.includes("INSERT")) {
            const txHash = boundParams[0];
            if (store.has(txHash)) {
              throw new Error("UNIQUE constraint failed: redeemed_transactions.tx_hash");
            }
            store.set(txHash, {
              txHash: boundParams[0],
              network: boundParams[1],
              bookId: boundParams[2],
              email: boundParams[3],
              senderAddress: boundParams[4],
              amountRaw: boundParams[5],
              blockNumber: boundParams[6],
              redeemedAt: boundParams[7],
            });
            return { success: true };
          }
          return { success: true };
        },
        async all() {
          return { results: Array.from(store.values()) };
        },
      } as unknown as D1PreparedStatement;
    },
  } as unknown as D1Database;
}

// Minimal mock KV implementation
function createMockKV(): KVNamespace {
  const store = new Map<string, string>();
  return {
    async get(key: string): Promise<string | null> {
      return store.get(key) || null;
    },
    async put(key: string, value: string): Promise<void> {
      store.set(key, value);
    },
  } as unknown as KVNamespace;
}

describe("Persistent Replay Protection", () => {
  const txHash = "0x" + "a".repeat(64);
  const network = "bsc";

  test("D1 Database: initial check, record, and duplicate rejection", async () => {
    const mockDb = createMockD1();
    const env = { DB: mockDb };

    // 1. Not redeemed yet
    const before = await isTransactionRedeemed(txHash, network, env);
    assert.equal(before, false);

    // 2. Record redemption
    const recordResult = await recordRedemption(
      {
        txHash,
        network,
        bookId: "the-lean-startup",
        email: "user@example.com",
        senderAddress: "0x" + "1".repeat(40),
        amountRaw: "5000000000000000000",
        blockNumber: 12345,
      },
      env
    );
    assert.equal(recordResult.success, true);

    // 3. Check returns true
    const after = await isTransactionRedeemed(txHash, network, env);
    assert.equal(after, true);

    // 4. Duplicate insert rejected atomically with UNIQUE constraint
    const duplicateResult = await recordRedemption(
      {
        txHash,
        network,
        bookId: "the-lean-startup",
        email: "attacker@example.com",
        senderAddress: "0x" + "2".repeat(40),
        amountRaw: "5000000000000000000",
        blockNumber: 12345,
      },
      env
    );
    assert.equal(duplicateResult.success, false);
    assert.equal(duplicateResult.duplicate, true);
    assert.equal(duplicateResult.error, "TRANSACTION_ALREADY_REDEEMED");

    // 5. Query details
    const stored = await getRedemptionRecord(txHash, network, env);
    assert.ok(stored);
    assert.equal(stored.bookId, "the-lean-startup");
    assert.equal(stored.email, "user@example.com");
  });

  test("KV Storage: fallback check and record", async () => {
    const mockKv = createMockKV();
    const env = { PAYMENT_KV: mockKv };

    assert.equal(await isTransactionRedeemed(txHash, network, env), false);

    await recordRedemption(
      {
        txHash,
        network,
        bookId: "test-book",
        email: "buyer@example.com",
        senderAddress: "0x" + "3".repeat(40),
        amountRaw: "5000000",
        blockNumber: 9999,
      },
      env
    );

    assert.equal(await isTransactionRedeemed(txHash, network, env), true);
    const key = getKvKey(network, txHash);
    const rawVal = await mockKv.get(key);
    assert.ok(rawVal);
    const parsed = JSON.parse(rawVal);
    assert.equal(parsed.bookId, "test-book");
  });
});
