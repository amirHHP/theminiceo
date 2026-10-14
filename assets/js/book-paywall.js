/**
 * Client-Side Controller for Decentralized Crypto Paywall
 * Handles network selection, dynamic QR code generation, Web3 transfers,
 * transaction hash verification, and polling for block confirmations.
 */
(function () {
  'use strict';

  const STORE_WALLET = "0x4370D6c7A90A2f1d57C9788233792152A95204C7";
  const DEFAULT_PRICE = "5.00";

  const NETWORKS = {
    bsc: {
      id: "bsc",
      name: "BNB Smart Chain (BEP-20)",
      nameFa: "بی‌ان‌بی چین (BEP-20) - کمترین کارمزد",
      chainIdHex: "0x38",
      usdtContract: "0x55d398326f99059ff775485246999027b3197955",
      decimals: 18,
      minConfirmations: 3,
    },
    polygon: {
      id: "polygon",
      name: "Polygon PoS (POL)",
      nameFa: "پالیگان (Polygon PoS) - سریع و پایدار",
      chainIdHex: "0x89",
      usdtContract: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
      decimals: 6,
      minConfirmations: 10,
    },
    arbitrum: {
      id: "arbitrum",
      name: "Arbitrum One (L2)",
      nameFa: "آربیتروم (Arbitrum One) - لایه دوم اتریوم",
      chainIdHex: "0xa4b1",
      usdtContract: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
      decimals: 6,
      minConfirmations: 2,
    },
  };

  const I18N = {
    fa: {
      copied: "کپی شد!",
      copyAddr: "کپی آدرس",
      verifying: "در حال استعلام از گره‌های بلاکچین...",
      pending: "تراکنش روی شبکه ارسال شده و در انتظار ثبت در بلاک است. سیستم تا چند ثانیه دیگر مجدداً وضعیت را بررسی می‌کند...",
      confirmed: "پرداخت ۵ تتر با موفقیت تأیید شد! فایل برای دانلود آماده است و نسخه پشتیبان به ایمیل ارسال شد.",
      downloadNow: "دانلود نسخه کامل کتاب (PDF)",
      invalidEmail: "لطفاً یک آدرس ایمیل معتبر وارد کنید.",
      invalidTxHash: "شناسه تراکنش باید یک هش معتبر هگزادسیمال با فرمت 0x باشد (۶۶ کاراکتر).",
      web3NotDetected: "کیف‌پول وب۳ (مانند متامسک) شناسایی نشد. لطفاً مبلغ را دستی انتقال داده و شناسه تراکنش را ثبت فرمایید.",
      web3Error: "خطا در برقراری ارتباط با کیف‌پول:",
      errors: {
        TRANSACTION_NOT_FOUND: "تراکنش روی این شبکه یافت نشد. لطفاً از نهایی شدن تراکنش و انتخاب شبکه درست اطمینان حاصل کنید.",
        TRANSACTION_FAILED: "تراکنش در بلاکچین ناموفق (Reverted) شده است.",
        TRANSACTION_ALREADY_REDEEMED: "این تراکنش قبلاً مصرف شده است و امکان استفاده مجدد ندارد.",
        INSUFFICIENT_AMOUNT: "مبلغ دریافتی کمتر از ۵ تتر است.",
        WRONG_RECIPIENT: "آدرس کیف‌پول مقصد با آدرس فروشگاه مطابقت ندارد.",
        INVALID_TOKEN_CONTRACT: "توکن انتقال یافته، قرارداد رسمی تتر (USDT) روی این شبکه نیست.",
        UNSUPPORTED_NETWORK: "شبکه انتخاب شده پشتیبانی نمی‌شود.",
        RATE_LIMIT_EXCEEDED: "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً کمی بعد تلاش کنید.",
        RPC_CONNECTION_FAILURE: "اختلال موقت در اتصال به نودهای شبکه بلاکچین. سیستم مجدداً تلاش خواهد کرد.",
      },
    },
    en: {
      copied: "Copied!",
      copyAddr: "Copy Address",
      verifying: "Querying blockchain RPC nodes...",
      pending: "Transaction detected. Waiting for block confirmations (auto-retrying in seconds)...",
      confirmed: "Payment of 5 USDT verified successfully! File is ready for download and a backup link was emailed.",
      downloadNow: "Download Full Book (PDF)",
      invalidEmail: "Please provide a valid email address.",
      invalidTxHash: "Transaction hash must be a valid 0x-prefixed 66-character hex string.",
      web3NotDetected: "No Web3 wallet (e.g. MetaMask) detected. Please transfer manually and paste the TxHash.",
      web3Error: "Web3 wallet error:",
      errors: {
        TRANSACTION_NOT_FOUND: "Transaction not found on this chain. Ensure the transaction is mined and correct network is chosen.",
        TRANSACTION_FAILED: "Transaction was reverted on-chain.",
        TRANSACTION_ALREADY_REDEEMED: "This transaction hash has already been redeemed.",
        INSUFFICIENT_AMOUNT: "Transferred amount is less than 5 USDT.",
        WRONG_RECIPIENT: "Recipient address does not match the store wallet.",
        INVALID_TOKEN_CONTRACT: "Transferred token is not genuine USDT on this network.",
        UNSUPPORTED_NETWORK: "The selected network is not supported.",
        RATE_LIMIT_EXCEEDED: "Too many requests. Please wait a moment.",
        RPC_CONNECTION_FAILURE: "Temporary RPC connectivity issue. Retrying...",
      },
    },
  };

  function initPaywall(container) {
    if (container.dataset.paywallInitialized) return;
    container.dataset.paywallInitialized = "true";

    const lang = container.dataset.lang === "en" ? "en" : "fa";
    const t = I18N[lang];
    const bookId = container.dataset.bookId || "book";
    const storeWallet = container.dataset.storeWallet || STORE_WALLET;

    const networkSelect = container.querySelector(".js-paywall-network");
    const walletDisplay = container.querySelector(".js-paywall-wallet");
    const copyBtn = container.querySelector(".js-paywall-copy");
    const qrBox = container.querySelector(".js-paywall-qr");
    const emailInput = container.querySelector(".js-paywall-email");
    const txInput = container.querySelector(".js-paywall-tx");
    const verifyBtn = container.querySelector(".js-paywall-verify");
    const web3Btn = container.querySelector(".js-paywall-web3");
    const noticeBox = container.querySelector(".js-paywall-notice");
    const successBox = container.querySelector(".js-paywall-success");
    const downloadCta = container.querySelector(".js-paywall-download-cta");

    let isPolling = false;
    let pollAttempts = 0;
    const MAX_POLLS = 15;

    // Render QR Code
    function updateQr() {
      if (!qrBox) return;
      if (window.PaywallQR && typeof window.PaywallQR.generateQrSvg === "function") {
        qrBox.innerHTML = window.PaywallQR.generateQrSvg(storeWallet, { size: 160 });
      } else {
        qrBox.innerHTML = `<div style="font-family:monospace;font-size:10px;word-break:break-all;padding:10px;">${storeWallet}</div>`;
      }
    }

    updateQr();

    // Copy Wallet Address
    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(storeWallet).then(() => {
            const originalText = copyBtn.innerText;
            copyBtn.innerText = t.copied;
            setTimeout(() => {
              copyBtn.innerText = originalText;
            }, 2000);
          });
        }
      });
    }

    // Notice display helper
    function showNotice(message, type = "error") {
      if (!noticeBox) return;
      noticeBox.style.display = "flex";
      noticeBox.className = `js-paywall-notice paywall-notice paywall-notice-${type}`;
      noticeBox.innerHTML = message;
    }

    function clearNotice() {
      if (!noticeBox) return;
      noticeBox.style.display = "none";
      noticeBox.innerHTML = "";
    }

    // Web3 One-Click Payment
    if (web3Btn) {
      web3Btn.addEventListener("click", async function () {
        if (!window.ethereum) {
          showNotice(t.web3NotDetected, "warning");
          return;
        }

        const netKey = networkSelect ? networkSelect.value : "bsc";
        const net = NETWORKS[netKey] || NETWORKS.bsc;

        try {
          // 1. Request accounts
          const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
          if (!accounts || accounts.length === 0) return;

          // 2. Switch to selected network
          try {
            await window.ethereum.request({
              method: "wallet_switchEthereumChain",
              params: [{ chainId: net.chainIdHex }],
            });
          } catch (switchErr) {
            console.warn("Chain switch note:", switchErr);
          }

          // 3. Encode ERC20 transfer(address, uint256)
          // Selector for transfer(address,uint256) is 0xa9059cbb
          const cleanRecipient = storeWallet.toLowerCase().replace("0x", "").padStart(64, "0");
          // Calculate raw amount (5 USDT = 5 * 10^decimals)
          const rawAmount = (BigInt(5) * BigInt(10) ** BigInt(net.decimals)).toString(16).padStart(64, "0");
          const callData = "0xa9059cbb" + cleanRecipient + rawAmount;

          showNotice(t.verifying, "warning");

          const txHash = await window.ethereum.request({
            method: "eth_sendTransaction",
            params: [
              {
                from: accounts[0],
                to: net.usdtContract,
                data: callData,
              },
            ],
          });

          if (txHash && txInput) {
            txInput.value = txHash;
            // Automatically trigger verification
            handleVerification();
          }
        } catch (err) {
          console.error("Web3 payment error:", err);
          showNotice(`${t.web3Error} ${err.message || err}`, "error");
        }
      });
    }

    // Submit & Verification Handler
    async function handleVerification() {
      if (isPolling && pollAttempts > 0) {
        // already in polling loop
      } else {
        clearNotice();
      }

      const email = emailInput ? emailInput.value.trim() : "";
      const txHash = txInput ? txInput.value.trim() : "";
      const network = networkSelect ? networkSelect.value : "bsc";

      if (!email || !email.includes("@")) {
        showNotice(t.invalidEmail, "error");
        return;
      }

      if (!txHash || !/^0x[a-fA-F0-9]{64}$/.test(txHash)) {
        showNotice(t.invalidTxHash, "error");
        return;
      }

      if (verifyBtn) {
        verifyBtn.disabled = true;
        verifyBtn.innerHTML = `<span class="paywall-spinner"></span> <span>${t.verifying}</span>`;
      }

      try {
        const workerBase = "https://theminiceo-paywall.ah-hosseini1372.workers.dev";
        const verifyEndpoint = window.PAYWALL_API_URL || (window.location.pathname.startsWith("/api") ? "/api/verify-payment" : `${workerBase}/api/verify-payment`);
        const res = await fetch(verifyEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            network: network,
            txHash: txHash,
            bookId: bookId,
            email: email,
          }),
        });

        const data = await res.json().catch(() => ({}));

        if (res.status === 200 && data.success) {
          // Success!
          isPolling = false;
          clearNotice();
          if (noticeBox) noticeBox.style.display = "none";

          if (successBox) {
            successBox.style.display = "block";
            const msgEl = successBox.querySelector(".js-paywall-success-msg");
            if (msgEl) msgEl.innerText = t.confirmed;
          }

          if (downloadCta && data.downloadUrl) {
            downloadCta.href = data.downloadUrl;
            downloadCta.style.display = "inline-flex";
          }

          // Hide input form
          const formCol = container.querySelector(".js-paywall-form-col");
          if (formCol) formCol.style.display = "none";
          const qrCol = container.querySelector(".js-paywall-qr-col");
          if (qrCol) qrCol.style.display = "none";

          return;
        }

        if (res.status === 202) {
          // Pending confirmations -> auto poll
          showNotice(
            `<span class="paywall-spinner" style="border-top-color:#d97706;border-color:rgba(217,119,6,0.3)"></span> <span>${t.pending}</span>`,
            "warning"
          );

          if (pollAttempts < MAX_POLLS) {
            isPolling = true;
            pollAttempts++;
            setTimeout(handleVerification, 4000);
            return;
          }
        }

        // Error handling
        isPolling = false;
        pollAttempts = 0;
        const errKey = data.error;
        const errMsg = (t.errors && t.errors[errKey]) || data.message || `Error (${res.status})`;
        showNotice(errMsg, "error");
      } catch (networkErr) {
        console.error("Payment verification network error:", networkErr);
        showNotice(t.errors.RPC_CONNECTION_FAILURE, "error");
      } finally {
        if (!isPolling && verifyBtn) {
          verifyBtn.disabled = false;
          verifyBtn.innerHTML = `<span>${lang === "en" ? "Verify Payment & Unlock" : "تأیید پرداخت و باز کردن دانلود"}</span>`;
        }
      }
    }

    if (verifyBtn) {
      verifyBtn.addEventListener("click", handleVerification);
    }
  }

  // Auto-init on page load
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      document.querySelectorAll(".js-paywall-container").forEach(initPaywall);
    });
  } else {
    document.querySelectorAll(".js-paywall-container").forEach(initPaywall);
  }
})();
