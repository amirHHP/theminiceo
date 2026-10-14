import { test, describe } from "node:test";
import assert from "node:assert/strict";
import { generateEmailPayload, sendBackupEmail } from "../src/email.js";
import { DEFAULT_STORE_WALLET } from "../src/config.js";

describe("Resend Email Dispatch & Templates", () => {
  const sampleOptions = {
    to: "customer@example.com",
    bookId: "escaping-the-build-trap",
    bookTitle: "Escaping the Build Trap",
    downloadUrl: "https://theminiceo.ir/api/download?token=valid.download.token",
    txHash: "0x" + "a".repeat(64),
    network: "bsc",
    amountUsdt: "5.00",
    storeWallet: DEFAULT_STORE_WALLET,
  };

  test("generateEmailPayload generates valid Resend payload with bilingual content", () => {
    const payload = generateEmailPayload(sampleOptions);

    assert.deepEqual(payload.to, ["customer@example.com"]);
    assert.ok(payload.subject.includes("escaping-the-build-trap"));
    assert.ok(payload.subject.includes("Escaping the Build Trap"));

    // Verify HTML body
    assert.ok(payload.html.includes(sampleOptions.downloadUrl));
    assert.ok(payload.html.includes(DEFAULT_STORE_WALLET));
    assert.ok(payload.html.includes(sampleOptions.txHash));
    assert.ok(payload.html.includes("BSC"));
    assert.ok(payload.html.includes("5.00 USDT"));
    assert.ok(payload.html.includes("2 hours"));
    assert.ok(payload.html.includes("با تشکر از خرید شما"));
    assert.ok(payload.html.includes("support@theminiceo.ir"));

    // Verify Plaintext body
    assert.ok(payload.text.includes(sampleOptions.downloadUrl));
    assert.ok(payload.text.includes(sampleOptions.txHash));
    assert.ok(payload.text.includes("support@theminiceo.ir"));
  });

  test("sendBackupEmail gracefully simulates dispatch when RESEND_API_KEY is missing", async () => {
    const result = await sendBackupEmail({
      ...sampleOptions,
      env: {}, // No RESEND_API_KEY
    });

    assert.equal(result.success, true);
    assert.equal(result.simulated, true);
    assert.ok(result.id?.startsWith("sim_"));
  });

  test("sendBackupEmail dispatches to Resend API when RESEND_API_KEY is provided", async () => {
    const originalFetch = globalThis.fetch;
    const captured: { current: { url: string; headers: Headers; body: any } | null } = { current: null };

    globalThis.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === "string" ? input : input.toString();
      captured.current = {
        url,
        headers: new Headers(init?.headers),
        body: JSON.parse(init?.body as string),
      };

      return new Response(JSON.stringify({ id: "resend_email_id_98765" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    };

    try {
      const result = await sendBackupEmail({
        ...sampleOptions,
        env: {
          RESEND_API_KEY: "re_test_key_12345",
        },
      });

      assert.equal(result.success, true);
      assert.equal(result.id, "resend_email_id_98765");
      assert.ok(captured.current);
      assert.equal(captured.current.url, "https://api.resend.com/emails");
      assert.equal(captured.current.headers.get("Authorization"), "Bearer re_test_key_12345");
      assert.deepEqual(captured.current.body.to, ["customer@example.com"]);
    } finally {
      globalThis.fetch = originalFetch;
    }
  });

  test("sendBackupEmail handles Resend API errors gracefully without throwing", async () => {
    const originalFetch = globalThis.fetch;

    globalThis.fetch = async () => {
      return new Response(JSON.stringify({ message: "Invalid API key" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    };

    try {
      const result = await sendBackupEmail({
        ...sampleOptions,
        env: {
          RESEND_API_KEY: "re_invalid_key",
        },
      });

      assert.equal(result.success, false);
      assert.ok(result.error);
    } finally {
      globalThis.fetch = originalFetch;
    }
  });
});
