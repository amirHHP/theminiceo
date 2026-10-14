/**
 * Persistent Replay Protection
 * Prevents double-spending of transaction hashes via Cloudflare D1 & KV
 */
/**
 * Key format for KV storage
 */
export function getKvKey(network, txHash) {
    return `tx:${network.toLowerCase()}:${txHash.toLowerCase()}`;
}
/**
 * Checks whether a transaction hash has already been redeemed in D1 or KV.
 */
export async function isTransactionRedeemed(txHash, network, env) {
    const normalizedHash = txHash.toLowerCase().trim();
    const normalizedNetwork = network.toLowerCase().trim();
    // 1. Check Cloudflare D1 (strongly consistent on primary)
    if (env.DB) {
        try {
            const existing = await env.DB.prepare("SELECT tx_hash FROM redeemed_transactions WHERE tx_hash = ?")
                .bind(normalizedHash)
                .first();
            if (existing) {
                return true;
            }
        }
        catch (err) {
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
        }
        catch (err) {
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
export async function recordRedemption(record, env) {
    const normalizedHash = record.txHash.toLowerCase().trim();
    const normalizedNetwork = record.network.toLowerCase().trim();
    const redeemedAt = record.redeemedAt ?? Date.now();
    const fullRecord = {
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
            await env.DB.prepare(`INSERT INTO redeemed_transactions
          (tx_hash, network, book_id, email, sender_address, amount_raw, block_number, redeemed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)`)
                .bind(fullRecord.txHash, fullRecord.network, fullRecord.bookId, fullRecord.email, fullRecord.senderAddress, fullRecord.amountRaw, fullRecord.blockNumber, fullRecord.redeemedAt)
                .run();
        }
        catch (err) {
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
        }
        catch (err) {
            console.error("Failed to write record to KV:", err);
        }
    }
    return { success: true };
}
/**
 * Retrieves full redemption details by txHash
 */
export async function getRedemptionRecord(txHash, network, env) {
    const normalizedHash = txHash.toLowerCase().trim();
    if (env.DB) {
        try {
            const row = await env.DB.prepare("SELECT tx_hash, network, book_id, email, sender_address, amount_raw, block_number, redeemed_at FROM redeemed_transactions WHERE tx_hash = ?")
                .bind(normalizedHash)
                .first();
            if (row) {
                return {
                    txHash: row.txHash || row.tx_hash,
                    network: row.network,
                    bookId: row.bookId || row.book_id,
                    email: row.email,
                    senderAddress: row.senderAddress || row.sender_address,
                    amountRaw: row.amountRaw || row.amount_raw,
                    blockNumber: Number(row.blockNumber || row.block_number),
                    redeemedAt: Number(row.redeemedAt || row.redeemed_at),
                };
            }
        }
        catch (err) {
            console.error("D1 getRedemptionRecord error:", err);
        }
    }
    const kv = env.PAYMENT_KV || env.PAYMENTS_KV;
    if (kv) {
        try {
            const key = getKvKey(network, normalizedHash);
            const data = await kv.get(key);
            if (data) {
                return JSON.parse(data);
            }
        }
        catch (err) {
            console.error("KV getRedemptionRecord error:", err);
        }
    }
    return null;
}
