"""
DepthSim Core Models

This module contains the core data structures and models for order book depth simulation:
- Order book levels and complete order book snapshots
- Trade and order data structures
- Enumerations for trade types and order sides
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
import numpy as np


class TradeType(Enum):
    """Enumeration for trade types."""
    BUY = "buy"
    SELL = "sell"


class OrderSide(Enum):
    """Enumeration for order book sides."""
    BID = "bid" 
    ASK = "ask"


@dataclass
class OrderBookLevel:
    """
    Represents a single level in the order book.
    
    Attributes:
        price: Price level
        size: Total size (volume) at this level
        orders: Number of orders at this level
    """
    price: float
    size: float
    orders: int

    def __post_init__(self):
        """Validate order book level data."""
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if self.size < 0:
            raise ValueError("Size cannot be negative")
        if self.orders < 0:
            raise ValueError("Orders count cannot be negative")


@dataclass
class OrderBook:
    """
    Represents a complete order book snapshot with bid and ask sides.
    
    Attributes:
        bids: List of bid levels (highest price first)
        asks: List of ask levels (lowest price first) 
        mid_price: Mid price between best bid and ask
        spread: Bid-ask spread in price units
        spread_bps: Bid-ask spread in basis points
        timestamp: Timestamp of the snapshot
    """
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    mid_price: float
    spread: float
    spread_bps: float
    timestamp: Optional[datetime] = None
    _total_bid_size: Optional[float] = None  # Cached for performance
    _total_ask_size: Optional[float] = None  # Cached for performance
    _imbalance: Optional[float] = None  # Cached imbalance calculation
    
    @property
    def best_bid(self) -> Optional[float]:
        """Get the best (highest) bid price."""
        return self.bids[0].price if self.bids else None
    
    @property
    def best_ask(self) -> Optional[float]:
        """Get the best (lowest) ask price."""
        return self.asks[0].price if self.asks else None
    
    @property
    def total_bid_size(self) -> float:
        """Get total size across all bid levels."""
        if hasattr(self, '_total_bid_size') and self._total_bid_size is not None:
            return self._total_bid_size
        return sum(level.size for level in self.bids)
    
    @property
    def total_ask_size(self) -> float:
        """Get total size across all ask levels.""" 
        if hasattr(self, '_total_ask_size') and self._total_ask_size is not None:
            return self._total_ask_size
        return sum(level.size for level in self.asks)
    
    @property
    def is_crossed(self) -> bool:
        """Check if the order book is crossed (bid >= ask)."""
        if not self.bids or not self.asks:
            return False
        return self.best_bid >= self.best_ask
    
    @property 
    def depth_imbalance(self) -> float:
        """Calculate depth imbalance (bid_size - ask_size) / (bid_size + ask_size)."""
        total_bid = self.total_bid_size
        total_ask = self.total_ask_size
        total_size = total_bid + total_ask
        
        if total_size == 0:
            return 0.0
        
        return (total_bid - total_ask) / total_size


@dataclass
class Trade:
    """
    Represents a trade/transaction.
    
    Attributes:
        timestamp: When the trade occurred
        price: Trade price
        size: Trade size
        side: Trade side (buy/sell)
        trade_id: Unique trade identifier
    """
    timestamp: datetime
    price: float
    size: float
    side: TradeType
    trade_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate trade data."""
        if self.price <= 0:
            raise ValueError("Trade price must be positive")
        if self.size <= 0:
            raise ValueError("Trade size must be positive")


@dataclass
class Quote:
    """
    Represents an L1 quote (best bid/ask).
    
    Attributes:
        timestamp: Quote timestamp
        bid: Best bid price
        ask: Best ask price
        bid_size: Size at best bid
        ask_size: Size at best ask
        mid: Mid price ((bid + ask) / 2)
        spread: Spread in price units (ask - bid)
        spread_bps: Spread in basis points
    """
    timestamp: datetime
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    
    @property
    def mid(self) -> float:
        """Calculate mid price."""
        return (self.bid + self.ask) / 2.0
    
    @property
    def spread(self) -> float:
        """Calculate spread in price units."""
        return self.ask - self.bid
    
    @property
    def spread_bps(self) -> float:
        """Calculate spread in basis points."""
        if self.mid == 0:
            return 0.0
        return (self.spread / self.mid) * 10000.0
    
    def __post_init__(self):
        """Validate quote data."""
        if self.bid <= 0 or self.ask <= 0:
            raise ValueError("Bid and ask prices must be positive")
        if self.bid >= self.ask:
            raise ValueError("Bid must be less than ask (no crossed quotes)")
        if self.bid_size < 0 or self.ask_size < 0:
            raise ValueError("Sizes cannot be negative")


class SpreadModel(Enum):
    """Enumeration for different spread calculation models."""
    CONSTANT = "constant"
    VOLATILITY = "volatility"
    VOLUME = "volume" 
    VOLATILITY_VOLUME = "volatility_volume"
    CUSTOM = "custom"