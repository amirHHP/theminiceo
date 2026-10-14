/**
 * Resend Email Dispatch Engine & Bilingual Templates
 * Sends backup download link and on-chain transaction receipt
 */
import { DEFAULT_STORE_WALLET } from "./config.js";
/**
 * Builds responsive bilingual HTML and plaintext email payloads
 */
export function generateEmailPayload(options) {
    const storeWallet = options.storeWallet || options.env?.STORE_WALLET_ADDRESS || DEFAULT_STORE_WALLET;
    const supportEmail = options.env?.SUPPORT_EMAIL || "support@theminiceo.ir";
    const from = options.env?.EMAIL_FROM || "TheMiniCEO Books <books@theminiceo.ir>";
    const title = options.bookTitle || options.bookId;
    const networkName = options.network ? options.network.toUpperCase() : "EVM";
    const amount = options.amountUsdt || "5.00";
    const subject = `Your Book Download: ${title} (${options.bookId}) - TheMiniCEO`;
    const html = `<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${subject}</title>
</head>
<body style="margin:0;padding:0;background-color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#f8fafc;">
  <table role="presentation" width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color:#0f172a;padding:24px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width:560px;background-color:#1e293b;border-radius:12px;overflow:hidden;border:1px solid #334155;box-shadow:0 10px 25px -5px rgba(0,0,0,0.5);" cellpadding="0" cellspacing="0">
          <!-- Header Banner -->
          <tr>
            <td style="padding:28px 24px 20px;background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);border-bottom:1px solid #334155;text-align:center;">
              <h1 style="margin:0;font-size:22px;font-weight:700;color:#f8fafc;letter-spacing:-0.5px;">TheMiniCEO Books</h1>
              <p style="margin:6px 0 0;font-size:13px;color:#94a3b8;">Decentralized Crypto Paywall</p>
            </td>
          </tr>

          <!-- Confirmation Message (English & Persian) -->
          <tr>
            <td style="padding:24px 24px 12px;">
              <h2 style="margin:0 0 10px;font-size:18px;color:#38bdf8;font-weight:600;">Payment Verified Successfully!</h2>
              <p style="margin:0 0 12px;font-size:14px;line-height:1.6;color:#e2e8f0;">
                Thank you for purchasing <strong>${title}</strong>. Your payment has been confirmed on-chain and your book is ready for download.
              </p>
              <div style="direction:rtl;text-align:right;background-color:#0f172a;border-radius:8px;padding:12px 16px;margin-bottom:16px;border:1px solid #334155;">
                <p style="margin:0;font-size:13px;line-height:1.6;color:#cbd5e1;">
                  با تشکر از خرید شما، پرداخت ارزی شما با موفقیت تایید شد و فایل کتاب آماده دانلود است.
                </p>
              </div>
            </td>
          </tr>

          <!-- Book Summary Card -->
          <tr>
            <td style="padding:0 24px 16px;">
              <div style="background-color:#0f172a;border-radius:8px;padding:16px;border:1px solid #334155;">
                <div style="font-size:12px;text-transform:uppercase;color:#94a3b8;font-weight:600;letter-spacing:0.5px;margin-bottom:6px;">Book Details</div>
                <div style="font-size:16px;color:#f8fafc;font-weight:600;">${title}</div>
                <div style="font-size:13px;color:#94a3b8;margin-top:4px;">Format: PDF Digital Edition</div>
              </div>
            </td>
          </tr>

          <!-- Download CTA Button -->
          <tr>
            <td style="padding:8px 24px 20px;text-align:center;">
              <a href="${options.downloadUrl}" style="display:inline-block;background-color:#2563eb;color:#ffffff;font-size:15px;font-weight:600;text-decoration:none;padding:14px 32px;border-radius:8px;box-shadow:0 4px 12px rgba(37,99,235,0.35);">
                Download Book PDF / دریافت فایل کتاب
              </a>
            </td>
          </tr>

          <!-- Expiration Warning Notice -->
          <tr>
            <td style="padding:0 24px 20px;">
              <div style="background-color:rgba(234,179,8,0.1);border-left:4px solid #eab308;padding:12px 14px;border-radius:0 6px 6px 0;">
                <p style="margin:0;font-size:13px;line-height:1.5;color:#fde047;">
                  ⚠️ <strong>Notice:</strong> For security, this direct download link is valid for <strong>2 hours</strong> (up to 5 download attempts). Please save the PDF file to your local device now.
                </p>
                <p style="margin:6px 0 0;font-size:12px;line-height:1.5;color:#fef08a;direction:rtl;text-align:right;">
                  توجه: این لینک اختصاصی به مدت ۲ ساعت معتبر است (حداکثر ۵ بار دانلود). لطفاً فایل را در دستگاه خود ذخیره نمایید.
                </p>
              </div>
            </td>
          </tr>

          <!-- Transaction Receipt -->
          <tr>
            <td style="padding:0 24px 24px;">
              <div style="border-top:1px solid #334155;padding-top:16px;">
                <div style="font-size:12px;text-transform:uppercase;color:#94a3b8;font-weight:600;letter-spacing:0.5px;margin-bottom:8px;">Payment Receipt</div>
                <table width="100%" style="font-size:12px;color:#cbd5e1;line-height:1.8;">
                  <tr>
                    <td style="color:#94a3b8;">Network:</td>
                    <td align="right" style="font-family:monospace;">${networkName}</td>
                  </tr>
                  <tr>
                    <td style="color:#94a3b8;">Amount:</td>
                    <td align="right" style="font-family:monospace;font-weight:bold;color:#38bdf8;">${amount} USDT</td>
                  </tr>
                  <tr>
                    <td style="color:#94a3b8;">Store Wallet:</td>
                    <td align="right" style="font-family:monospace;word-break:break-all;">${storeWallet}</td>
                  </tr>
                  <tr>
                    <td style="color:#94a3b8;">Tx Hash:</td>
                    <td align="right" style="font-family:monospace;word-break:break-all;">${options.txHash}</td>
                  </tr>
                </table>
              </div>
            </td>
          </tr>

          <!-- Footer & Support Contact -->
          <tr>
            <td style="padding:16px 24px 24px;background-color:#0f172a;border-top:1px solid #334155;text-align:center;font-size:12px;color:#64748b;line-height:1.6;">
              <p style="margin:0 0 6px;">
                Did your link expire before saving? Contact <a href="mailto:${supportEmail}" style="color:#38bdf8;text-decoration:none;">${supportEmail}</a> with your transaction hash.
              </p>
              <p style="margin:0;direction:rtl;">
                پشتیبانی: <a href="mailto:${supportEmail}" style="color:#38bdf8;text-decoration:none;">${supportEmail}</a>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>`;
    const text = `TheMiniCEO Books - Payment Confirmation

Thank you for purchasing ${title} (${options.bookId}).
Your payment has been verified on-chain.

Download link: ${options.downloadUrl}
Note: This link is valid for 2 hours (up to 5 downloads). Please download and save the file to your device now.

Payment Receipt:
- Network: ${networkName}
- Amount: ${amount} USDT
- Store Wallet: ${storeWallet}
- Tx Hash: ${options.txHash}

Did your link expire? Contact ${supportEmail} with your transaction hash.
پشتیبانی: ${supportEmail}
`;
    return {
        from,
        to: [options.to],
        subject,
        html,
        text,
    };
}
/**
 * Sends transactional backup email via Resend REST API
 * Gracefully falls back if RESEND_API_KEY is not configured
 */
export async function sendBackupEmail(options) {
    // 1. Native Cloudflare Workers Send Email (zero external dependencies)
    if (options.env?.EMAIL && typeof options.env.EMAIL.send === "function") {
        try {
            let EmailMsgClass;
            try {
                const cfEmailModule = await import("cloudflare:email");
                EmailMsgClass = cfEmailModule.EmailMessage;
            }
            catch {
                EmailMsgClass = globalThis.EmailMessage;
            }
            if (EmailMsgClass) {
                const payload = generateEmailPayload(options);
                const fromAddress = "books@theminiceo.ir";
                const subjectEncoded = `=?utf-8?B?${Buffer.from(payload.subject).toString("base64")}?=`;
                const rawMime = [
                    `From: TheMiniCEO Books <${fromAddress}>`,
                    `To: <${options.to}>`,
                    `Subject: ${subjectEncoded}`,
                    `MIME-Version: 1.0`,
                    `Content-Type: text/html; charset=utf-8`,
                    `Content-Transfer-Encoding: 8bit`,
                    ``,
                    payload.html,
                ].join("\r\n");
                const message = new EmailMsgClass(fromAddress, options.to, rawMime);
                await options.env.EMAIL.send(message);
                console.log(`[Email] Native Cloudflare email dispatched to ${options.to} for ${options.bookId}`);
                return { success: true, id: `cf_${Date.now()}` };
            }
        }
        catch (cfErr) {
            console.warn("[Email] Native Cloudflare send failed, checking Resend fallback:", cfErr);
        }
    }
    // 2. Resend REST API Fallback
    const apiKey = options.env?.RESEND_API_KEY?.trim();
    // Graceful fallback when Resend is not configured (e.g. during local tests)
    if (!apiKey) {
        console.log(`[Email] RESEND_API_KEY not configured. Simulating email dispatch for ${options.bookId} to ${options.to}`);
        return {
            success: true,
            simulated: true,
            id: `sim_${Date.now()}_${Math.random().toString(36).substring(2, 8)}`,
        };
    }
    const payload = generateEmailPayload(options);
    try {
        const response = await fetch("https://api.resend.com/emails", {
            method: "POST",
            headers: {
                Authorization: `Bearer ${apiKey}`,
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`[Email] Resend API error (${response.status}): ${errorText}`);
            return { success: false, error: errorText };
        }
        const result = (await response.json());
        return { success: true, id: result?.id };
    }
    catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        console.error("[Email] Exception during Resend email dispatch:", errorMsg);
        return { success: false, error: errorMsg };
    }
}
