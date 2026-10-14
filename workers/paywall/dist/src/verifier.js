/**
 * Payment Verification Engine
 * Direct On-Chain EVM Payment Verification against Public RPC Nodes
 */
import { DEFAULT_STORE_WALLET, ERC20_TRANSFER_TOPIC, formatUsdtAmount, getNetworkConfig, isValidTxHash, } from "./config.js";
import { isTransactionRedeemed } from "./replay.js";
import { EvmRpcClient, RpcConnectionError } from "./rpc.js";
/**
 * Standard 12 Diagnostic Error Codes and messages
 */
export const DIAGNOSTIC_ERRORS = {
    INVALID_TX_HASH_FORMAT: {
        status: 400,
        code: "INVALID_TX_HASH_FORMAT",
        message: "Invalid transaction hash. Must be a 66-character hexadecimal string beginning with 0x.",
    },
    UNSUPPORTED_NETWORK: {
        status: 400,
        code: "UNSUPPORTED_NETWORK",
        message: "Unsupported network. Please select BNB Smart Chain, Polygon, or Arbitrum One.",
    },
    TRANSACTION_ALREADY_REDEEMED: {
        status: 409,
        code: "TRANSACTION_ALREADY_REDEEMED",
        message: "This transaction has already been redeemed. Each transaction hash can only be used once.",
    },
    TRANSACTION_NOT_FOUND: {
        status: 404,
        code: "TRANSACTION_NOT_FOUND",
        message: "Transaction not found on this network. Please ensure the transaction has been broadcast and you selected the correct network.",
    },
    TRANSACTION_PENDING: {
        status: 202,
        code: "TRANSACTION_PENDING",
        message: "Transaction is pending in the network mempool. Please wait 15–30 seconds and click verify again.",
    },
    TRANSACTION_FAILED: {
        status: 400,
        code: "TRANSACTION_FAILED",
        message: "Transaction reverted on-chain. The payment was not completed by the network.",
    },
    INSUFFICIENT_CONFIRMATIONS: {
        status: 202,
        code: "INSUFFICIENT_CONFIRMATIONS",
        message: (current, required) => `Transaction has ${current}/${required} confirmations. Please wait a few seconds and try again.`,
    },
    NO_USDT_TRANSFER_FOUND: {
        status: 400,
        code: "NO_USDT_TRANSFER_FOUND",
        message: "No transfer of USDT to the designated store wallet was found in this transaction.",
    },
    INVALID_TOKEN_CONTRACT: {
        status: 400,
        code: "INVALID_TOKEN_CONTRACT",
        message: "Transfer was executed with an unauthorized token. Only canonical USDT is accepted.",
    },
    WRONG_RECIPIENT: {
        status: 400,
        code: "WRONG_RECIPIENT",
        message: (actual, expected) => `Payment was sent to a different wallet address (${actual}). Expected store address: ${expected}.`,
    },
    INSUFFICIENT_AMOUNT: {
        status: 400,
        code: "INSUFFICIENT_AMOUNT",
        message: (actualUsdt) => `Payment amount is insufficient. Received ${actualUsdt} USDT; required amount is 1.00 USDT.`,
    },
    RPC_CONNECTION_FAILURE: {
        status: 503,
        code: "RPC_CONNECTION_FAILURE",
        message: "Unable to connect to blockchain RPC nodes at this time. Please try again in a moment.",
    },
    STORE_WALLET_MISCONFIGURED: {
        status: 500,
        code: "STORE_WALLET_MISCONFIGURED",
        message: "Server store wallet is not properly configured.",
    },
};
/**
 * Main Payment Verification Logic
 */
export async function verifyPaymentOnChain(req, env, options) {
    const rawTxHash = req.txHash ? req.txHash.trim() : "";
    const rawNetwork = req.network ? req.network.trim().toLowerCase() : "";
    // 1. Format Validation: Regex ^0x[0-9a-fA-F]{64}$
    if (!isValidTxHash(rawTxHash)) {
        return {
            success: false,
            status: DIAGNOSTIC_ERRORS.INVALID_TX_HASH_FORMAT.status,
            error: DIAGNOSTIC_ERRORS.INVALID_TX_HASH_FORMAT.code,
            message: DIAGNOSTIC_ERRORS.INVALID_TX_HASH_FORMAT.message,
        };
    }
    const txHash = rawTxHash.toLowerCase();
    // 2. Network Support Validation
    const networkConfig = getNetworkConfig(rawNetwork);
    if (!networkConfig) {
        return {
            success: false,
            status: DIAGNOSTIC_ERRORS.UNSUPPORTED_NETWORK.status,
            error: DIAGNOSTIC_ERRORS.UNSUPPORTED_NETWORK.code,
            message: DIAGNOSTIC_ERRORS.UNSUPPORTED_NETWORK.message,
        };
    }
    // 3. Store Wallet Configuration Validation
    const storeWallet = (req.storeWallet || DEFAULT_STORE_WALLET).toLowerCase().trim();
    if (!/^0x[0-9a-f]{40}$/.test(storeWallet)) {
        return {
            success: false,
            status: DIAGNOSTIC_ERRORS.STORE_WALLET_MISCONFIGURED.status,
            error: DIAGNOSTIC_ERRORS.STORE_WALLET_MISCONFIGURED.code,
            message: DIAGNOSTIC_ERRORS.STORE_WALLET_MISCONFIGURED.message,
        };
    }
    // 4. Pre-flight Replay Protection Check
    const alreadyRedeemed = await isTransactionRedeemed(txHash, networkConfig.id, env);
    if (alreadyRedeemed) {
        return {
            success: false,
            status: DIAGNOSTIC_ERRORS.TRANSACTION_ALREADY_REDEEMED.status,
            error: DIAGNOSTIC_ERRORS.TRANSACTION_ALREADY_REDEEMED.code,
            message: DIAGNOSTIC_ERRORS.TRANSACTION_ALREADY_REDEEMED.message,
        };
    }
    // 5. Query EVM RPC for Transaction Receipt
    const rpcClient = options?.customRpcClient ||
        new EvmRpcClient(networkConfig.rpcUrls, options?.rpcOptions);
    let receipt = null;
    try {
        receipt = await rpcClient.eth_getTransactionReceipt(txHash);
    }
    catch (err) {
        if (err instanceof RpcConnectionError || (err instanceof Error && err.name === "RpcConnectionError")) {
            return {
                success: false,
                status: DIAGNOSTIC_ERRORS.RPC_CONNECTION_FAILURE.status,
                error: DIAGNOSTIC_ERRORS.RPC_CONNECTION_FAILURE.code,
                message: DIAGNOSTIC_ERRORS.RPC_CONNECTION_FAILURE.message,
            };
        }
        return {
            success: false,
            status: DIAGNOSTIC_ERRORS.RPC_CONNECTION_FAILURE.status,
            error: DIAGNOSTIC_ERRORS.RPC_CONNECTION_FAILURE.code,
            message: DIAGNOSTIC_ERRORS.RPC_CONNECTION_FAILURE.message,
        };
    }
    // 6. Handle Pending in Mempool vs Transaction Not Found
    if (!receipt) {
        try {
            const tx = await rpcClient.eth_getTransactionByHash(txHash);
            if (tx && (tx.blockNumber === null || tx.blockNumber === undefined)) {
                return {
                    success: false,
                    status: DIAGNOSTIC_ERRORS.TRANSACTION_PENDING.status,
                    error: DIAGNOSTIC_ERRORS.TRANSACTION_PENDING.code,
                    message: DIAGNOSTIC_ERRORS.TRANSACTION_PENDING.message,
                };
            }
        }
        catch {
            // If secondary lookup fails, treat as not found
        }
        return {
            success: false,
            status: DIAGNOSTIC_ERRORS.TRANSACTION_NOT_FOUND.status,
            error: DIAGNOSTIC_ERRORS.TRANSACTION_NOT_FOUND.code,
            message: DIAGNOSTIC_ERRORS.TRANSACTION_NOT_FOUND.message,
        };
    }
    // 7. Verify Transaction Execution Status (0x1 = Success, 0x0 = Reverted)
    const statusStr = String(receipt.status).toLowerCase();
    if (statusStr !== "0x1" && statusStr !== "1") {
        return {
            success: false,
            status: DIAGNOSTIC_ERRORS.TRANSACTION_FAILED.status,
            error: DIAGNOSTIC_ERRORS.TRANSACTION_FAILED.code,
            message: DIAGNOSTIC_ERRORS.TRANSACTION_FAILED.message,
        };
    }
    // 8. Confirmations Depth Verification
    const receiptBlock = BigInt(receipt.blockNumber);
    let latestBlock = receiptBlock;
    try {
        latestBlock = await rpcClient.eth_blockNumber();
    }
    catch {
        // If fetching latest block fails, fallback to receiptBlock (0/1 conf)
    }
    const confirmations = latestBlock >= receiptBlock ? latestBlock - receiptBlock + 1n : 0n;
    const minRequiredConf = BigInt(networkConfig.minConfirmations);
    if (confirmations < minRequiredConf) {
        return {
            success: false,
            status: DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.status,
            error: DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.code,
            message: DIAGNOSTIC_ERRORS.INSUFFICIENT_CONFIRMATIONS.message(confirmations, networkConfig.minConfirmations),
        };
    }
    // 9. Multi-Log Traversal: Parse and Validate ERC-20 Transfer Event
    const logs = Array.isArray(receipt.logs) ? receipt.logs : [];
    const normalizedTransferTopic = ERC20_TRANSFER_TOPIC.toLowerCase();
    let validMatchLog = null;
    let detectedWrongRecipient = null;
    let detectedInsufficientAmountUnits = null;
    let detectedWrongTokenContract = false;
    for (const log of logs) {
        if (log.removed === true)
            continue;
        if (!Array.isArray(log.topics) || log.topics.length < 3)
            continue;
        const topic0 = (log.topics[0] || "").toLowerCase();
        if (topic0 !== normalizedTransferTopic)
            continue;
        const logAddress = (log.address || "").toLowerCase();
        const recipient = ("0x" + log.topics[2].slice(-40)).toLowerCase();
        const sender = ("0x" + log.topics[1].slice(-40)).toLowerCase();
        // Safely parse raw BigInt value
        let value = 0n;
        try {
            const dataHex = log.data && log.data !== "0x" ? log.data : "0x0";
            value = BigInt(dataHex);
        }
        catch {
            value = 0n;
        }
        const isCanonicalUsdt = logAddress === networkConfig.usdtContract;
        const isStoreRecipient = recipient === storeWallet;
        if (!isCanonicalUsdt) {
            if (isStoreRecipient) {
                // Someone sent a non-canonical token to the store wallet
                detectedWrongTokenContract = true;
            }
            continue;
        }
        // From here, log IS canonical USDT
        if (!isStoreRecipient) {
            detectedWrongRecipient = recipient;
            continue;
        }
        // From here, log IS canonical USDT AND sent to store wallet
        if (value < networkConfig.minUnits) {
            detectedInsufficientAmountUnits = value;
            continue;
        }
        // Found legitimate transfer satisfying all rules!
        validMatchLog = log;
        break;
    }
    // 10. Evaluate Traversal Diagnostics if no valid transfer found
    if (!validMatchLog) {
        if (detectedInsufficientAmountUnits !== null) {
            const actualUsdtStr = formatUsdtAmount(detectedInsufficientAmountUnits, networkConfig.decimals);
            return {
                success: false,
                status: DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.status,
                error: DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.code,
                message: DIAGNOSTIC_ERRORS.INSUFFICIENT_AMOUNT.message(actualUsdtStr),
            };
        }
        if (detectedWrongRecipient !== null) {
            return {
                success: false,
                status: DIAGNOSTIC_ERRORS.WRONG_RECIPIENT.status,
                error: DIAGNOSTIC_ERRORS.WRONG_RECIPIENT.code,
                message: DIAGNOSTIC_ERRORS.WRONG_RECIPIENT.message(detectedWrongRecipient, storeWallet),
            };
        }
        if (detectedWrongTokenContract) {
            return {
                success: false,
                status: DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.status,
                error: DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.code,
                message: DIAGNOSTIC_ERRORS.INVALID_TOKEN_CONTRACT.message,
            };
        }
        return {
            success: false,
            status: DIAGNOSTIC_ERRORS.NO_USDT_TRANSFER_FOUND.status,
            error: DIAGNOSTIC_ERRORS.NO_USDT_TRANSFER_FOUND.code,
            message: DIAGNOSTIC_ERRORS.NO_USDT_TRANSFER_FOUND.message,
        };
    }
    // 11. Extract Verified Details
    const senderAddress = ("0x" + validMatchLog.topics[1].slice(-40)).toLowerCase();
    const rawUnits = BigInt(validMatchLog.data);
    const amountUsdt = formatUsdtAmount(rawUnits, networkConfig.decimals);
    return {
        success: true,
        status: 200,
        message: "Payment verified successfully on-chain.",
        data: {
            network: networkConfig.id,
            networkName: networkConfig.name,
            chainId: networkConfig.chainId,
            txHash,
            senderAddress,
            storeWallet,
            amountRaw: rawUnits.toString(),
            amountUsdt,
            blockNumber: Number(receiptBlock),
            confirmations: Number(confirmations),
            minConfirmations: networkConfig.minConfirmations,
        },
    };
}
