# DepthSim Tutorial: Complete Guide to Market Microstructure Simulation

This tutorial walks you through DepthSim's capabilities from basic concepts to advanced trading scenarios.

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Basic Concepts](#basic-concepts)
3. [Your First Simulation](#your-first-simulation)
4. [Understanding Spread Models](#understanding-spread-models)
5. [Order Book Depth Simulation](#order-book-depth-simulation)
6. [Market Impact Analysis](#market-impact-analysis)
7. [Realistic Trade Generation](#realistic-trade-generation)
8. [Building a Complete Trading Environment](#building-a-complete-trading-environment)
9. [Advanced Techniques](#advanced-techniques)
10. [Performance Optimization](#performance-optimization)

## Installation & Setup

### Basic Installation

```bash
pip install depthsim
```

### Development Installation

```bash
pip install depthsim[dev]
```

### With MockFlow Integration

```bash
pip install depthsim mockflow
```

### Verify Installation

```python
import depthsim
print(f"DepthSim version: {depthsim.__version__}")

# Test basic functionality
from depthsim import DepthSimulator
sim = DepthSimulator()
print("DepthSim installed successfully!")
```

## Basic Concepts

### What is Market Microstructure?

Market microstructure refers to the detailed mechanics of how trading occurs:

- **Bid-Ask Spreads**: The difference between best buy and sell prices
- **Order Book Depth**: Multiple price levels with size information
- **Trade Prints**: Actual transactions with timing and size details
- **Market Impact**: Price movement caused by large orders

### DepthSim's Role

DepthSim transforms basic market data (OHLCV) into realistic microstructure:

```
OHLCV Data → DepthSim → Bid/Ask Spreads + Order Books + Trades
```

### Key Components

1. **DepthSimulator**: Main simulation engine
2. **Spread Models**: Different ways spreads behave
3. **Order Books**: Multi-level price/size structures
4. **Trade Sequences**: Realistic trade timing and sizing

## Your First Simulation

### Step 1: Create Market Data

```python
import pandas as pd
import numpy as np
from depthsim import DepthSimulator

# Create simple market data
market_data = pd.DataFrame({
    'close': [50000, 50100, 49950, 50200, 50150],
    'volume': [1000000, 1200000, 800000, 1500000, 900000]
}, index=pd.date_range('2025-01-01', periods=5, freq='1H'))

print("Market Data:")
print(market_data)
```

### Step 2: Create Your First Simulator

```python
# Create basic depth simulator
sim = DepthSimulator(
    spread_model='constant',  # Fixed spreads
    spread_bps=5.0           # 5 basis points
)

print("Simulator created with constant 5bp spreads")
```

### Step 3: Generate Quotes

```python
# Generate bid-ask quotes
quotes = sim.generate_quotes(market_data)

print("\nGenerated Quotes:")
print(quotes)

# Examine the results
print(f"\nSpread Analysis:")
print(f"Average spread: {quotes['spread_bps'].mean():.2f}bp")
print(f"Average bid: ${quotes['bid'].mean():.2f}")
print(f"Average ask: ${quotes['ask'].mean():.2f}")
```

Expected output:
```
                          bid      ask      mid  spread_bps
2025-01-01 00:00:00  49987.5  50012.5  50000.0         5.0
2025-01-01 01:00:00  50087.5  50112.5  50100.0         5.0
2025-01-01 02:00:00  49937.5  49962.5  49950.0         5.0
...
```

### Step 4: Validate Results

```python
# Verify quote quality
for timestamp in quotes.index:
    bid = quotes.loc[timestamp, 'bid']
    ask = quotes.loc[timestamp, 'ask']
    mid = quotes.loc[timestamp, 'mid']
    close = market_data.loc[timestamp, 'close']
    
    assert ask > bid, "Ask must be higher than bid"
    assert abs(mid - close) < 0.01, "Mid should match close price"
    assert abs((ask - bid) / mid * 10000 - 5.0) < 0.1, "Spread should be 5bp"

print("All quotes validated successfully!")
```

## Understanding Spread Models

Spread models determine how bid-ask spreads behave under different market conditions.

### 1. Constant Spreads

Fixed spreads regardless of market conditions:

```python
constant_sim = DepthSimulator(
    spread_model='constant',
    spread_bps=6.0  # Always 6bp
)

quotes = constant_sim.generate_quotes(market_data)
print(f"Spread variation: {quotes['spread_bps'].std():.3f}bp (should be ~0)")
```

**When to use**: Baseline scenarios, simple backtesting

### 2. Volatility-Linked Spreads

Spreads widen during volatile periods:

```python
vol_sim = DepthSimulator(
    spread_model='volatility',
    base_spread_bps=4.0,           # Base spread
    volatility_sensitivity=50.0,    # How much vol affects spread
    min_spread_bps=1.0,            # Minimum spread
    max_spread_bps=20.0            # Maximum spread
)

# Create volatile market data
volatile_data = pd.DataFrame({
    'close': [50000, 52000, 48000, 51000, 49000],  # High volatility
    'volume': [1000000] * 5
}, index=pd.date_range('2025-01-01', periods=5, freq='1H'))

quotes = vol_sim.generate_quotes(volatile_data)
print("Volatility-linked spreads:")
for i, (timestamp, row) in enumerate(quotes.iterrows()):
    prev_price = volatile_data['close'].iloc[max(0, i-1)]
    curr_price = volatile_data.loc[timestamp, 'close']
    price_change = abs(curr_price - prev_price) / prev_price if i > 0 else 0
    
    print(f"{timestamp.strftime('%H:%M')}: ${curr_price:,.0f} "
          f"({price_change*100:+.1f}%) → {row['spread_bps']:.1f}bp")
```

**When to use**: Realistic backtesting, volatility research

### 3. Volume-Sensitive Spreads

Spreads tighten with higher trading volume:

```python
volume_sim = DepthSimulator(
    spread_model='volume',
    base_spread_bps=10.0,          # Base spread at zero volume
    volume_sensitivity=1.5,         # How much volume tightens spreads
    volume_normalization=1_000_000  # Volume level = 1.0 multiplier
)

# Create data with varying volume
volume_data = pd.DataFrame({
    'close': [50000] * 5,
    'volume': [500_000, 1_000_000, 2_000_000, 3_000_000, 1_500_000]
}, index=pd.date_range('2025-01-01', periods=5, freq='1H'))

quotes = volume_sim.generate_quotes(volume_data)
print("Volume-sensitive spreads:")
for timestamp, row in quotes.iterrows():
    volume = volume_data.loc[timestamp, 'volume']
    print(f"Volume: {volume:>9,} → Spread: {row['spread_bps']:>5.1f}bp")
```

**When to use**: Market making, liquidity analysis

### 4. Combined Models

Volatility + Volume interactions:

```python
combined_sim = DepthSimulator(
    spread_model='volatility_volume',
    base_spread_bps=5.0,
    volatility_sensitivity=60.0,
    volume_sensitivity=0.8
)

# Test with realistic market conditions
realistic_data = pd.DataFrame({
    'close': [50000, 50200, 49800, 51000, 50500],
    'volume': [800_000, 1_500_000, 2_200_000, 1_000_000, 1_800_000]
}, index=pd.date_range('2025-01-01', periods=5, freq='1H'))

quotes = combined_sim.generate_quotes(realistic_data)
print("Combined model spreads:")
for i, (timestamp, row) in enumerate(quotes.iterrows()):
    volume = realistic_data.loc[timestamp, 'volume']
    price = realistic_data.loc[timestamp, 'close']
    print(f"${price:,.0f}, Vol: {volume:>7,} → {row['spread_bps']:.1f}bp")
```

### 5. Time-of-Day Spreads

Spreads vary by market session:

```python
tod_sim = DepthSimulator(
    spread_model='time_of_day',
    base_spread_bps=5.0,
    open_close_multiplier=0.8,  # 20% tighter at open/close
    lunch_multiplier=1.4,       # 40% wider during lunch
    overnight_multiplier=2.0    # 2x wider overnight
)

# Create intraday data
intraday_data = pd.DataFrame({
    'close': [50000] * 8,
    'volume': [1_000_000] * 8
}, index=pd.date_range('2025-01-01 06:00', periods=8, freq='3H'))

quotes = tod_sim.generate_quotes(intraday_data)
print("Time-of-day spreads:")
for timestamp, row in quotes.iterrows():
    hour = timestamp.hour
    session = "Open" if 9 <= hour <= 11 else "Lunch" if 12 <= hour <= 14 else "Close" if 15 <= hour <= 16 else "Overnight"
    print(f"{timestamp.strftime('%H:%M')} ({session:>9}): {row['spread_bps']:.1f}bp")
```

### 6. Custom Spread Models

Create your own spread logic:

```python
def psychological_spread_model(mid_price, volatility, volume):
    """Wider spreads at round thousands."""
    base = 4.0
    
    # Volatility component
    vol_component = volatility * 80.0
    
    # Volume component (tighter with more volume)
    vol_component_volume = max(0, 3.0 - volume / 500_000)
    
    # Psychological levels (wider at round numbers)
    if mid_price % 1000 < 100:  # Within $100 of round thousands
        psychological_premium = 2.0
    elif mid_price % 500 < 50:  # Within $50 of $500 increments  
        psychological_premium = 1.0
    else:
        psychological_premium = 0.0
    
    return base + vol_component + vol_component_volume + psychological_premium

custom_sim = DepthSimulator(
    spread_model='custom',
    spread_function=psychological_spread_model,
    min_spread_bps=1.0,
    max_spread_bps=25.0
)

# Test with prices near round numbers
round_data = pd.DataFrame({
    'close': [49950, 50000, 50050, 50500, 50950],
    'volume': [1_000_000] * 5
}, index=pd.date_range('2025-01-01', periods=5, freq='1H'))

quotes = custom_sim.generate_quotes(round_data)
print("Custom psychological spreads:")
for timestamp, row in quotes.iterrows():
    price = round_data.loc[timestamp, 'close']
    distance_to_1000 = min(price % 1000, 1000 - (price % 1000))
    print(f"${price:>6}: {distance_to_1000:>3.0f} from 1000s → {row['spread_bps']:>5.1f}bp")
```

## Order Book Depth Simulation

Moving beyond L1 quotes to full order book depth.

### Basic Depth Ladder

```python
# Generate basic order book depth
depth_sim = DepthSimulator(
    spread_model='constant',
    spread_bps=5.0,
    depth_levels=10  # 10 levels per side
)

# Create test data
test_data = pd.DataFrame({
    'close': [50000.0, 50100.0],
    'volume': [2_000_000, 1_800_000]
}, index=pd.date_range('2025-01-01', periods=2, freq='1H'))

# Generate depth ladder
depth_ladder = depth_sim.generate_depth_ladder(test_data, levels=10)

# Examine first order book
first_timestamp = list(depth_ladder.keys())[0]
order_book = depth_ladder[first_timestamp]

print(f"Order Book at {first_timestamp}:")
print(f"Mid Price: ${order_book.mid_price:,.2f}")
print(f"Spread: {order_book.spread_bps:.2f}bp")

print(f"\nBid Levels (Best to Worst):")
for i, level in enumerate(order_book.bids[:5]):
    print(f"L{i+1}: ${level.price:>8,.2f} | {level.size:>8,} | {level.orders} orders")

print(f"\nAsk Levels (Best to Worst):")  
for i, level in enumerate(order_book.asks[:5]):
    print(f"L{i+1}: ${level.price:>8,.2f} | {level.size:>8,} | {level.orders} orders")
```

### Advanced L2 Depth with Microstructure

```python
# Advanced depth simulation with realistic features
advanced_sim = DepthSimulator(
    spread_model='volatility',
    base_spread_bps=4.0,
    volatility_sensitivity=40.0
)

# Generate sophisticated order book snapshots
l2_snapshots = advanced_sim.generate_l2_depth_snapshots(
    test_data,
    levels=20,                    # 20 levels per side
    asymmetry_factor=0.2,         # 20% asymmetry allowed
    size_clustering=True,         # Size clusters at key levels
    price_improvement=True        # Sub-penny pricing
)

first_book = next(iter(l2_snapshots.values()))

print("Advanced Order Book Features:")
print(f"Bid levels: {len(first_book.bids)}")
print(f"Ask levels: {len(first_book.asks)}")
print(f"Depth imbalance: {first_book.depth_imbalance:+.3f}")
print(f"Total depth: {first_book.total_bid_size + first_book.total_ask_size:,.0f}")

# Look for size clustering
print(f"\nSize Clustering Analysis:")
for i, level in enumerate(first_book.bids[:10]):
    is_round = (level.price % 10 < 0.5) or (level.price % 5 < 0.5)
    cluster_indicator = "*" if is_round else " "
    print(f"{cluster_indicator} L{i+1}: ${level.price:>8.3f} | {level.size:>8,}")

# Check for sub-penny pricing
print(f"\nSub-penny Pricing Examples:")
sub_penny_levels = [l for l in first_book.bids + first_book.asks 
                   if (l.price * 1000) % 10 not in [0, 5]]
for level in sub_penny_levels[:3]:
    print(f"  ${level.price:.3f} (sub-penny)")
```

### Order Book Analytics

```python
def analyze_order_book(order_book, name=""):
    """Comprehensive order book analysis."""
    
    print(f"\n=== {name} Order Book Analysis ===")
    
    # Basic metrics
    print(f"Mid Price: ${order_book.mid_price:,.2f}")
    print(f"Spread: {order_book.spread_bps:.2f}bp")
    print(f"Best Bid: ${order_book.best_bid:,.2f}")
    print(f"Best Ask: ${order_book.best_ask:,.2f}")
    
    # Depth metrics
    total_bid_size = order_book.total_bid_size
    total_ask_size = order_book.total_ask_size
    total_depth = total_bid_size + total_ask_size
    
    print(f"Total Bid Size: {total_bid_size:,.0f}")
    print(f"Total Ask Size: {total_ask_size:,.0f}")
    print(f"Depth Imbalance: {order_book.depth_imbalance:+.3f}")
    
    # Size distribution
    bid_sizes = [level.size for level in order_book.bids]
    ask_sizes = [level.size for level in order_book.asks]
    
    print(f"Bid Size Range: {min(bid_sizes):,.0f} - {max(bid_sizes):,.0f}")
    print(f"Ask Size Range: {min(ask_sizes):,.0f} - {max(ask_sizes):,.0f}")
    
    # Price levels analysis
    bid_range = order_book.bids[0].price - order_book.bids[-1].price
    ask_range = order_book.asks[-1].price - order_book.asks[0].price
    
    print(f"Bid Price Range: ${bid_range:.2f}")
    print(f"Ask Price Range: ${ask_range:.2f}")
    
    return {
        'mid_price': order_book.mid_price,
        'spread_bps': order_book.spread_bps,
        'depth_imbalance': order_book.depth_imbalance,
        'total_depth': total_depth,
        'bid_range': bid_range,
        'ask_range': ask_range
    }

# Analyze our order books
for timestamp, book in list(l2_snapshots.items())[:2]:
    metrics = analyze_order_book(book, f"{timestamp.strftime('%H:%M')}")
```

## Market Impact Analysis

Understanding how large orders affect prices.

### Basic Impact Simulation

```python
# Create deep order book for impact testing
impact_sim = DepthSimulator(
    spread_model='constant',
    spread_bps=4.0,
    depth_levels=25
)

deep_data = pd.DataFrame({
    'close': [50000.0],
    'volume': [3_000_000]  # High volume for deep book
}, index=pd.date_range('2025-01-01', periods=1, freq='1H'))

depth_ladder = impact_sim.generate_depth_ladder(deep_data, levels=25)
test_book = next(iter(depth_ladder.values()))

print("Market Impact Analysis")
print(f"Order book depth: {len(test_book.bids)} bids, {len(test_book.asks)} asks")
print(f"Best bid: ${test_book.best_bid:.2f}, Best ask: ${test_book.best_ask:.2f}")

# Test different order sizes
order_sizes = [50_000, 100_000, 250_000, 500_000, 1_000_000]

print(f"\nBuy Order Impact:")
print(f"{'Size':>10} | {'Avg Price':>10} | {'Impact':>8} | {'Levels':>7} | {'Fill %':>7}")
print(f"{'-'*10}|{'-'*11}|{'-'*9}|{'-'*8}|{'-'*8}")

for size in order_sizes:
    impact = impact_sim.simulate_market_impact(size, 'buy', test_book)
    fill_pct = impact['executed_size'] / size * 100
    
    print(f"${size:>8,} | ${impact['average_price']:>9.2f} | {impact['impact_bps']:>6.1f}bp | "
          f"{impact['levels_consumed']:>6} | {fill_pct:>6.1f}%")
```

### Impact Curve Analysis

```python
# Generate impact curve
def generate_impact_curve(order_book, max_size=2_000_000, step=50_000):
    """Generate liquidity/impact curve."""
    
    sizes = range(step, max_size + step, step)
    impact_curve = []
    
    for size in sizes:
        buy_impact = impact_sim.simulate_market_impact(size, 'buy', order_book)
        sell_impact = impact_sim.simulate_market_impact(size, 'sell', order_book)
        
        impact_curve.append({
            'size': size,
            'buy_impact_bps': buy_impact['impact_bps'],
            'sell_impact_bps': sell_impact['impact_bps'],
            'buy_fill_rate': buy_impact['executed_size'] / size,
            'sell_fill_rate': sell_impact['executed_size'] / size,
            'avg_impact_bps': (buy_impact['impact_bps'] + sell_impact['impact_bps']) / 2
        })
    
    return impact_curve

# Generate and analyze curve
impact_curve = generate_impact_curve(test_book, max_size=1_000_000, step=100_000)

print(f"\nLiquidity Curve Analysis:")
print(f"{'Size':>10} | {'Buy Impact':>10} | {'Sell Impact':>11} | {'Avg Fill':>9}")
print(f"{'-'*10}|{'-'*11}|{'-'*12}|{'-'*10}")

for point in impact_curve:
    avg_fill = (point['buy_fill_rate'] + point['sell_fill_rate']) / 2
    print(f"${point['size']:>8,} | {point['buy_impact_bps']:>8.1f}bp | "
          f"{point['sell_impact_bps']:>9.1f}bp | {avg_fill:>7.1%}")

# Find liquidity thresholds
full_fill_threshold = max([p['size'] for p in impact_curve 
                          if min(p['buy_fill_rate'], p['sell_fill_rate']) > 0.99])
low_impact_threshold = max([p['size'] for p in impact_curve 
                           if p['avg_impact_bps'] < 5.0])

print(f"\nLiquidity Thresholds:")
print(f"Full fill guarantee: up to ${full_fill_threshold:,}")
print(f"Low impact (<5bp): up to ${low_impact_threshold:,}")
```

### Execution Strategy Simulation

```python
def simulate_twap_execution(order_book, total_size, num_slices):
    """Simulate TWAP (Time-Weighted Average Price) execution."""
    
    slice_size = total_size / num_slices
    total_cost = 0
    total_executed = 0
    
    print(f"TWAP Simulation: ${total_size:,} in {num_slices} slices")
    print(f"Slice size: ${slice_size:,}")
    print(f"\n{'Slice':>5} | {'Price':>10} | {'Impact':>8} | {'Cost':>12}")
    print(f"{'-'*5}|{'-'*11}|{'-'*9}|{'-'*13}")
    
    for i in range(num_slices):
        impact = impact_sim.simulate_market_impact(slice_size, 'buy', order_book)
        
        slice_cost = impact['executed_size'] * impact['average_price']
        total_cost += slice_cost
        total_executed += impact['executed_size']
        
        print(f"{i+1:>5} | ${impact['average_price']:>9.2f} | {impact['impact_bps']:>6.1f}bp | "
              f"${slice_cost:>11,.0f}")
    
    avg_price = total_cost / total_executed if total_executed > 0 else 0
    total_impact = (avg_price - order_book.best_ask) / order_book.best_ask * 10000
    
    print(f"\nTWAP Results:")
    print(f"Average price: ${avg_price:.2f}")
    print(f"Total impact: {total_impact:.1f}bp")
    print(f"Total executed: ${total_executed:,.0f} ({total_executed/total_size:.1%})")
    
    return {
        'avg_price': avg_price,
        'total_impact_bps': total_impact,
        'execution_rate': total_executed / total_size
    }

# Test TWAP strategies
twap_5_slice = simulate_twap_execution(test_book, 500_000, 5)
twap_10_slice = simulate_twap_execution(test_book, 500_000, 10)

print(f"\nTWAP Strategy Comparison:")
print(f"5 slices: {twap_5_slice['total_impact_bps']:.1f}bp impact")
print(f"10 slices: {twap_10_slice['total_impact_bps']:.1f}bp impact")
```

## Realistic Trade Generation

Creating trade sequences that match real market patterns.

### Basic Trade Generation

```python
trade_sim = DepthSimulator(
    spread_model='volatility',
    base_spread_bps=4.0
)

# Generate realistic trade sequence
trade_data = pd.DataFrame({
    'close': [50000 + i * 25 for i in range(20)],  # Trending market
    'volume': [1_000_000 + i * 50_000 for i in range(20)]  # Increasing volume
}, index=pd.date_range('2025-01-01 09:00', periods=20, freq='15min'))

trades = trade_sim.generate_realistic_trade_sequence(
    trade_data,
    trade_intensity=1.5,        # 1.5x normal trading
    institutional_ratio=0.2     # 20% institutional trades
)

print(f"Generated {len(trades)} trades over {len(trade_data)} periods")

# Analyze basic statistics
buy_trades = [t for t in trades if t.side.value == 'buy']
sell_trades = [t for t in trades if t.side.value == 'sell']

print(f"Buy trades: {len(buy_trades)} ({len(buy_trades)/len(trades)*100:.1f}%)")
print(f"Sell trades: {len(sell_trades)} ({len(sell_trades)/len(trades)*100:.1f}%)")

sizes = [t.size for t in trades]
print(f"Average trade size: {sum(sizes)/len(sizes):,.0f}")
print(f"Median trade size: {sorted(sizes)[len(sizes)//2]:,.0f}")
print(f"Largest trade: {max(sizes):,.0f}")
```

### Institutional vs Retail Analysis

```python
# Generate institutional-heavy trading
inst_trades = trade_sim.generate_realistic_trade_sequence(
    trade_data,
    trade_intensity=1.0,
    institutional_ratio=0.8  # 80% institutional
)

# Generate retail-heavy trading  
retail_trades = trade_sim.generate_realistic_trade_sequence(
    trade_data,
    trade_intensity=2.0,
    institutional_ratio=0.1  # 10% institutional
)

def analyze_trade_patterns(trades, name):
    """Analyze trading patterns."""
    
    if not trades:
        print(f"{name}: No trades generated")
        return
    
    sizes = [t.size for t in trades]
    buy_trades = [t for t in trades if t.side.value == 'buy']
    
    print(f"\n{name} Trading Pattern:")
    print(f"  Total trades: {len(trades)}")
    print(f"  Buy ratio: {len(buy_trades)/len(trades)*100:.1f}%")
    print(f"  Avg size: {sum(sizes)/len(sizes):,.0f}")
    print(f"  Median size: {sorted(sizes)[len(sizes)//2]:,.0f}")
    print(f"  75th percentile: {sorted(sizes)[int(len(sizes)*0.75)]:,.0f}")
    print(f"  95th percentile: {sorted(sizes)[int(len(sizes)*0.95)]:,.0f}")
    print(f"  Max size: {max(sizes):,.0f}")
    
    # Trade timing analysis
    timestamps = [t.timestamp for t in trades]
    if len(timestamps) > 1:
        intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() / 60 
                    for i in range(len(timestamps)-1)]
        print(f"  Avg interval: {sum(intervals)/len(intervals):.1f} minutes")

analyze_trade_patterns(inst_trades, "Institutional")
analyze_trade_patterns(retail_trades, "Retail")

# Sample trades from each pattern
print(f"\nSample Institutional Trades:")
for i, trade in enumerate(inst_trades[:5]):
    side = "BUY" if trade.side.value == 'buy' else "SELL"
    print(f"  {trade.timestamp.strftime('%H:%M')} {side} {trade.size:,} @ ${trade.price:.2f}")

print(f"\nSample Retail Trades:")
for i, trade in enumerate(retail_trades[:5]):
    side = "BUY" if trade.side.value == 'buy' else "SELL"
    print(f"  {trade.timestamp.strftime('%H:%M')} {side} {trade.size:,} @ ${trade.price:.2f}")
```

### Trade Pattern Validation

```python
def validate_trade_realism(trades, market_data):
    """Validate trade patterns against market data."""
    
    print("Trade Pattern Validation:")
    
    # 1. Price validation
    all_prices = [t.price for t in trades]
    market_prices = market_data['close'].values
    price_range = (market_prices.min(), market_prices.max())
    
    valid_prices = [p for p in all_prices if price_range[0] * 0.99 <= p <= price_range[1] * 1.01]
    print(f"Valid prices: {len(valid_prices)}/{len(all_prices)} ({len(valid_prices)/len(all_prices)*100:.1f}%)")
    
    # 2. Size distribution validation
    sizes = [t.size for t in trades]
    reasonable_sizes = [s for s in sizes if 100 <= s <= market_data['volume'].max() * 0.1]
    print(f"Reasonable sizes: {len(reasonable_sizes)}/{len(sizes)} ({len(reasonable_sizes)/len(sizes)*100:.1f}%)")
    
    # 3. Timing validation
    trade_times = [t.timestamp for t in trades]
    market_times = market_data.index
    time_range = (market_times[0], market_times[-1] + pd.Timedelta(hours=1))
    
    valid_times = [t for t in trade_times if time_range[0] <= t <= time_range[1]]
    print(f"Valid timestamps: {len(valid_times)}/{len(trade_times)} ({len(valid_times)/len(trade_times)*100:.1f}%)")
    
    # 4. Side balance validation
    buy_count = len([t for t in trades if t.side.value == 'buy'])
    sell_count = len(trades) - buy_count
    side_balance = abs(buy_count - sell_count) / len(trades)
    
    print(f"Side balance: {side_balance:.1%} deviation (good if <20%)")
    
    return {
        'valid_prices': len(valid_prices) / len(all_prices),
        'reasonable_sizes': len(reasonable_sizes) / len(sizes),
        'valid_times': len(valid_times) / len(trade_times),
        'side_balance': side_balance
    }

# Validate our trade patterns
validation = validate_trade_realism(trades, trade_data)

if all(v > 0.9 for v in [validation['valid_prices'], validation['reasonable_sizes'], 
                        validation['valid_times']]) and validation['side_balance'] < 0.3:
    print("\nTrade patterns validated successfully!")
else:
    print("\nTrade patterns may need adjustment")
```

## Building a Complete Trading Environment

Combining all components for comprehensive backtesting.

### Step 1: Market Data Foundation

```python
def create_market_data(symbol="BTCUSDT", days=30):
    """Create or load comprehensive market data."""
    
    try:
        # Try to use MockFlow if available
        from mockflow import generate_mock_data
        market_data = generate_mock_data(
            symbol=symbol,
            timeframe="15m",
            days=days,
            scenario="auto"
        )
        print(f"Generated {len(market_data)} periods with MockFlow")
        
    except ImportError:
        # Fallback: create synthetic data
        print("MockFlow not found, creating synthetic data...")
        periods = days * 24 * 4  # 15-minute periods
        
        # Generate realistic price series
        base_price = 50000.0
        returns = np.random.normal(0, 0.02, periods)  # 2% volatility
        prices = [base_price]
        
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, base_price * 0.5))  # Price floor
        
        # Generate correlated volume
        volumes = []
        for i, price in enumerate(prices):
            # Volume correlation with price changes
            if i > 0:
                price_change = abs(np.log(price / prices[i-1]))
                volume_mult = 1 + price_change * 10
            else:
                volume_mult = 1
            
            base_vol = 1_500_000
            volume = int(base_vol * volume_mult * np.random.uniform(0.6, 1.8))
            volumes.append(volume)
        
        market_data = pd.DataFrame({
            'close': prices,
            'volume': volumes
        }, index=pd.date_range('2025-01-01', periods=periods, freq='15min'))
        
        print(f"Generated {len(market_data)} periods synthetically")
    
    return market_data

# Create market data
market_data = create_market_data("BTCUSDT", days=7)
print(f"Price range: ${market_data['close'].min():,.0f} - ${market_data['close'].max():,.0f}")
print(f"Volume range: {market_data['volume'].min():,} - {market_data['volume'].max():,}")
```

### Step 2: Execution Environment

```python
def create_execution_environment(market_data):
    """Create comprehensive execution environment."""
    
    print("Creating execution environment...")
    
    # Main execution simulator
    execution_sim = DepthSimulator(
        spread_model='volatility_volume',  # Realistic spread behavior
        base_spread_bps=3.5,
        volatility_sensitivity=40.0,
        volume_sensitivity=0.6,
        volatility_window=20
    )
    
    # Generate core execution components
    print("  Generating L1 quotes...")
    quotes = execution_sim.generate_quotes(market_data)
    
    print("  Generating L2 depth snapshots...")
    # Sample every 4th period for performance
    sample_periods = market_data.iloc[::4]
    depth_snapshots = execution_sim.generate_l2_depth_snapshots(
        sample_periods,
        levels=15,
        asymmetry_factor=0.1,
        size_clustering=True,
        price_improvement=True
    )
    
    print("  Generating realistic trades...")
    trade_sequence = execution_sim.generate_realistic_trade_sequence(
        market_data,
        trade_intensity=1.2,
        institutional_ratio=0.18
    )
    
    return {
        'simulator': execution_sim,
        'quotes': quotes,
        'depth_snapshots': depth_snapshots,
        'trade_sequence': trade_sequence
    }

# Create execution environment
exec_env = create_execution_environment(market_data)

print(f"\nExecution Environment Summary:")
print(f"  Quotes: {len(exec_env['quotes']):,}")
print(f"  Depth snapshots: {len(exec_env['depth_snapshots']):,}")
print(f"  Trade sequence: {len(exec_env['trade_sequence']):,} trades")
```

### Step 3: Combined Dataset

```python
def create_backtesting_dataset(market_data, exec_env):
    """Combine market data with execution environment."""
    
    # Start with market data
    backtest_data = market_data.copy()
    
    # Add execution data
    backtest_data['bid'] = exec_env['quotes']['bid']
    backtest_data['ask'] = exec_env['quotes']['ask']
    backtest_data['mid'] = exec_env['quotes']['mid']
    backtest_data['spread_bps'] = exec_env['quotes']['spread_bps']
    
    # Add derived metrics
    backtest_data['spread_pct'] = backtest_data['spread_bps'] / 10000
    backtest_data['half_spread_cost'] = backtest_data['spread_pct'] / 2  # One-way cost
    
    print(f"Backtesting dataset created:")
    print(f"  Columns: {list(backtest_data.columns)}")
    print(f"  Rows: {len(backtest_data):,}")
    print(f"  Date range: {backtest_data.index[0]} to {backtest_data.index[-1]}")
    
    return backtest_data

# Create comprehensive dataset
backtest_data = create_backtesting_dataset(market_data, exec_env)

# Validate data quality
print(f"\nData Quality Checks:")
print(f"Bid < Ask: {(backtest_data['bid'] < backtest_data['ask']).all()}")
print(f"No NaN values: {not backtest_data.isnull().any().any()}")
print(f"Positive spreads: {(backtest_data['spread_bps'] > 0).all()}")
print(f"Reasonable spreads: {(backtest_data['spread_bps'] < 50).all()}")
```

### Step 4: Trading Analytics

```python
def analyze_trading_environment(backtest_data, exec_env):
    """Comprehensive trading environment analysis."""
    
    print("=== Trading Environment Analysis ===")
    
    # 1. Spread Analysis
    spreads = backtest_data['spread_bps']
    print(f"\nSpread Statistics:")
    print(f"  Mean: {spreads.mean():.2f}bp")
    print(f"  Median: {spreads.median():.2f}bp")
    print(f"  Std Dev: {spreads.std():.2f}bp")
    print(f"  Min/Max: {spreads.min():.2f}bp / {spreads.max():.2f}bp")
    
    # 2. Trading Cost Analysis
    avg_cost_bps = spreads.mean() / 2  # Half-spread cost
    print(f"\n Trading Cost Estimates:")
    print(f"  Half-spread cost: {avg_cost_bps:.2f}bp per trade")
    print(f"  Round-trip cost: {spreads.mean():.2f}bp")
    
    # Cost for different trade sizes
    trade_sizes = [10_000, 50_000, 100_000, 500_000]
    print(f"  Estimated costs by trade size:")
    for size in trade_sizes:
        cost_usd = size * (avg_cost_bps / 10000)
        print(f"    ${size:>6,}: ${cost_usd:>6.2f} ({avg_cost_bps:.2f}bp)")
    
    # 3. Depth Analysis
    if exec_env['depth_snapshots']:
        imbalances = [book.depth_imbalance for book in exec_env['depth_snapshots'].values()]
        depths = [book.total_bid_size + book.total_ask_size 
                 for book in exec_env['depth_snapshots'].values()]
        
        print(f"\nDepth Analysis:")
        print(f"  Avg imbalance: {np.mean(imbalances):+.3f}")
        print(f"  Imbalance volatility: {np.std(imbalances):.3f}")
        print(f"  Avg total depth: {np.mean(depths):,.0f}")
        print(f"  Depth stability: {1 - np.std(depths)/np.mean(depths):.3f}")
    
    # 4. Trade Analysis
    if exec_env['trade_sequence']:
        trades = exec_env['trade_sequence']
        trade_volumes = [t.size for t in trades]
        
        print(f"\nTrade Analysis:")
        print(f"  Total trades: {len(trades):,}")
        print(f"  Total volume: {sum(trade_volumes):,.0f}")
        print(f"  Avg trade size: {np.mean(trade_volumes):,.0f}")
        print(f"  Trade frequency: {len(trades) / (len(market_data) / 4):.1f} per hour")  # 15min periods
    
    # 5. Market Quality Score
    spread_score = max(0, 100 - spreads.mean())  # Lower spreads = higher score
    depth_score = min(100, np.mean(depths) / 10000)  # More depth = higher score
    stability_score = (1 - np.std(imbalances)) * 100  # More stable = higher score
    
    overall_score = (spread_score + depth_score + stability_score) / 3
    
    print(f"\nMarket Quality Score: {overall_score:.1f}/100")
    print(f"  Spread Quality: {spread_score:.1f}/100")
    print(f"  Depth Quality: {depth_score:.1f}/100") 
    print(f"  Stability: {stability_score:.1f}/100")

# Analyze the trading environment
analyze_trading_environment(backtest_data, exec_env)
```

### Step 5: Strategy Integration Example

```python
def simulate_simple_strategy(backtest_data, exec_env):
    """Example: Simple momentum strategy with realistic costs."""
    
    print("\n=== Strategy Simulation Example ===")
    
    # Simple momentum signal
    backtest_data['returns'] = backtest_data['close'].pct_change()
    backtest_data['signal'] = np.where(backtest_data['returns'] > 0.002, 1,  # Buy signal
                                      np.where(backtest_data['returns'] < -0.002, -1, 0))  # Sell signal
    
    # Simulate trades
    position = 0
    cash = 100_000  # Starting cash
    trades_made = []
    
    for timestamp, row in backtest_data.iterrows():
        signal = row['signal']
        
        if signal != 0 and signal != np.sign(position):
            # Trade execution
            if signal == 1 and position <= 0:  # Buy
                trade_price = row['ask']  # Pay ask price
                trade_size = cash * 0.1 / trade_price  # 10% of cash
                cost = trade_size * trade_price
                
                if cash >= cost:
                    position += trade_size
                    cash -= cost
                    
                    trades_made.append({
                        'timestamp': timestamp,
                        'side': 'buy',
                        'size': trade_size,
                        'price': trade_price,
                        'cost': cost
                    })
                    
            elif signal == -1 and position > 0:  # Sell
                trade_price = row['bid']  # Receive bid price
                trade_size = min(position, position * 0.5)  # Sell half position
                proceeds = trade_size * trade_price
                
                position -= trade_size
                cash += proceeds
                
                trades_made.append({
                    'timestamp': timestamp,
                    'side': 'sell',
                    'size': trade_size,
                    'price': trade_price,
                    'proceeds': proceeds
                })
    
    # Calculate performance
    final_value = cash + position * backtest_data['close'].iloc[-1]
    total_return = (final_value - 100_000) / 100_000
    
    print(f"Strategy Results:")
    print(f"  Trades executed: {len(trades_made)}")
    print(f"  Final cash: ${cash:,.2f}")
    print(f"  Final position: {position:.4f} coins")
    print(f"  Final value: ${final_value:,.2f}")
    print(f"  Total return: {total_return:.2%}")
    
    # Trading cost analysis
    if trades_made:
        buy_trades = [t for t in trades_made if t['side'] == 'buy']
        sell_trades = [t for t in trades_made if t['side'] == 'sell']
        
        total_volume = sum(t.get('cost', t.get('proceeds', 0)) for t in trades_made)
        avg_spread = backtest_data['spread_bps'].mean()
        estimated_costs = total_volume * (avg_spread / 10000) / 2
        
        print(f"  Trading volume: ${total_volume:,.2f}")
        print(f"  Estimated costs: ${estimated_costs:,.2f} ({estimated_costs/total_volume:.2%})")
    
    return {
        'trades': trades_made,
        'final_value': final_value,
        'total_return': total_return
    }

# Simulate strategy
strategy_results = simulate_simple_strategy(backtest_data, exec_env)
```

This completes the comprehensive tutorial covering DepthSim from basic concepts to advanced applications. The tutorial demonstrates how to build a complete trading environment with realistic market microstructure for professional backtesting and analysis.

## Next Steps

1. **Explore Advanced Features**: Try different spread models and L2 depth features
2. **Optimize Performance**: Use sampling and caching for large datasets
3. **Build Custom Models**: Create your own spread and sizing models
4. **Integration**: Connect with your trading strategies and risk systems
5. **Validation**: Compare simulated results with real market data

For more advanced topics, see the [API Reference](API.md) and [Advanced Examples](examples/) directory.