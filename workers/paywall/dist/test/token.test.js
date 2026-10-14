import { test, describe, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { generateDownloadToken, verifyDownloadToken, checkAndIncrementDownloadLimit, resetDownloadCounters, base64UrlEncode, base64UrlDecode, } from "../src/token.js";
describe("Web Crypto HMAC Download Token Engine", () => {
    const secret = "test-secret-key-32-bytes-long-string-value";
    const bookData = {
        bookId: "the-lean-startup",
        filename: "The_Lean_Startup.pdf",
        txHash: "0x" + "a".repeat(64),
        email: "user@example.com",
        network: "bsc",
    };
    beforeEach(() => {
        resetDownloadCounters();
    });
    test("Base64Url encoding/decoding round-trip", () => {
        const raw = "Hello, Web3 Crypto Paywall! +/=";
        const encoded = base64UrlEncode(raw);
        assert.ok(!encoded.includes("+"));
        assert.ok(!encoded.includes("/"));
        assert.ok(!encoded.includes("="));
        const decodedBytes = base64UrlDecode(encoded);
        const decodedStr = new TextDecoder().decode(decodedBytes);
        assert.equal(decodedStr, raw);
    });
    test("Generates and verifies valid token", async () => {
        const { token, expiresAt } = await generateDownloadToken(bookData, secret, 7200);
        assert.ok(token);
        assert.ok(token.includes("."));
        assert.ok(expiresAt > Math.floor(Date.now() / 1000));
        const verification = await verifyDownloadToken(token, secret);
        assert.equal(verification.valid, true);
        assert.equal(verification.status, 200);
        assert.ok(verification.payload);
        assert.equal(verification.payload.bookId, "the-lean-startup");
        assert.equal(verification.payload.email, "user@example.com");
        assert.equal(verification.payload.network, "bsc");
    });
    test("Rejects token with incorrect secret / tampered signature", async () => {
        const { token } = await generateDownloadToken(bookData, secret, 7200);
        const res = await verifyDownloadToken(token, "wrong-secret-key");
        assert.equal(res.valid, false);
        assert.equal(res.status, 403);
        assert.equal(res.error, "INVALID_SIGNATURE");
    });
    test("Rejects tampered payload modifying bookId", async () => {
        const { token } = await generateDownloadToken(bookData, secret, 7200);
        const [payloadB64, sigB64] = token.split(".");
        const decoded = JSON.parse(new TextDecoder().decode(base64UrlDecode(payloadB64)));
        decoded.bookId = "expensive-book-id";
        const tamperedPayloadB64 = base64UrlEncode(JSON.stringify(decoded));
        const tamperedToken = `${tamperedPayloadB64}.${sigB64}`;
        const res = await verifyDownloadToken(tamperedToken, secret);
        assert.equal(res.valid, false);
        assert.equal(res.status, 403);
        assert.equal(res.error, "INVALID_SIGNATURE");
    });
    test("Rejects expired token (+1 second, past timestamp)", async () => {
        const now = 1790000000;
        // Generate token expiring at now
        const { token } = await generateDownloadToken(bookData, secret, 7200);
        // Verified 7201 seconds later
        const res = await verifyDownloadToken(token, secret, Math.floor(Date.now() / 1000) + 7201);
        assert.equal(res.valid, false);
        assert.equal(res.status, 410);
        assert.equal(res.error, "TOKEN_EXPIRED");
    });
    test("Rejects malformed tokens with 400 MALFORMED_TOKEN / MISSING_TOKEN", async () => {
        const emptyRes = await verifyDownloadToken("", secret);
        assert.equal(emptyRes.valid, false);
        assert.equal(emptyRes.status, 400);
        assert.equal(emptyRes.error, "MISSING_TOKEN");
        const noDotRes = await verifyDownloadToken("invalidtokenwithoutdots", secret);
        assert.equal(noDotRes.valid, false);
        assert.equal(noDotRes.status, 400);
        assert.equal(noDotRes.error, "MALFORMED_TOKEN");
        const multiDotRes = await verifyDownloadToken("a.b.c", secret);
        assert.equal(multiDotRes.valid, false);
        assert.equal(multiDotRes.status, 400);
        assert.equal(multiDotRes.error, "MALFORMED_TOKEN");
    });
    test("Download attempt limiter allows 5 downloads and blocks 6th with 429", async () => {
        const txHash = "0x" + "1234".repeat(16);
        for (let attempt = 1; attempt <= 5; attempt++) {
            const check = await checkAndIncrementDownloadLimit(txHash, undefined, 5);
            assert.equal(check.allowed, true, `Attempt ${attempt} must be allowed`);
            assert.equal(check.count, attempt);
        }
        // 6th attempt must be rejected
        const blockedCheck = await checkAndIncrementDownloadLimit(txHash, undefined, 5);
        assert.equal(blockedCheck.allowed, false, "6th attempt must be blocked");
        assert.equal(blockedCheck.count, 5);
    });
});
