#!/usr/bin/env python3
"""
DepthSim Advanced Features Example

Demonstrates the comprehensive features of DepthSim including:
- Multiple sophisticated spread models
- L2 depth snapshots with microstructure
- Market impact simulation
- Realistic trade sequence generation
- Advanced order book analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any

from depthsim import DepthSimulator
from depthsim.models import OrderBook, OrderBookLevel, Trade
from depthsim.spread_models import (
    ImbalanceAdjustedSpreadModel, 
    VolatilityVolumeSpreadModel,
    TimeOfDaySpreadModel,
    CustomSpreadModel
)


def create_advanced_market_data(periods: int = 200) -> pd.DataFrame:
    """Create synthetic market data with realistic patterns."""
    np.random.seed(42)
    
    # Generate timestamps (15-minute intervals)
    start_time = datetime(2024, 8, 20, 9, 30)  # Market open
    timestamps = [start_time + timedelta(minutes=15*i) for i in range(periods)]
    
    # Generate price series with volatility clustering
    base_price = 50000.0
    prices = [base_price]
    volatility = 0.002  # Base volatility
    
    for i in range(1, periods):
        # GARCH-like volatility clustering
        prev_return = np.log(prices[-1] / prices[-2]) if len(prices) > 1 else 0
        volatility = 0.001 + 0.8 * volatility + 0.1 * prev_return**2
        volatility = min(max(volatility, 0.0005), 0.02)  # Bounds
        
        # Price movement
        price_change = np.random.normal(0, volatility)
        new_price = prices[-1] * np.exp(price_change)
        prices.append(new_price)
    
    # Generate correlated volume
    volumes = []
    for i, price in enumerate(prices):
        # Higher volume during volatile periods and market open/close
        hour = timestamps[i].hour + timestamps[i].minute / 60.0
        
        # Time-of-day effect
        if 9.5 <= hour <= 11.0 or 15.0 <= hour <= 16.0:
            time_multiplier = 1.8  # Higher volume at open/close
        elif 12.0 <= hour <= 14.0:
            time_multiplier = 0.6   # Lower volume at lunch
        else:
            time_multiplier = 1.0
        
        # Volatility effect
        if i > 0:
            price_change = abs(np.log(price / prices[i-1]))
            vol_multiplier = 1 + price_change * 50  # Higher volume with big moves
        else:
            vol_multiplier = 1.0
        
        base_volume = 800_000
        volume = base_volume * time_multiplier * vol_multiplier * np.random.uniform(0.5, 1.5)
        volumes.append(int(volume))
    
    return pd.DataFrame({
        'close': prices,
        'volume': volumes
    }, index=pd.DatetimeIndex(timestamps))


def demonstrate_advanced_spread_models():
    """Demonstrate advanced spread models."""
    print("=== Advanced Spread Models Demo ===\n")
    
    market_data = create_advanced_market_data(periods=100)
    
    # Test new imbalance-adjusted spread model
    print("1. Imbalance-Adjusted Spread Model:")
    imbalance_sim = DepthSimulator(
        spread_model="imbalance",
        base_spread_bps=4.0,
        imbalance_sensitivity=15.0
    )
    
    # Generate some quotes to see spreads
    quotes = imbalance_sim.generate_quotes(market_data)
    print(f"   Average spread: {quotes['spread_bps'].mean():.2f}bp")
    print(f"   Spread range: {quotes['spread_bps'].min():.1f} - {quotes['spread_bps'].max():.1f}bp")
    
    # Test combined volatility + volume model  
    print("\n2. Volatility + Volume Combined Model:")
    combined_sim = DepthSimulator(
        spread_model="volatility_volume",
        base_spread_bps=5.0,
        volatility_sensitivity=80.0,
        volume_sensitivity=0.6
    )
    
    combined_quotes = combined_sim.generate_quotes(market_data)
    print(f"   Average spread: {combined_quotes['spread_bps'].mean():.2f}bp")
    print(f"   Spread range: {combined_quotes['spread_bps'].min():.1f} - {combined_quotes['spread_bps'].max():.1f}bp")
    
    # Test time-of-day model
    print("\n3. Time-of-Day Spread Model:")
    tod_sim = DepthSimulator(
        spread_model="time_of_day",
        base_spread_bps=6.0,
        overnight_multiplier=2.5,
        lunch_multiplier=1.8
    )
    
    tod_quotes = tod_sim.generate_quotes(market_data)
    print(f"   Average spread: {tod_quotes['spread_bps'].mean():.2f}bp")
    print(f"   Spread range: {tod_quotes['spread_bps'].min():.1f} - {tod_quotes['spread_bps'].max():.1f}bp")
    
    # Custom spread model example
    print("\n4. Custom Spread Model:")
    def custom_spread_func(mid_price: float, volatility: float, volume: float) -> float:
        """Custom spread function: wider spreads for round numbers."""
        base_spread = 5.0
        
        # Wider spreads at psychological levels (round thousands)
        if mid_price % 1000 < 50 or mid_price % 1000 > 950:
            psychological_premium = 2.0
        else:
            psychological_premium = 0.0
        
        # Volume and volatility effects
        vol_effect = volatility * 100
        volume_effect = max(0, 10 - volume / 100_000)  # Tighter with more volume
        
        return base_spread + psychological_premium + vol_effect + volume_effect
    
    custom_model = CustomSpreadModel(
        spread_function=custom_spread_func,
        min_spread_bps=1.0,
        max_spread_bps=25.0
    )
    
    custom_sim = DepthSimulator(spread_model=custom_model)
    custom_quotes = custom_sim.generate_quotes(market_data)
    print(f"   Average spread: {custom_quotes['spread_bps'].mean():.2f}bp")
    print(f"   Spread range: {custom_quotes['spread_bps'].min():.1f} - {custom_quotes['spread_bps'].max():.1f}bp")


def demonstrate_l2_depth_features():
    """Demonstrate advanced L2 depth snapshot features."""
    print("\n=== Advanced L2 Depth Features ===\n")
    
    market_data = create_advanced_market_data(periods=20)
    
    depth_sim = DepthSimulator(
        spread_model="volatility",
        base_spread_bps=4.0,
        depth_levels=25
    )
    
    print("1. Generating L2 depth snapshots with microstructure:")
    l2_snapshots = depth_sim.generate_l2_depth_snapshots(
        market_data,
        levels=20,
        asymmetry_factor=0.15,  # 15% asymmetry
        size_clustering=True,   # Cluster sizes at key levels
        price_improvement=True  # Sub-penny pricing
    )
    
    print(f"   Generated {len(l2_snapshots)} L2 snapshots")
    
    # Analyze first snapshot in detail
    first_timestamp = list(l2_snapshots.keys())[0]
    first_book = l2_snapshots[first_timestamp]
    
    print(f"\n2. Sample L2 Snapshot at {first_timestamp}:")
    print(f"   Bid levels: {len(first_book.bids)}")
    print(f"   Ask levels: {len(first_book.asks)}")
    print(f"   Mid price: ${first_book.mid_price:,.2f}")
    print(f"   Spread: {first_book.spread_bps:.2f}bp")
    print(f"   Depth imbalance: {first_book.depth_imbalance:.3f}")
    
    print(f"\n   Top 5 Bids:")
    for i, bid in enumerate(first_book.bids[:5]):
        print(f"   L{i+1}: ${bid.price:>8,.3f} | Size: {bid.size:>8,} | Orders: {bid.orders}")
    
    print(f"\n   Top 5 Asks:")
    for i, ask in enumerate(first_book.asks[:5]):
        print(f"   L{i+1}: ${ask.price:>8,.3f} | Size: {ask.size:>8,} | Orders: {ask.orders}")
    
    # Depth analysis across all snapshots
    print(f"\n3. Depth Analytics Across All Snapshots:")
    imbalances = [book.depth_imbalance for book in l2_snapshots.values()]
    spreads = [book.spread_bps for book in l2_snapshots.values()]
    bid_sizes = [book.total_bid_size for book in l2_snapshots.values()]
    ask_sizes = [book.total_ask_size for book in l2_snapshots.values()]
    
    print(f"   Average imbalance: {np.mean(imbalances):+.3f}")
    print(f"   Imbalance volatility: {np.std(imbalances):.3f}")
    print(f"   Average total bid size: {np.mean(bid_sizes):,.0f}")
    print(f"   Average total ask size: {np.mean(ask_sizes):,.0f}")


def demonstrate_market_impact_simulation():
    """Demonstrate market impact simulation."""
    print("\n=== Market Impact Simulation ===\n")
    
    market_data = create_advanced_market_data(periods=10)
    
    depth_sim = DepthSimulator(
        spread_model="volume",
        base_spread_bps=5.0,
        depth_levels=30  # Deep book for impact testing
    )
    
    # Generate a deep order book
    depth_ladder = depth_sim.generate_depth_ladder(market_data, levels=30)
    sample_book = next(iter(depth_ladder.values()))
    
    print("1. Market Impact Analysis:")
    print(f"   Order book depth: {len(sample_book.bids)} bids, {len(sample_book.asks)} asks")
    print(f"   Mid price: ${sample_book.mid_price:,.2f}")
    
    # Test different order sizes
    order_sizes = [50_000, 200_000, 500_000, 1_000_000, 2_000_000]
    
    print(f"\n   Buy Order Impact Analysis:")
    print(f"   {'Size':>10} | {'Avg Price':>10} | {'Impact':>8} | {'Levels':>6} | {'Filled':>8}")
    print(f"   {'-'*10}|{'-'*11}|{'-'*9}|{'-'*7}|{'-'*9}")
    
    for size in order_sizes:
        impact = depth_sim.simulate_market_impact(size, 'buy', sample_book)
        fill_rate = impact['executed_size'] / size * 100
        
        print(f"   ${size:>8,} | ${impact['average_price']:>9,.2f} | {impact['impact_bps']:>6.1f}bp | {impact['levels_consumed']:>5} | {fill_rate:>6.1f}%")
    
    print(f"\n   Sell Order Impact Analysis:")
    print(f"   {'Size':>10} | {'Avg Price':>10} | {'Impact':>8} | {'Levels':>6} | {'Filled':>8}")
    print(f"   {'-'*10}|{'-'*11}|{'-'*9}|{'-'*7}|{'-'*9}")
    
    for size in order_sizes:
        impact = depth_sim.simulate_market_impact(size, 'sell', sample_book)
        fill_rate = impact['executed_size'] / size * 100
        
        print(f"   ${size:>8,} | ${impact['average_price']:>9,.2f} | {impact['impact_bps']:>6.1f}bp | {impact['levels_consumed']:>5} | {fill_rate:>6.1f}%")


def demonstrate_realistic_trade_sequence():
    """Demonstrate realistic trade sequence generation."""
    print("\n=== Realistic Trade Sequence Generation ===\n")
    
    market_data = create_advanced_market_data(periods=24)  # One trading day
    
    depth_sim = DepthSimulator(
        spread_model="time_of_day",
        base_spread_bps=4.0
    )
    
    print("1. Generating realistic trade sequence:")
    trades = depth_sim.generate_realistic_trade_sequence(
        market_data,
        trade_intensity=2.0,        # 2x normal trading
        institutional_ratio=0.20    # 20% institutional trades
    )
    
    print(f"   Generated {len(trades)} trades over {len(market_data)} periods")
    
    # Analyze trade patterns
    buy_trades = [t for t in trades if t.side.value == 'buy']
    sell_trades = [t for t in trades if t.side.value == 'sell']
    
    total_buy_volume = sum(t.size for t in buy_trades)
    total_sell_volume = sum(t.size for t in sell_trades)
    avg_trade_size = sum(t.size for t in trades) / len(trades)
    
    print(f"\n2. Trade Analysis:")
    print(f"   Buy trades: {len(buy_trades)} ({len(buy_trades)/len(trades)*100:.1f}%)")
    print(f"   Sell trades: {len(sell_trades)} ({len(sell_trades)/len(trades)*100:.1f}%)")
    print(f"   Total buy volume: {total_buy_volume:,.0f}")
    print(f"   Total sell volume: {total_sell_volume:,.0f}")
    print(f"   Volume imbalance: {(total_buy_volume - total_sell_volume)/(total_buy_volume + total_sell_volume):.3f}")
    print(f"   Average trade size: {avg_trade_size:,.0f}")
    
    # Size distribution analysis
    trade_sizes = [t.size for t in trades]
    print(f"\n3. Trade Size Distribution:")
    print(f"   Min: {min(trade_sizes):,.0f}")
    print(f"   Median: {np.median(trade_sizes):,.0f}")
    print(f"   Mean: {np.mean(trade_sizes):,.0f}")
    print(f"   Max: {max(trade_sizes):,.0f}")
    print(f"   99th percentile: {np.percentile(trade_sizes, 99):,.0f}")
    
    # Sample trades
    print(f"\n4. Sample Trades:")
    print(f"   {'Time':>8} | {'Side':>4} | {'Size':>8} | {'Price':>10} | {'Trade ID':>15}")
    print(f"   {'-'*8}|{'-'*5}|{'-'*9}|{'-'*11}|{'-'*16}")
    
    for trade in trades[:8]:
        side = "BUY" if trade.side.value == 'buy' else "SELL"
        time_str = trade.timestamp.strftime("%H:%M")
        print(f"   {time_str:>8} | {side:>4} | {trade.size:>8,.0f} | ${trade.price:>9,.2f} | {trade.trade_id:>15}")


def demonstrate_comprehensive_analytics():
    """Demonstrate comprehensive market analytics."""
    print("\n=== Comprehensive Market Analytics ===\n")
    
    market_data = create_advanced_market_data(periods=100)
    
    # Use volatility-volume model for realistic behavior
    analytics_sim = DepthSimulator(
        spread_model="volatility_volume",
        base_spread_bps=5.0,
        volatility_sensitivity=60.0,
        volume_sensitivity=0.8,
        depth_levels=20
    )
    
    print("1. Generating comprehensive market simulation:")
    
    # Generate all components
    quotes = analytics_sim.generate_quotes(market_data)
    depth_ladder = analytics_sim.generate_depth_ladder(market_data, levels=15)
    trades = analytics_sim.generate_realistic_trade_sequence(market_data, trade_intensity=1.5)
    
    print(f"   Quotes: {len(quotes)}")
    print(f"   Depth snapshots: {len(depth_ladder)}")
    print(f"   Trades: {len(trades)}")
    
    # Market quality metrics
    print(f"\n2. Market Quality Metrics:")
    
    # Spread analysis
    spread_stats = {
        'mean': quotes['spread_bps'].mean(),
        'std': quotes['spread_bps'].std(),
        'min': quotes['spread_bps'].min(),
        'max': quotes['spread_bps'].max(),
        'median': quotes['spread_bps'].median()
    }
    
    print(f"   Spread Statistics (bp):")
    for metric, value in spread_stats.items():
        print(f"     {metric.capitalize()}: {value:.2f}")
    
    # Depth analysis
    imbalances = [book.depth_imbalance for book in depth_ladder.values()]
    total_depths = [book.total_bid_size + book.total_ask_size for book in depth_ladder.values()]
    
    print(f"\n   Depth Statistics:")
    print(f"     Avg imbalance: {np.mean(imbalances):+.3f}")
    print(f"     Imbalance volatility: {np.std(imbalances):.3f}")
    print(f"     Avg total depth: {np.mean(total_depths):,.0f}")
    print(f"     Depth stability: {1 - np.std(total_depths)/np.mean(total_depths):.3f}")
    
    # Trading activity
    trade_volumes = [t.size for t in trades]
    hourly_trades = {}
    
    for trade in trades:
        hour = trade.timestamp.hour
        hourly_trades[hour] = hourly_trades.get(hour, 0) + 1
    
    print(f"\n   Trading Activity:")
    print(f"     Total trades: {len(trades)}")
    print(f"     Total volume: {sum(trade_volumes):,.0f}")
    print(f"     Avg trade size: {np.mean(trade_volumes):,.0f}")
    print(f"     Most active hour: {max(hourly_trades.keys(), key=hourly_trades.get):02d}:00 ({max(hourly_trades.values())} trades)")


if __name__ == "__main__":
    print("DepthSim Advanced Features Demonstration")
    print("=" * 60)
    
    # Run all demonstrations
    demonstrate_advanced_spread_models()
    demonstrate_l2_depth_features()
    demonstrate_market_impact_simulation()
    demonstrate_realistic_trade_sequence()
    demonstrate_comprehensive_analytics()
    
    print("\n" + "=" * 60)
    print("Advanced features demonstration completed!")
    print("\nKey Features Demonstrated:")
    print("✓ Advanced spread models (imbalance, time-of-day, custom)")
    print("✓ L2 depth with microstructure (clustering, price improvement)")
    print("✓ Market impact simulation")
    print("✓ Realistic trade sequences (institutional vs retail)")
    print("✓ Comprehensive market analytics")