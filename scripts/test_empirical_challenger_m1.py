#!/usr/bin/env python3
"""
scripts/test_empirical_challenger_m1.py
Empirical Challenger Test Suite for Milestone 1 (workers/paywall/)

Target Challenges:
1. Cross-chain replay isolation (BSC vs Polygon vs Arbitrum)
2. Fake token contract detection (scam tokens, typosquatting, multi-log injection)
3. Confirmation depth boundaries (BSC: 3, Polygon: 10, Arbitrum: 2, Mempool 202, Fail-safe fallbacks)
4. Public RPC node resilience & timeout failover

Usage:
    python3 scripts/test_empirical_challenger_m1.py [-v]
"""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
PAYWALL_DIR = ROOT_DIR / "workers" / "paywall"

PASSED = 0
FAILED = 0
TOTAL_ASSERTIONS = 0


def log_test(name: str, passed: bool, msg: str = "", assertions: int = 1):
    global PASSED, FAILED, TOTAL_ASSERTIONS
    TOTAL_ASSERTIONS += assertions
    if passed:
        PASSED += 1
        print(f"  [PASS] {name} ({assertions} assertions)")
    else:
        FAILED += 1
        print(f"  [FAIL] {name}: {msg}")


def run_node_eval(code: str) -> dict:
    """Executes a Node.js snippet and returns parsed JSON output."""
    cmd = ["node", "-e", code]
    proc = subprocess.run(cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if proc.returncode != 0:
        return {"error": proc.stderr or proc.stdout, "returncode": proc.returncode}
    try:
        return json.loads(proc.stdout.strip())
    except Exception as e:
        return {"raw_stdout": proc.stdout, "error": str(e), "returncode": 0}


def test_cross_chain_replay():
    print("\n" + "=" * 70)
    print("CHALLENGE 1: Cross-Chain Replay Isolation")
    print("=" * 70)

    # 1.1 Valid BSC Hash on Polygon RPC returns 404 TRANSACTION_NOT_FOUND
    code_1_1 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const bscHash = '0x' + 'b5c1'.repeat(16);
      const mockRpc = {
        async eth_getTransactionReceipt() { return null; },
        async eth_getTransactionByHash() { return null; }
      };
      const res = await verifyPaymentOnChain({ network: 'polygon', txHash: bscHash }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_1_1)
    passed = res.get("status") == 404 and res.get("error") == "TRANSACTION_NOT_FOUND"
    log_test("1.1 BSC hash on Polygon RPC returns 404 TRANSACTION_NOT_FOUND", passed, str(res), 2)

    # 1.2 Valid BSC Hash on Arbitrum RPC returns 404 TRANSACTION_NOT_FOUND
    code_1_2 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const bscHash = '0x' + 'b5c1'.repeat(16);
      const mockRpc = {
        async eth_getTransactionReceipt() { return null; },
        async eth_getTransactionByHash() { return null; }
      };
      const res = await verifyPaymentOnChain({ network: 'arbitrum', txHash: bscHash }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_1_2)
    passed = res.get("status") == 404 and res.get("error") == "TRANSACTION_NOT_FOUND"
    log_test("1.2 BSC hash on Arbitrum RPC returns 404 TRANSACTION_NOT_FOUND", passed, str(res), 2)

    # 1.3 Collision Attack: Receipt with BSC USDT contract submitted on Polygon returns 400 INVALID_TOKEN_CONTRACT
    code_1_3 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { NETWORKS, ERC20_TRANSFER_TOPIC, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const bscHash = '0x' + 'b5c1'.repeat(16);
      const mockRpc = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: bscHash,
            blockNumber: '0x1000',
            status: '0x1',
            logs: [{
              address: NETWORKS.bsc.usdtContract, // BSC USDT address on Polygon!
              topics: [
                ERC20_TRANSFER_TOPIC,
                '0x' + '1'.repeat(40).padStart(64, '0'),
                '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
              ],
              data: '0x0000000000000000000000000000000000000000000000004563918244f40000' // 5 * 10^18
            }]
          };
        },
        async eth_blockNumber() { return 0x1020n; }
      };
      const res = await verifyPaymentOnChain({ network: 'polygon', txHash: bscHash }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_1_3)
    passed = res.get("status") == 400 and res.get("error") == "INVALID_TOKEN_CONTRACT"
    log_test("1.3 BSC contract address on Polygon RPC returns 400 INVALID_TOKEN_CONTRACT", passed, str(res), 2)

    # 1.4 Collision Attack: Receipt with BSC USDT contract submitted on Arbitrum returns 400 INVALID_TOKEN_CONTRACT
    code_1_4 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { NETWORKS, ERC20_TRANSFER_TOPIC, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const bscHash = '0x' + 'b5c1'.repeat(16);
      const mockRpc = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: bscHash,
            blockNumber: '0x1000',
            status: '0x1',
            logs: [{
              address: NETWORKS.bsc.usdtContract, // BSC USDT on Arbitrum!
              topics: [
                ERC20_TRANSFER_TOPIC,
                '0x' + '1'.repeat(40).padStart(64, '0'),
                '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
              ],
              data: '0x0000000000000000000000000000000000000000000000004563918244f40000'
            }]
          };
        },
        async eth_blockNumber() { return 0x1010n; }
      };
      const res = await verifyPaymentOnChain({ network: 'arbitrum', txHash: bscHash }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_1_4)
    passed = res.get("status") == 400 and res.get("error") == "INVALID_TOKEN_CONTRACT"
    log_test("1.4 BSC contract address on Arbitrum RPC returns 400 INVALID_TOKEN_CONTRACT", passed, str(res), 2)

    # 1.5 D1 Replay Protection across networks
    code_1_5 = """
    import('./workers/paywall/dist/src/replay.js').then(async ({ recordRedemption }) => {
      const { verifyPaymentOnChain } = await import('./workers/paywall/dist/src/verifier.js');
      const store = new Map();
      const mockDb = {
        prepare(q) {
          let bound = [];
          return {
            bind(...p) { bound = p; return this; },
            async first() { return store.get(bound[0]) || null; },
            async run() { store.set(bound[0], bound); return { success: true }; }
          };
        }
      };
      const txHash = '0x' + 'cafe'.repeat(16);
      await recordRedemption({
        txHash, network: 'bsc', bookId: 'b1', email: 'e@test.com',
        senderAddress: '0x1111111111111111111111111111111111111111',
        amountRaw: '5000000000000000000', blockNumber: 100
      }, { DB: mockDb });

      const resPoly = await verifyPaymentOnChain({ network: 'polygon', txHash }, { DB: mockDb });
      const resArb = await verifyPaymentOnChain({ network: 'arbitrum', txHash }, { DB: mockDb });
      console.log(JSON.stringify({ polyStatus: resPoly.status, polyErr: resPoly.error, arbStatus: resArb.status, arbErr: resArb.error }));
    });
    """
    res = run_node_eval(code_1_5)
    passed = res.get("polyStatus") == 409 and res.get("arbStatus") == 409 and res.get("polyErr") == "TRANSACTION_ALREADY_REDEEMED"
    log_test("1.5 Prior redemption on BSC prevents cross-chain reuse on Polygon/Arbitrum (409)", passed, str(res), 3)


def test_fake_token_detection():
    print("\n" + "=" * 70)
    print("CHALLENGE 2: Fake Token Contract Detection")
    print("=" * 70)

    # 2.1 Fake token on BSC
    code_2_1 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { ERC20_TRANSFER_TOPIC, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const fakeToken = '0x' + '9999'.repeat(10);
      const mockRpc = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: '0x' + 'aaaa'.repeat(16),
            blockNumber: '0x100',
            status: '0x1',
            logs: [{
              address: fakeToken,
              topics: [
                ERC20_TRANSFER_TOPIC,
                '0x' + '1'.repeat(40).padStart(64, '0'),
                '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
              ],
              data: '0x0000000000000000000000000000000000000000000000004563918244f40000'
            }]
          };
        },
        async eth_blockNumber() { return 0x200n; }
      };
      const res = await verifyPaymentOnChain({ network: 'bsc', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_2_1)
    passed = res.get("status") == 400 and res.get("error") == "INVALID_TOKEN_CONTRACT"
    log_test("2.1 Transferring fake ERC-20 token on BSC returns 400 INVALID_TOKEN_CONTRACT", passed, str(res), 2)

    # 2.2 Typosquatting token (1 char difference from real BSC USDT)
    code_2_2 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { ERC20_TRANSFER_TOPIC, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const typosquat = '0x55d398326f99059ff775485246999027b3197956'; // ends with 6 instead of 5
      const mockRpc = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: '0x' + 'aaaa'.repeat(16),
            blockNumber: '0x100',
            status: '0x1',
            logs: [{
              address: typosquat,
              topics: [
                ERC20_TRANSFER_TOPIC,
                '0x' + '1'.repeat(40).padStart(64, '0'),
                '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
              ],
              data: '0x0000000000000000000000000000000000000000000000004563918244f40000'
            }]
          };
        },
        async eth_blockNumber() { return 0x200n; }
      };
      const res = await verifyPaymentOnChain({ network: 'bsc', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_2_2)
    passed = res.get("status") == 400 and res.get("error") == "INVALID_TOKEN_CONTRACT"
    log_test("2.2 Typosquat token address (1 char diff) returns 400 INVALID_TOKEN_CONTRACT", passed, str(res), 2)

    # 2.3 Multi-log bundle injection: genuine token to random wallet + fake token to store wallet
    code_2_3 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { NETWORKS, ERC20_TRANSFER_TOPIC, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const fakeToken = '0x' + 'bad0'.repeat(10);
      const randomWallet = '0x' + '7'.repeat(40);
      const mockRpc = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: '0x' + 'aaaa'.repeat(16),
            blockNumber: '0x100',
            status: '0x1',
            logs: [
              // Log 0: Genuine USDT sent to random victim
              {
                address: NETWORKS.bsc.usdtContract,
                topics: [
                  ERC20_TRANSFER_TOPIC,
                  '0x' + '1'.repeat(40).padStart(64, '0'),
                  '0x' + randomWallet.toLowerCase().replace('0x', '').padStart(64, '0')
                ],
                data: '0x0000000000000000000000000000000000000000000000004563918244f40000'
              },
              // Log 1: Fake token sent to store wallet
              {
                address: fakeToken,
                topics: [
                  ERC20_TRANSFER_TOPIC,
                  '0x' + '1'.repeat(40).padStart(64, '0'),
                  '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
                ],
                data: '0x0000000000000000000000000000000000000000000000004563918244f40000'
              }
            ]
          };
        },
        async eth_blockNumber() { return 0x200n; }
      };
      const res = await verifyPaymentOnChain({ network: 'bsc', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_2_3)
    passed = res.get("success") is False and res.get("status") == 400
    log_test("2.3 Multi-log bundle with fake token to store wallet is rejected (status 400)", passed, str(res), 2)

    # 2.4 Approval event spoofing instead of Transfer event
    code_2_4 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { NETWORKS, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const approvalTopic = '0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925';
      const mockRpc = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: '0x' + 'aaaa'.repeat(16),
            blockNumber: '0x100',
            status: '0x1',
            logs: [{
              address: NETWORKS.bsc.usdtContract,
              topics: [
                approvalTopic,
                '0x' + '1'.repeat(40).padStart(64, '0'),
                '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
              ],
              data: '0x0000000000000000000000000000000000000000000000004563918244f40000'
            }]
          };
        },
        async eth_blockNumber() { return 0x200n; }
      };
      const res = await verifyPaymentOnChain({ network: 'bsc', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_2_4)
    passed = res.get("status") == 400 and res.get("error") == "NO_USDT_TRANSFER_FOUND"
    log_test("2.4 Approval event spoofing rejected with 400 NO_USDT_TRANSFER_FOUND", passed, str(res), 2)


def test_confirmation_boundaries():
    print("\n" + "=" * 70)
    print("CHALLENGE 3: Confirmation Depth Boundaries")
    print("=" * 70)

    # 3.1 BSC confirmation boundaries: 1, 2 confs -> 202, 3 confs -> 200
    code_3_1 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { NETWORKS, ERC20_TRANSFER_TOPIC, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const createRpc = (latestBlock) => ({
        async eth_getTransactionReceipt() {
          return {
            transactionHash: '0x' + 'aaaa'.repeat(16),
            blockNumber: '0x3e8', // 1000
            status: '0x1',
            logs: [{
              address: NETWORKS.bsc.usdtContract,
              topics: [
                ERC20_TRANSFER_TOPIC,
                '0x' + '1'.repeat(40).padStart(64, '0'),
                '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
              ],
              data: '0x0000000000000000000000000000000000000000000000004563918244f40000'
            }]
          };
        },
        async eth_blockNumber() { return latestBlock; }
      });

      const res1 = await verifyPaymentOnChain({ network: 'bsc', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: createRpc(1000n) }); // 1 conf
      const res2 = await verifyPaymentOnChain({ network: 'bsc', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: createRpc(1001n) }); // 2 confs
      const res3 = await verifyPaymentOnChain({ network: 'bsc', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: createRpc(1002n) }); // 3 confs
      console.log(JSON.stringify({
        c1Status: res1.status, c1Err: res1.error,
        c2Status: res2.status, c2Err: res2.error,
        c3Status: res3.status, c3Ok: res3.success
      }));
    });
    """
    res = run_node_eval(code_3_1)
    passed = (
        res.get("c1Status") == 202
        and res.get("c1Err") == "INSUFFICIENT_CONFIRMATIONS"
        and res.get("c2Status") == 202
        and res.get("c2Err") == "INSUFFICIENT_CONFIRMATIONS"
        and res.get("c3Status") == 200
        and res.get("c3Ok") is True
    )
    log_test("3.1 BSC boundary: 1 & 2 confs return 202, 3 confs returns 200 OK", passed, str(res), 4)

    # 3.2 Polygon confirmation boundaries: 9 confs -> 202, 10 confs -> 200
    code_3_2 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { NETWORKS, ERC20_TRANSFER_TOPIC, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const createRpc = (latestBlock) => ({
        async eth_getTransactionReceipt() {
          return {
            transactionHash: '0x' + 'aaaa'.repeat(16),
            blockNumber: '0x1388', // 5000
            status: '0x1',
            logs: [{
              address: NETWORKS.polygon.usdtContract,
              topics: [
                ERC20_TRANSFER_TOPIC,
                '0x' + '1'.repeat(40).padStart(64, '0'),
                '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
              ],
              data: '0x00000000000000000000000000000000000000000000000000000000004c4b40' // 5 * 10^6
            }]
          };
        },
        async eth_blockNumber() { return latestBlock; }
      });

      const res9 = await verifyPaymentOnChain({ network: 'polygon', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: createRpc(5008n) }); // 9 confs
      const res10 = await verifyPaymentOnChain({ network: 'polygon', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: createRpc(5009n) }); // 10 confs
      console.log(JSON.stringify({
        c9Status: res9.status, c9Err: res9.error,
        c10Status: res10.status, c10Ok: res10.success
      }));
    });
    """
    res = run_node_eval(code_3_2)
    passed = (
        res.get("c9Status") == 202
        and res.get("c9Err") == "INSUFFICIENT_CONFIRMATIONS"
        and res.get("c10Status") == 200
        and res.get("c10Ok") is True
    )
    log_test("3.2 Polygon boundary: 9 confs return 202, 10 confs returns 200 OK", passed, str(res), 3)

    # 3.3 Arbitrum confirmation boundaries: 1 conf -> 202, 2 confs -> 200
    code_3_3 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { NETWORKS, ERC20_TRANSFER_TOPIC, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const createRpc = (latestBlock) => ({
        async eth_getTransactionReceipt() {
          return {
            transactionHash: '0x' + 'aaaa'.repeat(16),
            blockNumber: '0x7d0', // 2000
            status: '0x1',
            logs: [{
              address: NETWORKS.arbitrum.usdtContract,
              topics: [
                ERC20_TRANSFER_TOPIC,
                '0x' + '1'.repeat(40).padStart(64, '0'),
                '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
              ],
              data: '0x00000000000000000000000000000000000000000000000000000000004c4b40'
            }]
          };
        },
        async eth_blockNumber() { return latestBlock; }
      });

      const res1 = await verifyPaymentOnChain({ network: 'arbitrum', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: createRpc(2000n) }); // 1 conf
      const res2 = await verifyPaymentOnChain({ network: 'arbitrum', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: createRpc(2001n) }); // 2 confs
      console.log(JSON.stringify({
        c1Status: res1.status, c1Err: res1.error,
        c2Status: res2.status, c2Ok: res2.success
      }));
    });
    """
    res = run_node_eval(code_3_3)
    passed = (
        res.get("c1Status") == 202
        and res.get("c1Err") == "INSUFFICIENT_CONFIRMATIONS"
        and res.get("c2Status") == 200
        and res.get("c2Ok") is True
    )
    log_test("3.3 Arbitrum boundary: 1 conf returns 202, 2 confs returns 200 OK", passed, str(res), 3)

    # 3.4 Mempool pending transaction returns 202 TRANSACTION_PENDING
    code_3_4 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const mockRpc = {
        async eth_getTransactionReceipt() { return null; },
        async eth_getTransactionByHash() { return { hash: '0x' + 'aaaa'.repeat(16), blockNumber: null }; }
      };
      const res = await verifyPaymentOnChain({ network: 'bsc', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_3_4)
    passed = res.get("status") == 202 and res.get("error") == "TRANSACTION_PENDING"
    log_test("3.4 Mempool pending transaction returns 202 TRANSACTION_PENDING", passed, str(res), 2)

    # 3.5 Fallback when eth_blockNumber throws: fails-safe to 1 conf (202 INSUFFICIENT_CONFIRMATIONS)
    code_3_5 = """
    import('./workers/paywall/dist/src/verifier.js').then(async ({ verifyPaymentOnChain }) => {
      const { NETWORKS, ERC20_TRANSFER_TOPIC, DEFAULT_STORE_WALLET } = await import('./workers/paywall/dist/src/config.js');
      const mockRpc = {
        async eth_getTransactionReceipt() {
          return {
            transactionHash: '0x' + 'aaaa'.repeat(16),
            blockNumber: '0x100',
            status: '0x1',
            logs: [{
              address: NETWORKS.bsc.usdtContract,
              topics: [
                ERC20_TRANSFER_TOPIC,
                '0x' + '1'.repeat(40).padStart(64, '0'),
                '0x' + DEFAULT_STORE_WALLET.toLowerCase().replace('0x', '').padStart(64, '0')
              ],
              data: '0x0000000000000000000000000000000000000000000000004563918244f40000'
            }]
          };
        },
        async eth_blockNumber() { throw new Error('RPC network partition'); }
      };
      const res = await verifyPaymentOnChain({ network: 'bsc', txHash: '0x' + 'aaaa'.repeat(16) }, {}, { customRpcClient: mockRpc });
      console.log(JSON.stringify(res));
    });
    """
    res = run_node_eval(code_3_5)
    passed = res.get("status") == 202 and res.get("error") == "INSUFFICIENT_CONFIRMATIONS"
    log_test("3.5 eth_blockNumber RPC failure safely defaults to 202 INSUFFICIENT_CONFIRMATIONS", passed, str(res), 2)


def test_public_rpc_resilience():
    print("\n" + "=" * 70)
    print("CHALLENGE 4: Public RPC Resilience & Live Connectivity")
    print("=" * 70)

    code_4 = """
    import('./workers/paywall/dist/src/config.js').then(async ({ NETWORKS }) => {
      const { EvmRpcClient } = await import('./workers/paywall/dist/src/rpc.js');
      const results = {};
      for (const [netId, net] of Object.entries(NETWORKS)) {
        const client = new EvmRpcClient(net.rpcUrls);
        const start = Date.now();
        try {
          const block = await client.eth_blockNumber();
          const latency = Date.now() - start;
          results[netId] = { ok: true, block: block.toString(), latencyMs: latency };
        } catch (err) {
          results[netId] = { ok: false, error: err.message };
        }
      }
      console.log(JSON.stringify(results));
    });
    """
    res = run_node_eval(code_4)
    bsc_ok = res.get("bsc", {}).get("ok") is True
    poly_ok = res.get("polygon", {}).get("ok") is True
    arb_ok = res.get("arbitrum", {}).get("ok") is True

    passed = bsc_ok and poly_ok and arb_ok
    log_test(
        f"4.1 Live Multi-Chain RPC connectivity (BSC: {res.get('bsc', {}).get('block')}, Polygon: {res.get('polygon', {}).get('block')}, Arbitrum: {res.get('arbitrum', {}).get('block')})",
        passed,
        str(res),
        3,
    )


def main():
    start = time.time()
    print("=" * 70)
    print("THEMINICEO PAYWALL EMPIRICAL CHALLENGER TEST SUITE")
    print("=" * 70)

    test_cross_chain_replay()
    test_fake_token_detection()
    test_confirmation_boundaries()
    test_public_rpc_resilience()

    duration = time.time() - start
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Tests Run:       {PASSED + FAILED}")
    print(f"Passed:                {PASSED}")
    print(f"Failed:                {FAILED}")
    print(f"Total Assertions:      {TOTAL_ASSERTIONS}")
    print(f"Duration:              {duration:.2f}s")

    if FAILED == 0:
        print("\n✅ VERDICT: APPROVE — ALL EMPIRICAL CHALLENGES PASSED SUCCESSFULLY!")
        return 0
    else:
        print(f"\n❌ VERDICT: CHALLENGE_FAILED — {FAILED} CHALLENGES FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
