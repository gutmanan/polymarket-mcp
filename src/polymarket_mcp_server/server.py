from typing import Any, Dict, Optional, Literal

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from py_clob_client.clob_types import OrderType

from src.polymarket_mcp_server.client.clob import CLOBClient
from src.polymarket_mcp_server.client.gamma import GammaClient

load_dotenv()

mcp = FastMCP("Polymarket MCP")
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

        # Convert to dict format for JSON serialization
        markets_data = []
        for market in markets:
            market_dict = market.model_dump()
            markets_data.append(market_dict)

        return {"markets": markets_data, "count": len(markets_data)}
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

        # Convert to dict format for JSON serialization
        markets_data = []
        for market in markets:
            market_dict = market.model_dump()
            markets_data.append(market_dict)

        return {"markets": markets_data, "count": len(markets_data)}
    except Exception as e:
        return {"error": f"Error getting markets: {str(e)}", "markets": []}


@mcp.tool(description="Search markets by question text.")
async def search_markets(query: str, limit: int = 20) -> Dict[str, Any]:
    """
    Search for markets by question text.

    Parameters:
    - query: Search term to match against market questions
    - limit: Maximum number of results to return
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        markets = gamma.get_all_current_markets()

        # Filter markets by query in question
        filtered_markets = []
        for market in markets:
            if market.question and query.lower() in market.question.lower():
                filtered_markets.append(market)

        if limit:
            filtered_markets = filtered_markets[:limit]

        # Convert to dict format
        markets_data = []
        for market in filtered_markets:
            market_dict = market.model_dump()
            markets_data.append(market_dict)

        return {"markets": markets_data, "count": len(markets_data)}
    except Exception as e:
        return {"error": f"Error searching markets: {str(e)}", "markets": []}


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

        order_id = clob.execute_limit_order(price, size, side, token_id)

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


@mcp.tool(description="Get USDC balance for the configured wallet.")
async def get_usdc_balance() -> Dict[str, Any]:
    """
    Get the USDC balance for the configured wallet.
    """
    try:
        if not clob:
            return {"error": "Polymarket CLOB client not initialized"}

        balance = clob.get_usdc_balance()

        return {
            "address": clob.address,
            "usdc_balance": balance
        }
    except Exception as e:
        return {"error": f"Error getting USDC balance: {str(e)}"}


if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run(transport="stdio")
