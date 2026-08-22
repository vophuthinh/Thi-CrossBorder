"""
Wealify API Client — Live data integration.

Endpoints discovered from dev-app.wealify.com (Nuxt.js source):
  Main API:  https://dev-api.wealify.com/api/
  VC API:    https://dev-api.virtual-card.wealify.com/api/

Authentication: JWT Bearer token via POST /v1/login
"""
from __future__ import annotations

import os
import time
import logging
from typing import Any, Optional

import requests

logger = logging.getLogger("wealify_client")


class WealifyClient:
    """Client for Wealify REST API (dev environment)."""

    def __init__(
        self,
        api_url: str | None = None,
        vc_api_url: str | None = None,
        email: str | None = None,
        password: str | None = None,
        timeout: int = 15,
    ):
        self.api_url = (api_url or os.getenv(
            "WEALIFY_API_URL", "https://dev-api.wealify.com/api"
        )).rstrip("/")
        self.vc_api_url = (vc_api_url or os.getenv(
            "WEALIFY_VC_API_URL", "https://dev-api.virtual-card.wealify.com/api"
        )).rstrip("/")
        self._email = email or os.getenv("WEALIFY_EMAIL", "")
        self._password = password or os.getenv("WEALIFY_PASSWORD", "")
        self._timeout = timeout

        # Token cache
        self._token: str | None = None
        self._token_expires_at: float = 0  # unix timestamp

    # ─── Authentication ──────────────────────────────────

    def login(self) -> str:
        """Authenticate and return JWT access token. Caches token until expiry."""
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token

        if not self._email or not self._password:
            raise ValueError(
                "WEALIFY_EMAIL and WEALIFY_PASSWORD must be set "
                "(env vars or constructor args)"
            )

        resp = requests.post(
            f"{self.api_url}/v1/login",
            json={"email": self._email, "password": self._password},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        if not data.get("status"):
            raise RuntimeError(f"Wealify login failed: {data}")

        token_data = data["data"]
        self._token = token_data["access_token"]
        # Token expires in access_expired_in ms, convert to unix timestamp
        expires_in_sec = token_data.get("access_expired_in", 86400000) / 1000
        self._token_expires_at = time.time() + expires_in_sec

        logger.info("Wealify login successful (token cached for %.0f min)", expires_in_sec / 60)
        return self._token

    def _headers(self) -> dict[str, str]:
        """Get auth headers, auto-login if needed."""
        token = self.login()
        return {"Authorization": f"Bearer {token}"}

    # ─── Virtual Accounts (VA) ───────────────────────────

    def get_va_list(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get list of Virtual Accounts, across all pages.
        Endpoint: GET /v2/virtual-accounts
        """
        all_items = []
        page = 1
        try:
            while True:
                resp = requests.get(
                    f"{self.api_url}/v2/virtual-accounts",
                    headers=self._headers(),
                    params={"page": page, "limit": limit, "wallet_type": "VA"},
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                items = data.get("items", [])
                
                if not items:
                    break
                    
                for va in items:
                    if "account_number" in va and isinstance(va["account_number"], str):
                        acct = va["account_number"]
                        if len(acct) > 4:
                            va["account_number"] = f"****{acct[-4:]}"
                            
                all_items.extend(items)
                
                next_page = data.get("next_page")
                if not next_page:
                    break
                page = next_page
                
            return all_items
        except Exception as e:
            logger.warning("Failed to fetch VA list: %s", e)
            return all_items

    def get_va_list_v1(self, page: int = 1, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get list of Virtual Accounts (v1 — simpler response).
        Endpoint: GET /v1/virtual-accounts?page=1&limit=100&wallet_type=VA
        """
        try:
            resp = requests.get(
                f"{self.api_url}/v1/virtual-accounts",
                headers=self._headers(),
                params={"page": page, "limit": limit, "wallet_type": "VA"},
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            items = data.get("data", [])
            for va in items:
                if "account_number" in va and isinstance(va["account_number"], str):
                    acct = va["account_number"]
                    if len(acct) > 4:
                        va["account_number"] = f"****{acct[-4:]}"
            return items
        except Exception as e:
            logger.warning("Failed to fetch VA list v1: %s", e)
            return []

    def get_wallets_balance(self) -> list[dict[str, Any]]:
        """
        Get wallet balances.
        Endpoint: GET /v2/wallets
        Returns: [{"balance": 274436000, "currency": "VND", "type": "VA"}, ...]
        """
        try:
            resp = requests.get(
                f"{self.api_url}/v2/wallets",
                headers=self._headers(),
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])
        except Exception as e:
            logger.warning("Failed to fetch wallet balances: %s", e)
            return []

    # ─── Virtual Cards (VC) ──────────────────────────────

    def get_vc_list(self, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get list of Virtual Cards with embedded transactions, across all pages.
        Endpoint: GET {vc_api_url}/v1/cards
        """
        all_items = []
        page = 1
        try:
            while True:
                resp = requests.get(
                    f"{self.vc_api_url}/v1/cards",
                    headers=self._headers(),
                    params={"page": page, "limit": limit},
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                items = data.get("items", [])
                
                if not items:
                    break
                    
                for card in items:
                    card.pop("cvv", None)
                    if "card_number" in card and "last_four" in card:
                        card["card_number"] = f"****{card['last_four']}"
                all_items.extend(items)
                
                next_page = data.get("next_page")
                if not next_page:
                    break
                page = next_page
                
            return all_items
        except Exception as e:
            logger.warning("Failed to fetch VC list: %s", e)
            return all_items

    def get_vc_transactions(self) -> list[dict[str, Any]]:
        """
        Get all VC transactions from all cards.
        Endpoint: GET {vc_api_url}/v1/transactions
        """
        # First get cards to map names
        cards = self.get_vc_list(limit=100)
        card_map = {c.get("id"): c for c in cards if c.get("id")}
        
        all_txns = []
        page = 1
        try:
            while True:
                resp = requests.get(
                    f"{self.vc_api_url}/v1/transactions",
                    headers=self._headers(),
                    params={"page": page, "limit": 100},
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                items = data.get("items", [])
                
                if not items:
                    break
                    
                for txn in items:
                    cid = txn.get("virtual_card_id")
                    card = card_map.get(cid, {})
                    txn["_card_name"] = card.get("card_name", "Unknown")
                    txn["_card_last4"] = card.get("last_four", "")
                    txn["_card_id"] = cid
                    all_txns.append(txn)
                    
                total_page = data.get("total_page", 0)
                if page >= total_page:
                    break
                page += 1
                
            return all_txns
        except Exception as e:
            logger.warning("Failed to fetch VC transactions: %s", e)
            return all_txns

    def get_va_transactions(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get all VA transactions (deposits/withdrawals) with pagination.
        Endpoint: GET /v2/transactions/va
        """
        all_items = []
        page = 1
        try:
            while True:
                resp = requests.get(
                    f"{self.api_url}/v2/transactions/va",
                    headers=self._headers(),
                    params={"page": page, "limit": limit},
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                items = data.get("items", [])
                if not items:
                    break
                all_items.extend(items)
                
                # Check for next page
                next_page = data.get("next_page")
                if not next_page:
                    break
                page = next_page
                
            return all_items
        except Exception as e:
            logger.warning("Failed to fetch VA transactions: %s", e)
            return all_items

    # ─── User Info ───────────────────────────────────────

    def get_user_info(self) -> dict[str, Any]:
        """Get current user profile from VA list metadata."""
        va_list = self.get_va_list(limit=1)
        if va_list:
            customer = va_list[0].get("customer", {})
            return {
                "id": customer.get("id"),
                "full_name": customer.get("full_name", ""),
                "email": customer.get("email", ""),
                "account_type": customer.get("account_type", ""),
                "tenant": customer.get("tenant", {}).get("name", ""),
            }
        return {}

    # ─── Aggregate: All Data ─────────────────────────────

    def get_all_data(self) -> dict[str, Any]:
        """
        Fetch all available data from Wealify API in one call.
        Returns a dict with standardized keys for downstream processing.
        """
        va_accounts = self.get_va_list()
        va_accounts_v1 = self.get_va_list_v1()
        va_transactions = self.get_va_transactions()
        wallets = self.get_wallets_balance()
        vc_cards = self.get_vc_list(limit=100)
        vc_transactions = self.get_vc_transactions()
        user_info = self.get_user_info()

        return {
            "va_accounts": va_accounts,
            "va_accounts_v1": va_accounts_v1,
            "va_transactions": va_transactions,
            "wallets": wallets,
            "vc_cards": vc_cards,
            "vc_transactions": vc_transactions,
            "user_info": user_info,
            "source": "wealify_live",
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }


# ─── Module-level convenience ────────────────────────────

_client: Optional[WealifyClient] = None


def get_wealify_client() -> WealifyClient:
    """Get or create singleton Wealify client."""
    global _client
    if _client is None:
        _client = WealifyClient()
    return _client
