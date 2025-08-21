"""
DepthSim - Order Book Depth Simulation Package

Professional-grade order book depth simulation for backtesting and market analysis.
Designed to consume market data and synthesize realistic bid-ask spreads, 
order book depth, and trade prints.

Main Components:
- DepthSimulator: Core simulation engine with multiple spread models
- Order book models: OrderBook, OrderBookLevel data structures  
- Spread models: Volatility-linked, volume-sensitive, and custom functions
- Trade print generation: Realistic trade arrival and sizing models
- Latency modeling: Market microstructure effects simulation
"""

__version__ = "0.1.0"
__author__ = "Conflux ML Engine Team"

# Import main public API
from .core import DepthSimulator
from .models import (
    OrderBook,
    OrderBookLevel,
    SpreadModel,
    TradeType,
)
from .spread_models import (
    ConstantSpreadModel,
    VolatilityLinkedSpreadModel, 
    VolumeLinkedSpreadModel,
)

# Package-level exports
__all__ = [
    "DepthSimulator",
    "OrderBook", 
    "OrderBookLevel",
    "SpreadModel",
    "TradeType",
    "ConstantSpreadModel",
    "VolatilityLinkedSpreadModel",
    "VolumeLinkedSpreadModel",
    "__version__"
]