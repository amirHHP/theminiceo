import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { EvmRpcClient, RpcConnectionError } from "../src/rpc.js";
describe("Fault-Tolerant EVM RPC Client", () => {
    test("Successfully queries with working primary endpoint", async () => {
        const mockFetch = async (url, init) => {
            const body = JSON.parse(init?.body);
            assert.equal(body.method, "eth_blockNumber");
            return new Response(JSON.stringify({ jsonrpc: "2.0", id: 1, result: "0x1234" }), {
                status: 200,
                headers: { "Content-Type": "application/json" },
            });
        };
        const client = new EvmRpcClient(["https://rpc1.example.com"], { fetchFn: mockFetch });
        const block = await client.eth_blockNumber();
        assert.equal(block, 0x1234n);
    });
    test("Cycles to secondary endpoint when primary fails", async () => {
        let callCount = 0;
        const mockFetch = async (url) => {
            callCount++;
            if (url === "https://rpc1.example.com") {
                throw new Error("Connection refused");
            }
            return new Response(JSON.stringify({ jsonrpc: "2.0", id: 1, result: "0x5678" }), {
                status: 200,
                headers: { "Content-Type": "application/json" },
            });
        };
        const client = new EvmRpcClient(["https://rpc1.example.com", "https://rpc2.example.com"], { fetchFn: mockFetch });
        const block = await client.eth_blockNumber();
        assert.equal(block, 0x5678n);
        assert.equal(callCount, 2);
    });
    test("Throws RpcConnectionError when all endpoints fail", async () => {
        const mockFetch = async () => {
            throw new Error("Network unreachable");
        };
        const client = new EvmRpcClient(["https://rpc1.example.com", "https://rpc2.example.com"], { fetchFn: mockFetch });
        await assert.rejects(async () => {
            await client.eth_blockNumber();
        }, (err) => {
            assert.ok(err instanceof RpcConnectionError);
            assert.equal(err.failedUrls.length, 2);
            return true;
        });
    });
    test("Handles RPC error responses correctly", async () => {
        const mockFetch = async () => {
            return new Response(JSON.stringify({
                jsonrpc: "2.0",
                id: 1,
                error: { code: -32600, message: "Invalid request" },
            }), { status: 200 });
        };
        const client = new EvmRpcClient(["https://rpc1.example.com"], { fetchFn: mockFetch });
        await assert.rejects(async () => {
            await client.eth_blockNumber();
        }, /Invalid request/);
    });
    test("Correctly fetches transaction receipt and transaction by hash", async () => {
        const mockReceipt = {
            transactionHash: "0x" + "1".repeat(64),
            blockNumber: "0x10",
            status: "0x1",
            logs: [],
        };
        const mockTx = {
            hash: "0x" + "1".repeat(64),
            blockNumber: "0x10",
            from: "0x" + "2".repeat(40),
            to: "0x" + "3".repeat(40),
            value: "0x0",
        };
        const mockFetch = async (_url, init) => {
            const body = JSON.parse(init?.body);
            if (body.method === "eth_getTransactionReceipt") {
                return new Response(JSON.stringify({ jsonrpc: "2.0", id: 1, result: mockReceipt }));
            }
            if (body.method === "eth_getTransactionByHash") {
                return new Response(JSON.stringify({ jsonrpc: "2.0", id: 1, result: mockTx }));
            }
            throw new Error("Unknown method");
        };
        const client = new EvmRpcClient(["https://rpc.example.com"], { fetchFn: mockFetch });
        const receipt = await client.eth_getTransactionReceipt(mockReceipt.transactionHash);
        assert.deepEqual(receipt, mockReceipt);
        const tx = await client.eth_getTransactionByHash(mockTx.hash);
        assert.deepEqual(tx, mockTx);
    });
});
