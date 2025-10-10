from typing import Any, Dict, Optional, Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from py_clob_client.clob_types import OrderType

from .client.clob import CLOBClient
from .client.data import DataClient
from .client.gamma import GammaClient

load_dotenv()

mcp = FastMCP("Polymarket MCP")

data = DataClient()
gamma = GammaClient()
clob = CLOBClient()


@mcp.tool(description="Get a specific market on Polymarket using Gamma API.")
async def get_market(slug: str) -> Dict[str, Any]:
    """
    Get a specific market by slug from the Gamma API.

    Parameters:
    - slug: The market slug (e.g., "will-boris-johnson-win
    """
    try:
        if not gamma:
            return {"error": "Polymarket Gamma client not initialized"}

        markets = gamma.get_markets(querystring_params={"slug": slug}, parse_pydantic=True)
        return {"markets": markets, "count": len(markets)}
    except Exception as e:
        return {"error": f"Error getting market: {str(e)}", "market": None}


@mcp.tool(description="Get a list of all available markets on Polymarket using CLOB API.")
async def get_markets(limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Get a list of all available markets from the CLOB API.

    Parameters:
    - active_only: If True, only return live/active markets
    - limit: Maximum number of markets to return
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        markets = gamma.get_current_markets(limit) if limit is not None else gamma.get_all_current_markets()
        return {"markets": markets, "count": len(markets)}
    except Exception as e:
        return {"error": f"Error getting markets: {str(e)}", "markets": []}


@mcp.tool(description="Get the order book for a specific token.")
async def get_order_book(token_id: str) -> Dict[str, Any]:
    """
    Get the current order book for a specific token.

    Parameters:
    - token_id: The CLOB token ID
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        orderbook = clob.get_orderbook(token_id)

        # Convert to dict format
        return {
            "token_id": token_id,
            "bids": [{"price": b.price, "size": b.size} for b in orderbook.bids],
            "asks": [{"price": a.price, "size": a.size} for a in orderbook.asks]
        }
    except Exception as e:
        return {"error": f"Error getting order book: {str(e)}"}


@mcp.tool(description="Get the mid price for a specific token.")
async def get_mid_price(token_id: str) -> Dict[str, Any]:
    """
    Get the mid price for a specific token based on the order book.

    Parameters:
    - token_id: The CLOB token ID
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        mid_price = clob.get_mid_from_book(token_id)

        return {
            "token_id": token_id,
            "mid_price": mid_price
        }
    except Exception as e:
        return {"error": f"Error getting mid price: {str(e)}"}


@mcp.tool(description="Get the current price for a specific token and side.")
async def get_price(token_id: str, side: Literal["BUY", "SELL"]) -> Dict[str, Any]:
    """
    Get the current price for a specific token and side.

    Parameters:
    - token_id: The CLOB token ID
    - side: Either "BUY" or "SELL"
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        price = clob.get_price(token_id, side)

        return {
            "token_id": token_id,
            "side": side,
            "price": price
        }
    except Exception as e:
        return {"error": f"Error getting price: {str(e)}"}


@mcp.tool(description="Place a limit order on Polymarket.")
async def place_limit_order(
        token_id: str,
        price: float,
        size: float,
        side: Literal["BUY", "SELL"] = "BUY",
) -> Dict[str, Any]:
    """
    Place a limit order on Polymarket.

    Parameters:
    - token_id: The CLOB token ID
    - price: The limit price
    - size: The order size
    - side: Either "BUY" or "SELL"
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        order_id = clob.execute_limit_order(token_id, price, size, side)

        return {
            "order_id": order_id,
            "token_id": token_id,
            "price": price,
            "size": size,
            "side": side
        }
    except Exception as e:
        return {"error": f"Error placing limit order: {str(e)}"}


@mcp.tool(description="Place a market order on Polymarket.")
async def place_market_order(
        token_id: str,
        amount: float,
        order_type: str = "FOK"
) -> Dict[str, Any]:
    """
    Place a market order on Polymarket.

    Parameters:
    - token_id: The CLOB token ID
    - amount: The notional amount in quote units
    - order_type: Order type (FOK, IOC, GTC)
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        # Convert string to OrderType enum
        order_type_enum = getattr(OrderType, order_type, OrderType.FOK)
        result = clob.execute_market_order(token_id, amount, order_type_enum)

        return {
            "result": result,
            "token_id": token_id,
            "amount": amount,
            "order_type": order_type
        }
    except Exception as e:
        return {"error": f"Error placing market order: {str(e)}"}


@mcp.tool(description="Cancel an existing order by ID.")
async def cancel_order(order_id: str) -> Dict[str, Any]:
    """
    Cancel an existing order by ID.

    Parameters:
    - order_id: The ID of the order to cancel
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        result = clob.cancel_order(order_id)

        return {
            "result": result,
            "order_id": order_id
        }
    except Exception as e:
        return {"error": f"Error cancelling order: {str(e)}"}


@mcp.tool(description="Get USDC balance for a specific user or the configured wallet if user not specified.")
async def get_usdc_balance(user: str = None) -> Dict[str, Any]:
    """
    Get the USDC balance for the configured wallet.
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        balance = data.get_usdc_balance(user)

        return {
            "address": clob.address,
            "usdc_balance": balance
        }
    except Exception as e:
        return {"error": f"Error getting USDC balance: {str(e)}"}


@mcp.tool(description="Get portfolio value for a specific user or the configured wallet if user not specified.")
async def get_portfolio_value(user: str = None) -> Dict[str, Any]:
    """
    Get the aggregated portfolio value for a specific user.

    Parameters:
    - user: The wallet address of the user
    """
    try:
        if not data:
            return {"error": "Polymarket Data client not initialized"}

        value = data.get_portfolio_value(user)

        return {
            "user": user,
            "portfolio_value": value
        }
    except Exception as e:
        return {"error": f"Error getting portfolio value: {str(e)}", "portfolio_value": {}}


@mcp.tool(description="Get positions for a specific user or the configured wallet if user not specified.")
async def get_positions(user: str = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Get current (open) positions for a specific user.

    Parameters:
    - user: The wallet address of the user
    - limit: Maximum number of positions to return
    """
    try:
        if not data:
            return {"error": "Polymarket Data client not initialized"}

        params = {"limit": limit} if limit is not None else {}
        positions = data.get_positions(user, querystring_params=params)

        return {
            "user": user,
            "positions": positions,
            "count": len(positions) if isinstance(positions, list) else 0
        }
    except Exception as e:
        return {"error": f"Error getting positions: {str(e)}", "positions": []}


@mcp.tool(description="Get closed positions for a specific user or the configured wallet if user not specified.")
async def get_closed_positions(user: str = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Get closed (settled) positions for a specific user.

    Parameters:
    - user: The wallet address of the user
    - limit: Maximum number of closed positions to return
    """
    try:
        if not data:
            return {"error": "Polymarket Data client not initialized"}

        params = {"limit": limit} if limit is not None else {}
        closed_positions = data.get_closed_positions(user, querystring_params=params)

        return {
            "user": user,
            "closed_positions": closed_positions,
            "count": len(closed_positions) if isinstance(closed_positions, list) else 0
        }
    except Exception as e:
        return {"error": f"Error getting closed positions: {str(e)}", "closed_positions": []}


@mcp.tool(description="Get trades for a specific user or the configured wallet if user not specified.")
async def get_trades(user: str = None, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Get trades/fills for a specific user.

    Parameters:
    - user: The wallet address of the user
    - limit: Maximum number of trades to return
    """
    try:
        if not data:
            return {"error": "Polymarket Data client not initialized"}

        params = {"limit": limit} if limit is not None else {}
        trades = data.get_trades(user, querystring_params=params)

        return {
            "user": user,
            "trades": trades,
            "count": len(trades) if isinstance(trades, list) else 0
        }
    except Exception as e:
        return {"error": f"Error getting trades: {str(e)}", "trades": []}


@mcp.tool(description="Redeem a position for a specific condition ID and index sets.")
async def redeem_position(condition_id: str, index_sets: list[int]) -> Dict[str, Any]:
    """
    Redeem a position for a specific condition ID and index sets.

    Parameters:
    - condition_id: The condition ID of the market
    - index_sets: List of index sets to redeem
    """
    try:
        if not data:
            return {"error": "Polymarket Data client not initialized"}

        tx_hash = data.redeem_position(condition_id, index_sets)

        return {
            "condition_id": condition_id,
            "index_sets": index_sets,
            "tx_hash": tx_hash
        }
    except Exception as e:
        return {"error": f"Error redeeming position: {str(e)}"}