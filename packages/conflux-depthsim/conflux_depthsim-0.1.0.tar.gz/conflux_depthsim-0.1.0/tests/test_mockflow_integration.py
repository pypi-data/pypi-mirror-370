"""
MockFlow Integration Tests for DepthSim

Tests the integration between DepthSim and MockFlow packages,
ensuring they work together seamlessly while maintaining clean separation.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
from unittest.mock import Mock, patch

from depthsim import DepthSimulator
from depthsim.models import OrderBook, Trade


class TestMockFlowIntegration:
    """Test integration with MockFlow package."""
    
    def create_mockflow_style_data(self, periods: int = 100) -> pd.DataFrame:
        """Create data that mimics MockFlow output structure."""
        np.random.seed(42)
        
        timestamps = pd.date_range('2024-01-01', periods=periods, freq='1H')
        
        # Generate OHLCV data like MockFlow would
        base_price = 50000.0
        prices = [base_price]
        
        for _ in range(periods - 1):
            change = np.random.normal(0, 0.015)  # 1.5% volatility
            new_price = prices[-1] * (1 + change)
            prices.append(max(new_price, 1000.0))
        
        data = {
            'open': [],
            'high': [],
            'low': [],
            'close': prices,
            'volume': []
        }
        
        for i, close in enumerate(prices):
            if i == 0:
                open_price = close
            else:
                open_price = prices[i-1]  # Previous close becomes open
            
            # Generate realistic OHLC
            volatility = abs(np.log(close / open_price)) if open_price > 0 else 0.01
            high = max(open_price, close) * (1 + np.random.uniform(0, volatility))
            low = min(open_price, close) * (1 - np.random.uniform(0, volatility))
            
            data['open'].append(open_price)
            data['high'].append(high)
            data['low'].append(low)
            
            # Volume correlated with price movement
            price_move = abs(close - open_price) / open_price if open_price > 0 else 0
            base_volume = 1_200_000
            volume = int(base_volume * (1 + price_move * 5) * np.random.uniform(0.6, 1.8))
            data['volume'].append(volume)
        
        return pd.DataFrame(data, index=timestamps)
    
    def test_basic_mockflow_integration(self):
        """Test basic integration with MockFlow-style data."""
        # Simulate MockFlow data
        mockflow_data = self.create_mockflow_style_data(periods=50)
        
        # DepthSim should consume this data seamlessly
        depth_sim = DepthSimulator(
            spread_model='volatility',
            base_spread_bps=5.0,
            volatility_window=20
        )
        
        # Generate execution layer on top of MockFlow data
        quotes = depth_sim.generate_quotes(mockflow_data, price_column='close')
        
        assert len(quotes) == 50
        assert all(quotes.index == mockflow_data.index)  # Same timestamps
        
        # Quotes should be reasonable relative to close prices
        for timestamp in mockflow_data.index[:10]:  # Check first 10
            close_price = mockflow_data.loc[timestamp, 'close']
            quote = quotes.loc[timestamp]
            
            # Mid price should be close to close price
            assert abs(quote['mid'] - close_price) / close_price < 0.001  # Within 0.1%
            
            # Bid/ask should bracket the close price reasonably
            assert quote['bid'] <= close_price <= quote['ask']
    
    def test_ohlcv_column_usage(self):
        """Test that DepthSim can use different OHLC columns appropriately."""
        mockflow_data = self.create_mockflow_style_data(periods=30)
        depth_sim = DepthSimulator(spread_model='constant', spread_bps=6.0)
        
        # Test using different price columns
        close_quotes = depth_sim.generate_quotes(mockflow_data, price_column='close')
        high_quotes = depth_sim.generate_quotes(mockflow_data, price_column='high')
        low_quotes = depth_sim.generate_quotes(mockflow_data, price_column='low')
        
        # All should have same length
        assert len(close_quotes) == len(high_quotes) == len(low_quotes) == 30
        
        # Mid prices should reflect the chosen column
        for i in range(10):  # Check first 10
            timestamp = mockflow_data.index[i]
            
            close_mid = close_quotes.loc[timestamp, 'mid']
            high_mid = high_quotes.loc[timestamp, 'mid']
            low_mid = low_quotes.loc[timestamp, 'mid']
            
            close_price = mockflow_data.loc[timestamp, 'close']
            high_price = mockflow_data.loc[timestamp, 'high']
            low_price = mockflow_data.loc[timestamp, 'low']
            
            # Mid prices should match the reference prices
            assert abs(close_mid - close_price) < 0.01
            assert abs(high_mid - high_price) < 0.01
            assert abs(low_mid - low_price) < 0.01
    
    def test_volume_integration(self):
        """Test that DepthSim properly uses MockFlow volume data."""
        mockflow_data = self.create_mockflow_style_data(periods=40)
        
        # Use volume-sensitive spread model
        depth_sim = DepthSimulator(
            spread_model='volume',
            base_spread_bps=8.0,
            volume_sensitivity=1.2
        )
        
        quotes = depth_sim.generate_quotes(mockflow_data)
        
        # Higher volume periods should have tighter spreads
        high_vol_periods = mockflow_data['volume'].nlargest(5).index
        low_vol_periods = mockflow_data['volume'].nsmallest(5).index
        
        high_vol_spreads = quotes.loc[high_vol_periods, 'spread_bps']
        low_vol_spreads = quotes.loc[low_vol_periods, 'spread_bps']
        
        # On average, high volume should have tighter spreads
        assert high_vol_spreads.mean() < low_vol_spreads.mean()
    
    def test_depth_ladder_with_mockflow(self):
        """Test depth ladder generation with MockFlow data."""
        mockflow_data = self.create_mockflow_style_data(periods=20)
        
        depth_sim = DepthSimulator(
            spread_model='volatility_volume',
            base_spread_bps=5.0,
            depth_levels=15
        )
        
        depth_ladder = depth_sim.generate_depth_ladder(mockflow_data, levels=15)
        
        assert len(depth_ladder) == 20
        
        # Each order book should be well-formed
        for timestamp, order_book in list(depth_ladder.items())[:5]:  # Check first 5
            mockflow_price = mockflow_data.loc[timestamp, 'close']
            mockflow_volume = mockflow_data.loc[timestamp, 'volume']
            
            # Order book mid should be close to MockFlow close
            assert abs(order_book.mid_price - mockflow_price) / mockflow_price < 0.002
            
            # Order book size should scale with MockFlow volume
            total_depth = order_book.total_bid_size + order_book.total_ask_size
            expected_depth = mockflow_volume * 0.16  # Expected ratio
            
            # Should be within reasonable range (volume affects sizing)
            assert 0.5 * expected_depth < total_depth < 3.0 * expected_depth
    
    def test_realistic_workflow_integration(self):
        """Test realistic workflow: MockFlow → DepthSim → Analysis."""
        # Step 1: Generate MockFlow-style market data
        market_data = self.create_mockflow_style_data(periods=100)
        
        # Step 2: Add execution layer with DepthSim
        execution_sim = DepthSimulator(
            spread_model='time_of_day',
            base_spread_bps=4.0,
            depth_levels=20
        )
        
        # Generate complete execution environment
        quotes = execution_sim.generate_quotes(market_data)
        depth_snapshots = execution_sim.generate_l2_depth_snapshots(
            market_data, 
            levels=15,
            asymmetry_factor=0.1
        )
        trade_sequence = execution_sim.generate_realistic_trade_sequence(
            market_data,
            trade_intensity=1.0,
            institutional_ratio=0.15
        )
        
        # Step 3: Create combined dataset for backtesting
        backtest_data = market_data.copy()
        backtest_data['bid'] = quotes['bid']
        backtest_data['ask'] = quotes['ask']
        backtest_data['mid'] = quotes['mid'] 
        backtest_data['spread_bps'] = quotes['spread_bps']
        
        # Validate combined dataset
        assert len(backtest_data) == 100
        expected_columns = ['open', 'high', 'low', 'close', 'volume', 'bid', 'ask', 'mid', 'spread_bps']
        for col in expected_columns:
            assert col in backtest_data.columns
        
        # Check data quality
        assert all(backtest_data['bid'] < backtest_data['ask'])
        assert all(backtest_data['low'] <= backtest_data['close'] <= backtest_data['high'])
        assert len(depth_snapshots) == 100
        assert len(trade_sequence) > 0
        
        # Step 4: Simulate trading analysis
        total_trade_volume = sum(t.size for t in trade_sequence)
        avg_spread = backtest_data['spread_bps'].mean()
        trading_costs_bp = avg_spread / 2  # Half spread as cost estimate
        
        assert total_trade_volume > 0
        assert 2.0 <= avg_spread <= 20.0  # Reasonable spread range
        assert 1.0 <= trading_costs_bp <= 10.0  # Reasonable cost range
    
    @pytest.mark.skipif(True, reason="Requires actual MockFlow installation")
    def test_real_mockflow_integration(self):
        """Test with actual MockFlow package if available."""
        try:
            from mockflow import generate_mock_data
            
            # Generate real MockFlow data
            mockflow_data = generate_mock_data(
                symbol="BTCUSDT",
                timeframe="1h", 
                days=7,
                scenario="auto"
            )
            
            # Use with DepthSim
            depth_sim = DepthSimulator(
                spread_model='volatility',
                base_spread_bps=5.0
            )
            
            quotes = depth_sim.generate_quotes(mockflow_data)
            
            assert len(quotes) == len(mockflow_data)
            assert all(quotes['spread_bps'] > 0)
            
            # Test market impact on real data
            depth_ladder = depth_sim.generate_depth_ladder(mockflow_data, levels=20)
            sample_book = next(iter(depth_ladder.values()))
            
            impact = depth_sim.simulate_market_impact(
                order_size=100_000,
                order_side='buy',
                order_book=sample_book
            )
            
            assert impact['impact_bps'] >= 0
            assert impact['executed_size'] > 0
            
        except ImportError:
            pytest.skip("MockFlow not available for integration testing")


class TestDataCompatibility:
    """Test compatibility with various data formats and edge cases."""
    
    def test_different_timestamp_formats(self):
        """Test compatibility with different timestamp formats."""
        # Test with different index types
        test_cases = [
            # Standard datetime index
            pd.date_range('2024-01-01', periods=10, freq='1H'),
            # String timestamps 
            [f"2024-01-01 {i:02d}:00:00" for i in range(10)],
            # Unix timestamps
            pd.to_datetime(range(1704067200, 1704067200 + 36000, 3600), unit='s')
        ]
        
        for i, timestamps in enumerate(test_cases):
            market_data = pd.DataFrame({
                'close': 50000 + np.random.randn(10) * 100,
                'volume': 1000000 + np.random.randint(-200000, 200000, 10)
            }, index=timestamps)
            
            depth_sim = DepthSimulator(spread_model='constant', spread_bps=5.0)
            
            # Should handle all timestamp formats
            quotes = depth_sim.generate_quotes(market_data)
            assert len(quotes) == 10, f"Failed for timestamp format {i}"
    
    def test_missing_columns_handling(self):
        """Test handling of missing or differently named columns."""
        # Test with minimal required columns
        minimal_data = pd.DataFrame({
            'close': [50000, 50100, 49900],
            'volume': [1000000, 1200000, 800000]
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        depth_sim = DepthSimulator(spread_model='constant', spread_bps=5.0)
        quotes = depth_sim.generate_quotes(minimal_data)
        
        assert len(quotes) == 3
        
        # Test with renamed columns
        renamed_data = pd.DataFrame({
            'price': [50000, 50100, 49900],  # Different name
            'vol': [1000000, 1200000, 800000]  # Different name
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        # Should work when column names are specified
        quotes = depth_sim.generate_quotes(renamed_data, price_column='price', volume_column='vol')
        assert len(quotes) == 3
    
    def test_extra_columns_handling(self):
        """Test that extra columns don't interfere."""
        rich_data = pd.DataFrame({
            'open': [49900, 50000, 49800],
            'high': [50200, 50300, 50100],  
            'low': [49800, 49900, 49700],
            'close': [50000, 50100, 49900],
            'volume': [1000000, 1200000, 800000],
            'trades': [1500, 1800, 1200],  # Extra column
            'vwap': [50050, 50150, 49950],  # Extra column
            'custom_indicator': [0.5, 0.6, 0.4]  # Extra column
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        depth_sim = DepthSimulator(spread_model='volume', base_spread_bps=5.0)
        
        # Should ignore extra columns and work normally
        quotes = depth_sim.generate_quotes(rich_data)
        assert len(quotes) == 3
        
        depth_ladder = depth_sim.generate_depth_ladder(rich_data, levels=10)
        assert len(depth_ladder) == 3
    
    def test_data_type_compatibility(self):
        """Test compatibility with different data types."""
        # Test with various numeric types
        market_data = pd.DataFrame({
            'close': np.array([50000, 50100, 49900], dtype=np.float32),  # float32
            'volume': np.array([1000000, 1200000, 800000], dtype=np.int64)  # int64
        }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
        
        depth_sim = DepthSimulator(spread_model='constant', spread_bps=5.0)
        
        quotes = depth_sim.generate_quotes(market_data)
        assert len(quotes) == 3
        
        # Results should be in standard float64
        assert quotes['bid'].dtype == np.float64
        assert quotes['ask'].dtype == np.float64
    
    def test_large_price_ranges(self):
        """Test compatibility with different price ranges."""
        # Test cases: crypto, forex, penny stocks, high-priced stocks
        test_cases = [
            {"close": [0.0001, 0.0002, 0.00015], "name": "penny_crypto"},  # Very low prices
            {"close": [1.2345, 1.2456, 1.2234], "name": "forex"},  # Mid-range
            {"close": [50000, 51000, 49500], "name": "crypto"},  # High crypto
            {"close": [500000, 510000, 495000], "name": "very_high"}  # Very high
        ]
        
        for case in test_cases:
            market_data = pd.DataFrame({
                'close': case["close"],
                'volume': [1000000, 1200000, 800000]
            }, index=pd.date_range('2024-01-01', periods=3, freq='1H'))
            
            depth_sim = DepthSimulator(spread_model='constant', spread_bps=10.0)
            
            quotes = depth_sim.generate_quotes(market_data)
            
            # Basic validation for each price range
            assert len(quotes) == 3, f"Failed for {case['name']}"
            assert all(quotes['ask'] > quotes['bid']), f"Invalid bid/ask for {case['name']}"
            
            # Relative spread should be reasonable
            for i in range(3):
                relative_spread = (quotes.iloc[i]['ask'] - quotes.iloc[i]['bid']) / quotes.iloc[i]['mid']
                assert 0.0001 <= relative_spread <= 0.05, f"Invalid relative spread for {case['name']}: {relative_spread}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])