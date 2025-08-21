#!/usr/bin/env python3
"""
MockFlow + DepthSim Integration Example

This example demonstrates how to use MockFlow for market data generation
and DepthSim for order book depth simulation as separate, complementary tools.

Architecture:
- MockFlow: Generates realistic OHLCV market data
- DepthSim: Consumes market data and adds order book depth + execution simulation
"""

from datetime import datetime
import pandas as pd

try:
    # Import MockFlow for market data generation
    from mockflow import generate_mock_data
    MOCKFLOW_AVAILABLE = True
except ImportError:
    MOCKFLOW_AVAILABLE = False
    print("MockFlow not found. Install with: pip install mockflow")

# Import DepthSim components
from depthsim import DepthSimulator
from depthsim.models import SpreadModel


def basic_integration_example():
    """Basic example of MockFlow + DepthSim integration."""
    print("=== Basic MockFlow + DepthSim Integration ===\n")
    
    if not MOCKFLOW_AVAILABLE:
        print("Skipping basic integration example - MockFlow not available")
        return
    
    # Step 1: Generate market data with MockFlow
    print("1. Generating market data with MockFlow...")
    market_data = generate_mock_data(
        symbol="BTCUSDT",
        timeframe="1h",
        days=7,
        scenario="auto"
    )
    
    print(f"   Generated {len(market_data)} candles")
    print(f"   Price range: ${market_data['close'].min():,.2f} - ${market_data['close'].max():,.2f}")
    print(f"   MockFlow columns: {list(market_data.columns)}")
    
    # Step 2: Create order book depth with DepthSim
    print("\n2. Adding order book depth with DepthSim...")
    depth_sim = DepthSimulator(
        spread_model="constant",
        base_spread_bps=5.0,
        depth_levels=10
    )
    
    # Generate quotes (bid/ask/spread)
    quotes = depth_sim.generate_quotes(market_data)
    
    print(f"   Added quotes for {len(quotes)} timestamps")
    print(f"   DepthSim quote columns: {list(quotes.columns)}")
    print(f"   Average spread: {quotes['spread_bps'].mean():.2f}bp")
    
    # Step 3: Generate order book depth ladder
    print("\n3. Generating order book depth ladder...")
    depth_ladder = depth_sim.generate_depth_ladder(market_data, levels=5)
    
    print(f"   Generated depth for {len(depth_ladder)} timestamps")
    
    # Show sample order book
    sample_timestamp = list(depth_ladder.keys())[0]
    sample_book = depth_ladder[sample_timestamp]
    
    print(f"\n   Sample order book at {sample_timestamp}:")
    print(f"   Best Bid: ${sample_book.best_bid:,.2f}")
    print(f"   Best Ask: ${sample_book.best_ask:,.2f}")
    print(f"   Spread: {sample_book.spread_bps:.2f}bp")
    print(f"   Total Bid Size: {sample_book.total_bid_size:,}")
    print(f"   Total Ask Size: {sample_book.total_ask_size:,}")


def advanced_spread_models_example():
    """Example showing different spread models with MockFlow data."""
    print("\n=== Advanced Spread Models ===\n")
    
    if not MOCKFLOW_AVAILABLE:
        print("Skipping advanced spread models example - MockFlow not available")
        return
    
    # Generate volatile market data
    print("1. Generating volatile market scenario...")
    market_data = generate_mock_data(
        symbol="ETHUSDT",
        timeframe="15m",
        days=3,
        scenario="bear"  # Volatile bear market
    )
    
    # Test different spread models
    spread_models = [
        ("constant", {"base_spread_bps": 8.0}),
        ("volatility", {"base_spread_bps": 5.0, "volatility_sensitivity": 100.0}),
        ("volume", {"base_spread_bps": 6.0, "volume_sensitivity": 0.5})
    ]
    
    results = {}
    
    for model_name, params in spread_models:
        print(f"\n2. Testing {model_name} spread model...")
        
        depth_sim = DepthSimulator(
            spread_model=model_name,
            **params
        )
        
        quotes = depth_sim.generate_quotes(market_data)
        
        results[model_name] = {
            "mean_spread": quotes['spread_bps'].mean(),
            "std_spread": quotes['spread_bps'].std(),
            "min_spread": quotes['spread_bps'].min(),
            "max_spread": quotes['spread_bps'].max()
        }
        
        print(f"   Average spread: {results[model_name]['mean_spread']:.2f}bp")
        print(f"   Spread volatility: {results[model_name]['std_spread']:.2f}bp")
        print(f"   Spread range: {results[model_name]['min_spread']:.1f} - {results[model_name]['max_spread']:.1f}bp")
    
    # Compare results
    print("\n3. Spread Model Comparison:")
    print("   Model       | Avg Spread | Volatility | Range")
    print("   ------------|------------|------------|-------------")
    for model_name, stats in results.items():
        print(f"   {model_name:<11} | {stats['mean_spread']:>8.1f}bp | {stats['std_spread']:>8.1f}bp | {stats['min_spread']:>4.1f}-{stats['max_spread']:>4.1f}bp")


def market_making_simulation_example():
    """Example of market making simulation using both packages."""
    print("\n=== Market Making Simulation ===\n")
    
    if not MOCKFLOW_AVAILABLE:
        print("Skipping market making example - MockFlow not available")
        return
    
    # Generate market data for different scenarios
    scenarios = ["bull", "bear", "sideways"]
    
    for scenario in scenarios:
        print(f"1. Simulating market making in {scenario} market...")
        
        # Generate scenario-specific market data
        market_data = generate_mock_data(
            symbol="ADAUSDT",
            timeframe="5m",
            days=1,  # Single day for focused analysis
            scenario=scenario
        )
        
        # Configure market maker spreads
        depth_sim = DepthSimulator(
            spread_model="volume",  # Adjust spreads based on volume
            base_spread_bps=10.0,   # Wider spreads for market making
            volume_sensitivity=1.0,  # Strong volume sensitivity
            depth_levels=15         # Deeper book for market making
        )
        
        quotes = depth_sim.generate_quotes(market_data)
        depth_ladder = depth_sim.generate_depth_ladder(market_data, levels=10)
        
        # Analyze market making metrics
        avg_spread = quotes['spread_bps'].mean()
        total_volume = market_data['volume'].sum()
        price_volatility = market_data['close'].pct_change().std() * 100
        
        print(f"   Scenario: {scenario}")
        print(f"   Average spread: {avg_spread:.2f}bp")
        print(f"   Total volume: {total_volume:,.0f}")
        print(f"   Price volatility: {price_volatility:.2f}%")
        
        # Sample depth analysis
        sample_book = next(iter(depth_ladder.values()))
        print(f"   Sample depth imbalance: {sample_book.depth_imbalance:.3f}")
        print()


def backtesting_integration_example():
    """Example showing how to use both packages for backtesting."""
    print("\n=== Backtesting Integration ===\n")
    
    if not MOCKFLOW_AVAILABLE:
        print("Skipping backtesting example - MockFlow not available")
        return
    
    print("1. Setting up backtesting environment...")
    
    # Generate comprehensive market data for backtesting
    market_data = generate_mock_data(
        symbol="BTCUSDT",
        timeframe="30m",
        days=30,
        scenario="auto"
    )
    
    # Create execution environment with DepthSim
    execution_sim = DepthSimulator(
        spread_model="volatility",
        base_spread_bps=3.0,
        volatility_sensitivity=50.0,
        depth_levels=20
    )
    
    # Generate execution data
    quotes = execution_sim.generate_quotes(market_data)
    
    # Combine market data with execution data
    backtest_data = market_data.copy()
    backtest_data['bid'] = quotes['bid']
    backtest_data['ask'] = quotes['ask']
    backtest_data['spread_bps'] = quotes['spread_bps']
    
    print(f"   Generated backtest dataset: {len(backtest_data)} periods")
    print(f"   Data columns: {list(backtest_data.columns)}")
    
    # Sample backtesting metrics
    print("\n2. Backtesting environment metrics:")
    print(f"   Average bid-ask spread: {backtest_data['spread_bps'].mean():.2f}bp")
    print(f"   Spread volatility: {backtest_data['spread_bps'].std():.2f}bp")
    print(f"   Market impact estimate: {(backtest_data['spread_bps'] / 2).mean():.2f}bp per side")
    
    # Demonstrate realistic trading costs
    trade_size_usd = 10000  # $10k trade
    avg_price = backtest_data['close'].mean()
    avg_spread_usd = avg_price * (backtest_data['spread_bps'].mean() / 10000)
    
    print(f"\n3. Realistic trading costs for ${trade_size_usd:,} trades:")
    print(f"   Average price: ${avg_price:,.2f}")
    print(f"   Average spread: ${avg_spread_usd:.2f}")
    print(f"   Trading cost: {(avg_spread_usd / 2 / trade_size_usd) * 10000:.1f}bp per trade")


if __name__ == "__main__":
    print("MockFlow + DepthSim Integration Examples")
    print("=" * 50)
    
    # Run all examples
    basic_integration_example()
    advanced_spread_models_example()
    market_making_simulation_example()
    backtesting_integration_example()
    
    print("\n" + "=" * 50)
    print("Integration examples completed!")
    
    if not MOCKFLOW_AVAILABLE:
        print("\nNote: Install MockFlow to run all examples:")
        print("pip install mockflow")