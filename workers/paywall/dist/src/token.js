/**
 * Web Crypto HMAC-SHA256 Expiring Download Token Engine
 * Zero external dependencies, pure native crypto.subtle
 */
export function base64UrlEncode(input) {
    let bytes;
    if (typeof input === "string") {
        bytes = new TextEncoder().encode(input);
    }
    else {
        bytes = input;
    }
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    const base64 = btoa(binary);
    return base64.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
export function base64UrlDecode(str) {
    let base64 = str.replace(/-/g, "+").replace(/_/g, "/");
    while (base64.length % 4 !== 0) {
        base64 += "=";
    }
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes;
}
function getRandomNonce(length = 12) {
    const bytes = new Uint8Array(Math.ceil(length / 2));
    crypto.getRandomValues(bytes);
    let hex = "";
    for (let i = 0; i < bytes.length; i++) {
        hex += bytes[i].toString(16).padStart(2, "0");
    }
    return hex.slice(0, length);
}
/**
 * Creates an HMAC-SHA256 CryptoKey from string secret
 */
async function getHmacKey(secret) {
    const enc = new TextEncoder();
    return crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
}
/**
 * Generates a signed, URL-safe download token valid for 2 hours (7200s)
 */
export async function generateDownloadToken(data, secret, expirySeconds = 7200) {
    const now = Math.floor(Date.now() / 1000);
    const expiresAt = now + expirySeconds;
    const payload = {
        bookId: data.bookId,
        filename: data.filename,
        txHash: data.txHash.toLowerCase(),
        email: data.email,
        network: data.network.toLowerCase(),
        iat: now,
        exp: expiresAt,
        nonce: getRandomNonce(12),
    };
    const b64Payload = base64UrlEncode(JSON.stringify(payload));
    const hmacKey = await getHmacKey(secret);
    const sigBuffer = await crypto.subtle.sign("HMAC", hmacKey, new TextEncoder().encode(b64Payload));
    const b64Sig = base64UrlEncode(new Uint8Array(sigBuffer));
    const token = `${b64Payload}.${b64Sig}`;
    return { token, expiresAt };
}
const memoryDownloadCounters = new Map();
/**
 * Verifies a download token, ensuring valid HMAC signature and expiration
 */
export async function verifyDownloadToken(token, secret, nowTs) {
    if (!token || typeof token !== "string" || !token.trim()) {
        return { valid: false, error: "MISSING_TOKEN", status: 400 };
    }
    const parts = token.split(".");
    if (parts.length !== 2 || !parts[0] || !parts[1]) {
        return { valid: false, error: "MALFORMED_TOKEN", status: 400 };
    }
    const [b64Payload, b64Sig] = parts;
    try {
        const hmacKey = await getHmacKey(secret);
        let sigBytes;
        try {
            sigBytes = base64UrlDecode(b64Sig);
        }
        catch {
            return { valid: false, error: "MALFORMED_TOKEN", status: 400 };
        }
        const isValidSig = await crypto.subtle.verify("HMAC", hmacKey, sigBytes, new TextEncoder().encode(b64Payload));
        if (!isValidSig) {
            return { valid: false, error: "INVALID_SIGNATURE", status: 403 };
        }
        let payloadJson;
        let payload;
        try {
            payloadJson = new TextDecoder().decode(base64UrlDecode(b64Payload));
            payload = JSON.parse(payloadJson);
        }
        catch {
            return { valid: false, error: "MALFORMED_TOKEN", status: 400 };
        }
        const now = nowTs ?? Math.floor(Date.now() / 1000);
        if (payload.exp < now) {
            return { valid: false, error: "TOKEN_EXPIRED", payload, status: 410 };
        }
        return { valid: true, payload, status: 200 };
    }
    catch (err) {
        return { valid: false, error: "MALFORMED_TOKEN", status: 400 };
    }
}
/**
 * Checks and increments download attempt counter for a given transaction hash.
 * Enforces maximum 5 attempts per token via KV `dl_count:${txHash}`.
 */
export async function checkAndIncrementDownloadLimit(txHash, env, maxAttempts = 5) {
    const normHash = txHash.toLowerCase().trim();
    const kvKey = `dl_count:${normHash}`;
    const kv = env?.PAYMENT_KV || env?.PAYMENTS_KV;
    let currentCount = 0;
    if (kv) {
        try {
            const val = await kv.get(kvKey);
            if (val !== null) {
                currentCount = parseInt(val, 10) || 0;
            }
        }
        catch (err) {
            console.error("[Token] KV error reading download count:", err);
            currentCount = memoryDownloadCounters.get(normHash) || 0;
        }
    }
    else {
        currentCount = memoryDownloadCounters.get(normHash) || 0;
    }
    if (currentCount >= maxAttempts) {
        return { allowed: false, count: currentCount, maxAttempts };
    }
    const newCount = currentCount + 1;
    if (kv) {
        try {
            await kv.put(kvKey, String(newCount), { expirationTtl: 86400 });
        }
        catch (err) {
            console.error("[Token] KV error writing download count:", err);
        }
    }
    memoryDownloadCounters.set(normHash, newCount);
    return { allowed: true, count: newCount, maxAttempts };
}
/**
 * Clears in-memory download counters (used for test isolation)
 */
export function resetDownloadCounters() {
    memoryDownloadCounters.clear();
}
