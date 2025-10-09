import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()


class DataClient:
    def __init__(self):
        self.data_url = os.environ.get("DATA_HOST", "https://data-api.polymarket.com")
        self.positions_endpoint = self.data_url + "/positions"
        self.closed_positions_endpoint = self.data_url + "/closed-positions"
        self.value_endpoint = self.data_url + "/value"
        self.trades_endpoint = self.data_url + "/trades"

    # ---------- user-scoped reads ----------

    def get_positions(self, user: str, querystring_params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Current (open) positions for the wallet/user.
        NOTE: If you trade via a funder/proxy, pass the *funder* address here.
        """
        params = dict(querystring_params or {})
        params["user"] = user
        response = httpx.get(self.positions_endpoint, params=params)
        return response.json()

    def get_closed_positions(self, user: str, querystring_params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Closed positions (resolved/settled) with realized PnL, etc.
        """
        params = dict(querystring_params or {})
        params["user"] = user
        response = httpx.get(self.closed_positions_endpoint, params=params)
        return response.json()

    def get_portfolio_value(self, user: str) -> Any:
        """
        Aggregated wallet value: totalValue, cash, unsettled, pnl, etc.
        """
        response = httpx.get(self.value_endpoint, params={"user": user})
        return response.json()

    def get_trades(
            self,
            user: str,
            querystring_params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        User trades/fills. Optional filters can include:
        - limit, cursor
        - since, until (epoch seconds)
        - market (market_id), token_id
        """
        params = dict(querystring_params or {})
        params["user"] = user
        response = httpx.get(self.trades_endpoint, params=params)
        return response.json()

if __name__ == "__main__":
    client = DataClient()
    test_user = "0x1d9eedff0b086a19906f3d3ce5c235078ec0dc6a"
    # print(client.get_positions(test_user, {"limit": 5}))
    # print(client.get_closed_positions(test_user, {"limit": 5}))
    print(client.get_portfolio_value(test_user))
    # print(client.get_trades(test_user, {"limit": 5}))