import { test, describe } from "node:test";
import assert from "node:assert/strict";
import {
  verifyPaymentOnChain,
  DIAGNOSTIC_ERRORS,
} from "../src/verifier.js";
import {
  DEFAULT_STORE_WALLET,
  DEFAULT_USDT_PRICE,
  ERC20_TRANSFER_TOPIC,
  NETWORKS,
} from "../src/config.js";
import { EvmRpcClient, type RpcReceipt } from "../src/rpc.js";
import { handleRequest, type Env } from "../src/index.js";
import { recordRedemption } from "../src/replay.js";

// Helper to construct 32-byte hex word from address
function topicAddress(address: string): string {
  const clean = address.toLowerCase().replace(/^0x/, "");
  return "0x" + clean.padStart(64, "0");
}

// Helper to construct 32-byte hex word from BigInt value
function dataValue(value: bigint): string {
  return "0x" + value.toString(16).padStart(64, "0");
}

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
              throw new Error("UNIQUE constraint failed: tx_hash");
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

describe("Empirical Challenge Suite: Multi-Chain Replay & RPC Resilience", () => {
  const storeWallet = DEFAULT_STORE_WALLET.toLowerCase();
  const buyerWallet = "0x" + "1".repeat(40);
  const legitimateBscTxHash = "0x" + "b5c1".repeat(16);

  // =========================================================================
  // CHALLENGE 1: Cross-Chain Replay Isolation
  // =========================================================================
  describe("1. Cross-Chain Replay Isolation", () => {
    test("1.1 Submitting valid BSC transaction hash on Polygon returns 404 TRANSACTION_NOT_FOUND when tx does not exist on Polygon", async () => {
      // Polygon RPC has never seen this BSC transaction hash
      const polygonRpcClient = {
        async eth_getTransactionReceipt() {
          return null;
        },
        async eth_getTransactionByHash() {
          return null;
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "polygon", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: polygonRpcClient }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 404);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.TRANSACTION_NOT_FOUND.code);
      assert.ok(res.message.includes("Transaction not found on this network"));
    });

    test("1.2 Submitting valid BSC transaction hash on Arbitrum returns 404 TRANSACTION_NOT_FOUND when tx does not exist on Arbitrum", async () => {
      const arbitrumRpcClient = {
        async eth_getTransactionReceipt() {
          return null;
        },
        async eth_getTransactionByHash() {
          return null;
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "arbitrum", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: arbitrumRpcClient }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 404);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.TRANSACTION_NOT_FOUND.code);
      assert.ok(res.message.includes("Transaction not found on this network"));
    });

    test("1.3 Cross-chain collision attack: BSC payment receipt submitted to Polygon RPC is rejected with 400 INVALID_TOKEN_CONTRACT", async () => {
      // Suppose by hash collision or synthetic replay, a receipt exists on Polygon RPC
      // but it transferred BSC USDT contract (0x55d398326f99059ff775485246999027b3197955)
      // instead of Polygon canonical USDT (0xc2132D05D31c914a87C6611C10748AEb04B58e8F)
      const collisionRpcClient = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: legitimateBscTxHash,
            blockNumber: "0x1000",
            status: "0x1",
            logs: [
              {
                address: NETWORKS.bsc.usdtContract, // BSC USDT contract on Polygon!
                topics: [
                  ERC20_TRANSFER_TOPIC,
                  topicAddress(buyerWallet),
                  topicAddress(storeWallet),
                ],
                data: dataValue(5000000000000000000n),
              },
            ],
          };
        },
        async eth_blockNumber() {
          return 0x1020n; // 33 confirmations
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "polygon", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: collisionRpcClient }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.code);
      assert.ok(res.message.includes("unauthorized token"));
    });

    test("1.4 Cross-chain collision attack: BSC payment receipt submitted to Arbitrum RPC is rejected with 400 INVALID_TOKEN_CONTRACT", async () => {
      const collisionRpcClient = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: legitimateBscTxHash,
            blockNumber: "0x1000",
            status: "0x1",
            logs: [
              {
                address: NETWORKS.bsc.usdtContract, // BSC USDT contract on Arbitrum!
                topics: [
                  ERC20_TRANSFER_TOPIC,
                  topicAddress(buyerWallet),
                  topicAddress(storeWallet),
                ],
                data: dataValue(5000000000000000000n),
              },
            ],
          };
        },
        async eth_blockNumber() {
          return 0x1010n;
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "arbitrum", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: collisionRpcClient }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.code);
    });

    test("1.5 Cross-chain replay attack prevention after prior redemption in D1 database", async () => {
      const db = createMockD1();
      // Record transaction redemption on BSC
      await recordRedemption(
        {
          txHash: legitimateBscTxHash,
          network: "bsc",
          bookId: "clean-code",
          email: "buyer@example.com",
          senderAddress: buyerWallet,
          amountRaw: "5000000000000000000",
          blockNumber: 1000,
        },
        { DB: db }
      );

      // Now attacker attempts to redeem same hash on Polygon
      const resPolygon = await verifyPaymentOnChain(
        { network: "polygon", txHash: legitimateBscTxHash },
        { DB: db }
      );
      assert.equal(resPolygon.success, false);
      assert.equal(resPolygon.status, 409);
      assert.equal(resPolygon.error, DIAGNOSTIC_ERRORS.TRANSACTION_ALREADY_REDEEMED.code);

      // And on Arbitrum
      const resArbitrum = await verifyPaymentOnChain(
        { network: "arbitrum", txHash: legitimateBscTxHash },
        { DB: db }
      );
      assert.equal(resArbitrum.success, false);
      assert.equal(resArbitrum.status, 409);
      assert.equal(resArbitrum.error, DIAGNOSTIC_ERRORS.TRANSACTION_ALREADY_REDEEMED.code);
    });

    test("1.6 Full API HTTP Endpoint verifies cross-chain replay rejection", async () => {
      const db = createMockD1();
      const env: Env = {
        STORE_WALLET_ADDRESS: storeWallet,
        USDT_PRICE: DEFAULT_USDT_PRICE,
        DOWNLOAD_HMAC_SECRET: "sec-key",
        BASE_URL: "https://theminiceo.ir",
        DB: db,
        CUSTOM_RPC_CLIENT: {
          async eth_getTransactionReceipt() {
            return null;
          },
          async eth_getTransactionByHash() {
            return null;
          },
        } as unknown as EvmRpcClient,
      };

      const req = new Request("https://theminiceo.ir/api/verify-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          network: "polygon",
          txHash: legitimateBscTxHash,
          bookId: "clean-code",
          email: "attacker@example.com",
        }),
      });

      const res = await handleRequest(req, env);
      assert.equal(res.status, 404);
      const json = (await res.json()) as any;
      assert.equal(json.success, false);
      assert.equal(json.error, "TRANSACTION_NOT_FOUND");
    });
  });

  // =========================================================================
  // CHALLENGE 2: Fake Token Contract Detection
  // =========================================================================
  describe("2. Fake Token Contract Detection", () => {
    test("2.1 Rejects transactions transferring fake/scam ERC-20 token on BSC (status 400 INVALID_TOKEN_CONTRACT)", async () => {
      const fakeToken = "0x" + "badf00d".repeat(5) + "1234567890";
      const rpcClient = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: legitimateBscTxHash,
            blockNumber: "0x500",
            status: "0x1",
            logs: [
              {
                address: fakeToken,
                topics: [
                  ERC20_TRANSFER_TOPIC,
                  topicAddress(buyerWallet),
                  topicAddress(storeWallet),
                ],
                data: dataValue(1000000000000000000000n), // 1000 fake tokens!
              },
            ],
          };
        },
        async eth_blockNumber() {
          return 0x510n; // 17 confirmations
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.code);
    });

    test("2.2 Rejects fake token transfer on Polygon (status 400 INVALID_TOKEN_CONTRACT)", async () => {
      const fakePolygonToken = "0x" + "2".repeat(40);
      const rpcClient = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: legitimateBscTxHash,
            blockNumber: "0x500",
            status: "0x1",
            logs: [
              {
                address: fakePolygonToken,
                topics: [
                  ERC20_TRANSFER_TOPIC,
                  topicAddress(buyerWallet),
                  topicAddress(storeWallet),
                ],
                data: dataValue(5000000n),
              },
            ],
          };
        },
        async eth_blockNumber() {
          return 0x520n;
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "polygon", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.code);
    });

    test("2.3 Rejects fake token with single-character difference from canonical USDT (typosquatting token address)", async () => {
      // Real BSC USDT is 0x55d398326f99059ff775485246999027b3197955
      const typosquatToken = "0x55d398326f99059ff775485246999027b3197956";
      const rpcClient = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: legitimateBscTxHash,
            blockNumber: "0x500",
            status: "0x1",
            logs: [
              {
                address: typosquatToken,
                topics: [
                  ERC20_TRANSFER_TOPIC,
                  topicAddress(buyerWallet),
                  topicAddress(storeWallet),
                ],
                data: dataValue(5000000000000000000n),
              },
            ],
          };
        },
        async eth_blockNumber() {
          return 0x520n;
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.code);
    });

    test("2.4 Multi-log attack: Attacker bundles genuine USDT to third-party and fake USDT to store wallet", async () => {
      const fakeToken = "0x" + "f".repeat(40);
      const thirdParty = "0x" + "3".repeat(40);
      const rpcClient = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: legitimateBscTxHash,
            blockNumber: "0x500",
            status: "0x1",
            logs: [
              // Log 0: Genuine USDT sent to THIRD PARTY
              {
                address: NETWORKS.bsc.usdtContract,
                topics: [
                  ERC20_TRANSFER_TOPIC,
                  topicAddress(buyerWallet),
                  topicAddress(thirdParty),
                ],
                data: dataValue(5000000000000000000n),
              },
              // Log 1: Fake USDT sent to STORE WALLET
              {
                address: fakeToken,
                topics: [
                  ERC20_TRANSFER_TOPIC,
                  topicAddress(buyerWallet),
                  topicAddress(storeWallet),
                ],
                data: dataValue(5000000000000000000n),
              },
            ],
          };
        },
        async eth_blockNumber() {
          return 0x520n;
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient }
      );

      // Must NOT succeed!
      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      // Either WRONG_RECIPIENT (for canonical log) or INVALID_TOKEN_CONTRACT
      assert.ok(
        res.error === DIAGNOSTIC_ERRORS.WRONG_RECIPIENT.code ||
        res.error === DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.code
      );
    });

    test("2.5 Rejects Non-Transfer event (e.g. Approval) on canonical USDT contract", async () => {
      const approvalTopic = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925";
      const rpcClient = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: legitimateBscTxHash,
            blockNumber: "0x500",
            status: "0x1",
            logs: [
              {
                address: NETWORKS.bsc.usdtContract,
                topics: [
                  approvalTopic, // Approval, not Transfer!
                  topicAddress(buyerWallet),
                  topicAddress(storeWallet),
                ],
                data: dataValue(5000000000000000000n),
              },
            ],
          };
        },
        async eth_blockNumber() {
          return 0x520n;
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient }
      );

      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.NO_USDT_TRANSFER_FOUND.code);
    });
  });

  // =========================================================================
  // CHALLENGE 3: Confirmation Depth Boundaries
  // =========================================================================
  describe("3. Confirmation Depth Boundaries", () => {
    const receiptBlock = 1000n;

    function createConfirmedReceipt(): RpcReceipt {
      return {
        transactionHash: legitimateBscTxHash,
        blockNumber: "0x3e8", // 1000 in hex
        status: "0x1",
        logs: [
          {
            address: NETWORKS.bsc.usdtContract,
            topics: [
              ERC20_TRANSFER_TOPIC,
              topicAddress(buyerWallet),
              topicAddress(storeWallet),
            ],
            data: dataValue(5000000000000000000n),
          },
        ],
      };
    }

    test("3.1 BSC boundary: 1 and 2 confirmations return 202 INSUFFICIENT_CONFIRMATIONS; 3 confirmations returns 200 OK", async () => {
      // Case A: 1 confirmation (latestBlock = receiptBlock = 1000)
      const rpcClient1 = {
        async eth_getTransactionReceipt() {
          return createConfirmedReceipt();
        },
        async eth_blockNumber() {
          return receiptBlock; // 1000 - 1000 + 1 = 1 conf
        },
      } as unknown as EvmRpcClient;

      const res1 = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient1 }
      );
      assert.equal(res1.success, false);
      assert.equal(res1.status, 202);
      assert.equal(res1.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.code);
      assert.ok(res1.message.includes("1/3 confirmations"));

      // Case B: 2 confirmations (latestBlock = 1001)
      const rpcClient2 = {
        async eth_getTransactionReceipt() {
          return createConfirmedReceipt();
        },
        async eth_blockNumber() {
          return 1001n; // 1001 - 1000 + 1 = 2 confs
        },
      } as unknown as EvmRpcClient;

      const res2 = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient2 }
      );
      assert.equal(res2.success, false);
      assert.equal(res2.status, 202);
      assert.equal(res2.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.code);
      assert.ok(res2.message.includes("2/3 confirmations"));

      // Case C: 3 confirmations (latestBlock = 1002) -> Boundary reached!
      const rpcClient3 = {
        async eth_getTransactionReceipt() {
          return createConfirmedReceipt();
        },
        async eth_blockNumber() {
          return 1002n; // 1002 - 1000 + 1 = 3 confs
        },
      } as unknown as EvmRpcClient;

      const res3 = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient3 }
      );
      assert.equal(res3.success, true);
      assert.equal(res3.status, 200);
      assert.equal(res3.data?.confirmations, 3);
      assert.equal(res3.data?.minConfirmations, 3);
    });

    test("3.2 Polygon boundary: 9 confirmations return 202 INSUFFICIENT_CONFIRMATIONS; 10 confirmations returns 200 OK", async () => {
      function createPolygonReceipt(): RpcReceipt {
        return {
          transactionHash: legitimateBscTxHash,
          blockNumber: "0x1388", // 5000 in hex
          status: "0x1",
          logs: [
            {
              address: NETWORKS.polygon.usdtContract,
              topics: [
                ERC20_TRANSFER_TOPIC,
                topicAddress(buyerWallet),
                topicAddress(storeWallet),
              ],
              data: dataValue(5000000n), // 5 USDT (6 decimals)
            },
          ],
        };
      }

      // Case A: 9 confirmations (latestBlock = 5008)
      const rpcClient9 = {
        async eth_getTransactionReceipt() {
          return createPolygonReceipt();
        },
        async eth_blockNumber() {
          return 5008n; // 5008 - 5000 + 1 = 9 confs (Polygon requires 10)
        },
      } as unknown as EvmRpcClient;

      const res9 = await verifyPaymentOnChain(
        { network: "polygon", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient9 }
      );
      assert.equal(res9.success, false);
      assert.equal(res9.status, 202);
      assert.equal(res9.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.code);
      assert.ok(res9.message.includes("9/10 confirmations"));

      // Case B: 10 confirmations (latestBlock = 5009) -> Boundary reached!
      const rpcClient10 = {
        async eth_getTransactionReceipt() {
          return createPolygonReceipt();
        },
        async eth_blockNumber() {
          return 5009n; // 5009 - 5000 + 1 = 10 confs
        },
      } as unknown as EvmRpcClient;

      const res10 = await verifyPaymentOnChain(
        { network: "polygon", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient10 }
      );
      assert.equal(res10.success, true);
      assert.equal(res10.status, 200);
      assert.equal(res10.data?.confirmations, 10);
      assert.equal(res10.data?.minConfirmations, 10);
    });

    test("3.3 Arbitrum boundary: 1 confirmation returns 202 INSUFFICIENT_CONFIRMATIONS; 2 confirmations returns 200 OK", async () => {
      function createArbitrumReceipt(): RpcReceipt {
        return {
          transactionHash: legitimateBscTxHash,
          blockNumber: "0x7d0", // 2000 in hex
          status: "0x1",
          logs: [
            {
              address: NETWORKS.arbitrum.usdtContract,
              topics: [
                ERC20_TRANSFER_TOPIC,
                topicAddress(buyerWallet),
                topicAddress(storeWallet),
              ],
              data: dataValue(5000000n), // 5 USDT (6 decimals)
            },
          ],
        };
      }

      // 1 confirmation (latestBlock = 2000)
      const rpcClient1 = {
        async eth_getTransactionReceipt() {
          return createArbitrumReceipt();
        },
        async eth_blockNumber() {
          return 2000n; // 2000 - 2000 + 1 = 1 conf (Arbitrum requires 2)
        },
      } as unknown as EvmRpcClient;

      const res1 = await verifyPaymentOnChain(
        { network: "arbitrum", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient1 }
      );
      assert.equal(res1.success, false);
      assert.equal(res1.status, 202);
      assert.equal(res1.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.code);
      assert.ok(res1.message.includes("1/2 confirmations"));

      // 2 confirmations (latestBlock = 2001) -> Boundary reached!
      const rpcClient2 = {
        async eth_getTransactionReceipt() {
          return createArbitrumReceipt();
        },
        async eth_blockNumber() {
          return 2001n; // 2001 - 2000 + 1 = 2 confs
        },
      } as unknown as EvmRpcClient;

      const res2 = await verifyPaymentOnChain(
        { network: "arbitrum", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClient2 }
      );
      assert.equal(res2.success, true);
      assert.equal(res2.status, 200);
      assert.equal(res2.data?.confirmations, 2);
    });

    test("3.4 Mempool pending transaction returns 202 TRANSACTION_PENDING", async () => {
      const rpcClientMempool = {
        async eth_getTransactionReceipt() {
          return null; // not mined yet
        },
        async eth_getTransactionByHash() {
          return {
            hash: legitimateBscTxHash,
            blockNumber: null, // Pending in mempool!
          };
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClientMempool }
      );
      assert.equal(res.success, false);
      assert.equal(res.status, 202);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.TRANSACTION_PENDING.code);
      assert.ok(res.message.includes("mempool"));
    });

    test("3.5 Node failure during eth_blockNumber safely defaults to 1 confirmation and returns 202 INSUFFICIENT_CONFIRMATIONS", async () => {
      const rpcClientError = {
        async eth_getTransactionReceipt() {
          return createConfirmedReceipt();
        },
        async eth_blockNumber() {
          throw new Error("RPC temporary failure fetching latest block");
        },
      } as unknown as EvmRpcClient;

      // When eth_blockNumber fails, fallback logic treats latestBlock as receiptBlock (1 conf)
      // Since BSC requires 3 confs, it safely returns 202 INSUFFICIENT_CONFIRMATIONS rather than 200
      const res = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClientError }
      );
      assert.equal(res.success, false);
      assert.equal(res.status, 202);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.code);
    });

    test("3.6 Reverted transaction (status 0x0) returns 400 TRANSACTION_FAILED regardless of confirmation depth", async () => {
      const rpcClientReverted = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: legitimateBscTxHash,
            blockNumber: "0x100",
            status: "0x0", // Reverted!
            logs: [],
          };
        },
        async eth_blockNumber() {
          return 0x500n; // 1000+ confirmations
        },
      } as unknown as EvmRpcClient;

      const res = await verifyPaymentOnChain(
        { network: "bsc", txHash: legitimateBscTxHash },
        {},
        { customRpcClient: rpcClientReverted }
      );
      assert.equal(res.success, false);
      assert.equal(res.status, 400);
      assert.equal(res.error, DIAGNOSTIC_ERRORS.TRANSACTION_FAILED.code);
    });
  });
});
