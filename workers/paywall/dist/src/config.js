/**
 * Multi-Chain Network Configuration & EVM Parameters
 * Direct On-Chain Crypto Payment Verification Worker
 */
export const DEFAULT_STORE_WALLET = "0x4370D6c7A90A2f1d57C9788233792152A95204C7";
export const DEFAULT_USDT_PRICE = "5.00";
export const DEFAULT_DOWNLOAD_EXPIRY_SECONDS = 7200; // 2 hours
export const RPC_TIMEOUT_MS = 3500; // 3.5s per RPC attempt
/**
 * ERC-20 Transfer event signature:
 * Transfer(address indexed from, address indexed to, uint256 value)
 * keccak256("Transfer(address,address,uint256)")
 */
export const ERC20_TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";
export const NETWORKS = {
    bsc: {
        id: "bsc",
        name: "BNB Smart Chain (BEP-20)",
        chainId: 56,
        symbol: "BNB",
        usdtContract: "0x55d398326f99059ff775485246999027b3197955".toLowerCase(),
        decimals: 18,
        minUnits: 5000000000000000000n, // 5 * 10^18
        minConfirmations: 3,
        rpcUrls: [
            "https://bsc-dataseed.bnbchain.org",
            "https://bsc-dataseed-public.bnbchain.org",
            "https://bsc-rpc.publicnode.com",
            "https://binance.llamarpc.com",
            "https://1rpc.io/bnb",
        ],
        explorerTxUrl: "https://bscscan.com/tx/",
        recommended: true,
        estimatedFee: "< $0.05",
    },
    polygon: {
        id: "polygon",
        name: "Polygon PoS",
        chainId: 137,
        symbol: "POL",
        usdtContract: "0xc2132D05D31c914a87C6611C10748AEb04B58e8F".toLowerCase(),
        decimals: 6,
        minUnits: 5000000n, // 5 * 10^6
        minConfirmations: 10,
        // Note: polygon-rpc.com is permanently retired by Polygon Labs in 2026; avoided
        rpcUrls: [
            "https://polygon-bor-rpc.publicnode.com",
            "https://public.1rpc.io/matic",
            "https://polygon.drpc.org",
            "https://rpc.ankr.com/polygon",
        ],
        explorerTxUrl: "https://polygonscan.com/tx/",
        recommended: false,
        estimatedFee: "< $0.02",
    },
    arbitrum: {
        id: "arbitrum",
        name: "Arbitrum One",
        chainId: 42161,
        symbol: "ETH",
        usdtContract: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9".toLowerCase(),
        decimals: 6,
        minUnits: 5000000n, // 5 * 10^6
        minConfirmations: 2,
        rpcUrls: [
            "https://arb1.arbitrum.io/rpc",
            "https://arbitrum-one-rpc.publicnode.com",
            "https://public.1rpc.io/arb",
            "https://arbitrum.drpc.org",
        ],
        explorerTxUrl: "https://arbiscan.io/tx/",
        recommended: false,
        estimatedFee: "< $0.10",
    },
};
/**
 * Helper to fetch a network configuration by identifier
 */
export function getNetworkConfig(networkKey) {
    if (!networkKey)
        return undefined;
    const key = networkKey.trim().toLowerCase();
    return NETWORKS[key];
}
/**
 * Returns sanitized network list for client display
 */
export function getPublicNetworksList() {
    return Object.values(NETWORKS).map((net) => ({
        id: net.id,
        name: net.name,
        chainId: net.chainId,
        symbol: net.symbol,
        usdtContract: net.usdtContract,
        decimals: net.decimals,
        recommended: net.recommended,
        explorerTxUrl: net.explorerTxUrl,
        estimatedFee: net.estimatedFee,
    }));
}
/**
 * Validates transaction hash format: exactly 66 characters hex string starting with 0x
 */
export function isValidTxHash(txHash) {
    return typeof txHash === "string" && /^0x[0-9a-fA-F]{64}$/.test(txHash.trim());
}
/**
 * Validates Ethereum wallet address format: exactly 42 characters hex string starting with 0x
 */
export function isValidEthAddress(address) {
    return typeof address === "string" && /^0x[0-9a-fA-F]{40}$/.test(address.trim());
}
/**
 * Formats atomic BigInt token units into human-readable decimal USDT string
 * using pure integer arithmetic to prevent IEEE 754 precision errors.
 */
export function formatUsdtAmount(rawUnits, decimals) {
    const divisor = 10n ** BigInt(decimals);
    const whole = rawUnits / divisor;
    const remainder = rawUnits % divisor;
    const fracStr = remainder.toString().padStart(decimals, "0").slice(0, 2);
    return `${whole}.${fracStr}`;
}
