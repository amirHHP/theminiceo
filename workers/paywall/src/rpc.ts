/**
 * Fault-Tolerant EVM JSON-RPC Client
 * Cycles through fallback endpoints with AbortController timeout protection
 */

import { RPC_TIMEOUT_MS } from "./config.js";

export interface RpcLog {
  address: string;
  topics: string[];
  data: string;
  removed?: boolean;
  logIndex?: string;
}

export interface RpcReceipt {
  transactionHash: string;
  blockNumber: string | number;
  status: string; // "0x1" for success, "0x0" for reverted
  from?: string;
  to?: string;
  logs: RpcLog[];
}

export interface RpcTransaction {
  hash: string;
  blockNumber: string | null;
  from?: string;
  to?: string;
  value?: string;
}

export class RpcConnectionError extends Error {
  constructor(message: string, public readonly failedUrls: string[]) {
    super(message);
    this.name = "RpcConnectionError";
  }
}

export interface RpcClientOptions {
  timeoutMs?: number;
  fetchFn?: typeof fetch;
}

export class EvmRpcClient {
  private readonly rpcUrls: readonly string[];
  private readonly timeoutMs: number;
  private readonly fetchFn: typeof fetch;

  constructor(rpcUrls: readonly string[], options?: RpcClientOptions) {
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
  async callRpc<T>(method: string, params: unknown[] = []): Promise<T> {
    const failedUrls: string[] = [];
    let lastError: Error | null = null;

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

        const data = (await response.json()) as {
          jsonrpc?: string;
          id?: number;
          result?: T;
          error?: { code?: number; message?: string };
        };

        if (data.error) {
          throw new Error(data.error.message || `RPC returned error code ${data.error.code}`);
        }

        return data.result as T;
      } catch (err: unknown) {
        clearTimeout(timer);
        failedUrls.push(url);
        if (err instanceof Error) {
          if (err.name === "AbortError") {
            lastError = new Error(`Request to ${url} timed out after ${this.timeoutMs}ms`);
          } else {
            lastError = err;
          }
        } else {
          lastError = new Error(String(err));
        }
      }
    }

    throw new RpcConnectionError(
      `All ${this.rpcUrls.length} RPC endpoints failed. Last error: ${lastError?.message || "Unknown error"}`,
      failedUrls
    );
  }

  /**
   * Retrieves the transaction receipt by transaction hash.
   * Returns null if transaction has not yet been mined into a block.
   */
  async eth_getTransactionReceipt(txHash: string): Promise<RpcReceipt | null> {
    return this.callRpc<RpcReceipt | null>("eth_getTransactionReceipt", [txHash]);
  }

  /**
   * Retrieves transaction information by hash.
   * Returns null if transaction is not recognized in the node's view.
   * If pending in mempool, blockNumber will be null.
   */
  async eth_getTransactionByHash(txHash: string): Promise<RpcTransaction | null> {
    return this.callRpc<RpcTransaction | null>("eth_getTransactionByHash", [txHash]);
  }

  /**
   * Retrieves current latest block number on chain as a BigInt.
   */
  async eth_blockNumber(): Promise<bigint> {
    const hex = await this.callRpc<string>("eth_blockNumber", []);
    if (!hex) {
      throw new Error("Empty blockNumber returned by RPC");
    }
    return BigInt(hex);
  }
}
