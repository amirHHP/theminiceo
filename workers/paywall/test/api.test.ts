import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { handleRequest } from "../src/index.js";
import {
  DEFAULT_STORE_WALLET,
  DEFAULT_USDT_PRICE,
  ERC20_TRANSFER_TOPIC,
  NETWORKS,
} from "../src/config.js";

// Minimal mock D1
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
        async first() {
          if (query.includes("SELECT")) {
            return store.get(boundParams[0]) || null;
          }
          return null;
        },
        async run() {
          if (query.includes("INSERT")) {
            if (store.has(boundParams[0])) {
              throw new Error("UNIQUE constraint failed");
            }
            store.set(boundParams[0], boundParams);
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

describe("Worker API Endpoints & Router", () => {
  const env = {
    STORE_WALLET_ADDRESS: DEFAULT_STORE_WALLET,
    USDT_PRICE: DEFAULT_USDT_PRICE,
    DOWNLOAD_HMAC_SECRET: "test-secret-12345",
    BASE_URL: "https://theminiceo.ir",
    DB: createMockD1(),
  };

  test("OPTIONS /api/config returns 204 CORS preflight", async () => {
    const req = new Request("https://theminiceo.ir/api/config", {
      method: "OPTIONS",
      headers: {
        Origin: "https://theminiceo.ir",
        "Access-Control-Request-Method": "GET",
      },
    });

    const res = await handleRequest(req, env);
    assert.equal(res.status, 204);
    assert.ok(res.headers.get("Access-Control-Allow-Origin"));
    assert.ok(res.headers.get("Access-Control-Allow-Methods")?.includes("GET"));
  });

  test("GET /api/config returns complete multi-chain parameters matching spec", async () => {
    const req = new Request("https://theminiceo.ir/api/config", {
      method: "GET",
    });

    const res = await handleRequest(req, env);
    assert.equal(res.status, 200);
    assert.equal(res.headers.get("Content-Type"), "application/json; charset=utf-8");

    const json = (await res.json()) as any;
    assert.equal(json.success, true);
    assert.equal(json.pricing.amount, "5.00");
    assert.equal(json.pricing.currency, "USDT");
    assert.equal(json.storeWallet, DEFAULT_STORE_WALLET);
    assert.equal(json.downloadExpirySeconds, 7200);
    assert.equal(json.networks.length, 3);

    const bsc = json.networks.find((n: any) => n.id === "bsc");
    assert.ok(bsc);
    assert.equal(bsc.chainId, 56);
    assert.equal(bsc.decimals, 18);
    assert.equal(bsc.usdtContract, NETWORKS.bsc.usdtContract);
  });

  test("POST /api/verify-payment rejects invalid JSON", async () => {
    const req = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "invalid-json{",
    });

    const res = await handleRequest(req, env);
    assert.equal(res.status, 400);
    const json = (await res.json()) as any;
    assert.equal(json.success, false);
    assert.equal(json.error, "INVALID_JSON");
  });

  test("POST /api/verify-payment validates missing fields", async () => {
    // Missing network
    const req1 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const res1 = await handleRequest(req1, env);
    assert.equal(res1.status, 400);

    // Unsupported network
    const req2 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ network: "fantom", txHash: "0x" + "a".repeat(64) }),
    });
    const res2 = await handleRequest(req2, env);
    assert.equal(res2.status, 400);
    const json2 = (await res2.json()) as any;
    assert.equal(json2.error, "UNSUPPORTED_NETWORK");

    // Invalid TxHash
    const req3 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ network: "bsc", txHash: "0xshort" }),
    });
    const res3 = await handleRequest(req3, env);
    assert.equal(res3.status, 400);
    const json3 = (await res3.json()) as any;
    assert.equal(json3.error, "INVALID_TX_HASH_FORMAT");

    // Missing bookId
    const req4 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ network: "bsc", txHash: "0x" + "a".repeat(64), bookId: "" }),
    });
    const res4 = await handleRequest(req4, env);
    assert.equal(res4.status, 400);
    const json4 = (await res4.json()) as any;
    assert.equal(json4.error, "BOOK_ID_REQUIRED");

    // Missing / invalid email
    const req5 = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "bsc",
        txHash: "0x" + "a".repeat(64),
        bookId: "the-lean-startup",
        email: "notanemail",
      }),
    });
    const res5 = await handleRequest(req5, env);
    assert.equal(res5.status, 400);
    const json5 = (await res5.json()) as any;
    assert.equal(json5.error, "INVALID_EMAIL");
  });

  test("POST /api/verify-payment succeeds with valid on-chain payment and rejects replay", async () => {
    const validTxHash = "0x" + "b".repeat(64);
    const buyerWallet = "0x" + "1".repeat(40);
    const mockRpcClient = {
      async eth_getTransactionReceipt() {
        return {
          transactionHash: validTxHash,
          blockNumber: "0x1000",
          status: "0x1",
          logs: [
            {
              address: NETWORKS.bsc.usdtContract,
              topics: [
                ERC20_TRANSFER_TOPIC,
                topicAddress(buyerWallet),
                topicAddress(DEFAULT_STORE_WALLET),
              ],
              data: dataValue(5000000000000000000n), // 5.0 USDT
            },
          ],
        };
      },
      async eth_blockNumber() {
        return 0x1020n; // Plenty of confirmations
      },
    } as unknown as any;

    const testEnv = {
      ...env,
      CUSTOM_RPC_CLIENT: mockRpcClient,
      DB: createMockD1(),
    };

    const verifyReq = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "bsc",
        txHash: validTxHash,
        bookId: "the-lean-startup",
        email: "buyer@example.com",
      }),
    });

    const verifyRes = await handleRequest(verifyReq, testEnv);
    assert.equal(verifyRes.status, 200);
    const verifyData = (await verifyRes.json()) as any;
    assert.equal(verifyData.success, true);
    assert.ok(verifyData.downloadUrl.includes("/api/download?token="));
    assert.ok(verifyData.expiresAt > Math.floor(Date.now() / 1000));
    assert.equal(verifyData.expiresInSeconds, 7200);
    assert.equal(verifyData.book.id, "the-lean-startup");
    assert.equal(verifyData.txDetails.network, "bsc");
    assert.equal(verifyData.txDetails.txHash, validTxHash);
    assert.equal(verifyData.txDetails.amountUsdt, "5.00");
    assert.equal(verifyData.emailDispatched, true);

    // Replay Attempt with exact same txHash
    const replayReq = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "bsc",
        txHash: validTxHash,
        bookId: "the-lean-startup",
        email: "attacker@example.com",
      }),
    });

    const replayRes = await handleRequest(replayReq, testEnv);
    assert.equal(replayRes.status, 409);
    const replayData = (await replayRes.json()) as any;
    assert.equal(replayData.success, false);
    assert.equal(replayData.error, "TRANSACTION_ALREADY_REDEEMED");
  });

  test("POST /api/verify-payment triggers ctx.waitUntil for background email dispatch", async () => {
    const validTxHash = "0x" + "c".repeat(64);
    const buyerWallet = "0x" + "2".repeat(40);
    const mockRpcClient = {
      async eth_getTransactionReceipt() {
        return {
          transactionHash: validTxHash,
          blockNumber: "0x2000",
          status: "0x1",
          logs: [
            {
              address: NETWORKS.bsc.usdtContract,
              topics: [
                ERC20_TRANSFER_TOPIC,
                topicAddress(buyerWallet),
                topicAddress(DEFAULT_STORE_WALLET),
              ],
              data: dataValue(5000000000000000000n),
            },
          ],
        };
      },
      async eth_blockNumber() {
        return 0x2020n;
      },
    } as unknown as any;

    const testEnv = {
      ...env,
      CUSTOM_RPC_CLIENT: mockRpcClient,
      DB: createMockD1(),
    };

    const waitUntilPromises: Promise<any>[] = [];
    const mockCtx = {
      waitUntil(promise: Promise<any>) {
        waitUntilPromises.push(promise);
      },
      passThroughOnException() {},
    } as unknown as ExecutionContext;

    const req = new Request("https://theminiceo.ir/api/verify-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        network: "bsc",
        txHash: validTxHash,
        bookId: "the-lean-startup",
        email: "buyer_ctx@example.com",
      }),
    });

    const res = await handleRequest(req, testEnv, mockCtx);
    assert.equal(res.status, 200);
    const data = (await res.json()) as any;
    assert.equal(data.emailDispatched, true);
    assert.equal(waitUntilPromises.length, 1);
    await Promise.all(waitUntilPromises);
  });

  test("GET /api/download rejects missing or malformed token", async () => {
    // Missing token parameter
    const req1 = new Request("https://theminiceo.ir/api/download", { method: "GET" });
    const res1 = await handleRequest(req1, env);
    assert.equal(res1.status, 400);
    const json1 = (await res1.json()) as any;
    assert.equal(json1.error, "MISSING_TOKEN");

    // Empty token parameter
    const req2 = new Request("https://theminiceo.ir/api/download?token=", { method: "GET" });
    const res2 = await handleRequest(req2, env);
    assert.equal(res2.status, 400);
    const json2 = (await res2.json()) as any;
    assert.equal(json2.error, "MISSING_TOKEN");

    // Malformed token without dot
    const req3 = new Request("https://theminiceo.ir/api/download?token=malformednodot", { method: "GET" });
    const res3 = await handleRequest(req3, env);
    assert.equal(res3.status, 400);
    const json3 = (await res3.json()) as any;
    assert.equal(json3.error, "MALFORMED_TOKEN");
  });

  test("GET /api/download rejects invalid signature and expired token", async () => {
    // Import token helpers
    const { generateDownloadToken } = await import("../src/token.js");
    const hmacSecret = env.DOWNLOAD_HMAC_SECRET;

    // Valid token signed with different secret
    const { token: forgedToken } = await generateDownloadToken(
      {
        bookId: "the-lean-startup",
        filename: "The_Lean_Startup.pdf",
        txHash: "0x" + "d".repeat(64),
        email: "user@example.com",
        network: "bsc",
      },
      "different-hmac-secret",
      7200
    );

    const reqForged = new Request(`https://theminiceo.ir/api/download?token=${forgedToken}`, { method: "GET" });
    const resForged = await handleRequest(reqForged, env);
    assert.equal(resForged.status, 403);
    const jsonForged = (await resForged.json()) as any;
    assert.equal(jsonForged.error, "INVALID_SIGNATURE");

    // Expired token
    const { token: expiredToken } = await generateDownloadToken(
      {
        bookId: "the-lean-startup",
        filename: "The_Lean_Startup.pdf",
        txHash: "0x" + "e".repeat(64),
        email: "user@example.com",
        network: "bsc",
      },
      hmacSecret,
      -10 // Expired 10 seconds ago
    );

    const reqExpired = new Request(`https://theminiceo.ir/api/download?token=${expiredToken}`, { method: "GET" });
    const resExpired = await handleRequest(reqExpired, env);
    assert.equal(resExpired.status, 410);
    const jsonExpired = (await resExpired.json()) as any;
    assert.equal(jsonExpired.error, "TOKEN_EXPIRED");
  });

  test("GET /api/download streams PDF file from R2 and supports Range requests", async () => {
    const { generateDownloadToken } = await import("../src/token.js");
    const samplePdfBytes = new TextEncoder().encode(
      "%PDF-1.7\n1 0 obj\n<< /Title (TheMiniCEO Book) >>\nendobj\ntrailer\n<< /Size 2 >>\n%%EOF"
    );

    const mockBucket: R2Bucket = {
      async get(key: string, options?: R2GetOptions) {
        if (key !== "The_Lean_Startup_How_Todays_Entrepreneurs_Use_Continuous_Innovation.pdf") {
          return null;
        }
        const range = options?.range as any;
        let slice = samplePdfBytes;
        let effectiveOffset = 0;
        let effectiveLength = samplePdfBytes.byteLength;
        if (range && typeof range.offset === "number" && typeof range.length === "number") {
          effectiveOffset = range.offset;
          effectiveLength = range.length;
          slice = samplePdfBytes.subarray(range.offset, range.offset + range.length);
        }
        return {
          key,
          size: slice.byteLength,
          etag: '"r2-test-etag"',
          httpEtag: '"r2-test-etag"',
          range: range ? { offset: effectiveOffset, length: effectiveLength } : undefined,
          body: new ReadableStream({
            start(c) {
              c.enqueue(slice);
              c.close();
            },
          }),
        } as unknown as R2ObjectBody;
      },
    } as unknown as R2Bucket;

    const testEnv = {
      ...env,
      BOOKS_BUCKET: mockBucket,
    };

    const txHash = "0x" + "f".repeat(64);
    const { token } = await generateDownloadToken(
      {
        bookId: "the-lean-startup",
        filename: "The_Lean_Startup_How_Todays_Entrepreneurs_Use_Continuous_Innovation.pdf",
        txHash,
        email: "user@example.com",
        network: "bsc",
      },
      env.DOWNLOAD_HMAC_SECRET,
      7200
    );

    // Full file download
    const req = new Request(`https://theminiceo.ir/api/download?token=${token}`, { method: "GET" });
    const res = await handleRequest(req, testEnv);
    assert.equal(res.status, 200);
    assert.equal(res.headers.get("Content-Type"), "application/pdf");
    assert.ok(res.headers.get("Content-Disposition")?.includes("the-lean-startup.pdf"));

    const streamBytes = new Uint8Array(await res.arrayBuffer());
    assert.equal(streamBytes.byteLength, samplePdfBytes.byteLength);

    // Range request (bytes=0-15)
    const rangeReq = new Request(`https://theminiceo.ir/api/download?token=${token}`, {
      method: "GET",
      headers: { Range: "bytes=0-15" },
    });
    const rangeRes = await handleRequest(rangeReq, testEnv);
    assert.equal(rangeRes.status, 206);
    assert.equal(rangeRes.headers.get("Content-Length"), "16");
    assert.ok(rangeRes.headers.get("Content-Range")?.startsWith("bytes 0-15/"));
  });

  test("GET /api/download enforces 5-download limit and returns 429 on 6th attempt", async () => {
    const { generateDownloadToken, resetDownloadCounters } = await import("../src/token.js");
    resetDownloadCounters();

    const samplePdfBytes = new TextEncoder().encode("%PDF-1.7\nSample Book Content\n%%EOF");
    const mockBucket: R2Bucket = {
      async get() {
        return {
          key: "test.pdf",
          size: samplePdfBytes.byteLength,
          body: new ReadableStream({
            start(c) {
              c.enqueue(samplePdfBytes);
              c.close();
            },
          }),
        } as unknown as R2ObjectBody;
      },
    } as unknown as R2Bucket;

    const testEnv = {
      ...env,
      BOOKS_BUCKET: mockBucket,
    };

    const limitTxHash = "0x" + "a1b2".repeat(16);
    const { token } = await generateDownloadToken(
      {
        bookId: "the-lean-startup",
        filename: "The_Lean_Startup.pdf",
        txHash: limitTxHash,
        email: "user@example.com",
        network: "bsc",
      },
      env.DOWNLOAD_HMAC_SECRET,
      7200
    );

    for (let i = 1; i <= 5; i++) {
      const req = new Request(`https://theminiceo.ir/api/download?token=${token}`, { method: "GET" });
      const res = await handleRequest(req, testEnv);
      assert.equal(res.status, 200, `Download attempt ${i} must succeed with 200 OK`);
    }

    // 6th attempt must return 429 DOWNLOAD_LIMIT_EXCEEDED
    const req6 = new Request(`https://theminiceo.ir/api/download?token=${token}`, { method: "GET" });
    const res6 = await handleRequest(req6, testEnv);
    assert.equal(res6.status, 429);
    const json6 = (await res6.json()) as any;
    assert.equal(json6.error, "DOWNLOAD_LIMIT_EXCEEDED");
  });

  test("GET /api/download returns 404 FILE_NOT_FOUND when object missing from R2", async () => {
    const { generateDownloadToken } = await import("../src/token.js");
    const emptyBucket: R2Bucket = {
      async get() {
        return null;
      },
    } as unknown as R2Bucket;

    const testEnv = {
      ...env,
      BOOKS_BUCKET: emptyBucket,
    };

    const { token } = await generateDownloadToken(
      {
        bookId: "missing-book",
        filename: "Missing_File.pdf",
        txHash: "0x" + "7".repeat(64),
        email: "user@example.com",
        network: "bsc",
      },
      env.DOWNLOAD_HMAC_SECRET,
      7200
    );

    const req = new Request(`https://theminiceo.ir/api/download?token=${token}`, { method: "GET" });
    const res = await handleRequest(req, testEnv);
    assert.equal(res.status, 404);
    const json = (await res.json()) as any;
    assert.equal(json.error, "FILE_NOT_FOUND");
  });

  test("Unknown routes return 404", async () => {
    const req = new Request("https://theminiceo.ir/api/unknown-endpoint", {
      method: "GET",
    });
    const res = await handleRequest(req, env);
    assert.equal(res.status, 404);
  });
});
