"""
Performance and Stress Tests for DepthSim

Tests for performance characteristics, memory usage, and behavior
under stress conditions with large datasets.
"""

import pytest
import pandas as pd
import numpy as np
import time
import gc
from datetime import datetime, timedelta
from typing import List, Dict

from depthsim import DepthSimulator
from depthsim.models import OrderBook, Trade


class TestPerformanceBasic:
    """Test basic performance characteristics."""
    
    def create_large_dataset(self, periods: int) -> pd.DataFrame:
        """Create large synthetic dataset for testing."""
        np.random.seed(42)
        
        timestamps = pd.date_range('2024-01-01', periods=periods, freq='15min')
        
        # Generate realistic price series
        base_price = 50000.0
        prices = [base_price]
        
        for _ in range(periods - 1):
            change = np.random.normal(0, 0.002)
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1000.0))  # Price floor
        
        # Generate correlated volume
        volumes = []
        for i, price in enumerate(prices):
            base_volume = 1_000_000
            volatility_multiplier = 1 + abs(np.log(price / prices[max(0, i-1)]) if i > 0 else 0) * 10
            random_multiplier = np.random.uniform(0.5, 2.0)
            volume = int(base_volume * volatility_multiplier * random_multiplier)
            volumes.append(volume)
        
        return pd.DataFrame({
            'close': prices,
            'volume': volumes
        }, index=timestamps)
    
    def test_quote_generation_performance(self):
        """Test quote generation performance with different data sizes."""
        sizes = [100, 500, 1000, 2000]
        results = {}
        
        for size in sizes:
            market_data = self.create_large_dataset(size)
            sim = DepthSimulator(spread_model='volatility', base_spread_bps=5.0)
            
            start_time = time.time()
            quotes = sim.generate_quotes(market_data)
            end_time = time.time()
            
            duration = end_time - start_time
            rate = size / duration if duration > 0 else float('inf')
            
            results[size] = {
                'duration': duration,
                'rate': rate,
                'quotes_count': len(quotes)
            }
            
            # Validate results
            assert len(quotes) == size
            assert all(quotes['spread_bps'] > 0)
        
        print(f"\nQuote Generation Performance:")
        print(f"{'Size':>6} | {'Duration':>10} | {'Rate':>12} | {'Quotes':>8}")
        print(f"{'-'*6}|{'-'*11}|{'-'*13}|{'-'*9}")
        
        for size, metrics in results.items():
            print(f"{size:>6} | {metrics['duration']:>8.3f}s | {metrics['rate']:>9.0f}/s | {metrics['quotes_count']:>8}")
        
        # Performance should be reasonable (>100 quotes/second for most sizes)
        for size, metrics in results.items():
            if size <= 1000:  # For reasonable sizes
                assert metrics['rate'] > 50, f"Performance too slow for size {size}: {metrics['rate']:.1f} quotes/s"
    
    def test_depth_generation_performance(self):
        """Test depth ladder generation performance."""
        sizes = [50, 200, 500, 1000]
        results = {}
        
        for size in sizes:
            market_data = self.create_large_dataset(size)
            sim = DepthSimulator(spread_model='constant', spread_bps=5.0, depth_levels=15)
            
            start_time = time.time()
            depth_ladder = sim.generate_depth_ladder(market_data, levels=15)
            end_time = time.time()
            
            duration = end_time - start_time
            rate = size / duration if duration > 0 else float('inf')
            
            results[size] = {
                'duration': duration,
                'rate': rate,
                'books_count': len(depth_ladder)
            }
            
            # Validate results
            assert len(depth_ladder) == size
            for book in list(depth_ladder.values())[:5]:  # Check first 5
                assert len(book.bids) > 0
                assert len(book.asks) > 0
        
        print(f"\nDepth Generation Performance:")
        print(f"{'Size':>6} | {'Duration':>10} | {'Rate':>12} | {'Books':>8}")
        print(f"{'-'*6}|{'-'*11}|{'-'*13}|{'-'*9}")
        
        for size, metrics in results.items():
            print(f"{size:>6} | {metrics['duration']:>8.3f}s | {metrics['rate']:>9.0f}/s | {metrics['books_count']:>8}")
        
        # Depth generation is more expensive but should still be reasonable
        for size, metrics in results.items():
            if size <= 500:  # For reasonable sizes
                assert metrics['rate'] > 20, f"Depth generation too slow for size {size}: {metrics['rate']:.1f} books/s"
    
    def test_trade_sequence_performance(self):
        """Test trade sequence generation performance."""
        sizes = [50, 200, 500]  # Smaller sizes for trade generation
        results = {}
        
        for size in sizes:
            market_data = self.create_large_dataset(size)
            sim = DepthSimulator(spread_model='volume', base_spread_bps=4.0)
            
            start_time = time.time()
            trades = sim.generate_realistic_trade_sequence(
                market_data, 
                trade_intensity=1.0
            )
            end_time = time.time()
            
            duration = end_time - start_time
            rate = size / duration if duration > 0 else float('inf')
            
            results[size] = {
                'duration': duration,
                'rate': rate,
                'trades_count': len(trades)
            }
            
            # Validate results
            assert isinstance(trades, list)
            for trade in trades[:5]:  # Check first 5
                assert trade.size > 0
                assert trade.price > 0
        
        print(f"\nTrade Generation Performance:")
        print(f"{'Size':>6} | {'Duration':>10} | {'Rate':>12} | {'Trades':>8}")
        print(f"{'-'*6}|{'-'*11}|{'-'*13}|{'-'*9}")
        
        for size, metrics in results.items():
            print(f"{size:>6} | {metrics['duration']:>8.3f}s | {metrics['rate']:>9.0f}/s | {metrics['trades_count']:>8}")


class TestMemoryUsage:
    """Test memory usage characteristics."""
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def test_memory_scaling(self):
        """Test memory usage scaling with data size."""
        sizes = [100, 500, 1000]
        memory_usage = {}
        
        for size in sizes:
            gc.collect()  # Clean up before measurement
            initial_memory = self.get_memory_usage()
            
            # Generate large dataset
            market_data = pd.DataFrame({
                'close': np.random.uniform(45000, 55000, size),
                'volume': np.random.randint(500000, 3000000, size)
            }, index=pd.date_range('2024-01-01', periods=size, freq='1H'))
            
            sim = DepthSimulator(spread_model='volatility', base_spread_bps=5.0, depth_levels=20)
            
            # Generate all data types
            quotes = sim.generate_quotes(market_data)
            depth_ladder = sim.generate_depth_ladder(market_data, levels=20)
            
            final_memory = self.get_memory_usage()
            memory_used = final_memory - initial_memory
            
            memory_usage[size] = {
                'memory_mb': memory_used,
                'memory_per_period': memory_used / size if size > 0 else 0,
                'quotes_size': len(quotes),
                'depth_size': len(depth_ladder)
            }
            
            # Clean up
            del quotes, depth_ladder, market_data, sim
            gc.collect()
        
        print(f"\nMemory Usage Analysis:")
        print(f"{'Size':>6} | {'Memory MB':>10} | {'MB/Period':>10} | {'Efficiency':>11}")
        print(f"{'-'*6}|{'-'*11}|{'-'*11}|{'-'*12}")
        
        for size, metrics in memory_usage.items():
            efficiency = "Good" if metrics['memory_per_period'] < 1.0 else "Moderate"
            print(f"{size:>6} | {metrics['memory_mb']:>8.1f} | {metrics['memory_per_period']:>8.3f} | {efficiency:>11}")
        
        # Memory usage should scale reasonably
        for size, metrics in memory_usage.items():
            assert metrics['memory_per_period'] < 2.0, f"Memory usage too high: {metrics['memory_per_period']:.3f} MB/period"


class TestStressTesting:
    """Test behavior under stress conditions."""
    
    def test_extreme_volume_values(self):
        """Test with extreme volume values."""
        extreme_data = pd.DataFrame({
            'close': [50000.0, 50100.0, 49900.0],
            'volume': [1, 1_000_000_000, 500]  # Extreme range
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        sim = DepthSimulator(spread_model='volume', base_spread_bps=5.0)
        
        # Should handle without crashing
        quotes = sim.generate_quotes(extreme_data)
        assert len(quotes) == 3
        assert all(quotes['spread_bps'] > 0)
        assert all(quotes['spread_bps'] < 1000)  # Reasonable upper bound
        
        depth_ladder = sim.generate_depth_ladder(extreme_data, levels=10)
        assert len(depth_ladder) == 3
        
        for book in depth_ladder.values():
            assert len(book.bids) > 0
            assert len(book.asks) > 0
            assert all(level.size > 0 for level in book.bids + book.asks)
    
    def test_extreme_price_values(self):
        """Test with extreme price values."""
        extreme_data = pd.DataFrame({
            'close': [0.01, 100000.0, 0.001],  # Very low and very high prices
            'volume': [1000000, 2000000, 500000]
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        sim = DepthSimulator(spread_model='constant', spread_bps=10.0)
        
        quotes = sim.generate_quotes(extreme_data)
        assert len(quotes) == 3
        
        # All prices should be positive and reasonable
        assert all(quotes['bid'] > 0)
        assert all(quotes['ask'] > 0)
        assert all(quotes['ask'] > quotes['bid'])
        
        # Spreads should be reasonable relative to prices
        for idx, row in quotes.iterrows():
            relative_spread = (row['ask'] - row['bid']) / row['mid']
            assert relative_spread < 0.1  # Less than 10%
    
    def test_high_frequency_data(self):
        """Test with high-frequency (many periods) data."""
        # Generate 1 week of 1-minute data (7 * 24 * 60 = 10,080 periods)
        periods = 5000  # Reduced for testing
        
        hf_data = pd.DataFrame({
            'close': 50000 + np.cumsum(np.random.normal(0, 10, periods)),
            'volume': np.random.randint(10000, 100000, periods)
        }, index=pd.date_range('2024-01-01', periods=periods, freq='1min'))
        
        sim = DepthSimulator(spread_model='volatility', base_spread_bps=3.0)
        
        start_time = time.time()
        quotes = sim.generate_quotes(hf_data)
        quote_time = time.time() - start_time
        
        assert len(quotes) == periods
        assert quote_time < 60, f"Quote generation too slow: {quote_time:.1f}s"
        
        # Test subset for depth (full depth would be very slow)
        subset_data = hf_data.iloc[::100]  # Every 100th point
        
        start_time = time.time()
        depth_ladder = sim.generate_depth_ladder(subset_data, levels=10)
        depth_time = time.time() - start_time
        
        assert len(depth_ladder) == len(subset_data)
        assert depth_time < 30, f"Depth generation too slow: {depth_time:.1f}s"
    
    def test_many_depth_levels(self):
        """Test with many order book depth levels."""
        market_data = pd.DataFrame({
            'close': [50000.0, 50100.0],
            'volume': [2000000, 1800000]
        }, index=pd.date_range('2024-01-01', periods=2, freq='1H'))
        
        # Test with deep order books
        deep_levels = [50, 100, 200]
        
        for levels in deep_levels:
            sim = DepthSimulator(spread_model='constant', spread_bps=5.0, depth_levels=levels)
            
            start_time = time.time()
            depth_ladder = sim.generate_depth_ladder(market_data, levels=levels)
            duration = time.time() - start_time
            
            assert len(depth_ladder) == 2
            
            # Check depth structure
            for book in depth_ladder.values():
                assert len(book.bids) <= levels
                assert len(book.asks) <= levels
                assert len(book.bids) > levels * 0.5  # At least half requested levels
                
                # Verify price ordering
                bid_prices = [level.price for level in book.bids]
                ask_prices = [level.price for level in book.asks]
                
                assert bid_prices == sorted(bid_prices, reverse=True)
                assert ask_prices == sorted(ask_prices)
            
            # Performance should still be reasonable
            assert duration < 10, f"Deep book generation too slow for {levels} levels: {duration:.1f}s"
    
    def test_concurrent_simulation_compatibility(self):
        """Test that multiple simulators can run without interference."""
        market_data = pd.DataFrame({
            'close': [50000.0, 50100.0, 49900.0],
            'volume': [1500000, 1800000, 1200000]
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        # Create multiple simulators with different configs
        simulators = [
            DepthSimulator(spread_model='constant', spread_bps=5.0, seed=100),
            DepthSimulator(spread_model='volatility', base_spread_bps=4.0, seed=200),
            DepthSimulator(spread_model='volume', base_spread_bps=6.0, seed=300)
        ]
        
        # Run all simultaneously
        results = []
        for sim in simulators:
            quotes = sim.generate_quotes(market_data)
            depth = sim.generate_depth_ladder(market_data, levels=10)
            trades = sim.generate_realistic_trade_sequence(market_data, trade_intensity=0.5)
            
            results.append({
                'quotes': quotes,
                'depth': depth,
                'trades': trades
            })
        
        # All should produce valid results
        assert len(results) == 3
        
        for i, result in enumerate(results):
            assert len(result['quotes']) == 3
            assert len(result['depth']) == 3
            assert isinstance(result['trades'], list)
            
            # Results should be different between simulators (different seeds/models)
            if i > 0:
                prev_quotes = results[i-1]['quotes']
                curr_quotes = result['quotes']
                
                # At least some spread values should be different
                spread_diff = abs(curr_quotes['spread_bps'] - prev_quotes['spread_bps']).sum()
                assert spread_diff > 0.1, "Simulators should produce different results"


class TestLongRunningScenarios:
    """Test long-running and complex scenarios."""
    
    def test_full_trading_day_simulation(self):
        """Test complete trading day simulation."""
        # Full trading day: 6.5 hours * 4 (15-min intervals) = 26 periods
        trading_day = pd.date_range('2024-01-01 09:30', periods=26, freq='15min')
        
        # Generate realistic intraday pattern
        prices = []
        volumes = []
        base_price = 50000.0
        
        for i, timestamp in enumerate(trading_day):
            hour = timestamp.hour + timestamp.minute / 60.0
            
            # Intraday price drift
            time_factor = (i / len(trading_day) - 0.5) * 0.001  # Small drift
            price_change = np.random.normal(time_factor, 0.002)
            
            if i == 0:
                price = base_price
            else:
                price = prices[-1] * (1 + price_change)
            prices.append(price)
            
            # Intraday volume pattern (U-shaped)
            if 9.5 <= hour <= 10.5 or 15.5 <= hour <= 16.0:
                volume_mult = 1.8  # High at open/close
            elif 12.0 <= hour <= 14.0:
                volume_mult = 0.6   # Low at lunch
            else:
                volume_mult = 1.0
            
            volume = int(1_500_000 * volume_mult * np.random.uniform(0.7, 1.3))
            volumes.append(volume)
        
        market_data = pd.DataFrame({
            'close': prices,
            'volume': volumes
        }, index=trading_day)
        
        # Full simulation with time-of-day effects
        sim = DepthSimulator(
            spread_model='time_of_day',
            base_spread_bps=4.0,
            open_close_multiplier=0.8,
            lunch_multiplier=1.4,
            overnight_multiplier=2.0
        )
        
        # Generate all components
        start_time = time.time()
        
        quotes = sim.generate_quotes(market_data)
        depth_snapshots = sim.generate_l2_depth_snapshots(market_data, levels=15)
        trade_sequence = sim.generate_realistic_trade_sequence(
            market_data, 
            trade_intensity=1.5,
            institutional_ratio=0.18
        )
        
        total_time = time.time() - start_time
        
        # Validate comprehensive results
        assert len(quotes) == 26
        assert len(depth_snapshots) == 26
        assert len(trade_sequence) > 0
        
        # Check time-of-day spread effects
        open_spreads = quotes.iloc[:4]['spread_bps']  # First hour
        lunch_spreads = quotes.iloc[10:14]['spread_bps']  # Lunch time
        
        # Lunch spreads should generally be wider than open spreads
        assert lunch_spreads.mean() > open_spreads.mean() * 1.1
        
        # Performance should be reasonable for full day
        assert total_time < 120, f"Full day simulation too slow: {total_time:.1f}s"
        
        print(f"\nFull Trading Day Simulation:")
        print(f"  Time periods: {len(market_data)}")
        print(f"  Quotes generated: {len(quotes)}")
        print(f"  Depth snapshots: {len(depth_snapshots)}")
        print(f"  Trades generated: {len(trade_sequence)}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Avg spread: {quotes['spread_bps'].mean():.2f}bp")
        print(f"  Total volume: {sum(t.size for t in trade_sequence):,}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show prints