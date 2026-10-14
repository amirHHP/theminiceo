/**
 * Persistent Replay Protection
 * Prevents double-spending of transaction hashes via Cloudflare D1 & KV
 */

export interface RedemptionRecord {
  txHash: string;
  network: string;
  bookId: string;
  email: string;
  senderAddress: string;
  amountRaw: string;
  blockNumber: number;
  redeemedAt: number;
}

export interface ReplayStorageEnv {
  DB?: D1Database;
  PAYMENT_KV?: KVNamespace;
  PAYMENTS_KV?: KVNamespace;
}

/**
 * Key format for KV storage
 */
export function getKvKey(network: string, txHash: string): string {
  return `tx:${network.toLowerCase()}:${txHash.toLowerCase()}`;
}

/**
 * Checks whether a transaction hash has already been redeemed in D1 or KV.
 */
export async function isTransactionRedeemed(
  txHash: string,
  network: string,
  env: ReplayStorageEnv
): Promise<boolean> {
  const normalizedHash = txHash.toLowerCase().trim();
  const normalizedNetwork = network.toLowerCase().trim();

  // 1. Check Cloudflare D1 (strongly consistent on primary)
  if (env.DB) {
    try {
      const existing = await env.DB.prepare(
        "SELECT tx_hash FROM redeemed_transactions WHERE tx_hash = ?"
      )
        .bind(normalizedHash)
        .first();

      if (existing) {
        return true;
      }
    } catch (err: unknown) {
      console.error("D1 check error:", err);
    }
  }

  // 2. Check KV namespace
  const kv = env.PAYMENT_KV || env.PAYMENTS_KV;
  if (kv) {
    try {
      const key = getKvKey(normalizedNetwork, normalizedHash);
      const val = await kv.get(key);
      if (val !== null) {
        return true;
      }
    } catch (err: unknown) {
      console.error("KV check error:", err);
    }
  }

  return false;
}

/**
 * Atomically registers a transaction redemption in D1 and/or KV.
 * Returns { success: true } if registered, or { success: false, duplicate: true }
 * if a unique constraint or duplicate was detected.
 */
export async function recordRedemption(
  record: Omit<RedemptionRecord, "redeemedAt"> & { redeemedAt?: number },
  env: ReplayStorageEnv
): Promise<{ success: boolean; duplicate?: boolean; error?: string }> {
  const normalizedHash = record.txHash.toLowerCase().trim();
  const normalizedNetwork = record.network.toLowerCase().trim();
  const redeemedAt = record.redeemedAt ?? Date.now();

  const fullRecord: RedemptionRecord = {
    txHash: normalizedHash,
    network: normalizedNetwork,
    bookId: record.bookId,
    email: record.email,
    senderAddress: record.senderAddress.toLowerCase().trim(),
    amountRaw: record.amountRaw,
    blockNumber: record.blockNumber,
    redeemedAt,
  };

  // 1. Atomic registration in Cloudflare D1
  if (env.DB) {
    try {
      await env.DB.prepare(
        `INSERT INTO redeemed_transactions
          (tx_hash, network, book_id, email, sender_address, amount_raw, block_number, redeemed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
      )
        .bind(
          fullRecord.txHash,
          fullRecord.network,
          fullRecord.bookId,
          fullRecord.email,
          fullRecord.senderAddress,
          fullRecord.amountRaw,
          fullRecord.blockNumber,
          fullRecord.redeemedAt
        )
        .run();
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : String(err);
      if (errMsg.includes("UNIQUE constraint failed") || errMsg.includes("constraint failed")) {
        return { success: false, duplicate: true, error: "TRANSACTION_ALREADY_REDEEMED" };
      }
      console.error("Failed to insert record into D1:", err);
      // If D1 fails with non-duplicate error, rethrow or return failure
      return { success: false, error: errMsg };
    }
  }

  // 2. Also register in Cloudflare KV (for fast edge lookups)
  const kv = env.PAYMENT_KV || env.PAYMENTS_KV;
  if (kv) {
    try {
      const key = getKvKey(normalizedNetwork, normalizedHash);
      await kv.put(key, JSON.stringify(fullRecord));
    } catch (err: unknown) {
      console.error("Failed to write record to KV:", err);
    }
  }

  return { success: true };
}

/**
 * Retrieves full redemption details by txHash
 */
export async function getRedemptionRecord(
  txHash: string,
  network: string,
  env: ReplayStorageEnv
): Promise<RedemptionRecord | null> {
  const normalizedHash = txHash.toLowerCase().trim();

  if (env.DB) {
    try {
      const row = await env.DB.prepare(
        "SELECT tx_hash, network, book_id, email, sender_address, amount_raw, block_number, redeemed_at FROM redeemed_transactions WHERE tx_hash = ?"
      )
        .bind(normalizedHash)
        .first<RedemptionRecord>();

      if (row) {
        return {
          txHash: row.txHash || (row as unknown as { tx_hash: string }).tx_hash,
          network: row.network,
          bookId: row.bookId || (row as unknown as { book_id: string }).book_id,
          email: row.email,
          senderAddress: row.senderAddress || (row as unknown as { sender_address: string }).sender_address,
          amountRaw: row.amountRaw || (row as unknown as { amount_raw: string }).amount_raw,
          blockNumber: Number(row.blockNumber || (row as unknown as { block_number: number }).block_number),
          redeemedAt: Number(row.redeemedAt || (row as unknown as { redeemed_at: number }).redeemed_at),
        };
      }
    } catch (err: unknown) {
      console.error("D1 getRedemptionRecord error:", err);
    }
  }

  const kv = env.PAYMENT_KV || env.PAYMENTS_KV;
  if (kv) {
    try {
      const key = getKvKey(network, normalizedHash);
      const data = await kv.get(key);
      if (data) {
        return JSON.parse(data) as RedemptionRecord;
      }
    } catch (err: unknown) {
      console.error("KV getRedemptionRecord error:", err);
    }
  }

  return null;
}
