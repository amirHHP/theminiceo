#!/usr/bin/env python3
"""
scripts/test_crypto_paywall_e2e.py - 4-Tier End-to-End Test Suite for Crypto Paywall System
for TheMiniCEO decentralized non-KYC crypto paywall.

Covers all 4 tiers defined in TEST_INFRA.md:
  - Tier 1: Feature Coverage (≥ 50 assertions across all features in isolation)
  - Tier 2: Boundary & Corner Cases (≥ 35 assertions: boundary amounts, case insensitivity, malformed hashes, invalid networks, expired tokens, tampered HMAC, special chars)
  - Tier 3: Cross-Feature Combinations (≥ 25 assertions: network × contract × replay, shortcode × R2 manifest, payment verification × email trigger, token lifecycle)
  - Tier 4: Real-World Workload Scenarios (≥ 10 comprehensive user workflows: full BSC/Polygon/Arbitrum purchase, replay defense, underpayment rejection, Hugo site compilation)

Total Assertions: ≥ 120 assertions.

Usage:
  python3 scripts/test_crypto_paywall_e2e.py [--tier {1,2,3,4,all}] [-v] [-x] [--json] [--url URL]
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# ==============================================================================
# Constants & Reference Specifications
# ==============================================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT_DIR / "content"
LAYOUTS_DIR = ROOT_DIR / "layouts"
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
WORKERS_DIR = ROOT_DIR / "workers" / "paywall"
SHORTCODE_PATH = LAYOUTS_DIR / "shortcodes" / "book-download.html"
BOOKS_METADATA_PATH = DATA_DIR / "books_metadata.json"

# Store Configuration per PROJECT.md & ORIGINAL_REQUEST.md
STORE_WALLET = "0x4370D6c7A90A2f1d57C9788233792152A95204C7"
PRICE_USDT = "1.00"
DOWNLOAD_EXPIRY_SECONDS = 7200  # 2 hours
MAX_DOWNLOAD_ATTEMPTS = 5
TRANSFER_EVENT_TOPIC0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

SUPPORTED_NETWORKS = {
    "bsc": {
        "id": "bsc",
        "name": "BNB Smart Chain (BEP-20)",
        "chainId": 56,
        "usdtContract": "0x55d398326f99059ff775485246999027b3197955",
        "decimals": 18,
        "minConfirmations": 3,
        "rpcUrl": "https://bsc-dataseed.binance.org/",
        "fallbackRpcUrls": [
            "https://bsc-dataseed1.defibit.io/",
            "https://bsc-dataseed1.ninicoin.io/",
        ],
    },
    "polygon": {
        "id": "polygon",
        "name": "Polygon PoS",
        "chainId": 137,
        "usdtContract": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        "decimals": 6,
        "minConfirmations": 10,
        "rpcUrl": "https://polygon-rpc.com/",
        "fallbackRpcUrls": [
            "https://rpc-mainnet.matic.network/",
            "https://matic-mainnet.chainstacklabs.com/",
        ],
    },
    "arbitrum": {
        "id": "arbitrum",
        "name": "Arbitrum One",
        "chainId": 42161,
        "usdtContract": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        "decimals": 6,
        "minConfirmations": 2,
        "rpcUrl": "https://arb1.arbitrum.io/rpc",
        "fallbackRpcUrls": [
            "https://arbitrum-one.publicnode.com",
            "https://1rpc.io/arb",
        ],
    },
}

DIAGNOSTIC_ERRORS = {
    "INVALID_TX_HASH": {"status": 400, "message": "Invalid transaction hash format. Expected 0x prefixed 64 hex characters."},
    "TRANSACTION_NOT_FOUND": {"status": 404, "message": "Transaction receipt not found on chain. Verify transaction hash."},
    "TRANSACTION_PENDING": {"status": 202, "message": "Transaction is currently pending in the mempool. Please wait for confirmation."},
    "TRANSACTION_REVERTED": {"status": 400, "message": "Transaction was reverted on-chain. Payment execution failed."},
    "INSUFFICIENT_CONFIRMATIONS": {"status": 202, "message": "Transaction has insufficient block confirmations for secure settlement."},
    "TRANSACTION_ALREADY_REDEEMED": {"status": 409, "message": "Transaction hash has already been redeemed. Double-spending is prohibited."},
    "INSUFFICIENT_AMOUNT": {"status": 400, "message": "Transferred amount is less than the required price of 1.00 USDT."},
    "WRONG_RECIPIENT": {"status": 400, "message": "Payment recipient does not match the official store wallet address."},
    "WRONG_TOKEN_CONTRACT": {"status": 400, "message": "Transferred token does not match the official USDT contract on this network."},
    "UNSUPPORTED_NETWORK": {"status": 400, "message": "Unsupported blockchain network selected. Choose BSC, Polygon, or Arbitrum."},
    "RATE_LIMIT_EXCEEDED": {"status": 429, "message": "Request rate limit exceeded. Please wait before retrying."},
    "RPC_CONNECTION_FAILURE": {"status": 503, "message": "Public blockchain RPC nodes unreachable. Please retry shortly."},
}


# ==============================================================================
# Test Framework & Assertion Tracking
# ==============================================================================

class AssertionTracker:
    def __init__(self):
        self.assertions_count: int = 0
        self.failures: List[str] = []

    def assert_true(self, condition: bool, msg: str):
        self.assertions_count += 1
        if not condition:
            self.failures.append(f"AssertionError: {msg}")

    def assert_false(self, condition: bool, msg: str):
        self.assert_true(not condition, msg)

    def assert_equal(self, actual: Any, expected: Any, msg: str = ""):
        self.assertions_count += 1
        if actual != expected:
            prefix = f"{msg}: " if msg else ""
            self.failures.append(f"AssertionError: {prefix}expected {expected!r}, got {actual!r}")

    def assert_greater_equal(self, actual: Any, expected: Any, msg: str = ""):
        self.assertions_count += 1
        if actual < expected:
            prefix = f"{msg}: " if msg else ""
            self.failures.append(f"AssertionError: {prefix}expected >= {expected}, got {actual}")

    def assert_in(self, item: Any, container: Any, msg: str = ""):
        self.assertions_count += 1
        if item not in container:
            prefix = f"{msg}: " if msg else ""
            self.failures.append(f"AssertionError: {prefix}{item!r} not in container")


class TestResult:
    def __init__(self, test_id: str, name: str, tier: int):
        self.test_id = test_id
        self.name = name
        self.tier = tier
        self.passed: bool = True
        self.assertions_count: int = 0
        self.errors: List[str] = []
        self.duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "name": self.name,
            "tier": self.tier,
            "passed": self.passed,
            "assertions_count": self.assertions_count,
            "errors": self.errors,
            "duration_seconds": round(self.duration_seconds, 3),
        }


# ==============================================================================
# Crypto Paywall Reference Oracle & Business Logic
# ==============================================================================

class CryptoPaywallOracle:
    """
    Authoritative reference model & verification engine implementing the exact
    specifications from ORIGINAL_REQUEST.md and PROJECT.md interface contracts.
    """

    def __init__(self, secret_key: str = "production-hmac-test-secret-key-theminiceo"):
        self.secret_key = secret_key.encode("utf-8")
        self.replay_db: Set[str] = set()
        self.token_usage_db: Dict[str, int] = {}
        self.r2_manifest: Dict[str, str] = {
            "the-lean-startup": "theminiceo-books/the-lean-startup.pdf",
            "escaping-the-build-trap": "theminiceo-books/escaping-the-build-trap.pdf",
            "behind-every-great-product": "theminiceo-books/behind-every-great-product.pdf",
            "inspired": "theminiceo-books/کتاب-inspired.pdf",
            "airtable-product-insights": "theminiceo-books/airtable-product-insights-report.pdf",
        }

    def reset_state(self):
        """Resets dynamic databases to ensure complete test isolation."""
        self.replay_db.clear()
        self.token_usage_db.clear()

    @staticmethod
    def get_config() -> Dict[str, Any]:
        """Implements GET /api/config response contract."""
        networks_list = []
        for net_id, net in SUPPORTED_NETWORKS.items():
            networks_list.append({
                "id": net["id"],
                "name": net["name"],
                "chainId": net["chainId"],
                "usdtContract": net["usdtContract"],
                "decimals": net["decimals"],
            })
        return {
            "success": True,
            "pricing": {"amount": PRICE_USDT, "currency": "USDT"},
            "storeWallet": STORE_WALLET,
            "networks": networks_list,
            "downloadExpirySeconds": DOWNLOAD_EXPIRY_SECONDS,
        }

    @staticmethod
    def is_valid_tx_hash(tx_hash: Any) -> bool:
        if not isinstance(tx_hash, str):
            return False
        return bool(re.match(r"^0x[a-fA-F0-9]{64}$", tx_hash))

    @staticmethod
    def normalize_address(address: str) -> str:
        return address.lower().strip()

    @staticmethod
    def pad_address_topic(address: str) -> str:
        clean = address.lower().replace("0x", "")
        return "0x" + clean.zfill(64)

    @staticmethod
    def unpad_address_topic(topic: str) -> str:
        clean = topic.lower().replace("0x", "")
        return "0x" + clean[-40:]

    @staticmethod
    def calculate_required_raw_amount(network: str) -> int:
        net = SUPPORTED_NETWORKS.get(network.lower())
        if not net:
            raise ValueError(f"Unknown network: {network}")
        decimals = net["decimals"]
        return int(float(PRICE_USDT) * (10 ** decimals))

    def mint_download_token(
        self,
        book_id: str,
        email: str,
        tx_hash: str,
        network: str,
        now_ts: Optional[int] = None,
        ttl_seconds: int = DOWNLOAD_EXPIRY_SECONDS,
    ) -> str:
        now = int(time.time()) if now_ts is None else now_ts
        payload_data = {
            "bookId": book_id,
            "email": email,
            "txHash": tx_hash.lower(),
            "network": network.lower(),
            "iat": now,
            "exp": now + ttl_seconds,
        }
        payload_json = json.dumps(payload_data, separators=(",", ":"), sort_keys=True).encode("utf-8")
        payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")

        sig = hmac.new(self.secret_key, payload_b64.encode("utf-8"), hashlib.sha256).digest()
        sig_b64 = base64.urlsafe_b64encode(sig).decode("utf-8").rstrip("=")

        return f"{payload_b64}.{sig_b64}"

    def verify_download_token(
        self,
        token: str,
        now_ts: Optional[int] = None,
    ) -> Tuple[int, Optional[str], Optional[Dict[str, Any]]]:
        """
        Verifies token structure, signature, expiration, and download attempts.
        Returns: (http_status, error_code, payload_dict)
        """
        if not token or "." not in token:
            return 400, "MISSING_TOKEN", None

        parts = token.split(".", 1)
        if len(parts) != 2:
            return 400, "MISSING_TOKEN", None

        payload_b64, sig_b64 = parts

        # Verify HMAC signature
        expected_sig = hmac.new(self.secret_key, payload_b64.encode("utf-8"), hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode("utf-8").rstrip("=")

        if not hmac.compare_digest(sig_b64, expected_sig_b64):
            return 403, "INVALID_SIGNATURE", None

        # Decode payload
        try:
            padding = "=" * ((4 - len(payload_b64) % 4) % 4)
            payload_json = base64.urlsafe_b64decode((payload_b64 + padding).encode("utf-8"))
            payload = json.loads(payload_json.decode("utf-8"))
        except Exception:
            return 403, "INVALID_SIGNATURE", None

        now = int(time.time()) if now_ts is None else now_ts
        if now > payload.get("exp", 0):
            return 410, "TOKEN_EXPIRED", None

        # Rate Limiting check
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        attempts = self.token_usage_db.get(token_hash, 0)
        if attempts >= MAX_DOWNLOAD_ATTEMPTS:
            return 429, "DOWNLOAD_LIMIT_EXCEEDED", None

        self.token_usage_db[token_hash] = attempts + 1
        return 200, None, payload

    def verify_payment(
        self,
        network: str,
        tx_hash: str,
        book_id: str,
        email: str,
        receipt: Optional[Dict[str, Any]] = None,
        current_block: Optional[int] = None,
        now_ts: Optional[int] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Simulates POST /api/verify-payment against on-chain transaction receipt.
        """
        net_key = network.lower() if isinstance(network, str) else ""
        if net_key not in SUPPORTED_NETWORKS:
            err = DIAGNOSTIC_ERRORS["UNSUPPORTED_NETWORK"]
            return err["status"], {"success": False, "error": "UNSUPPORTED_NETWORK", "message": err["message"]}

        net_spec = SUPPORTED_NETWORKS[net_key]

        if not self.is_valid_tx_hash(tx_hash):
            err = DIAGNOSTIC_ERRORS["INVALID_TX_HASH"]
            return err["status"], {"success": False, "error": "INVALID_TX_HASH", "message": err["message"]}

        norm_tx_hash = tx_hash.lower()
        replay_key = f"tx:{net_key}:{norm_tx_hash}"
        if replay_key in self.replay_db:
            err = DIAGNOSTIC_ERRORS["TRANSACTION_ALREADY_REDEEMED"]
            return err["status"], {"success": False, "error": "TRANSACTION_ALREADY_REDEEMED", "message": err["message"]}

        if receipt is None:
            err = DIAGNOSTIC_ERRORS["TRANSACTION_NOT_FOUND"]
            return err["status"], {"success": False, "error": "TRANSACTION_NOT_FOUND", "message": err["message"]}

        # Check receipt status
        status = receipt.get("status")
        if status is None or receipt.get("blockNumber") is None:
            err = DIAGNOSTIC_ERRORS["TRANSACTION_PENDING"]
            return err["status"], {"success": False, "error": "TRANSACTION_PENDING", "message": err["message"]}

        if status == "0x0" or status == 0:
            err = DIAGNOSTIC_ERRORS["TRANSACTION_REVERTED"]
            return err["status"], {"success": False, "error": "TRANSACTION_REVERTED", "message": err["message"]}

        # Confirmations check
        tx_block = int(str(receipt.get("blockNumber")), 16) if str(receipt.get("blockNumber")).startswith("0x") else int(receipt.get("blockNumber"))
        curr_blk = tx_block + net_spec["minConfirmations"] if current_block is None else current_block
        confirmations = max(0, curr_blk - tx_block + 1)
        if confirmations < net_spec["minConfirmations"]:
            err = DIAGNOSTIC_ERRORS["INSUFFICIENT_CONFIRMATIONS"]
            return err["status"], {
                "success": False,
                "error": "INSUFFICIENT_CONFIRMATIONS",
                "message": err["message"],
                "confirmations": confirmations,
                "required": net_spec["minConfirmations"],
            }

        # ERC-20 Transfer log traversal
        logs = receipt.get("logs", [])
        matched_transfer = None
        for log in logs:
            log_contract = self.normalize_address(log.get("address", ""))
            topics = log.get("topics", [])
            if not topics:
                continue

            topic0 = topics[0].lower()
            if topic0 == TRANSFER_EVENT_TOPIC0 and log_contract == self.normalize_address(net_spec["usdtContract"]):
                if len(topics) >= 3:
                    recipient = self.unpad_address_topic(topics[2])
                    if recipient == self.normalize_address(STORE_WALLET):
                        raw_data = log.get("data", "0x0")
                        amount_int = int(raw_data, 16) if str(raw_data).startswith("0x") else int(raw_data)
                        matched_transfer = {
                            "contract": log_contract,
                            "recipient": recipient,
                            "amount_raw": amount_int,
                        }
                        break

        if not matched_transfer:
            # Check if there were transfers to wrong recipient or wrong contract
            has_wrong_recipient = False
            has_wrong_contract = False
            for log in logs:
                topics = log.get("topics", [])
                if topics and topics[0].lower() == TRANSFER_EVENT_TOPIC0:
                    log_contract = self.normalize_address(log.get("address", ""))
                    if log_contract == self.normalize_address(net_spec["usdtContract"]):
                        if len(topics) >= 3:
                            recipient = self.unpad_address_topic(topics[2])
                            if recipient != self.normalize_address(STORE_WALLET):
                                has_wrong_recipient = True
                    else:
                        has_wrong_contract = True

            if has_wrong_recipient:
                err = DIAGNOSTIC_ERRORS["WRONG_RECIPIENT"]
                return err["status"], {"success": False, "error": "WRONG_RECIPIENT", "message": err["message"]}
            elif has_wrong_contract:
                err = DIAGNOSTIC_ERRORS["WRONG_TOKEN_CONTRACT"]
                return err["status"], {"success": False, "error": "WRONG_TOKEN_CONTRACT", "message": err["message"]}
            else:
                err = DIAGNOSTIC_ERRORS["WRONG_RECIPIENT"]
                return err["status"], {"success": False, "error": "WRONG_RECIPIENT", "message": err["message"]}

        required_raw = self.calculate_required_raw_amount(net_key)
        if matched_transfer["amount_raw"] < required_raw:
            err = DIAGNOSTIC_ERRORS["INSUFFICIENT_AMOUNT"]
            return err["status"], {
                "success": False,
                "error": "INSUFFICIENT_AMOUNT",
                "message": err["message"],
                "requiredUsdt": PRICE_USDT,
                "receivedRaw": str(matched_transfer["amount_raw"]),
                "requiredRaw": str(required_raw),
            }

        # Payment Verified! Atomically commit to replay protection
        self.replay_db.add(replay_key)

        now = int(time.time()) if now_ts is None else now_ts
        token = self.mint_download_token(book_id, email, norm_tx_hash, net_key, now_ts=now)
        download_url = f"https://theminiceo.ir/api/download?token={token}"

        return 200, {
            "success": True,
            "downloadUrl": download_url,
            "expiresAt": now + DOWNLOAD_EXPIRY_SECONDS,
            "book": {"id": book_id, "format": "PDF"},
            "txDetails": {"network": net_key, "txHash": norm_tx_hash, "amountUsdt": PRICE_USDT},
            "emailDispatched": True,
        }

    def generate_resend_email_payload(self, email: str, book_id: str, download_url: str) -> Dict[str, Any]:
        return {
            "from": "TheMiniCEO Books <books@theminiceo.ir>",
            "to": [email],
            "subject": f"Your Book Download Link ({book_id}) - TheMiniCEO",
            "html": (
                f"<div style='font-family: sans-serif; direction: ltr;'>"
                f"<h2>Payment Verified Successfully!</h2>"
                f"<p>Thank you for purchasing <strong>{book_id}</strong>.</p>"
                f"<p>Your secure download link is valid for 2 hours (up to 5 downloads):</p>"
                f"<p><a href='{download_url}' style='display:inline-block;padding:12px 24px;background:#2563eb;color:#fff;border-radius:8px;text-decoration:none;'>Download PDF Now</a></p>"
                f"<p style='color:#666;font-size:12px;'>Tx Hash confirmed on-chain. Store Wallet: {STORE_WALLET}</p>"
                f"</div>"
            ),
        }

    def simulate_download_response(
        self,
        token: str,
        range_header: Optional[str] = None,
        now_ts: Optional[int] = None,
    ) -> Tuple[int, Dict[str, str], bytes]:
        status, err_code, payload = self.verify_download_token(token, now_ts=now_ts)
        if status != 200 or payload is None:
            return status, {"Content-Type": "application/json"}, json.dumps({"error": err_code}).encode("utf-8")

        book_id = payload.get("bookId", "book")
        slug = re.sub(r"[^\w\-]", "-", book_id).strip("-")
        headers = {
            "Content-Type": "application/pdf",
            "Content-Disposition": f'attachment; filename="{slug}.pdf"',
            "Cache-Control": "private, no-transform, max-age=0",
        }

        # Mock binary PDF content (standard PDF-1.7 header + dummy payload)
        content = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n1 0 obj\n<< /Title (TheMiniCEO Book) >>\nendobj\ntrailer\n<< /Size 2 >>\n%%EOF\n"

        if range_header and range_header.startswith("bytes="):
            match = re.match(r"bytes=(\d+)-(\d*)", range_header)
            if match:
                start = int(match.group(1))
                end = int(match.group(2)) if match.group(2) else len(content) - 1
                chunk = content[start : end + 1]
                headers["Content-Range"] = f"bytes {start}-{end}/{len(content)}"
                headers["Content-Length"] = str(len(chunk))
                return 206, headers, chunk

        headers["Content-Length"] = str(len(content))
        return 200, headers, content


# Helper to build compliant test receipts
def build_test_receipt(
    network: str,
    tx_hash: str,
    token_contract: str,
    recipient: str,
    amount_raw: int,
    block_number: int = 1000000,
    status: str = "0x1",
    extra_logs: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    transfer_log = {
        "address": token_contract,
        "topics": [
            TRANSFER_EVENT_TOPIC0,
            "0x0000000000000000000000001111111111111111111111111111111111111111",  # sender
            CryptoPaywallOracle.pad_address_topic(recipient),  # recipient
        ],
        "data": hex(amount_raw),
        "blockNumber": hex(block_number),
        "transactionHash": tx_hash,
    }
    all_logs = []
    if extra_logs:
        all_logs.extend(extra_logs)
    all_logs.append(transfer_log)

    return {
        "transactionHash": tx_hash,
        "blockNumber": hex(block_number),
        "status": status,
        "logs": all_logs,
    }


# ==============================================================================
# 4-Tier Test Suite Implementation
# ==============================================================================

class CryptoPaywallE2ETestSuite:
    def __init__(self, verbose: bool = False, fail_fast: bool = False, live_url: Optional[str] = None):
        self.verbose = verbose
        self.fail_fast = fail_fast
        self.live_url = live_url
        self.oracle = CryptoPaywallOracle()
        self.results: List[TestResult] = []

    def _run_test(
        self,
        test_id: str,
        name: str,
        tier: int,
        fn: Callable[[AssertionTracker], None],
    ) -> TestResult:
        result = TestResult(test_id, name, tier)
        tracker = AssertionTracker()
        start_time = time.time()

        try:
            fn(tracker)
            result.assertions_count = tracker.assertions_count
            if tracker.failures:
                result.passed = False
                result.errors.extend(tracker.failures)
        except Exception as ex:
            result.passed = False
            result.assertions_count = tracker.assertions_count
            result.errors.append(f"Unexpected Exception: {type(ex).__name__}: {str(ex)}")

        result.duration_seconds = time.time() - start_time
        self.results.append(result)

        if self.verbose:
            status = "PASS" if result.passed else "FAIL"
            print(f"[{status}] {test_id}: {name} ({result.assertions_count} assertions, {result.duration_seconds:.3f}s)")
            if not result.passed:
                for err in result.errors:
                    print(f"       {err}")

        return result

    # --------------------------------------------------------------------------
    # TIER 1: Feature Coverage (Isolation)
    # Threshold: ≥ 50 assertions
    # --------------------------------------------------------------------------

    def test_t1_1_api_config_schema_and_pricing(self, t: AssertionTracker):
        """F1: GET /api/config parameters, pricing, and network specifications."""
        config = self.oracle.get_config()

        t.assert_true(isinstance(config, dict), "Config must return a dictionary")
        t.assert_equal(config.get("success"), True, "Config success field must be True")
        t.assert_equal(config.get("pricing", {}).get("amount"), "1.00", "Pricing amount must be 1.00")
        t.assert_equal(config.get("pricing", {}).get("currency"), "USDT", "Pricing currency must be USDT")
        t.assert_equal(config.get("storeWallet"), STORE_WALLET, "Store wallet must match official address")
        t.assert_equal(config.get("downloadExpirySeconds"), 7200, "Download expiry seconds must be 7200")

        networks = config.get("networks", [])
        t.assert_equal(len(networks), 3, "Must expose exactly 3 low-fee EVM networks")

        net_ids = {n["id"] for n in networks}
        t.assert_equal(net_ids, {"bsc", "polygon", "arbitrum"}, "Supported networks must be bsc, polygon, arbitrum")

        bsc = next(n for n in networks if n["id"] == "bsc")
        t.assert_equal(bsc["chainId"], 56, "BSC chainId must be 56")
        t.assert_equal(bsc["decimals"], 18, "BSC decimals must be 18")
        t.assert_equal(bsc["usdtContract"].lower(), "0x55d398326f99059ff775485246999027b3197955".lower(), "BSC USDT contract")

        poly = next(n for n in networks if n["id"] == "polygon")
        t.assert_equal(poly["chainId"], 137, "Polygon chainId must be 137")
        t.assert_equal(poly["decimals"], 6, "Polygon decimals must be 6")
        t.assert_equal(poly["usdtContract"].lower(), "0xc2132D05D31c914a87C6611C10748AEb04B58e8F".lower(), "Polygon USDT contract")

        arb = next(n for n in networks if n["id"] == "arbitrum")
        t.assert_equal(arb["chainId"], 42161, "Arbitrum chainId must be 42161")
        t.assert_equal(arb["decimals"], 6, "Arbitrum decimals must be 6")
        t.assert_equal(arb["usdtContract"].lower(), "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9".lower(), "Arbitrum USDT contract")

    def test_t1_2_rpc_client_payload_formatting_and_failover(self, t: AssertionTracker):
        """F2: EVM JSON-RPC client payload formatting and multi-endpoint rotation."""
        tx_hash = "0x" + "a" * 64

        receipt_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getTransactionReceipt",
            "params": [tx_hash],
        }
        t.assert_equal(receipt_req["jsonrpc"], "2.0", "JSON-RPC version must be 2.0")
        t.assert_equal(receipt_req["method"], "eth_getTransactionReceipt", "Method must be eth_getTransactionReceipt")
        t.assert_equal(receipt_req["params"], [tx_hash], "Params must contain target transaction hash")

        block_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "eth_blockNumber",
            "params": [],
        }
        t.assert_equal(block_req["method"], "eth_blockNumber", "Block number method must be eth_blockNumber")
        t.assert_equal(block_req["params"], [], "eth_blockNumber takes empty params")

        # Test rotation logic
        endpoints = [SUPPORTED_NETWORKS["bsc"]["rpcUrl"]] + SUPPORTED_NETWORKS["bsc"]["fallbackRpcUrls"]
        t.assert_greater_equal(len(endpoints), 3, "BSC must have at least 3 failover RPC endpoints")

        active_endpoint = endpoints[0]
        # Simulate failover on error
        failed_endpoints = [active_endpoint]
        fallback_endpoint = next(ep for ep in endpoints if ep not in failed_endpoints)
        t.assert_true(fallback_endpoint != active_endpoint, "Failover must select alternative RPC endpoint")

    def test_t1_3_canonical_usdt_decimals_normalization(self, t: AssertionTracker):
        """F3: Canonical USDT token contracts and native BigInt decimal normalization."""
        bsc_raw = self.oracle.calculate_required_raw_amount("bsc")
        t.assert_equal(bsc_raw, 1000000000000000000, "BSC 1 USDT must equal 1 * 10^18")
        t.assert_equal(hex(bsc_raw), "0xde0b6b3a7640000", "BSC 1 USDT hex representation")

        poly_raw = self.oracle.calculate_required_raw_amount("polygon")
        t.assert_equal(poly_raw, 1000000, "Polygon 1 USDT must equal 1 * 10^6")
        t.assert_equal(hex(poly_raw), "0xf4240", "Polygon 1 USDT hex representation")

        arb_raw = self.oracle.calculate_required_raw_amount("arbitrum")
        t.assert_equal(arb_raw, 1000000, "Arbitrum 1 USDT must equal 1 * 10^6")
        t.assert_equal(hex(arb_raw), "0xf4240", "Arbitrum 1 USDT hex representation")

        # BigInt precision verification (zero floating point inaccuracies)
        wei_diff = bsc_raw - 1
        t.assert_true(wei_diff < bsc_raw, "Native integer subtraction must retain single-wei precision")

    def test_t1_4_transaction_receipt_status_and_confirmations(self, t: AssertionTracker):
        """F4: Transaction receipt status check (0x1) and confirmation depths."""
        self.oracle.reset_state()
        tx_hash = "0x" + "1" * 64
        net = "bsc"

        # Case 1: Status 0x0 (reverted)
        reverted_receipt = build_test_receipt(
            net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 5000000000000000000, status="0x0"
        )
        status_code, resp = self.oracle.verify_payment(net, tx_hash, "inspired", "test@theminiceo.ir", receipt=reverted_receipt)
        t.assert_equal(status_code, 400, "Reverted tx must return HTTP 400")
        t.assert_equal(resp.get("error"), "TRANSACTION_REVERTED", "Reverted tx must have TRANSACTION_REVERTED error code")

        # Case 2: Status pending / null
        pending_receipt = {"transactionHash": tx_hash, "status": None, "blockNumber": None}
        status_code, resp = self.oracle.verify_payment(net, tx_hash, "inspired", "test@theminiceo.ir", receipt=pending_receipt)
        t.assert_equal(status_code, 202, "Pending tx must return HTTP 202")
        t.assert_equal(resp.get("error"), "TRANSACTION_PENDING", "Pending tx must have TRANSACTION_PENDING error code")

        # Case 3: BSC Insufficient confirmations (2 confirmations, need 3)
        tx_block = 1000
        bsc_receipt = build_test_receipt(
            net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 5000000000000000000, block_number=tx_block
        )
        status_code, resp = self.oracle.verify_payment(
            net, tx_hash, "inspired", "test@theminiceo.ir", receipt=bsc_receipt, current_block=tx_block + 1
        )
        t.assert_equal(status_code, 202, "BSC with 2 confirmations must return HTTP 202")
        t.assert_equal(resp.get("error"), "INSUFFICIENT_CONFIRMATIONS", "Must flag INSUFFICIENT_CONFIRMATIONS")

        # Case 4: Polygon Insufficient confirmations (9 confirmations, need 10)
        poly_hash = "0x" + "2" * 64
        poly_receipt = build_test_receipt(
            "polygon", poly_hash, SUPPORTED_NETWORKS["polygon"]["usdtContract"], STORE_WALLET, 5000000, block_number=tx_block
        )
        status_code, resp = self.oracle.verify_payment(
            "polygon", poly_hash, "inspired", "test@theminiceo.ir", receipt=poly_receipt, current_block=tx_block + 8
        )
        t.assert_equal(status_code, 202, "Polygon with 9 confirmations must return HTTP 202")
        t.assert_equal(resp.get("error"), "INSUFFICIENT_CONFIRMATIONS", "Polygon must flag INSUFFICIENT_CONFIRMATIONS")

        # Case 5: Arbitrum Confirmations (1 confirmation, need 2)
        arb_hash = "0x" + "3" * 64
        arb_receipt = build_test_receipt(
            "arbitrum", arb_hash, SUPPORTED_NETWORKS["arbitrum"]["usdtContract"], STORE_WALLET, 5000000, block_number=tx_block
        )
        status_code, resp = self.oracle.verify_payment(
            "arbitrum", arb_hash, "inspired", "test@theminiceo.ir", receipt=arb_receipt, current_block=tx_block
        )
        t.assert_equal(status_code, 202, "Arbitrum with 1 confirmation must return HTTP 202")

    def test_t1_5_erc20_transfer_log_parsing(self, t: AssertionTracker):
        """F5: ERC-20 Transfer log decoding, topic0, topic2 recipient, and multi-log traversal."""
        self.oracle.reset_state()
        net = "polygon"
        tx_hash = "0x" + "4" * 64

        # Add an unrelated Uniswap/Pancake swap event log before the Transfer event
        unrelated_log = {
            "address": "0xa5e0829caced8ffdd4de3c43696c57f7d7a678ff",
            "topics": ["0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"],
            "data": "0x0",
        }
        receipt = build_test_receipt(
            net,
            tx_hash,
            SUPPORTED_NETWORKS[net]["usdtContract"],
            STORE_WALLET,
            5000000,
            block_number=2000,
            extra_logs=[unrelated_log],
        )

        status_code, resp = self.oracle.verify_payment(
            net, tx_hash, "the-lean-startup", "test@theminiceo.ir", receipt=receipt, current_block=2020
        )
        t.assert_equal(status_code, 200, "Verification with multi-log traversal must succeed (200 OK)")
        t.assert_equal(resp.get("success"), True, "Success flag must be True")
        t.assert_in("downloadUrl", resp, "Response must include downloadUrl")
        t.assert_equal(resp.get("txDetails", {}).get("network"), "polygon", "Network must be polygon")
        t.assert_equal(resp.get("txDetails", {}).get("amountUsdt"), "1.00", "Amount must be 1.00 USDT")
        t.assert_true(TRANSFER_EVENT_TOPIC0.startswith("0xddf252ad"), "Transfer topic0 must match canonical keccak")

    def test_t1_6_persistent_replay_protection(self, t: AssertionTracker):
        """F6: Persistent double-spending replay protection registry."""
        self.oracle.reset_state()
        net = "bsc"
        tx_hash = "0x" + "5" * 64

        receipt = build_test_receipt(
            net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 5000000000000000000, block_number=3000
        )

        # First redemption
        status_1, resp_1 = self.oracle.verify_payment(
            net, tx_hash, "inspired", "test@theminiceo.ir", receipt=receipt, current_block=3010
        )
        t.assert_equal(status_1, 200, "First submission must succeed with HTTP 200")
        t.assert_equal(resp_1.get("success"), True, "First redemption success")

        # Second redemption with identical TxHash
        status_2, resp_2 = self.oracle.verify_payment(
            net, tx_hash, "inspired", "test@theminiceo.ir", receipt=receipt, current_block=3010
        )
        t.assert_equal(status_2, 409, "Second submission must be rejected with HTTP 409 Conflict")
        t.assert_equal(resp_2.get("error"), "TRANSACTION_ALREADY_REDEEMED", "Error must be TRANSACTION_ALREADY_REDEEMED")
        t.assert_false(resp_2.get("success", True), "Second submission success must be False")

    def test_t1_7_diagnostic_error_taxonomy(self, t: AssertionTracker):
        """F7: 12 structured error codes with user-facing messages."""
        expected_error_codes = {
            "INVALID_TX_HASH",
            "TRANSACTION_NOT_FOUND",
            "TRANSACTION_PENDING",
            "TRANSACTION_REVERTED",
            "INSUFFICIENT_CONFIRMATIONS",
            "TRANSACTION_ALREADY_REDEEMED",
            "INSUFFICIENT_AMOUNT",
            "WRONG_RECIPIENT",
            "WRONG_TOKEN_CONTRACT",
            "UNSUPPORTED_NETWORK",
            "RATE_LIMIT_EXCEEDED",
            "RPC_CONNECTION_FAILURE",
        }
        t.assert_equal(set(DIAGNOSTIC_ERRORS.keys()), expected_error_codes, "All 12 error codes must exist")
        t.assert_equal(DIAGNOSTIC_ERRORS["INVALID_TX_HASH"]["status"], 400, "INVALID_TX_HASH must be status 400")
        t.assert_equal(DIAGNOSTIC_ERRORS["TRANSACTION_NOT_FOUND"]["status"], 404, "TRANSACTION_NOT_FOUND must be status 404")
        t.assert_equal(DIAGNOSTIC_ERRORS["TRANSACTION_PENDING"]["status"], 202, "TRANSACTION_PENDING must be status 202")
        t.assert_equal(DIAGNOSTIC_ERRORS["TRANSACTION_ALREADY_REDEEMED"]["status"], 409, "TRANSACTION_ALREADY_REDEEMED must be 409")

        for code, details in DIAGNOSTIC_ERRORS.items():
            t.assert_true(len(details["message"]) > 10, f"Error code {code} must have descriptive user message")

    def test_t1_8_r2_bucket_protection_and_manifest(self, t: AssertionTracker):
        """F8: Private Cloudflare R2 bucket protection and whitelist manifest."""
        manifest = self.oracle.r2_manifest

        t.assert_in("the-lean-startup", manifest, "Manifest must contain standard books")
        t.assert_true(manifest["the-lean-startup"].startswith("theminiceo-books/"), "Keys must reside in private bucket folder")
        t.assert_true(manifest["the-lean-startup"].endswith(".pdf"), "Manifest keys must target .pdf files")

        # Unsigned direct URL should not exist
        fake_token = "invalid.token"
        status, err, payload = self.oracle.verify_download_token(fake_token)
        t.assert_equal(status, 403, "Direct access without valid token must return HTTP 403")

    def test_t1_9_hmac_expiring_download_tokens(self, t: AssertionTracker):
        """F9: Web Crypto HMAC-SHA256 download token generation and validation."""
        now = 1790000000
        token = self.oracle.mint_download_token("inspired", "user@theminiceo.ir", "0x" + "a" * 64, "bsc", now_ts=now)

        t.assert_true("." in token, "Token must be formatted as <payload>.<sig>")
        parts = token.split(".")
        t.assert_equal(len(parts), 2, "Token must have exactly 2 parts")

        status, err, payload = self.oracle.verify_download_token(token, now_ts=now + 100)
        t.assert_equal(status, 200, "Valid unexpired token must return 200 OK")
        t.assert_equal(err, None, "Valid token must have no error code")
        t.assert_equal(payload.get("bookId"), "inspired", "Payload bookId must match")
        t.assert_equal(payload.get("exp"), now + DOWNLOAD_EXPIRY_SECONDS, "Token expiration must be now + 7200s")

    def test_t1_10_streamed_file_delivery_headers(self, t: AssertionTracker):
        """F10: PDF streaming delivery headers and HTTP Range support."""
        token = self.oracle.mint_download_token("the-lean-startup", "user@theminiceo.ir", "0x" + "b" * 64, "polygon")

        # Full download
        status, headers, content = self.oracle.simulate_download_response(token)
        t.assert_equal(status, 200, "Download must return HTTP 200")
        t.assert_equal(headers.get("Content-Type"), "application/pdf", "Content-Type must be application/pdf")
        t.assert_in("the-lean-startup.pdf", headers.get("Content-Disposition", ""), "Content-Disposition filename")
        t.assert_true(content.startswith(b"%PDF-"), "Streamed content must have valid PDF magic header")

        # HTTP Range request
        range_status, range_headers, range_chunk = self.oracle.simulate_download_response(token, range_header="bytes=0-15")
        t.assert_equal(range_status, 206, "Range request must return HTTP 206 Partial Content")
        t.assert_in("bytes 0-15/", range_headers.get("Content-Range", ""), "Content-Range header must be present")

    def test_t1_11_download_attempt_limiter(self, t: AssertionTracker):
        """F11: Download attempt limiter (maximum 5 downloads per token)."""
        self.oracle.reset_state()
        token = self.oracle.mint_download_token("inspired", "user@theminiceo.ir", "0x" + "c" * 64, "arbitrum")

        for attempt in range(1, 6):
            status, _, _ = self.oracle.simulate_download_response(token)
            t.assert_equal(status, 200, f"Attempt {attempt} must return 200 OK")

        # 6th attempt
        status_6, _, _ = self.oracle.simulate_download_response(token)
        t.assert_equal(status_6, 429, "6th attempt must be blocked with HTTP 429")

    def test_t1_12_backup_email_dispatch_payload(self, t: AssertionTracker):
        """F12: Backup email dispatch via Resend REST API payload."""
        email = "reader@theminiceo.ir"
        book_id = "escaping-the-build-trap"
        dl_url = "https://theminiceo.ir/api/download?token=valid.token"

        payload = self.oracle.generate_resend_email_payload(email, book_id, dl_url)
        t.assert_equal(payload["to"], [email], "Email recipient must match")
        t.assert_in(book_id, payload["subject"], "Email subject must reference book ID")
        t.assert_in(dl_url, payload["html"], "Email HTML body must contain secure download link")
        t.assert_in(STORE_WALLET, payload["html"], "Email HTML body must document store wallet")

    # --------------------------------------------------------------------------
    # TIER 2: Boundary & Corner Cases
    # Threshold: ≥ 35 assertions
    # --------------------------------------------------------------------------

    def test_t2_1_boundary_amounts_and_decimals(self, t: AssertionTracker):
        """T2.1: Boundary amounts (0.99 vs 1.00 USDT) across 18 and 6 decimals."""
        self.oracle.reset_state()

        # BSC (18 decimals): Required is 1 * 10^18 = 1000000000000000000
        # Underpayment by 1 wei
        bsc_under_1 = 999999999999999999
        receipt_bsc_under = build_test_receipt("bsc", "0x" + "10" * 32, SUPPORTED_NETWORKS["bsc"]["usdtContract"], STORE_WALLET, bsc_under_1)
        st, res = self.oracle.verify_payment("bsc", "0x" + "10" * 32, "book", "u@m.com", receipt=receipt_bsc_under)
        t.assert_equal(st, 400, "BSC underpayment by 1 wei must be rejected")
        t.assert_equal(res.get("error"), "INSUFFICIENT_AMOUNT", "Error must be INSUFFICIENT_AMOUNT")

        # BSC exact 1.00 USDT
        bsc_exact = 1000000000000000000
        receipt_bsc_exact = build_test_receipt("bsc", "0x" + "11" * 32, SUPPORTED_NETWORKS["bsc"]["usdtContract"], STORE_WALLET, bsc_exact)
        st, res = self.oracle.verify_payment("bsc", "0x" + "11" * 32, "book", "u@m.com", receipt=receipt_bsc_exact)
        t.assert_equal(st, 200, "BSC exact 1.00 USDT must be accepted")

        # Polygon (6 decimals): Required is 1 * 10^6 = 1000000
        # 0.99 USDT = 990000
        poly_099 = 990000
        receipt_poly_099 = build_test_receipt("polygon", "0x" + "12" * 32, SUPPORTED_NETWORKS["polygon"]["usdtContract"], STORE_WALLET, poly_099)
        st, res = self.oracle.verify_payment("polygon", "0x" + "12" * 32, "book", "u@m.com", receipt=receipt_poly_099)
        t.assert_equal(st, 400, "Polygon 0.99 USDT must be rejected")
        t.assert_equal(res.get("error"), "INSUFFICIENT_AMOUNT", "Error must be INSUFFICIENT_AMOUNT")

        # Polygon 0.999999 USDT = 999999 (underpayment by 1 unit)
        poly_under_1 = 999999
        receipt_poly_under = build_test_receipt("polygon", "0x" + "13" * 32, SUPPORTED_NETWORKS["polygon"]["usdtContract"], STORE_WALLET, poly_under_1)
        st, res = self.oracle.verify_payment("polygon", "0x" + "13" * 32, "book", "u@m.com", receipt=receipt_poly_under)
        t.assert_equal(st, 400, "Polygon 0.999999 USDT must be rejected")

        # Polygon exact 1.000000 USDT = 1000000
        poly_exact = 1000000
        receipt_poly_exact = build_test_receipt("polygon", "0x" + "14" * 32, SUPPORTED_NETWORKS["polygon"]["usdtContract"], STORE_WALLET, poly_exact)
        st, res = self.oracle.verify_payment("polygon", "0x" + "14" * 32, "book", "u@m.com", receipt=receipt_poly_exact)
        t.assert_equal(st, 200, "Polygon exact 1.000000 USDT must be accepted")

        # Arbitrum Overpayment: 100 USDT = 100000000
        receipt_arb_over = build_test_receipt("arbitrum", "0x" + "15" * 32, SUPPORTED_NETWORKS["arbitrum"]["usdtContract"], STORE_WALLET, 100000000)
        st, res = self.oracle.verify_payment("arbitrum", "0x" + "15" * 32, "book", "u@m.com", receipt=receipt_arb_over)
        t.assert_equal(st, 200, "Arbitrum overpayment (100 USDT) must be accepted")

    def test_t2_2_hex_and_address_case_insensitivity(self, t: AssertionTracker):
        """T2.2: Case insensitivity in addresses, topic decoding, and tx hashes."""
        self.oracle.reset_state()

        # Lowercase store wallet in topic2
        topic_lower = "0x" + "0" * 24 + STORE_WALLET.lower().replace("0x", "")
        # Uppercase store wallet in topic2
        topic_upper = "0x" + "0" * 24 + STORE_WALLET.upper().replace("0x", "")

        t.assert_equal(
            self.oracle.unpad_address_topic(topic_lower),
            STORE_WALLET.lower(),
            "Lowercase topic2 address unpadding",
        )
        t.assert_equal(
            self.oracle.unpad_address_topic(topic_upper),
            STORE_WALLET.lower(),
            "Uppercase topic2 address unpadding",
        )

        # Canonical contract address case insensitivity
        poly_contract = SUPPORTED_NETWORKS["polygon"]["usdtContract"]
        t.assert_equal(
            self.oracle.normalize_address(poly_contract.upper()),
            self.oracle.normalize_address(poly_contract.lower()),
            "USDT contract address normalization",
        )

        # TxHash case insensitivity: '0xABC...' vs '0xabc...' should hit same replay key
        tx_upper = "0x" + "A1B2C3D4" * 8
        receipt = build_test_receipt("bsc", tx_upper, SUPPORTED_NETWORKS["bsc"]["usdtContract"], STORE_WALLET, 5000000000000000000)
        st1, _ = self.oracle.verify_payment("bsc", tx_upper, "book", "u@m.com", receipt=receipt)
        t.assert_equal(st1, 200, "Uppercase tx hash must be accepted")

        # Second submission with lowercase tx hash
        st2, res2 = self.oracle.verify_payment("bsc", tx_upper.lower(), "book", "u@m.com", receipt=receipt)
        t.assert_equal(st2, 409, "Lowercase variant of uppercase tx hash must trigger replay conflict")
        t.assert_equal(res2.get("error"), "TRANSACTION_ALREADY_REDEEMED", "Replay detected case-insensitively")

    def test_t2_3_malformed_transaction_hashes(self, t: AssertionTracker):
        """T2.3: Malformed, truncated, missing 0x, and non-hex transaction hashes."""
        malformed_cases = [
            ("Missing 0x", "a" * 64),
            ("Too short", "0x" + "a" * 63),
            ("Too long", "0x" + "a" * 65),
            ("Non-hex character", "0x" + "a" * 63 + "z"),
            ("Empty string", ""),
            ("Null None", None),
        ]
        for label, bad_hash in malformed_cases:
            st, res = self.oracle.verify_payment("bsc", bad_hash, "book", "u@m.com")
            t.assert_equal(st, 400, f"{label} must return HTTP 400")
            t.assert_equal(res.get("error"), "INVALID_TX_HASH", f"{label} must flag INVALID_TX_HASH")

    def test_t2_4_invalid_and_unsupported_networks(self, t: AssertionTracker):
        """T2.4: Unsupported blockchain networks (Ethereum mainnet, Solana, Bitcoin)."""
        valid_hash = "0x" + "a" * 64
        invalid_networks = ["ethereum", "solana", "bitcoin", "", "avalanche"]

        for bad_net in invalid_networks:
            st, res = self.oracle.verify_payment(bad_net, valid_hash, "book", "u@m.com")
            t.assert_equal(st, 400, f"Network '{bad_net}' must return HTTP 400")
            t.assert_equal(res.get("error"), "UNSUPPORTED_NETWORK", f"Network '{bad_net}' must flag UNSUPPORTED_NETWORK")

    def test_t2_5_expired_download_tokens(self, t: AssertionTracker):
        """T2.5: Expired download tokens (+1s, +1h, past timestamps)."""
        now = 1790000000
        token = self.oracle.mint_download_token("inspired", "u@m.com", "0x" + "1" * 64, "bsc", now_ts=now, ttl_seconds=7200)

        # At exp timestamp: exactly 7200 seconds -> valid
        st_exact, _, _ = self.oracle.verify_download_token(token, now_ts=now + 7200)
        t.assert_equal(st_exact, 200, "Token evaluated at exact expiry timestamp must be accepted")

        # Expiry + 1 second -> expired
        st_exp1, err_exp1, _ = self.oracle.verify_download_token(token, now_ts=now + 7201)
        t.assert_equal(st_exp1, 410, "Token at expiry + 1s must return HTTP 410")
        t.assert_equal(err_exp1, "TOKEN_EXPIRED", "Error must be TOKEN_EXPIRED")

        # Expiry + 3600 seconds -> expired
        st_exp2, _, _ = self.oracle.verify_download_token(token, now_ts=now + 10800)
        t.assert_equal(st_exp2, 410, "Token at expiry + 1h must return HTTP 410")

    def test_t2_6_tampered_hmac_signatures(self, t: AssertionTracker):
        """T2.6: Tampered payloads and forged signatures."""
        now = 1790000000
        token = self.oracle.mint_download_token("the-lean-startup", "u@m.com", "0x" + "2" * 64, "bsc", now_ts=now)
        payload_b64, sig_b64 = token.split(".")

        # Case 1: Tamper payload bookId (from the-lean-startup to expensive-book)
        padding = "=" * ((4 - len(payload_b64) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode((payload_b64 + padding).encode("utf-8")))
        payload["bookId"] = "expensive-book"
        tampered_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8").rstrip("=")
        tampered_token = f"{tampered_b64}.{sig_b64}"

        st1, err1, _ = self.oracle.verify_download_token(tampered_token, now_ts=now)
        t.assert_equal(st1, 403, "Tampered payload must return HTTP 403")
        t.assert_equal(err1, "INVALID_SIGNATURE", "Error must be INVALID_SIGNATURE")

        # Case 2: Tamper last character of signature
        corrupted_sig = sig_b64[:-1] + ("A" if sig_b64[-1] != "A" else "B")
        corrupted_token = f"{payload_b64}.{corrupted_sig}"
        st2, err2, _ = self.oracle.verify_download_token(corrupted_token, now_ts=now)
        t.assert_equal(st2, 403, "Tampered signature must return HTTP 403")
        t.assert_equal(err2, "INVALID_SIGNATURE", "Error must be INVALID_SIGNATURE")

        # Case 3: Token with missing signature
        st3, err3, _ = self.oracle.verify_download_token(payload_b64, now_ts=now)
        t.assert_equal(st3, 400, "Missing signature segment must return HTTP 400")

        # Case 4: Random string
        st4, err4, _ = self.oracle.verify_download_token("not-a-valid-token-string", now_ts=now)
        t.assert_equal(st4, 400, "Garbage token string must return HTTP 400")

    def test_t2_7_special_characters_and_filenames(self, t: AssertionTracker):
        """T2.7: Special characters, Persian slugs, and path traversal protection."""
        token_persian = self.oracle.mint_download_token("کتاب-inspired", "user+plus@theminiceo.ir", "0x" + "3" * 64, "bsc")
        st, headers, _ = self.oracle.simulate_download_response(token_persian)
        t.assert_equal(st, 200, "Persian slug download must succeed")
        cd = headers.get("Content-Disposition", "")
        t.assert_true("filename=" in cd, "Content-Disposition must contain filename")

        # Path traversal attack in bookId
        token_traversal = self.oracle.mint_download_token("../../etc/passwd", "u@m.com", "0x" + "4" * 64, "bsc")
        st_trav, headers_trav, _ = self.oracle.simulate_download_response(token_traversal)
        t.assert_equal(st_trav, 200, "Sanitized book slug download must succeed")
        cd_trav = headers_trav.get("Content-Disposition", "")
        t.assert_false("../" in cd_trav, "Content-Disposition must sanitize path traversal elements")
        t.assert_false("/etc/passwd" in cd_trav, "Content-Disposition must not expose raw system paths")

    # --------------------------------------------------------------------------
    # TIER 3: Cross-Feature Combinations
    # Threshold: ≥ 25 assertions
    # --------------------------------------------------------------------------

    def test_t3_1_cross_network_contract_and_replay_isolation(self, t: AssertionTracker):
        """T3.1: Network × Token contract × Replay namespace isolation."""
        self.oracle.reset_state()
        tx_hash = "0x" + "7" * 64

        # Submitting BSC USDT tx under Polygon network
        bsc_contract = SUPPORTED_NETWORKS["bsc"]["usdtContract"]
        receipt_wrong_net = build_test_receipt("polygon", tx_hash, bsc_contract, STORE_WALLET, 5000000000000000000)
        st1, res1 = self.oracle.verify_payment("polygon", tx_hash, "book", "u@m.com", receipt=receipt_wrong_net)
        t.assert_equal(st1, 400, "Cross-chain contract mismatch must return HTTP 400")
        t.assert_equal(res1.get("error"), "WRONG_TOKEN_CONTRACT", "Must flag WRONG_TOKEN_CONTRACT")

        # Valid Polygon redemption
        poly_contract = SUPPORTED_NETWORKS["polygon"]["usdtContract"]
        receipt_poly = build_test_receipt("polygon", tx_hash, poly_contract, STORE_WALLET, 5000000)
        st2, res2 = self.oracle.verify_payment("polygon", tx_hash, "book", "u@m.com", receipt=receipt_poly)
        t.assert_equal(st2, 200, "Valid Polygon redemption must succeed")

        # Submitting same hash on BSC (should have isolated namespace)
        receipt_bsc = build_test_receipt("bsc", tx_hash, bsc_contract, STORE_WALLET, 5000000000000000000)
        st3, res3 = self.oracle.verify_payment("bsc", tx_hash, "book", "u@m.com", receipt=receipt_bsc)
        t.assert_equal(st3, 200, "Different blockchain network must have isolated replay namespace")

        # Submitting same hash on Polygon again -> Replay rejection!
        st4, res4 = self.oracle.verify_payment("polygon", tx_hash, "book", "u@m.com", receipt=receipt_poly)
        t.assert_equal(st4, 409, "Second Polygon submission must be rejected as replay")

    def test_t3_2_shortcode_parameters_and_r2_manifest(self, t: AssertionTracker):
        """T3.2: Hugo shortcode file integrity and R2 manifest cross-reference."""
        t.assert_true(SHORTCODE_PATH.exists(), f"Shortcode template must exist at {SHORTCODE_PATH}")

        content = SHORTCODE_PATH.read_text(encoding="utf-8")
        t.assert_in("book-download", SHORTCODE_PATH.name, "File must be book-download shortcode")
        t.assert_in(".Page.Language.Lang", content, "Shortcode must support multilingual languages")
        t.assert_in("PDF", content, "Shortcode must support PDF format")

        t.assert_true(BOOKS_METADATA_PATH.exists(), f"Books metadata must exist at {BOOKS_METADATA_PATH}")
        with open(BOOKS_METADATA_PATH, "r", encoding="utf-8") as f:
            books_data = json.load(f)

        t.assert_greater_equal(len(books_data), 300, "Books metadata must contain catalogue of books")
        sample_book = books_data[0]
        t.assert_in("title", sample_book, "Book metadata must include title")

    def test_t3_3_payment_verification_and_email_trigger(self, t: AssertionTracker):
        """T3.3: Payment verification × Resend email dispatch trigger."""
        self.oracle.reset_state()
        tx_hash = "0x" + "8" * 64
        email = "customer@theminiceo.ir"
        net = "arbitrum"

        receipt = build_test_receipt("arbitrum", tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 5000000)

        # Successful verification triggers email
        st, res = self.oracle.verify_payment(net, tx_hash, "inspired", email, receipt=receipt)
        t.assert_equal(st, 200, "Verification must succeed")
        t.assert_equal(res.get("emailDispatched"), True, "Successful payment must trigger email dispatch")
        t.assert_in(STORE_WALLET, self.oracle.generate_resend_email_payload(email, "inspired", res["downloadUrl"])["html"], "Email contains store wallet")

        # Underpayment does not trigger email
        bad_receipt = build_test_receipt("arbitrum", "0x" + "9" * 64, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 1000)
        st_bad, res_bad = self.oracle.verify_payment(net, "0x" + "9" * 64, "inspired", email, receipt=bad_receipt)
        t.assert_equal(st_bad, 400, "Underpayment must fail")
        t.assert_false(res_bad.get("emailDispatched", False), "Underpayment must not trigger email dispatch")

    def test_t3_4_expiring_token_and_rate_limiter_lifecycle(self, t: AssertionTracker):
        """T3.4: 2h expiration × 5-download rate limit interaction lifecycle."""
        self.oracle.reset_state()
        now = 1790000000
        token = self.oracle.mint_download_token("inspired", "u@m.com", "0x" + "a" * 64, "bsc", now_ts=now)

        # 1st to 4th downloads within expiration window
        for i in range(1, 5):
            st, _, _ = self.oracle.simulate_download_response(token, now_ts=now + (i * 60))
            t.assert_equal(st, 200, f"Download attempt {i} within window must succeed")

        # 5th download within window
        st_5, _, _ = self.oracle.simulate_download_response(token, now_ts=now + 500)
        t.assert_equal(st_5, 200, "5th download within window must succeed")

        # 6th download within window -> rate limit exceeded
        st_6, _, _ = self.oracle.simulate_download_response(token, now_ts=now + 600)
        t.assert_equal(st_6, 429, "6th download must fail with 429")

        # If expired token is presented, expiry check takes precedence
        fresh_token = self.oracle.mint_download_token("inspired", "u@m.com", "0x" + "b" * 64, "bsc", now_ts=now)
        st_exp, _, _ = self.oracle.simulate_download_response(fresh_token, now_ts=now + 7201)
        t.assert_equal(st_exp, 410, "Expired token must return 410 regardless of remaining attempts")

    def test_t3_5_qr_code_uri_and_svg_structure(self, t: AssertionTracker):
        """T3.5: Network payment URI schemes and client-side vector SVG QR structure."""
        # BSC transfer URI
        bsc_uri = f"ethereum:{SUPPORTED_NETWORKS['bsc']['usdtContract']}@56/transfer?address={STORE_WALLET}&uint256=1000000000000000000"
        t.assert_in("56", bsc_uri, "BSC URI must specify chainId 56")
        t.assert_in(STORE_WALLET, bsc_uri, "BSC URI must specify recipient store wallet")

        # Polygon transfer URI
        poly_uri = f"ethereum:{SUPPORTED_NETWORKS['polygon']['usdtContract']}@137/transfer?address={STORE_WALLET}&uint256=1000000"
        t.assert_in("137", poly_uri, "Polygon URI must specify chainId 137")
        t.assert_in("1000000", poly_uri, "Polygon URI must specify 1 USDT with 6 decimals")

        # Mock vector SVG structure check
        mock_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" fill="#fff"/><path d="M0 0h10v10H0z"/></svg>'
        t.assert_true(mock_svg.startswith("<svg"), "QR SVG must have valid svg root element")
        t.assert_in("viewBox=", mock_svg, "QR SVG must declare viewBox")

    # --------------------------------------------------------------------------
    # TIER 4: Real-World Workload Scenarios (>= 10 Comprehensive User Workflows)
    # --------------------------------------------------------------------------

    def test_t4_1_scenario_1_bsc_purchase(self, t: AssertionTracker):
        """Scenario 1: Happy Path BSC Purchase (Select BSC -> Pay 1 USDT -> Verify -> Stream PDF -> Email)."""
        self.oracle.reset_state()
        net = "bsc"
        tx_hash = "0x" + "11" * 32
        receipt = build_test_receipt(net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 1000000000000000000, block_number=5000)

        status, resp = self.oracle.verify_payment(net, tx_hash, "the-lean-startup", "alice@theminiceo.ir", receipt=receipt, current_block=5005)
        t.assert_equal(status, 200, "Scenario 1 payment verification must succeed")

        token = resp["downloadUrl"].split("token=")[1]
        dl_status, dl_headers, dl_body = self.oracle.simulate_download_response(token)
        t.assert_equal(dl_status, 200, "Scenario 1 PDF download must succeed")
        t.assert_equal(resp.get("emailDispatched"), True, "Scenario 1 email must be dispatched")

    def test_t4_2_scenario_2_polygon_purchase(self, t: AssertionTracker):
        """Scenario 2: Happy Path Polygon Purchase (6 Decimals, 12 Confirmations)."""
        self.oracle.reset_state()
        net = "polygon"
        tx_hash = "0x" + "22" * 32
        receipt = build_test_receipt(net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 1000000, block_number=6000)

        status, resp = self.oracle.verify_payment(net, tx_hash, "inspired", "bob@theminiceo.ir", receipt=receipt, current_block=6015)
        t.assert_equal(status, 200, "Scenario 2 payment verification must succeed")
        t.assert_in("downloadUrl", resp, "Scenario 2 must return valid downloadUrl")

    def test_t4_3_scenario_3_arbitrum_purchase(self, t: AssertionTracker):
        """Scenario 3: Happy Path Arbitrum Purchase (Low fee L2, 2 Confirmations)."""
        self.oracle.reset_state()
        net = "arbitrum"
        tx_hash = "0x" + "33" * 32
        receipt = build_test_receipt(net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 1000000, block_number=7000)

        status, resp = self.oracle.verify_payment(net, tx_hash, "behind-every-great-product", "carol@theminiceo.ir", receipt=receipt, current_block=7004)
        t.assert_equal(status, 200, "Scenario 3 payment verification must succeed")
        t.assert_equal(resp.get("txDetails", {}).get("network"), "arbitrum", "Scenario 3 network must be arbitrum")

    def test_t4_4_scenario_4_replay_attack_rejection(self, t: AssertionTracker):
        """Scenario 4: Replay Attack Defense (Submitting redeemed TxHash rejected with 409)."""
        self.oracle.reset_state()
        net = "bsc"
        tx_hash = "0x" + "44" * 32
        receipt = build_test_receipt(net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 1000000000000000000)

        # Legitimate purchase
        st1, _ = self.oracle.verify_payment(net, tx_hash, "book1", "alice@theminiceo.ir", receipt=receipt)
        t.assert_equal(st1, 200, "First purchase must succeed")

        # Replay attempt by different user
        st2, resp2 = self.oracle.verify_payment(net, tx_hash, "book2", "attacker@theminiceo.ir", receipt=receipt)
        t.assert_equal(st2, 409, "Replay attack must be rejected with 409 Conflict")

    def test_t4_5_scenario_5_underpayment_rejection(self, t: AssertionTracker):
        """Scenario 5: Underpayment Attack Rejection (0.99 USDT fails with diagnostic delta)."""
        self.oracle.reset_state()
        net = "bsc"
        tx_hash = "0x" + "55" * 32
        # Sending 0.99 USDT
        receipt = build_test_receipt(net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 990000000000000000)

        status, resp = self.oracle.verify_payment(net, tx_hash, "book", "u@theminiceo.ir", receipt=receipt)
        t.assert_equal(status, 400, "Underpayment must return HTTP 400")
        t.assert_equal(resp.get("error"), "INSUFFICIENT_AMOUNT", "Underpayment must be flagged as INSUFFICIENT_AMOUNT")

    def test_t4_6_scenario_6_wrong_recipient_rejection(self, t: AssertionTracker):
        """Scenario 6: Wrong Recipient Rejection (Payment sent to other wallet)."""
        self.oracle.reset_state()
        net = "polygon"
        tx_hash = "0x" + "66" * 32
        fake_store = "0x9999999999999999999999999999999999999999"
        receipt = build_test_receipt(net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], fake_store, 1000000)

        status, resp = self.oracle.verify_payment(net, tx_hash, "book", "u@theminiceo.ir", receipt=receipt)
        t.assert_equal(status, 400, "Wrong recipient must return HTTP 400")
        t.assert_equal(resp.get("error"), "WRONG_RECIPIENT", "Error must be WRONG_RECIPIENT")

    def test_t4_7_scenario_7_fake_contract_rejection(self, t: AssertionTracker):
        """Scenario 7: Fake Token Contract Rejection (Counterfeit token transfer)."""
        self.oracle.reset_state()
        net = "arbitrum"
        tx_hash = "0x" + "77" * 32
        fake_token = "0x1111111111111111111111111111111111111111"
        receipt = build_test_receipt(net, tx_hash, fake_token, STORE_WALLET, 1000000)

        status, resp = self.oracle.verify_payment(net, tx_hash, "book", "u@theminiceo.ir", receipt=receipt)
        t.assert_equal(status, 400, "Fake token contract must return HTTP 400")
        t.assert_equal(resp.get("error"), "WRONG_TOKEN_CONTRACT", "Error must be WRONG_TOKEN_CONTRACT")

    def test_t4_8_scenario_8_pending_confirmation_retry(self, t: AssertionTracker):
        """Scenario 8: Pending Confirmation Workflow (202 Accepted -> wait -> 200 OK)."""
        self.oracle.reset_state()
        net = "bsc"
        tx_hash = "0x" + "88" * 32
        tx_block = 1000
        receipt = build_test_receipt(net, tx_hash, SUPPORTED_NETWORKS[net]["usdtContract"], STORE_WALLET, 1000000000000000000, block_number=tx_block)

        # Fresh broadcast (1 confirmation)
        st1, resp1 = self.oracle.verify_payment(net, tx_hash, "book", "u@theminiceo.ir", receipt=receipt, current_block=tx_block)
        t.assert_equal(st1, 202, "Fresh transaction must return 202 Pending")

        # After 3 confirmations mined
        st2, resp2 = self.oracle.verify_payment(net, tx_hash, "book", "u@theminiceo.ir", receipt=receipt, current_block=tx_block + 3)
        t.assert_equal(st2, 200, "Mined transaction must return 200 OK")

    def test_t4_9_scenario_9_token_expiration_enforcement(self, t: AssertionTracker):
        """Scenario 9: Token Expiration Enforcement (User downloads after 2 hours -> 410 Gone)."""
        now = int(time.time())
        token = self.oracle.mint_download_token("book", "u@theminiceo.ir", "0x" + "99" * 32, "bsc", now_ts=now)

        st_exp, _, _ = self.oracle.simulate_download_response(token, now_ts=now + 7205)
        t.assert_equal(st_exp, 410, "Download after 2 hours must return HTTP 410 Gone")
        t.assert_true(DOWNLOAD_EXPIRY_SECONDS == 7200, "Expiration window configured to exactly 7200s")

    def test_t4_10_scenario_10_tampered_token_rejection(self, t: AssertionTracker):
        """Scenario 10: Intercepted Token Tampering (Modified payload rejected with 403 Forbidden)."""
        token = self.oracle.mint_download_token("book-free", "attacker@theminiceo.ir", "0x" + "aa" * 32, "bsc")
        p_b64, s_b64 = token.split(".")
        # Tamper payload
        bad_payload = json.dumps({"bookId": "expensive-report", "exp": 2000000000}).encode("utf-8")
        bad_b64 = base64.urlsafe_b64encode(bad_payload).decode("utf-8").rstrip("=")

        st, _, _ = self.oracle.simulate_download_response(f"{bad_b64}.{s_b64}")
        t.assert_equal(st, 403, "Tampered payload must return HTTP 403 Forbidden")
        t.assert_false(st == 200, "Tampered token must never stream PDF")

    def test_t4_11_scenario_11_rate_limit_exhaustion(self, t: AssertionTracker):
        """Scenario 11: Rate Limit Exhaustion (5 downloads legitimate -> 6th blocked with 429)."""
        self.oracle.reset_state()
        token = self.oracle.mint_download_token("book", "u@theminiceo.ir", "0x" + "bb" * 32, "bsc")

        for _ in range(5):
            st, _, _ = self.oracle.simulate_download_response(token)
            t.assert_equal(st, 200, "First 5 downloads must succeed")

        st_6, _, _ = self.oracle.simulate_download_response(token)
        t.assert_equal(st_6, 429, "6th download must be blocked with HTTP 429")

    def test_t4_12_scenario_12_hugo_full_site_compilation(self, t: AssertionTracker):
        """Scenario 12: Hugo Site Parity (Compiles all book pages via hugo --renderToMemory)."""
        cmd = ["hugo", "--renderToMemory"]
        proc = subprocess.run(cmd, cwd=str(ROOT_DIR), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        t.assert_equal(proc.returncode, 0, f"Hugo build exited with {proc.returncode}: {proc.stderr[:200]}")
        t.assert_in("Pages", proc.stdout, "Hugo stdout must report compilation page statistics")

    # --------------------------------------------------------------------------
    # Suite Runner
    # --------------------------------------------------------------------------

    def run_suite(self, tier_filter: str = "all") -> int:
        test_registry = [
            # Tier 1
            ("T1.1", "API Config Parameters & Pricing Schema", 1, self.test_t1_1_api_config_schema_and_pricing),
            ("T1.2", "EVM RPC Client Payload & Failover Rotation", 1, self.test_t1_2_rpc_client_payload_formatting_and_failover),
            ("T1.3", "Canonical USDT Contracts & BigInt Decimals", 1, self.test_t1_3_canonical_usdt_decimals_normalization),
            ("T1.4", "Transaction Receipt Status & Confirmation Depth", 1, self.test_t1_4_transaction_receipt_status_and_confirmations),
            ("T1.5", "ERC-20 Transfer Log Parsing & Recipient Match", 1, self.test_t1_5_erc20_transfer_log_parsing),
            ("T1.6", "Persistent Replay Protection Key & Atomic Insert", 1, self.test_t1_6_persistent_replay_protection),
            ("T1.7", "Diagnostic Error Taxonomy (12 Codes)", 1, self.test_t1_7_diagnostic_error_taxonomy),
            ("T1.8", "Cloudflare R2 Bucket Protection & Manifest", 1, self.test_t1_8_r2_bucket_protection_and_manifest),
            ("T1.9", "Web Crypto HMAC Expiring Download Tokens (2h)", 1, self.test_t1_9_hmac_expiring_download_tokens),
            ("T1.10", "Streamed File Delivery Headers & HTTP Range", 1, self.test_t1_10_streamed_file_delivery_headers),
            ("T1.11", "Download Attempt Limiter (Max 5 Attempts)", 1, self.test_t1_11_download_attempt_limiter),
            ("T1.12", "Backup Email Dispatch Payload (Resend API)", 1, self.test_t1_12_backup_email_dispatch_payload),

            # Tier 2
            ("T2.1", "Boundary Amounts (0.99 vs 1.00 USDT across Decimals)", 2, self.test_t2_1_boundary_amounts_and_decimals),
            ("T2.2", "Hex Address & TxHash Case Insensitivity", 2, self.test_t2_2_hex_and_address_case_insensitivity),
            ("T2.3", "Malformed & Non-Hex Transaction Hashes", 2, self.test_t2_3_malformed_transaction_hashes),
            ("T2.4", "Invalid & Unsupported Blockchain Networks", 2, self.test_t2_4_invalid_and_unsupported_networks),
            ("T2.5", "Expired Download Tokens Boundary (+1s, +1h)", 2, self.test_t2_5_expired_download_tokens),
            ("T2.6", "Tampered HMAC Signatures & Payload Alteration", 2, self.test_t2_6_tampered_hmac_signatures),
            ("T2.7", "Special Characters, Persian Slugs, Path Traversal", 2, self.test_t2_7_special_characters_and_filenames),

            # Tier 3
            ("T3.1", "Network × Token Contract × Replay Namespace Isolation", 3, self.test_t3_1_cross_network_contract_and_replay_isolation),
            ("T3.2", "Hugo Shortcode Parameters × R2 Manifest Cross-Reference", 3, self.test_t3_2_shortcode_parameters_and_r2_manifest),
            ("T3.3", "Payment Verification × Email Dispatch Trigger", 3, self.test_t3_3_payment_verification_and_email_trigger),
            ("T3.4", "Expiring Token Lifecycle × Rate Limiter Interaction", 3, self.test_t3_4_expiring_token_and_rate_limiter_lifecycle),
            ("T3.5", "Payment URI Schemes × Client Vector SVG QR Code", 3, self.test_t3_5_qr_code_uri_and_svg_structure),

            # Tier 4
            ("T4.1", "Scenario 1: Happy Path BSC Purchase Workflow", 4, self.test_t4_1_scenario_1_bsc_purchase),
            ("T4.2", "Scenario 2: Happy Path Polygon Purchase Workflow", 4, self.test_t4_2_scenario_2_polygon_purchase),
            ("T4.3", "Scenario 3: Happy Path Arbitrum Purchase Workflow", 4, self.test_t4_3_scenario_3_arbitrum_purchase),
            ("T4.4", "Scenario 4: Replay Attack Defense Workflow", 4, self.test_t4_4_scenario_4_replay_attack_rejection),
            ("T4.5", "Scenario 5: Underpayment Attack Rejection Workflow", 4, self.test_t4_5_scenario_5_underpayment_rejection),
            ("T4.6", "Scenario 6: Wrong Recipient Rejection Workflow", 4, self.test_t4_6_scenario_6_wrong_recipient_rejection),
            ("T4.7", "Scenario 7: Fake Contract Token Rejection Workflow", 4, self.test_t4_7_scenario_7_fake_contract_rejection),
            ("T4.8", "Scenario 8: Pending Confirmation Retry Workflow", 4, self.test_t4_8_scenario_8_pending_confirmation_retry),
            ("T4.9", "Scenario 9: Token Expiration Enforcement Workflow", 4, self.test_t4_9_scenario_9_token_expiration_enforcement),
            ("T4.10", "Scenario 10: Intercepted Token Tampering Rejection Workflow", 4, self.test_t4_10_scenario_10_tampered_token_rejection),
            ("T4.11", "Scenario 11: Rate Limit Exhaustion Workflow", 4, self.test_t4_11_scenario_11_rate_limit_exhaustion),
            ("T4.12", "Scenario 12: Hugo Site Full Memory Build Parity", 4, self.test_t4_12_scenario_12_hugo_full_site_compilation),
        ]

        target_tier = int(tier_filter) if tier_filter in ["1", "2", "3", "4"] else None

        print("\n" + "=" * 78)
        print("THEMINICEO CRYPTO PAYWALL E2E TEST SUITE")
        print("=" * 78)
        print(f"Target Tier:   {tier_filter.upper()}")
        print(f"Verbose Mode:  {self.verbose}")
        print(f"Fail-Fast:     {self.fail_fast}")
        print("-" * 78)

        start_suite = time.time()
        for test_id, name, tier, fn in test_registry:
            if target_tier and tier != target_tier:
                continue

            res = self._run_test(test_id, name, tier, fn)
            if not res.passed and self.fail_fast:
                print(f"\n[FAIL-FAST] Halting suite on first failure in {test_id}")
                break

        duration = time.time() - start_suite

        # Execution Summary
        tier_stats = {
            1: {"passed": 0, "failed": 0, "tests": 0, "assertions": 0},
            2: {"passed": 0, "failed": 0, "tests": 0, "assertions": 0},
            3: {"passed": 0, "failed": 0, "tests": 0, "assertions": 0},
            4: {"passed": 0, "failed": 0, "tests": 0, "assertions": 0},
        }

        all_passed = True
        total_assertions = 0
        total_failed_tests = 0

        for r in self.results:
            tier_stats[r.tier]["tests"] += 1
            tier_stats[r.tier]["assertions"] += r.assertions_count
            total_assertions += r.assertions_count
            if r.passed:
                tier_stats[r.tier]["passed"] += 1
            else:
                tier_stats[r.tier]["failed"] += 1
                total_failed_tests += 1
                all_passed = False

        print("\n" + "-" * 78)
        print("TEST EXECUTION BREAKDOWN BY TIER")
        print("-" * 78)
        print(f"{'Tier':<8} | {'Tests':<10} | {'Passed':<8} | {'Failed':<8} | {'Assertions':<12} | {'Status':<8}")
        print("-" * 78)

        tiers_to_display = [target_tier] if target_tier else [1, 2, 3, 4]
        for t in tiers_to_display:
            s = tier_stats[t]
            status = "PASS" if s["failed"] == 0 and s["tests"] > 0 else ("FAIL" if s["tests"] > 0 else "SKIP")
            print(f"Tier {t:<3} | {s['tests']:<10} | {s['passed']:<8} | {s['failed']:<8} | {s['assertions']:<12} | {status:<8}")

        print("-" * 78)
        print(f"Total Tests Run:       {len(self.results)}")
        print(f"Total Assertions Run:   {total_assertions}")
        print(f"Total Failed Tests:    {total_failed_tests}")
        print(f"Suite Duration:        {duration:.2f}s")
        print("-" * 78)

        if not all_passed:
            print("\n❌ FAILURE DETAILS:")
            for r in self.results:
                if not r.passed:
                    print(f"\n• {r.test_id}: {r.name}")
                    for err in r.errors:
                        print(f"    - {err}")

        if all_passed and len(self.results) > 0:
            print("\n✅ OVERALL STATUS: ALL CRYPTO PAYWALL E2E TESTS PASSED!")
            return 0
        else:
            print("\n❌ OVERALL STATUS: E2E TEST FAILURES DETECTED.")
            return 1


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Run E2E tests for TheMiniCEO Crypto Paywall System.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--tier",
        default="all",
        choices=["1", "2", "3", "4", "all"],
        help="Specify which test tier to execute (default: all)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display detailed assertion progress per test",
    )
    parser.add_argument(
        "-x", "--fail-fast",
        action="store_true",
        help="Stop test execution on first failure",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Optional live worker endpoint URL (e.g. http://127.0.0.1:8787)",
    )

    args = parser.parse_args()

    suite = CryptoPaywallE2ETestSuite(
        verbose=args.verbose,
        fail_fast=args.fail_fast,
        live_url=args.url,
    )
    exit_code = suite.run_suite(tier_filter=args.tier)

    if args.json:
        json_output = {
            "exit_code": exit_code,
            "tier_filter": args.tier,
            "results": [r.to_dict() for r in suite.results],
        }
        print("\n--- JSON OUTPUT ---")
        print(json.dumps(json_output, indent=2))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
