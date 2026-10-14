import { test, describe } from "node:test";
import assert from "node:assert/strict";
import {
  NETWORKS,
  getNetworkConfig,
  getPublicNetworksList,
  isValidTxHash,
  isValidEthAddress,
  formatUsdtAmount,
  DEFAULT_STORE_WALLET,
  DEFAULT_USDT_PRICE,
  ERC20_TRANSFER_TOPIC,
} from "../src/config.js";

describe("Multi-Chain Network Configuration", () => {
  test("BSC network parameters match specification", () => {
    const bsc = NETWORKS.bsc;
    assert.equal(bsc.id, "bsc");
    assert.equal(bsc.chainId, 56);
    assert.equal(bsc.decimals, 18);
    assert.equal(bsc.usdtContract, "0x55d398326f99059ff775485246999027b3197955".toLowerCase());
    assert.equal(bsc.minUnits, 1000000000000000000n);
    assert.equal(bsc.minConfirmations, 3);
    assert.ok(bsc.rpcUrls.length >= 3);
    assert.ok(bsc.rpcUrls.some((u) => u.includes("bsc-dataseed")));
    assert.equal(bsc.recommended, true);
  });

  test("Polygon network parameters match specification and avoid deprecated RPC", () => {
    const poly = NETWORKS.polygon;
    assert.equal(poly.id, "polygon");
    assert.equal(poly.chainId, 137);
    assert.equal(poly.decimals, 6);
    assert.equal(poly.usdtContract, "0xc2132D05D31c914a87C6611C10748AEb04B58e8F".toLowerCase());
    assert.equal(poly.minUnits, 1000000n);
    assert.equal(poly.minConfirmations, 10);
    assert.ok(poly.rpcUrls.length >= 3);
    // CRITICAL: polygon-rpc.com must NOT be present
    assert.ok(!poly.rpcUrls.some((u) => u.includes("polygon-rpc.com")));
  });

  test("Arbitrum One network parameters match specification", () => {
    const arb = NETWORKS.arbitrum;
    assert.equal(arb.id, "arbitrum");
    assert.equal(arb.chainId, 42161);
    assert.equal(arb.decimals, 6);
    assert.equal(arb.usdtContract, "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9".toLowerCase());
    assert.equal(arb.minUnits, 1000000n);
    assert.equal(arb.minConfirmations, 2);
    assert.ok(arb.rpcUrls.length >= 3);
    assert.ok(arb.rpcUrls.some((u) => u.includes("arb1.arbitrum.io")));
  });

  test("getNetworkConfig retrieves by case-insensitive key", () => {
    assert.equal(getNetworkConfig("BSC")?.chainId, 56);
    assert.equal(getNetworkConfig("polygon ")?.chainId, 137);
    assert.equal(getNetworkConfig("Arbitrum")?.chainId, 42161);
    assert.equal(getNetworkConfig("ethereum"), undefined);
    assert.equal(getNetworkConfig(""), undefined);
  });

  test("getPublicNetworksList exports sanitized network objects", () => {
    const list = getPublicNetworksList();
    assert.equal(list.length, 3);
    const ids = list.map((n) => n.id);
    assert.deepEqual(ids, ["bsc", "polygon", "arbitrum"]);
  });

  test("TxHash and EthAddress format validations", () => {
    const validHash = "0x" + "a".repeat(64);
    assert.ok(isValidTxHash(validHash));
    assert.ok(!isValidTxHash("0x" + "a".repeat(63))); // too short
    assert.ok(!isValidTxHash("0x" + "a".repeat(65))); // too long
    assert.ok(!isValidTxHash("a".repeat(64))); // missing 0x
    assert.ok(!isValidTxHash("0x" + "g".repeat(64))); // invalid hex

    assert.ok(isValidEthAddress(DEFAULT_STORE_WALLET));
    assert.ok(!isValidEthAddress("0x123"));
  });

  test("Native BigInt decimal arithmetic prevents IEEE 754 precision loss", () => {
    // BSC 18 decimals
    assert.equal(formatUsdtAmount(1000000000000000000n, 18), "1.00");
    assert.equal(formatUsdtAmount(5500000000000000000n, 18), "5.50");
    assert.equal(formatUsdtAmount(2500000000000000000n, 18), "2.50");
    assert.equal(formatUsdtAmount(100000000000000000000n, 18), "100.00");

    // Polygon / Arbitrum 6 decimals
    assert.equal(formatUsdtAmount(1000000n, 6), "1.00");
    assert.equal(formatUsdtAmount(10000000n, 6), "10.00");
    assert.equal(formatUsdtAmount(4990000n, 6), "4.99");
  });

  test("Constants integrity", () => {
    assert.equal(DEFAULT_STORE_WALLET, "0x4370D6c7A90A2f1d57C9788233792152A95204C7");
    assert.equal(DEFAULT_USDT_PRICE, "1.00");
    assert.equal(
      ERC20_TRANSFER_TOPIC,
      "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    );
  });
});
