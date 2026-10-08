"""Market data endpoints."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.trading import MarketCandle, MarketData
from app.services.market_data import MarketDataService

router = APIRouter()


@router.get("", response_model=List[MarketData])
async def get_markets(
    search: Optional[str] = Query(None, description="Search by symbol"),
    current_user: User = Depends(get_current_user),
) -> List[MarketData]:
    """Get list of available markets."""
    market_service = MarketDataService()
    markets = await market_service.get_markets(search=search)
    return markets


@router.get("/{symbol}", response_model=MarketData)
async def get_market_detail(
    symbol: str,
    current_user: User = Depends(get_current_user),
) -> MarketData:
    """Get detailed market data for a specific symbol."""
    market_service = MarketDataService()
    market = await market_service.get_market_data(symbol.upper())
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.get("/{symbol}/candles", response_model=List[MarketCandle])
async def get_candles(
    symbol: str,
    timeframe: str = Query("1h", description="Candlestick timeframe"),
    limit: int = Query(100, ge=1, le=1000, description="Number of candles"),
    current_user: User = Depends(get_current_user),
) -> List[MarketCandle]:
    """Get candlestick data for a symbol."""
    market_service = MarketDataService()
    candles = await market_service.get_candles(
        symbol=symbol.upper(),
        timeframe=timeframe,
        limit=limit,
    )
    return candles


@router.get("/{symbol}/orderbook")
async def get_orderbook(
    symbol: str,
    depth: int = Query(20, ge=1, le=100, description="Order book depth"),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get order book data for a symbol."""
    market_service = MarketDataService()
    orderbook = await market_service.get_orderbook(symbol.upper(), depth)
    return orderbook


@router.get("/{symbol}/trades")
async def get_recent_trades(
    symbol: str,
    limit: int = Query(50, ge=1, le=500, description="Number of recent trades"),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """Get recent trades for a symbol."""
    market_service = MarketDataService()
    trades = await market_service.get_recent_trades(symbol.upper(), limit)
    return trades
