import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { verifyPaymentOnChain, DIAGNOSTIC_ERRORS, } from "../src/verifier.js";
import { DEFAULT_STORE_WALLET, ERC20_TRANSFER_TOPIC, NETWORKS, } from "../src/config.js";
// Helper to construct 32-byte hex word from address
function topicAddress(address) {
    const clean = address.toLowerCase().replace(/^0x/, "");
    return "0x" + clean.padStart(64, "0");
}
// Helper to construct 32-byte hex word from BigInt value
function dataValue(value) {
    return "0x" + value.toString(16).padStart(64, "0");
}
describe("Payment Verification Engine (12 Diagnostic Errors & Multi-Log Traversal)", () => {
    const txHash = "0x" + "a".repeat(64);
    const storeWallet = DEFAULT_STORE_WALLET.toLowerCase();
    const buyerWallet = "0x" + "1".repeat(40);
    test("Error 1: INVALID_TX_HASH_FORMAT (status 400)", async () => {
        const res = await verifyPaymentOnChain({ network: "bsc", txHash: "0x1234" }, {});
        assert.equal(res.success, false);
        assert.equal(res.status, 400);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.INVALID_TX_HASH_FORMAT.code);
    });
    test("Error 2: UNSUPPORTED_NETWORK (status 400)", async () => {
        const res = await verifyPaymentOnChain({ network: "solana", txHash }, {});
        assert.equal(res.success, false);
        assert.equal(res.status, 400);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.UNSUPPORTED_NETWORK.code);
    });
    test("Error 3: TRANSACTION_ALREADY_REDEEMED (status 409)", async () => {
        const mockEnv = {
            PAYMENT_KV: {
                async get() {
                    return JSON.stringify({ txHash });
                },
                async put() { },
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, mockEnv);
        assert.equal(res.success, false);
        assert.equal(res.status, 409);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.TRANSACTION_ALREADY_REDEEMED.code);
    });
    test("Error 4: TRANSACTION_NOT_FOUND (status 404)", async () => {
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return null;
            },
            async eth_getTransactionByHash() {
                return null;
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, false);
        assert.equal(res.status, 404);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.TRANSACTION_NOT_FOUND.code);
    });
    test("Error 5: TRANSACTION_PENDING in mempool (status 202)", async () => {
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return null;
            },
            async eth_getTransactionByHash() {
                return { hash: txHash, blockNumber: null };
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, false);
        assert.equal(res.status, 202);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.TRANSACTION_PENDING.code);
    });
    test("Error 6: TRANSACTION_FAILED / reverted on-chain (status 400)", async () => {
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return {
                    transactionHash: txHash,
                    blockNumber: "0x100",
                    status: "0x0", // Reverted
                    logs: [],
                };
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, false);
        assert.equal(res.status, 400);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.TRANSACTION_FAILED.code);
    });
    test("Error 7: INSUFFICIENT_CONFIRMATIONS (status 202)", async () => {
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return {
                    transactionHash: txHash,
                    blockNumber: "0x64", // Block 100
                    status: "0x1",
                    logs: [],
                };
            },
            async eth_blockNumber() {
                return 101n; // 101 - 100 + 1 = 2 confirmations (BSC requires 3)
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, false);
        assert.equal(res.status, 202);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.code);
    });
    test("Error 8: NO_USDT_TRANSFER_FOUND (status 400)", async () => {
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return {
                    transactionHash: txHash,
                    blockNumber: "0x64",
                    status: "0x1",
                    logs: [], // Empty logs
                };
            },
            async eth_blockNumber() {
                return 120n;
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, false);
        assert.equal(res.status, 400);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.NO_USDT_TRANSFER_FOUND.code);
    });
    test("Error 9: INVALID_TOKEN_CONTRACT (status 400)", async () => {
        const fakeTokenAddress = "0x" + "9".repeat(40);
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return {
                    transactionHash: txHash,
                    blockNumber: "0x64",
                    status: "0x1",
                    logs: [
                        {
                            address: fakeTokenAddress,
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
                return 120n;
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, false);
        assert.equal(res.status, 400);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.code);
    });
    test("Error 10: WRONG_RECIPIENT (status 400)", async () => {
        const otherWallet = "0x" + "8".repeat(40);
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return {
                    transactionHash: txHash,
                    blockNumber: "0x64",
                    status: "0x1",
                    logs: [
                        {
                            address: NETWORKS.bsc.usdtContract,
                            topics: [
                                ERC20_TRANSFER_TOPIC,
                                topicAddress(buyerWallet),
                                topicAddress(otherWallet), // wrong recipient
                            ],
                            data: dataValue(5000000000000000000n),
                        },
                    ],
                };
            },
            async eth_blockNumber() {
                return 120n;
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, false);
        assert.equal(res.status, 400);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.WRONG_RECIPIENT.code);
    });
    test("Error 11: INSUFFICIENT_AMOUNT (status 400)", async () => {
        const underpayment = 500000000000000000n; // 0.5 USDT on BSC
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return {
                    transactionHash: txHash,
                    blockNumber: "0x64",
                    status: "0x1",
                    logs: [
                        {
                            address: NETWORKS.bsc.usdtContract,
                            topics: [
                                ERC20_TRANSFER_TOPIC,
                                topicAddress(buyerWallet),
                                topicAddress(storeWallet),
                            ],
                            data: dataValue(underpayment),
                        },
                    ],
                };
            },
            async eth_blockNumber() {
                return 120n;
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, false);
        assert.equal(res.status, 400);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.code);
        assert.ok(res.message.includes("0.50 USDT"));
    });
    test("Error 12: RPC_CONNECTION_FAILURE (status 503)", async () => {
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                throw new Error("RPC timeout");
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, false);
        assert.equal(res.status, 503);
        assert.equal(res.error, DIAGNOSTIC_ERRORS.RPC_CONNECTION_FAILURE.code);
    });
    test("Successful verification on BSC with Multi-Log Traversal", async () => {
        const intermediateAddress = "0x" + "7".repeat(40);
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return {
                    transactionHash: txHash,
                    blockNumber: "0x64",
                    status: "0x1",
                    logs: [
                        // Log 0: DEX swap event
                        {
                            address: intermediateAddress,
                            topics: ["0x" + "0".repeat(64)],
                            data: "0x1",
                        },
                        // Log 1: Fee transfer
                        {
                            address: NETWORKS.bsc.usdtContract,
                            topics: [
                                ERC20_TRANSFER_TOPIC,
                                topicAddress(buyerWallet),
                                topicAddress(intermediateAddress),
                            ],
                            data: dataValue(100000000000000000n), // 0.1 USDT
                        },
                        // Log 2: Valid Store Transfer!
                        {
                            address: NETWORKS.bsc.usdtContract,
                            topics: [
                                ERC20_TRANSFER_TOPIC,
                                topicAddress(buyerWallet),
                                topicAddress(storeWallet),
                            ],
                            data: dataValue(1000000000000000000n), // 1.0 USDT
                        },
                    ],
                };
            },
            async eth_blockNumber() {
                return 120n;
            },
        };
        const res = await verifyPaymentOnChain({ network: "bsc", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, true);
        assert.equal(res.status, 200);
        assert.ok(res.data);
        assert.equal(res.data.network, "bsc");
        assert.equal(res.data.amountUsdt, "1.00");
        assert.equal(res.data.senderAddress, buyerWallet);
        assert.equal(res.data.storeWallet, storeWallet);
    });
    test("Successful verification on Polygon (6 decimals)", async () => {
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return {
                    transactionHash: txHash,
                    blockNumber: "0x64",
                    status: "0x1",
                    logs: [
                        {
                            address: NETWORKS.polygon.usdtContract,
                            topics: [
                                ERC20_TRANSFER_TOPIC,
                                topicAddress(buyerWallet),
                                topicAddress(storeWallet),
                            ],
                            data: dataValue(1000000n), // 1 USDT (6 decimals)
                        },
                    ],
                };
            },
            async eth_blockNumber() {
                return 120n;
            },
        };
        const res = await verifyPaymentOnChain({ network: "polygon", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, true);
        assert.equal(res.data?.network, "polygon");
        assert.equal(res.data?.amountUsdt, "1.00");
    });
    test("Successful verification on Arbitrum One (6 decimals)", async () => {
        const mockRpcClient = {
            async eth_getTransactionReceipt() {
                return {
                    transactionHash: txHash,
                    blockNumber: "0x64",
                    status: "0x1",
                    logs: [
                        {
                            address: NETWORKS.arbitrum.usdtContract,
                            topics: [
                                ERC20_TRANSFER_TOPIC,
                                topicAddress(buyerWallet),
                                topicAddress(storeWallet),
                            ],
                            data: dataValue(10000000n), // 10 USDT
                        },
                    ],
                };
            },
            async eth_blockNumber() {
                return 120n;
            },
        };
        const res = await verifyPaymentOnChain({ network: "arbitrum", txHash }, {}, { customRpcClient: mockRpcClient });
        assert.equal(res.success, true);
        assert.equal(res.data?.network, "arbitrum");
        assert.equal(res.data?.amountUsdt, "10.00");
    });
});
