/**
 * Fault-Tolerant EVM JSON-RPC Client
 * Cycles through fallback endpoints with AbortController timeout protection
 */
import { RPC_TIMEOUT_MS } from "./config.js";
export class RpcConnectionError extends Error {
    failedUrls;
    constructor(message, failedUrls) {
        super(message);
        this.failedUrls = failedUrls;
        this.name = "RpcConnectionError";
    }
}
export class EvmRpcClient {
    rpcUrls;
    timeoutMs;
    fetchFn;
    constructor(rpcUrls, options) {
        if (!rpcUrls || rpcUrls.length === 0) {
            throw new Error("EvmRpcClient requires at least one RPC URL");
        }
        this.rpcUrls = rpcUrls;
        this.timeoutMs = options?.timeoutMs ?? RPC_TIMEOUT_MS;
        this.fetchFn = options?.fetchFn ?? fetch;
    }
    /**
     * Executes a JSON-RPC request with automated endpoint failover and timeout protection
     */
    async callRpc(method, params = []) {
        const failedUrls = [];
        let lastError = null;
        for (const url of this.rpcUrls) {
            const controller = new AbortController();
            const timer = setTimeout(() => controller.abort(), this.timeoutMs);
            try {
                const response = await this.fetchFn(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json",
                    },
                    body: JSON.stringify({
                        jsonrpc: "2.0",
                        id: 1,
                        method,
                        params,
                    }),
                    signal: controller.signal,
                });
                clearTimeout(timer);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status} ${response.statusText}`);
                }
                const data = (await response.json());
                if (data.error) {
                    throw new Error(data.error.message || `RPC returned error code ${data.error.code}`);
                }
                return data.result;
            }
            catch (err) {
                clearTimeout(timer);
                failedUrls.push(url);
                if (err instanceof Error) {
                    if (err.name === "AbortError") {
                        lastError = new Error(`Request to ${url} timed out after ${this.timeoutMs}ms`);
                    }
                    else {
                        lastError = err;
                    }
                }
                else {
                    lastError = new Error(String(err));
                }
            }
        }
        throw new RpcConnectionError(`All ${this.rpcUrls.length} RPC endpoints failed. Last error: ${lastError?.message || "Unknown error"}`, failedUrls);
    }
    /**
     * Retrieves the transaction receipt by transaction hash.
     * Returns null if transaction has not yet been mined into a block.
     */
    async eth_getTransactionReceipt(txHash) {
        return this.callRpc("eth_getTransactionReceipt", [txHash]);
    }
    /**
     * Retrieves transaction information by hash.
     * Returns null if transaction is not recognized in the node's view.
     * If pending in mempool, blockNumber will be null.
     */
    async eth_getTransactionByHash(txHash) {
        return this.callRpc("eth_getTransactionByHash", [txHash]);
    }
    /**
     * Retrieves current latest block number on chain as a BigInt.
     */
    async eth_blockNumber() {
        const hex = await this.callRpc("eth_blockNumber", []);
        if (!hex) {
            throw new Error("Empty blockNumber returned by RPC");
        }
        return BigInt(hex);
    }
}
