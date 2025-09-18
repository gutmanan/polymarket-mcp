import os
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from dotenv import load_dotenv
from pydantic import ValidationError
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds, OrderArgs, MarketOrderArgs, OrderType, OrderBookSummary
from py_clob_client.constants import POLYGON
from py_order_utils.builders import OrderBuilder
from py_order_utils.model import OrderData
from py_order_utils.signer import Signer

from src.polymarket_mcp_server.datamodel.objects import SimpleMarket

load_dotenv()


def parse_iso8601(s: str) -> datetime:
    """Python 3.10-friendly parse for timestamps like 2020-11-04T00:00:00Z."""
    if not s:
        # naive max future to pass "is_live"
        return datetime.max.replace(tzinfo=timezone.utc)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


class Polymarket:
    """
    CLOB-first Polymarket client.

    - Uses py-clob-client exclusively.
    - No gamma endpoints.
    - Provides helpers to fetch/normalize markets & events, order book, prices, and place orders.
    """

    def __init__(
            self,
            clob_host: str = "https://clob.polymarket.com",
            chain_id: int = POLYGON,
            polygon_rpc: str = os.getenv("RPC_URL"),
            do_approvals: bool = False,
    ) -> None:
        self.clob_host = clob_host
        self.chain_id = chain_id
        self.private_key = os.getenv("PRIVATE_KEY")
        if not self.private_key:
            raise RuntimeError("Missing PRIVATE_KEY in env")

        # web3 (for approvals/balances; PoA middleware for Polygon)
        self.w3 = Web3(Web3.HTTPProvider(polygon_rpc))
        self.w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
        self.address = self.w3.eth.account.from_key(self.private_key).address

        # CLOB client + optional API creds (if you’ve pre-created them)
        self.client = self._init_client()

        # Known addresses (unchanged from your original; keep if you need on-chain ops)
        self.exchange_address = "0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e"

        # Optional approvals (off by default)
        if do_approvals:
            self._init_approvals()

    # ---------- init helpers ----------

    def _init_client(self) -> ClobClient:
        creds = None
        if os.getenv("CLOB_API_KEY"):
            creds = ApiCreds(
                api_key=os.getenv("CLOB_API_KEY"),
                api_secret=os.getenv("CLOB_SECRET"),
                api_passphrase=os.getenv("CLOB_PASS_PHRASE"),
            )
            client = ClobClient(self.clob_host, key=self.private_key, chain_id=self.chain_id, creds=creds)
        else:
            client = ClobClient(self.clob_host, key=self.private_key, chain_id=self.chain_id)
            client.set_api_creds(client.create_or_derive_api_creds())
        return client

    def _init_approvals(self) -> None:
        """Wire ERC20/1155 approvals if you place on-chain via the exchange contracts.
           Left as a placeholder since most CLOB ops don’t need manual calls here."""
        pass

    # ---------- mapping ----------

    @staticmethod
    def _safe_float(d: Dict[str, Any], key: str, default: float = 0.0) -> float:
        try:
            v = d.get(key, default)
            return float(v) if v is not None else default
        except Exception:
            return default

    # ---------- live/liquidity filters ----------

    @staticmethod
    def is_live(m: SimpleMarket) -> bool:
        return (m.active is True
                and m.closed is False
                and m.archived is False
                and m.accepting_orders is True
                and parse_iso8601(m.end_date_iso) > datetime.now(timezone.utc)
                )

    # ---------- markets & events (CLOB) ----------

    def get_all_markets(self) -> List[SimpleMarket]:
        """
        Fetch all markets from CLOB (sampling API) and return as SimpleMarket list.
        """
        cursor: str | None = ""
        markets_out: List[SimpleMarket] = []

        while True:
            print(cursor)
            resp = self.client.get_sampling_markets(next_cursor=cursor)
            data = resp.get("data", [])
            cursor = resp.get("next_cursor")

            for m in data:
                try:
                    markets_out.append(SimpleMarket.model_validate(m))
                except ValidationError as e:
                    # If a row doesn't fit your schema, skip it
                    # You could log here if you want visibility
                    continue

            if not cursor or cursor == "LTE=":
                break

        return markets_out

    def filter_markets_for_trading(self, markets: List[SimpleMarket]) -> List[SimpleMarket]:
        return [m for m in markets if self.is_live(m)]

    # ---------- order book & prices ----------

    def get_orderbook(self, token_id: str) -> OrderBookSummary:
        return self.client.get_order_book(token_id)

    def get_mid_from_book(self, token_id: str) -> Optional[float]:
        ob = self.get_orderbook(token_id)
        try:
            best_bid = max(float(b.price) for b in ob.bids) if ob.bids else None
            best_ask = min(float(a.price) for a in ob.asks) if ob.asks else None
            if best_bid is None or best_ask is None:
                return None
            return round((best_bid + best_ask) / 2.0, 4)
        except Exception:
            return None

    def get_price(self, token_id: str, side: str) -> float:
        """Spot price helper (CLOB provides a lightweight endpoint)."""
        return float(self.client.get_price(token_id, side=side))

    # ---------- orders ----------

    def build_limit_order(
            self,
            market_token: str,
            price: float,
            size: float,
            side: str = "BUY",  # "BUY" or "SELL"
            fee_bps: int = 1,
            expiration: str = "0",
            nonce: Optional[str] = None,
    ):
        """
        Signed limit order payload using py-order-utils.
        Use execute_limit_order for the CLOB-native path (recommended).
        """
        signer = Signer(self.private_key)
        obuilder = OrderBuilder(self.exchange_address, self.chain_id, signer)

        buy = side.upper() == "BUY"
        side_int = 0 if buy else 1
        maker_amount = size if buy else 0
        taker_amount = size if not buy else 0

        order_data = OrderData(
            maker=self.address,
            tokenId=market_token,
            makerAmount=maker_amount,
            takerAmount=taker_amount,
            feeRateBps=str(fee_bps),
            nonce=nonce or str(round(time.time())),
            side=side_int,
            expiration=expiration,
        )
        return obuilder.build_signed_order(order_data)

    def execute_limit_order(self, price: float, size: float, side: str, token_id: str) -> str:
        """
        CLOB-native limit order. side: 0=BUY, 1=SELL (use py_clob_client.order_builder.constants BUY/SELL)
        """
        return self.client.create_and_post_order(OrderArgs(price=price, size=size, side=side, token_id=token_id))

    def execute_market_order(self, token_id: str, amount: float, order_type: OrderType = OrderType.FOK) -> Dict[
        str, Any]:
        """
        Market order: amount is the notional size in quote units the CLOB expects.
        """
        args = MarketOrderArgs(token_id=token_id, amount=amount)
        signed = self.client.create_market_order(args)
        return self.client.post_order(signed, orderType=order_type)

    # ---------- balances ----------

    def get_usdc_balance(self, usdc_address: str = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174") -> float:
        """USDC balance (Polygon)."""
        erc20_abi = [
            {"name": "balanceOf", "type": "function", "stateMutability": "view",
             "inputs": [{"name": "owner", "type": "address"}], "outputs": [{"name": "", "type": "uint256"}]}
        ]
        usdc = self.w3.eth.contract(address=usdc_address, abi=erc20_abi)
        raw = usdc.functions.balanceOf(self.address).call()
        # USDC has 6 decimals
        return raw / 10 ** 6
