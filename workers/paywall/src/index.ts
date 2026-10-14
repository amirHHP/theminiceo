/**
 * Cloudflare Worker Entrypoint & API Router
 * Direct On-Chain Crypto Payment Verification Worker
 */

import {
  DEFAULT_DOWNLOAD_EXPIRY_SECONDS,
  DEFAULT_STORE_WALLET,
  DEFAULT_USDT_PRICE,
  getNetworkConfig,
  getPublicNetworksList,
  isValidTxHash,
} from "./config.js";
import { recordRedemption, type ReplayStorageEnv } from "./replay.js";
import {
  generateDownloadToken,
  verifyDownloadToken,
  checkAndIncrementDownloadLimit,
} from "./token.js";
import { fetchBookFromR2 } from "./storage.js";
import { sendBackupEmail } from "./email.js";
import { DIAGNOSTIC_ERRORS, verifyPaymentOnChain } from "./verifier.js";
import manifestData from "./manifest.json" with { type: "json" };

import { EvmRpcClient } from "./rpc.js";

export interface Env extends ReplayStorageEnv {
  STORE_WALLET_ADDRESS?: string;
  USDT_PRICE?: string;
  DOWNLOAD_HMAC_SECRET?: string;
  BASE_URL?: string;
  ALLOWED_ORIGIN?: string;
  CUSTOM_RPC_CLIENT?: EvmRpcClient;
  BOOKS_BUCKET?: R2Bucket;
  EMAIL?: SendEmail;
  RESEND_API_KEY?: string;
  EMAIL_FROM?: string;
  SUPPORT_EMAIL?: string;
}

export interface VerifyRequestBody {
  network?: string;
  txHash?: string;
  bookId?: string;
  email?: string;
}

interface BookManifestEntry {
  id: string;
  title: string;
  filename: string;
  format: string;
  sizeStr: string;
}

const manifest = manifestData as Record<string, BookManifestEntry>;

/**
 * Builds standard CORS headers
 */
export function getCorsHeaders(origin?: string | null, allowedOriginSetting?: string): Headers {
  const headers = new Headers();
  const allowOrigin = allowedOriginSetting || "*";
  headers.set("Access-Control-Allow-Origin", origin && allowedOriginSetting === origin ? origin : allowOrigin);
  headers.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization, Accept");
  headers.set("Access-Control-Max-Age", "86400");
  return headers;
}

/**
 * Responds with JSON payload and CORS headers
 */
function jsonResponse(data: unknown, status = 200, extraHeaders?: HeadersInit): Response {
  const headers = new Headers(extraHeaders);
  headers.set("Content-Type", "application/json; charset=utf-8");
  return new Response(JSON.stringify(data), {
    status,
    headers,
  });
}

/**
 * Looks up book metadata from bundled manifest or creates fallback
 */
function resolveBook(bookId: string): BookManifestEntry {
  const normalizedId = bookId.trim().toLowerCase();
  if (manifest[normalizedId]) {
    return manifest[normalizedId];
  }
  // Check without hyphens or exact match
  if (manifest[bookId]) {
    return manifest[bookId];
  }
  // Fallback representation
  return {
    id: bookId,
    title: bookId.replace(/[-_]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
    filename: `${bookId}.pdf`,
    format: "PDF",
    sizeStr: "2.0 MB",
  };
}

/**
 * Main Fetch Handler for Cloudflare Worker
 */
export async function handleRequest(request: Request, env: Env, ctx?: ExecutionContext): Promise<Response> {
  const url = new URL(request.url);
  const pathname = url.pathname.replace(/\/+$/, "") || "/";
  const origin = request.headers.get("Origin");
  const corsHeaders = getCorsHeaders(origin, env.ALLOWED_ORIGIN);

  // 1. Handle CORS Preflight (OPTIONS)
  if (request.method === "OPTIONS") {
    return new Response(null, {
      status: 204,
      headers: corsHeaders,
    });
  }

  // 2. GET /api/config — Exposes payment parameters, networks, pricing
  if (request.method === "GET" && (pathname === "/api/config" || pathname === "/config")) {
    const responsePayload = {
      success: true,
      pricing: {
        amount: env.USDT_PRICE || DEFAULT_USDT_PRICE,
        currency: "USDT",
      },
      storeWallet: env.STORE_WALLET_ADDRESS || DEFAULT_STORE_WALLET,
      networks: getPublicNetworksList(),
      downloadExpirySeconds: DEFAULT_DOWNLOAD_EXPIRY_SECONDS,
      supportEmail: "support@theminiceo.ir",
    };

    corsHeaders.set("Cache-Control", "public, max-age=300, s-maxage=600");
    return jsonResponse(responsePayload, 200, corsHeaders);
  }

  // 3. GET /api/download — Streams PDF from R2 via Expiring HMAC Download Token
  if (request.method === "GET" && (pathname === "/api/download" || pathname === "/download")) {
    const token = url.searchParams.get("token");
    if (!token || !token.trim()) {
      return jsonResponse(
        {
          success: false,
          error: "MISSING_TOKEN",
          message: "Download token is missing.",
        },
        400,
        corsHeaders
      );
    }

    const hmacSecret = env.DOWNLOAD_HMAC_SECRET || "paywall-secret-key-theminiceo-2026-prod";
    const verification = await verifyDownloadToken(token, hmacSecret);

    if (!verification.valid || !verification.payload) {
      if (verification.error === "MISSING_TOKEN") {
        return jsonResponse(
          {
            success: false,
            error: "MISSING_TOKEN",
            message: "Download token is missing.",
          },
          400,
          corsHeaders
        );
      }
      if (verification.error === "MALFORMED_TOKEN") {
        return jsonResponse(
          {
            success: false,
            error: "MALFORMED_TOKEN",
            message: "Download token is malformed.",
          },
          400,
          corsHeaders
        );
      }
      if (verification.error === "INVALID_SIGNATURE") {
        return jsonResponse(
          {
            success: false,
            error: "INVALID_SIGNATURE",
            message: "Token signature is invalid or has been tampered with.",
          },
          403,
          corsHeaders
        );
      }
      if (verification.error === "TOKEN_EXPIRED") {
        return jsonResponse(
          {
            success: false,
            error: "TOKEN_EXPIRED",
            message: "This download link expired after 2 hours. Please check your backup email or contact support.",
          },
          410,
          corsHeaders
        );
      }
      return jsonResponse(
        {
          success: false,
          error: verification.error || "INVALID_TOKEN",
          message: "Download token verification failed.",
        },
        verification.status || 400,
        corsHeaders
      );
    }

    // Enforce Download Attempt Rate Limiter (maximum 5 attempts per token)
    const limitCheck = await checkAndIncrementDownloadLimit(verification.payload.txHash, env, 5);
    if (!limitCheck.allowed) {
      return jsonResponse(
        {
          success: false,
          error: "DOWNLOAD_LIMIT_EXCEEDED",
          message: "Download attempt limit exceeded (maximum 5 attempts per token).",
        },
        429,
        corsHeaders
      );
    }

    // Stream PDF from Cloudflare R2 Bucket
    const book = resolveBook(verification.payload.bookId);
    const filename = verification.payload.filename || book.filename;
    const rangeHeader = request.headers.get("Range");

    const storageResponse = await fetchBookFromR2(env, filename, rangeHeader, {
      bookTitle: book.title,
      bookId: verification.payload.bookId,
    });

    if (storageResponse.status === 404) {
      return jsonResponse(
        {
          success: false,
          error: "FILE_NOT_FOUND",
          message: "The requested book file is not available in storage.",
        },
        404,
        corsHeaders
      );
    }

    // Attach CORS headers if origin is present
    for (const [key, val] of corsHeaders.entries()) {
      storageResponse.headers.set(key, val);
    }

    return storageResponse;
  }

  // 4. POST /api/verify-payment — Direct On-Chain Verification
  if (request.method === "POST" && (pathname === "/api/verify-payment" || pathname === "/verify-payment")) {
    let body: VerifyRequestBody;
    try {
      body = (await request.json()) as VerifyRequestBody;
    } catch {
      return jsonResponse(
        {
          success: false,
          error: "INVALID_JSON",
          message: "Request body must be a valid JSON object.",
        },
        400,
        corsHeaders
      );
    }

    // Harden input validation against type confusion
    const rawNetwork = body ? body.network : undefined;
    const rawTxHash = body ? body.txHash : undefined;
    const rawBookId = body ? body.bookId : undefined;
    const rawEmail = body ? body.email : undefined;

    if (typeof rawNetwork !== "string" || !rawNetwork.trim()) {
      return jsonResponse(
        {
          success: false,
          error: DIAGNOSTIC_ERRORS.UNSUPPORTED_NETWORK.code,
          message: "Network parameter is required.",
        },
        400,
        corsHeaders
      );
    }

    const network = rawNetwork.trim().toLowerCase();

    if (!getNetworkConfig(network)) {
      return jsonResponse(
        {
          success: false,
          error: DIAGNOSTIC_ERRORS.UNSUPPORTED_NETWORK.code,
          message: DIAGNOSTIC_ERRORS.UNSUPPORTED_NETWORK.message,
        },
        400,
        corsHeaders
      );
    }

    if (typeof rawTxHash !== "string" || !rawTxHash.trim()) {
      return jsonResponse(
        {
          success: false,
          error: DIAGNOSTIC_ERRORS.INVALID_TX_HASH_FORMAT.code,
          message: "Transaction hash parameter is required.",
        },
        400,
        corsHeaders
      );
    }

    const txHash = rawTxHash.trim();

    if (!isValidTxHash(txHash)) {
      return jsonResponse(
        {
          success: false,
          error: DIAGNOSTIC_ERRORS.INVALID_TX_HASH_FORMAT.code,
          message: DIAGNOSTIC_ERRORS.INVALID_TX_HASH_FORMAT.message,
        },
        400,
        corsHeaders
      );
    }

    if (typeof rawBookId !== "string" || !rawBookId.trim()) {
      return jsonResponse(
        {
          success: false,
          error: "BOOK_ID_REQUIRED",
          message: "Book identifier is required.",
        },
        400,
        corsHeaders
      );
    }

    const bookId = rawBookId.trim();

    if (typeof rawEmail !== "string" || !rawEmail.trim() || !rawEmail.includes("@")) {
      return jsonResponse(
        {
          success: false,
          error: "INVALID_EMAIL",
          message: "A valid email address is required.",
        },
        400,
        corsHeaders
      );
    }

    const email = rawEmail.trim();

    // Execute On-Chain Verification
    const storeWallet = env.STORE_WALLET_ADDRESS || DEFAULT_STORE_WALLET;
    const verification = await verifyPaymentOnChain(
      {
        network,
        txHash,
        storeWallet,
      },
      env,
      env.CUSTOM_RPC_CLIENT ? { customRpcClient: env.CUSTOM_RPC_CLIENT } : undefined
    );

    if (!verification.success || !verification.data) {
      return jsonResponse(
        {
          success: false,
          error: verification.error,
          message: verification.message,
        },
        verification.status,
        corsHeaders
      );
    }

    // Atomic Replay Registration in D1 / KV
    const replayRecord = await recordRedemption(
      {
        txHash: verification.data.txHash,
        network: verification.data.network,
        bookId,
        email,
        senderAddress: verification.data.senderAddress,
        amountRaw: verification.data.amountRaw,
        blockNumber: verification.data.blockNumber,
      },
      env
    );

    if (!replayRecord.success) {
      return jsonResponse(
        {
          success: false,
          error: DIAGNOSTIC_ERRORS.TRANSACTION_ALREADY_REDEEMED.code,
          message: DIAGNOSTIC_ERRORS.TRANSACTION_ALREADY_REDEEMED.message,
        },
        409,
        corsHeaders
      );
    }

    // Resolve Book Metadata & Generate Expiring Download Token
    const book = resolveBook(bookId);
    const hmacSecret = env.DOWNLOAD_HMAC_SECRET || "paywall-secret-key-theminiceo-2026-prod";
    const baseUrl = env.BASE_URL || "https://theminiceo.ir";

    const { token, expiresAt } = await generateDownloadToken(
      {
        bookId: book.id,
        filename: book.filename,
        txHash: verification.data.txHash,
        email,
        network: verification.data.network,
      },
      hmacSecret,
      DEFAULT_DOWNLOAD_EXPIRY_SECONDS
    );

    const downloadUrl = `${baseUrl}/api/download?token=${token}`;

    // Asynchronous and non-blocking Backup Email Dispatch in ctx.waitUntil
    const emailPromise = sendBackupEmail({
      to: email,
      bookId: book.id,
      bookTitle: book.title,
      downloadUrl,
      txHash: verification.data.txHash,
      network: verification.data.network,
      amountUsdt: verification.data.amountUsdt,
      storeWallet,
      env,
    }).catch((err) => {
      console.error("[Email] Background dispatch error:", err);
    });

    if (ctx && typeof ctx.waitUntil === "function") {
      ctx.waitUntil(emailPromise);
    }

    const responseData = {
      success: true,
      downloadUrl,
      expiresAt,
      expiresInSeconds: DEFAULT_DOWNLOAD_EXPIRY_SECONDS,
      book: {
        id: book.id,
        title: book.title,
        filename: book.filename,
        format: book.format,
        sizeStr: book.sizeStr,
      },
      txDetails: {
        network: verification.data.network,
        txHash: verification.data.txHash,
        amountUsdt: verification.data.amountUsdt,
        blockNumber: verification.data.blockNumber,
        confirmedAt: Math.floor(Date.now() / 1000),
      },
      emailDispatched: true,
    };

    return jsonResponse(responseData, 200, corsHeaders);
  }

  // 5. Default 404 for unknown endpoints
  return jsonResponse(
    {
      success: false,
      error: "NOT_FOUND",
      message: `Endpoint ${request.method} ${pathname} not found.`,
    },
    404,
    corsHeaders
  );
}

export default {
  fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    return handleRequest(request, env, ctx);
  },
};
