#!/usr/bin/env python3
"""
DepthSim Standalone Examples

This module demonstrates DepthSim functionality using synthetic market data,
without requiring MockFlow or other external market data packages.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from depthsim import DepthSimulator
from depthsim.models import OrderBook, OrderBookLevel, Quote, Trade


def create_synthetic_market_data(periods: int = 100, symbol: str = "BTCUSDT") -> pd.DataFrame:
    """Create synthetic OHLCV market data for testing DepthSim."""
    np.random.seed(42)  # For reproducibility
    
    # Generate timestamps
    start_time = datetime(2024, 1, 1)
    timestamps = [start_time + timedelta(hours=i) for i in range(periods)]
    
    # Generate price series with some volatility
    base_price = 50000.0
    price_changes = np.random.normal(0, 0.02, periods)  # 2% volatility
    
    close_prices = [base_price]
    for change in price_changes[1:]:
        new_price = close_prices[-1] * (1 + change)
        close_prices.append(max(new_price, 1000))  # Minimum price floor
    
    # Generate OHLC from close prices
    data = []
    for i, close in enumerate(close_prices):
        if i == 0:
            open_price = close
        else:
            open_price = close_prices[i-1]
        
        # Generate high/low with some intrabar movement
        intrabar_range = close * 0.01  # 1% intrabar range
        high = close + np.random.uniform(0, intrabar_range)
        low = close - np.random.uniform(0, intrabar_range)
        
        # Ensure OHLC relationships are valid
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        # Generate volume
        base_volume = 1_000_000
        volume_multiplier = np.random.uniform(0.5, 2.0)
        volume = int(base_volume * volume_multiplier)
        
        data.append({
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    return pd.DataFrame(data, index=pd.DatetimeIndex(timestamps))


def basic_depth_simulation_example():
    """Basic example of depth simulation with synthetic data."""
    print("=== Basic Depth Simulation ===\n")
    
    # Create synthetic market data
    market_data = create_synthetic_market_data(periods=50)
    print(f"1. Created synthetic market data: {len(market_data)} periods")
    print(f"   Price range: ${market_data['close'].min():,.2f} - ${market_data['close'].max():,.2f}")
    
    # Create DepthSimulator
    depth_sim = DepthSimulator(
        spread_model="constant",
        base_spread_bps=5.0,
        depth_levels=10
    )
    
    # Generate quotes
    print("\n2. Generating bid/ask quotes...")
    quotes = depth_sim.generate_quotes(market_data)
    
    print(f"   Generated quotes for {len(quotes)} timestamps")
    print(f"   Average spread: {quotes['spread_bps'].mean():.2f}bp")
    print(f"   Spread range: {quotes['spread_bps'].min():.1f} - {quotes['spread_bps'].max():.1f}bp")
    
    # Show sample quotes
    print("\n   Sample quotes:")
    sample_quotes = quotes.head(3)
    for idx, row in sample_quotes.iterrows():
        print(f"   {idx}: Bid ${row['bid']:,.2f}, Ask ${row['ask']:,.2f}, Spread {row['spread_bps']:.1f}bp")


def spread_model_comparison_example():
    """Compare different spread models with the same market data."""
    print("\n=== Spread Model Comparison ===\n")
    
    # Create volatile market data
    market_data = create_synthetic_market_data(periods=100)
    
    spread_models = [
        ("constant", {"base_spread_bps": 8.0}),
        ("volatility", {"base_spread_bps": 5.0, "volatility_sensitivity": 100.0}),
        ("volume", {"base_spread_bps": 6.0, "volume_sensitivity": 1.0})
    ]
    
    print("1. Testing spread models on same market data...")
    print("\nModel Results:")
    print("   Model       | Avg Spread | Std Dev | Min  | Max  ")
    print("   ------------|------------|---------|------|------")
    
    for model_name, params in spread_models:
        depth_sim = DepthSimulator(spread_model=model_name, **params)
        quotes = depth_sim.generate_quotes(market_data)
        
        avg = quotes['spread_bps'].mean()
        std = quotes['spread_bps'].std()
        min_val = quotes['spread_bps'].min()
        max_val = quotes['spread_bps'].max()
        
        print(f"   {model_name:<11} | {avg:>8.1f}bp | {std:>5.1f}bp | {min_val:>3.1f}bp | {max_val:>3.1f}bp")


def order_book_ladder_example():
    """Demonstrate order book depth ladder generation."""
    print("\n=== Order Book Depth Ladder ===\n")
    
    # Create market data
    market_data = create_synthetic_market_data(periods=10)
    
    # Create depth simulator with deeper levels
    depth_sim = DepthSimulator(
        spread_model="volatility",
        base_spread_bps=7.0,
        volatility_sensitivity=50.0,
        depth_levels=15
    )
    
    print("1. Generating order book depth ladder...")
    depth_ladder = depth_sim.generate_depth_ladder(market_data, levels=8)
    
    print(f"   Generated depth for {len(depth_ladder)} timestamps")
    
    # Show detailed order book for first timestamp
    first_timestamp = list(depth_ladder.keys())[0]
    order_book = depth_ladder[first_timestamp]
    
    print(f"\n2. Sample Order Book at {first_timestamp}:")
    print(f"   Mid Price: ${order_book.mid_price:,.2f}")
    print(f"   Spread: {order_book.spread_bps:.2f}bp")
    print(f"   Depth Imbalance: {order_book.depth_imbalance:.3f}")
    
    print("\n   Bid Levels:")
    for i, bid_level in enumerate(order_book.bids[:5]):
        print(f"   L{i+1}: ${bid_level.price:>8,.2f} | Size: {bid_level.size:>8,} | Orders: {bid_level.orders}")
    
    print("\n   Ask Levels:")
    for i, ask_level in enumerate(order_book.asks[:5]):
        print(f"   L{i+1}: ${ask_level.price:>8,.2f} | Size: {ask_level.size:>8,} | Orders: {ask_level.orders}")


def trade_simulation_example():
    """Demonstrate trade print simulation."""
    print("\n=== Trade Print Simulation ===\n")
    
    # Create market data
    market_data = create_synthetic_market_data(periods=20)
    
    # Create depth simulator
    depth_sim = DepthSimulator(
        spread_model="constant",
        base_spread_bps=6.0,
        depth_levels=10
    )
    
    print("1. Generating trade prints...")
    trade_prints = depth_sim.generate_trade_prints(
        market_data, 
        trade_frequency=5.0  # 5 trades per minute
    )
    
    print(f"   Generated {len(trade_prints)} trades across {len(market_data)} periods")
    
    # Analyze trades
    total_volume = sum(trade.size for trade in trade_prints)
    avg_trade_size = total_volume / len(trade_prints) if trade_prints else 0
    
    print(f"   Total volume: {total_volume:,}")
    print(f"   Average trade size: {avg_trade_size:,.0f}")
    
    # Show sample trades
    print("\n   Sample trades:")
    for i, trade in enumerate(trade_prints[:5]):
        side = "BUY" if trade.side.value == "buy" else "SELL"
        print(f"   {i+1}: {side} {trade.size:,} @ ${trade.price:,.2f}")


def performance_benchmarking_example():
    """Benchmark DepthSim performance with large datasets."""
    print("\n=== Performance Benchmarking ===\n")
    
    import time
    
    data_sizes = [100, 500, 1000, 2000]
    
    print("1. Benchmarking quote generation performance...")
    print("\n   Periods | Quote Time | Depth Time | Rate (quotes/sec)")
    print("   --------|------------|------------|------------------")
    
    for periods in data_sizes:
        # Create market data
        market_data = create_synthetic_market_data(periods=periods)
        depth_sim = DepthSimulator(
            spread_model="volatility",
            base_spread_bps=5.0,
            depth_levels=10
        )
        
        # Benchmark quote generation
        start_time = time.time()
        quotes = depth_sim.generate_quotes(market_data)
        quote_time = time.time() - start_time
        
        # Benchmark depth ladder generation
        start_time = time.time()
        depth_ladder = depth_sim.generate_depth_ladder(market_data, levels=10)
        depth_time = time.time() - start_time
        
        quote_rate = periods / quote_time if quote_time > 0 else 0
        
        print(f"   {periods:>7} | {quote_time:>8.3f}s | {depth_time:>8.3f}s | {quote_rate:>13,.0f}")


def data_validation_example():
    """Demonstrate data validation and quality checks."""
    print("\n=== Data Validation ===\n")
    
    # Create market data
    market_data = create_synthetic_market_data(periods=100)
    depth_sim = DepthSimulator(
        spread_model="constant",
        base_spread_bps=5.0
    )
    
    # Generate quotes and depth
    quotes = depth_sim.generate_quotes(market_data)
    depth_ladder = depth_sim.generate_depth_ladder(market_data, levels=10)
    
    print("1. Validating generated data...")
    
    # Validate quotes
    assert all(quotes['ask'] > quotes['bid']), "Ask prices must be > bid prices"
    assert all(quotes['spread_bps'] > 0), "Spreads must be positive"
    assert all(quotes['mid'] == (quotes['bid'] + quotes['ask']) / 2), "Mid price validation failed"
    print("   ✓ Quote validation passed")
    
    # Validate order books
    for timestamp, book in list(depth_ladder.items())[:10]:  # Check first 10
        assert book.best_bid < book.best_ask, f"Crossed market at {timestamp}"
        assert not book.is_crossed, f"Order book marked as crossed at {timestamp}"
        assert book.total_bid_size > 0, f"No bid liquidity at {timestamp}"
        assert book.total_ask_size > 0, f"No ask liquidity at {timestamp}"
    print("   ✓ Order book validation passed")
    
    # Data quality metrics
    print("\n2. Data quality metrics:")
    print(f"   Quote count: {len(quotes)}")
    print(f"   Order book count: {len(depth_ladder)}")
    print(f"   Average spread: {quotes['spread_bps'].mean():.2f}bp")
    print(f"   Spread consistency: {(quotes['spread_bps'].std() / quotes['spread_bps'].mean()):.3f}")
    
    sample_book = next(iter(depth_ladder.values()))
    print(f"   Average depth per level: {sample_book.total_bid_size / len(sample_book.bids):,.0f}")


if __name__ == "__main__":
    print("DepthSim Standalone Examples")
    print("=" * 40)
    
    # Run all examples
    basic_depth_simulation_example()
    spread_model_comparison_example()
    order_book_ladder_example()
    trade_simulation_example()
    performance_benchmarking_example()
    data_validation_example()
    
    print("\n" + "=" * 40)
    print("All examples completed successfully!")