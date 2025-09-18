import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import json
from polymarket_mcp_server.server import (
    get_markets,
    get_order_book,
    get_mid_price,
    get_price,
    search_markets,
    place_limit_order,
    place_market_order,
    get_usdc_balance,
)


@pytest.fixture
def mock_polymarket():
    """Mock the polymarket CLOB client."""
    with patch('polymarket_mcp_server.server.polymarket') as mock:
        mock_client = MagicMock()
        mock.client = mock_client
        mock.get_all_markets.return_value = [
            MagicMock(
                id="test_market_1",
                question="Will it rain tomorrow?",
                description="Test market description",
                active=True,
                closed=False,
                archived=False,
                accepting_orders=True,
                end_date_iso="2024-12-31T23:59:59Z",
                tokens=[{"token_id": "123", "outcome": "Yes"}],
                volume=1000.0,
                liquidity=500.0,
                model_dump=lambda: {
                    "id": "test_market_1",
                    "question": "Will it rain tomorrow?",
                    "description": "Test market description",
                    "active": True,
                    "closed": False,
                    "archived": False,
                    "accepting_orders": True,
                    "end_date_iso": "2024-12-31T23:59:59Z",
                    "tokens": [{"token_id": "123", "outcome": "Yes"}],
                    "volume": 1000.0,
                    "liquidity": 500.0
                }
            )
        ]
        mock.filter_markets_for_trading.return_value = mock.get_all_markets.return_value
        mock.get_orderbook.return_value = MagicMock(
            bids=[MagicMock(price="0.45", size="100")],
            asks=[MagicMock(price="0.55", size="100")]
        )
        mock.get_mid_from_book.return_value = 0.50
        mock.get_price.return_value = 0.52
        mock.execute_limit_order.return_value = "order_123"
        mock.execute_market_order.return_value = {"order_id": "market_order_123"}
        mock.get_usdc_balance.return_value = 1000.0
        mock.address = "0x1234567890123456789012345678901234567890"
        yield mock


@pytest.mark.asyncio
async def test_get_markets(mock_polymarket):
    """Test getting markets."""
    result = await get_markets()
    
    assert "markets" in result
    assert "count" in result
    assert result["count"] == 1
    assert len(result["markets"]) == 1
    
    market = result["markets"][0]
    assert market["id"] == "test_market_1"
    assert market["question"] == "Will it rain tomorrow?"
    assert market["active"] is True


@pytest.mark.asyncio
async def test_get_markets_active_only(mock_polymarket):
    """Test getting only active markets."""
    result = await get_markets(active_only=True)
    
    assert "markets" in result
    assert result["count"] == 1
    mock_polymarket.filter_markets_for_trading.assert_called_once()


@pytest.mark.asyncio
async def test_get_markets_with_limit(mock_polymarket):
    """Test getting markets with limit."""
    result = await get_markets(limit=5)
    
    assert "markets" in result
    assert result["count"] == 1  # Only 1 market in mock data


@pytest.mark.asyncio
async def test_get_order_book(mock_polymarket):
    """Test getting order book."""
    result = await get_order_book("test_token_123")
    
    assert "token_id" in result
    assert "bids" in result
    assert "asks" in result
    assert result["token_id"] == "test_token_123"
    assert len(result["bids"]) == 1
    assert len(result["asks"]) == 1
    assert result["bids"][0]["price"] == "0.45"
    assert result["asks"][0]["price"] == "0.55"


@pytest.mark.asyncio
async def test_get_mid_price(mock_polymarket):
    """Test getting mid price."""
    result = await get_mid_price("test_token_123")
    
    assert "token_id" in result
    assert "mid_price" in result
    assert result["token_id"] == "test_token_123"
    assert result["mid_price"] == 0.50


@pytest.mark.asyncio
async def test_get_price(mock_polymarket):
    """Test getting price for a side."""
    result = await get_price("test_token_123", "BUY")
    
    assert "token_id" in result
    assert "side" in result
    assert "price" in result
    assert result["token_id"] == "test_token_123"
    assert result["side"] == "BUY"
    assert result["price"] == 0.52


@pytest.mark.asyncio
async def test_search_markets(mock_polymarket):
    """Test searching markets."""
    result = await search_markets("rain")
    
    assert "markets" in result
    assert "count" in result
    assert result["count"] == 1
    assert result["markets"][0]["question"] == "Will it rain tomorrow?"


@pytest.mark.asyncio
async def test_place_limit_order(mock_polymarket):
    """Test placing a limit order."""
    result = await place_limit_order("test_token_123", 0.50, 100.0, "BUY")
    
    assert "order_id" in result
    assert "token_id" in result
    assert "price" in result
    assert "size" in result
    assert "side" in result
    assert result["order_id"] == "order_123"
    assert result["token_id"] == "test_token_123"
    assert result["price"] == 0.50
    assert result["size"] == 100.0
    assert result["side"] == "BUY"


@pytest.mark.asyncio
async def test_place_market_order(mock_polymarket):
    """Test placing a market order."""
    result = await place_market_order("test_token_123", 50.0, "FOK")
    
    assert "result" in result
    assert "token_id" in result
    assert "amount" in result
    assert "order_type" in result
    assert result["token_id"] == "test_token_123"
    assert result["amount"] == 50.0
    assert result["order_type"] == "FOK"


@pytest.mark.asyncio
async def test_get_usdc_balance(mock_polymarket):
    """Test getting USDC balance."""
    result = await get_usdc_balance()
    
    assert "address" in result
    assert "usdc_balance" in result
    assert result["address"] == "0x1234567890123456789012345678901234567890"
    assert result["usdc_balance"] == 1000.0


@pytest.mark.asyncio
async def test_error_handling_no_client():
    """Test error handling when polymarket client is not initialized."""
    with patch('polymarket_mcp_server.server.polymarket', None):
        result = await get_markets()
        assert "error" in result
        assert "not initialized" in result["error"]


@pytest.mark.asyncio
async def test_api_error_handling(mock_polymarket):
    """Test API error handling."""
    mock_polymarket.get_all_markets.side_effect = Exception("API Error")
    
    result = await get_markets()
    assert "error" in result
    assert "API Error" in result["error"]